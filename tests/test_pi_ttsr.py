"""Loads pi/ttsr.ts with a stub pi API and checks rule parsing, matching, and injection."""

import json
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXTENSION = REPO_ROOT / "pi" / "ttsr.ts"

# Each scenario is a list of steps. The harness replays them against the registered
# handlers and prints one JSON record of what the extension did.
HARNESS = """
const [extensionUrl, cwd, stepsJson, branchJson] = process.argv.slice(1);
const { default: register } = await import(extensionUrl);
const handlers = {};
const commands = {};
const out = { notices: [], sent: [], entries: [], aborts: 0, results: [] };
register({
  on: (event, fn) => { handlers[event] = fn; },
  registerCommand: (name, options) => { commands[name] = options; },
  sendMessage: (message, options) => out.sent.push({ message, options }),
  appendEntry: (customType, data) => out.entries.push({ customType, data }),
});
const ctx = {
  cwd,
  ui: { notify: (message, level) => out.notices.push({ message, level }) },
  abort: () => { out.aborts++; },
  sessionManager: { getBranch: () => JSON.parse(branchJson) },
};
await handlers.session_start({ type: "session_start", reason: "startup" }, ctx);
for (const step of JSON.parse(stepsJson)) {
  const handler = step.command ? commands[step.command].handler : handlers[step.event];
  const result = step.command ? await handler("", ctx) : await handler(step.payload ?? {}, ctx);
  out.results.push(result ?? null);
}
console.log(JSON.stringify(out));
"""

GIT_STASH_RULE = """\
---
description: "Agents prove a red test without git stash"
condition: '\\bgit\\s+stash\\b'
scope: "tool:bash"
---

Prove a red test by copying the file to /tmp and restoring it.
"""


def tool_call(command: str, tool: str = "bash", call_id: str = "c1") -> dict:
    return {"event": "tool_call", "payload": {"toolName": tool, "toolCallId": call_id, "input": {"command": command}}}


def text_delta(delta: str, index: int = 0) -> dict:
    return {
        "event": "message_update",
        "payload": {
            "message": {"role": "assistant", "timestamp": 111},
            "assistantMessageEvent": {"type": "text_delta", "contentIndex": index, "delta": delta},
        },
    }


@unittest.skipUnless(shutil.which("node"), "node is required to load the pi extension")
class TestPiTtsr(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base = Path(self.temp_dir.name)
        self.cwd = self.base / "project"
        self.agent_dir = self.base / "agent"
        (self.cwd / ".pi" / "rules").mkdir(parents=True)
        (self.agent_dir / "rules").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def user_rule(self, name: str, source: str):
        (self.agent_dir / "rules" / f"{name}.md").write_text(textwrap.dedent(source), encoding="utf-8")

    def project_rule(self, name: str, source: str):
        (self.cwd / ".pi" / "rules" / f"{name}.md").write_text(textwrap.dedent(source), encoding="utf-8")

    def run_steps(self, steps: list, branch: list | None = None) -> dict:
        proc = subprocess.run(
            ["node", "--input-type=module", "-e", HARNESS,
             EXTENSION.as_uri(), str(self.cwd), json.dumps(steps), json.dumps(branch or [])],
            capture_output=True,
            text=True,
            env={"PATH": shutil.os.environ["PATH"], "PI_CODING_AGENT_DIR": str(self.agent_dir)},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout.strip().splitlines()[-1])

    def test_tool_rule_blocks_matching_bash_call_with_rule_text(self):
        self.user_rule("no-git-stash", GIT_STASH_RULE)
        out = self.run_steps([tool_call("git stash push -m wip")])
        result = out["results"][0]
        self.assertTrue(result["block"])
        self.assertIn('<system-interrupt reason="rule_violation" rule="no-git-stash"', result["reason"])
        self.assertIn("copying the file to /tmp", result["reason"])
        self.assertEqual(out["entries"], [{"customType": "ttsr_injection", "data": {"rules": ["no-git-stash"]}}])

    def test_tool_rule_ignores_other_tools_and_non_matching_commands(self):
        self.user_rule("no-git-stash", GIT_STASH_RULE)
        out = self.run_steps([
            tool_call("git status"),
            {"event": "tool_call", "payload": {"toolName": "write", "toolCallId": "c2",
                                               "input": {"path": "a.md", "content": "git stash"}}},
        ])
        self.assertEqual(out["results"], [None, None])

    def test_once_mode_fires_a_rule_only_once(self):
        self.user_rule("no-git-stash", GIT_STASH_RULE)
        out = self.run_steps([tool_call("git stash", call_id="c1"), tool_call("git stash pop", call_id="c2")])
        self.assertTrue(out["results"][0]["block"])
        self.assertIsNone(out["results"][1])

    def test_after_gap_mode_refires_after_gap_turns(self):
        self.user_rule("no-git-stash", GIT_STASH_RULE.replace('scope: "tool:bash"', 'scope: "tool:bash"\nrepeatMode: after-gap\nrepeatGap: 2'))
        out = self.run_steps([
            tool_call("git stash", call_id="c1"),
            {"event": "turn_end"},
            tool_call("git stash", call_id="c2"),
            {"event": "turn_end"},
            tool_call("git stash", call_id="c3"),
        ])
        self.assertTrue(out["results"][0]["block"])
        self.assertIsNone(out["results"][2])
        self.assertTrue(out["results"][4]["block"])

    def test_restored_session_entries_suppress_once_rules(self):
        self.user_rule("no-git-stash", GIT_STASH_RULE)
        branch = [{"type": "custom", "customType": "ttsr_injection", "data": {"rules": ["no-git-stash"]}}]
        out = self.run_steps([tool_call("git stash")], branch)
        self.assertEqual(out["results"], [None])

    def test_never_mode_lets_tool_run_and_appends_reminder_to_result(self):
        self.user_rule("no-git-stash", GIT_STASH_RULE.replace('scope: "tool:bash"', 'scope: "tool:bash"\ninterruptMode: never'))
        out = self.run_steps([
            tool_call("git stash"),
            {"event": "tool_result", "payload": {"toolCallId": "c1", "content": [{"type": "text", "text": "ok"}]}},
        ])
        self.assertIsNone(out["results"][0])
        content = out["results"][1]["content"]
        self.assertEqual(content[0], {"type": "text", "text": "ok"})
        self.assertIn('<system-reminder reason="rule_violation" rule="no-git-stash"', content[1]["text"])

    def test_path_scoped_rule_matches_new_edit_text_only_for_matching_paths(self):
        self.user_rule("ts-no-any", """\
            ---
            condition: ':\\s*any\\b'
            scope: "tool:edit(*.ts), tool:write(*.ts)"
            ---

            Use unknown instead of any.
            """)
        edit = lambda path, call_id: {"event": "tool_call", "payload": {
            "toolName": "edit", "toolCallId": call_id,
            "input": {"path": path, "edits": [{"oldText": "x: any", "newText": "x: any"}]}}}
        out = self.run_steps([edit("src/a.md", "c1"), edit("src/a.ts", "c2")])
        self.assertIsNone(out["results"][0])
        self.assertTrue(out["results"][1]["block"])

    def test_text_rule_aborts_stream_then_injects_and_discards_partial_output(self):
        self.user_rule("same-origin", """\
            ---
            condition: '同站'
            scope: text
            ---

            The user's decision says 同源, not 同站.
            """)
        out = self.run_steps([
            text_delta("導覽只限"),
            text_delta("同站"),
            {"event": "message_end", "payload": {"message": {"role": "assistant", "stopReason": "aborted", "timestamp": 111}}},
            {"event": "agent_settled", "payload": {}},
            {"event": "context", "payload": {"messages": [
                {"role": "user", "timestamp": 100},
                {"role": "assistant", "timestamp": 111},
            ]}},
        ])
        self.assertEqual(out["aborts"], 1)
        self.assertEqual(len(out["sent"]), 1)
        sent = out["sent"][0]
        self.assertEqual(sent["options"], {"triggerTurn": True})
        self.assertIn('<system-interrupt reason="rule_violation" rule="same-origin"', sent["message"]["content"])
        self.assertEqual(out["results"][4], {"messages": [{"role": "user", "timestamp": 100}]})

    def test_text_scope_is_not_checked_for_tool_only_rules(self):
        self.user_rule("no-git-stash", GIT_STASH_RULE)
        out = self.run_steps([text_delta("I will run git stash")])
        self.assertEqual(out["aborts"], 0)

    def test_project_rule_shadows_user_rule_of_same_name(self):
        self.user_rule("no-git-stash", GIT_STASH_RULE)
        self.project_rule("no-git-stash", GIT_STASH_RULE.replace("git\\s+stash", "git\\s+stash\\s+drop"))
        out = self.run_steps([tool_call("git stash"), tool_call("git stash drop", call_id="c2")])
        self.assertIsNone(out["results"][0])
        self.assertTrue(out["results"][1]["block"])

    def test_prose_rules_and_unsupported_fields_are_reported_not_loaded(self):
        self.user_rule("prose", "# Prose rule\n\nNo frontmatter here.\n")
        self.user_rule("judged", """\
            ---
            question: "Does this violate the rule?"
            ---

            Body.
            """)
        self.user_rule("bad-regex", """\
            ---
            condition: '('
            ---

            Body.
            """)
        out = self.run_steps([{"command": "ttsr"}])
        startup = out["notices"][0]["message"]
        self.assertIn("judged: question not supported; rule skipped", startup)
        self.assertIn("bad-regex: invalid condition", startup)
        self.assertIn("TTSR rules: 0", out["notices"][-1]["message"])


if __name__ == "__main__":
    unittest.main()

"""Loads the aaaav loop extensions with a stub pi API and replays events against them."""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

PI_DIR = Path(__file__).resolve().parent.parent / "pi"

# Replays steps against the registered handlers and prints what the extension returned.
HARNESS = """
import { registerHooks } from "node:module";
// pi provides its own package to extensions; the stub carries the one value export they use.
const PI_STUB = String.raw`export function parseSkillBlock(text) {
  const match = text.match(/^<skill name="([^"]+)" location="([^"]+)">\\n([\\s\\S]*?)\\n<\\/skill>(?:\\n\\n([\\s\\S]+))?$/);
  return match ? { name: match[1], location: match[2], content: match[3], userMessage: match[4]?.trim() || undefined } : null;
}`;
registerHooks({
  resolve: (specifier, context, next) =>
    specifier === "@earendil-works/pi-coding-agent"
      ? { url: "data:text/javascript," + encodeURIComponent(PI_STUB), shortCircuit: true }
      : next(specifier, context),
});
const [extensionUrl, cwd, stepsJson, branchJson, classifyJson] = process.argv.slice(1);
const { default: register } = await import(extensionUrl);
const handlers = {};
const tools = {};
register({
  on: (event, fn) => { handlers[event] = fn; },
  registerTool: (tool) => { tools[tool.name] = tool; },
});
const classifyPlan = JSON.parse(classifyJson);
const out = { results: [], classifyCalls: [], notices: [] };
const ctx = {
  cwd,
  ui: { notify: (message, level) => out.notices.push({ step: out.results.length, message, level }) },
  sessionManager: { getBranch: () => JSON.parse(branchJson) },
  modelRegistry: {
    findOfType: (...args) => {
      out.findArgs = args;
      return classifyPlan === "missing" ? undefined : { id: "jev-latest" };
    },
    hasConfiguredAuth: () => classifyPlan !== "no-auth",
    classify: async (_model, context) => {
      out.classifyCalls.push(context.state);
      if (classifyPlan === "throw") throw new Error("network down");
      return classifyPlan;
    },
  },
};
for (const step of JSON.parse(stepsJson)) {
  try {
    const result = step.tool
      ? await tools[step.tool].execute("t1", step.params, undefined, undefined, ctx)
      : await handlers[step.event]?.(step.payload ?? {}, ctx);
    out.results.push(result ?? null);
  } catch (error) {
    out.results.push({ error: error.message });
  }
}
console.log(JSON.stringify(out));
"""


def user_start(prompt: str = "fix the export") -> dict:
    return {"event": "message_end", "payload": {"message": {"role": "user", "content": [{"type": "text", "text": prompt}]}}}


def assistant(text: str) -> dict:
    return {"event": "message_end", "payload": {"message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}}


def tool_call(tool: str, path: str = "src/app.py") -> dict:
    return {"event": "tool_call", "payload": {"toolName": tool, "toolCallId": "c1", "input": {"path": path, "command": "pytest"}}}


def typed(source: str, text: str = "x") -> dict:
    return {"event": "input", "payload": {"text": text, "source": source}}


SETTLED = {"event": "agent_settled", "payload": {"aborted": False}}
AGENT_START = {"event": "agent_start", "payload": {}}

SETTLE = {"event": "agent_before_settle", "payload": {"outcome": "completed", "entries": [], "continue": False}}


def answers(done: float, review: str, quality: float, checkpoint: float = 0.9) -> dict:
    return {
        "stopReason": "stop",
        "answers": {
            "checkpoint": {"type": "bool", "probability": checkpoint},
            "done": {"type": "bool", "probability": done},
            "review": {"type": "choice", "choice": review, "probabilities": {review: 0.6}, "confidence": 0.4},
            "quality": {"type": "score", "score": quality, "confidence": 0.5},
        },
    }


@unittest.skipUnless(shutil.which("node"), "node is required to load the pi extensions")
class ExtensionCase(unittest.TestCase):
    extension = ""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cwd = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def replay(self, steps: list[dict], branch: list | None = None, classify: object = None, env: dict | None = None) -> dict:
        # A suite run inside a subagent must not inherit its markers.
        base = {key: value for key, value in os.environ.items() if not key.startswith("PI_SUBAGENT_")}
        proc = subprocess.run(
            ["node", "--input-type=module", "-e", HARNESS, (PI_DIR / self.extension).as_uri(), str(self.cwd),
             json.dumps(steps), json.dumps(branch or []), json.dumps(classify)],
            capture_output=True,
            text=True,
            env={**base, **(env or {})},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout.strip().splitlines()[-1])


class TestAnchorGate(ExtensionCase):
    extension = "anchor-gate.ts"

    def warned_steps(self, out: dict) -> list[int]:
        for notice in out["notices"]:
            self.assertEqual(notice["level"], "warning")
            self.assertIn("Reality anchor:", notice["message"])
        return [notice["step"] for notice in out["notices"]]

    def test_edit_without_anchor_warns_once_per_user_message_and_never_blocks(self):
        out = self.replay([
            {"event": "session_start"},
            user_start(),
            tool_call("edit"),
            tool_call("write"),
            user_start("now the import"),
            tool_call("edit"),
        ])
        self.assertEqual(out["results"], [None] * 6)
        self.assertEqual(self.warned_steps(out), [2, 5])

    def test_anchor_line_silences_the_warning_until_the_next_user_prompt(self):
        out = self.replay([
            {"event": "session_start"},
            user_start(),
            assistant("Alignment: fix it.\nReality anchor: pytest tests/test_export.py"),
            tool_call("write"),
            user_start("now the import"),
            tool_call("write"),
        ])
        self.assertEqual(self.warned_steps(out), [5])

    def test_text_and_html_files_scratch_specs_temp_paths_and_other_tools_pass(self):
        out = self.replay([
            {"event": "session_start"},
            user_start(),
            tool_call("write", "README.md"),
            tool_call("edit", "notes/todo.TXT"),
            tool_call("write", "report/index.html"),
            tool_call("edit", "legacy/page.HTM"),
            tool_call("write", "scratch/friction.json"),
            tool_call("edit", "docs/specs/2026-10-21-x/design.html"),
            tool_call("write", str(Path(tempfile.gettempdir()) / "aaaav-gate-outside" / "page.html")),
            tool_call("bash"),
        ])
        self.assertEqual(out["notices"], [])

    def test_a_user_message_that_steers_the_running_loop_rearms_the_warning(self):
        out = self.replay([
            {"event": "session_start"},
            user_start(),
            assistant("Reality anchor: pytest"),
            user_start("also rename it"),
            tool_call("edit"),
        ])
        self.assertEqual(self.warned_steps(out), [4])

    def test_resumed_session_ignores_an_anchor_stated_before_the_last_user_message(self):
        branch = [
            {"type": "message", "message": {"role": "assistant", "content": [{"type": "text", "text": "Reality anchor: pytest"}]}},
            {"type": "message", "message": {"role": "user", "content": "now the import"}},
        ]
        self.assertEqual(self.warned_steps(self.replay([{"event": "session_start"}, tool_call("edit")], branch)), [1])

    def test_resumed_session_keeps_an_anchor_stated_after_the_last_user_message(self):
        branch = [
            {"type": "message", "message": {"role": "user", "content": "fix it"}},
            {"type": "message", "message": {"role": "assistant", "content": [{"type": "text", "text": "Reality anchor: pytest"}]}},
        ]
        self.assertEqual(self.replay([{"event": "session_start"}, tool_call("edit")], branch)["notices"], [])


class TestDecisionTool(ExtensionCase):
    extension = "decision-tool.ts"

    def rows(self) -> list[list[str]]:
        return [line.split("\t") for line in (self.cwd / "scratch/decisions-t.tsv").read_text().splitlines()]

    def test_first_row_writes_the_header_and_cells_stay_single_line_and_formula_safe(self):
        self.replay([
            {"tool": "aaaav_decision", "params": {"log": "scratch/decisions-t.tsv", "decision": "a\tb\nc",
                                                  "why": "=HYPERLINK(1)", "evidence": "-rf", "result": "@x"}},
        ])
        rows = self.rows()
        self.assertEqual(rows[0], ["ts", "decision", "why", "evidence", "result"])
        self.assertEqual(rows[1][1:], ["a b c", "'=HYPERLINK(1)", "'-rf", "'@x"])

    def test_start_row_names_the_run_and_the_rows_before_it(self):
        self.replay([
            {"tool": "aaaav_decision", "params": {"log": "scratch/decisions-t.tsv", "decision": "first", "why": "w",
                                                  "evidence": "abc123", "result": "open"}},
            {"tool": "aaaav_decision", "params": {"log": "scratch/decisions-t.tsv", "start": "worker-2"}},
        ])
        last = self.rows()[-1]
        self.assertEqual(last[1], "start")
        self.assertIn("1 earlier rows", last[2])
        self.assertEqual(last[3:], ["worker-2", "open"])

    def test_a_log_outside_the_scratch_trail_is_refused(self):
        out = self.replay([{"tool": "aaaav_decision", "params": {"log": "src/app.py", "decision": "d", "why": "w",
                                                                   "evidence": "e", "result": "r"}}])
        self.assertIn("scratch/decisions-", out["results"][0]["error"])
        self.assertFalse((self.cwd / "src/app.py").exists())

    def test_missing_cells_fail_without_writing(self):
        out = self.replay([{"tool": "aaaav_decision", "params": {"log": "scratch/decisions-t.tsv", "decision": "only"}}])
        self.assertIn("all required", out["results"][0]["error"])
        self.assertFalse((self.cwd / "scratch/decisions-t.tsv").exists())


class TestSecondThought(ExtensionCase):
    extension = "second-thought.ts"

    def run_turn(self, classify: object, extra: list[dict] | None = None) -> dict:
        steps = [user_start(), tool_call("bash"), assistant("Done, tests pass."), SETTLE, *(extra or [])]
        return self.replay(steps, classify=classify)

    def test_disagreement_continues_once_with_a_visible_message(self):
        out = self.run_turn(answers(0.11, "focused", 0.63), [assistant("Rechecked: 1 test fails."), SETTLE])
        first, second = out["results"][3], out["results"][5]
        self.assertTrue(first["continue"])
        self.assertEqual([entry["type"] for entry in first["entries"]], ["custom", "custom_message"])
        self.assertIn("done 0.11", first["entries"][1]["content"])
        self.assertIsNone(second)
        self.assertEqual(out["classifyCalls"], [{"request": "fix the export", "trigger": "user", "wake": "", "reply": "Done, tests pass."}])

    def test_full_review_tier_alone_is_a_concern(self):
        out = self.run_turn(answers(0.9, "full", 2.8))
        self.assertIn("full independent review", out["results"][3]["entries"][1]["content"])

    def test_agreement_records_the_numbers_without_continuing(self):
        result = self.run_turn(answers(0.84, "none", 2.88))["results"][3]
        self.assertNotIn("continue", result)
        self.assertEqual(result["entries"][0]["data"]["concerns"], [])

    def test_an_evidenced_reply_near_half_is_not_a_concern(self):
        result = self.run_turn(answers(0.3, "focused", 2.0))["results"][3]
        self.assertNotIn("continue", result)

    def test_failure_records_unknown_and_continues_nothing(self):
        result = self.run_turn("throw")["results"][3]
        self.assertEqual(result["entries"][0]["data"], {"verdict": "unknown", "reason": "network down"})
        self.assertNotIn("continue", result)

    def test_only_the_request_and_the_reply_are_sent_and_both_are_truncated(self):
        steps = [user_start("r" * 2000), tool_call("bash"), assistant("y" * 5000), SETTLE]
        out = self.replay(steps, classify=answers(0.9, "none", 2.9))
        self.assertEqual(out["findArgs"], ["classifier", "typesafe", "jev-latest"])
        self.assertEqual(out["classifyCalls"], [{"request": "r" * 1500, "trigger": "user", "wake": "", "reply": "y" * 3000}])

    def test_a_skill_command_sends_the_users_words_not_the_skill_body(self):
        expanded = '<skill name="coding" location="/Users/me/skills/coding/SKILL.md">\n' + "body " * 500 + "\n</skill>\n\nfix the export"
        out = self.replay([user_start(expanded), tool_call("edit"), assistant("Done."), SETTLE], classify=answers(0.9, "none", 2.9))
        self.assertEqual(out["classifyCalls"][0]["request"], "fix the export")

    def test_a_steering_user_message_is_judged_on_its_own(self):
        steps = [user_start("first"), tool_call("bash"), assistant("Done first."), SETTLE,
                 user_start("second"), tool_call("bash"), assistant("Done second."), SETTLE]
        out = self.replay(steps, classify=answers(0.9, "none", 2.9))
        self.assertEqual([call["request"] for call in out["classifyCalls"]], ["first", "second"])

    def test_a_low_done_score_alone_is_shown_without_a_continuation(self):
        result = self.run_turn(answers(0.05, "focused", 2.5))["results"][3]
        self.assertNotIn("continue", result)
        self.assertIn("done 0.05", result["entries"][1]["content"])
        self.assertNotIn("Recheck", result["entries"][1]["content"])

    def test_a_run_an_extension_message_starts_is_judged_against_the_typed_request(self):
        steps = [typed("interactive", "ship it"), user_start("ship it"), tool_call("bash"), assistant("Started."), SETTLE, SETTLED,
                 typed("extension", "New intercom message above."), user_start("New intercom message above."),
                 tool_call("bash"), assistant("Shipped."), SETTLE]
        out = self.replay(steps, classify=answers(0.9, "none", 2.9))
        self.assertEqual([(call["request"], call["trigger"], call["wake"]) for call in out["classifyCalls"]],
                         [("ship it", "user", ""), ("ship it", "wake", "New intercom message above.")])

    def test_a_custom_message_that_wakes_a_run_is_sent_as_the_wake(self):
        def custom(text: str, kind: str = "pi-loop-monitor") -> dict:
            return {"event": "message_end", "payload": {"message": {"role": "custom", "customType": kind, "content": text}}}
        steps = [user_start("ship it"), tool_call("MonitorCreate"), assistant("Waiting."), SETTLE, SETTLED,
                 custom("Monitor #2 started"), custom("Monitor #2 done: if on npm, pin it."),
                 tool_call("bash"), assistant("Pinned."), custom("note", "aaaav-second-thought"), SETTLE]
        out = self.replay(steps, classify=answers(0.9, "none", 2.9))
        self.assertEqual(out["classifyCalls"], [{"request": "ship it", "trigger": "wake", "wake": "Monitor #2 done: if on npm, pin it.", "reply": "Pinned."}])

    def test_a_reply_that_is_not_a_checkpoint_gets_no_reminder(self):
        result = self.run_turn(answers(0.02, "full", 0.5, checkpoint=0.1))["results"][3]
        self.assertNotIn("continue", result)
        self.assertEqual([entry["type"] for entry in result["entries"]], ["custom"])
        self.assertEqual(result["entries"][0]["data"]["concerns"], [])
        self.assertEqual(result["entries"][0]["data"]["checkpoint"], 0.1)

    def test_an_extension_input_that_never_lands_does_not_shift_later_messages(self):
        steps = [typed("extension", "swallowed"), typed("interactive", "ship it"), user_start("ship it"),
                 tool_call("bash"), assistant("Shipped."), SETTLE]
        out = self.replay(steps, classify=answers(0.9, "none", 2.9))
        self.assertEqual(out["classifyCalls"], [{"request": "ship it", "trigger": "user", "wake": "", "reply": "Shipped."}])

    def test_an_extension_text_with_surrounding_whitespace_still_matches(self):
        steps = [user_start("ship it"), tool_call("bash"), assistant("Started."), SETTLE, SETTLED,
                 typed("extension", "wake\n"), user_start("wake\n"), tool_call("bash"), assistant("Shipped."), SETTLE]
        out = self.replay(steps, classify=answers(0.9, "none", 2.9))
        self.assertEqual([(call["request"], call["trigger"]) for call in out["classifyCalls"]], [("ship it", "user"), ("ship it", "wake")])

    def test_a_swallowed_extension_text_is_forgotten_once_the_session_settles(self):
        steps = [typed("extension", "ship it"), SETTLED, user_start("ship it"),
                 tool_call("bash"), assistant("Shipped."), SETTLE]
        out = self.replay(steps, classify=answers(0.9, "none", 2.9))
        self.assertEqual(out["classifyCalls"], [{"request": "ship it", "trigger": "user", "wake": "", "reply": "Shipped."}])

    def test_a_recheck_continuation_does_not_ask_again(self):
        # pi fires agent_start again for the continuation; the recheck runs bash again.
        steps = [user_start(), AGENT_START, tool_call("bash"), assistant("Done."), SETTLE,
                 AGENT_START, tool_call("bash"), assistant("Rechecked, tests pass."), SETTLE]
        out = self.replay(steps, classify=answers(0.9, "full", 2.9))
        self.assertTrue(out["results"][4]["continue"])
        self.assertIsNone(out["results"][8])
        self.assertEqual(len(out["classifyCalls"]), 1)

    def test_work_before_a_compaction_continuation_still_counts(self):
        steps = [user_start(), tool_call("edit"), AGENT_START, assistant("Done."), SETTLE]
        out = self.replay(steps, classify=answers(0.9, "none", 2.9))
        self.assertEqual(len(out["classifyCalls"]), 1)

    def test_a_run_that_arranged_a_wake_is_not_judged(self):
        for tool in ("MonitorCreate", "subagent"):
            steps = [user_start(), tool_call("bash"), tool_call(tool), assistant("Waiting on it."), SETTLE]
            out = self.replay(steps, classify=answers(0.0, "full", 0))
            self.assertIsNone(out["results"][4], tool)
            self.assertEqual(out["classifyCalls"], [], tool)

    def test_the_run_after_a_wake_is_judged_on_its_own_work(self):
        steps = [user_start("ship it"), tool_call("MonitorCreate"), assistant("Waiting."), SETTLE, SETTLED,
                 assistant("Still waiting."), SETTLE, SETTLED,
                 tool_call("bash"), assistant("Shipped."), SETTLE]
        out = self.replay(steps, classify=answers(0.9, "none", 2.9))
        self.assertEqual(out["classifyCalls"], [{"request": "ship it", "trigger": "wake", "wake": "", "reply": "Shipped."}])

    def test_without_a_key_or_a_classifier_nothing_is_asked_or_recorded(self):
        for plan in ("no-auth", "missing"):
            out = self.run_turn(plan)
            self.assertIsNone(out["results"][3], plan)
            self.assertEqual(out["classifyCalls"], [], plan)

    def test_a_subagent_session_is_never_judged(self):
        steps = [user_start(), tool_call("bash"), assistant("Done, tests pass."), SETTLE]
        markers = [{"PI_SUBAGENT_ID": "child-1"}, {"PI_SUBAGENT_CHILD": "1"},
                   {"PI_SUBAGENT_CHILD_AGENT": "worker", "PI_SUBAGENT_PARENT_PID": "42"}]
        for env in markers:
            out = self.replay(steps, classify=answers(0.1, "full", 0), env=env)
            self.assertIsNone(out["results"][3], env)
            self.assertEqual(out["classifyCalls"], [], env)

    def test_a_run_that_changed_nothing_is_not_judged(self):
        out = self.replay([user_start(), assistant("It works like this."), SETTLE], classify=answers(0.1, "full", 0))
        self.assertIsNone(out["results"][2])
        self.assertEqual(out["classifyCalls"], [])


if __name__ == "__main__":
    unittest.main()

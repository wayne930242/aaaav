"""The anchor gate, the decision trail tool, and the Jev second thought, replayed against stub pi events."""

import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.pi_harness import (
    SETTLE,
    SETTLED,
    ExtensionCase,
    assistant,
    bash_result,
    stage,
    todo_create,
    todo_state,
    tool_call,
    tool_result,
    user_start,
)


class TestAnchorGate(ExtensionCase):
    extensions = ("book.ts", "anchor-gate.ts")

    def warned_steps(self, out: dict, mention: str = "Reality anchor:") -> list[int]:
        for notice in out["notices"]:
            self.assertEqual(notice["level"], "warning")
            self.assertIn(mention, notice["message"])
        return [notice["step"] for notice in out["notices"]]

    def loop(self, kind: str | None = "inline") -> list[dict]:
        steps = [{"event": "session_start"}, user_start(), todo_create()]
        return steps + ([stage(stage="kind", kind=kind, intent="x")] if kind else [])

    def test_without_an_open_loop_nothing_is_gated(self):
        out = self.replay([{"event": "session_start"}, user_start(), tool_call("edit"), tool_call("write")])
        self.assertEqual(out["notices"], [])

    def test_in_a_loop_an_edit_without_an_anchor_warns_once_per_user_message_and_never_blocks(self):
        out = self.replay([*self.loop(), tool_call("edit"), tool_call("write"), user_start("now the import"), tool_call("edit")])
        self.assertEqual(out["results"][4:], [None, None, None, None])
        self.assertEqual(self.warned_steps(out), [4, 7])

    def test_an_edit_before_the_kind_is_declared_is_gated_like_inline(self):
        self.assertEqual(self.warned_steps(self.replay([*self.loop(None), tool_call("edit")])), [3])

    def test_a_quick_loop_is_not_gated(self):
        self.assertEqual(self.replay([*self.loop("quick"), tool_call("edit")])["notices"], [])

    def test_the_anchor_line_silences_the_warning_until_the_next_user_prompt(self):
        out = self.replay([
            *self.loop(),
            assistant("Alignment: fix it.\nReality anchor: pytest tests/test_export.py"),
            tool_call("write"),
            user_start("now the import"),
            tool_call("write"),
        ])
        self.assertEqual(self.warned_steps(out), [7])

    def test_an_anchor_stage_counts_as_the_anchor_for_the_whole_loop(self):
        out = self.replay([*self.loop(), stage(stage="anchor", check="pytest"), tool_call("edit"), user_start("again"), tool_call("edit")])
        self.assertEqual(out["notices"], [])

    def test_a_skipped_anchor_stage_counts_too(self):
        self.assertEqual(self.replay([*self.loop(), stage(stage="anchor", skip="no check exists"), tool_call("edit")])["notices"], [])

    def test_text_and_html_files_scratch_specs_temp_paths_and_other_tools_pass(self):
        out = self.replay([
            *self.loop(),
            tool_call("write", "README.md"),
            tool_call("edit", "notes/todo.TXT"),
            tool_call("write", "report/index.html"),
            tool_call("edit", "legacy/page.HTM"),
            tool_call("write", "scratch/friction.json"),
            tool_call("edit", "docs/specs/2026-10-21-x/design.html"),
            tool_call("write", str(Path(tempfile.gettempdir()) / "anchorloop-gate-outside" / "page.html")),
            tool_call("bash"),
        ])
        self.assertEqual(out["notices"], [])

    def test_a_user_message_that_steers_the_running_loop_rearms_the_warning(self):
        out = self.replay([*self.loop(), assistant("Reality anchor: pytest"), user_start("also rename it"), tool_call("edit")])
        self.assertEqual(self.warned_steps(out), [6])

    def test_resumed_session_ignores_an_anchor_stated_before_the_last_user_message(self):
        branch = [
            {"type": "message", "message": {"role": "assistant", "content": [{"type": "text", "text": "Reality anchor: pytest"}]}},
            {"type": "message", "message": {"role": "user", "content": "now the import"}},
        ]
        out = self.replay([{"event": "session_start"}, todo_create(), tool_call("edit")], branch=branch)
        self.assertEqual(self.warned_steps(out), [2])

    def test_resumed_session_keeps_an_anchor_stated_after_the_last_user_message(self):
        branch = [
            {"type": "message", "message": {"role": "user", "content": "fix it"}},
            {"type": "message", "message": {"role": "assistant", "content": [{"type": "text", "text": "Reality anchor: pytest"}]}},
        ]
        self.assertEqual(self.replay([{"event": "session_start"}, todo_create(), tool_call("edit")], branch=branch)["notices"], [])

    def spec(self, status: str) -> None:
        path = self.cwd / "docs" / "specs" / "2026-10-29-x" / "spec.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"Status: {status}\n\n# Spec\n")

    def durable(self) -> list[dict]:
        return [*self.loop("durable"), stage(stage="anchor", check="pytest"),
                tool_result("write", {"path": "docs/specs/2026-10-29-x/spec.md"})]

    def test_a_durable_production_edit_warns_once_while_the_spec_is_not_approved(self):
        self.spec("proposed")
        out = self.replay([*self.durable(), tool_call("edit"), tool_call("edit", "src/b.py")])
        self.assertEqual(self.warned_steps(out, "Status: approved"), [6])

    def test_a_durable_production_edit_with_an_approved_spec_is_silent(self):
        self.spec("approved")
        self.assertEqual(self.replay([*self.durable(), tool_call("edit")])["notices"], [])

    def test_a_durable_loop_with_no_recorded_spec_warns(self):
        out = self.replay([*self.loop("durable"), stage(stage="anchor", check="pytest"), tool_call("edit")])
        self.assertEqual(self.warned_steps(out, "Status: approved"), [5])

    def test_spec_and_doc_edits_in_a_durable_loop_are_not_production_edits(self):
        self.spec("proposed")
        out = self.replay([*self.durable(), tool_call("edit", "docs/specs/2026-10-29-x/design.md"), tool_call("write", "notes.md")])
        self.assertEqual(out["notices"], [])

    def test_an_inline_loop_ignores_the_spec_gate(self):
        self.spec("proposed")
        self.assertEqual(self.replay([*self.loop(), stage(stage="anchor", check="x"), tool_call("edit")])["notices"], [])


class TestDecisionTool(ExtensionCase):
    extension = "decision-tool.ts"

    def rows(self) -> list[list[str]]:
        return [line.split("\t") for line in (self.cwd / "scratch/decisions-t.tsv").read_text().splitlines()]

    def test_first_row_writes_the_header_and_cells_stay_single_line_and_formula_safe(self):
        self.replay([
            {"tool": "anchorloop_decision", "params": {"log": "scratch/decisions-t.tsv", "decision": "a\tb\nc",
                                                  "why": "=HYPERLINK(1)", "evidence": "-rf", "result": "@x"}},
        ])
        rows = self.rows()
        self.assertEqual(rows[0], ["ts", "decision", "why", "evidence", "result"])
        self.assertEqual(rows[1][1:], ["a b c", "'=HYPERLINK(1)", "'-rf", "'@x"])

    def test_start_row_names_the_run_and_the_rows_before_it(self):
        self.replay([
            {"tool": "anchorloop_decision", "params": {"log": "scratch/decisions-t.tsv", "decision": "first", "why": "w",
                                                  "evidence": "abc123", "result": "open"}},
            {"tool": "anchorloop_decision", "params": {"log": "scratch/decisions-t.tsv", "start": "worker-2"}},
        ])
        last = self.rows()[-1]
        self.assertEqual(last[1], "start")
        self.assertIn("1 earlier rows", last[2])
        self.assertEqual(last[3:], ["worker-2", "open"])

    def test_a_log_outside_the_scratch_trail_is_refused(self):
        out = self.replay([{"tool": "anchorloop_decision", "params": {"log": "src/app.py", "decision": "d", "why": "w",
                                                                   "evidence": "e", "result": "r"}}])
        self.assertIn("scratch/decisions-", out["results"][0]["error"])
        self.assertFalse((self.cwd / "src/app.py").exists())

    def test_missing_cells_fail_without_writing(self):
        out = self.replay([{"tool": "anchorloop_decision", "params": {"log": "scratch/decisions-t.tsv", "decision": "only"}}])
        self.assertIn("all required", out["results"][0]["error"])
        self.assertFalse((self.cwd / "scratch/decisions-t.tsv").exists())


class TestSecondThought(ExtensionCase):
    extensions = ("book.ts", "second-thought.ts")

    def loop(self, kind: str = "inline", *more: dict) -> list[dict]:
        return [user_start(), todo_create(), stage(stage="kind", kind=kind, intent="fix the export"), stage(stage="anchor", check="pytest -q"), *more]

    def settle_after(self, classify: object, *more: dict, kind: str = "inline", extra: list[dict] | None = None) -> dict:
        return self.replay([*self.loop(kind, *more), SETTLE, *(extra or [])], classify=classify)

    def test_without_a_loop_nothing_is_asked_or_recorded(self):
        out = self.replay([user_start(), tool_call("bash"), assistant("Done."), SETTLE], classify=answers("close", 0.9, "none", 2.9))
        self.assertIsNone(out["results"][3])
        self.assertEqual(out["classifyCalls"], [])

    def test_jev_sees_only_the_book_state_and_asks_the_next_stage_with_done_review_quality(self):
        self.git_repo()
        (self.cwd / "app.py").write_text("print(1)\nprint(2)\n")
        todos = todo_state({"subject": "build it", "status": "in_progress", "metadata": {"anchor": "pytest -q", "ref": "docs/x.md#Gone"}},
                           {"subject": "done", "status": "completed"})
        out = self.replay([
            user_start(), todo_create("build it", anchor="pytest -q", ref="docs/x.md#Gone"), todo_create("done", task_id=2, status="completed"),
            stage(stage="kind", kind="reviewed", intent="fix the export"), stage(stage="anchor", check="pytest -q"),
            {"event": "tool_call", "payload": {"toolName": "edit", "toolCallId": "e", "input": {"path": "app.py"}}},
            stage(stage="act"), {"branchAdd": [todos]}, bash_result("pytest -q", 0, "3 passed"), stage(stage="verify"), SETTLE,
        ], classify=answers("close", 0.9, "none", 2.9))
        (state,) = out["classifyCalls"]
        self.assertEqual(sorted(state), ["anchor", "diff", "intent", "kind", "tasks", "todos", "verify"])
        self.assertEqual((state["kind"], state["intent"], state["anchor"]), ("reviewed", "fix the export", "pytest -q"))
        self.assertIn("1 file changed", state["diff"])
        self.assertLessEqual(len(state["diff"]), 1200)
        self.assertIn("last check: exit 0 — 3 passed", state["verify"])
        self.assertEqual(state["todos"], "1 open of 2")
        legend, task = state["tasks"].splitlines()[:2]
        self.assertEqual(legend, "legend: #id status subject — anchor (last exit) — ref → line range; missing = heading gone")
        self.assertEqual(out["questionSets"], [["next", "done", "review", "quality"]])
        self.assertEqual(task, "#1 in_progress build it — pytest -q (exit 0) — docs/x.md#Gone → missing")

    def test_the_message_leads_with_the_suggestion_and_the_book_facts(self):
        check = [bash_result("pytest -q", 0, "3 passed"), stage(stage="verify")]
        out = self.settle_after(answers("close", 0.84, "none", 2.88), stage(stage="act"), *check)
        result = out["results"][-1]
        self.assertNotIn("continue", result)
        text = result["entries"][1]["content"]
        self.assertTrue(text.startswith("Second thought (Jev, advisory): next → close (verify exit 0 after the last change, no review, 0 open todos)"), text)
        self.assertEqual(result["entries"][0]["data"]["next"], "close")
        self.assertEqual(result["entries"][0]["data"]["concerns"], [])

    def test_a_verify_suggestion_continues_the_run_once_when_no_verify_follows_the_last_act(self):
        out = self.replay([*self.loop(), stage(stage="act"), SETTLE, stage(stage="act"), SETTLE], classify=answers("verify", 0.5, "none", 2.5))
        first, second = out["results"][5], out["results"][7]
        self.assertTrue(first["continue"])
        self.assertIn("verify missing", first["entries"][1]["content"])
        self.assertNotIn("continue", second)

    def test_a_verify_suggestion_does_not_continue_when_a_check_already_follows_the_last_act(self):
        out = self.settle_after(answers("verify", 0.5, "none", 2.5), stage(stage="act"), bash_result("pytest -q", 0, "ok"), stage(stage="verify"))
        self.assertNotIn("continue", out["results"][-1])

    def test_a_review_suggestion_continues_only_while_no_review_follows_the_last_act(self):
        missing = self.settle_after(answers("review", 0.5, "focused", 2.5), stage(stage="act"), kind="reviewed")
        self.assertTrue(missing["results"][-1]["continue"])
        reviewed = self.settle_after(answers("review", 0.5, "focused", 2.5), stage(stage="act"),
                                     stage(stage="review", note="ok"), kind="reviewed")
        self.assertNotIn("continue", reviewed["results"][-1])

    def test_a_fix_suggestion_continues_while_a_blocking_review_has_no_act_after_it(self):
        blocked = {"event": "message_end", "payload": {"message": {"role": "custom", "customType": "subagent_result",
                   "details": {"agent": "reviewer", "name": "r", "resultContent": "Blocking: P0=0 P1=1"}}}}
        out = self.settle_after(answers("fix", 0.2, "focused", 2.5), stage(stage="act"), blocked, stage(stage="review"), kind="reviewed")
        self.assertTrue(out["results"][-1]["continue"])
        fixed = self.settle_after(answers("fix", 0.2, "focused", 2.5), stage(stage="act"), blocked, stage(stage="review"), stage(stage="act"), kind="reviewed")
        self.assertNotIn("continue", fixed["results"][-1])

    def test_continue_close_and_ask_user_suggestions_never_continue_the_run(self):
        for choice in ("continue", "close", "ask-user"):
            out = self.settle_after(answers(choice, 0.5, "none", 2.5), stage(stage="act"))
            self.assertNotIn("continue", out["results"][-1], choice)
            self.assertIn(f"next → {choice}", out["results"][-1]["entries"][1]["content"])

    def test_a_run_is_judged_only_when_the_book_gained_an_entry_since_the_last_judgment(self):
        out = self.replay([*self.loop(), SETTLE, SETTLED, SETTLE, SETTLED, stage(stage="act"), SETTLE],
                          classify=answers("close", 0.9, "none", 2.9))
        self.assertIsNotNone(out["results"][4])
        self.assertIsNone(out["results"][6])
        self.assertIsNotNone(out["results"][9])
        self.assertEqual(len(out["classifyCalls"]), 2)

    def test_a_full_rating_is_noted_without_a_recheck_after_a_clean_review_that_follows_the_last_act(self):
        clean = {"event": "message_end", "payload": {"message": {"role": "custom", "customType": "subagent_result",
                 "details": {"agent": "reviewer", "name": "r", "resultContent": "**Blocking:** P0=0 P1=0"}}}}
        out = self.settle_after(answers("close", 0.9, "full", 2.9), stage(stage="act"), clean, stage(stage="review"), kind="reviewed")
        result = out["results"][-1]
        self.assertNotIn("continue", result)
        text = result["entries"][1]["content"]
        self.assertIn("no blocking finding", text)
        self.assertNotIn("needs full independent review", text)
        self.assertEqual(result["entries"][0]["data"]["concerns"], [])

    def test_a_full_rating_is_a_concern_when_no_clean_review_follows_the_last_act(self):
        out = self.settle_after(answers("review", 0.9, "full", 2.9), stage(stage="act"), kind="reviewed")
        self.assertIn("needs full independent review", out["results"][-1]["entries"][1]["content"])

    def test_low_done_and_quality_are_listed_as_concerns(self):
        out = self.settle_after(answers("continue", 0.05, "none", 0.5), stage(stage="act"))
        content = out["results"][-1]["entries"][1]["content"]
        self.assertIn("evidence not shown to cover the intent", content)
        self.assertIn("result below the intent", content)

    def test_a_close_tool_result_carries_the_advisory(self):
        steps = [*self.loop(), stage(stage="act"),
                 {"event": "tool_call", "payload": {"toolName": "anchorloop_stage", "toolCallId": "c9", "input": {"stage": "close", "verdict": "landed"}}},
                 stage(stage="close", verdict="landed"),
                 tool_result("anchorloop_stage", {"stage": "close", "verdict": "landed"}, "Loop closed (landed)", call_id="c9")]
        out = self.replay(steps, classify=answers("close", 0.9, "none", 2.9))
        result = out["results"][-1]
        self.assertEqual(result["content"][0]["text"], "Loop closed (landed)")
        self.assertIn("Second thought (Jev, advisory): next → close", result["content"][1]["text"])
        self.assertEqual(out["classifyCalls"][0]["intent"], "fix the export")
        self.assertEqual(self.book_files(), [])

    def test_a_refused_close_is_not_judged(self):
        todos = todo_state({"subject": "x", "status": "pending"})
        steps = [*self.loop(), {"branchAdd": [todos]},
                 {"event": "tool_call", "payload": {"toolName": "anchorloop_stage", "toolCallId": "c9", "input": {"stage": "close", "verdict": "landed"}}},
                 tool_result("anchorloop_stage", {"stage": "close"}, "refused", call_id="c9", isError=True)]
        out = self.replay(steps, classify=answers("close", 0.9, "none", 2.9))
        self.assertIsNone(out["results"][-1])
        self.assertEqual(out["classifyCalls"], [])

    def test_failure_records_unknown_and_continues_nothing(self):
        result = self.settle_after("throw", stage(stage="act"))["results"][-1]
        self.assertEqual(result["entries"][0]["data"], {"verdict": "unknown", "reason": "network down"})
        self.assertNotIn("continue", result)

    def test_without_a_key_or_a_classifier_nothing_is_asked_or_recorded(self):
        for plan in ("no-auth", "missing"):
            out = self.settle_after(plan)
            self.assertIsNone(out["results"][-1], plan)
            self.assertEqual(out["classifyCalls"], [], plan)

    def test_a_run_that_arranged_a_wake_is_not_judged(self):
        for tool in ("MonitorCreate", "subagent"):
            out = self.replay([*self.loop(), tool_call(tool), SETTLE], classify=answers("close", 0.9, "none", 2.9))
            self.assertIsNone(out["results"][-1], tool)
            self.assertEqual(out["classifyCalls"], [], tool)

    def test_a_subagent_session_is_never_judged(self):
        markers = [{"PI_SUBAGENT_ID": "child-1"}, {"PI_SUBAGENT_CHILD": "1"},
                   {"PI_SUBAGENT_CHILD_AGENT": "worker", "PI_SUBAGENT_PARENT_PID": "42"}]
        for env in markers:
            out = self.replay([*self.loop(), SETTLE], classify=answers("verify", 0.1, "full", 0), env=env)
            self.assertIsNone(out["results"][-1], env)
            self.assertEqual(out["classifyCalls"], [], env)


def answers(next_stage: str, done: float, review: str, quality: float) -> dict:
    return {
        "stopReason": "stop",
        "answers": {
            "next": {"type": "choice", "choice": next_stage, "probabilities": {next_stage: 0.7}},
            "done": {"type": "bool", "probability": done},
            "review": {"type": "choice", "choice": review, "probabilities": {review: 0.6}, "confidence": 0.4},
            "quality": {"type": "score", "score": quality, "confidence": 0.5},
        },
    }


if __name__ == "__main__":
    unittest.main()

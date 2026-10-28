"""The phase machine over the loop book: sequences per kind, completion from evidence, regression, skip and back, the read phase, reflect."""

import unittest

from tests.pi_harness import bash_result, stage, todo_create, tool_result
from tests.test_pi_book import BookCase, answers, edit, subagent_result, text_of

DIR = "docs/specs/2026-10-29-x"
OPEN_ROWS = "| Question | Answer | Basis | Status |\n|---|---|---|---|\n| Which db? | pg | req | grounded |\n| Cache? | | | open |\n"
DONE_ROWS = "| Question | Answer | Basis | Status |\n|---|---|---|---|\n| Which db? | pg | req | grounded |\n| Cache? | yes | user | confirmed |\n"
CLOSED_ROWS = "| Question | Answer | Basis | Status |\n|---|---|---|---|\n| Which db? | pg | req | grounded |\n"
DESIGN = "## Approach\n\nUse the existing table.\n"


def spec_text(status: str, approved_from: bool = False) -> str:
    return f"Status: {status}\n{'Approved from: user 2026-10-29' if approved_from else ''}\n\n# Spec\n\n## Behavior\n\nA.\n"


class PhaseCase(BookCase):
    extensions = ("book.ts",)

    def artifact(self, name: str, text: str) -> dict:
        path = self.cwd / DIR / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return tool_result("write", {"path": f"{DIR}/{name}"})

    def line(self, steps: list[dict], **kwargs) -> str:
        return self.read_text(steps, **kwargs).splitlines()[0]


class TestSequences(PhaseCase):
    def test_each_kind_starts_at_its_first_phase(self):
        quick = self.line(self.open_loop("quick"), session="s-quick")
        inline = self.line(self.open_loop("inline"), session="s-inline")
        durable = self.line(self.open_loop("durable"), session="s-durable")
        self.assertEqual(quick, "quick · phase start → act (missing: a change to the code)")
        self.assertTrue(inline.startswith("inline · phase start → anchor (missing: a `Reality anchor:` line"), inline)
        self.assertEqual(durable, "durable · phase start → decide (missing: decision.md with decision rows (no spec folder recorded))")

    def test_an_inline_loop_walks_anchor_act_verify_and_regresses_when_the_code_changes_again(self):
        steps = self.open_loop(anchor="pytest -q")
        self.assertEqual(self.line(steps), "inline · phase anchor ✓ → act (missing: a change to the code)")
        self.assertEqual(self.line([edit()]), "inline · phase act ✓ → verify (missing: a passing run of `pytest -q` after the last change)")
        self.assertEqual(self.line([bash_result("pytest -q", 1, "1 failed")]), "inline · phase act ✓ → fix (missing: the anchor exited 1 after the last change)")
        self.assertIn("→ verify (missing", self.line([edit()]))
        self.assertEqual(self.line([bash_result("pytest -q", 0, "ok")]), "inline · phase verify ✓ → close")
        self.assertIn("phase act ✓ → verify", self.line([edit()]))

    def test_a_reviewed_loop_needs_a_clear_review_after_the_last_change(self):
        self.replay([*self.open_loop("reviewed", anchor="pytest"), edit(), bash_result("pytest", 0, "ok")])
        self.assertIn("phase verify ✓ → review (missing: a review round after the last change", self.line([]))
        self.assertIn("→ fix (missing: blocking review findings are open)", self.line([subagent_result("reviewer", "r1", "Blocking: P0=0 P1=1")]))
        self.replay([edit(), bash_result("pytest", 0, "ok")])
        self.assertIn("→ review (missing: a review round after the last change", self.line([]))
        self.assertEqual(self.line([subagent_result("reviewer", "r2", "Blocking: P0=0 P1=0")]), "reviewed · phase review ✓ → close")

    def test_two_blocking_rounds_in_a_row_ask_for_the_user(self):
        self.replay([*self.open_loop("reviewed", anchor="pytest"), edit(), bash_result("pytest", 0, "ok"), subagent_result("reviewer", "r1", "Blocking: P0=0 P1=2"),
                     edit(), bash_result("pytest", 0, "ok"), subagent_result("reviewer", "r2", "Blocking: P0=0 P1=1")])
        self.assertIn("two consecutive review rounds still blocking: hand the trend to the user", self.line([]))

    def test_a_declared_verify_completes_the_phase_of_a_loop_whose_anchor_is_not_a_command(self):
        stated = {"event": "message_end", "payload": {"message": {"role": "assistant", "content": [{"type": "text", "text": "Reality anchor: the page shows the new column"}]}}}
        self.replay([*self.open_loop(), stated, edit()])
        self.assertEqual(self.line([]), "inline · phase act ✓ → verify (missing: a verify declaration (the anchor is not a command))")
        self.assertEqual(self.line([stage(stage="verify", note="the column is there")]), "inline · phase verify ✓ → close")
        self.assertIn("phase act ✓ → verify", self.line([edit(), bash_result("ls", 0, "x")]))

    def test_the_reality_anchor_line_counts_as_the_anchor_phase_and_never_as_a_command(self):
        stated = {"event": "message_end", "payload": {"message": {"role": "assistant", "content": [{"type": "text", "text": "Alignment: x\nReality anchor: pytest tests/x.py, once at the end"}]}}}
        self.replay([*self.open_loop(), stated, edit(), bash_result("pytest tests/x.py", 0, "ok")])
        self.assertEqual(self.entries("anchor")[0]["line"], True)
        self.assertEqual(self.entries("verify"), [])
        self.assertIn("phase act ✓ → verify (missing: a verify declaration", self.line([]))

    def test_a_bare_reality_anchor_line_still_counts(self):
        stated = {"event": "message_end", "payload": {"message": {"role": "assistant", "content": [{"type": "text", "text": "Reality anchor:\n- pytest"}]}}}
        self.replay([*self.open_loop(), stated])
        self.assertEqual(self.line([]), "inline · phase anchor ✓ → act (missing: a change to the code)")

    def test_a_reality_anchor_line_stated_before_the_loop_opened_counts_once_it_opens(self):
        branch = [{"type": "message", "message": {"role": "user", "content": "fix"}},
                  {"type": "message", "message": {"role": "assistant", "content": [{"type": "text", "text": "Reality anchor: pytest"}]}}]
        self.replay([todo_create(), stage(stage="kind", kind="inline", intent="x")], branch=branch)
        self.assertEqual(self.entries("anchor")[0]["check"], "pytest")


class TestDurable(PhaseCase):
    def test_a_durable_loop_walks_decide_grill_spec_read_approve_design_anchor(self):
        self.replay(self.open_loop("durable"))
        self.assertIn("phase decide ✓ → grill (missing: 1 open decision row)", self.line([self.artifact("decision.md", OPEN_ROWS)]))
        self.assertIn("phase grill ✓ → spec (missing: spec.md with Status: proposed)", self.line([self.artifact("decision.md", DONE_ROWS)]))
        self.assertIn("phase spec ✓ → read (missing: a fresh-context read of the spec", self.line([self.artifact("spec.md", spec_text("proposed"))]))
        self.assertIn("phase read ✓ → approve (missing: spec.md Status: approved with Approved from (now proposed))", self.line([stage(stage="fresh-read", note="a new session")]))
        self.assertIn("phase approve ✓ → design (missing: design.md with its approach section filled)", self.line([self.artifact("spec.md", spec_text("approved", True))]))
        self.assertIn("phase design ✓ → anchor (missing:", self.line([self.artifact("design.md", DESIGN)]))
        self.assertEqual(self.line([stage(stage="kind", anchor="pytest -q")]), "durable · phase anchor ✓ → act (missing: a change to the code)")

    def test_a_spec_edited_back_to_proposed_regresses_approve_and_what_follows(self):
        self.replay([*self.open_loop("durable", anchor="pytest -q"), self.artifact("decision.md", DONE_ROWS), self.artifact("spec.md", spec_text("proposed")),
                     stage(stage="fresh-read"), self.artifact("design.md", DESIGN)])
        self.replay([self.artifact("spec.md", spec_text("approved", True))])
        self.assertTrue(self.line([]).startswith("durable · phase anchor ✓ → act (missing: a change to the code)"))
        self.assertIn("phase read ✓ → approve (missing: spec.md Status: approved with Approved from (now proposed))", self.line([self.artifact("spec.md", spec_text("proposed"))]))

    def test_a_spec_that_names_no_approval_is_not_approved(self):
        self.replay([*self.open_loop("durable"), self.artifact("decision.md", DONE_ROWS), self.artifact("spec.md", spec_text("proposed")), stage(stage="fresh-read")])
        self.assertIn("→ approve (missing: spec.md Status: approved with Approved from (now approved))", self.line([self.artifact("spec.md", spec_text("approved", False))]))

    def test_grill_is_skipped_by_itself_when_the_decision_table_never_had_an_open_row(self):
        text = self.line([*self.open_loop("durable"), self.artifact("decision.md", CLOSED_ROWS)])
        self.assertIn("phase decide ✓ → spec", text)
        self.assertIn("skipped: grill (no open rows)", text)

    def test_a_design_with_an_empty_approach_is_not_designed(self):
        self.replay([*self.open_loop("durable"), self.artifact("decision.md", DONE_ROWS), self.artifact("spec.md", spec_text("approved", True)), stage(stage="fresh-read")])
        self.assertIn("→ design (missing:", self.line([self.artifact("design.md", "## Approach\n\n## Risks\n\nY.\n")]))

    def test_a_pickup_loop_finds_the_spec_through_its_intent_and_reads_artifacts_from_disk(self):
        for name, text in (("decision.md", DONE_ROWS), ("spec.md", spec_text("approved", True)), ("design.md", DESIGN)):
            self.artifact(name, text)
        line = self.line(self.open_loop("durable", intent=f"implement {DIR}", anchor="pytest -q"))
        self.assertEqual(line, "durable · phase anchor ✓ → act (missing: a change to the code)")

    def test_a_pickup_loop_names_the_spec_in_a_todo_ref(self):
        for name, text in (("decision.md", DONE_ROWS), ("spec.md", spec_text("approved", True))):
            self.artifact(name, text)
        steps = [todo_create("build", ref=f"{DIR}/spec.md#Behavior"), stage(stage="kind", kind="durable", intent="build it")]
        self.assertIn("phase approve ✓ → design", self.line(steps))


class TestRead(PhaseCase):
    BRIEF = f"You have no context. Read {DIR}/spec.md, restate the contract, and list what you had to guess."

    def proposed(self) -> list[dict]:
        return [*self.open_loop("durable"), self.artifact("decision.md", DONE_ROWS), self.artifact("spec.md", spec_text("proposed"))]

    def goldfish(self) -> list[dict]:
        return self.entries("goldfish")

    def test_a_returned_subagent_whose_brief_names_the_spec_is_judged_by_jev_as_a_fresh_read(self):
        self.replay(self.proposed())
        out = self.replay([subagent_result("scout", "fresh", "Contract: A. Guessed: none.", self.BRIEF)], classify=answers(fresh_read=0.9))
        (entry,) = self.goldfish()
        self.assertEqual((entry["source"], entry["ok"], entry["child"]), ("jev", True, "fresh"))
        self.assertEqual(out["classifyCalls"][0]["brief"], self.BRIEF)
        self.assertIn("phase read ✓ → approve", self.line([]))

    def test_the_spec_path_is_only_a_pre_filter(self):
        self.replay(self.proposed())
        out = self.replay([subagent_result("scout", "other", "done", "Look at src/app.py"), subagent_result("scout", "again", "done", "Look at docs")], classify=answers(fresh_read=0.9))
        self.assertEqual((self.goldfish(), out["classifyCalls"]), ([], []))
        self.replay([subagent_result("worker", "fixer", "I fixed it", self.BRIEF)], classify=answers(fresh_read=0.1))
        (entry,) = self.goldfish()
        self.assertFalse(entry["ok"])
        self.assertIn("phase spec ✓ → read", self.line([]))

    def test_without_a_jev_key_the_read_stays_missing_for_the_manual_declaration(self):
        self.replay(self.proposed())
        self.replay([subagent_result("scout", "fresh", "ok", self.BRIEF)], classify="no-auth")
        self.assertEqual(self.goldfish(), [])
        self.replay([stage(stage="fresh-read", note="read by hand")])
        self.assertEqual((self.goldfish()[0]["source"], self.goldfish()[0]["note"]), ("declared", "read by hand"))
        self.assertIn("phase read ✓ → approve", self.line([]))

    def test_a_manual_declaration_skips_detection(self):
        self.replay([*self.proposed(), stage(stage="fresh-read")])
        out = self.replay([subagent_result("scout", "fresh", "ok", self.BRIEF)], classify=answers(fresh_read=0.9))
        self.assertEqual(out["classifyCalls"], [])
        self.assertEqual(len(self.goldfish()), 1)

    def test_no_detection_happens_before_the_spec_is_proposed(self):
        self.replay([*self.open_loop("durable"), self.artifact("decision.md", DONE_ROWS), self.artifact("spec.md", spec_text("draft"))])
        out = self.replay([subagent_result("scout", "early", "ok", self.BRIEF)], classify=answers(fresh_read=0.9))
        self.assertEqual(out["classifyCalls"], [])


class TestSkipAndBack(PhaseCase):
    def test_skip_names_a_phase_of_the_kind_and_the_reason_shows_in_the_phase_line(self):
        out = self.replay([*self.open_loop(), stage(stage="skip", phase="decide", reason="x"), stage(stage="skip", phase="close", reason="x"), stage(stage="skip", phase="anchor"),
                           stage(stage="skip", phase="anchor", reason="a typo")])
        self.assertIn("one of anchor, act, verify, reflect", out["results"][2]["error"])
        self.assertIn("phase", out["results"][3]["error"])
        self.assertIn("reason", out["results"][4]["error"])
        self.assertEqual(self.line([]), "inline · phase start → act (missing: a change to the code) · skipped: anchor (a typo)")

    def test_a_skipped_phase_counts_for_the_ones_after_it(self):
        self.replay([*self.open_loop(), stage(stage="skip", phase="anchor", reason="no check exists")])
        self.assertEqual(self.line([edit(), stage(stage="skip", phase="verify", reason="docs only")]), "inline · phase act ✓ → close · skipped: anchor (no check exists), verify (docs only)")

    def test_back_makes_a_phase_and_those_after_it_count_only_on_new_evidence(self):
        self.replay([*self.open_loop(anchor="pytest -q"), edit(), bash_result("pytest -q", 0, "ok")])
        self.assertEqual(self.line([]), "inline · phase verify ✓ → close")
        self.assertEqual(self.line([stage(stage="back", phase="act", reason="the first try was wrong")]),
                         "inline · phase anchor ✓ → act (missing: a change to the code) · back: act (the first try was wrong)")
        self.assertIn("phase act ✓ → verify", self.line([edit()]))
        self.assertEqual(self.line([bash_result("pytest -q", 0, "ok")]).split(" · back")[0], "inline · phase verify ✓ → close")

    def test_back_to_an_artifact_phase_needs_a_new_write(self):
        self.replay([*self.open_loop("durable"), self.artifact("decision.md", DONE_ROWS), self.artifact("spec.md", spec_text("proposed"))])
        self.assertIn("phase decide ✓ → spec", self.line([stage(stage="back", phase="spec", reason="rewrite the contract")]))
        self.assertIn("phase spec ✓ → read", self.line([self.artifact("spec.md", spec_text("proposed"))]))

    def test_back_validates_its_phase_and_reason(self):
        out = self.replay([*self.open_loop(), stage(stage="back", phase="review", reason="x"), stage(stage="back", phase="act")])
        self.assertIn("one of", out["results"][2]["error"])
        self.assertIn("reason", out["results"][3]["error"])

    def test_the_close_summary_and_session_entry_show_skips_and_backs(self):
        out = self.replay([*self.open_loop(), stage(stage="skip", phase="anchor", reason="no check"), edit(), stage(stage="back", phase="act", reason="redo"), edit(),
                           stage(stage="skip", phase="verify", reason="docs"), stage(stage="close", verdict="landed")])
        text = text_of(out["results"][-1])
        self.assertIn("skipped anchor (no check), verify (docs); back act (redo)", text)
        data = out["appended"][0]["data"]
        self.assertEqual((data["skipped"], data["back"]), (["anchor (no check)", "verify (docs)"], ["act (redo)"]))


class TestCloseAndReflect(PhaseCase):
    def test_closing_with_incomplete_phases_warns_in_one_line_and_never_refuses(self):
        out = self.replay([*self.open_loop(anchor="pytest -q"), stage(stage="close", verdict="landed")])
        text = text_of(out["results"][-1])
        self.assertIn("Loop closed (landed)", text)
        warning = text.splitlines()[-1]
        self.assertTrue(warning.startswith("anchorloop: close comes before act (a change to the code); verify ("), warning)
        self.assertIn("skip with `anchorloop_stage skip act <reason>`", warning)

    def test_closing_as_abandoned_or_blocked_is_not_a_jump(self):
        out = self.replay([*self.open_loop(anchor="pytest -q"), stage(stage="close", verdict="abandoned")])
        self.assertNotIn("anchorloop:", text_of(out["results"][-1]))

    def test_a_quick_loop_gets_one_reminder_at_close_and_nothing_before(self):
        out = self.replay([*self.open_loop("quick", anchor="make lint"), edit(), stage(stage="close", verdict="landed")])
        self.assertTrue(text_of(out["results"][-1]).splitlines()[-1].startswith("anchorloop: closing a quick loop with check ("))

    def test_reflect_is_the_last_phase_before_close_and_completes_when_every_friction_has_a_reflect(self):
        self.replay([*self.open_loop(anchor="pytest -q"), edit(), bash_result("pytest -q", 0, "ok")])
        self.assertEqual(self.line([]), "inline · phase verify ✓ → close")
        self.assertIn("phase verify ✓ → reflect (missing: 1 friction entry without a reflect)", self.line([stage(stage="friction", tried="a", found="b")]))
        self.assertEqual(self.line([stage(stage="reflect", friction=[1], **{"class": "gap"})]), "inline · phase reflect ✓ → close")

    def test_closing_with_unreflected_friction_is_a_jump_that_warns_and_lists_it(self):
        out = self.replay([*self.open_loop(anchor="pytest -q"), edit(), bash_result("pytest -q", 0, "ok"), stage(stage="friction", tried="a", found="b"), stage(stage="close", verdict="landed")])
        text = text_of(out["results"][-1])
        self.assertIn("Unreflected friction for the Reflexive Pass: 1 (b)", text)
        self.assertIn("anchorloop: close comes before reflect (1 friction entry without a reflect)", text)

    def test_reflect_can_be_skipped(self):
        self.replay([*self.open_loop(anchor="pytest -q"), edit(), bash_result("pytest -q", 0, "ok"), stage(stage="friction", tried="a", found="b")])
        self.assertIn("skipped: reflect (resolved in the change)", self.line([stage(stage="skip", phase="reflect", reason="resolved in the change")]))


if __name__ == "__main__":
    unittest.main()

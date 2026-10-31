"""2.4.0: anchor reruns record their own one-line friction, and the footer shows the loop's kind and phase."""

from tests.pi_harness import bash_result, stage, todo_create, todo_update, tool_result
from tests.test_pi_book import BookCase, edit, text_of

PYTEST_FAIL = "\n".join([
    "============================= test session starts ==============================",
    "tests/test_x.py F",
    "    def test_x():",
    ">       assert add(1, 2) == 4",
    "E       assert 3 == 4",
    "Traceback (most recent call last):",
    '  File "x.py", line 3, in <module>',
    "FAILED tests/test_x.py::test_x - assert 3 == 4",
    "========================= 1 failed, 4 passed in 0.12s ==========================",
])


class TestAutoFriction(BookCase):
    def rerun(self, failing_output: str = PYTEST_FAIL, between: list | None = None) -> dict:
        return self.replay([
            *self.open_loop(anchor="pytest -q"), edit(), bash_result("pytest -q", 0, "5 passed"),
            edit(), bash_result("pytest -q", 1, failing_output), *(between or []),
            edit(), bash_result("pytest -q", 0, "5 passed"),
        ])

    def test_a_rerun_that_passes_again_records_one_short_friction_line(self):
        out = self.rerun()
        [friction] = self.entries("friction")
        self.assertTrue(friction["auto"])
        self.assertIn("pytest -q", friction["tried"])
        self.assertIn("FAILED tests/test_x.py::test_x - assert 3 == 4", friction["found"])
        self.assertLessEqual(len(friction["found"]), 120)
        self.assertNotIn("Traceback", friction["found"])
        self.assertIn("friction #1 recorded", text_of(out["results"][-1]))
        self.assertEqual(self.entries("friction"), [friction])

    def test_the_key_line_is_cut_to_120_characters(self):
        self.rerun("error: " + "x" * 400)
        [friction] = self.entries("friction")
        self.assertLessEqual(len(friction["found"]), 120)
        self.assertLessEqual(max(len(entry.get("key", "")) for entry in self.entries("verify")), 120)
        self.assertTrue(friction["found"].endswith("…"))

    def test_stack_frames_never_stand_in_for_the_key_line(self):
        self.rerun('boom happened\n  File "lib/error_utils.py", line 3, in run\n    at handleError (lib/x.js:1:1)')
        self.assertEqual(self.entries("friction")[0]["found"], "boom happened")

    def test_without_an_error_line_the_last_line_is_kept(self):
        self.rerun("compiling\n3 checks did not pass")
        self.assertIn("3 checks did not pass", self.entries("friction")[0]["found"])

    def test_red_first_work_records_nothing(self):
        self.replay([*self.open_loop(anchor="pytest -q"), edit(), bash_result("pytest -q", 1, PYTEST_FAIL), edit(), bash_result("pytest -q", 0, "ok")])
        self.assertEqual(self.entries("friction"), [])

    def test_a_friction_the_agent_recorded_after_the_failure_is_not_doubled(self):
        self.rerun(between=[stage(stage="friction", tried="pytest -q after the rename", found="import path changed")])
        self.assertEqual([entry.get("auto", False) for entry in self.entries("friction")], [False])

    def test_a_task_anchor_rerun_records_friction_too(self):
        task = {"id": 1, "subject": "write the fix", "status": "in_progress", "metadata": {"anchor": "npm test"}}
        update = tool_result("todo", {"action": "update", "id": 1, "status": "in_progress"}, "updated", details={"tasks": [task], "nextId": 2})
        self.replay([*self.open_loop(anchor="pytest -q"), update, edit(), bash_result("npm test", 0, "ok"), edit(),
                     bash_result("npm test", 1, "Error: expected 2 got 3\n    at foo (a.js:1:1)"), edit(), bash_result("npm test", 0, "ok")])
        [friction] = self.entries("friction")
        self.assertIn("npm test", friction["tried"])
        self.assertIn("Error: expected 2 got 3", friction["found"])

    def test_the_auto_friction_still_waits_for_a_reflect_before_close(self):
        self.rerun()
        out = self.replay([stage(stage="read")])
        self.assertIn("1 friction entry without a reflect", text_of(out["results"][-1]))
        out = self.replay([stage(stage="reflect", friction=[1], **{"class": "resolved"}), stage(stage="read")])
        self.assertNotIn("without a reflect", text_of(out["results"][-1]))


class TestFooterStatus(BookCase):
    def last_status(self, out: dict) -> str | None:
        mine = [status for status in out["statuses"] if status["key"] == "anchorloop"]
        return mine[-1]["text"] if mine else "never set"

    def test_the_footer_names_the_kind_and_the_phase(self):
        out = self.replay([*self.open_loop(kind="reviewed", anchor="pytest -q"), edit(), bash_result("pytest -q", 0, "ok")])
        self.assertEqual(self.last_status(out), "anchorloop reviewed · verify ✓ → review")

    def test_a_failed_check_shows_fix_next(self):
        out = self.replay([*self.open_loop(anchor="pytest -q"), edit(), bash_result("pytest -q", 1, "1 failed")])
        self.assertEqual(self.last_status(out), "anchorloop inline · act ✓ → fix")

    def test_unreflected_friction_is_counted(self):
        out = self.replay([*self.open_loop(anchor="pytest -q"), stage(stage="friction", tried="a", found="b")])
        self.assertTrue(self.last_status(out).endswith(" · 1 friction to reflect"))

    def test_an_undeclared_loop_says_so(self):
        out = self.replay([todo_create()])
        self.assertEqual(self.last_status(out), "anchorloop no kind · start → anchor")

    def test_closing_the_loop_clears_the_footer(self):
        out = self.replay([*self.open_loop(kind="quick"), stage(stage="skip", phase="act", reason="nothing"), todo_update(1, "write the fix", "completed"),
                           stage(stage="close", verdict="abandoned")])
        self.assertIsNone(self.last_status(out))

    def test_session_start_shows_an_open_loop_again(self):
        self.replay([*self.open_loop(anchor="pytest -q")])
        out = self.replay([{"event": "session_start", "payload": {}}])
        self.assertEqual(self.last_status(out), "anchorloop inline · anchor ✓ → act")

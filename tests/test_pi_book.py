"""The loop book: opening on todo create, stages with attached evidence, durable artifacts, closing, sweeping."""

import json
import subprocess
import unittest
from pathlib import Path

from tests.pi_harness import (
    ExtensionCase,
    bash_result,
    stage,
    todo_create,
    todo_state,
    todo_update,
    tool_result,
)


def reviewer_result(text: str, agent: str = "reviewer") -> dict:
    message = {"role": "custom", "customType": "subagent_result", "details": {"name": "r1", "agent": agent, "resultContent": text}}
    return {"event": "message_end", "payload": {"message": message}}


def text_of(result: dict) -> str:
    return "\n".join(block["text"] for block in result["content"])


def answers(**probabilities: float) -> dict:
    return {"stopReason": "stop", "answers": {name: {"type": "bool", "probability": value} for name, value in probabilities.items()}}


class BookCase(ExtensionCase):
    extension = "book.ts"

    def open_loop(self, kind: str = "inline", intent: str = "fix the export") -> list[dict]:
        return [todo_create(), stage(stage="kind", kind=kind, intent=intent)]


class TestLifecycle(BookCase):
    def test_nothing_is_recorded_without_a_loop(self):
        out = self.replay([stage(stage="kind", kind="inline", intent="x"), stage(stage="read")])
        self.assertIn("No loop is open", text_of(out["results"][0]))
        self.assertEqual(self.book_files(), [])

    def test_the_first_todo_create_opens_a_loop_and_a_later_one_extends_it(self):
        out = self.replay([todo_create("first"), todo_create("second")])
        self.assertIn("anchorloop_stage", text_of(out["results"][0]))
        self.assertIn("created", text_of(out["results"][0]))
        self.assertIsNone(out["results"][1])
        self.assertEqual(len(self.book_files()), 1)
        header, entries = self.book()
        self.assertEqual((header["owner"], header["session"], [e["stage"] for e in entries]), ("main", str(self.session_file), ["task"]))

    def test_todo_calls_other_than_create_do_not_open_a_loop(self):
        self.replay([tool_result("todo", {"action": "list"}), tool_result("todo", {"action": "update", "id": 1})])
        self.assertEqual(self.book_files(), [])

    def test_a_second_kind_declaration_upgrades_the_open_loop(self):
        out = self.replay([*self.open_loop("inline"), stage(stage="kind", kind="reviewed"), stage(stage="read")])
        self.assertEqual(len(self.book_files()), 1)
        self.assertIn("kind changed: inline → reviewed", text_of(out["results"][2]))
        self.assertIn("kind: reviewed — fix the export", text_of(out["results"][3]))
        self.assertEqual(self.stages(), ["kind", "kind"])

    def test_the_first_kind_needs_an_intent(self):
        out = self.replay([todo_create(), stage(stage="kind", kind="quick")])
        self.assertIn("intent", out["results"][1]["error"])

    def test_any_stage_accepts_a_skip_reason(self):
        self.replay([*self.open_loop(), stage(stage="anchor", skip="a typo")])
        self.assertEqual(self.book()[1][-1]["skip"], "a typo")

    def test_close_refuses_while_a_todo_lacks_a_disposition_and_lists_it(self):
        todos = todo_state(
            {"subject": "ship it", "status": "in_progress"},
            {"subject": "ticketed", "status": "pending", "metadata": {"followup": "MP-12"}},
            {"subject": "vague", "status": "pending", "metadata": {"followup": "later"}},
            {"subject": "done", "status": "completed"},
        )
        out = self.replay([*self.open_loop(), {"branchAdd": [todos]}, stage(stage="close", verdict="landed")])
        error = out["results"][3]["error"]
        self.assertIn("#1 ship it", error)
        self.assertIn("#3 vague", error)
        self.assertNotIn("ticketed", error)
        self.assertNotIn("done", error)
        self.assertEqual(len(self.book_files()), 1)
        self.assertEqual(out["appended"], [])

    def test_close_records_one_session_entry_and_deletes_the_book_and_its_children(self):
        child = self.books / "x" / "agents" / "kid.yml"
        child.parent.mkdir(parents=True)
        child.write_text('id: "kid"\nsession: null\nentries:\n')
        todos = todo_state(
            {"subject": "a", "status": "pending", "metadata": {"followup": "MP-12"}},
            {"subject": "b", "status": "pending", "metadata": {"followup": "memory"}},
            {"subject": "c", "status": "in_progress", "metadata": {"followup": "drop — superseded"}},
        )
        link = tool_result("subagent", {}, "started", details={"id": "kid", "name": "w", "agent": "worker", "status": "started"})
        out = self.replay([*self.open_loop(), stage(stage="anchor", check="pytest -q"), link, {"branchAdd": [todos]},
                           stage(stage="close", verdict="landed")])
        self.assertIn("Loop closed (landed)", text_of(out["results"][-1]))
        self.assertIn("todo", text_of(out["results"][-1]))
        self.assertEqual(self.book_files(), [])
        self.assertFalse(child.exists())
        (entry,) = out["appended"]
        self.assertEqual(entry["customType"], "anchorloop-loop")
        data = entry["data"]
        self.assertEqual((data["intent"], data["kind"], data["verdict"]), ("fix the export", "inline", "landed"))
        self.assertEqual(data["stages"], ["kind", "anchor"])
        self.assertEqual(data["reviewRounds"], 0)
        self.assertEqual([f["followup"] for f in data["followups"]], ["MP-12", "memory", "drop — superseded"])

    def test_a_new_loop_can_open_once_the_old_one_is_closed(self):
        self.replay([*self.open_loop(), stage(stage="close", verdict="abandoned")])
        self.assertEqual(self.book_files(), [])
        self.replay([todo_create()])
        self.assertEqual(len(self.book_files()), 1)

    def test_read_summarizes_in_about_five_lines(self):
        out = self.replay([*self.open_loop(), stage(stage="anchor", check="pytest -q"), stage(stage="read")])
        lines = text_of(out["results"][3]).splitlines()
        self.assertEqual(len(lines), 4)
        self.assertTrue(lines[0].startswith("kind: inline"))
        self.assertIn("stages: kind, anchor", lines[1])


class TestEvidence(BookCase):
    def test_check_attaches_the_exit_code_and_last_line_of_the_latest_matching_bash_call(self):
        out = self.replay([
            *self.open_loop(),
            stage(stage="anchor", check="pytest -q"),
            bash_result("cd tests && pytest -q 2>&1 | tail", 1, "collected 3\n1 failed\n"),
            bash_result("ls", 0, "files\n"),
            stage(stage="verify"),
            bash_result("pytest -q", 0, "3 passed\n"),
            stage(stage="verify"),
        ])
        self.assertIn("exit 1 — 1 failed", text_of(out["results"][5]))
        self.assertIn("exit 0 — 3 passed", text_of(out["results"][7]))
        verify = [entry for entry in self.book()[1] if entry["stage"] == "verify"]
        self.assertEqual([(e["exit"], e["last"]) for e in verify], [(1, "1 failed"), (0, "3 passed")])

    def test_check_is_unknown_when_no_bash_call_ran_the_anchor(self):
        out = self.replay([*self.open_loop(), stage(stage="anchor", check="pytest -q"), bash_result("ls", 0, "x"), stage(stage="verify")])
        self.assertIn("exit unknown", text_of(out["results"][4]))
        self.assertEqual(self.book()[1][-1]["exit"], "unknown")

    def test_a_quick_loop_takes_the_command_on_the_check_call(self):
        out = self.replay([*self.open_loop("quick"), bash_result("make lint", 2, "2 errors\n"), stage(stage="check", check="make lint")])
        self.assertIn("exit 2 — 2 errors", text_of(out["results"][3]))

    def test_act_attaches_the_diff_against_the_base_head_of_each_repo(self):
        self.git_repo()
        other = self.cwd.parent / "other"
        other.mkdir()
        for args in (["init", "-q"], ["config", "user.email", "t@example.com"], ["config", "user.name", "t"]):
            subprocess.run(["git", "-C", str(other), *args], check=True, capture_output=True)
        (other / "lib.py").write_text("x = 1\n")
        subprocess.run(["git", "-C", str(other), "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(other), "commit", "-qm", "base"], check=True, capture_output=True)
        head = subprocess.run(["git", "-C", str(self.cwd), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        steps = [*self.open_loop(), {"event": "tool_call", "payload": {"toolName": "edit", "toolCallId": "e1", "input": {"path": str(other / "lib.py")}}}]
        self.replay(steps)
        (self.cwd / "app.py").write_text("print(1)\nprint(2)\n")
        (other / "lib.py").write_text("x = 2\ny = 3\n")
        out = self.replay([stage(stage="act")])
        bases = [entry for entry in self.book()[1] if entry["stage"] == "base"]
        self.assertEqual([Path(b["repo"]).name for b in bases], ["work", "other"])
        self.assertEqual(bases[0]["head"], head)
        diff = text_of(out["results"][0])
        self.assertIn("work: 1 file changed", diff)
        self.assertIn("other: 1 file changed", diff)

    def test_a_repo_is_added_once_at_its_first_touch(self):
        self.git_repo()
        edit = {"event": "tool_call", "payload": {"toolName": "write", "toolCallId": "e1", "input": {"path": "app.py"}}}
        self.replay([*self.open_loop(), edit, edit])
        self.assertEqual(self.stages().count("base"), 1)


class TestReview(BookCase):
    def test_review_counts_come_from_the_latest_reviewer_blocking_line(self):
        out = self.replay([
            *self.open_loop("reviewed"),
            reviewer_result("Findings...\n\n**Blocking:** P0=0 P1=2\n"),
            stage(stage="review"),
            reviewer_result("Round two.\nBlocking: P0=0 P1=1"),
            stage(stage="review"),
            reviewer_result("Clean.\n**Blocking: P0=0 P1=0**"),
            stage(stage="review"),
        ])
        reviews = [entry for entry in self.book()[1] if entry["stage"] == "review"]
        self.assertEqual([(e["round"], e["p0"], e["p1"], e["blocking"]) for e in reviews], [(1, 0, 2, True), (2, 0, 1, True), (3, 0, 0, False)])
        self.assertNotIn("hand the trend", text_of(out["results"][3]))
        self.assertIn("hand the trend to the user", text_of(out["results"][5]))
        self.assertNotIn("hand the trend", text_of(out["results"][7]))

    def test_an_adversarial_reviewer_counts_and_other_agents_do_not(self):
        self.replay([*self.open_loop("reviewed"), reviewer_result("Blocking: P0=1 P1=0", "worker"), reviewer_result("Blocking: P0=0 P1=3", "adversarial-reviewer"),
                     stage(stage="review")])
        self.assertEqual(self.book()[1][-1]["p1"], 3)

    def test_without_a_blocking_line_jev_answers_whether_findings_block(self):
        out = self.replay([*self.open_loop("reviewed"), stage(stage="review", note="found a P1 race in the cache")], classify=answers(blocking=0.9))
        self.assertEqual((self.book()[1][-1]["blocking"], self.book()[1][-1]["source"]), (True, "jev"))
        self.assertIn("blocking yes", text_of(out["results"][2]))
        self.assertEqual(out["classifyCalls"], [{"review": "found a P1 race in the cache"}])

    def test_without_a_blocking_line_or_a_jev_key_the_finding_state_is_unknown(self):
        self.replay([*self.open_loop("reviewed"), stage(stage="review", note="looks fine")], classify="no-auth")
        self.assertIsNone(self.book()[1][-1]["blocking"])

    def test_only_the_main_session_records_review_and_verify(self):
        env = {"PI_SUBAGENT_ID": "kid", "PI_SUBAGENT_NAME": "w", "PI_SUBAGENT_SESSION": str(self.session_file)}
        out = self.replay([*self.open_loop(), stage(stage="verify"), stage(stage="review")], env=env)
        child = self.books.rglob("kid.yml").__next__()
        self.assertEqual(self.stages(child), ["kind", "check"])
        self.assertIn("main session only", text_of(out["results"][3]))
        self.assertEqual(child.parent.name, "agents")


class TestChildren(BookCase):
    def test_main_links_a_child_when_the_subagent_result_returns_its_id_and_read_shows_its_checks(self):
        env = {"PI_SUBAGENT_ID": "kid", "PI_SUBAGENT_NAME": "worker-1", "PI_SUBAGENT_SESSION": str(self.session_file)}
        self.replay([*self.open_loop("inline", "child work"), stage(stage="anchor", check="pytest"), bash_result("pytest", 0, "5 passed"), stage(stage="verify")], env=env)
        link = tool_result("subagent", {}, "started", details={"id": "kid", "name": "worker-1", "agent": "worker", "status": "started"})
        out = self.replay([*self.open_loop(), link, stage(stage="read")])
        self.assertIn("child worker-1: inline; stages kind, anchor, check; check exit 0: 5 passed", text_of(out["results"][3]))
        main = [path for path in self.book_files() if path.parent.name != "agents"][0]
        self.assertIn("link", self.stages(main))


class TestDurableArtifacts(BookCase):
    def write(self, name: str, text: str) -> dict:
        path = self.cwd / "docs" / "specs" / "2026-10-29-x" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return tool_result("write", {"path": f"docs/specs/2026-10-29-x/{name}"})

    def entries(self, stage_name: str) -> list[dict]:
        return [entry for entry in self.book()[1] if entry["stage"] == stage_name and entry.get("auto")]

    def test_decision_edits_record_row_counts_and_the_questions_whose_status_changed(self):
        table = "| Question | Answer | Basis | Status |\n|---|---|---|---|\n| Which db? | pg | req | grounded |\n| Cache? | | | open |\n"
        self.replay([*self.open_loop("durable"), self.write("decision.md", table)])
        self.replay([self.write("decision.md", table.replace("| | | open |", "| yes | user | confirmed |"))])
        self.replay([self.write("decision.md", table.replace("| | | open |", "| yes | user | confirmed |") + "| Auth? | | | open |\n")])
        first, second, third = self.entries("decision")
        self.assertEqual(first["counts"], {"grounded": 1, "confirmed": 0, "open": 1})
        self.assertEqual(first["changed"], ["Which db?", "Cache?"])
        self.assertEqual(second["counts"], {"grounded": 1, "confirmed": 1, "open": 0})
        self.assertEqual(second["changed"], ["Cache?"])
        self.assertEqual((third["counts"]["open"], third["changed"]), (1, ["Auth?"]))

    def test_spec_edits_record_the_status_and_the_headings_whose_text_changed(self):
        text = "Status: proposed\n\n# Spec\n\n## Behavior\n\nA.\n\n## Edge cases\n\nB.\n"
        self.replay([*self.open_loop("durable"), self.write("spec.md", text)])
        self.replay([self.write("spec.md", text.replace("proposed", "approved").replace("A.", "A2."))])
        first, second = self.entries("spec")
        self.assertEqual(first["status"], "proposed")
        self.assertEqual(sorted(first["changed"]), ["Behavior", "Edge cases", "Spec"])
        self.assertEqual(second["status"], "approved")
        self.assertIn("Behavior", second["changed"])
        self.assertNotIn("Edge cases", second["changed"])

    def test_design_and_verification_record_changed_headings_and_result_counts(self):
        design = "## Approach\n\nX.\n\n## Risks\n\nY.\n"
        table = "# Verification\n\n| Requirement | Evidence | Result |\n|---|---|---|\n| a | ran | pass |\n| b | ran | fail |\n| c | - | unknown |\n"
        self.replay([*self.open_loop("durable"), self.write("design.md", design), self.write("verification.md", table)])
        self.replay([self.write("design.md", design.replace("Y.", "Z."))])
        _, d2 = self.entries("design")
        self.assertEqual(d2["changed"], ["Risks"])
        self.assertEqual(self.entries("verification")[0]["counts"], {"pass": 1, "fail": 1, "unknown": 1})

    def test_edits_to_other_files_or_outside_a_loop_record_nothing(self):
        self.replay([tool_result("write", {"path": "docs/specs/2026-10-29-x/notes.md"}), self.write("spec.md", "Status: proposed\n")])
        self.assertEqual(self.book_files(), [])
        self.replay([*self.open_loop(), tool_result("write", {"path": "src/app.py"})])
        self.assertEqual(self.stages(), ["kind"])


class TestTodoLinks(BookCase):
    SPEC = "Status: proposed\n\n# Spec\n\n## Behavior\n\nA.\nB.\n\n## Edge\n\nC.\n"
    REF = "docs/specs/2026-10-29-x/spec.md"

    def spec(self, text: str) -> None:
        path = self.cwd / self.REF
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def tasks(self) -> list[dict]:
        return [entry for entry in self.book()[1] if entry["stage"] == "task"]

    def test_create_and_update_record_task_entries_with_anchor_resolved_refs_and_followup(self):
        self.spec(self.SPEC)
        refs = [f"{self.REF}#Behavior", f"{self.REF}#Gone"]
        self.replay([todo_create("build it", anchor="pytest -q tests/x", ref=refs, followup="MP-9"),
                     todo_update(1, "build it", "in_progress", anchor="pytest -q tests/x", ref=refs[:1])])
        first, second = self.tasks()
        self.assertEqual((first["id"], first["subject"], first["status"], first["anchor"], first["followup"]),
                         (1, "build it", "pending", "pytest -q tests/x", "MP-9"))
        self.assertEqual(first["refs"], [{"ref": refs[0], "range": "L5-L8"}, {"ref": refs[1], "range": "missing"}])
        self.assertEqual((second["status"], len(second["refs"])), ("in_progress", 1))

    def test_a_task_without_anchor_or_ref_is_recorded_as_is_without_a_warning(self):
        out = self.replay([todo_create("plain"), stage(stage="kind", kind="durable", intent="x")])
        (entry,) = self.tasks()
        self.assertEqual(set(entry), {"ts", "stage", "id", "subject", "status"})
        self.assertNotIn("warn", text_of(out["results"][0]).lower())
        self.assertEqual(out["notices"], [])

    def test_a_todo_update_outside_a_loop_opens_nothing(self):
        self.replay([todo_update(1, "x", "completed")])
        self.assertEqual(self.book_files(), [])

    def test_read_lists_tasks_with_anchor_exit_code_and_refs_re_resolved_at_read(self):
        self.spec(self.SPEC)
        ref = f"{self.REF}#Behavior"
        todos = todo_state({"subject": "build it", "status": "in_progress", "metadata": {"anchor": "pytest -q", "ref": ref}},
                           {"subject": "plain", "status": "pending"})
        self.replay([todo_create("build it", anchor="pytest -q", ref=ref), todo_create("plain", task_id=2),
                     stage(stage="kind", kind="inline", intent="x"), bash_result("cd t && pytest -q", 1, "1 failed")])
        out = self.replay([{"branchAdd": [todos]}, stage(stage="read")])
        lines = text_of(out["results"][1]).splitlines()
        self.assertIn(f"#1 in_progress build it — pytest -q (exit 1) — {ref} → L5-L8", lines)
        self.assertIn("#2 pending plain — loop anchor", lines)
        self.spec(self.SPEC.replace("## Behavior\n", "## Renamed\n"))
        out = self.replay([{"branchAdd": [todos]}, stage(stage="read")])
        self.assertIn(f"{ref} → missing", text_of(out["results"][1]))

    def test_a_bash_call_that_does_not_match_a_task_anchor_records_nothing(self):
        self.replay([todo_create("t", anchor="pytest -q"), bash_result("ls", 0, "x")])
        self.assertEqual([e["stage"] for e in self.book()[1]], ["task"])

    def test_bare_heading_refs_resolve_against_the_recorded_spec_folder(self):
        self.spec(self.SPEC)
        write = tool_result("write", {"path": self.REF})
        self.replay([todo_create("t"), stage(stage="kind", kind="durable", intent="x"), write,
                     todo_create("u", task_id=2, ref="spec.md#Edge")])
        self.assertEqual(self.tasks()[-1]["refs"], [{"ref": "spec.md#Edge", "range": "L10-L12"}])


class TestSweep(BookCase):
    def write_book(self, path: Path, session: str | None, *entries: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# anchorloop loop book", f'id: "{path.stem}"', f"session: {json.dumps(session)}", "entries:", *[f"- {json.dumps(e)}" for e in entries]]
        path.write_text("\n".join(lines) + "\n")

    def test_session_start_deletes_dead_books_and_unlinked_children_and_lists_the_rest(self):
        proj = self.books / "proj"
        self.write_book(proj / "dead.yml", "/nonexistent/s.jsonl", {"stage": "kind", "kind": "inline", "intent": "old"})
        self.write_book(proj / "live.yml", str(self.session_file), {"stage": "kind", "kind": "reviewed", "intent": "mine"}, {"stage": "link", "child": "linked"})
        self.write_book(proj / "agents" / "linked.yml", None)
        self.write_book(proj / "agents" / "orphan.yml", None)
        self.write_book(proj / "agents" / "kid-of-dead.yml", None)
        dead = proj / "dead.yml"
        dead.write_text(dead.read_text() + json.dumps({"stage": "link", "child": "kid-of-dead"}).join(["- ", "\n"]))
        out = self.replay([{"event": "session_start", "payload": {}}])
        self.assertEqual(sorted(p.name for p in self.books.rglob("*.yml")), ["linked.yml", "live.yml"])
        (notice,) = out["notices"]
        self.assertIn("deleted stale loop book", notice["message"])
        self.assertIn("dead.yml", notice["message"])
        self.assertIn("orphan.yml", notice["message"])
        self.assertIn("open loop book: ", notice["message"])
        self.assertIn("live.yml (reviewed: mine)", notice["message"])

    def test_a_quiet_start_with_no_books_says_nothing(self):
        self.assertEqual(self.replay([{"event": "session_start", "payload": {}}])["notices"], [])


class TestParallelAppends(BookCase):
    def test_parallel_writers_keep_the_book_valid_yaml_with_every_entry(self):
        self.replay(self.open_loop())
        steps = [stage(stage="check", note="x" * 3000)] * 15
        procs = [subprocess.Popen(self.command(steps), stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env()) for _ in range(6)]
        for proc in procs:
            _, err = proc.communicate()
            self.assertEqual(proc.returncode, 0, err)
        header, entries = self.book()
        self.assertEqual(header["owner"], "main")
        self.assertEqual(len(entries), 2 + 6 * 15)
        self.assertTrue(all(entry["stage"] in ("task", "kind", "check") for entry in entries))


if __name__ == "__main__":
    unittest.main()

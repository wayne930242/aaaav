"""Regressions fixed in 2.2.3: kept child books, merge and anchor recognition, sweep, and appends to a deleted book."""

import shutil
import subprocess
import unittest

from tests.pi_harness import PI_DIR, bash_result, stage, todo_create, tool_result
from tests.test_pi_book import BookCase, text_of


class TestKeptChildBook(BookCase):
    ENV = {"PI_SUBAGENT_ID": "kid", "PI_SUBAGENT_NAME": "worker-1"}
    link = tool_result("subagent", {}, "started", details={"id": "kid", "name": "worker-1", "agent": "worker", "status": "started"})

    def child_env(self) -> dict:
        return {**self.ENV, "PI_SUBAGENT_SESSION": str(self.session_file)}

    def first_loop(self) -> None:
        steps = [*self.open_loop("inline", "first", anchor="pytest"), bash_result("pytest", 0, "ok"), stage(stage="friction", tried="a", found="b"), stage(stage="close", verdict="landed")]
        self.replay(steps, env=self.child_env())

    def test_a_childs_new_loop_keeps_its_closed_book_beside_it_for_main(self):
        self.first_loop()
        self.replay([todo_create("again"), stage(stage="kind", kind="inline", intent="second")], env=self.child_env())
        names = sorted(path.name for path in self.books.rglob("kid*.yml"))
        self.assertEqual(names, ["kid.closed-1.yml", "kid.yml"])
        out = self.replay([*self.open_loop(), self.link, stage(stage="read")])
        text = text_of(out["results"][-1])
        self.assertIn("child worker-1~1: inline (closed)", text)
        self.assertIn("child worker-1: inline;", text)
        self.assertIn("friction worker-1~1#1: a → b", text)

    def test_main_close_and_sweep_remove_the_kept_book_with_the_child(self):
        self.first_loop()
        self.replay([todo_create("again")], env=self.child_env())
        self.replay([*self.open_loop(), self.link, stage(stage="close", verdict="landed")])
        self.assertEqual(list(self.books.rglob("*.yml")), [])

    def test_sweep_keeps_a_kept_book_while_its_parent_links_the_child(self):
        self.first_loop()
        self.replay([todo_create("again")], env=self.child_env())
        self.replay([*self.open_loop(), self.link])
        self.replay([{"event": "session_start", "payload": {}}])
        self.assertEqual(sorted(path.name for path in self.books.rglob("kid*.yml")), ["kid.closed-1.yml", "kid.yml"])


class RunCase(BookCase):
    def fresh(self) -> None:
        shutil.rmtree(self.books, ignore_errors=True)

    def exits(self, command: str, code: int = 0, anchor: str = "pytest -q") -> list:
        self.fresh()
        self.replay([*self.open_loop(anchor=anchor), bash_result(command, code, "out")])
        return [e["exit"] for e in self.entries("verify")]

    def edits(self, command: str, output: str = "ok", code: int = 0) -> int:
        self.fresh()
        self.replay([*self.open_loop(anchor="pytest"), bash_result(command, code, output)])
        return len(self.entries("edit"))


class TestMergeAsAct(RunCase):
    def test_git_global_options_before_the_verb_still_count(self):
        for command in ("git -c core.editor=true merge feature", "git --no-pager pull", 'git -C "a b" pull', "git -C /tmp/x -c k=v cherry-pick abc", "cd x && git --git-dir=.git merge f"):
            with self.subTest(command=command):
                self.assertEqual(self.edits(command), 1)

    def test_verbs_that_do_no_work_do_not_count(self):
        for command in ("git pull --dry-run", "git cherry-pick --skip", "git merge --abort", "git cherry-pick --quit", "git -C x merge --abort", 'echo "git pull"', "git config pull.rebase false"):
            with self.subTest(command=command):
                self.assertEqual(self.edits(command), 0)

    def test_an_abort_flag_of_a_later_command_does_not_hide_the_merge(self):
        for command in ("git merge feature && git rebase --abort", "git merge feature; git cherry-pick --quit", "git merge feature\ngit rebase --abort", "git merge feature | tee log"):
            with self.subTest(command=command):
                self.assertEqual(self.edits(command), 1)

    def test_already_up_to_date_with_hyphens_is_no_change(self):
        self.assertEqual(self.edits("git pull", "Already up-to-date."), 0)
        self.assertEqual(self.edits("git pull", "Already up to date."), 0)

    def test_a_cherry_pick_continue_bases_on_the_head_before_the_pick(self):
        repo = self.cwd.parent / "conflict"
        repo.mkdir()
        run = lambda *args: subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env={**self.env(), "GIT_EDITOR": "true"}).stdout.strip()
        run("init", "-q")
        run("config", "user.email", "t@example.com")
        run("config", "user.name", "t")
        (repo / "a.txt").write_text("base\n")
        run("add", "a.txt")
        run("commit", "-qm", "base")
        run("checkout", "-qb", "side")
        (repo / "a.txt").write_text("side\n")
        run("commit", "-qam", "side")
        pick = run("rev-parse", "HEAD")
        run("checkout", "-q", "-")
        (repo / "a.txt").write_text("main\n")
        run("commit", "-qam", "main")
        before = run("rev-parse", "HEAD")
        run("cherry-pick", pick)
        (repo / "a.txt").write_text("both\n")
        run("add", "a.txt")
        run("cherry-pick", "--continue")
        self.assertNotEqual(run("rev-parse", "HEAD"), before)
        self.replay([*self.open_loop(anchor="pytest"), bash_result(f"git -C {repo} cherry-pick --continue", 0, "1 file changed")])
        self.assertEqual([e["head"] for e in self.entries("base") if e["repo"] == str(repo.resolve())], [before])


class TestAnchorNesting(RunCase):
    def test_runs_inside_a_substitution_are_not_runs(self):
        for command in ("echo $(true; pytest -q)", "echo $(cd x && pytest -q)", "diff <(true; pytest -q) exp", "echo $(pytest -q)", "cat >(pytest -q)", "echo $(echo $(pytest -q))"):
            with self.subTest(command=command):
                self.assertEqual(self.exits(command), [])

    def test_a_group_after_or_or_bang_voids_the_exit_however_far_the_run_is_inside(self):
        for command in ("[ -d x ] || (setup; pytest -q)", "true || (a; b; pytest -q)", "! (a; pytest -q)", "true || { a; pytest -q; }"):
            with self.subTest(command=command):
                self.assertEqual(self.exits(command), ["unknown"])

    def test_an_assignment_of_the_run_has_the_exit_of_the_run(self):
        self.assertEqual(self.exits("x=$(pytest -q)", 1), [1])
        self.assertEqual(self.exits("cd app && out=$(uv run pytest -q)", 1), [1])
        self.assertEqual(self.exits("x=$(pytest -q) || true"), ["unknown"])
        self.assertEqual(self.exits("true || x=$(pytest -q)"), ["unknown"])
        self.assertEqual(self.exits("x=$(pytest -q 2>&1 | tail -3)"), ["unknown"])
        self.assertEqual(self.exits("export x=$(pytest -q)"), [])
        self.assertEqual(self.exits("x=$(echo a; pytest -q)"), [])

    def test_a_pipefail_in_a_finished_nested_group_does_not_count(self):
        self.assertEqual(self.exits("( (a); set -o pipefail ); pytest -q | tail", 1), ["unknown"])
        self.assertEqual(self.exits("set -o pipefail; ((a)); pytest -q | tail", 1), [1])


class TestAnchorRecognition(RunCase):
    def test_runs_of_spaces_and_tabs_match(self):
        self.assertEqual(self.exits("pytest  -q", 1), [1])
        self.assertEqual(self.exits("cd x &&\tpytest   -q", 1), [1])
        self.assertEqual(self.exits("pytest -q", 1, anchor="pytest   -q"), [1])

    def test_package_runner_wrappers_count(self):
        for command in ("npx vitest run", "npx --yes vitest run", "pnpm exec vitest run", "bunx vitest run"):
            with self.subTest(command=command):
                self.assertEqual(self.exits(command, 1, anchor="vitest run"), [1])

    def test_grouped_and_conditional_runs_are_recorded_with_an_unknown_exit(self):
        for command in ("{ pytest -q; }", "if pytest -q; then echo ok; fi", "while pytest -q; do :; done", "if ! pytest -q; then echo bad; fi"):
            with self.subTest(command=command):
                self.assertEqual(self.exits(command), ["unknown"])

    def test_and_without_spaces_matches(self):
        self.assertEqual(self.exits("cd x&&pytest -q&&echo done", 1), [1])

    def test_an_anchor_with_quoted_arguments_matches_only_the_same_text(self):
        anchor = 'pytest -k "not slow"'
        self.assertEqual(self.exits('pytest -k "not slow"', 1, anchor=anchor), [1])
        self.assertEqual(self.exits('pytest -k "other"', 1, anchor=anchor), [])
        self.assertEqual(self.exits("echo 'pytest -k \"not slow\"'", 1, anchor=anchor), [])


class TestAppendToDeletedBook(BookCase):
    def test_appending_to_a_book_that_is_gone_creates_no_headerless_file(self):
        support = (PI_DIR / "support" / "book.ts").as_uri()
        script = f"""
import {{ appendEntry }} from {support!r};
import {{ mkdirSync, existsSync }} from "node:fs";
const dir = process.argv[1];
mkdirSync(dir, {{ recursive: true }});
appendEntry(dir + "/gone.yml", "edit", {{ path: "x" }});
console.log(JSON.stringify({{ exists: existsSync(dir + "/gone.yml") }}));
"""
        proc = subprocess.run(["node", "--input-type=module", "-e", script, str(self.books / "proj")], capture_output=True, text=True, env=self.env())
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), '{"exists":false}')


if __name__ == "__main__":
    unittest.main()

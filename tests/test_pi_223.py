"""Regressions fixed in 2.2.3: kept child books, merge and anchor recognition, sweep, and appends to a deleted book."""

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

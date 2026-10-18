"""Runs skills/aaaav-do/scripts/decision_log.py as the agent does and checks the trail it writes."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "skills" / "aaaav-do" / "scripts" / "decision_log.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-I", str(SCRIPT), *args], capture_output=True, text=True)


class TestDecisionLog(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log = Path(self.temp_dir.name) / "scratch" / "decisions-task.tsv"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def lines(self) -> list[str]:
        return self.log.read_text().splitlines()

    def test_first_append_writes_header_and_one_row(self) -> None:
        result = run("append", str(self.log), "kept v1 API", "callers still use it", "src/api.py:12", "tests green")
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = self.lines()
        self.assertEqual(lines[0], "ts\tdecision\twhy\tevidence\tresult")
        self.assertEqual(lines[1].split("\t")[1:], ["kept v1 API", "callers still use it", "src/api.py:12", "tests green"])

    def test_cells_stay_on_one_line_and_never_start_a_formula(self) -> None:
        run("append", str(self.log), "a\tb\nc", "=HYPERLINK(1)", "-rf", "@x")
        run("append", str(self.log), '"quoted', "+1", "plain", "done")
        rows = [row.split("\t")[1:] for row in self.lines()[1:]]
        self.assertEqual(rows, [["a b c", "'=HYPERLINK(1)", "'-rf", "'@x"], ["'\"quoted", "'+1", "plain", "done"]])

    def test_start_row_names_the_run_and_the_rows_it_did_not_write(self) -> None:
        run("append", str(self.log), "first", "why", "abc123", "open")
        run("start", str(self.log), "worker-2")
        cells = self.lines()[-1].split("\t")
        self.assertEqual(cells[1], "start")
        self.assertIn("1 earlier rows", cells[2])
        self.assertEqual(cells[3:], ["worker-2", "open"])

    def test_tail_prints_the_last_rows_without_header(self) -> None:
        for n in range(3):
            run("append", str(self.log), f"d{n}", "w", "e", "r")
        result = run("tail", str(self.log), "2")
        self.assertEqual([line.split("\t")[1] for line in result.stdout.splitlines()], ["d1", "d2"])

    def test_wrong_cell_count_fails_without_writing(self) -> None:
        result = run("append", str(self.log), "only", "three", "cells")
        self.assertEqual(result.returncode, 2)
        self.assertIn("expected 4 cells", result.stderr)
        self.assertFalse(self.log.exists())


if __name__ == "__main__":
    unittest.main()

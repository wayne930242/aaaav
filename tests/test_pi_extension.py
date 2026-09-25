"""Loads pi/validate-tool-use.ts with a stub pi API and checks the tool_result handler."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXTENSION = REPO_ROOT / "pi" / "validate-tool-use.ts"

HARNESS = """
const [extensionUrl, toolName, filePath, cwd] = process.argv.slice(1);
const { default: register } = await import(extensionUrl);
let handler;
register({ on: (event, fn) => { if (event === "tool_result") handler = fn; } });
const original = [{ type: "text", text: "ok" }];
const result = await handler(
  { toolName, input: { path: filePath }, content: original, isError: false },
  { cwd },
);
console.log(JSON.stringify(result ?? null));
"""


@unittest.skipUnless(shutil.which("node"), "node is required to load the pi extension")
class TestPiExtension(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_handler(self, tool_name: str, file_path: Path):
        proc = subprocess.run(
            ["node", "--input-type=module", "-e", HARNESS,
             EXTENSION.as_uri(), tool_name, str(file_path), str(self.base_path)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout.strip().splitlines()[-1])

    def test_write_appends_advice(self):
        test_file = self.base_path / "AGENTS.md"
        test_file.write_text("# Bad Rules\n- You must never under any circumstances do X.\n", encoding="utf-8")
        result = self.run_handler("write", test_file)
        self.assertEqual(result["content"][0], {"type": "text", "text": "ok"})
        self.assertEqual(len(result["content"]), 2)
        self.assertIn("[aaaav] Validation suggestions", result["content"][1]["text"])
        self.assertIn("defensive wording", result["content"][1]["text"])

    def test_clean_file_leaves_result_unchanged(self):
        test_file = self.base_path / "AGENTS.md"
        test_file.write_text("# Clean Rules\n- Direct statement.\n", encoding="utf-8")
        self.assertIsNone(self.run_handler("edit", test_file))

    def test_other_tools_are_ignored(self):
        test_file = self.base_path / "AGENTS.md"
        test_file.write_text("# Bad Rules\n- You must never under any circumstances do X.\n", encoding="utf-8")
        self.assertIsNone(self.run_handler("read", test_file))


if __name__ == "__main__":
    unittest.main()

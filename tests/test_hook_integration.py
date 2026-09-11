"""Integration tests for validate_tool_use.py hook entrypoint."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_SCRIPT = REPO_ROOT / "hooks" / "validate_tool_use.py"


class TestHookIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_claude_payload_clean_file(self):
        test_file = self.base_path / "AGENTS.md"
        test_file.write_text("# Clean Rules\n- Direct statement.\n", encoding="utf-8")

        payload = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(test_file),
            },
            "cwd": str(self.base_path),
        }

        proc = subprocess.run(
            ["python3", str(HOOK_SCRIPT)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        output = json.loads(proc.stdout)
        self.assertEqual(output, {})

    def test_claude_payload_warning(self):
        test_file = self.base_path / "AGENTS.md"
        test_file.write_text("# Bad Rules\n- You must never under any circumstances do X.\n", encoding="utf-8")

        payload = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(test_file),
            },
            "cwd": str(self.base_path),
        }

        proc = subprocess.run(
            ["python3", str(HOOK_SCRIPT)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        output = json.loads(proc.stdout)
        self.assertIn("hookSpecificOutput", output)
        self.assertIn("defensive wording", output["systemMessage"])

    def test_antigravity_payload_clean_file(self):
        test_file = self.base_path / "AGENTS.md"
        test_file.write_text("# Clean Rules\n- Direct statement.\n", encoding="utf-8")

        payload = {
            "conversationId": "test-id",
            "workspacePaths": [str(self.base_path)],
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": str(test_file),
                },
            },
        }

        proc = subprocess.run(
            ["python3", str(HOOK_SCRIPT)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        output = json.loads(proc.stdout)
        self.assertEqual(output, {})

    def test_empty_input_graceful_exit(self):
        proc = subprocess.run(
            ["python3", str(HOOK_SCRIPT)],
            input="",
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()

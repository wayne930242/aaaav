"""Unit tests for rule and instruction file validator."""

import tempfile
import unittest
from pathlib import Path
from hooks.validators.rule_validator import check_rules_file


class TestRuleValidator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_valid_rule_file(self):
        rule_file = self.base_path / "AGENTS.md"
        rule_file.write_text(
            """# Agent Guidelines

- Write clean, maintainable code.
- Ensure all tests pass before completing tasks.
- Keep responses concise and focused.
""",
            encoding="utf-8",
        )
        warnings = check_rules_file(rule_file)
        self.assertEqual(warnings, [])

    def test_defensive_phrasing_flagged(self):
        rule_file = self.base_path / "AGENTS.md"
        rule_file.write_text(
            """# Agent Guidelines

- STRICT RED LINE: Do not touch production code without verification.
- Under no circumstances make assumptions.
""",
            encoding="utf-8",
        )
        warnings = check_rules_file(rule_file)
        self.assertTrue(any("detected defensive wording" in w for w in warnings))

    def test_simplified_chinese_flagged(self):
        rule_file = self.base_path / "AGENTS.md"
        rule_file.write_text(
            """# 規則說明
这个文件使用简体字。
""",
            encoding="utf-8",
        )
        warnings = check_rules_file(rule_file)
        self.assertTrue(any("Simplified Chinese detected" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()

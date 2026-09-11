"""Unit tests for SKILL.md validator."""

import tempfile
import unittest
from pathlib import Path
from hooks.validators.skill_validator import check_skill_md


class TestSkillValidator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_valid_streamlined_skill(self):
        skill_dir = self.base_path / "my-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(
            """---
name: my-skill
description: Use when executing streamlined tasks.
---

# My Skill

Direct instructions for execution.
""",
            encoding="utf-8",
        )
        warnings = check_skill_md(skill_file)
        self.assertEqual(warnings, [])

    def test_missing_frontmatter(self):
        skill_dir = self.base_path / "my-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("# My Skill without frontmatter", encoding="utf-8")

        warnings = check_skill_md(skill_file)
        self.assertTrue(any("missing or invalid YAML frontmatter" in w for w in warnings))

    def test_extra_frontmatter_fields(self):
        skill_dir = self.base_path / "my-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(
            """---
name: my-skill
description: Use when executing streamlined tasks.
author: John Doe
version: 1.0.0
---
# Content
""",
            encoding="utf-8",
        )
        warnings = check_skill_md(skill_file)
        self.assertTrue(any("extra frontmatter fields" in w for w in warnings))

    def test_broken_markdown_links(self):
        skill_dir = self.base_path / "my-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(
            """---
name: my-skill
description: Use when executing streamlined tasks.
---
See [Missing Ref](references/missing.md).
""",
            encoding="utf-8",
        )
        warnings = check_skill_md(skill_file)
        self.assertTrue(any("broken local link: references/missing.md" in w for w in warnings))

    def test_orphaned_files(self):
        skill_dir = self.base_path / "my-skill"
        skill_dir.mkdir()
        ref_dir = skill_dir / "references"
        ref_dir.mkdir()
        orphan = ref_dir / "orphan.md"
        orphan.write_text("# Orphan content", encoding="utf-8")

        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(
            """---
name: my-skill
description: Use when executing streamlined tasks.
---
# Skill without linking orphan
""",
            encoding="utf-8",
        )
        warnings = check_skill_md(skill_file)
        self.assertTrue(any("orphaned file not referenced" in w for w in warnings))

    def test_defensive_anti_pattern_detection(self):
        skill_dir = self.base_path / "my-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(
            """---
name: my-skill
description: Use when executing streamlined tasks.
---
You must never under any circumstances modify code without permission.
""",
            encoding="utf-8",
        )
        warnings = check_skill_md(skill_file)
        self.assertTrue(any("detected defensive anti-pattern" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()

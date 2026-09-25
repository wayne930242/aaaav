"""Unit tests for the pi package manifest and version synchronization."""

import json
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestPiManifest(unittest.TestCase):
    def test_pi_manifest(self):
        data = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "aaaav")
        self.assertIn("pi-package", data["keywords"])
        for path in data["pi"]["extensions"] + data["pi"]["skills"]:
            self.assertTrue((REPO_ROOT / path).exists(), f"pi resource {path} must exist")
        extensions = {(REPO_ROOT / path).resolve() for path in data["pi"]["extensions"]}
        for extension in sorted((REPO_ROOT / "pi").glob("*.ts")):
            self.assertIn(extension.resolve(), extensions, f"{extension.name} must be listed in package.json#pi.extensions")
        skill_roots = [(REPO_ROOT / path).resolve() for path in data["pi"]["skills"]]
        for skill in sorted((REPO_ROOT / "skills").glob("*/SKILL.md")):
            self.assertTrue(any(skill.resolve().is_relative_to(root) for root in skill_roots),
                            f"{skill.parent.name} must be covered by package.json#pi.skills")

    def test_version_synchronization(self):
        pi_data = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["version"], pi_data["version"])


if __name__ == "__main__":
    unittest.main()

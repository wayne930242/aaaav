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

    def test_version_synchronization(self):
        pi_data = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["version"], pi_data["version"])


if __name__ == "__main__":
    unittest.main()

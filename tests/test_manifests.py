"""Unit tests for plugin manifests and version synchronization."""

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestPluginManifests(unittest.TestCase):
    def test_antigravity_manifest(self):
        manifest_file = REPO_ROOT / "plugin.json"
        self.assertTrue(manifest_file.is_file(), "plugin.json must exist")
        data = json.loads(manifest_file.read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "weihung-loop-boot")
        self.assertIn("version", data)

    def test_claude_manifest(self):
        manifest_file = REPO_ROOT / ".claude-plugin" / "plugin.json"
        self.assertTrue(manifest_file.is_file(), ".claude-plugin/plugin.json must exist")
        data = json.loads(manifest_file.read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "weihung-loop-boot")
        self.assertIn("version", data)

        marketplace_file = REPO_ROOT / ".claude-plugin" / "marketplace.json"
        self.assertTrue(marketplace_file.is_file(), ".claude-plugin/marketplace.json must exist")
        market_data = json.loads(marketplace_file.read_text(encoding="utf-8"))
        self.assertEqual(market_data["name"], "weihung-loop-boot")

    def test_codex_manifest(self):
        manifest_file = REPO_ROOT / ".codex-plugin" / "plugin.json"
        self.assertTrue(manifest_file.is_file(), ".codex-plugin/plugin.json must exist")
        data = json.loads(manifest_file.read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "weihung-loop-boot")
        self.assertIn("version", data)

    def test_version_synchronization(self):
        agy_data = json.loads((REPO_ROOT / "plugin.json").read_text(encoding="utf-8"))
        claude_data = json.loads((REPO_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        market_data = json.loads((REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        codex_data = json.loads((REPO_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))

        version = agy_data["version"]
        self.assertEqual(claude_data["version"], version)
        self.assertEqual(market_data["metadata"]["version"], version)
        self.assertEqual(market_data["plugins"][0]["version"], version)
        self.assertEqual(codex_data["version"], version)

    def test_hooks_configuration(self):
        agy_hooks = REPO_ROOT / "hooks.json"
        self.assertTrue(agy_hooks.is_file())
        json.loads(agy_hooks.read_text(encoding="utf-8"))

        claude_hooks = REPO_ROOT / "hooks" / "hooks.json"
        self.assertTrue(claude_hooks.is_file())
        json.loads(claude_hooks.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

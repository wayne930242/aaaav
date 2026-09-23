"""Unit tests for Codex skill install/uninstall behavior against a fake HOME."""

import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALL_SCRIPT = REPO_ROOT / "scripts" / "install.sh"
UNINSTALL_SCRIPT = REPO_ROOT / "scripts" / "uninstall.sh"


def run_script(script: Path, target: str, fake_home: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(script), "--target", target],
        env={"HOME": str(fake_home), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=True,
    )


class TestCodexSkillDedupe(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fake_home = Path(self.tmp.name)
        self.codex_skills_dir = self.fake_home / ".codex" / "skills"
        self.codex_skills_dir.mkdir(parents=True)

        # Simulate a symlink an earlier installer run left behind.
        self.stale_link = self.codex_skills_dir / "aaaav-do"
        self.stale_link.symlink_to(REPO_ROOT / "skills" / "aaaav-do")

        # Simulate a symlink for a skill later renamed or removed from the repo.
        self.orphan_link = self.codex_skills_dir / "renamed-skill"
        self.orphan_link.symlink_to(REPO_ROOT / "skills" / "grilling")

        # Simulate unrelated entries that must be left untouched.
        self.unrelated_link = self.codex_skills_dir / "other-plugin-skill"
        other_target = self.fake_home / "elsewhere"
        other_target.mkdir()
        self.unrelated_link.symlink_to(other_target)

        self.unrelated_dir = self.codex_skills_dir / "codebase-memory"
        self.unrelated_dir.mkdir()

    def test_install_removes_only_repo_owned_links(self) -> None:
        run_script(INSTALL_SCRIPT, "codex", self.fake_home)

        self.assertFalse(self.stale_link.exists() or self.stale_link.is_symlink())
        self.assertFalse(self.orphan_link.exists() or self.orphan_link.is_symlink())
        self.assertTrue(self.unrelated_link.is_symlink())
        self.assertTrue(self.unrelated_dir.is_dir())

    def test_install_creates_no_new_codex_skill_links(self) -> None:
        run_script(INSTALL_SCRIPT, "codex", self.fake_home)

        remaining = {p.name for p in self.codex_skills_dir.iterdir()}
        self.assertEqual(remaining, {"other-plugin-skill", "codebase-memory"})

    def test_uninstall_removes_only_repo_owned_links(self) -> None:
        run_script(UNINSTALL_SCRIPT, "codex", self.fake_home)

        self.assertFalse(self.stale_link.exists() or self.stale_link.is_symlink())
        self.assertFalse(self.orphan_link.exists() or self.orphan_link.is_symlink())
        self.assertTrue(self.unrelated_link.is_symlink())
        self.assertTrue(self.unrelated_dir.is_dir())

    def test_dry_run_leaves_links_untouched(self) -> None:
        subprocess.run(
            ["bash", str(INSTALL_SCRIPT), "--target", "codex", "--dry-run"],
            env={"HOME": str(self.fake_home), "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertTrue(self.stale_link.is_symlink())
        self.assertTrue(self.orphan_link.is_symlink())


if __name__ == "__main__":
    unittest.main()

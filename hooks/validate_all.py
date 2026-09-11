#!/usr/bin/env python3
"""CLI utility to validate all skills, rules, and durable specs in a workspace."""

import argparse
import sys
from pathlib import Path

# Add script directory to path
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from validators.skill_validator import check_skill_md
from validators.rule_validator import check_rules_file
from validators.durable_validator import check_durable_spec


def scan_workspace(root: Path) -> dict[str, list[str]]:
    """Scan root for SKILL.md, rule files, and durable specs, collecting warnings."""
    results: dict[str, list[str]] = {}

    # 1. Scan SKILL.md files
    for skill_file in root.rglob("SKILL.md"):
        # Ignore virtual environments or hidden dirs
        if any(part.startswith(".") or part in ("venv", ".venv", "__pycache__") for part in skill_file.parts):
            continue
        warnings = check_skill_md(skill_file)
        if warnings:
            results[str(skill_file.relative_to(root))] = warnings

    # 2. Scan rule files
    for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md"):
        rule_file = root / name
        if rule_file.is_file():
            warnings = check_rules_file(rule_file)
            if warnings:
                results[str(rule_file.relative_to(root))] = warnings

    rules_dir = root / "rules"
    if rules_dir.is_dir():
        for rule_file in rules_dir.rglob("*.md"):
            warnings = check_rules_file(rule_file)
            if warnings:
                results[str(rule_file.relative_to(root))] = warnings
        for rule_file in rules_dir.rglob("*.rules"):
            warnings = check_rules_file(rule_file)
            if warnings:
                results[str(rule_file.relative_to(root))] = warnings

    # 3. Scan durable specs
    specs_dir = root / "docs" / "specs"
    if specs_dir.is_dir():
        for spec_file in specs_dir.rglob("*.md"):
            warnings = check_durable_spec(spec_file)
            if warnings:
                results[str(spec_file.relative_to(root))] = warnings

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate skills, rules, and durable specs.")
    parser.add_argument("path", nargs="?", default=".", help="Root directory to scan (defaults to current directory)")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    print(f"Scanning workspace: {root}")
    results = scan_workspace(root)

    if not results:
        print("✓ All skills, rules, and durable specs passed validation cleanly.")
        sys.exit(0)

    print(f"\nFound issues in {len(results)} file(s):")
    for file_path, warnings in results.items():
        print(f"\n  [{file_path}]")
        for w in warnings:
            print(f"    - {w}")

    sys.exit(1)


if __name__ == "__main__":
    main()

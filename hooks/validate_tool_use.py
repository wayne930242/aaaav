#!/usr/bin/env python3
"""PostToolUse hook entrypoint for Antigravity, Claude Code, and Codex.

Validates edited files against skill compactness, direct expected behavior,
and durable review standards without interrupting execution.
"""

import json
import sys
from pathlib import Path

# Add script directory to path for relative imports
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from validators.utils import extract_file_path_from_payload
from validators.skill_validator import check_skill_md
from validators.rule_validator import check_rules_file
from validators.durable_validator import check_durable_spec


def run_validation(path: Path) -> list[str]:
    """Route file to appropriate validator based on path and filename."""
    warnings: list[str] = []
    name = path.name.lower()
    path_str = str(path).replace("\\", "/")

    # 1. SKILL.md
    if name == "skill.md":
        warnings.extend(check_skill_md(path))

    # 2. Rule and instruction files
    elif name in ("agents.md", "claude.md", "gemini.md") or "/rules/" in path_str:
        warnings.extend(check_rules_file(path))

    # 3. Durable spec artifacts
    elif "/docs/specs/" in path_str and name.endswith(".md"):
        warnings.extend(check_durable_spec(path))

    return warnings


def main() -> None:
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            sys.exit(0)
        data = json.loads(raw_input)
    except Exception:
        # Never block execution if input parsing fails
        sys.exit(0)

    try:
        file_path_str = extract_file_path_from_payload(data)
        if not file_path_str:
            # Check if payload was just Antigravity or Claude with no file
            is_claude = "tool_input" in data
            print(json.dumps({}) if not is_claude else json.dumps({}))
            sys.exit(0)

        # Resolve path
        cwd_str = data.get("cwd", "")
        if not cwd_str and "workspacePaths" in data and data["workspacePaths"]:
            cwd_str = data["workspacePaths"][0]

        cwd = Path(cwd_str) if cwd_str else Path.cwd()
        target_path = Path(file_path_str)
        if not target_path.is_absolute():
            target_path = cwd / target_path

        if not target_path.exists():
            print(json.dumps({}))
            sys.exit(0)

        warnings = run_validation(target_path)
        is_claude = "tool_input" in data

        if warnings:
            try:
                rel = target_path.relative_to(cwd)
            except ValueError:
                rel = target_path

            lines = "\n".join(f"  - {w}" for w in warnings)
            msg = f"⚠ [aaaav-loop-boot] Validation suggestions for {rel}:\n{lines}"

            if is_claude:
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": msg,
                    },
                    "systemMessage": msg,
                }
                print(json.dumps(output))
            else:
                # Antigravity expects {} on stdout
                sys.stderr.write(msg + "\n")
                print(json.dumps({}))
        else:
            print(json.dumps({}))

    except Exception as e:
        sys.stderr.write(f"aaaav-loop-boot hook error: {e}\n")
        print(json.dumps({}))

    sys.exit(0)


if __name__ == "__main__":
    main()

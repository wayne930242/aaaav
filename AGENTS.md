# Agent Working Agreements: aaaav-loop-boot

This repository defines a streamlined, multi-platform AAAAV plugin for Antigravity, Claude Code, and Codex.

## Core Directives

- All prompts, agent instructions, and code comments must be in English.
- User communication must always be in Traditional Chinese (繁體中文).
- Prompts, documentation, and guidelines must directly state expected behavior. Avoid unnecessary defensive phrasing, prohibitive lists, and endless red lines.
- Source-changing work follows AAAAV: Align → Advance → Anchor → Act → Verify.
- Establish the reality anchor and checkpoint before the first production edit.
- Commit messages must not mention AI tools.

## Development Workflow

- Run `python3 hooks/validate_all.py .` to ensure skills and rules conform to the compactness and quality baselines.
- Run `python3 -m unittest discover -s tests` before declaring verification complete.

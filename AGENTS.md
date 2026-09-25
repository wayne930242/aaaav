# Agent Working Agreements: aaaav

This repository is the AAAAV pi package: the workflow skills in `skills/` and the pi extension `pi/validate-tool-use.ts`, which runs `hooks/validate_tool_use.py` after `write` and `edit`.

## Core Directives

- All prompts, agent instructions, and code comments must be in English.
- User communication must always be in Traditional Chinese (繁體中文).
- Prompts, documentation, and guidelines state expected behavior directly, without defensive phrasing or prohibitive lists.
- Source-changing work follows AAAAV: Align → Advance → Anchor → Act → Verify (with Reflexive pass).
- Establish the reality anchor and checkpoint before the first production edit.
- Commit messages must not mention AI tools.

## Versioning & Release Directives

- Bump the version in `package.json` and `pyproject.toml` together whenever package capabilities, workflow contracts, or configurations change.

## Development Workflow

- Run `uv run python hooks/validate_all.py .` to ensure skills and rules conform to the compactness and quality baselines.
- Run `uv run --with pytest pytest -q` before declaring verification complete; `tests/test_pi_extension.py` loads the pi extension with Node.

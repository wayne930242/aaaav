# Claude Code Project Guidelines: aaaav-loop-boot

This project is a multi-platform plugin supporting Antigravity, Claude Code, and Codex.

## Essential Laws

- Communication: Always use Traditional Chinese (繁體中文).
- Prompts & Instructions: Always write instructions, docstrings, and skills in English.
- Tone: State expected behaviors directly; avoid defensive language or artificial guardrails.
- Workflow: Execute source-changing tasks via AAAAV (Align → Advance → Anchor → Act → Verify).
- Quality: Run unit tests and workspace validators before finishing.
- Commits: Commit messages must not mention AI tools.

## Quick Commands

- Run full test suite: `python3 -m unittest discover -s tests`
- Run workspace validation: `python3 hooks/validate_all.py .`
- Test tool-use hook: `python3 hooks/validate_tool_use.py`

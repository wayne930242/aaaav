# weihung-loop-boot

Streamlined AAAAV agent workflow plugin supporting Google Antigravity (`agy`), Claude Code (`claude`), and OpenAI Codex (`codex`).

## Philosophy

Modern foundation models are capable. They do not require endless logging of every transient friction or the accumulation of infinite defensive "red lines". Instead, this plugin emphasizes:

1. **Streamlining Skills**: Keep skills concise, actionable, and focused on direct expected behavior. Offload detailed procedures to `references/` via progressive disclosure.
2. **Standardizing Capabilities**: Unify reporting (`Requirement | Evidence | Result`), communication (transparent reasoning and proactive reporting), and documentation (link-first, single-pass readability).
3. **Durable-Oriented Review**: Prevent rules from proliferating endlessly. Focus on essential core rules and missing skills *before* work starts; during the Verify phase, review newly added rules and skills for *adjustment and tuning*, avoiding defensive restrictions.

## The AAAAV Loop

This plugin operationalizes the AAAAV workflow:

```text
Align ──► Advance ──► Anchor ──► Act ──► Verify
```

- **Align**: Restate the intent in the user's terms and classify the work as **Inline** or **Durable**.
  - *Inline*: Localized, clear requirements, minimal future reuse. Declares contract and authorization; leaves no spec artifacts.
  - *Durable*: Architectural decisions, public contracts, or cross-session continuity. Conducts pre-flight skill/rule checks and leaves specs under `docs/specs/`.
- **Advance**: `Decision → Spec → Design` for Durable work. Once a task is dispatched, this belongs to the worker and the user; a bounded loop you carry yourself runs inline.
- **Anchor**: Name the reality anchor and arrange its checkpoint before the first production edit.
- **Act**: Implement through the target project's native practices in minimal, surgical increments.
- **Verify**: Exercise the reality anchor and record observed evidence in the standardized verification table. Review newly introduced rules or skills for tuning.

## Protection Hooks

Inspired by `reflexive-claude-code`, this plugin provides non-blocking protection hooks via `hooks.json` and Python validators:

- **SKILL.md Validator**: Validates frontmatter, detects broken markdown links and orphaned reference files, checks compactness (< 120 lines), and flags defensive anti-patterns.
- **Rule Validator**: Validates `AGENTS.md`, `CLAUDE.md`, and `rules/*.md` against defensive phrasing and micro-rule proliferation.
- **Durable Spec Validator**: Checks pre-flight skill/rule readiness in `decision.md`, approval status in `spec.md`, and the `Requirement | Evidence | Result` format in `verification.md`.

## Project Structure

```text
weihung-loop-boot/
├── plugin.json                    # Antigravity plugin manifest
├── .claude-plugin/
│   ├── plugin.json                # Claude Code plugin manifest
│   └── marketplace.json           # Claude Code marketplace catalog
├── .codex-plugin/
│   └── plugin.json                # OpenAI Codex plugin manifest
├── hooks.json                     # Antigravity hook configuration
├── hooks/
│   ├── hooks.json                 # Claude Code hook configuration
│   ├── validate_tool_use.py       # PostToolUse hook entrypoint
│   ├── validate_all.py            # Workspace-wide validation CLI
│   └── validators/                # Modular validators
├── skills/
│   ├── leveraging-aaaav/          # Core AAAAV execution skill
│   │   ├── SKILL.md
│   │   └── references/            # Reporting, communication, docs, durable review
│   └── streamlining-skills/       # Skill creation & compaction skill
│       ├── SKILL.md
│       └── references/            # Defensive patterns, skill template
├── scripts/
│   ├── install.sh                 # Multi-platform installer (agy, claude, codex)
│   └── validate.sh                # Test & validation runner
└── tests/                         # Full automated test suite (pytest / unittest)
```

## Installation

Install across platforms using the unified installer:

```bash
# Install to all supported platforms (Antigravity, Claude Code, Codex)
bash scripts/install.sh --target all

# Or install to a specific platform
bash scripts/install.sh --target agy
bash scripts/install.sh --target claude
bash scripts/install.sh --target codex
```

## Validation & Testing

Run the automated test suite and workspace validation:

```bash
bash scripts/validate.sh
```

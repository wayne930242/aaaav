---
name: solid-loop
description: Use when creating, auditing, or refactoring skills to eliminate defensive bloat, standardize communication and reporting, and maintain high-density concise instructions.
---

# Streamlining Skills

Maintain compact, actionable skills. Modern models require clear operational contracts rather than defensive guardrails or endless prohibitions.

## Core Refactoring Workflow

Follow these steps when evaluating or authoring a skill:

1. **Verify Frontmatter**: Ensure `name` and `description` are present. The description must specify concrete trigger conditions using third-person phrasing (include "Use when...").
2. **Remove Defensive Phrasing**: Identify prohibitive red lines and negative restrictions. Replace them with positive statements of expected behavior. See [references/defensive-patterns.md](references/defensive-patterns.md).
3. **Apply Progressive Disclosure**: Keep `SKILL.md` under 120 lines. Offload detailed procedures, extensive schemas, checklists, and templates to `references/`.
4. **Standardize Contracts**:
   - Reference standard reporting formats for verification output.
   - Anchor communications in transparent reasoning and direct status.
5. **Verify Links and References**: Ensure every file in `references/` is linked from `SKILL.md`, and that no broken links or orphaned files exist.

Use the provided [Skill Template](references/template-skill.md) when bootstrapping a new skill.

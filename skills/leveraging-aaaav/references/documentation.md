# Documentation Standards

Standardize documentation practices to maintain thin, readable, and maintainable project knowledge.

## Core Documentation Rules

1. **Single-Pass Readability**: Structure documents so a human or agent can comprehend the intent and scope in one reading pass.
2. **Link Rather Than Copy**: Link directly to source files, line ranges, issues, or parent specifications. Do not duplicate code blocks or requirements across multiple files.
3. **Direct Tone**: Explain what components do, their contracts, and their interfaces. Avoid defensive prose, speculative disclaimers, or excessive historical background.
4. **Keep User-Root and Plugins Thin**: Document only behavior that is stable across multiple projects. Project-specific context belongs inside project repositories.

## Durable Spec Artifacts

When a task requires durable documentation, organize artifacts under `docs/specs/YYYY-MM-DD-<slug>/`:

- **`decision.md`**: Problem statement, boundaries, evaluated options, and the question/answer decision table. Confirms skill readiness before work starts.
- **`spec.md`**: Observable behavioral contract, edge cases, reality anchor, and approval status (`Status: proposed` until approved).
- **`design.md`**: Selected architectural approach, interfaces, seams, and concrete test setup.
- **`verification.md`**: The `Requirement | Evidence | Result` table, human checkpoints, and adjustment reviews of newly added rules or skills.

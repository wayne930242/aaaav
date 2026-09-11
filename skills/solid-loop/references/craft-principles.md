# Skill Craft Principles

Refining skills for high predictability, lean context load, and reliable execution.

## Information Hierarchy

Organize skill content into three distinct tiers:

1. **In-Skill Steps**: Primary tier in `SKILL.md`. Ordered operational sequences that guide the agent. Each step must culminate in a concrete completion criterion.
2. **In-Skill Reference**: Secondary tier in `SKILL.md`. Flat peer-sets of rules, contracts, and core definitions. Co-locate related rules under single headings.
3. **Disclosed Reference**: Tertiary tier in `references/`. Auxiliary templates, deep reference catalogs, and situational branches reached via explicit context pointers.

## Steering Levers

- **Leading Words**: Compact concepts living in model pretraining (e.g. *tight*, *tracer*, *reality anchor*). A single strong token activates rich prior behaviors without spending tokens on lengthy definitions.
- **Completion Criteria**: The observable condition indicating step completion.
  - **Checkability**: The agent must distinguish done from not-done with certainty. Clear bounds resist premature completion.
  - **Demand**: Sets required legwork. Explicitly bound coverage (e.g., "every changed module verified") to prevent shallow execution.
- **Positive Steering**: Describe expected behavior directly. Avoid negative prohibitions, which prime the forbidden behavior into working memory (the negation failure mode).

## Pruning Discipline

- **Sentence-by-Sentence No-Op Test**: Evaluate every sentence in isolation. If removing the sentence does not alter model behavior from baseline, delete the entire sentence.
- **Single Source of Truth**: Keep one authoritative home for each instruction. Prune duplication across files.
- **Sediment Removal**: Aggressively remove historical instructions that no longer apply to modern capable models.

---
name: solid-loop
description: Use when creating, auditing, or refactoring skills to eliminate defensive bloat, standardize communication and reporting, and maintain high-density concise instructions.
---

# Solid Loop

Author and maintain skills for maximum predictability, compactness, and high-density instruction.

The root virtue is **predictability** -- ensuring the agent follows the same dependable process on every run.

## Core Pillars

1. **Information Hierarchy**:
   - **In-Skill Steps**: Ordered actions in `SKILL.md` ending in explicit completion criteria.
   - **In-Skill Reference**: Co-located definitions and rules consulted on demand.
   - **Disclosed Reference**: Secondary procedures and checklists moved to `references/` behind explicit context pointers.
2. **Steering Levers**:
   - **Leading Words**: Anchor behaviors using pretrained concepts (e.g., *tight*, *red*, *tracer*, *reality anchor*) rather than verbose explanations.
   - **Completion Criteria**: Keep bounds checkable to prevent premature completion, and demanding to drive thorough legwork.
   - **Positive Steering**: Prompt the target behavior directly. State what to do rather than listing prohibited negatives (avoiding the negation elephant).
3. **Pruning Discipline**:
   - **Sentence-by-Sentence No-Op Test**: Test each sentence in isolation. Delete sentences that do not change behavior relative to the model's baseline.
   - **Single Source of Truth**: Retain one canonical location for each operational contract. Eliminate sediment and duplication.

## Refactoring and Authoring Procedure

Follow this sequence when authoring or auditing any skill:

1. **Verify Frontmatter and Triggers**:
   - Ensure `name` matches the directory and `description` front-loads concrete triggers ("Use when...").
   - Eliminate identity summaries already in the body.
2. **Eliminate Defensive Phrasing and Negation**:
   - Convert prohibitions and red lines into direct, positive operational requirements. See [references/defensive-patterns.md](references/defensive-patterns.md).
3. **Apply Progressive Disclosure and Pruning**:
   - Run the no-op test sentence by sentence.
   - Disclose schemas, templates, and reference catalogs into `references/`. Keep `SKILL.md` under 120 lines.
   - Review architectural levers in [references/craft-principles.md](references/craft-principles.md).
4. **Sharpen Completion Criteria**:
   - Give every step a verifiable completion criterion.
   - Ensure demand requires sufficient investigation before the agent advances.
5. **Verify Links and Integrity**:
   - Confirm all referenced files exist in `references/` without orphans or broken links.
   - Use [references/template-skill.md](references/template-skill.md) to bootstrap new skills.

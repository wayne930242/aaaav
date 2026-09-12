---
name: solid-loop
description: Use when auditing, tuning, or refactoring agent skills and instructions used during a task to reduce friction and detours.
---

# Solid Loop

Audit, tune, and maintain the agent system for predictability, efficiency, and minimal friction.

The root virtue is **predictability and efficiency** -- ensuring agent instructions save task time and tokens rather than causing detours or reading unnecessary files.

## Reflexive Scope and Retrospective Anchor

When invoked during the Reflexive pass of Verify, restrict reflection to the rules, `AGENTS.md` / `CLAUDE.md`, and skills actually used during the task.

Anchor the audit on one guiding question:

> *"What did I wish I knew earlier that would have reduced friction and detours in this run?"*

## Core Pillars

1. **Skill ROI Evaluation**:
   - **Time & Token Yield**: Confirm whether each invoked skill saved task time and tokens, or whether it caused detours and reading unnecessary files.
   - **Prune High-Overhead Skills**: If a skill forced excess context loading with negligible return, prune its references or sharpen its triggers.
2. **Information Hierarchy**:
   - **In-Skill Steps**: Ordered actions in `SKILL.md` ending in explicit completion criteria.
   - **In-Skill Reference**: Co-located definitions and rules consulted on demand.
   - **Disclosed Reference**: Secondary procedures moved to `references/` behind explicit context pointers. Keep `SKILL.md` under 120 lines.
3. **Steering Levers**:
   - **Leading Words**: Anchor behaviors using pretrained concepts (e.g., *tight*, *red*, *tracer*, *reality anchor*) rather than verbose explanations.
   - **Completion Criteria**: Keep bounds checkable to prevent premature completion.
   - **Positive Steering**: Direct statement of target behavior rather than listing prohibitions.
4. **Pruning Discipline**:
   - **Sentence-by-Sentence No-Op Test**: Delete sentences that do not change behavior relative to baseline.
   - **Single Source of Truth**: Retain one canonical home for each operational contract; eliminate sediment.

## Audit and Tuning Procedure

Follow this sequence when auditing used skills or instructions:

1. **Review Task Friction**: Trace where the run stalled, read irrelevant files, or took detours.
2. **Audit Touched Skills**: Evaluate whether the skill earned its context cost versus taking detours.
3. **Eliminate Defensive Phrasing**: Replace prohibitions with direct expected behaviors. See [references/defensive-patterns.md](references/defensive-patterns.md).
4. **Apply Progressive Disclosure and Pruning**: Run the no-op test, disclose secondary catalogs to `references/`, and consult [references/craft-principles.md](references/craft-principles.md).
5. **Solidify and Verify**: Ensure completion criteria are checkable and all links exist without orphans. Bootstrap missing skills via [references/template-skill.md](references/template-skill.md).

---
name: solid-loop
description: Use when auditing, tuning, or refactoring agent skills and instructions used during a task to reduce friction and detours.
---

# Solid Loop

Audit, tune, and maintain the agent system for predictability, efficiency, and minimal friction.

The root virtue is **predictability and efficiency** -- ensuring agent instructions save task time and tokens rather than causing detours or reading unnecessary files.

## The Friction Gate (Anti-Over-Reflection)

Act only on **obvious findings backed by trajectory evidence**:
- The agent read unneeded files due to misleading context pointers.
- Ambiguous skill triggers caused false invocations or multi-turn detours.
- Missing core project invariants forced repeated trial-and-error.

If friction was minor, transient, or speculative, exit immediately without making edits.

Anchor the audit on one guiding question:

> *"What did I wish I knew earlier that would have reduced friction and detours in this run?"*

## Action Priority: Pruning First

1. **Prune (Highest Priority)**: Remove references that caused unneeded file reading; eliminate sediment and no-op sentences.
2. **Tune**: Surgically update the single ambiguous trigger sentence or completion criterion in place.
3. **Scaffold (Rare)**: Bootstrap a minimal, lean skill via [references/template-skill.md](references/template-skill.md) only when a recurring operational procedure was absent and caused major detours.

## Core Pillars

1. **Information Hierarchy**:
   - **In-Skill Steps**: Ordered actions in `SKILL.md` ending in explicit completion criteria.
   - **In-Skill Reference**: Co-located definitions and rules consulted on demand.
   - **Disclosed Reference**: Secondary procedures moved to `references/` behind explicit context pointers. Keep `SKILL.md` under 120 lines.
2. **Steering Levers**:
   - **Leading Words**: Anchor behaviors using pretrained concepts (e.g., *tight*, *red*, *tracer*, *reality anchor*).
   - **Completion Criteria**: Keep bounds checkable to prevent premature completion.
   - **Positive Steering**: Direct statement of target behavior rather than listing prohibitions. See [references/defensive-patterns.md](references/defensive-patterns.md).
3. **Pruning Discipline**:
   - **Sentence-by-Sentence No-Op Test**: Delete sentences that do not change behavior relative to baseline. See [references/craft-principles.md](references/craft-principles.md).
   - **Single Source of Truth**: Retain one canonical home for each operational contract.

## Output Contract

Keep reflexive output concise (2-3 lines max):

```text
Friction: <the specific detour or wasted context observed>
Action: <pruned reference / tightened trigger / no-op>
```

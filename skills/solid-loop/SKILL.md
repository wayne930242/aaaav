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

## Information Hierarchy and Craft Levers

Organize skill content into three tiers:

1. **In-Skill Steps**: Primary tier in `SKILL.md`. Ordered operational sequences that guide the agent, ending in checkable completion criteria.
2. **In-Skill Reference**: Secondary tier in `SKILL.md`. Co-located definitions, rules, and core tables. Keep `SKILL.md` under 300 lines (official self-contained skill standard).
3. **Disclosed Reference**: Tertiary tier in `references/`. Auxiliary templates or deep reference catalogs reached via explicit context pointers.

### Steering Levers

- **Leading Words**: Anchor behaviors using compact pretrained concepts (e.g., *tight*, *red*, *tracer*, *reality anchor*) rather than verbose explanations.
- **Completion Criteria**: Keep bounds checkable to prevent premature completion, and demanding to drive thorough legwork.
- **Positive Steering**: Direct statement of target behavior rather than listing prohibitions (avoiding the negation elephant).
- **Sentence-by-Sentence No-Op Test**: Evaluate every sentence in isolation. Delete sentences that do not change behavior relative to the baseline.
- **Single Source of Truth**: Retain one canonical home for each operational contract; eliminate duplicate rules across files.

## Defensive Patterns vs. Expected Behavior

Replace defensive prohibitions, endless red lines, and negative framing with concise, positive statements of expected behavior.

### The Negation Anti-Pattern

Negative steering ("do not think of an elephant") brings the forbidden concept into context, increasing the likelihood that the model acts on it. State the positive target behavior directly so the prohibited pattern is never primed.

### Pattern Comparison

| Negative Steering (Avoid) | Direct Expected Behavior (Use) | Rationale |
|---|---|---|
| "Forbidden to edit files without prior consent" | "State the contract and authorization before editing production code." | Clear operational trigger instead of fear-based prohibition. |
| "Avoid making assumptions or guessing answers" | "Resolve uncertainty from project sources; ask only for genuine user-owned decisions." | Actionable hierarchy of resolution rather than paralysis. |
| "Barred from writing complex code or adding extras" | "Implement the smallest solution that satisfies the contract. Avoid unsolicited features." | States the design objective positively. |
| "Broken links and untested code are barred" | "Verify every local markdown link and run relevant test suites before completion." | Clear, verifiable task instead of emotional rhetoric. |
| "Do not pretend to understand without checking" | "Ground claims in observed evidence from project files or reality anchors." | Positive epistemology based on evidence. |

## Output Contract

Keep reflexive output concise (2-3 lines max):

```text
Friction: <the specific detour or wasted context observed>
Action: <pruned reference / tightened trigger / no-op>
```

## References

- [Skill Template](references/template-skill.md)

---
name: solid-loop
description: Use when applying friction notes to agent skills and instructions, or when auditing a skill for sprawl.
---

# Solid Loop

Correct the agent system from friction notes while keeping every skill as small as the fix allows.

The root virtue is **predictability**: each instruction sends the next run straight to the work, with no detour and no unneeded read.

## Apply Friction Notes

Friction notes arrive classified as `misdirection` or `gap` by the `aaaav-do` reflexive pass.

1. **Correct each misdirection.** Open the line named in `Led by`. Rewrite it to state what `Found` established, or delete it when the line has no correct form.
2. **Place each gap.** Search the agent system for a statement of the `Found` fact.
   - When one exists, the run could not reach it: sharpen the context pointer or description that should have led there.
   - When none exists, write the fact as one direct sentence in its owning location: project facts in `AGENTS.md` or `CLAUDE.md`, procedure in the skill that ran the step.
   - Scaffold a new skill from [references/template-skill.md](references/template-skill.md) only when the gap is a multi-step procedure that no skill owns.
   - A fact the change itself resolved, or a general tool-use slip that no project or skill owns, needs no placement.
3. **Hold the size.** Run the no-op test on every section you edited and delete each sentence that fails. Keep each `SKILL.md` under 300 lines; disclose reference into `references/` when it grows past that.

**Complete when:** every note has an action or is marked resolved by the change, and every edited section has passed the no-op test.

## Audit for Sprawl

Without friction notes, audit the named skill with the craft levers below, then run step 3.

## Craft Levers

Organize skill content on three tiers:

1. **In-skill steps** in `SKILL.md`: ordered actions, each ending on a checkable completion criterion.
2. **In-skill reference** in `SKILL.md`: co-located definitions, rules, and core tables.
3. **Disclosed reference** in `references/`: templates and deep catalogs reached through explicit context pointers.

- **Leading words**: Anchor behavior with compact pretrained concepts (*tight*, *red*, *tracer*, *reality anchor*) instead of spelled-out explanations.
- **Completion criteria**: Make each criterion checkable, and demanding enough to drive thorough legwork.
- **No-op test**: Evaluate each sentence in isolation and delete the ones that do not change behavior relative to the model's default.
- **Single source of truth**: Give each operational contract one canonical home.
- **Positive steering**: State the target behavior. A prohibition names the unwanted pattern and makes it more likely, so rewrite it as the behavior to perform:

| Prohibition | Expected behavior |
|---|---|
| "Forbidden to edit files without prior consent" | "State the contract and authorization before editing production code." |
| "Avoid making assumptions or guessing answers" | "Resolve uncertainty from project sources; ask only for genuine user-owned decisions." |
| "Barred from writing complex code or adding extras" | "Implement the smallest solution that satisfies the contract." |
| "Broken links and untested code are barred" | "Verify every local markdown link and run relevant test suites before completion." |
| "Do not pretend to understand without checking" | "Ground claims in observed evidence from project files or reality anchors." |

## Output Contract

Report one pair per friction note:

```text
Friction: <Found> (misdirection | gap)
Action: <corrected line | sharpened pointer | placed at <location> | resolved by the change>
```

## References

- [Skill Template](references/template-skill.md)

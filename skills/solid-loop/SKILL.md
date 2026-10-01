---
name: solid-loop
description: Use when creating, editing, or auditing agent skills and instructions, or applying friction notes.
---

# Solid Loop

Correct the agent system from friction notes, or create and edit it directly, while keeping every skill as small as the fix allows.

The root virtue is **predictability**: each instruction sends the next run straight to the work, with no detour and no unneeded read.
Remove duplication (one meaning in several places), sediment (stale layers), sprawl (length beyond use), no-op lines, and negation; prevent premature completion with checkable criteria.

## Apply Friction Notes

Friction notes arrive classified as `misdirection` or `gap` by the `aaaav-do` reflexive pass.

1. **Correct each misdirection.** Open the line named in `Led by`. Rewrite it to state what `Found` established, or delete it when the line has no correct form.
2. **Place each gap.** Search the agent system for a statement of the `Found` fact.
   - When one exists, the run could not reach it: sharpen the context pointer or description that should have led there.
   - When none exists, write the fact as one direct sentence in its owning location: project facts in `AGENTS.md` or `CLAUDE.md`, procedure in the skill that ran the step.
   - Create a new skill when the gap is a multi-step procedure that no skill owns.
   - A fact the change itself resolved, or a general tool-use slip that no project or skill owns, needs no placement.
3. **Hold the size.** Pair each added sentence with a merge or deletion in the same file, so the file ends no longer than it began.
   When a fix exposes one fact stated in several places, keep one authoritative statement and replace the rest with a pointer or delete them.
   Run the no-op test on every section you edited and delete each sentence that fails.

**Complete when:** every note has an action or is marked resolved by the change, every edited section has passed the no-op test, and no edited file is longer than before unless the addition is a multi-step procedure no skill owns.

## Create or Edit Directly

1. **Create from the template.** Start a new skill from [references/template-skill.md](references/template-skill.md), keeping only the sections its work needs.
2. **Apply the craft levers** below to the new or target skill or instruction.
3. **Hold the size.** Run the no-op test on every sentence you wrote or edited, delete each that fails, and keep each `SKILL.md` under 300 lines by disclosing reference into `references/`.

**Complete when:** the description names each branch once, every step ends on a checkable criterion, every edited section has passed the no-op test, and each operational contract has one home.

## Craft Levers

- **Information hierarchy**: Put ordered actions in `SKILL.md` as steps, co-located rules in `SKILL.md` as reference, and templates or deep catalogs in `references/` behind explicit context pointers.
- **Leading words**: Anchor behavior with compact pretrained concepts (*tight*, *red*, *tracer*, *reality anchor*) instead of spelled-out explanations.
- **Completion criteria**: Make each criterion checkable, and demanding enough to drive thorough legwork.
- **No-op test**: Evaluate each sentence in isolation and delete the ones that do not change behavior relative to the model's default.
- **Single source of truth**: Give each operational contract one canonical home.
- **Positive steering**: State the target behavior, because a prohibition names the unwanted pattern and makes it more likely.

| Prohibition | Expected behavior |
| --- | --- |
| "Forbidden to edit files without prior consent" | "State the contract and authorization before editing production code." |
| "Avoid making assumptions or guessing answers" | "Resolve uncertainty from project sources; ask only for genuine user-owned decisions." |

## Output Contract

Report one pair per friction note:

```text
Friction: <Found> (misdirection | gap)
Action: <corrected line | sharpened pointer | placed at <location> | resolved by the change>
```

For a direct create or edit, report the files changed and the net line count of each.

## References

- [Skill Template](references/template-skill.md)

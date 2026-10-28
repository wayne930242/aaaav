---
name: anchorloop
description: Use when doing loop work (change, check, iterate) that no skill was named for, especially coding; every entry skill runs this loop, and its playbooks cover unattended runs, pauses, and resuming a prior run.
---

# Anchor Loop

Every entry skill (`answering`, `investigating`, `inspecting`, `coding`, `writing`, `solid-loop`) runs this loop and supplies the steps through one of its playbooks. The target project's instructions and an exact project skill govern where they speak.

## Align

Open with one working interpretation in your own words:

    Alignment: <the requested task and intended outcome>

Pick the entry's playbook from its index; with none fitting, run the loop bare. For work longer than one increment, copy the playbook's steps verbatim into `todo`, keeping each step you will not run as `skip: <reason>`, so the plan shows what was left out and why.

## Anchor

Before the first change, state:

    Reality anchor: <the exact check that observes the result, and its checkpoint>

The anchorloop extension holds `write` and `edit` outside `scratch/` and `docs/specs/` until this line appears after the user's latest message.

Size the anchor to the change's actual reach and pick one method: an executable check, a user operation, human judgment, or a focused review. An anchor assigned by a coordinator governs. Pick a review anchor when the change touches a shared contract, authorization or permission data, a migration, or security, or when the Jev second thought rates its review `full`; other changes rest on their check and the author's own read of the diff. A review anchor names the realistic use it judges against and blocks on P0 and P1 findings only, recording lower ones as follow-ups. Answer each finding with a fix, a contest citing evidence the reviewer could read, or an escalation to the user when that evidence lives elsewhere; fill any gap a fresh reader hit. After fixes it re-checks only those findings and the lines the fixes changed, and when two consecutive rounds still raise new blocking findings the run stops and hands the trend to the user, because a fresh exploratory review each round finds new edge cases instead of converging. The checkpoint is normally once, after the last increment.

## Act

Work in the smallest useful increments through the project's native practices, deleting before adding (**Subtract before you add**).

Give follow-up work (a fix round, a retry, the next item) to a fresh subagent carrying the original brief, every later directive, and the prior report and branch, because a resumed chain silently drops directives; resume an existing subagent only for state it alone holds, such as uncommitted changes or a running process. Write briefs, follow-ups, and messages to agents by [agent-terse](../agent-terse/SKILL.md); read each subagent's output and write its summary yourself.

Report problems outside the contract as follow-ups rather than fixing them in this change, because each extra fix reopens review on code the round never meant to touch.

The reply names a [principle](PRINCIPLES.md) only when it changed a decision, together with that decision.

### Friction Notes

Each time an attempt fails and a later attempt reveals why, append a note before continuing:

    - Tried: <the attempt that failed>
      Found: <what the failure revealed>
      Led by: <the skill or instruction line that prompted the attempt, or `none`>

Keep them in `scratch/friction.md` unless the entry names another home.

### Decision Trail

A run the user reviews after stepping away records one row per fork, completed unit, pivot, or blocker in `scratch/decisions-<task-slug>.tsv` with the `anchorloop_decision` tool. Evidence is a pointer (commit, `file:line`, artifact path), never prose, and a wrong call gets a superseding row instead of an edit. Before handing back, check every row against what the run actually did and build the report from the trail.

## Verify

Exercise the anchor and report what it observed. A requirement the anchor did not exercise is `unknown`, whatever unrelated checks show. Report local tests, builds, interactive runs, commit, push, CI, and deployment as separate claims; one never stands in for another. A criterion that needs human judgment is a human checkpoint: propose a `human-feedback` pass when it is still `unknown`, and record its verdict apart from executable or review evidence.

A review anchor stays open until an independent reviewer returns its verdict. When none can run or its result is lost, report `blocked: independent review` and keep merge and release closed, because the author's own review, green tests, and CI each miss what an independent reader catches.

Write the reply the playbook's `Reply:` line names, with the anchor's evidence. A Jev second thought the extension may add after a changing run is advisory: recheck the evidence it questions, then decide. When a calling workflow supplies an artifact, write the results into it instead of a separate report or plan.

### Reflexive Pass

Run only when friction notes exist, and say nothing about it otherwise. Classify each note: **misdirection** when the `Led by` line states or implies something `Found` contradicts; **gap** when no instruction in use states the `Found` fact. A gap the change itself resolved, or a tool slip no instruction owns, is recorded as resolved. Invoke `solid-loop` with the rest.

**Complete when:** every requirement has evidence from its anchor or is reported `unknown`, and every friction note is applied through `solid-loop` or recorded as resolved.

## Playbooks

- [autonomous-run](playbooks/autonomous-run.md): the user steps away and the run drives to a predicate without them.
- [pause](playbooks/pause.md): an explicit pause, going offline, a restart, or imminent compaction.
- [pickup](playbooks/pickup.md): resuming or taking over a prior run's work.

Lifecycle playbooks wrap the entry playbook that does the work.

---

Playbooks, principles, and the decision trail are adapted from [pstack](https://github.com/backnotprop/pstack) by Lauren Tan (MIT License), revision `e44668c`. Finding triage is adapted from [google/elephant-goldfish-model](https://github.com/google/elephant-goldfish-model) (Apache-2.0), revision `a8380ab`, `skills/egm-resolve/SKILL.md`.

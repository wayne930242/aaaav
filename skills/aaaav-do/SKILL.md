---
name: aaaav-do
description: Use when executing scoped, ambiguous, or multi-step source-changing work.
---

# AAAAV Development Loop

Own source-changing work after entering the target project; its instructions and skills govern execution. Follow **AAAAV: Align → Advance → Anchor → Act → Verify**. Advance carries Decision → Spec → Design for durable Mini SDD work. Return when user intent or observable behavior changes.

## Align

Open every run with one working interpretation in the model's own words:

    Alignment: <the requested task and intended outcome>

Declare the change **Inline** or **Durable** before the first production edit:

- **Inline:** The work is simple, requirements and approach are clear, impact is bounded, and implementation and verification fit this run. State the approach and proceed under the user's existing authorization. A lasting behavior, public contract, or existing artifact can still be Inline when the change is simple; Inline requires no spec or new artifact files.
- **Durable:** The work needs a persistent design record because of material ambiguity, consequential trade-offs, complex cross-component coordination, migration risk, or continuity across sessions. A user-requested spec also follows Durable.

Inline work follows Alignment with this required line, and names the authorization only when it is in doubt:

    Inline — Contract: <one sentence of the observable behavior after the change>

Approval already given is not requested again. Durable work reads [MINI-SDD.md](MINI-SDD.md) and creates or resumes its folder before it specifies anything; that folder is its declaration.

## Advance

An inline `Contract:` is approved by the user's source-change request and skips Advance. Durable work runs Decision → Spec → Design as [MINI-SDD.md](MINI-SDD.md) describes, and Spec waits for the user's approval before any production edit.

## Anchor

Before the first production edit, state:

    Reality anchor: <the exact check that observes the changed behavior, and its checkpoint>

Point the anchor at what the change touches: the specific test, command, interface, or reviewer that observes the changed behavior, sized to the change's actual reach. A one-line instruction edit anchors on the tests that assert that file; a shared code path anchors on its callers' tests. A run with an assigned anchor takes it from its coordinator, and that anchor governs. Otherwise choose it from the task, user, and target project. Pick one method: an executable check, a user operation, human judgment, or a focused review. The checkpoint is the point where the anchor runs, normally once after the last increment. Debugging reads [DEBUGGING.md](DEBUGGING.md) and establishes its red-capable loop before diagnosing.

## Act

The harness-native plan owns sequencing. Follow the target project's native practices and work in the smallest useful increments. Mini SDD creates no `tasks.md`, agent state, or diary.

### Friction Notes

A friction note records what the run discovered through trial and error.
Each time an attempt fails and a later attempt reveals why (a command errors, a file sits elsewhere, an assumption proves wrong), append a note before continuing:

    - Tried: <the attempt that failed>
      Found: <what the failure revealed>
      Led by: <the skill or instruction line that prompted the attempt, or `none`>

Durable work appends notes under `## Friction Notes` in `design.md`; inline work appends them to `scratch/friction.md`.

Report problems found in the code the change touches as you meet them; fixes outside the contract go to the user rather than into the diff.

## Verify

A dispatched run verifies inside the anchor its coordinator assigned and hands back the completed work with that evidence.

### 1. Evidence Verification

Exercise the chosen reality anchor and capture what it observed. For Inline work, a green anchor plus a read of your own diff completes verification; report the contract with its observed output in one line. Durable work verifies as [MINI-SDD.md](MINI-SDD.md) describes. A requirement the anchor did not exercise is `unknown`; a green unrelated suite is not evidence for it. A human checkpoint owns criteria that require human judgment; record its verdict distinctly from executable or review evidence. When such a criterion is still `unknown` after the anchor runs, propose a `human-feedback` pass and carry its verdict the same way; otherwise report it as a human checkpoint without asking. When a coordinator assigned the anchor, that anchor governs.

Report local tests, builds, interactive runs, browser inspection, commit, push, CI, and deployment as separate claims; one never stands in for another.

### 2. Reflexive Pass

Run only when friction notes exist; with none, finish Verify and print nothing about it. Classify each note:

- **misdirection**: the `Led by` instruction states or implies something the `Found` line contradicts.
- **gap**: no instruction in use states the `Found` fact, so the run detoured to find it.

A gap the change itself resolved, or a general tool slip no instruction owns, is recorded as resolved. Invoke `solid-loop` with the remaining notes.

**Complete when:** every requirement has evidence from its anchor or is reported `unknown`, and every friction note is applied through `solid-loop` or recorded as resolved.

**Complete when:** every requirement has credible evidence from its chosen anchor, every friction note, if any, is applied through `solid-loop` or recorded as resolved, and every remaining verification gap is reported as incomplete.

## Standards and References

- [MINI-SDD Contract](MINI-SDD.md)
- [Debugging Branch](DEBUGGING.md)

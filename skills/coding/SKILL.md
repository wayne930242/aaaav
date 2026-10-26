---
name: coding
description: Use when changing source code or its tests, such as fixing a bug, adding or changing behavior, refactoring, improving performance, or prototyping a design question.
---

# Coding

Run the loop in [../anchorloop/SKILL.md](../anchorloop/SKILL.md) with one of the playbooks below. Return to Align when user intent or observable behavior changes.

## Classify

Before the first production edit, declare the change **Inline** or **Durable**:

- **Inline:** requirements and approach are clear, impact is bounded, and implementation and verification fit this run; a lasting behavior or public contract can still be Inline when the change is simple. Follow Alignment with `Inline — Contract: <one sentence of the observable behavior after the change>`; the user's source-change request approves it, and approval already given is not asked again.
- **Durable:** the work needs a persistent design record because of material ambiguity, consequential trade-offs, cross-component coordination, migration risk, continuity across sessions, or a user-requested spec. Read [MINI-SDD.md](MINI-SDD.md) and create or resume its folder, which keeps no `tasks.md`; Spec waits for the user's approval before any production edit.

## Anchor

Point the anchor at what the change touches: a one-line edit anchors on the tests that assert that file; a shared code path anchors on its callers' tests. For Inline work, a green anchor plus a read of your own diff completes Verify; report the contract with its observed output in one line. Durable work verifies into `verification.md` as MINI-SDD describes.

## Playbooks

- [bug-fix](playbooks/bug-fix.md): broken, failing, slow-for-a-reason, or intermittent behavior.
- [feature](playbooks/feature.md): new or changed behavior, or an interface that crosses a module.
- [refactoring](playbooks/refactoring.md): structure changes, behavior does not.
- [perf](playbooks/perf.md): a measured slowness to improve against a baseline.
- [prototype](playbooks/prototype.md): disposable code that settles a design or behavior question.

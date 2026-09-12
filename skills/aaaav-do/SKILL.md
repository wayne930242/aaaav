---
name: aaaav-do
description: Use when executing scoped, ambiguous, or multi-step source-changing work.
---

# AAAAV Development Loop

Own source-changing work after entering the target project; its instructions and skills govern execution. Follow **AAAAV: Align → Advance → Anchor → Act → Verify** (also referenced as ADAAV: Align → Advance → Anchor → Act → Verify). Advance carries Decision → Spec → Design for durable Mini SDD work. Return when user intent or observable behavior changes.

## Align

Open every run with one working interpretation in the model's own words:

    Alignment: <the requested task and intended outcome>

Declare the change **Inline** or **Durable** before the first production edit:

- **Inline:** Requirements are clear, impact is localized, implementation and verification fit this run, and the decisions have little future reuse. Inline work may change observable behavior and writes no artifact files.
- **Durable:** A decision, constraint, or proof must outlive this run -- unconfirmed design, a public or external contract, a migration, cross-component coordination, continuity across a session or handoff, a user-requested spec, or an active related artifact.

Escalate to durable when the request carries material ambiguity, spans modules or sessions, sets a lasting contract, is high risk, expands scope, or requests a spec first.

Inline work follows Alignment with these two lines. They are required output:

    Inline — Contract: <one sentence of the observable behavior after the change>
    Authorization: <the user's explicit source-change request>

Approval already given is not requested again. Durable work reads [MINI-SDD.md](MINI-SDD.md) and creates or resumes its folder before it specifies anything; that folder is its declaration.

## Advance

Once a task is dispatched, this belongs to the worker and the user; a bounded loop you carry yourself runs it inline. For Durable work:

### Decision

Resolve facts from their source; use `investigating` or `inspecting` when search is wide. Invoke `grill-with-docs` for every durable Decision step. Create `decision.md` for new work and resume a legacy artifact in place. Check that core rules are ready before implementation. Open decisions that block observable behavior are settled before proceeding.

**Complete when:** no open decision blocks observable behavior.

### Spec

State the observable contract, edge cases, compatibility constraints, non-goals, and the applied project standards. Name the reality anchor and checkpoint. Persist the durable contract in `spec.md` under `Status: proposed` before presenting it, then await explicit user confirmation.

`proposed` keeps production source untouched while artifacts and read-only work stay open. Only the user's approving reply sets `Status: approved`, `Approved at`, and `Approved from`. An inline `Contract:` is approved by its `Authorization:`.

### Design

Choose the smallest approach that fits the confirmed contract and architecture. Invoke `codebase-design` when interfaces or seams change, `prototype` when a named question is cheaper to settle by experiment, and the project's exact skill. Design is done when implementation invents no product behavior or architecture.

## Anchor

Before the first production edit, state:

    Reality anchor: <the simplest credible contact with reality and its checkpoint>

Choose it from the task, user, and target project. The method inside may use an executable check, user operation, human judgment, or focused review. Debugging reads [DEBUGGING.md](DEBUGGING.md) and establishes its red-capable loop before diagnosing.

## Act

The harness-native plan owns sequencing. Follow the target project's native practices and work in the smallest useful increments. Mini SDD creates no `tasks.md`, agent state, or diary.

## Verify

### 1. Evidence Verification

Exercise the chosen reality anchor and capture what it observed. Then review the diff separately against project standards, the approved contract, and the confirmed domain model. A human checkpoint owns criteria that require human judgment; record its verdict distinctly from executable or review evidence. When those criteria cover UI or a human-use scenario, ask the user whether to run a `human-feedback` pass, and carry its verdict the same way.

Give every requirement in the contract its own `Requirement | Evidence | Result` row, where `Result` is `pass`, `fail`, or `unknown` and `Evidence` names the real interface exercised and what it observed. A green suite, a passing unrelated check, or an agent's claim of completion is not evidence for a requirement nothing exercised; that requirement stays `unknown`.

### 2. Reflexive Pass

After functional verification, conduct a scoped reflection limited strictly to the rules, `AGENTS.md` / `CLAUDE.md`, and skills actually used during this run:

1. **Retrospective Question**: Ask *"What did I wish I knew earlier that would have reduced friction and detours in this run?"*
2. **Skill ROI Evaluation**: Audit whether each skill used helped save task time and tokens, or whether it caused detours and reading unnecessary files.
3. **Agent System Calibration**: Invoke `solid-loop` to adjust, scaffold, or prune rules and skills based on the retrospective findings. Avoid defensive phrasing or prohibitive red lines.

**Complete when:** every requirement has credible evidence from its chosen anchor, the reflexive pass has reviewed used system assets, and every remaining gap is reported as incomplete. Keep local verification, commit, push, CI, deployment, and browser proof as distinct claims.

## Standards and References

- [MINI-SDD Contract](MINI-SDD.md)
- [Debugging Branch](DEBUGGING.md)
- [Reporting Standards](references/reporting.md)
- [Communication Guidelines](references/communication.md)
- [Documentation Standards](references/documentation.md)
- [Durable Review & Pre-Flight Standards](references/durable-review.md)

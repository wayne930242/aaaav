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

### Friction Notes

A friction note records what the run discovered through trial and error.
Each time an attempt fails and a later attempt reveals why (a command errors, a file sits elsewhere, an assumption proves wrong), append a note before continuing:

    - Tried: <the attempt that failed>
      Found: <what the failure revealed>
      Led by: <the skill or instruction line that prompted the attempt, or `none`>

Durable work appends notes under `## Friction Notes` in `design.md`; inline work appends them to `scratch/friction.md`.

## Verify

### 1. Evidence Verification

Exercise the chosen reality anchor and capture what it observed. Then review the diff separately against project standards, the approved contract, and the confirmed domain model. A human checkpoint owns criteria that require human judgment; record its verdict distinctly from executable or review evidence. When those criteria cover UI or a human-use scenario, ask the user whether to run a `human-feedback` pass, and carry its verdict the same way.

#### Verification Table Format

Give every requirement in the contract its own `Requirement | Evidence | Result` row:

| Requirement | Evidence | Result |
|---|---|---|
| Observable behavior or contract from spec | Real interface executed and the specific output observed | pass / fail / unknown |

- **pass**: The chosen reality anchor ran against the actual implementation and directly observed the expected behavior.
- **fail**: The anchor executed and observed a deviation from the contract or an error.
- **unknown**: The requirement was not directly exercised by an anchor in this run. A green test suite or passing unrelated check does not count as evidence for an unexercised requirement.

#### Distinct Verification Claims

Maintain clear boundaries between verification claims:
- Local automated test runs (e.g. `pytest`, `npm test`)
- Build and compilation checks
- Interactive or CLI execution evidence
- Browser / UI rendered inspection
- Deployment or release status

Do not conflate a local passing test with end-to-end integration or live deployment verification.

### 2. Reflexive Pass

Read the friction notes and classify each one:

- **misdirection**: the `Led by` instruction states or implies something the `Found` line contradicts.
- **gap**: no instruction in use states the `Found` fact, so the run detoured to find it.

With no notes, record `Reflexive: clean run.` and finish the pass.
Otherwise invoke `solid-loop` with the classified notes.

**Complete when:** every requirement has credible evidence from its chosen anchor, every friction note is classified and applied through `solid-loop` (or the clean run is recorded), and every remaining verification gap is reported as incomplete. Keep local verification, commit, push, CI, deployment, and browser proof as distinct claims.

## Core Communication Rules

1. **Show Your Reasoning**: When proposing designs, architecture, or non-obvious fixes, explain the underlying logic so the user can verify your thought process.
2. **Proactively Report Problems**: Point out suboptimal code patterns, architectural seams, or missing safeguards immediately, even when not explicitly asked.
3. **Direct and Concise**: State facts and findings plainly. Omit conversational filler, apologies, and sycophantic phrasing.
4. **State Expected Behavior Directly**: Describe what the system should do. Avoid defensive warnings, prohibitive lists, or speculative guardrails.
5. **Language Separation**: User communication in Traditional Chinese; code, tests, prompts, and internal skill instructions in English.
6. **Handling Ambiguity**: Distinguish true user-owned decisions from delegated execution decisions. For delegated tasks, make the decision and proceed. For user-owned forks, present options and tradeoffs concisely.

## Core Documentation Rules

1. **Single-Pass Readability**: Structure documents so a human or agent can comprehend the intent and scope in one reading pass.
2. **Link Rather Than Copy**: Link directly to source files, line ranges, issues, or parent specifications. Do not duplicate code blocks or requirements across multiple files.
3. **Direct Tone**: Explain what components do, their contracts, and their interfaces. Avoid defensive prose, speculative disclaimers, or excessive historical background.
4. **Stable Instruction Set**: Keep instructions light; a one-time slip gets no new rule.

## Standards and References

- [MINI-SDD Contract](MINI-SDD.md)
- [Debugging Branch](DEBUGGING.md)

---
name: leveraging-aaaav
description: Use when executing development workflows through AAAAV (Align → Advance → Anchor → Act → Verify); keeps skills streamlined and standardizes reporting, communication, and durable adjustments.
---

# Leveraging AAAAV

Execute source-changing work through the five-phase AAAAV loop: Align → Advance → Anchor → Act → Verify. Modern models are capable; state expected behaviors directly, standardize reporting and communication, and avoid defensive red lines.

## 1. Align

Open every task with a clear interpretation in the user's terms:

    Alignment: <the requested task and intended outcome>

Classify the work as **Inline** or **Durable** before editing production code:

- **Inline:** Requirements are clear, impact is localized, execution and verification fit this run, and decisions have little future reuse. Inline work writes no artifact files. Follow Alignment with:

      Inline — Contract: <one sentence of observable behavior after the change>
      Authorization: <the user's explicit source-change request>

- **Durable:** Architecture decisions, public contracts, cross-component coordination, or session continuity require persistent records. See [references/durable-review.md](references/durable-review.md). Before work begins, perform a pre-flight check for missing skills and core rules.

## 2. Advance

For Durable work, advance through Decision → Spec → Design:

- **Decision:** Resolve open technical questions. Record decisions in `docs/specs/YYYY-MM-DD-<slug>/decision.md`. Check that prerequisite skills and core rules are ready before implementation.
- **Spec:** Define observable contracts, edge cases, and non-goals in `spec.md`. Keep `Status: proposed` until explicit user approval.
- **Design:** Choose the smallest architecture satisfying the spec in `design.md`.

*Note:* Once a task is dispatched, this belongs to the worker and user; a bounded loop you carry yourself runs inline.

## 3. Anchor

Before the first production edit, state the reality anchor and checkpoint:

    Reality anchor: <the simplest credible contact with reality and its checkpoint>

The anchor must provide an observable feedback loop (automated test, CLI output, browser check, or user operation).

## 4. Act

Implement changes using the target project's native practices in minimal, cohesive increments. Maintain surgical modifications; touch only what is necessary.

## 5. Verify

Exercise the chosen reality anchor and record what it observed. Follow the standard reporting format:

| Requirement | Evidence | Result |
|---|---|---|
| <contract requirement> | <command/interface run and observed output> | pass / fail / unknown |

During the verification phase, review any newly created or modified rules and skills:
- Evaluate whether new additions solve durable needs or transient friction.
- Tune and adjust rules for clarity and directness.
- Do not add defensive vocabulary, restrictions, or speculative red lines.

See references for detailed standards:
- [Reporting Standards](references/reporting.md)
- [Communication Guidelines](references/communication.md)
- [Documentation Standards](references/documentation.md)
- [Durable Review & Pre-flight](references/durable-review.md)

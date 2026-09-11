# Durable Review & Pre-Flight Standards

Conduct retrospectives and reviews under the Durable philosophy: avoid infinite expansion of rules and guardrails, ensure readiness before work begins, and focus reviews on tuning rather than defensive restrictions.

## 1. Pre-Flight Readiness (Before Work Begins)

Before editing code for durable tasks, verify prerequisite foundations:

1. **Check Core Rules**: Ensure project-level core principles are active and understood:
   - Traditional Chinese for communication, English for prompts/instructions.
   - Direct statement of expected behaviors without defensive phrasing.
   - Reality anchor defined before production edits.
2. **Audit Required Skills**: Identify whether the planned work requires specialized capabilities (e.g., domain modeling, API design, security scanning):
   - If a crucial skill is missing, define and introduce it before commencing production edits.
   - Supply the missing capability upfront so execution operates on established ground.

## 2. Preventing Infinite Expansion

- Modern models have strong general capabilities; avoid accumulating reactive micro-rules for every transient failure.
- When an issue occurs, determine whether it reflects an architectural ambiguity or simply an execution misstep.
- Resist creating permanent "red lines" or restrictive checklists for transient slips. Maintain a light and stable rule set.

## 3. Post-Implementation Review (During Verification)

When a task introduces new rules or new skills, review them during the Verify phase:

1. **Evaluate Purpose**: Confirm that the new rule or skill serves a durable, recurring pattern rather than an isolated edge case.
2. **Review for Adjustment (調整)**: Focus the review on tuning clarity, calibration, and trigger conditions:
   - Is the trigger condition ("Use when...") distinct and unambiguous?
   - Are expected behaviors stated directly and positively?
   - Can instructions be compacted further?
3. **Avoid Defensive Phrasing**: Do not introduce defensive vocabulary (e.g., "never under any circumstances", "strictly forbidden"). The objective is constructive alignment, not defensive obstruction.

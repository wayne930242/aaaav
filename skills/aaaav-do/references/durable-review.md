# Durable Review & Reflexive Standards

Conduct retrospectives and reviews under the Durable philosophy: avoid infinite expansion of rules and guardrails, ensure core rule readiness before work begins, and focus post-task reflection on reducing friction and detours.

## 1. Pre-Flight Readiness (Before Work Begins)

Before editing code for durable tasks, verify core foundations:

1. **Check Core Rules**: Ensure project-level core principles are active and understood:
   - Traditional Chinese for communication, English for prompts/instructions.
   - Direct statement of expected behaviors without defensive phrasing.
   - Reality anchor defined before production edits.
2. **Lean Startup**: Do not scaffold or bootstrap skills up front in Advance. Proceed directly into execution using native project practices and existing capabilities.

## 2. Preventing Infinite Expansion

- Modern models have strong general capabilities; avoid accumulating reactive micro-rules for every transient failure.
- When an issue occurs, determine whether it reflects an architectural ambiguity or simply an execution misstep.
- Resist creating permanent red lines or restrictive checklists for transient slips. Maintain a light and stable rule set.

## 3. Reflexive Review (During Verification)

After exercising the reality anchor, run a scoped Reflexive pass. Limit this review strictly to rules, `AGENTS.md` / `CLAUDE.md`, and skills actually used during the task:

1. **Retrospective Question**:
   - Ask: *"What did I wish I knew earlier that would have reduced friction and detours in this run?"*
   - Focus on concrete friction, unexpected discovery paths, or missing project context.
2. **Skill ROI Evaluation**:
   - For every skill invoked: did it save task time and tokens, or did it cause detours and reading unnecessary files?
   - If a skill forced excess context loading or confusing detours, mark it for pruning or refactoring.
3. **Calibrate via `solid-loop`**:
   - Invoke `solid-loop` to refine, tune, scaffold, or prune instructions and skills.
   - Ensure expected behaviors are stated directly and positively, avoiding defensive red lines.

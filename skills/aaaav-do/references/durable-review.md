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

After exercising the reality anchor, run a scoped Reflexive pass. Limit this review strictly to rules, `AGENTS.md` / `CLAUDE.md`, and skills actually used during the task.

### In-Flight Friction Capture (During Act)

When major friction or confusing detours occur while implementing:
- **Durable Work**: Record them directly under `## Friction Notes` in `design.md` (the implementation handoff document).
- **Inline Work**: Record them in a lightweight scratch file (e.g. `scratch/friction.md`).

This captures real runtime evidence at the moment it happens, removing retrospective guesswork.

### The Friction Gate (Early Exit)

- **Clean Run**: When no friction notes exist and execution was smooth, record: `Reflexive: Clean run, no friction or detours.` Complete immediately without invoking `solid-loop` or reading extra files.
- **Obvious Friction Only**: When friction notes exist or tangible trajectory evidence demonstrates friction:
  - Misleading context pointers that caused reading unneeded files.
  - Ambiguous skill triggers that led to multi-turn detours.
  - Missing project invariants that forced trial-and-error discovery.

### Action Priority

1. **Retrospective Question**: Ask *"What did I wish I knew earlier that would have reduced friction and detours in this run?"*
2. **Prune**: Remove unneeded references, sediment, and noisy context pointers.
3. **Tune**: Adjust the single ambiguous trigger or completion criterion in place based on the recorded friction.
4. **Scaffold (Rare)**: Bootstrap a minimal skill only when a recurring operational procedure was absent and caused major detours.

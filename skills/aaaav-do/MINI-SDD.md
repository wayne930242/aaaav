# Durable phases and artifacts

Read this when work is classified as durable. The threshold itself lives in [SKILL.md](SKILL.md); this file holds the Durable phases and what each artifact contains.

Artifacts live in `docs/specs/YYYY-MM-DD-<slug>/`. Create each file when its phase is reached, not up front. Link to project instructions, ADRs, code, research, tickets, and visuals rather than copying them.

## Decision → `decision.md`

Resolve facts from their source; use `investigating` or `inspecting` when search is wide. Invoke `grill-with-docs` only when `decision.md` has an `open` row. Check that core rules are ready before implementation.

The file holds outcome and actors; in and out of scope; concrete scenarios; confirmed decisions; open consequential decisions. Explore every consequential branch in:

```markdown
| Question | Answer | Basis | Status |
|---|---|---|---|
| ... | ... | request, evidence, or decision link | grounded, confirmed, or open |
```

Status is `grounded`, `confirmed`, or `open`. `grounded` comes from the request, source facts, or existing decisions; `confirmed` comes from the user; `open` is a consequential user-owned decision.

**Complete when:** no open row blocks observable behavior.

## Spec → `spec.md`

State the observable contract, edge cases, compatibility constraints, non-goals, and the applied project standards. Persist it in `spec.md` under `Status: proposed` before presenting it, then await explicit user confirmation. `proposed` keeps production source untouched while artifacts and read-only work stay open. Only the user's approving reply sets `Status: approved`, `Approved at`, and `Approved from`.

The file opens with the approval header, then observable behavior and edge cases; compatibility constraints and non-goals; applied standards with their impact; evidence and precedent links; the selected reality anchor and checkpoint.

```markdown
Status: proposed | approved
Approved at: <date the user approved, empty while proposed>
Approved from: <the user reply that approved it, empty while proposed>
```

## Design → `design.md`

Choose the smallest approach that fits the approved spec and architecture. Invoke `codebase-design` when interfaces or seams change, `prototype` when a named question is cheaper to settle by experiment, and the project's exact skill.

The file holds the chosen approach; interfaces and data flow affected; existing precedent; decisions, trade-offs, and risks; the method selected inside the reality anchor. A straightforward design may be short, but it still names precedent and seam. Friction notes recorded during Act go under `## Friction Notes`.

**Complete when:** implementation invents no product behavior or architecture.

## Verify → `verification.md`

Review the diff against project standards, the approved spec, and the confirmed domain model; dispatch a verification agent when the anchor needs an independent observer. Give every requirement in `spec.md` its own row:

```markdown
| Requirement | Evidence | Result |
|---|---|---|
| Observable behavior from spec | Real interface executed and the specific output observed | pass / fail / unknown |
```

- **pass**: The reality anchor ran against the actual implementation and directly observed the expected behavior.
- **fail**: The anchor executed and observed a deviation from the spec or an error.
- **unknown**: No anchor exercised the requirement in this run.

Then human appropriateness verdicts; deviations from the approved spec or design; unresolved verification gaps and their impact. When friction notes exist, include a Reflexive section listing each with its classification (`misdirection` or `gap`) and its action.

## Updates

Update the owning phase file when new information changes it. A new consequential decision returns to `decision.md`; a change to user intent or observable behavior returns to Spec and user confirmation.

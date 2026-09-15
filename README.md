# aaaav

Streamlined AAAAV agent workflow plugin for Antigravity, Claude Code, and Codex.

## Concept

AAAAV gives an agent a short, repeatable workflow built on three skills:

1. **`aaaav-do`** (development loop):
   - **Align**: Restate intent in user terms; classify the change as **Inline** (localized, clear scope) or **Durable** (a decision that outlives the run).
   - **Advance**: Durable work moves through `Decision → Spec → Design`, settling contracts, seams, and decisions.
   - **Anchor**: Name the reality anchor and checkpoint before the first production edit.
   - **Act**: Implement through the project's native practices. Every trial-and-error discovery becomes a friction note (`Tried` / `Found` / `Led by`) under `## Friction Notes` in `design.md`, or in `scratch/friction.md` for Inline work.
   - **Verify**: Exercise the anchor and report observations in a `Requirement | Evidence | Result` table. The **Reflexive** pass classifies each friction note as a **misdirection** (an instruction led the attempt the wrong way) or a **gap** (no instruction covered it, so the run detoured). A run without notes records a clean run.
2. **`solid-loop`** (agent system correction):
   - Applies classified friction notes: corrects the misleading line, or places the missing fact in its single owning location.
   - Keeps skills from sprawling: searches for an existing statement before adding one, runs the no-op test on every edited section, and keeps each `SKILL.md` under 300 lines.
3. **`boot-loop`** (agent system bootstrap):
   - Dispatches independent workers that run investigation jobs through `aaaav-do`.
   - Merges the friction notes they return and runs one `solid-loop` pass to build or refine `AGENTS.md`, `CLAUDE.md`, and project skills.

## Usage

### 1. Installation

Install across Antigravity, Claude Code, and Codex:

```bash
# Install to all supported platforms
bash scripts/install.sh --target all

# Or install to a specific platform
bash scripts/install.sh --target agy
bash scripts/install.sh --target claude
bash scripts/install.sh --target codex
```

### 2. Invoking the Development Loop

Trigger `aaaav-do` for any source-changing task:

```text
# Inline Work (Localized, clear scope)
Alignment: Add input validation for email field
Inline — Contract: Reject invalid email strings at API boundary with HTTP 400
Authorization: User request to add email validation
Reality anchor: pytest tests/test_email.py

# Durable Work (Architectural change or new spec)
Alignment: Implement multi-tenant authentication provider
# Advances through docs/specs/YYYY-MM-DD-<slug>/:
# 1. decision.md     (Resolves facts, confirms core rules)
# 2. spec.md         (Status: proposed until approved, names reality anchor)
# 3. design.md       (Minimal architecture and seams)
# 4. verification.md (Requirement | Evidence | Result table & Reflexive review)
```

### 3. Validating Workflows & Skills

Validate skills, rules, and durable artifacts:

```bash
# Run workspace validation and test suite
bash scripts/validate.sh
```

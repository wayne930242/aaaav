# aaaav-loop-boot

Streamlined AAAAV agent workflow plugin for Antigravity, Claude Code, and Codex.

## Concept

Modern foundation models are capable pair programmers. They do not require endless defensive "red lines" or exhaustive error logs. This plugin establishes high-density, actionable workflows centered on two streamlined skills:

1. **`aaaav-do`** (Development Loop):
   - **Align**: Restate intent in user terms; classify as **Inline** (fast, localized) or **Durable** (architectural, cross-session).
   - **Advance**: `Decision → Spec → Design` for Durable work. Focus on contracts, seams, and decisions; no upfront skill scaffolding.
   - **Anchor**: Name the reality anchor and checkpoint before the first production edit.
   - **Act**: Implement surgical changes through native project practices; optionally jot down major friction in `design.md` (`## Friction Notes`) or `scratch/friction.md` for Inline work.
   - **Verify**: Exercise the anchor and report observations in `Requirement | Evidence | Result` tables. Run a scoped **Reflexive** pass checking friction notes, with a default clean-run early exit.
2. **`solid-loop`** (Agent System Reflexive Audit & Solidification):
   - Invoked during the Verify Reflexive pass to audit skills and instructions used in the task.
   - Evaluates whether skills saved task time and tokens, or caused detours and reading unnecessary files.
   - Centers on the retrospective question: *"What did I wish I knew earlier that would have reduced friction and detours in this run?"*
   - Keeps skills self-contained and under 300 lines (official standard) by inlining high-priority operational references.

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

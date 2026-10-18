# aaaav

Streamlined AAAAV agent workflow package for [pi](https://github.com/earendil-works/pi).

The package provides:

- **Workflow skills** in `skills/`, loaded by pi as package skills.
- **Validator extension** `pi/validate-tool-use.ts`: after every successful `write` or `edit`, it runs `hooks/validate_tool_use.py` on the edited file and appends any suggestions to the tool result the model reads. It checks `SKILL.md` files, instruction files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `rules/`), and durable artifacts under `docs/specs/`. The extension needs `python3` on `PATH`; when the validator cannot run, the tool result says so.
- **Stream rules extension** `pi/ttsr.ts`: a port of oh-my-pi's Time Traveling Stream Rules. A Markdown rule in `~/.pi/agent/rules/` or `<project>/.pi/rules/` whose frontmatter has a `condition` regex is watched during the run. A match in streamed assistant text aborts the response, drops it, and retries with the rule injected; a match in tool arguments (the command for `bash`, the new text for `write` and `edit`) blocks the call with the rule as its reason. Frontmatter fields follow oh-my-pi: `condition`, `scope` (`text`, `thinking`, `tool`, `tool:bash`, `tool:edit(*.ts)`), `globs`, and `interruptMode` (`always`, `prose-only`, `tool-only`, `never`), plus `repeatMode` (`once` or `after-gap`) and `repeatGap`. A rule fires once per session by default. `astCondition`, `question`, and `agents` are not supported; a rule that uses them is skipped and reported. `/ttsr` lists the loaded rules.

## Concept

AAAAV gives an agent a short, repeatable workflow built on three skills:

1. **`aaaav-do`** (development loop):
   - **Align**: Restate intent in user terms; classify the change as **Inline** (localized, clear scope) or **Durable** (a decision that outlives the run).
   - **Advance**: Durable work moves through `Decision → Spec → Design`, settling contracts, seams, and decisions.
   - **Anchor**: Name the reality anchor and checkpoint before the first production edit.
   - **Act**: Implement through the project's native practices. Every trial-and-error discovery becomes a friction note (`Tried` / `Found` / `Led by`) under `## Friction Notes` in `design.md`, or in `scratch/friction.md` for Inline work. A run the user reviews after stepping away also keeps a decision trail in `scratch/decisions-<task-slug>.tsv`.
   - **Verify**: Exercise the anchor and report observations in a `Requirement | Evidence | Result` table. The **Reflexive** pass classifies each friction note as a **misdirection** (an instruction led the attempt the wrong way) or a **gap** (no instruction covered it, so the run detoured). A run without notes records a clean run.
2. **`solid-loop`** (agent system correction):
   - Applies classified friction notes: corrects the misleading line, or places the missing fact in its single owning location.
   - Keeps skills from sprawling: searches for an existing statement before adding one, runs the no-op test on every edited section, and keeps each `SKILL.md` under 300 lines.
3. **`boot-loop`** (agent system bootstrap):
   - Dispatches independent workers that run investigation jobs through `aaaav-do`.
   - Merges the friction notes they return and runs one `solid-loop` pass to build or refine `AGENTS.md` and project skills.

## Skills

| Skill | Use it when |
| --- | --- |
| `aaaav-do` | Executing scoped, ambiguous, or multi-step source-changing work. |
| `solid-loop` | Creating, editing, or auditing agent skills and instructions, or applying friction notes. |
| `boot-loop` | Bootstrapping or overhauling an agent system with investigative tracer jobs and one consolidated `solid-loop` pass. |
| `investigating` | Researching questions, diagnosing root causes, or gathering evidence. |
| `inspecting` | Auditing or reviewing a specific target, diff, commit, or spec. |
| `assuring-quality` | Final QA, exploratory verification, or release-readiness audits. |
| `human-feedback` | Evaluating human feedback or conducting interactive UI verification. |
| `grilling` | Resolving user-owned decisions or ambiguous architectural tradeoffs. |
| `grill-me` | The user asks to be grilled on an idea. |
| `grill-with-docs` | Exploring durable decisions, domain terms, or ADRs. |
| `codebase-design` | Designing or changing module interfaces and seams. |
| `domain-modeling` | Refining project terminology or domain boundaries. |
| `prototype` | Resolving an architectural question or hypothesis with disposable code. |

## Usage

### 1. Installation

Install from GitHub:

```bash
pi install git:github.com/wayne930242/aaaav
```

Or install a local checkout, which pi loads in place so edits take effect on the next session:

```bash
pi install /path/to/aaaav
```

Add `-l` to install into the current project's `.pi/settings.json` instead of your user settings. Remove it with `pi remove <same source>`.

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
# Run workspace validation and the unittest suite
bash scripts/validate.sh

# Or run the full test suite, including the pi extension test (needs node)
uv run --with pytest pytest -q
```

## Acknowledgments

Several workflow rules are adapted from [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan and its port [pstack-claude](https://github.com/michael-denyer/pstack-claude) by Michael Denyer (both MIT License): the decision trail, closed review gate, and fresh-subagent hand-off in `aaaav-do`; testing the shared premise in its debugging branch; the evidence grades in `investigating` and `inspecting`; settling observable questions by experiment in `grilling`; and encoding lessons in structure and pinning derived copies in `solid-loop`. Ported skills credit their sources in their own footers.

---
name: boot-loop
description: Use when bootstrapping or overhauling an agent system by dispatching investigative tracer jobs and harvesting friction notes for a consolidated solid-loop pass.
---

# Boot Loop

Bootstrap or overhaul a project's agent system from empirical evidence gathered by parallel investigative workers.

`boot-loop` probes the codebase through focused investigation tasks, collects the friction notes they produce, and runs one `solid-loop` pass on them.

## Workflow

### 1. Scope Investigative Tracer Jobs

Select 2 to 4 distinct, high-impact investigation targets representing primary areas of the repository:

- **Build & Test Reality**: Run test suites, typecheckers, or linters to identify local execution quirks and missing setup steps.
- **Architectural Seams**: Trace a core user flow or data pipeline to identify primary entry points and boundaries.
- **Conventions & Idioms**: Inspect typical module structure, configuration conventions, and dependency patterns.

Each job must have a concrete, falsifiable objective.

### 2. Dispatch Independent Workers (`aaaav-do`)

Dispatch isolated subagents or background workers for each target:

- Each worker follows **`aaaav-do`** (Align → Advance → Anchor → Act → Verify).
- Each worker records and classifies friction notes as `aaaav-do` defines them, then returns the classified notes instead of invoking `solid-loop`.

Wait for workers to complete their designated investigation runs.

### 3. Merge Friction Notes

Collect the classified notes from all completed workers and merge notes whose `Found` lines state the same fact.

### 4. Run One `solid-loop` Pass

Apply the merged notes through a single `solid-loop` pass.

### 5. Verify Agent System Integrity

1. Run the workspace validator (`bash scripts/validate.sh` or `python3 hooks/validate_all.py .`) to ensure:
   - Frontmatter and trigger phrasing are valid.
   - All skill bodies remain under 300 lines with valid local links.
   - Expected behaviors are stated directly without defensive phrasing.
2. Emit a concise completion summary listing:
   - Workers dispatched and jobs executed.
   - Friction notes applied and their actions.
   - Updated or created agent system components.

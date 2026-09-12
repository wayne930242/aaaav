---
name: boot-loop
description: Use when bootstrapping or overhauling an agent system by dispatching investigative tracer jobs and harvesting friction notes for a consolidated solid-loop pass.
---

# Boot Loop

Bootstrap or overhaul a project's agent system from empirical evidence gathered by parallel investigative workers.

Rather than guessing rules or scaffolding arbitrary skills up front, `boot-loop` probes the actual codebase through focused investigation tasks, gathers concrete friction, and executes a single consolidated `solid-loop` pass to establish a predictable, lean harness.

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
- Instruct each worker to record concrete runtime friction into its `Friction Notes` (e.g. `scratch/friction.md` or `design.md`):
  - Where did the worker stall or take unproductive detours?
  - Which files or context pointers caused wasted reads?
  - What missing domain invariants or command conventions forced trial-and-error?

Wait for workers to complete their designated investigation runs.

### 3. Harvest and Synthesize Friction Notes

Collect the `Friction Notes` and trajectories from all completed workers:

1. **Group Shared Detours**: Identify recurring obstacles (e.g. multiple workers failed to locate the test runner or misidentified project layout).
2. **Filter Noise**: Separate transient slips from systemic gaps. Keep only high-signal friction backed by trajectory evidence.
3. **Anchor on Retrospection**: Synthesize with the core question:
   > *"What should any agent entering this project know upfront to eliminate these detours?"*

### 4. Execute Consolidated `solid-loop` Pass

Run a single, authoritative `solid-loop` cycle on the synthesized findings:

- **Prune**: Cut misleading instructions, stale configuration references, or bloat from existing rules and skills.
- **Tune Root Files**: Update `AGENTS.md` / `CLAUDE.md` with verified reality anchors, project build/test commands, and non-negotiable conventions (stated directly and positively).
- **Scaffold Core Skills (if needed)**: Bootstrap lean skills for recurring, non-trivial workflows identified by workers using [solid-loop's template](../solid-loop/references/template-skill.md).

### 5. Verify Agent System Integrity

1. Run the workspace validator (`bash scripts/validate.sh` or `python3 hooks/validate_all.py .`) to ensure:
   - Frontmatter and trigger phrasing are valid.
   - All skill bodies remain under 300 lines with valid local links.
   - Expected behaviors are stated directly without defensive phrasing.
2. Emit a concise completion summary listing:
   - Workers dispatched and jobs executed.
   - Synthesized friction points addressed.
   - Updated or created agent system components.

Status: approved
Approved at: 2026-10-21
Approved from: 「批准，照這份做」; push 授權：「可以，驗完就 push」

# Spec: aaaav 1.0

Three phases, each verified before the next. Every new or edited sentence passes the no-op test; a playbook holds only steps the model would not take by default.

## Phase 1: skill tree

### Layout

```text
skills/
  aaaav/          SKILL.md (loop) · PRINCIPLES.md · playbooks/{autonomous-run,pause,pickup}.md
  answering/      playbooks/{explain,compare}.md
  investigating/  playbooks/{research,diagnose}.md
  inspecting/     playbooks/{diff-review,qa-release}.md
  coding/         MINI-SDD.md · playbooks/{bug-fix,feature,refactoring,perf,prototype}.md
  writing/        playbooks/{draft,tighten,comments}.md
  solid-loop/     playbooks/{apply-friction,author-skill,bootstrap}.md · references/
  grilling/  domain-modeling/ (CONTEXT-FORMAT.md, ADR-FORMAT.md)  human-feedback/
```

### Core `aaaav`

Holds what stays true for every task type (harness² invariant test): Align → Anchor → Act → Verify with the Reflexive pass, friction notes, the decision trail (through the extension tool), fresh-subagent hand-off, the review gate, and separate delivery claims. Align restates the task, picks the entry's playbook, and, for work longer than one increment, copies its steps into `todo`, marking a step it will not run `skip: <reason>`. Its description triggers on unattended, paused, and resumed runs.

### Entries

Each entry `SKILL.md` has a description in the user's words, one line pointing to the core loop, the entry's anchor, and a playbook index (name and trigger per line). Each playbook has a bold ownership line, numbered steps, and a `**Reply:**` line.

| Entry | Anchor | Playbooks and their non-default steps |
|---|---|---|
| answering | every material claim carries its source and evidence grade | explain: mechanism first, smallest view; compare: options against criteria, a recommendation, push back on a wrong premise |
| investigating | the question is answered or the missing evidence is named | research: primary sources, cross-check, grades; diagnose: red-capable observation before theory, deliverable is a diagnosis |
| inspecting | every scoped item has a verdict and evidence | diff-review: current DIFF-REVIEW; qa-release: current assuring-quality |
| coding | the check that observes the changed behavior | bug-fix: current DEBUGGING, revert "might help" changes, repro before fix in history; feature: data shape and structure before logic, interface design when crossing a module, throughput checkpoint; refactoring: pin behavior first (type check and lint do not count), subtract first, migrate callers and delete the old API in one wave, revert when reader load did not drop; perf: repeated baseline, explain what limits the number, one change at a time; prototype: current prototype skill |
| writing | a reader without context can say what the document asks of them; comment-only work changes no behavior | draft: reader and decision first; tighten: delete before rewording; comments: keep only a why the code cannot show |
| solid-loop | validator clean and every edited section passes the no-op test | apply-friction and author-skill: current sections; bootstrap: current boot-loop |

Inline/Durable classification and MINI-SDD move to `coding`. `writing` loads `writing-in-weihung-voice` for Traditional Chinese articles when that skill exists.

### Principles

`aaaav/PRINCIPLES.md`: about twelve named principles (name, when it applies, one-sentence rule), credited to pstack with its revision. The final reply names a principle only when it changed a decision, with that decision.

### solid-loop changes from harness²

- Placement test: a fix that holds for every task type goes to the core; one that holds for a task type goes to its entry or playbook; one that holds for one project goes to that project's instructions.
- Cheapest effective mechanism, replacing step 3's wording without growing it: script for repeated deterministic work, skill for a triggered multi-step procedure, tool-loop lever (extension hook) for a check the model demonstrably skips, prose for judgment.
- A friction note with no before/after contrast gets no placement.

### Merges and deletions

grill-me and grill-with-docs fold into grilling; boot-loop into solid-loop; assuring-quality into inspecting; prototype, codebase-design, and DEBUGGING.md into coding; `aaaav-do` is renamed `coding`. No file outside `docs/specs/` names a deleted skill or file afterward.

### Validator

Local Markdown links are checked in every `.md` under a skill directory, and a file counts as referenced when `SKILL.md` or a file it links to references it.

### weihung-agent-root

The AGENTS.md.in routing paragraph becomes one line pointing to the entry skills. `providing-knowledge` is deleted; its presentation part (HTML page, show_doc, Chawan limits) becomes `rules/presenting.md`. `going-to-sleep` points to the core lifecycle playbooks instead of restating them. README tables and install tests follow.

## Phase 2: pi-aaaav extension

Added beside the existing validator and TTSR extensions, each a small file under `pi/`.

- **Anchor gate.** `tool_call` on `write` or `edit` blocks when no assistant text since the latest user message contains `Reality anchor:` and the path is outside `scratch/`, `docs/specs/`, and temp dirs. The block reason names the fix. The prose rule in both AGENTS.md files is deleted.
- **Decision tool.** `aaaav_decision` appends a row (decision, why, evidence, result, optional `start`) to `scratch/decisions-<task-slug>.tsv` with the current escaping rules. `decision_log.py` and its test are deleted; the tests move to the extension.
- **Jev second thought.** On `agent_before_settle`, when the run called `write`, `edit`, or `bash` and `TYPESAFE_API_KEY` is set, ask Jev three questions (done, review tier, quality) over the latest user request and the final reply, each truncated. When done < 0.5, quality < 1.5, or review is `full`, append a visible message with the numbers and continue once so the agent rechecks its evidence; it may disagree and finish. Otherwise record the numbers as a custom entry. At most one continuation per user message. An API failure records `unknown` and continues nothing. Thresholds live in one constant table.

## Phase 3: release

Package renamed `pi-aaaav`, `private` removed, version 1.0.0 in `package.json`, `pyproject.toml`, and `uv.lock`; README and README.zh-TW describe the tree and the extension and pin the upstream revisions. Published to npm through `publishing-pi-extensions`; the user enters the OTP. Agent-root switches its install source to `npm:pi-aaaav`.

## Reality anchor

Phase 1: `uv run python hooks/validate_all.py .` clean; `uv run --with pytest pytest -q` green, including a broken link inside a playbook being reported; a grep showing no reference to a deleted skill or file outside `docs/specs/` in either repo; agent-root's test suite green; one independent `reviewer` pass over the skill text, blocking on contradictions between core, entry, and playbook, stale pointers, and departures from this spec.
Phase 2: extension tests with an injected fetch cover gate block and allow, decision rows, Jev disagreement (one continuation), agreement (entry only), and failure (nothing continues); one live pi run in print mode against real Jev with a synthetic task.
Phase 3: `npm pack --dry-run` lists only package files; `pi install npm:pi-aaaav` on a fresh agent-root install loads all extensions and skills.
Checkpoint: each phase's anchor runs once after its last increment; push and publish follow phase 3.

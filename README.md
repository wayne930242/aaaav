# pi-anchorloop

[繁體中文](README.zh-TW.md)

Agent workflow skills and loop extensions for [pi](https://github.com/earendil-works/pi). Every main task type enters through its own skill, picks a playbook, and runs one shared loop: **Align → Anchor → Act → Verify**.

## Skills

```text
anchorloop            core loop · principles · playbooks: autonomous-run, pause, pickup
├─ answering     explain · compare
├─ investigating research · diagnose
├─ inspecting    diff-review · qa-release
├─ coding        bug-fix · feature · refactoring · perf · prototype  (+ Mini SDD)
├─ writing       draft · tighten · comments
└─ solid-loop    apply-friction · author-skill · bootstrap
shared           grilling · domain-modeling · human-feedback · agent-terse
```

- **`anchorloop`** holds what is true for every task type: restate the task, pick the entry's playbook, keep real work items in `todo` (its first create opens a loop), state a `Reality anchor:` before the first change, work in small increments deleting before adding, verify against the anchor, and record friction notes. The Reflexive pass hands friction notes to `solid-loop`. `PRINCIPLES.md` names the principles playbooks cite and the user can steer with. The lifecycle playbooks cover unattended runs, clean pauses, and picking up a prior run.
- **Entry skills** each name the anchor for their task type and index their playbooks. A playbook has an ownership line, numbered steps, and a `Reply:` line that sets what the final report contains.
- **Shared skills** are called by entries: `grilling` for user-owned decisions, `domain-modeling` for terms and ADRs, `human-feedback` for reactions to working output, `agent-terse` for text only agents read: briefs, reports, and agent messages.

## Extensions

| File | What it does |
| --- | --- |
| `pi/book.ts` | The loop book. The first `todo` create opens a loop; the agent declares its kind (`quick`, `inline`, `reviewed`, `durable`) and each stage with the `anchorloop_stage` tool, and the extension attaches evidence: diff stats against each repo's base `HEAD`, the exit code and last line of the bash call that ran the anchor, reviewer `Blocking: P0=<n> P1=<m>` counts, and summaries of `docs/specs/*/` artifacts as they are edited. It also records each todo with its `anchor`, `ref` (`<path>#<heading>`, resolved to line ranges), and `followup` metadata. One YAML book per open loop lives under `~/.pi/agent/anchorloop/books/` (`ANCHORLOOP_BOOKS_DIR` overrides it), subagent books under `agents/`; `session_start` sweeps books whose session is gone. `close` is manual and refuses while a pending or in-progress todo lacks `metadata.followup` (a ticket id, `memory`, or `drop — <reason>`); missed stages only warn. |
| `pi/anchor-gate.ts` | Inside an open loop, shows one warning per user message when `write` or `edit` runs before the loop has an `anchor` stage or the assistant states `Reality anchor:`, and one warning per durable loop when a production edit runs while the recorded spec is not `Status: approved`; the call still goes through. Outside a loop and in `quick` loops it stays silent. `.md`, `.txt`, and `.html` files, `scratch/`, `docs/specs/`, and temp files outside the project pass silently. Edits made through `bash` are not checked. |
| `pi/decision-tool.ts` | The `anchorloop_decision` tool appends single-line, spreadsheet-safe rows to a decision trail TSV, or a `start` row when a run picks up another run's trail. |
| `pi/second-thought.ts` | Inside an open loop, asks Jev (TypeSafe's typed-decision model, through pi's classifier registry) what to do next when a run settles and the loop book gained an entry since the last judgment, and at a `close` declaration. Jev sees only the book: kind, intent, anchor, diff summary (≤1200 chars), verify state (stages, review rounds, child checks), the open todo count, and the task list. Its main output is a next-stage suggestion (`continue`, `verify`, `review`, `fix`, `close`, `ask-user`), shown as an advisory that leads with `next → <stage>` and the book facts behind it; alongside it come `done` (does the evidence cover the intent), the review tier still needed, and quality. The run continues once, only when the suggestion is `verify`, `review`, or `fix` and the book shows that stage missing after the last `act`; a `full` rating after a clean review that follows the last `act` shows a note instead of a recheck. A run that called `MonitorCreate`, `LoopCreate`, `goal_wait`, or a `subagent` tool is waiting and is not judged. Without a TypeSafe key it does nothing, and outside a loop it never runs. In a subagent session (`PI_SUBAGENT_ID` from pi-herdr-agents, or `PI_SUBAGENT_CHILD` from pi-subagents) it registers nothing, since the agent that spawned it judges the result. |
| `pi/validate-tool-use.ts` | After each `write` or `edit`, validates the file in-process (`pi/support/validators.ts`, a port of `hooks/validators/`) and appends suggestions for `SKILL.md`, instruction files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `rules/`), and `docs/specs/` artifacts. Needs no Python; the Python validators in `hooks/` remain for `validate_all.py` and the parity test. |
| `pi/ttsr.ts` | A port of oh-my-pi's Time Traveling Stream Rules. A Markdown rule in `~/.pi/agent/rules/` or `<project>/.pi/rules/` whose frontmatter has a `condition` regex is watched during the run. A match in streamed assistant text aborts the response, drops it, and retries with the rule injected; a match in tool arguments (the command for `bash`, the new text for `write` and `edit`) blocks the call with the rule as its reason. Frontmatter fields follow oh-my-pi: `condition`, `scope` (`text`, `thinking`, `tool`, `tool:bash`, `tool:edit(*.ts)`), `globs`, and `interruptMode` (`always`, `prose-only`, `tool-only`, `never`), plus `repeatMode` (`once` or `after-gap`) and `repeatGap`. A rule fires once per session by default. `astCondition`, `question`, and `agents` are not supported; a rule that uses them is skipped and reported. `/ttsr` lists the loaded rules. |

## Install

Install the npm package `pi-anchorloop`; it is the recommended way to use anchorloop:

```bash
pi install npm:pi-anchorloop
```

A local checkout loads in place, so edits take effect on `/reload`:

```bash
pi install /path/to/anchorloop
```

## Develop

```bash
uv run python hooks/validate_all.py .   # skills, rules, and durable specs
uv run --with pytest pytest -q          # validators and the pi extensions (needs node)
```

## Acknowledgments

- [pstack](https://github.com/backnotprop/pstack) by Lauren Tan (MIT), mirror revision `e44668c` of [cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack), and its port [pstack-claude](https://github.com/michael-denyer/pstack-claude) by Michael Denyer (MIT): task-type playbooks, named principles, the lifecycle playbooks, the decision trail, the closed review gate, fresh-subagent hand-off, and evidence grades.
- [google-research/harness2](https://github.com/google-research/harness2) (Apache-2.0), revision `1cfe254`: solid-loop's placement test, cheapest-mechanism order, and declining a lesson without a before/after contrast.
- [mattpocock/skills](https://github.com/mattpocock/skills) (MIT): grilling, domain-modeling, the diff review, the prototype playbook, and the feature playbook's interface checks.
- [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) (Apache-2.0), revision `bad48a0`: the terse voice in `agent-terse`.
- HumanLayer's [show-me](https://github.com/humanlayer/skills/tree/main/plugins/show-me) (MIT): the views in `answering`.
- [oh-my-pi](https://github.com/can1357/oh-my-pi): Time Traveling Stream Rules.

Ported files credit their sources in their own footers.

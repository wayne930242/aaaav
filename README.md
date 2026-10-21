# pi-aaaav

[繁體中文](README.zh-TW.md)

Agent workflow skills and loop extensions for [pi](https://github.com/earendil-works/pi). Every main task type enters through its own skill, picks a playbook, and runs one shared loop: **Align → Anchor → Act → Verify**.

## Skills

```text
aaaav            core loop · principles · playbooks: autonomous-run, pause, pickup
├─ answering     explain · compare
├─ investigating research · diagnose
├─ inspecting    diff-review · qa-release
├─ coding        bug-fix · feature · refactoring · perf · prototype  (+ Mini SDD)
├─ writing       draft · tighten · comments
└─ solid-loop    apply-friction · author-skill · bootstrap
shared           grilling · domain-modeling · human-feedback · agent-terse
```

- **`aaaav`** holds what is true for every task type: restate the task, pick the entry's playbook and copy its steps into `todo`, state a `Reality anchor:` before the first change, work in small increments deleting before adding, verify against the anchor, and record friction notes. The Reflexive pass hands friction notes to `solid-loop`. `PRINCIPLES.md` names the principles playbooks cite and the user can steer with. The lifecycle playbooks cover unattended runs, clean pauses, and picking up a prior run.
- **Entry skills** each name the anchor for their task type and index their playbooks. A playbook has an ownership line, numbered steps, and a `Reply:` line that sets what the final report contains.
- **Shared skills** are called by entries: `grilling` for user-owned decisions, `domain-modeling` for terms and ADRs, `human-feedback` for reactions to working output, `agent-terse` for text only agents read: briefs, reports, and agent messages.

## Extensions

| File | What it does |
| --- | --- |
| `pi/anchor-gate.ts` | Holds `write` and `edit` until the assistant states `Reality anchor:` after the user's latest message. `scratch/`, `docs/specs/`, and temp files outside the project pass. Edits made through `bash` are not gated. |
| `pi/decision-tool.ts` | The `aaaav_decision` tool appends single-line, spreadsheet-safe rows to a decision trail TSV, or a `start` row when a run picks up another run's trail. |
| `pi/second-thought.ts` | Before a run that called `write`, `edit`, or `bash` settles, asks Jev (TypeSafe's typed-decision model, through pi's classifier registry) whether the final reply shows the request met, which review tier it needs, and its quality. When quality < 1.5 or the tier is `full`, it adds one visible advisory message and one continuation; the agent may disagree and finish. When only done < 0.25, the message is shown without a continuation. The request is the latest message the user typed; messages extensions send (intercom, monitor wakes) do not replace it. A run that called `MonitorCreate`, `LoopCreate`, `goal_wait`, or a `subagent` tool is waiting on a wake and is not judged. Only the request and the final reply are sent. Without a TypeSafe key it records `unknown` and does nothing. |
| `pi/validate-tool-use.ts` | After each `write` or `edit`, runs `hooks/validate_tool_use.py` on the file and appends suggestions for `SKILL.md`, instruction files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `rules/`), and `docs/specs/` artifacts. Needs `python3` on `PATH`. |
| `pi/ttsr.ts` | A port of oh-my-pi's Time Traveling Stream Rules. A Markdown rule in `~/.pi/agent/rules/` or `<project>/.pi/rules/` whose frontmatter has a `condition` regex is watched during the run. A match in streamed assistant text aborts the response, drops it, and retries with the rule injected; a match in tool arguments (the command for `bash`, the new text for `write` and `edit`) blocks the call with the rule as its reason. Frontmatter fields follow oh-my-pi: `condition`, `scope` (`text`, `thinking`, `tool`, `tool:bash`, `tool:edit(*.ts)`), `globs`, and `interruptMode` (`always`, `prose-only`, `tool-only`, `never`), plus `repeatMode` (`once` or `after-gap`) and `repeatGap`. A rule fires once per session by default. `astCondition`, `question`, and `agents` are not supported; a rule that uses them is skipped and reported. `/ttsr` lists the loaded rules. |

## Install

```bash
pi install npm:pi-aaaav
```

A local checkout loads in place, so edits take effect on `/reload`:

```bash
pi install /path/to/aaaav
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

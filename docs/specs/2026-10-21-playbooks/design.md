# Design: aaaav 1.0

## Approach

Move before writing: `git mv` each surviving file to its new home first, so history follows the content, then cut each moved file to its playbook shape. New prose is written only for answering, writing, feature, refactoring, perf, the lifecycle playbooks, and the principles.

Cross-skill pointers are relative paths (`../aaaav/SKILL.md`); the validator already resolves links against the skill directory, and Phase 1 extends it to sub-files.

## Seams

- Core ↔ entry: an entry names the core loop once and adds only its anchor and playbook index. The core never names an entry's steps.
- Entry ↔ playbook: the index line is the only routing; a playbook does not restate the loop.
- Skills ↔ extension (Phase 2): the core names `aaaav_decision` and states that the anchor gate and the Jev second thought exist; their mechanics live in code.
- aaaav ↔ agent-root: agent-root owns presentation (`rules/presenting.md`), voice, and the sleep/remote rituals; aaaav owns process.

## Precedent

pstack `poteto-mode/playbooks/*.md` (ownership line, steps, Reply); harness2 `core/prompts.py` `_TTS_INV`/`_TTS_DOM` and `experience()`; this repo's `pi/ttsr.ts` for `tool_call` blocking and `pi.appendEntry`.

## Risks

- Renaming `aaaav-do` breaks agent-root text and memory notes that name it; the grep anchor covers both repos, and memory notes are history.
- The anchor gate can block legitimate follow-up edits; the reason text names the one-line fix, and Phase 2's live run checks the friction.

## Friction Notes

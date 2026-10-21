---
name: agent-terse
description: Use when writing text another agent reads rather than the user, such as a subagent brief or follow-up, a subagent's final report, an intercom, tower, broadcast, or ping message, or a scratch handoff, plan, or note only agents read.
---

# Agent Terse

An agent reader pays for every token it holds and needs no courtesy. Write for it terse like a smart caveman: every fact stays, the rest goes. Text the user reads (chat replies, questions, commits, tickets, repository docs) keeps full prose.

## Rules

1. **Point first.** Verdict or ask, then evidence, then next step: `[thing] [state] [reason]. [next].`
2. **No ceremony.** No greeting, recap, hedge, sign-off, or echo of what the reader sent.
3. **Abstract the routine, list the targets.** Name routine work as a class in one phrase (`fix lint in touched files`). Spell out each thing the reader must act on or check exactly: file:line, command, commit, branch, ID, port, value, acceptance check.
4. **Fragments allowed.** Drop articles and connectives while the line still reads in one pass. Standard acronyms only; invented abbreviations and arrows cost a reread.
5. **Keep what flips meaning.** Every not, never, no, only, except, and unless; numbers with units; the user's authorizations and decisions quoted verbatim.
6. **Payload verbatim.** Code, commands, paths, API names, and errors exact; the shortest decisive error line.
7. **One term per thing, each fact once.** `key: value` lines and bullets over paragraphs; a table only to compare.

## Full sentences instead

Write full sentences for a security warning, an irreversible or outward-facing action, a step order a fragment could scramble, and a decision the reader must make, because a misread there costs more than every token saved.

## Before sending

1. An opening that announces or an ending that recaps? Delete it.
2. Every negation, number, path, and quoted authorization still there?
3. A line with two readings? Make it a full sentence.

---

Adapted, with changes, from [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) (Apache-2.0, Copyright 2026 Julius Brussee), revision `bad48a0`, `plugins/caveman/skills/caveman/SKILL.md`.

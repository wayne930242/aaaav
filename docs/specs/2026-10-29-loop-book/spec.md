Status: approved
Approved at: 2026-10-29
Approved from: user replies 2026-10-29 00:2x–01:0x (「同意」 v1; v2 notes; v3 「可以」 with the spec-file note below)

# Spec: loop book

An agent declares where its anchorloop loop stands with one tool; the extension attaches evidence, keeps one YAML book per open loop, and gives the Jev second thought the book's intent, diff summary, and verify state instead of excerpts of the request and reply. Gates exist to make work easier: a missed stage warns, never blocks, except closing a loop with undisposed todos.

## Behavior

### Loop lifecycle

- No open loop: nothing is gated or recorded; the anchor gate and the second thought stay silent. Simple work runs without ceremony.
- The first `todo` create while no loop is open opens a loop and its book. The todo tool result gets one appended line telling the agent to declare the loop kind. A `todo` create while a loop is open extends that loop.
- Only one loop is open per session. A second `kind` declaration on an open loop changes (upgrades) its kind; it never opens a new loop.
- `close` is manual. It refuses while any `pending` or `in_progress` todo lacks `metadata.followup` set to a ticket id, `memory`, or `drop — <reason>`, and lists those todos. On success it appends one custom session entry (intent, kind, verdict, stages, review rounds, diff summary, followups), deletes the book file and its child books, and tells the agent to clear the todo list.
- A new loop cannot open until the open one is closed.

### Loop kinds and their stages

| Kind | Use | Stages expected |
|---|---|---|
| `quick` | config, typo, small tweak | `act`, `check`, `close` |
| `inline` | clear scope, finishes this run | `anchor`, `act`, `verify`, `close` |
| `reviewed` | shared contract, authorization or permission data, migration, security | `anchor`, `act`, `verify`, `review`×N, `close` |
| `durable` | MINI-SDD | `decision`, `spec`, `design`, then as `reviewed` |

Any stage accepts `skip: <reason>`. Missing stages produce warnings, not refusals:
- `inline`/`reviewed`/`durable`: a `write` or `edit` outside the anchor-gate exemptions before an `anchor` stage warns once (the existing anchor gate, now active only inside an open loop; the `Reality anchor:` line also counts as the anchor stage).
- `durable`: a production edit while the spec's `Status:` is not `approved` warns once.
- `reviewed`/`durable`: two consecutive review rounds with blocking findings warn: stop and hand the trend to the user.

### Tool `anchorloop_stage`

| Call | Agent supplies | Extension attaches |
|---|---|---|
| `kind` | kind, one-line intent | base `HEAD` of the session cwd's repo; repos of later edited paths are added with their `HEAD` at first touch |
| `anchor` | the check (command or review) | — |
| `act` | optional note | diff stat against each base |
| `check` / `verify` | optional note | exit code and last output line of the latest bash call whose command contains the anchor command; `unknown` when none ran |
| `review` | optional note | round number; P0/P1 counts from the latest reviewer result's `Blocking: P0=<n> P1=<m>` line, else a Jev yes/no on blocking findings |
| `decision` / `spec` / `design` | optional note | see Durable artifacts |
| `close` | `landed`, `blocked`, or `abandoned` | todo check, diff summary, review rounds |
| `read` | `summary` (default) or `all` | about five lines: kind, stages done, last verify, review rounds and trend, open children |

In a subagent (`isSubagent()` in `pi/second-thought.ts`), the book lives under the child's `PI_SUBAGENT_ID` and a declared `verify` is recorded as `check`; only main records `verify` and `review`. Main links a child book when its `subagent` tool result returns the child id, and `read` includes each linked child's summary.

### Friction and reflection

Agents write their own mistakes and friction into the book, so the reflexive loop reads one source:

- `anchorloop_stage friction` with `tried`, `found`, and `led_by` (the skill or instruction line that prompted the attempt, or `none`) appends a numbered `friction` entry. Main and subagents both write it; a child's friction shows in main's `read` and in the Jev state under its child id.
- The book records failed attempts automatically: each anchor, check, or task-anchor run keeps its exit code, so a fail later followed by a pass is visible as a `retry` pair without any agent call.
- `anchorloop_stage reflect` with `friction` ids, `class` (`misdirection`, `gap`, or `resolved`), and `action` (e.g. `solid-loop`, `memory`, a commit) appends a `reflect` entry.
- Second thought adds two next-stage choices: `friction` when the book shows a `retry` pair with no friction entry after it, and `reflect` when friction entries lack a `reflect`. Both are advisory.
- `close` does not refuse over friction. Its session entry carries every friction entry with its reflect class, so the record survives the book's deletion, and its result lists unreflected friction for the Reflexive Pass.
- The Friction Notes section of `skills/anchorloop/SKILL.md` points to `anchorloop_stage friction` instead of `scratch/friction.md`; the Reflexive Pass reads the book's friction entries.

### Todo links

Inside an open loop, each `todo` create or update is recorded as a task entry carrying its id, subject, status, and these `metadata` keys when present:

- `anchor`: the task's own check (command or review); a task without one inherits the loop anchor.
- `ref`: one or more `<path>#<heading>` pointers into a spec, design, or other doc. The book resolves each heading to its current line range when recording (`spec.md#Second thought → L88-L101`) and re-resolves at `read`; a heading that no longer exists shows `missing`.
- `followup`: as in Loop lifecycle.

The Jev state includes this task list with a one-line legend (`#id status subject — anchor (last exit) — ref → line range; missing = heading gone`), so Jev can judge each task's own anchor and spec coverage.

`read` lists each task as `#id status subject — anchor — refs (line ranges)` and, when a bash call matched a task's own `anchor`, its last exit code. A task in an `inline`, `reviewed`, or `durable` loop without `anchor` or `ref` is recorded as is; no warning. The skill text mentions the keys once, as optional, in a clause where `todo` is introduced (e.g. "a todo may carry `anchor` or `ref` in its metadata when its check or source differs from the loop's"); it does not ask agents to fill them, because the second thought catches missing coverage. `followup` is named only in the close rule.

### Durable artifacts recorded automatically

A successful `write` or `edit` to `docs/specs/*/{decision,spec,design,verification}.md` inside an open loop appends an entry with a brief content summary, without any agent call:
- `decision.md`: row counts by status (`grounded`, `confirmed`, `open`) and the questions of rows whose status changed since the last entry.
- `spec.md`: its `Status:` value and the headings whose text changed.
- `design.md`, `verification.md`: headings whose text changed; for `verification.md`, pass/fail/unknown counts.

Repeated edits during grilling produce one entry each, so the book shows the spec converging.

### Book file

Valid YAML at `~/.pi/agent/anchorloop/books/<project-slug>/<book-id>.yml`, children under `agents/<PI_SUBAGENT_ID>.yml`. A header written once (book id, owner, session file, kind, intent, bases), then `entries:` with one flow mapping per line, each appended with a single `O_APPEND` write. Kind changes and new bases are entries, never header rewrites.

`session_start` deletes books whose owner session file no longer exists and child books linked to no open book, and lists the deletions; open books of live sessions stay and are listed.

### Second thought

- Runs only while a loop is open: when a run settles and the book gained an entry since the last judgment, and at a `close` declaration.
- Sends Jev only `kind`, `intent`, `anchor`, `diff` (≤1200 chars), `verify` (stages, review rounds, child checks), and `todos` (open count) from the book. The `checkpoint` question is removed.
- Its main output is a **next-stage suggestion**, a choice question: `continue` (keep acting), `verify`, `review`, `fix`, `close`, or `ask-user`. `done` asks whether the verify evidence covers the intent; `review` asks which review the diff still needs given the recorded reviews; `quality` is unchanged.
- The advisory message to main leads with the suggestion, e.g. `Second thought: next → close (verify pass after last change, review r2 clear, 0 open todos)`. It is advisory; it continues the run only when the suggestion is `verify`, `review`, or `fix` and the book shows that stage missing after the last `act`, once per run.
- When a review is recorded after the last `act`/`fix` with no open blocking finding, a `full` rating shows a note and does not request a recheck.

### Skill text trims

- A: delete the rule that a Jev `full` rating forces a review anchor; review anchors come from the explicit list or the user, and Jev's tier is advisory.
- B: `Alignment:` and `Reality anchor:` are required only inside an open loop.
- C: `todo` holds real work items only; stop copying playbook steps with `skip:` lines; stage progress lives in `anchorloop_stage`.
- D: feature playbook's four throughput todos only when dispatching parallel workers.
- E: a small fix that main holds full context for is made by main; larger follow-up rounds go to a fresh subagent.
- F: drop "continuity across sessions" from the Durable threshold; the book and `pickup` carry continuity.
- Unchanged: the fresh-reader spec check in MINI-SDD.

## Non-goals

Blocking any tool besides `close`; recording stages without a declared loop; changing `anchorloop_decision`.

## Reality anchor

`uv run --with pytest pytest -q` with new tests covering: todo-opens-loop and extend; kind upgrade; close refusal listing undisposed todos and success deleting books plus the session entry; evidence attachment from bash exit codes; `Blocking:` parsing; durable artifact summaries across repeated edits; subagent verify recorded as check and child linking; second-thought state built from the book, silence without a loop, recheck suppression; stale-book sweep; YAML validity under parallel appends. Plus `uv run python hooks/validate_all.py .`. Then one fresh-context reviewer, because the second thought's judging interface changes.

# Decision: aaaav 1.0, entry tree and pi-aaaav extension

## Outcome and actors

Every main task type, not only coding, enters through its own skill, which carries a set of playbooks over one shared AAAAV loop. Programmatic parts of the loop run in a pi extension instead of prose. Sources: pstack `e44668c` (playbooks, principles, lifecycle), google-research/harness2 `1cfe254` (invariant/domain placement, cheapest mechanism, no lesson without a contrast), TypeSafe Jev (typed decisions; probe `/tmp/jev-probe.py`), reports `/tmp/aaaav-pstack-review.html` and `/tmp/aaaav-entry-tree.html`.

## Scope

In: the three-layer skill tree, its playbooks and principles index, the merges and deletions, the `pi-aaaav` extension (anchor gate, decision tool, Jev second thought), npm publication, and the weihung-agent-root changes the tree requires.

Out: skill evals, a user guide, per-principle skills, a pstack-style single front door, a hard word budget.

## Decisions

| Question | Answer | Basis | Status |
|---|---|---|---|
| Structure | core `aaaav` (loop, principles, lifecycle playbooks); entries answering, investigating, inspecting, coding, writing, solid-loop, each with playbooks; capabilities grilling, domain-modeling, human-feedback | user 2026-10-21 | confirmed |
| Size discipline | no word budget; the goal is no verbosity, enforced by solid-loop's no-op test and deletion-first | user 2026-10-21 | confirmed |
| Names | core `aaaav`; `aaaav-do` becomes `coding`; agent-root routing line shrinks to "pick the entry skill whose description matches" | user 2026-10-21 | confirmed |
| Answering | `providing-knowledge` merges into `answering`; its show_doc/HTML presentation becomes an agent-root rule | user 2026-10-21 | confirmed |
| Jev | advisory second thought for the agent, never a block | user 2026-10-21 | confirmed |
| Architecture | pi first: programmatic loop parts ship as the `pi-aaaav` extension, published to npm | user 2026-10-21 | confirmed |
| Deleted skills | grill-me, grill-with-docs, boot-loop, assuring-quality, prototype, codebase-design; DEBUGGING.md and decision_log.py go too | tree report §3 | confirmed |
| Data sent to Jev | the latest user request and the final reply only, both truncated; no tool output, diffs, or files | Jev is a hosted API; the reply already carries the anchor evidence | grounded |
| Anchor gate scope | `write`/`edit` outside `scratch/`, `docs/specs/`, and temp dirs, with no `Reality anchor:` line in assistant text since the latest user message | AGENTS.md core directive, moved from prose to structure | grounded |
| Delivery | three ordered phases, one push and one npm publish at 1.0.0 after all verify | sequence verifiable units | grounded |

## Readiness

Core rules hold: English instructions, Traditional Chinese user communication, direct statement of expected behavior, anchor before the first production edit (now enforced by the extension). No open row blocks observable behavior.

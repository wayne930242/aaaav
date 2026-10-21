# Verification: aaaav 1.0

| Requirement | Evidence | Result |
|---|---|---|
| Three-layer tree: core, six entries with playbooks, three shared skills | `skills/` layout; `uv run python hooks/validate_all.py .` clean | pass |
| Align picks a playbook and copies its steps into `todo` past one increment | `skills/aaaav/SKILL.md` Align; reviewer round 1 found no contradiction between core, entries, and playbooks | pass |
| Merged skills leave no stale pointer outside `docs/specs/` in either repo | grep for the deleted names returns only credit footers; reviewer round 1 pointer check | pass |
| Rules dropped in the move are restored or allowed by the spec | reviewer round 1 listed nine P3 losses; each restored (feature, prototype, qa-release, coding Inline/approval/tasks.md, bug-fix premise and commit order, Reflexive silence) | pass |
| Validator follows links inside playbooks | `test_links_inside_linked_files` red before the change, green after | pass |
| weihung-agent-root follows the tree | `pi_steps`, `pi_resources`, `pi_configs`, `pi_packages`, `pi_fresh_machine`, `uninstall.sh`, all `.mjs` tests green; `install.sh` fails identically at HEAD `a8557d9` | pass |
| Anchor gate blocks `write`/`edit` without a `Reality anchor:` since the latest user message, exempting scratch, specs, and temp files outside the project | `tests/test_pi_aaaav.py` TestAnchorGate; live `pi -p` run blocked the first edit and passed the retry after the anchor | pass |
| `aaaav_decision` replaces `decision_log.py` | TestDecisionTool; live run wrote header and row | pass |
| Jev second thought: one advisory continuation on a concern, entry only on agreement, nothing without a key, only request and reply sent | TestSecondThought; three live runs each continued once and then settled | pass |
| Mutation check: reverting each P2 fix turns its test red | five tests red with the fixes reverted, green restored | pass |
| Independent review of Phase 2 | round 1: 3 P2 and 6 P3; round 2: all nine fixed, no new blocking bug | pass |
| `npm pack` ships only package files and the validator runs from the tarball | `npm pack --dry-run` 51 files; packed `validate_tool_use.py` returned suggestions | pass |
| Published to npm and installed by agent-root from `npm:pi-aaaav` | not yet run | unknown |

## Deviations

- The Phase 2 tests stub `ctx.modelRegistry` instead of an injected fetch, because pi's classifier registry owns the HTTP call.
- The gate does not see edits made through `bash`; the first live run edited with `printf >>` and was never gated. Recorded as a follow-up.
- Jev's `done` threshold of 0.5 sits on the scores of replies that carry evidence (0.32, 0.41, 0.46–0.53) while bare claims score 0.02–0.05; recorded as a follow-up.

## Friction Notes

- Tried: running the anchor-gate test with the project in a temp dir.
  Found: the temp-root exemption also exempted a project living under the temp dir, so the gate never fired.
  Led by: none (the spec's exemption list did not separate inside and outside the project).
- Tried: `git worktree remove --force` to clean a probe worktree.
  Found: the safety net blocks `--force`; a clean worktree removes without it.
  Led by: none.

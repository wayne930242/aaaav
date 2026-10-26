# Principles

Each entry: the name, when it applies, and the rule. Playbooks cite them by name, and the user steers with the same names.

## Core

- **Subtract before you add.** Sizing any change. Delete dead code, one-caller wrappers, redundant checks, and stale prose first; the smallest change that solves the problem ships.
- **Foundational thinking.** Before writing logic or integrating a new requirement. Choose the data shape and its organizing structure first, as if the requirement had been there from day one, so the code that follows is obvious.
- **Attack the premise.** Two fixes resting on one premise failed the same check. Write the premise as one sentence and test it directly before another fix.
- **Minimize reader load.** Shaping code or prose that is hard to trace. Count the layers between question and answer and the state a reader must hold; collapse what does not earn its place.
- **Build the lever.** Work you would repeat by hand. Write the script, codemod, or check that does or proves it; the tool is what a reviewer reruns.

## Architecture

- **Model the domain.** Logic that branches a lot or repeats a shape across files. Put the rule in one structure (state machine, table, typed model) instead of scattered conditionals.
- **Boundary discipline.** Wiring validation and errors. Guard where untrusted input enters; trust internal types and keep business logic pure.
- **Migrate callers, then delete.** Replacing an internal API. Move every caller and delete the old path in the same change; no compatibility layer outlives the move.

## Verification

- **Prove it works.** Before declaring done. Check the real artifact (run it, read the stored value), never a proxy, a self-report, or "it compiles".
- **Fix root causes.** Debugging. Fix where the system first went wrong; a guard counts as a fix only when the state it handles is legitimate.
- **Sequence verifiable units.** Multi-step work and commit order. Each unit ends in a check that passes before the next starts; the history reads as an argument, failing test before fix.
- **Test behavior, not implementation.** Writing or keeping a test. Assert what users of the code observe, so the test fails when behavior breaks and survives internal change.
- **Observe, don't ask.** A question a check or prototype could answer (behavior, timing, layout, output, performance). Run it; only product and preference calls go to the user.
- **Explain the number.** Trusting a measurement. Name what limits it and rule out that it measured something else before reporting it.

## Delegation

- **Never block on the human.** Reversible execution. Proceed and present the result; bring only irreversible actions and user-owned decisions to the user.

---

Adapted from the pstack principle skills by Lauren Tan (MIT License), revision `e44668c`.

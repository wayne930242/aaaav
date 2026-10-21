# Feature

**You own the design.**

1. Align: learn how the affected subsystem works now, and name the data shape and its organizing structure (**Model the domain**, **Foundational thinking**) before any logic.
2. Act: when the change crosses a module, settle its interface first. Place the seam at an existing boundary; add one only for real variation, because one adapter is hypothetical and two demonstrate variation. Hide invariants and ordering behind the interface, and make it the test surface. A module whose removal makes complexity vanish rather than move to callers is a pass-through; delete it. With no precedent and a costly-to-reverse choice, compare two interface shapes on depth, locality, compatibility, and testability, or settle it with the `prototype` playbook; a user-owned trade-off goes to the user.
3. Act: for more than one unit, write the throughput checkpoint as four `todo` items, each `n/a: <reason>` when it does not apply: blocking first steps; independent workstreams; shared mutable state, split before serializing; the smallest safe decomposition.
4. Act: build in units that each end in a check (**Sequence verifiable units**).
5. Verify: on the surface the user will use; an inconclusive or wrong-surface result is not a pass.

**Reply:** what was built, the shape chosen and why, the checkpoint, and open decisions; a table when alternatives were compared.

---

Interface checks adapted from [mattpocock/skills](https://github.com/mattpocock/skills) `codebase-design` (MIT License, Copyright (c) 2026 Matt Pocock).

# Prototype

**You own the decision, not the code.** The prototype is a throwaway instrument; the real build follows `feature`.

1. Align: write the one question the prototype answers, the observation that settles it, and who owns the verdict. Choose a prototype only when running an experiment is cheaper or clearer than deciding from existing evidence.
2. Act: build the smallest experiment in the project's native runtime, near its subject and visibly marked as a prototype, with ephemeral state unless persistence is the question. Implement only what observing the answer needs, and expose the state it depends on. Alternatives sit behind one switch, each labeled.
3. Verify: observe the thing being decided (output, timing, a screenshot of each variant). When the remaining verdict is suitability, the human anchor's reviewer judges it.
4. Record the question, environment, evidence, verdict, and decision in `design.md`, or in the reply when there is none. Delete the prototype afterward unless the user or project keeps it; it is committed only when the delivery workflow authorizes it.

**Reply:** the variants, the evidence, the trade-offs, a recommendation, and the scratch path, stated as throwaway.

---

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) `prototype` (MIT License, Copyright (c) 2026 Matt Pocock).

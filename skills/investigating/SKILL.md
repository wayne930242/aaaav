---
name: investigating
description: Use when researching questions, diagnosing root causes, or gathering evidence.
---

# Investigating

1. Define the exact question and completion boundary.
2. Gather relevant evidence:
   - code: use LSP (`read_symbol`) for symbols and ast-grep for structure; use text
     search for prose, configuration, and literals; check history when behavior changed over time
   - external facts: current primary sources, official documentation, source
     code, specifications, or first-party APIs
   - runtime: reproducible commands, logs, errors, and test output
3. Cross-check material claims and resolve source conflicts.
4. Grade each material claim by its strongest evidence: asserted, cited
   (`file:line` or primary source), reasoned (the failure path walked and shown
   not to reach), executed (a script or test against the real code), or
   reproduced (observed in the running system). A claim with no evidence is
   `unknown`.
5. Report the reasoning chain with each material claim's source and grade beside it.

When another workflow supplies an artifact path, return evidence in the shape
that phase needs. Do not create a parallel plan or specification.

**Complete when:** the scoped question is answered or the missing evidence is
named precisely.

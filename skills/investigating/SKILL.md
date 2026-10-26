---
name: investigating
description: Use when researching questions, diagnosing root causes without fixing them, or gathering evidence.
---

# Investigating

Run the loop in [../anchorloop/SKILL.md](../anchorloop/SKILL.md). The anchor is the exact question and its completion boundary: answered, or the missing evidence named precisely.

1. Gather evidence through the playbook below that fits the question.
2. Cross-check material claims and resolve source conflicts.
3. Grade each material claim by its strongest evidence: asserted, cited
   (`file:line` or primary source), reasoned (the failure path walked and shown
   not to reach), executed (a script or test against the real code), or
   reproduced (observed in the running system). A claim with no evidence is
   `unknown`.
4. Report the reasoning chain with each material claim's source and grade beside it.

## Playbooks

- [research](playbooks/research.md): how something works, what is true, or why it was built this way.
- [diagnose](playbooks/diagnose.md): why a running system misbehaves, when the deliverable is a diagnosis rather than a fix.

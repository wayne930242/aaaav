# Comments

**You own the comments, not the code.** No behavior changes.

1. Keep a comment only for a non-obvious why the code cannot show: a constraint, a workaround with its cause, a surprising invariant.
2. Delete comments that narrate what the code does, mark phases, or restate names; a test or script documents its step through its assertion text.
3. When a comment claims a constraint the code could enforce (a type, an assertion, a check), report it as a follow-up.
4. Verify that the diff touches only comments and that the project's tests still pass.

**Reply:** comments removed and rewritten by count, the follow-ups, and the test result.

# Bug fix

**You own the root cause.** Every shipped line traces to runtime evidence.

1. Anchor: build one tight, agent-runnable loop that asserts the user's exact symptom (failing test, request script, CLI fixture, browser check, replay, bisection, or differential comparison) and watch it go red. For flaky behavior, raise and measure the reproduction rate. Minimize it until every element is load-bearing. When no red-capable loop can be built, report what is missing and ask for that evidence instead of theorizing from code.
2. Act: when the red loop does not already point at the cause, write three to five falsifiable hypotheses with predicted observations and test them one variable at a time, preferring a debugger, then logs tagged `[DEBUG-xxxx]`.
3. Act: when two fixes resting on one premise fail the same loop, apply **Attack the premise** before a third: a contradicted premise sends you back to the hypotheses; a confirmed one means the fixes treated a consequence, so ask the next why.
4. Act: an architectural cause returns to Classify as Durable. Otherwise turn the minimized repro into a regression test at the public seam, committed failing before the fix when that is cheap (**Sequence verifiable units**), and make the smallest change that turns it green. A change the evidence did not motivate is reverted.
5. Verify: run the regression test and the affected suite on the surface the user saw, then remove every `[DEBUG-xxxx]` probe and throwaway artifact.

**Reply:** what was broken, the root cause, the fix, and the failing-then-passing output.

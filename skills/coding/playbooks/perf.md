# Perf

**You own the number.**

1. Anchor: measure a baseline on the real workload, repeated, with its range.
2. Act: **Explain the number**: find what limits it and rule out a warm cache, a skipped path, or a debug build before trusting it. Profile before changing code.
3. Act: one change at a time against the baseline; keep a change only when its gain sits outside the noise, and revert the rest.
4. Verify: rerun the baseline workload under the same conditions.

**Reply:** faster, slower, no measurable difference, or inconclusive, with run counts, ranges, what limits the number, and the profile that pointed at the change.

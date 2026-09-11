# Reporting Standards

All skills and verification steps must provide standardized, verifiable reporting.

## Verification Table Format

Present every verification result in a standard three-column table:

| Requirement | Evidence | Result |
|---|---|---|
| Observable behavior or contract from spec | Real interface executed and the specific output observed | pass / fail / unknown |

### Result Criteria

- **pass**: The chosen reality anchor ran against the actual implementation and directly observed the expected behavior.
- **fail**: The anchor executed and observed a deviation from the contract or an error.
- **unknown**: The requirement was not directly exercised by an anchor in this run. A green test suite or passing unrelated check does not count as evidence for an unexercised requirement.

## Distinct Verification Claims

Maintain clear boundaries between verification claims:
- Local automated test runs (e.g., `pytest`, `npm test`)
- Build and compilation checks
- Interactive or CLI execution evidence
- Browser / UI rendered inspection
- Deployment or release status

Never conflate a local passing test with end-to-end integration or live deployment verification.

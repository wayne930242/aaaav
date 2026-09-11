# Defensive Patterns vs. Expected Behavior

Replace defensive prohibitions, endless red lines, and negative framing with concise, positive statements of expected behavior.

## The Negation Anti-Pattern

Negative steering ("do not think of an elephant") brings the forbidden concept into context, increasing the likelihood that the model acts on it. State the positive target behavior directly so the prohibited pattern is never primed.

## Pattern Comparison

| Defensive Anti-Pattern (Avoid) | Direct Expected Behavior (Use) | Rationale |
|---|---|---|
| "You must NEVER under any circumstances edit files without asking." | "State the contract and authorization before editing production code." | Clear operational trigger instead of fear-based prohibition. |
| "STRICT RED LINE: Do not make any assumptions or guess anything." | "Resolve uncertainty from project sources; ask only for genuine user-owned decisions." | Actionable hierarchy of resolution rather than paralysis. |
| "Under no condition should you ever write complex code or add extra features." | "Implement the smallest solution that satisfies the contract. Avoid unsolicited features." | States the design objective positively. |
| "Absolute zero tolerance for broken links or untested code." | "Verify every local markdown link and run relevant test suites before completion." | Clear, verifiable task instead of emotional rhetoric. |
| "Do not hallucinate facts or pretend to understand." | "Ground claims in observed evidence from project files or reality anchors." | Positive epistemology based on evidence. |

## Key Principle

Prompts and agent instructions must directly state expected outcomes and operational boundaries. Strong models execute effectively when given clear intent, reality anchors, and observable completion criteria.

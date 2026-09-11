"""Constants for skill, rule, and durable spec validation."""

# Allowed fields in SKILL.md YAML frontmatter
SKILL_ALLOWED_FIELDS = frozenset({"name", "description"})

# Maximum recommended lines for a streamlined SKILL.md before progressive disclosure to references/
SKILL_MAX_RECOMMENDED_LINES = 120

# Defensive phrasing patterns to discourage (encourage stating expected behavior directly)
DEFENSIVE_PATTERNS = [
    r"never under any circumstances",
    r"under no circumstances",
    r"you must never ever",
    r"do not under any condition",
    r"strict red line",
    r"absolute red line",
    r"prohibited at all costs",
    r"zero tolerance for any",
    r"absolutely forbidden to ever",
    r"無限多的紅線",
    r"千萬不要",
    r"嚴禁在任何情況下",
    r"絕對不可",
]

# Essential core rules to check during durable pre-flight
CORE_RULES = [
    "Traditional Chinese communication",
    "English instructions and prompts",
    "Direct statement of expected behavior without defensive phrasing",
    "AAAAV reality anchor named before first production edit",
]

# Standard verification result states
VALID_VERIFICATION_RESULTS = {"pass", "fail", "unknown"}

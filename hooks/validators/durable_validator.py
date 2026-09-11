"""Validator for Durable artifacts and reviews in docs/specs/*/."""

import re
from pathlib import Path
from .constants import DEFENSIVE_PATTERNS, VALID_VERIFICATION_RESULTS
from .utils import find_defensive_phrases


def check_decision_md(path: Path) -> list[str]:
    """Check decision.md for required structure and pre-flight skill/rule readiness."""
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")

    # Check for decision table
    if not re.search(r"\|\s*Question\s*\|\s*Answer\s*\|\s*Basis\s*\|\s*Status\s*\|", text, re.IGNORECASE):
        warnings.append("decision.md should include a Question | Answer | Basis | Status table.")

    # Check for pre-flight prerequisite readiness (skills and core rules)
    lower = text.lower()
    if "prerequisite" not in lower and "skill" not in lower and "rule" not in lower and "readiness" not in lower:
        warnings.append(
            "check and supply missing core rules or crucial skills before starting work; "
            "note skill readiness in decision.md."
        )

    return warnings


def check_spec_md(path: Path) -> list[str]:
    """Check spec.md for approval status and reality anchor definition."""
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")

    # Status header
    if not re.search(r"Status:\s*(proposed|approved)", text, re.IGNORECASE):
        warnings.append("spec.md must declare 'Status: proposed' or 'Status: approved' at the top.")

    # Reality anchor declaration
    if "reality anchor" not in text.lower() and "anchor" not in text.lower():
        warnings.append("spec.md should name the chosen reality anchor and its checkpoint.")

    return warnings


def check_verification_md(path: Path) -> list[str]:
    """Check verification.md for standard evidence rows and adjustment-focused reviews."""
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")

    # 1. Standard Requirement | Evidence | Result table
    table_match = re.search(r"\|\s*Requirement\s*\|\s*Evidence\s*\|\s*Result\s*\|", text, re.IGNORECASE)
    if not table_match:
        warnings.append(
            "verification.md must include a 'Requirement | Evidence | Result' table."
        )
    else:
        # Check that results use valid states (excluding the table header)
        result_rows = re.findall(r"\|\s*[^|]+\s*\|\s*[^|]+\s*\|\s*([a-zA-Z]+)\s*\|", text)
        invalid_results = [
            r.lower() for r in result_rows 
            if r.lower() not in VALID_VERIFICATION_RESULTS and r.lower() != "result"
        ]
        if invalid_results:
            warnings.append(
                f"invalid verification Result values found: {', '.join(set(invalid_results))}. "
                "Result must be one of: pass, fail, unknown."
            )

    # 2. Review of newly added rules or skills (tuning vs defensive vocabulary)
    found_defensive = find_defensive_phrases(text, DEFENSIVE_PATTERNS)
    if found_defensive:
        warnings.append(
            f"detected defensive wording in verification/review: {', '.join(found_defensive)}. "
            "Reviews of new rules and skills must focus on adjustment and tuning, not adding defensive red lines."
        )

    return warnings


def check_durable_spec(path: Path) -> list[str]:
    """Route durable spec file to specific validator."""
    name = path.name.lower()
    if name == "decision.md" or name == "requirements.md":
        return check_decision_md(path)
    elif name == "spec.md":
        return check_spec_md(path)
    elif name == "verification.md":
        return check_verification_md(path)
    return []

"""Validator for SKILL.md files focusing on compactness and direct expected behavior."""

from pathlib import Path
from .constants import (
    SKILL_ALLOWED_FIELDS,
    SKILL_MAX_RECOMMENDED_LINES,
    DEFENSIVE_PATTERNS,
)
from .utils import (
    parse_frontmatter,
    extract_markdown_links,
    find_defensive_phrases,
)


def check_skill_md(path: Path) -> list[str]:
    """Run streamlining and standardization checks on a SKILL.md file."""
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"failed to read SKILL.md: {e}"]

    skill_dir = path.parent
    lines = text.splitlines()

    # 1. Frontmatter check
    fields = parse_frontmatter(text)
    if fields is None:
        warnings.append("missing or invalid YAML frontmatter (--- ... ---)")
    else:
        extra_fields = sorted(set(fields.keys()) - SKILL_ALLOWED_FIELDS)
        if extra_fields:
            warnings.append(f"extra frontmatter fields: {', '.join(extra_fields)}")

        if "name" not in fields or not fields["name"].strip():
            warnings.append("missing required frontmatter field: 'name'")

        if "description" not in fields or not fields["description"].strip():
            warnings.append("missing required frontmatter field: 'description'")
        else:
            desc = fields["description"]
            if "use when" not in desc.lower():
                warnings.append("description should specify trigger criteria (include 'Use when...')")

    # 2. Compactness check (streamlined skills)
    if len(lines) > SKILL_MAX_RECOMMENDED_LINES:
        has_references = (skill_dir / "references").is_dir()
        if not has_references:
            warnings.append(
                f"skill has {len(lines)} lines (exceeds recommended {SKILL_MAX_RECOMMENDED_LINES}). "
                "Move detailed guidelines or templates to references/ to keep SKILL.md streamlined."
            )

    # 3. Broken markdown links
    local_links = extract_markdown_links(text)
    for link in local_links:
        target = (skill_dir / link).resolve()
        if not target.exists():
            warnings.append(f"broken local link: {link}")

    # 4. Orphaned files check
    linked_normalized = {str(Path(l)).replace("\\", "/") for l in local_links}
    for f in skill_dir.rglob("*"):
        if f == path or f.is_dir():
            continue
        rel = str(f.relative_to(skill_dir)).replace("\\", "/")
        in_link = rel in linked_normalized
        in_text = rel in text or f.name in text
        if not (in_link or in_text):
            warnings.append(f"orphaned file not referenced in SKILL.md: {rel}")

    # 5. Defensive phrasing check
    found_patterns = find_defensive_phrases(text, DEFENSIVE_PATTERNS)
    if found_patterns:
        warnings.append(
            f"detected defensive anti-pattern(s): {', '.join(found_patterns)}. "
            "State expected behavior directly rather than constructing defensive red lines."
        )

    return warnings

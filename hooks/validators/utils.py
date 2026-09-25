"""Utility functions for validators."""

import re
from pathlib import Path


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Parse YAML frontmatter from markdown text using regex."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end].strip()
    result: dict[str, str] = {}
    current_key = None
    current_val: list[str] = []

    for line in block.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        # Check for top-level key: value
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match and not line.startswith(" "):
            if current_key is not None:
                result[current_key] = "\n".join(current_val).strip().strip("\"'")
            current_key = match.group(1)
            raw_val = match.group(2).strip()
            current_val = [raw_val] if raw_val else []
        elif current_key is not None:
            current_val.append(line.strip())

    if current_key is not None:
        result[current_key] = "\n".join(current_val).strip().strip("\"'")

    return result


def extract_markdown_links(text: str) -> list[str]:
    """Extract local markdown link targets [label](target)."""
    # Strip inline code and fenced code blocks
    stripped = re.sub(r"```[\s\S]*?```", "", text)
    stripped = re.sub(r"`[^`\n]+`", "", stripped)
    # Match markdown links: [label](target)
    matches = re.findall(r"\[(?:[^\]]*)\]\(([^)#\s]+)(?:#[^)]*)?\)", stripped)
    # Filter out web URLs, mailto, etc.
    local_links = [m for m in matches if not re.match(r"^[a-zA-Z]+://", m) and not m.startswith("mailto:")]
    return local_links


def find_defensive_phrases(text: str, patterns: list[str]) -> list[str]:
    """Find defensive phrasing anti-patterns outside code blocks."""
    stripped = re.sub(r"```[\s\S]*?```", "", text)
    stripped = re.sub(r"`[^`\n]+`", "", stripped)
    found: list[str] = []
    for pattern in patterns:
        if re.search(pattern, stripped, re.IGNORECASE):
            found.append(pattern)
    return found


def extract_file_path_from_payload(payload: dict) -> str | None:
    """Extract the edited file path from the pi extension payload's tool_input.file_path."""
    tool_input = payload.get("tool_input", {})
    if isinstance(tool_input, dict) and tool_input.get("file_path"):
        return str(tool_input["file_path"])
    return None

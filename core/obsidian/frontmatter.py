"""Parse YAML frontmatter trong Obsidian markdown."""
from __future__ import annotations
import re
import yaml

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)


def parse(content: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_str)."""
    # Normalize CRLF → LF (Obsidian on Windows writes CRLF)
    content = content.replace("\r\n", "\n")
    m = FRONTMATTER_RE.match(content)
    if not m:
        return {}, content
    fm_yaml, body = m.groups()
    try:
        return yaml.safe_load(fm_yaml) or {}, body
    except yaml.YAMLError as e:
        raise ValueError(f"Malformed YAML frontmatter: {e}") from e

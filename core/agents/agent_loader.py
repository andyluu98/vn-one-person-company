"""Load agent definition từ .md file (YAML frontmatter + system prompt body)."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from core.obsidian.frontmatter import parse as parse_frontmatter


@dataclass
class AgentDefinition:
    id: str
    name_vn: str
    department: str
    system_prompt: str
    name_en: Optional[str] = None
    seniority: str = "mid"
    emoji: str = ""
    expertise: list[str] = field(default_factory=list)
    required_refs: list[str] = field(default_factory=list)
    required_tools: list[str] = field(default_factory=list)
    optional_tools: list[str] = field(default_factory=list)
    deliverables: list[str] = field(default_factory=list)
    model_override: Optional[str] = None
    temperature: float = 0.7


class AgentLoader:
    def load(self, path: Path) -> AgentDefinition:
        content = Path(path).read_text(encoding="utf-8")
        fm, body = parse_frontmatter(content)

        if not fm.get("id"):
            raise ValueError(f"Agent missing 'id' field: {path}")

        llm_override = fm.get("llm_override", {}) or {}

        return AgentDefinition(
            id=fm["id"],
            name_vn=fm.get("name_vn", fm["id"]),
            name_en=fm.get("name_en"),
            department=fm.get("department", ""),
            seniority=fm.get("seniority", "mid"),
            emoji=fm.get("emoji", ""),
            expertise=fm.get("expertise", []),
            required_refs=fm.get("required_refs", []),
            required_tools=fm.get("required_tools", []),
            optional_tools=fm.get("optional_tools", []),
            deliverables=fm.get("deliverables", []),
            model_override=llm_override.get("model") or fm.get("model_override"),
            temperature=float(llm_override.get("temperature", fm.get("temperature", 0.7))),
            system_prompt=body.strip(),
        )

"""Department model + loader."""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field


class DebateRole(BaseModel):
    default: str = "pro"
    override: dict[str, str] = Field(default_factory=dict)


class RoutingRule(BaseModel):
    keywords: list[str]
    agent: str


class Department(BaseModel):
    code: str
    name_vn: str
    name_en: Optional[str] = None
    tier: int
    description: str = ""
    agents: list[str] = Field(default_factory=list)
    default_speaker: str = ""
    routing_rules: list[RoutingRule] = Field(default_factory=list)
    refs_folder: str = "refs/"
    depends_on: list[str] = Field(default_factory=list)
    debate_role: DebateRole = Field(default_factory=DebateRole)


class DepartmentLoader:
    def __init__(self, departments_root: Path):
        self.root = Path(departments_root)

    def load(self, code: str) -> Department:
        path = self.root / code / "department.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Department not found: {code}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return Department(**data)

    def load_all(self) -> list[Department]:
        out = []
        for child in sorted(self.root.iterdir()):
            if child.is_dir() and child.name.startswith(("0", "1")) and (child / "department.yaml").exists():
                out.append(self.load(child.name))
        return out

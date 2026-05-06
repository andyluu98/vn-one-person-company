"""Central registry: load 13 dept + agents từ /departments + /packs."""
from __future__ import annotations
from pathlib import Path
from core.agents.department import Department, DepartmentLoader
from core.agents.agent_loader import AgentLoader, AgentDefinition


class DepartmentWithAgents:
    """Department + loaded AgentDefinition objects."""

    def __init__(self, dept: Department, agents: list[AgentDefinition]):
        self.dept = dept
        self.agents_by_id: dict[str, AgentDefinition] = {a.id: a for a in agents}

    @property
    def code(self) -> str:
        return self.dept.code

    @property
    def name_vn(self) -> str:
        return self.dept.name_vn

    def get_agent(self, agent_id: str) -> AgentDefinition:
        if agent_id not in self.agents_by_id:
            raise KeyError(f"Agent {agent_id} not in {self.code}")
        return self.agents_by_id[agent_id]

    def select_agent_for_brief(self, brief: str) -> AgentDefinition:
        """Use routing_rules để chọn agent phù hợp với brief."""
        brief_lower = brief.lower()
        for rule in self.dept.routing_rules:
            if any(kw.lower() in brief_lower for kw in rule.keywords):
                if rule.agent in self.agents_by_id:
                    return self.agents_by_id[rule.agent]
        if self.dept.default_speaker and self.dept.default_speaker in self.agents_by_id:
            return self.agents_by_id[self.dept.default_speaker]
        if self.agents_by_id:
            return next(iter(self.agents_by_id.values()))
        raise KeyError(f"Department {self.code} has no agents")


class Registry:
    def __init__(self, departments_root: Path, packs_root: Path | None = None):
        self.dept_loader = DepartmentLoader(departments_root)
        self.agent_loader = AgentLoader()
        self.depts_root = Path(departments_root)
        self.packs_root = Path(packs_root) if packs_root else None
        self._cache: dict[str, DepartmentWithAgents] = {}

    def get(self, dept_code: str) -> DepartmentWithAgents:
        if dept_code in self._cache:
            return self._cache[dept_code]

        dept = self.dept_loader.load(dept_code)
        agents = self._load_agents_for(dept)
        result = DepartmentWithAgents(dept, agents)
        self._cache[dept_code] = result
        return result

    def _load_agents_for(self, dept: Department) -> list[AgentDefinition]:
        agents_dir = self.depts_root / dept.code / "agents"
        if not agents_dir.exists():
            return []
        result = []
        for agent_id in dept.agents:
            agent_path = agents_dir / f"{agent_id}.md"
            if agent_path.exists():
                result.append(self.agent_loader.load(agent_path))
        return result

    def list_active(self, codes: list[str]) -> list[DepartmentWithAgents]:
        return [self.get(c) for c in codes]

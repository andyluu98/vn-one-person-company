from pathlib import Path
import pytest
from core.agents.registry import Registry


def test_registry_loads_dept_with_agents(tmp_path):
    (tmp_path / "07-marketing" / "agents").mkdir(parents=True)
    (tmp_path / "07-marketing" / "department.yaml").write_text(
        "code: '07-marketing'\nname_vn: MKT\ntier: 3\nagents: [test-agent]\ndefault_speaker: test-agent\n",
        encoding="utf-8",
    )
    (tmp_path / "07-marketing" / "agents" / "test-agent.md").write_text(
        "---\nid: test-agent\nname_vn: Test\ndepartment: 07-marketing\n---\n# Test\n",
        encoding="utf-8",
    )

    reg = Registry(tmp_path)
    dept = reg.get("07-marketing")
    assert dept.code == "07-marketing"
    assert "test-agent" in dept.agents_by_id
    assert dept.select_agent_for_brief("anything").id == "test-agent"

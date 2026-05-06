"""Test PerspectivesCollector - round 1 of meeting (parallel dept perspectives)."""
from unittest.mock import MagicMock
from pathlib import Path
from core.orchestrator.perspectives_collector import PerspectivesCollector
from core.meeting.debate_state import new_meeting_state


def test_collector_loads_dept_and_calls_agent():
    """Collector cho moi dept -> load default speaker -> call LLM."""
    llm = MagicMock(complete=MagicMock(return_value="Phong X noi: ABC"))

    repo = Path(__file__).parent.parent.parent
    collector = PerspectivesCollector(
        departments_root=repo / "departments",
        llm=llm,
    )

    state = new_meeting_state(
        brief="test", departments=["07-marketing"],
    )
    out = collector.collect(state)

    assert "07-marketing" in out["perspectives"]
    assert "ABC" in out["perspectives"]["07-marketing"]

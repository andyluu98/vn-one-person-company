"""Unit tests cho Growth/Cautious/Balanced perspective debators."""
from unittest.mock import MagicMock

from core.agents.perspective_debators import (
    BalancedDebator,
    CautiousDebator,
    GrowthDebator,
)
from core.meeting.debate_state import new_meeting_state


def test_growth_debator_appends_to_history():
    llm = MagicMock(complete=MagicMock(return_value="GO bold"))
    g = GrowthDebator(llm=llm)
    state = new_meeting_state(brief="x", departments=[])
    state["pro_con_debate"]["history"] = ["PRO: ...", "CON: ..."]
    out = g.run(state)
    assert "GO" in out["perspective_debate"]["growth_history"][-1]


def test_cautious_debator_speaks_after_growth():
    llm = MagicMock(complete=MagicMock(return_value="Hold gates first"))
    c = CautiousDebator(llm=llm)
    state = new_meeting_state(brief="x", departments=[])
    state["perspective_debate"]["growth_history"] = ["GO bold"]
    out = c.run(state)
    assert "Hold" in out["perspective_debate"]["cautious_history"][-1]


def test_balanced_debator_synthesizes():
    llm = MagicMock(complete=MagicMock(return_value="Pilot 4 weeks"))
    b = BalancedDebator(llm=llm)
    state = new_meeting_state(brief="x", departments=[])
    state["perspective_debate"]["growth_history"] = ["GO bold"]
    state["perspective_debate"]["cautious_history"] = ["Hold"]
    out = b.run(state)
    assert "Pilot" in out["perspective_debate"]["balanced_history"][-1]
    assert out["perspective_debate"]["count"] == 1

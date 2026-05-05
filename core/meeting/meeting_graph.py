"""LangGraph orchestrator — toàn bộ meeting flow.

Adapted from TradingAgents/graph/trading_graph.py với neutral naming.

Flow:
  perspectives → pro_con_loop → perspective_loop → synthesizer → END
"""
from __future__ import annotations
from typing import Callable
from langgraph.graph import StateGraph, END
from core.meeting.debate_state import MeetingState
from core.meeting.conditional_logic import next_pro_con_node, next_perspective_node
from core.meeting.synthesizer import Synthesizer
from core.meeting.checkpointer import make_checkpointer
from core.agents.pro_advocate import ProAdvocate
from core.agents.con_advocate import ConAdvocate
from core.agents.perspective_debators import (
    GrowthDebator, CautiousDebator, BalancedDebator,
)


class MeetingGraph:
    """Build + run LangGraph meeting flow."""

    def __init__(
        self,
        llm,
        perspectives_collector: Callable[[MeetingState], dict],
        checkpointer=None,
    ):
        """
        perspectives_collector: function nhận state, trả {"perspectives": {...}}.
        Sẽ implement Phase 3 từ DepartmentLoader.
        checkpointer: optional. If None, uses default SQLite checkpointer.
                      Pass False to disable checkpointing (useful for tests).
        """
        self.llm = llm
        self.perspectives_collector = perspectives_collector
        self.checkpointer = checkpointer
        self.pro = ProAdvocate(llm)
        self.con = ConAdvocate(llm)
        self.growth = GrowthDebator(llm)
        self.cautious = CautiousDebator(llm)
        self.balanced = BalancedDebator(llm)
        self.synthesizer = Synthesizer(llm)

    def build(self):
        graph = StateGraph(MeetingState)

        graph.add_node("perspectives", self.perspectives_collector)
        graph.add_node("pro", self.pro.run)
        graph.add_node("con", self.con.run)
        graph.add_node("growth", self.growth.run)
        graph.add_node("cautious", self.cautious.run)
        graph.add_node("balanced", self.balanced.run)
        graph.add_node("synthesizer", self.synthesizer.run)

        graph.set_entry_point("perspectives")
        graph.add_edge("perspectives", "pro")

        graph.add_conditional_edges("pro", next_pro_con_node, {
            "con": "con", "perspective_phase": "growth", "pro": "pro",
        })
        graph.add_conditional_edges("con", next_pro_con_node, {
            "pro": "pro", "perspective_phase": "growth", "con": "con",
        })
        graph.add_conditional_edges("growth", next_perspective_node, {
            "cautious": "cautious", "synthesizer": "synthesizer",
        })
        graph.add_conditional_edges("cautious", next_perspective_node, {
            "balanced": "balanced", "synthesizer": "synthesizer",
        })
        graph.add_conditional_edges("balanced", next_perspective_node, {
            "growth": "growth", "synthesizer": "synthesizer",
        })
        graph.add_edge("synthesizer", END)

        # checkpointer logic:
        #   None  → use default SQLite saver
        #   False → no checkpointer
        #   else  → use the provided one
        if self.checkpointer is False:
            return graph.compile()
        cp = self.checkpointer if self.checkpointer is not None else make_checkpointer()
        return graph.compile(checkpointer=cp)

    def invoke(self, state: MeetingState, config: dict | None = None) -> MeetingState:
        cfg = config or {"configurable": {"thread_id": state.get("task_id", "default")}}
        return self.build().invoke(state, config=cfg)

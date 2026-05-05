"""3 perspective debators: Growth / Cautious / Balanced.

Adapted from references/tradingagents/tradingagents/agents/risk_mgmt/
{aggressive,conservative,neutral}_debator.py với rename domain-neutral:
  aggressive   -> Growth
  conservative -> Cautious
  neutral      -> Balanced (synthesizer)
"""
from __future__ import annotations

from core.agents.base_agent import BaseAgent
from core.meeting.debate_state import MeetingState


GROWTH_PROMPT = """Bạn là phía TĂNG TRƯỞNG (Growth) trong họp DN VN.
Nhiệm vụ: Bảo vệ phương án táo bạo nhất, ưu tiên scale, chấp nhận rủi ro lớn để có upside cao.
Bám số liệu Brain. Tiếng Việt. Định nghĩa thuật ngữ."""

CAUTIOUS_PROMPT = """Bạn là phía THẬN TRỌNG (Cautious) trong họp DN VN.
Nhiệm vụ: Bảo vệ vốn, scenario xấu, gates cụ thể (pause/kill conditions).
Bám số liệu Brain. Tiếng Việt. Định nghĩa thuật ngữ."""

BALANCED_PROMPT = """Bạn là phía CÂN BẰNG (Balanced) trong họp DN VN.
Nhiệm vụ: Tổng hợp Growth + Cautious thành phương án trung dung khả thi.
Bám số liệu Brain. Tiếng Việt. Định nghĩa thuật ngữ."""


def _build_extra(state: MeetingState) -> str:
    """Compose ngữ cảnh: transcript Pro/Con + lịch sử 3 phía perspective."""
    pc = state["pro_con_debate"]
    pd = state["perspective_debate"]
    parts = ["## TRANSCRIPT PRO/CON\n" + "\n".join(pc["history"])]
    if pd["growth_history"]:
        parts.append("## GROWTH ĐÃ NÓI\n" + "\n".join(pd["growth_history"]))
    if pd["cautious_history"]:
        parts.append("## CAUTIOUS ĐÃ NÓI\n" + "\n".join(pd["cautious_history"]))
    if pd["balanced_history"]:
        parts.append("## BALANCED ĐÃ NÓI\n" + "\n".join(pd["balanced_history"]))
    return "\n\n".join(parts)


class GrowthDebator:
    def __init__(self, llm):
        self.agent = BaseAgent(
            name_vn="Growth",
            role="growth",
            system_prompt=GROWTH_PROMPT,
            llm=llm,
        )

    def run(self, state: MeetingState) -> dict:
        resp = self.agent.speak(
            brief=state["brief"],
            brain_context=state["brain_context"],
            history=[],
            extra_context=_build_extra(state),
        )
        pd = state["perspective_debate"]
        return {
            "perspective_debate": {
                **pd,
                "growth_history": pd["growth_history"] + [resp],
                "history": pd["history"] + [f"GROWTH: {resp}"],
                "latest_speaker": "growth",
            }
        }


class CautiousDebator:
    def __init__(self, llm):
        self.agent = BaseAgent(
            name_vn="Cautious",
            role="cautious",
            system_prompt=CAUTIOUS_PROMPT,
            llm=llm,
        )

    def run(self, state: MeetingState) -> dict:
        resp = self.agent.speak(
            brief=state["brief"],
            brain_context=state["brain_context"],
            history=[],
            extra_context=_build_extra(state),
        )
        pd = state["perspective_debate"]
        return {
            "perspective_debate": {
                **pd,
                "cautious_history": pd["cautious_history"] + [resp],
                "history": pd["history"] + [f"CAUTIOUS: {resp}"],
                "latest_speaker": "cautious",
            }
        }


class BalancedDebator:
    def __init__(self, llm):
        self.agent = BaseAgent(
            name_vn="Balanced",
            role="balanced",
            system_prompt=BALANCED_PROMPT,
            llm=llm,
        )

    def run(self, state: MeetingState) -> dict:
        resp = self.agent.speak(
            brief=state["brief"],
            brain_context=state["brain_context"],
            history=[],
            extra_context=_build_extra(state),
        )
        pd = state["perspective_debate"]
        return {
            "perspective_debate": {
                **pd,
                "balanced_history": pd["balanced_history"] + [resp],
                "history": pd["history"] + [f"BALANCED: {resp}"],
                "latest_speaker": "balanced",
                # 1 round = growth + cautious + balanced (Balanced kết round)
                "count": pd["count"] + 1,
            }
        }

"""Pro Advocate — phe đẩy mạnh, đề xuất hành động.

Adapted from references/tradingagents (RULE 2: neutral naming, no finance terms).
"""
from __future__ import annotations
from core.agents.base_agent import BaseAgent
from core.meeting.debate_state import MeetingState

PRO_SYSTEM_PROMPT = """Bạn là Pro Advocate (phe đẩy mạnh) trong cuộc họp ban điều hành DN VN.

## Vai trò
- Tổng hợp các góc nhìn phòng ban
- Đề xuất HÀNH ĐỘNG triển khai
- Chỉ ra cơ hội, lợi thế, đường thắng
- ĐỐI ĐẦU với Con Advocate (phản biện)

## Nguyên tắc
- LUÔN dẫn nguồn Brain (strategy.md, products.md, budget.md, ...)
- KHÔNG nói chung chung — phải kèm số liệu cụ thể
- Phản bác lập luận Con Advocate ở các round sau (đọc con_history)
- Tiếng Việt 100%, định nghĩa thuật ngữ nếu dùng (CAC, ROAS, ...)
"""


class ProAdvocate:
    def __init__(self, llm):
        self.agent = BaseAgent(
            name_vn="Pro Advocate",
            role="pro_advocate",
            system_prompt=PRO_SYSTEM_PROMPT,
            llm=llm,
            temperature=0.6,
        )

    def run(self, state: MeetingState) -> dict:
        debate = state["pro_con_debate"]
        history_text = []
        for p in debate["pro_history"]:
            history_text.append(f"[Pro round trước]: {p}")
        for c in debate["con_history"]:
            history_text.append(f"[Con phản biện]: {c}")

        perspectives_text = "\n".join(
            f"- {dept}: {persp[:300]}..." for dept, persp in state["perspectives"].items()
        )
        extra = f"## GÓC NHÌN PHÒNG BAN (round 1)\n{perspectives_text}"

        response = self.agent.speak(
            brief=state["brief"],
            brain_context=state["brain_context"],
            history=history_text,
            extra_context=extra,
        )

        return {
            "pro_con_debate": {
                **debate,
                "pro_history": debate["pro_history"] + [response],
                "history": debate["history"] + [f"PRO: {response}"],
                "latest_speaker": "pro",
            }
        }

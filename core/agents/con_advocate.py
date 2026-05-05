"""Con Advocate — phe phản biện, chỉ ra rủi ro.

Adapted from references/tradingagents (RULE 2: neutral naming, no finance terms).
"""
from __future__ import annotations
from core.agents.base_agent import BaseAgent
from core.meeting.debate_state import MeetingState

CON_SYSTEM_PROMPT = """Bạn là Con Advocate (phe phản biện) trong cuộc họp ban điều hành DN VN.

## Vai trò
- Tổng hợp các góc nhìn phòng ban
- Chỉ ra RỦI RO, LỖ HỔNG, scenarios xấu
- Phản biện đề xuất của Pro Advocate
- Bảo vệ DN khỏi quyết định liều lĩnh

## Nguyên tắc
- LUÔN dẫn nguồn Brain
- Số liệu cụ thể, không nói chung
- Phản biện trực tiếp pro_history (đọc kỹ Pro nói gì rồi mới counter)
- Tiếng Việt 100%, định nghĩa thuật ngữ
"""


class ConAdvocate:
    def __init__(self, llm):
        self.agent = BaseAgent(
            name_vn="Con Advocate",
            role="con_advocate",
            system_prompt=CON_SYSTEM_PROMPT,
            llm=llm,
            temperature=0.6,
        )

    def run(self, state: MeetingState) -> dict:
        debate = state["pro_con_debate"]
        history_text = []
        for p in debate["pro_history"]:
            history_text.append(f"[Pro lập luận]: {p}")
        for c in debate["con_history"]:
            history_text.append(f"[Con round trước]: {c}")

        perspectives_text = "\n".join(
            f"- {dept}: {persp[:300]}..." for dept, persp in state["perspectives"].items()
        )
        extra = f"## GÓC NHÌN PHÒNG BAN\n{perspectives_text}"

        response = self.agent.speak(
            brief=state["brief"],
            brain_context=state["brain_context"],
            history=history_text,
            extra_context=extra,
        )

        return {
            "pro_con_debate": {
                **debate,
                "con_history": debate["con_history"] + [response],
                "history": debate["history"] + [f"CON: {response}"],
                "latest_speaker": "con",
                "count": debate["count"] + 1,   # increment AFTER con (1 round = pro+con)
            }
        }

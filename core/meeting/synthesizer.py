"""Synthesizer — tổng hợp toàn meeting → decision report cho CEO.

Adapted from TradingAgents/agents/managers/portfolio_manager.py với:
- Domain-neutral output (không leak portfolio/trade)
- RULE 4 enforce: TL;DR + định nghĩa thuật ngữ
- RULE 5 enforce: cite research findings
"""
from __future__ import annotations

from core.agents.base_agent import BaseAgent
from core.meeting.debate_state import MeetingState

SYNTHESIZER_PROMPT = """Bạn là người tổng hợp họp DN, viết báo cáo quyết định cho CEO.

## Output BẮT BUỘC theo format:

```markdown
# Báo cáo quyết định: <task>

## 📌 Tóm lại (đọc 30 giây)
- [3-5 dòng dân thường hiểu, đọc xong là biết nên làm gì]

## Khuyến nghị
[GO / GO with revisions / NO-GO / NEED_MORE_INFO]

## Điều chỉnh từ brief gốc (nếu có)
| Item | Brief gốc | Khuyến nghị | Lý do |
| ... |

## Phân tích chi tiết

### Mỗi phòng nói gì
[Tổng hợp perspectives]

### Tranh luận Pro vs Con
[Highlight key arguments]

### 3 góc nhìn (Growth/Cautious/Balanced)
[Summary]

## Việc cần làm trước khi triển khai (BLOCKERS)
[Checklist]

## KPI gates
[Cụ thể: tuần X nếu Y < Z thì pause]

## Câu hỏi cần CEO quyết
[A/B/C/D]
```

## Nguyên tắc (BẮT BUỘC)
- 🔒 RULE 4: Định nghĩa MỌI thuật ngữ chuyên ngành lần đầu xuất hiện
- 🔒 RULE 5: Cite mọi nhận định (Brain file:line, hoặc research source URL)
- Tiếng Việt 100%, đọc xong là CEO hiểu, không cần Google
- TL;DR phải đứng đầu, dân thường đọc 30 giây hiểu
"""


class Synthesizer:
    def __init__(self, llm):
        self.agent = BaseAgent(
            name_vn="Synthesizer",
            role="synthesizer",
            system_prompt=SYNTHESIZER_PROMPT,
            llm=llm,
            temperature=0.4,
        )

    def run(self, state: MeetingState) -> dict:
        perspectives_text = "\n\n".join(
            f"### {dept}\n{persp}" for dept, persp in state["perspectives"].items()
        )
        pc_text = "\n".join(state["pro_con_debate"]["history"])
        pd_text = "\n".join(state["perspective_debate"]["history"])
        research_text = ""
        if state.get("research_findings"):
            research_text = "## RESEARCH\n" + str(state["research_findings"])[:3000]

        extra = (
            f"## GÓC NHÌN PHÒNG BAN\n{perspectives_text}\n\n"
            f"## PRO vs CON\n{pc_text}\n\n"
            f"## PERSPECTIVE DEBATE\n{pd_text}\n\n"
            f"{research_text}"
        )

        report = self.agent.speak(
            brief=state["brief"],
            brain_context=state["brain_context"],
            history=[],
            extra_context=extra,
        )
        return {"final_report": report}

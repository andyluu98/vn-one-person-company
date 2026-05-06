"""Sinh câu hỏi clarification dựa trên gap.

🔒 RULE 1: KHÔNG generate question nếu gaps rỗng.
🔒 RULE 4: Tiếng Việt, định nghĩa thuật ngữ.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import re
from core.brain.gap_analyzer import Gap, Severity


@dataclass
class Question:
    text: str
    citation: str
    severity: Severity
    choices: list[str] = field(default_factory=list)
    free_text: bool = False


QG_PROMPT = """Bạn sinh câu hỏi clarification cho CEO DN VN.

## Nguyên tắc CỨNG (vi phạm = reject output)
- 🔒 Mỗi câu hỏi PHẢI có citation về Brain (file:section)
- 🔒 Tiếng Việt, không jargon trừ khi định nghĩa kèm
- 🔒 Có 2-4 choices (đa số), hoặc free_text nếu open-ended
- 🔒 Câu hỏi ngắn gọn, đọc 30 giây hiểu

## Output JSON: array of questions
```json
[
  {
    "text": "...",
    "citation": "00-Brain/<file>.md[:section]",
    "choices": ["A", "B", "C"],
    "severity": "CRITICAL|WARN",
    "free_text": false
  }
]
```

CRITICAL gap → câu hỏi PHẢI hỏi.
WARN gap → câu hỏi NÊN hỏi (CEO có thể skip).
INFO gap → KHÔNG hỏi.
"""


class QuestionGenerator:
    def __init__(self, llm):
        self.llm = llm

    def generate(self, gaps: list[Gap], brain: dict, brief: str) -> list[Question]:
        # 🔒 RULE 1: no gaps → no questions
        if not gaps:
            return []

        actionable = [g for g in gaps if g.severity in (Severity.CRITICAL, Severity.WARN)]
        if not actionable:
            return []

        gaps_text = "\n".join(
            f"- [{g.severity.value}] {g.field}: brief='{g.brief_value}' vs brain='{g.current_value}' "
            f"(cite: {g.citation}) — {g.reason}"
            for g in actionable
        )

        messages = [
            {"role": "system", "content": QG_PROMPT},
            {"role": "user", "content": f"## BRIEF\n{brief}\n\n## GAPS\n{gaps_text}\n\nSinh questions."},
        ]
        raw = self.llm.complete(messages)

        m = re.search(r"\[.*\]", raw, re.DOTALL)
        if not m:
            return []
        data = json.loads(m.group(0))

        return [Question(
            text=d["text"],
            citation=d["citation"],
            severity=Severity(d["severity"]),
            choices=d.get("choices", []),
            free_text=d.get("free_text", False),
        ) for d in data]

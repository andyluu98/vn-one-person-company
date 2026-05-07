"""So brief với Brain → list gaps cần CEO làm rõ.

🔒 RULE 1 enforce: gap PHẢI có citation chỉ về Brain file/section.
"""
from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
import json
import re
from core.brain.schema import BrainContext


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    WARN = "WARN"
    INFO = "INFO"


@dataclass
class Gap:
    field: str
    severity: Severity
    current_value: str
    brief_value: str
    reason: str
    citation: str   # 00-Brain/<file>.md[:section]


GAP_PROMPT = """Bạn là Gap Analyzer. So brief với Brain context, tìm điểm mâu thuẫn / thiếu thông tin.

## Output JSON BẮT BUỘC: array of gaps
```json
[
  {
    "field": "ICP|budget|product_fit|headcount|...",
    "severity": "CRITICAL|WARN|INFO",
    "current_value": "...",
    "brief_value": "...",
    "reason": "...",
    "citation": "00-Brain/<file>.md hoặc 00-Brain/<file>.md:<section>"
  }
]
```

## Nguyên tắc
- 🔒 RULE 1: Mỗi gap PHẢI có citation về Brain
- CRITICAL: brief mâu thuẫn strategy/budget/laws
- WARN: brief có thể OK nhưng cần CEO confirm
- INFO: nice-to-know, KHÔNG hỏi CEO
- Nếu brief KHỚP Brain hoàn toàn → return []
- Trả JSON array, KHÔNG kèm markdown
"""


class GapAnalyzer:
    def __init__(self, llm):
        self.llm = llm

    def analyze(self, brief: str, brain: BrainContext) -> list[Gap]:
        brain_dump = brain.model_dump_json(indent=2)
        messages = [
            {"role": "system", "content": GAP_PROMPT},
            {"role": "user", "content": (
                f"## BRIEF\n{brief}\n\n"
                f"## BRAIN\n```json\n{brain_dump}\n```\n\n"
                "Tìm gaps. Trả JSON array."
            )},
        ]
        raw = self.llm.complete(messages)
        data = self._parse_json_array(raw)
        return [Gap(
            field=d["field"],
            severity=Severity(d["severity"]),
            current_value=d.get("current_value", ""),
            brief_value=d.get("brief_value", ""),
            reason=d.get("reason", ""),
            citation=d["citation"],
        ) for d in data]

    async def aanalyze(self, brief: str, brain: BrainContext) -> list[Gap]:
        """Async version of analyze() — dùng trong async MCP tools."""
        brain_dump = brain.model_dump_json(indent=2)
        messages = [
            {"role": "system", "content": GAP_PROMPT},
            {"role": "user", "content": (
                f"## BRIEF\n{brief}\n\n"
                f"## BRAIN\n```json\n{brain_dump}\n```\n\n"
                "Tìm gaps. Trả JSON array."
            )},
        ]
        raw = await self.llm.acomplete(messages)
        data = self._parse_json_array(raw)
        return [Gap(
            field=d["field"],
            severity=Severity(d["severity"]),
            current_value=d.get("current_value", ""),
            brief_value=d.get("brief_value", ""),
            reason=d.get("reason", ""),
            citation=d["citation"],
        ) for d in data]

    @staticmethod
    def _parse_json_array(raw: str) -> list[dict]:
        m = re.search(r"\[.*\]", raw, re.DOTALL)
        if not m:
            return []
        return json.loads(m.group(0))

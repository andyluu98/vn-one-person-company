"""Phân loại task: SIMPLE / COMPLEX / STRATEGIC + chọn phòng tham gia."""
from __future__ import annotations
from enum import Enum
from pathlib import Path
import json
import re
import yaml
from dataclasses import dataclass
from core.brain.schema import BrainContext


class TaskClass(str, Enum):
    SIMPLE = "SIMPLE"
    COMPLEX = "COMPLEX"
    STRATEGIC = "STRATEGIC"


@dataclass
class TaskClassification:
    class_: TaskClass
    departments: list[str]
    reasoning: str
    confidence: float = 0.8


ROUTER_PROMPT = """Bạn là router phân loại task DN VN.

## Phân loại
- SIMPLE: 1-2 phòng, không cần họp. VD: soạn JD, hợp đồng mẫu.
- COMPLEX: 3-5 phòng họp debate. VD: chiến dịch QC, kế hoạch tuyển dụng.
- STRATEGIC: 5+ phòng, CEO duyệt giữa chừng. VD: gọi vốn, M&A, pivot.

## Phòng ban (mã chuẩn)
01-governance, 02-strategy, 03-finance, 04-people, 05-operations,
06-sales, 07-marketing, 08-customer, 09-product-tech, 10-training,
11-reporting, 12-growth, + pack-specific (13-XX)

## Output JSON BẮT BUỘC
```json
{
  "class": "SIMPLE|COMPLEX|STRATEGIC",
  "departments": ["XX-name", ...],
  "reasoning": "..."
}
```

## Nguyên tắc chọn phòng
- Suy ra từ keyword trong brief
- Tham chiếu Brain để biết phòng nào active
- Strict: chỉ chọn phòng thực sự cần
"""


class Router:
    def __init__(self, llm, rules_path: Path | None = None):
        self.llm = llm
        if rules_path:
            self.rules = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
        else:
            self.rules = {}

    def classify(self, brief: str, brain: BrainContext) -> TaskClassification:
        active = brain.headcount.active_departments
        rules_text = yaml.safe_dump(self.rules, allow_unicode=True)

        messages = [
            {"role": "system", "content": ROUTER_PROMPT + f"\n\n## RULES\n```yaml\n{rules_text}\n```"},
            {"role": "user", "content": (
                f"## BRIEF\n{brief}\n\n"
                f"## PHÒNG ĐANG ACTIVE\n{active}\n\n"
                f"Phân loại + chọn phòng cần triệu tập. Trả JSON đúng format."
            )},
        ]
        raw = self.llm.complete(messages)
        data = self._parse_json(raw)
        return TaskClassification(
            class_=TaskClass(data["class"]),
            departments=data["departments"],
            reasoning=data.get("reasoning", ""),
            confidence=float(data.get("confidence", 0.8)),
        )

    @staticmethod
    def _parse_json(raw: str) -> dict:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            raise ValueError(f"Router output no JSON: {raw[:200]}")
        return json.loads(m.group(0))

from unittest.mock import MagicMock
from pathlib import Path
from core.orchestrator.router import Router, TaskClass
from core.brain.schema import (
    BrainContext, Strategy, Budget, Headcount, Product,
)

REPO = Path(__file__).parent.parent.parent


def _brain():
    return BrainContext(
        strategy=Strategy(vision="V", icp="SME"),
        products=[Product(code="P", name="X", price_vnd=1000, margin_pct=50)],
        budget=Budget(total_year_vnd=1_000_000_000),
        headcount=Headcount(active_departments=["07-marketing", "03-finance"]),
        laws=[], decisions=[], state="growth", glossary={},
    )


def test_router_keyword_simple():
    llm = MagicMock(complete=MagicMock(return_value='{"class": "SIMPLE", "departments": ["04-people"], "reasoning": "JD task"}'))
    r = Router(llm=llm, rules_path=REPO / "core/orchestrator/classifier_rules.yaml")
    result = r.classify("Soạn JD cho vị trí kế toán trưởng", _brain())
    assert result.class_ == TaskClass.SIMPLE


def test_router_keyword_complex():
    llm = MagicMock(complete=MagicMock(return_value=
        '{"class": "COMPLEX", "departments": ["07-marketing", "02-strategy", "03-finance", "08-customer", "01-governance"], "reasoning": "campaign needs many"}'
    ))
    r = Router(llm=llm, rules_path=REPO / "core/orchestrator/classifier_rules.yaml")
    result = r.classify("Tạo chiến dịch QC nhắm khách thu nhập 50tr+", _brain())
    assert result.class_ == TaskClass.COMPLEX
    assert len(result.departments) == 5


def test_router_returns_reasoning():
    llm = MagicMock(complete=MagicMock(return_value=
        '{"class": "STRATEGIC", "departments": ["02-strategy","03-finance","12-growth","01-governance","04-people"], "reasoning": "M&A high stakes"}'
    ))
    r = Router(llm=llm, rules_path=REPO / "core/orchestrator/classifier_rules.yaml")
    result = r.classify("Đánh giá M&A đối thủ Y", _brain())
    assert "M&A" in result.reasoning

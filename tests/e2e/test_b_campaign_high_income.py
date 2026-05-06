"""E2E test case B - Chien dich QC nham khach thu nhap 50tr+.

Validates 6 RULES + acceptance criteria with mocked LLM.
"""
import json
import shutil
from pathlib import Path
from unittest.mock import MagicMock
import pytest


REPO = Path(__file__).parent.parent.parent
FIXTURE = REPO / "tests/fixtures/techco-vault"


@pytest.fixture
def llm_mock():
    """Mocked LLM with pre-canned responses for each stage."""

    responses = {
        "router_classify": json.dumps({
            "class": "COMPLEX",
            "departments": ["07-marketing", "02-strategy", "03-finance", "08-customer", "01-governance"],
            "reasoning": "Campaign QC + budget lon + can check legal + ICP gap",
        }),
        "gap_analysis": json.dumps([
            {"field": "ICP", "severity": "CRITICAL",
             "current_value": "SME (chu DN)", "brief_value": "thu nhap 50tr+",
             "reason": "Brief lech ICP strategy", "citation": "00-Brain/strategy.md"},
            {"field": "content_capability", "severity": "CRITICAL",
             "current_value": "khong co content-premium", "brief_value": "can content cao cap",
             "reason": "Headcount thieu specialist", "citation": "00-Brain/headcount.md"},
        ]),
        "questions": json.dumps([
            {"text": "Pivot dai han hay test 1 lan?",
             "citation": "00-Brain/strategy.md",
             "choices": ["Pivot dai han", "Test 1 lan (chu SME thu nhap 50tr+)", "Huy"],
             "severity": "CRITICAL", "free_text": False},
            {"text": "Tao agent content-premium hay outsource?",
             "citation": "00-Brain/headcount.md",
             "choices": ["Tao agent moi", "Outsource", "Marketing kiem"],
             "severity": "CRITICAL", "free_text": False},
        ]),
        "tool_plan": json.dumps({"tools": [
            {"tool": "industry_benchmark", "queries": ["saas_b2b cac"]},
        ]}),
        "perspective": "Phong de xuat trien khai can trong, kem so lieu Brain.",
        "pro_advocate": "GO. Co hoi thi truong ro. CAC 8tr/SQL theo benchmark.",
        "con_advocate": "Rui ro 62% budget don 1 cho + CSKH chua ready.",
        "growth": "GO bold - runway 18m du test ICP cao cap.",
        "cautious": "GO with gates - tuan 1 CTR < 2% pause.",
        "balanced": "Pilot 200tr/4 tuan + setup CSKH Premium.",
        "synthesizer": """## 📌 Tóm lại (đọc 30 giây)
- GO with revisions: 200tr/4 tuan
- 4 BLOCKERS phai xong truoc launch
- KPI: 1 deal Premium thang dau

## Khuyến nghị
GO with revisions

## Việc cần làm trước launch
1. [ ] Setup CSKH Premium tier
2. [ ] Train sales pitch Premium
3. [ ] Tao agent content-premium-b2b-specialist
4. [ ] Update privacy policy

## KPI gates
- Tuan 1: CTR >= 2%
- Tuan 4: >= 1 deal Premium

## Câu hỏi cần CEO quyết
A. Approve plan nay
B. Approve nhung khong cho blockers
C. Reject
D. Sua
""",
    }

    def respond(messages, model=None):
        sys_text = messages[0]["content"]

        # Order matters - check most-specific first
        if "router phân loại task" in sys_text or "Router" in sys_text and "phân loại" in sys_text:
            return responses["router_classify"]
        if "Gap Analyzer" in sys_text:
            return responses["gap_analysis"]
        if "sinh câu hỏi clarification" in sys_text:
            return responses["questions"]
        if "Tool Router" in sys_text:
            return responses["tool_plan"]
        if "Pro Advocate" in sys_text:
            return responses["pro_advocate"]
        if "Con Advocate" in sys_text:
            return responses["con_advocate"]
        if "TĂNG TRƯỞNG" in sys_text:
            return responses["growth"]
        if "THẬN TRỌNG" in sys_text:
            return responses["cautious"]
        if "CÂN BẰNG" in sys_text:
            return responses["balanced"]
        if "tổng hợp họp DN" in sys_text or "báo cáo quyết định" in sys_text:
            return responses["synthesizer"]
        if "biên tập viên DN VN" in sys_text:
            # simplifier - just return synth content unchanged
            return responses["synthesizer"]
        if "Tóm tắt báo cáo" in sys_text:
            # tldr - already has '📌 Tóm lại' marker
            return ""
        if "Ban la phong" in sys_text and "trong DN VN" in sys_text:
            # PerspectivesCollector dept agent
            return responses["perspective"]
        return "..."

    llm = MagicMock()
    llm.complete.side_effect = respond
    return llm


def test_e2e_b_campaign_full_flow(tmp_path, llm_mock):
    """Full E2E flow: brief -> clarify -> meeting -> decision report."""
    vault = tmp_path / "vault"
    shutil.copytree(FIXTURE, vault)

    from core.orchestrator.flow_controller import FlowController, FlowStage

    fc = FlowController(vault_root=vault, llm=llm_mock)

    # Stage 1: brief -> clarification
    result = fc.run(brief="Tạo chiến dịch QC nhắm khách thu nhập 50tr+, NS 500tr, launch trước 30/6")

    assert result.stage == FlowStage.PAUSE_CLARIFICATION
    task_folder = result.task_folder

    # Verify files
    assert (task_folder / "00-brief.md").exists()
    assert (task_folder / "01-routing.md").exists()
    assert (task_folder / "02-context.md").exists()
    assert (task_folder / "03-clarification.md").exists()

    # RULE 1: questions co citation
    clarif = (task_folder / "03-clarification.md").read_text(encoding="utf-8")
    assert "00-Brain/strategy.md" in clarif
    assert "00-Brain/headcount.md" in clarif

    # Auto-tick CEO answers
    answered = clarif.replace(
        "- [ ] Test 1 lan (chu SME thu nhap 50tr+)",
        "- [x] Test 1 lan (chu SME thu nhap 50tr+)",
    ).replace(
        "- [ ] Tao agent moi",
        "- [x] Tao agent moi",
    )
    (task_folder / "03-clarification.md").write_text(answered, encoding="utf-8")

    # Stage 2: resume after clarification
    result = fc.resume_after_clarification(task_folder)
    assert result.stage == FlowStage.PAUSE_DECISION_REPORT

    # Stage 3: meeting
    departments = ["07-marketing", "02-strategy", "03-finance", "08-customer", "01-governance"]
    result = fc.run_meeting(task_folder, departments=departments)
    assert result.stage == FlowStage.PAUSE_DECISION_REPORT

    # Verify meeting outputs
    assert (task_folder / "03b-research-findings.md").exists()
    assert (task_folder / "04-meeting-r1-perspectives.md").exists()
    assert (task_folder / "05-meeting-r2-debate.md").exists()
    assert (task_folder / "06-meeting-r3-perspectives.md").exists()
    assert (task_folder / "07-decision-report.md").exists()

    # ACCEPTANCE
    decision = (task_folder / "07-decision-report.md").read_text(encoding="utf-8")
    assert "📌 Tóm lại" in decision
    assert "Khuyến nghị" in decision or "Câu hỏi cần CEO quyết" in decision


def test_acceptance_no_trade_leakage_in_outputs(tmp_path, llm_mock):
    """RULE 2: outputs phai khong co Bull/Bear/trade/etc."""
    vault = tmp_path / "vault"
    shutil.copytree(FIXTURE, vault)

    from core.orchestrator.flow_controller import FlowController
    fc = FlowController(vault_root=vault, llm=llm_mock)
    result = fc.run(brief="Test campaign")

    forbidden = ["Bull", "Bear", "ticker", "yfinance", "trader"]
    for f in (result.task_folder).rglob("*.md"):
        content = f.read_text(encoding="utf-8")
        for word in forbidden:
            assert word not in content, f"Found '{word}' in {f.name}"

"""Phase 3 smoke: orchestrator pipeline imports + run với mock LLM."""
from unittest.mock import MagicMock
from pathlib import Path
import json
import shutil


def test_full_orchestrator_imports():
    from core.orchestrator.router import Router, TaskClass
    from core.orchestrator.flow_controller import FlowController, FlowStage
    from core.orchestrator.perspectives_collector import PerspectivesCollector
    from core.brain.gap_analyzer import GapAnalyzer
    from core.clarifier.question_generator import QuestionGenerator
    from core.clarifier.clarification_io import write_clarification, read_answers


def test_full_flow_writes_all_task_files(tmp_path):
    fixture = Path(__file__).parent.parent / "fixtures" / "demo-vault"
    vault = tmp_path / "vault"
    shutil.copytree(fixture, vault)

    # Need 02-Tasks dir for create_task_folder
    (vault / "02-Tasks").mkdir(exist_ok=True)

    llm = MagicMock()
    llm.complete.side_effect = [
        json.dumps({"class": "COMPLEX", "departments": ["07-marketing"], "reasoning": "r"}),
        json.dumps([{
            "field": "ICP", "severity": "CRITICAL",
            "current_value": "SME", "brief_value": "50tr+",
            "reason": "x", "citation": "00-Brain/strategy.md"
        }]),
        json.dumps([{
            "text": "Pivot?", "citation": "00-Brain/strategy.md",
            "choices": ["A", "B"], "severity": "CRITICAL", "free_text": False,
        }]),
    ]

    from core.orchestrator.flow_controller import FlowController
    fc = FlowController(vault_root=vault, llm=llm)
    r = fc.run(brief="Tạo chiến dịch")

    expected = ["00-brief.md", "01-routing.md", "02-context.md", "03-clarification.md"]
    for fname in expected:
        assert (r.task_folder / fname).exists(), f"Missing {fname}"

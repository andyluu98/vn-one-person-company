import json
from unittest.mock import MagicMock
from core.clarifier.question_generator import QuestionGenerator, Question
from core.brain.gap_analyzer import Gap, Severity


def test_no_gaps_no_questions():
    qg = QuestionGenerator(llm=MagicMock())
    questions = qg.generate(gaps=[], brain={}, brief="x")
    assert questions == []


def test_critical_gap_generates_critical_question():
    fake = json.dumps([{
        "text": "strategy.md ghi ICP là SME. Brief 50tr+ — pivot hay test?",
        "citation": "00-Brain/strategy.md",
        "choices": ["Pivot dài hạn", "Test 1 lần", "Hủy"],
        "severity": "CRITICAL",
    }])
    llm = MagicMock(complete=MagicMock(return_value=fake))
    qg = QuestionGenerator(llm=llm)
    gap = Gap(field="ICP", severity=Severity.CRITICAL,
              current_value="SME", brief_value="50tr+",
              reason="r", citation="00-Brain/strategy.md")
    questions = qg.generate(gaps=[gap], brain={"strategy": "..."}, brief="b")
    assert len(questions) == 1
    assert questions[0].severity == Severity.CRITICAL
    assert "strategy.md" in questions[0].citation

from pathlib import Path
from core.clarifier.question_generator import Question
from core.brain.gap_analyzer import Severity
from core.clarifier.clarification_io import (
    write_clarification, read_answers, AnsweredQuestion,
)


def test_write_clarification_creates_file(tmp_path):
    qs = [Question(
        text="Pivot hay test?",
        citation="00-Brain/strategy.md",
        choices=["Pivot dài hạn", "Test 1 lần"],
        severity=Severity.CRITICAL,
    )]
    f = tmp_path / "03-clarification.md"
    write_clarification(f, qs)
    content = f.read_text(encoding="utf-8")
    assert "Pivot hay test?" in content
    assert "[ ] Pivot dài hạn" in content
    assert "00-Brain/strategy.md" in content


def test_read_answers_parses_user_choice(tmp_path):
    f = tmp_path / "03-clarification.md"
    f.write_text(
        "---\ntype: clarification\n---\n"
        "## Q1 [CRITICAL]\n_Cite: 00-Brain/strategy.md_\n"
        "Pivot hay test?\n\n"
        "- [ ] Pivot dài hạn\n"
        "- [x] Test 1 lần\n"
        "- [ ] Hủy\n",
        encoding="utf-8",
    )
    answers = read_answers(f)
    assert len(answers) == 1
    assert answers[0].choice == "Test 1 lần"

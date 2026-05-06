"""Tests for P1.8 — CitationValidator post-Synthesizer."""
from __future__ import annotations

from pathlib import Path

import pytest

from core.orchestrator.citation_validator import (
    CitationFlag,
    CitationValidator,
    _is_common_knowledge,
    _split_sentences,
)


# ── helpers ───────────────────────────────────────────────────────────────


def _write_report(tmp_path: Path, content: str, name: str = "07-decision-report.md") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ── _split_sentences ──────────────────────────────────────────────────────


class TestSplitSentences:
    def test_single_sentence(self):
        result = _split_sentences("Doanh thu tăng 20% so cùng kỳ.")
        assert result == ["Doanh thu tăng 20% so cùng kỳ."]

    def test_multiple_sentences(self):
        text = "Doanh thu tăng 20%. Chi phí giảm 5 triệu VND. Đây là kết quả tốt."
        result = _split_sentences(text)
        assert len(result) == 3

    def test_question_and_exclamation(self):
        text = "Liệu tăng 30% có khả thi? Đây là mục tiêu đầy thách thức!"
        result = _split_sentences(text)
        assert len(result) == 2

    def test_empty_string(self):
        assert _split_sentences("") == []

    def test_no_punctuation(self):
        result = _split_sentences("một câu không có dấu chấm")
        assert result == ["một câu không có dấu chấm"]


# ── _is_common_knowledge ──────────────────────────────────────────────────


class TestIsCommonKnowledge:
    def test_tet_is_common(self):
        assert _is_common_knowledge("Tết Nguyên Đán là dịp tiêu thụ lớn nhất năm.")

    def test_tet_dip_is_common(self):
        assert _is_common_knowledge("Đây là mùa lễ hội truyền thống.")

    def test_claim_with_number_not_common(self):
        assert not _is_common_knowledge("Doanh thu tăng 20% so với quý trước.")

    def test_legal_ref_not_common(self):
        assert not _is_common_knowledge("Theo Nghị định 15/2018/NĐ-CP, doanh nghiệp phải...")

    def test_pho_bien_is_common(self):
        assert _is_common_knowledge("Đây là thông lệ phổ biến trong ngành.")


# ── CitationValidator core logic ──────────────────────────────────────────


class TestCitationValidatorFindClaims:
    """Test _find_uncited_claims directly with string content."""

    def setup_method(self):
        self.validator = CitationValidator()

    def test_numeric_claim_no_citation_flagged(self):
        content = "Doanh thu tháng 3 tăng 25% so với tháng 2."
        flags = self.validator._find_uncited_claims(content)
        assert any(f.reason == "numeric_claim" for f in flags)

    def test_numeric_claim_with_source_not_flagged(self):
        content = "Doanh thu tháng 3 tăng 25% so với tháng 2. [source: finance.md]"
        flags = self.validator._find_uncited_claims(content)
        assert len(flags) == 0

    def test_numeric_claim_with_brain_file_not_flagged(self):
        content = "Chi phí lao động chiếm 23.5% tổng chi phí (strategy.md mục 4)."
        flags = self.validator._find_uncited_claims(content)
        assert len(flags) == 0

    def test_numeric_claim_with_url_not_flagged(self):
        content = "Tăng trưởng 15% theo https://gso.gov.vn/report-2024."
        flags = self.validator._find_uncited_claims(content)
        assert len(flags) == 0

    def test_legal_claim_no_citation_flagged(self):
        content = "Theo Nghị định 15/2018/NĐ-CP, thực phẩm chức năng phải đăng ký."
        flags = self.validator._find_uncited_claims(content)
        assert any(f.reason == "legal_claim" for f in flags)

    def test_legal_claim_with_brain_laws_not_flagged(self):
        content = "Theo Nghị định 15/2018/NĐ-CP [laws.md mục 3], cần đăng ký sản phẩm."
        flags = self.validator._find_uncited_claims(content)
        assert len(flags) == 0

    def test_thong_tu_flagged(self):
        content = "Theo Thông tư 200/2014/TT-BTC, báo cáo tài chính phải nộp trước 30/3."
        flags = self.validator._find_uncited_claims(content)
        # Has both legal AND numeric — at least one flag
        assert len(flags) >= 1

    def test_common_knowledge_not_flagged(self):
        content = "Tết Nguyên Đán là dịp tiêu thụ lớn nhất trong năm cho hầu hết ngành bán lẻ."
        flags = self.validator._find_uncited_claims(content)
        assert len(flags) == 0

    def test_heading_lines_skipped(self):
        content = "## Doanh thu tăng 25% quý này\n\nNội dung không có số."
        flags = self.validator._find_uncited_claims(content)
        assert len(flags) == 0

    def test_code_block_skipped(self):
        content = "```yaml\nrevenue: 25000000\ngrowth: 20%\n```"
        flags = self.validator._find_uncited_claims(content)
        assert len(flags) == 0

    def test_table_row_skipped(self):
        content = "| Tháng 3 | 25% | tăng |"
        flags = self.validator._find_uncited_claims(content)
        assert len(flags) == 0

    def test_short_sentence_skipped(self):
        # < 20 chars — not enough context
        content = "Tăng 20%."
        flags = self.validator._find_uncited_claims(content)
        assert len(flags) == 0

    def test_vnd_currency_flagged(self):
        content = "Ngân sách marketing dự kiến 500 triệu VND cho Q3."
        flags = self.validator._find_uncited_claims(content)
        assert any(f.reason == "numeric_claim" for f in flags)

    def test_usd_currency_flagged(self):
        content = "Chi phí triển khai ước tính khoảng 50.000 USD cho năm đầu."
        flags = self.validator._find_uncited_claims(content)
        assert any(f.reason == "numeric_claim" for f in flags)

    def test_multiple_flags_from_multiple_lines(self):
        content = (
            "Doanh thu tháng 3 tăng 25% so với tháng 2.\n"
            "Đây là kết quả tốt trong bối cảnh thị trường.\n"
            "Chi phí lao động 23.5% tổng chi phí.\n"
        )
        flags = self.validator._find_uncited_claims(content)
        assert len(flags) >= 2

    def test_flag_contains_line_number(self):
        content = "Dòng 1 không có số.\nDòng 2 tăng 25% so với tháng trước.\n"
        flags = self.validator._find_uncited_claims(content)
        assert any(f.line_no == 2 for f in flags)

    def test_sentence_truncated_to_200_chars(self):
        long_sentence = "Doanh thu tăng 50% " + "x" * 300 + "."
        flags = self.validator._find_uncited_claims(long_sentence)
        if flags:
            assert len(flags[0].sentence) <= 200

    def test_brain_file_inline_reference_clears_flag(self):
        content = "Tỷ lệ gross margin 45% theo strategy.md mục kế hoạch tài chính."
        flags = self.validator._find_uncited_claims(content)
        assert len(flags) == 0

    def test_markdown_link_with_url_clears_flag(self):
        content = "Tăng trưởng ngành 12% theo [Báo cáo GSO](https://gso.gov.vn/2024)."
        flags = self.validator._find_uncited_claims(content)
        assert len(flags) == 0

    def test_no_claims_returns_empty(self):
        content = "Đây là một báo cáo hoàn toàn không có số liệu hay tham chiếu pháp lý."
        flags = self.validator._find_uncited_claims(content)
        assert flags == []


# ── CitationValidator.validate (file I/O) ────────────────────────────────


class TestCitationValidatorFileIO:
    def setup_method(self):
        self.validator = CitationValidator()

    def test_returns_empty_for_nonexistent_file(self, tmp_path):
        flags = self.validator.validate(tmp_path / "missing.md")
        assert flags == []

    def test_no_warning_appended_when_no_flags(self, tmp_path):
        p = _write_report(tmp_path, "# Báo cáo\n\nKhông có số liệu nào ở đây.")
        original = p.read_text(encoding="utf-8")
        flags = self.validator.validate(p)
        assert flags == []
        assert p.read_text(encoding="utf-8") == original

    def test_warning_appended_when_flags_found(self, tmp_path):
        content = (
            "---\ntype: decision_report\n---\n"
            "# Báo cáo\n\n"
            "Doanh thu tháng 3 tăng 25% so với tháng 2.\n"
        )
        p = _write_report(tmp_path, content)
        flags = self.validator.validate(p)
        assert len(flags) > 0
        result = p.read_text(encoding="utf-8")
        assert "⚠️" in result
        assert "Claims thiếu trích nguồn" in result

    def test_warning_section_contains_flagged_sentence(self, tmp_path):
        content = "# Báo cáo\n\nNgân sách marketing dự kiến 500 triệu VND cho Q3.\n"
        p = _write_report(tmp_path, content)
        self.validator.validate(p)
        result = p.read_text(encoding="utf-8")
        assert "500 triệu VND" in result

    def test_no_double_append_on_second_validate_call(self, tmp_path):
        content = "# Báo cáo\n\nDoanh thu tăng 25% so với tháng trước.\n"
        p = _write_report(tmp_path, content)
        self.validator.validate(p)
        self.validator.validate(p)
        result = p.read_text(encoding="utf-8")
        # Warning header should appear exactly once
        assert result.count("Claims thiếu trích nguồn") == 1

    def test_warning_section_format(self, tmp_path):
        content = "# Report\n\nDoanh thu tháng 3 tăng 25%.\nTheo Nghị định 15/2018, cần đăng ký.\n"
        p = _write_report(tmp_path, content)
        flags = self.validator.validate(p)
        result = p.read_text(encoding="utf-8")
        # Each flag listed as bullet
        assert "- **[Dòng" in result

    def test_original_content_preserved_before_warning(self, tmp_path):
        content = "---\ntype: decision_report\n---\n# Báo cáo\n\nDoanh thu tăng 25%.\n"
        p = _write_report(tmp_path, content)
        self.validator.validate(p)
        result = p.read_text(encoding="utf-8")
        assert result.startswith("---\ntype: decision_report")

    def test_flag_count_matches_return_value(self, tmp_path):
        content = (
            "Doanh thu tăng 25%.\n"
            "Chi phí 500 triệu VND.\n"
            "Theo Nghị định 15/2018, cần giấy phép.\n"
        )
        p = _write_report(tmp_path, content)
        flags = self.validator.validate(p)
        # All flagged lines should be in return list (at least 2)
        assert len(flags) >= 2


# ── integration: clean report round-trip ─────────────────────────────────


class TestCitationValidatorIntegration:
    def test_full_report_with_citations_passes_clean(self, tmp_path):
        content = (
            "---\ntype: decision_report\nstop: 1\n---\n"
            "# Báo cáo quyết định\n\n"
            "## Tóm lại\n"
            "Phương án khả thi dựa trên dữ liệu hiện có.\n\n"
            "## Phân tích\n"
            "Gross margin đạt 45% theo [strategy.md] mục kế hoạch.\n"
            "Chi phí lao động 23.5% [source: finance.md] theo VAS.\n"
            "Theo Nghị định 15/2018/NĐ-CP [laws.md mục 3], sản phẩm cần đăng ký.\n"
        )
        p = tmp_path / "07-decision-report.md"
        p.write_text(content, encoding="utf-8")
        validator = CitationValidator()
        flags = validator.validate(p)
        assert flags == []
        # File unchanged
        assert p.read_text(encoding="utf-8") == content

    def test_full_report_with_missing_citations_gets_warning(self, tmp_path):
        content = (
            "---\ntype: decision_report\nstop: 1\n---\n"
            "# Báo cáo quyết định\n\n"
            "## Phân tích\n"
            "Gross margin đạt 45% trong quý vừa qua.\n"
            "Chi phí nhân sự chiếm 500 triệu VND.\n"
            "Đây là mức phổ biến trong ngành.\n"
        )
        p = tmp_path / "07-decision-report.md"
        p.write_text(content, encoding="utf-8")
        validator = CitationValidator()
        flags = validator.validate(p)
        assert len(flags) >= 2
        result = p.read_text(encoding="utf-8")
        assert "⚠️ Cảnh báo" in result

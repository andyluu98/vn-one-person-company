"""P1.8 — Citation validator post-Synthesizer.

Phân tích decision report markdown, tìm claims có facts/numbers/regulations
mà không có citation, append cảnh báo vào cuối report.

Heuristics (không quá strict):
- Claim = câu chứa số liệu cụ thể (vd "tăng 20%", "5 triệu VND", "30 ngày")
  HOẶC tên luật/nghị định (vd "Nghị định 15/2018", "Thông tư 200")
- Citation = câu/đoạn chứa [source: ...] hoặc cite Brain file (strategy.md, laws.md, ...)
  hoặc URL (http/https)
- Common knowledge phrases được miễn (không cần cite)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


# ────────────────────────────── Patterns ─────────────────────────────── #

# Số liệu cụ thể: phần trăm, tiền tệ VND/USD, ngày/tháng dạng số.
# NOTE: outer \b omitted intentionally — % and VND are non-word chars so \b after
# them creates an impossible boundary. Patterns are specific enough without it.
_RE_NUMERIC_CLAIM = re.compile(
    r"""
    (?:
        \d+[\.,]?\d*\s*%                                               # phần trăm: 20%, 3.5%
      | \d+[\.,]?\d*\s*(?:triệu|tỷ|nghìn|ngàn)\s*(?:VND|USD|đồng)?   # tiền tệ VN
      | \d+[\.,]?\d*\s*(?:VND|USD|EUR)                                 # tiền tệ quốc tế
      | \d+\s*(?:ngày|tháng|năm|tuần|giờ|phút)                        # khoảng thời gian
      | \d{1,3}(?:[.,]\d{3})+                                          # số lớn: 1.000.000
    )
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Tên luật/nghị định/thông tư.
# \b before keyword works fine (keyword starts with word char).
# Trailing \b omitted — number/slash suffix ends with non-word chars in many cases.
_RE_LEGAL_CLAIM = re.compile(
    r"""
    \b(?:Nghị\s*định|Thông\s*tư|Quyết\s*định|Luật|Pháp\s*lệnh|Circular|Decree)
    \s+\d+[\w/\-]*
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Citation markers được chấp nhận
_RE_CITATION = re.compile(
    r"""
    (?:
        \[source\s*:\s*[^\]]+\]          # [source: ...]
      | \[[^\]]+\.md[^\]]*\]             # [strategy.md], [finance.md:12], etc.
      | \[[^\]]+\]\(https?://[^\)]+\)    # markdown link với URL
      | https?://\S+                     # bare URL
      | \*\s*Nguồn\s*:                   # * Nguồn:
      | Tham\s*chiếu\s*Brain\s*:         # "Tham chiếu Brain:"
      | cite\s*[:：]                     # "cite:"
      | \(Brain\s*[^)]+\)                # (Brain strategy.md)
      | \[[^\]]*(?:strategy|finance|laws|products|operations|marketing|hr|tech)\.md[^\]]*\]
    )
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Brain file names — nếu câu nhắc tới file brain thì coi là có cite
_RE_BRAIN_FILE = re.compile(
    r"\b(?:strategy|finance|laws|products|operations|marketing|hr|tech|glossary)\.md\b",
    re.IGNORECASE,
)

# Common knowledge phrases được miễn — không cần citation
_COMMON_KNOWLEDGE_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        r"Tết\s+(?:Nguyên\s+Đán|là|dịp)",
        r"mùa\s+lễ\s+hội",
        r"truyền\s+thống\s+văn\s+hóa",
        r"thông\s+thường",
        r"phổ\s+biến",
        r"thường\s+thấy",
        r"theo\s+thông\s+lệ",
        r"kinh\s+nghiệm\s+chung",
    ]
]

# Bỏ qua các section headings và frontmatter lines
_RE_HEADING = re.compile(r"^#{1,6}\s+|^---|^\*\*\*|^---$")
# Câu quá ngắn (< 20 ký tự) — không đủ context để là claim
_MIN_SENTENCE_LEN = 20


# ────────────────────────────── Data model ─────────────────────────────── #


@dataclass
class CitationFlag:
    """Một claim thiếu citation."""
    line_no: int
    sentence: str
    reason: str  # "numeric_claim" | "legal_claim"


# ────────────────────────────── Validator ─────────────────────────────── #


class CitationValidator:
    """Validate decision report, flag claims thiếu citation, append warning section."""

    # Warning section header injected vào cuối report
    WARNING_HEADER = "\n\n---\n\n## ⚠️ Cảnh báo: Claims thiếu trích nguồn\n\n"
    WARNING_INTRO = (
        "Các câu sau chứa số liệu hoặc tham chiếu pháp lý nhưng "
        "không tìm thấy citation rõ ràng. CEO nên xác minh trước khi triển khai:\n\n"
    )

    def validate(self, report_path: Path) -> list[CitationFlag]:
        """Đọc report, flag claims thiếu citation, ghi warning section vào file.

        Returns:
            Danh sách CitationFlag (có thể rỗng nếu không có vấn đề).
        """
        path = Path(report_path)
        if not path.exists():
            return []

        content = path.read_text(encoding="utf-8")
        flags = self._find_uncited_claims(content)

        if flags:
            warning = self._build_warning_section(flags)
            # Append warning — chỉ nếu chưa có (tránh double-append khi validate lại)
            if self.WARNING_HEADER.strip() not in content:
                path.write_text(content + warning, encoding="utf-8")

        return flags

    def _find_uncited_claims(self, content: str) -> list[CitationFlag]:
        """Parse từng câu trong content, trả về danh sách flags."""
        flags: list[CitationFlag] = []
        lines = content.splitlines()

        for line_no, line in enumerate(lines, start=1):
            # Bỏ qua headings, frontmatter, blank lines
            stripped = line.strip()
            if not stripped or _RE_HEADING.match(stripped):
                continue
            # Bỏ qua đoạn code block (không validate nội dung code/yaml)
            if stripped.startswith("```") or stripped.startswith("|"):
                continue

            # Citation marker có thể ở sau dấu chấm cùng dòng (vd:
            # "Doanh thu tăng 25%. [source: finance.md]"). Check toàn dòng,
            # nếu có citation thì bỏ qua mọi câu trong dòng đó.
            line_has_cite = bool(
                _RE_CITATION.search(stripped) or _RE_BRAIN_FILE.search(stripped)
            )

            # Tách câu trong dòng (theo dấu chấm/chấm hỏi/chấm than)
            sentences = _split_sentences(stripped)

            for sentence in sentences:
                if len(sentence) < _MIN_SENTENCE_LEN:
                    continue
                if _is_common_knowledge(sentence):
                    continue

                # Kiểm tra có citation trong câu hoặc trong dòng cùng cấp
                has_cite = line_has_cite or bool(
                    _RE_CITATION.search(sentence) or _RE_BRAIN_FILE.search(sentence)
                )
                if has_cite:
                    continue

                # Flag nếu có numeric claim
                if _RE_NUMERIC_CLAIM.search(sentence):
                    flags.append(CitationFlag(
                        line_no=line_no,
                        sentence=sentence[:200],
                        reason="numeric_claim",
                    ))
                # Flag nếu nhắc luật/nghị định không có citation
                elif _RE_LEGAL_CLAIM.search(sentence):
                    flags.append(CitationFlag(
                        line_no=line_no,
                        sentence=sentence[:200],
                        reason="legal_claim",
                    ))

        return flags

    def _build_warning_section(self, flags: list[CitationFlag]) -> str:
        """Tạo markdown warning section từ danh sách flags."""
        lines = [self.WARNING_HEADER, self.WARNING_INTRO]
        for f in flags:
            label = "Số liệu" if f.reason == "numeric_claim" else "Pháp lý"
            lines.append(f"- **[Dòng {f.line_no}] {label}:** {f.sentence}\n")
        return "".join(lines)


# ────────────────────────────── Helpers ─────────────────────────────── #


def _split_sentences(text: str) -> list[str]:
    """Tách văn bản thành câu theo dấu chấm câu tiếng Việt.

    Không dùng regex phức tạp — split đơn giản đủ cho heuristic validator.
    """
    # Split tại dấu chấm, hỏi, than — nhưng giữ lại dấu (join lại sau)
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def _is_common_knowledge(sentence: str) -> bool:
    """Trả về True nếu câu thuộc nhóm common knowledge không cần cite."""
    return any(p.search(sentence) for p in _COMMON_KNOWLEDGE_PATTERNS)

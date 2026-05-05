"""Load 00-Brain/*.md → BrainContext."""
from __future__ import annotations
import re
from pathlib import Path
from core.obsidian.frontmatter import parse as parse_frontmatter
from core.brain.schema import (
    Strategy, Product, Budget, BudgetLine, Headcount,
    LawReference, DecisionEntry, BrainContext,
)

class BrainReader:
    # Maps raw state strings from markdown to valid BusinessStage literals
    _STAGE_MAP: dict[str, str] = {
        "pre-seed": "pre-seed",
        "seed": "seed",
        "growth": "growth",
        "mature": "mature",
        "pivot": "pivot",
    }

    def __init__(self, vault_root: Path):
        self.vault = Path(vault_root)
        self.brain_dir = self.vault / "00-Brain"

    def load(self) -> BrainContext:
        if not self.brain_dir.exists():
            raise FileNotFoundError(f"Brain dir not found: {self.brain_dir}")
        return BrainContext(
            strategy=self._read_strategy(),
            products=self._read_products(),
            budget=self._read_budget(),
            headcount=self._read_headcount(),
            laws=self._read_laws(),
            decisions=self._read_decisions(),
            state=self._read_state(),
            glossary=self._read_glossary(),
        )

    # ------------------------------------------------------------------ helpers

    def _read_file(self, name: str) -> tuple[dict, str]:
        path = self.brain_dir / name
        if not path.exists():
            return {}, ""
        return parse_frontmatter(path.read_text(encoding="utf-8"))

    def _extract_section(self, body: str, heading: str) -> str:
        """Return content after `## heading` until next ## or EOF."""
        pattern = rf"##\s+{re.escape(heading)}\s*\n(.*?)(?=\n##\s|\Z)"
        m = re.search(pattern, body, re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else ""

    # ------------------------------------------------------------------ parsers

    def _read_strategy(self) -> Strategy:
        _, body = self._read_file("strategy.md")
        vision = self._extract_section(body, "Tầm nhìn") or "(chưa điền)"
        icp = self._extract_section(body, "Khách hàng mục tiêu (ICP)") or "(chưa điền)"
        return Strategy(vision=vision, icp=icp)

    def _read_products(self) -> list[Product]:
        _, body = self._read_file("products.md")
        # Parse markdown table rows: | CODE | Name | price | margin | status |
        rows = re.findall(
            r"\|\s*([A-Z][A-Z0-9]*)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*(\d+(?:\.\d+)?)\s*\|\s*(\w+)\s*\|",
            body,
        )
        return [
            Product(
                code=r[0],
                name=r[1].strip(),
                price_vnd=int(r[2]),
                margin_pct=float(r[3]),
                status=r[4],
            )
            for r in rows
        ]

    def _read_budget(self) -> Budget:
        _, body = self._read_file("budget.md")
        total_match = re.search(r"Tổng ngân sách:\s*([\d_,.]+)", body)
        total = int(re.sub(r"[_,.]", "", total_match.group(1))) if total_match else 0
        return Budget(total_year_vnd=total)

    def _read_headcount(self) -> Headcount:
        _, body = self._read_file("headcount.md")
        depts = re.findall(r"^-\s+(\d{2}-[\w-]+)", body, re.MULTILINE)
        return Headcount(active_departments=depts)

    def _read_laws(self) -> list[LawReference]:
        _, body = self._read_file("laws.md")
        rows = re.findall(r"-\s+(.+?)\s*\((\d+/\d+/\w+)\)", body)
        return [LawReference(name=r[0], code=r[1]) for r in rows]

    def _read_decisions(self) -> list[DecisionEntry]:
        # TODO Phase 3: parse DecisionEntry blocks from decisions-log.md
        return []

    def _read_state(self) -> str:
        _, body = self._read_file("state.md")
        section = self._extract_section(body, "Giai đoạn")
        if not section:
            return "unknown"
        m = re.search(r"\[(\w[\w\s/-]+)\]", section)
        raw = m.group(1) if m else "unknown"
        return self._STAGE_MAP.get(raw.lower().strip(), "unknown")

    def _read_glossary(self) -> dict[str, str]:
        _, body = self._read_file("glossary.md")
        terms = re.findall(r"^-\s+\*\*(.+?)\*\*:\s*(.+)$", body, re.MULTILINE)
        return dict(terms)

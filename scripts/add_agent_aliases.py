"""One-time script: thêm aliases vào agent .md frontmatter.

Idempotent — chỉ thêm nếu chưa có.
aliases = [name_vn, id (English ID làm alias để search nhanh)]
"""
from __future__ import annotations
from pathlib import Path

from core.obsidian.frontmatter import parse as parse_frontmatter

import yaml


REPO = Path(__file__).parent.parent


# Agent ID → list aliases tiếng Anh quen dùng (ngoài name_vn)
EXTRA_AGENT_ALIASES: dict[str, list[str]] = {
    "cfo": ["CFO"],
    "ceo": ["CEO"],
    "cmo": ["CMO"],
    "cto": ["CTO"],
    "coo": ["COO"],
    "hr-manager": ["HR Manager", "HRBP"],
    "tech-lead": ["Tech Lead", "TL"],
    "product-manager": ["Product Manager", "PM"],
    "sales-lead": ["Sales Lead"],
    "growth-strategist": ["Growth", "Growth Lead"],
    "data-analyst": ["DA", "Data Analyst"],
    "data-scientist": ["DS", "Data Scientist"],
    "head-chef": ["Bếp trưởng", "Chef"],
    "ads-specialist": ["Ads", "Ads Specialist"],
    "seo-specialist": ["SEO", "SEO Specialist"],
}


def _format_aliases_yaml(aliases: list[str]) -> str:
    """Render YAML inline list, an toàn dấu tiếng Việt."""
    return yaml.safe_dump(
        {"aliases": aliases},
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).strip()


def _process(md_path: Path) -> str:
    text = md_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    if "aliases" in fm:
        return "skipped"

    name_vn = fm.get("name_vn", "")
    agent_id = fm.get("id", "")
    if not name_vn:
        return f"no-name_vn:{md_path.name}"

    aliases: list[str] = [name_vn]
    extra = EXTRA_AGENT_ALIASES.get(agent_id, [])
    for a in extra:
        if a not in aliases:
            aliases.append(a)

    fm["aliases"] = aliases

    # Reserialize frontmatter giữ thứ tự cũ
    new_fm = yaml.safe_dump(
        fm, allow_unicode=True, sort_keys=False, default_flow_style=False, width=120
    ).strip()
    new_text = f"---\n{new_fm}\n---\n\n{body.lstrip()}"
    md_path.write_text(new_text, encoding="utf-8")
    return "updated"


def main() -> None:
    targets: list[Path] = []
    targets += list((REPO / "departments").glob("*/agents/*.md"))
    targets += list((REPO / "packs").glob("*/departments/*/agents/*.md"))

    counts = {"updated": 0, "skipped": 0, "warn": 0}
    for p in targets:
        result = _process(p)
        if result == "updated":
            counts["updated"] += 1
            print(f"  [OK] {p.relative_to(REPO)}")
        elif result == "skipped":
            counts["skipped"] += 1
        else:
            counts["warn"] += 1
            print(f"  [WARN] {result}")

    print(
        f"\nTotal: {counts['updated']} updated, "
        f"{counts['skipped']} skipped, {counts['warn']} warn"
    )


if __name__ == "__main__":
    main()

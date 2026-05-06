"""Wikilink generator — tạo Brain hub + Department hub + cross-link agents.

Idempotent: chạy lại không phá file đã có. Append `## Liên kết` chỉ khi marker chưa có.
"""
from __future__ import annotations
from pathlib import Path

import yaml


LINK_MARKER = "## Liên kết"


def generate_wikilinks(vault: Path) -> dict:
    """Tạo index.md hub + thêm wikilinks vào agent files.

    Returns:
        dict với số file đã write/update.
    """
    vault = Path(vault)
    brain = vault / "00-Brain"
    depts_root = vault / "01-Departments"

    summary = {"brain_hub": False, "dept_hubs": 0, "agents_linked": 0}

    if not brain.exists() or not depts_root.exists():
        return summary

    brain_stems = sorted(
        f.stem for f in brain.glob("*.md") if f.stem != "index"
    )
    dept_dirs = sorted(
        d for d in depts_root.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )

    summary["brain_hub"] = _write_brain_hub(brain, brain_stems, dept_dirs)

    for d in dept_dirs:
        meta = _read_dept_meta(d)
        if meta is None:
            continue
        if _write_dept_hub(d, meta, brain_stems):
            summary["dept_hubs"] += 1
        summary["agents_linked"] += _link_agents(d, meta, brain_stems)

    return summary


def _write_brain_hub(
    brain: Path, brain_stems: list[str], dept_dirs: list[Path]
) -> bool:
    target = brain / "index.md"
    if target.exists():
        return False
    lines = [
        "# 🧠 Brain — Trung tâm tri thức",
        "",
        "Hub điều hướng toàn bộ Brain files và 12+ phòng ban.",
        "",
        "## Brain Files",
        "",
    ]
    lines += [f"- [[{s}]]" for s in brain_stems]
    lines += ["", "## Departments", ""]
    for d in dept_dirs:
        meta = _read_dept_meta(d)
        label = meta.get("name_vn", d.name) if meta else d.name
        lines.append(f"- [[01-Departments/{d.name}/index|{d.name} — {label}]]")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def _write_dept_hub(d: Path, meta: dict, brain_stems: list[str]) -> bool:
    target = d / "index.md"
    if target.exists():
        return False
    name_vn = meta.get("name_vn", d.name)
    agents = meta.get("agents", []) or []
    depends_on = meta.get("depends_on", []) or []

    lines = [
        f"# {d.name} — {name_vn}",
        "",
        "← [[../../00-Brain/index|🧠 Brain Hub]]",
        "",
        "## Agents",
        "",
    ]
    lines += [f"- [[{a}]]" for a in agents]
    lines += ["", "## Brain References", ""]
    lines += [f"- [[{s}]]" for s in brain_stems]
    if depends_on:
        lines += ["", "## Phòng ban liên quan", ""]
        lines += [f"- [[../{dep}/index|{dep}]]" for dep in depends_on]

    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def _link_agents(d: Path, meta: dict, brain_stems: list[str]) -> int:
    agents_dir = d / "agents"
    if not agents_dir.exists():
        return 0
    name_vn = meta.get("name_vn", d.name)
    key_refs = [s for s in ("strategy", "laws", "state") if s in brain_stems]

    count = 0
    for agent_file in agents_dir.glob("*.md"):
        text = agent_file.read_text(encoding="utf-8")
        if LINK_MARKER in text:
            continue
        block = [
            "",
            LINK_MARKER,
            "",
            f"- Phòng ban: [[../index|{d.name} — {name_vn}]]",
            "- Brain Hub: [[../../../00-Brain/index|🧠 Brain]]",
        ]
        if key_refs:
            refs = " · ".join(f"[[{s}]]" for s in key_refs)
            block.append(f"- Refs: {refs}")
        agent_file.write_text(
            text.rstrip() + "\n" + "\n".join(block) + "\n",
            encoding="utf-8",
        )
        count += 1
    return count


def _read_dept_meta(d: Path) -> dict | None:
    yaml_path = d / "department.yaml"
    if not yaml_path.exists():
        return None
    try:
        return yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None

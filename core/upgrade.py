"""Upgrade existing vault — refresh agents/depts/templates, preserve user data.

Use case: User đã onboard vault từ phiên bản cũ. Khi plugin upgrade
(enriched prompts, aliases, ...), cần đẩy file mới vào vault hiện có
mà KHÔNG động đến dữ liệu CEO đã điền (Brain content, Tasks, Outputs).
"""
from __future__ import annotations
import shutil
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).parent.parent


# Brain files KHÔNG bao giờ ghi đè (CEO đã điền)
PRESERVE_BRAIN = True


def upgrade_vault(
    vault_path: Path | str,
    refresh_agents: bool = True,
    refresh_dept_yaml: bool = True,
    refresh_brain_aliases: bool = True,
    regenerate_hubs: bool = False,
) -> dict:
    """Refresh code-controlled files trong vault, giữ user data nguyên vẹn.

    Args:
        vault_path: Đường dẫn vault
        refresh_agents: Ghi đè agent .md files (lấy enriched prompts mới)
        refresh_dept_yaml: Ghi đè department.yaml (aliases_vn, routing_rules mới)
        refresh_brain_aliases: Thêm aliases vào Brain files (giữ nội dung body)
        regenerate_hubs: Xoá index.md cũ + tạo lại (mặc định KHÔNG vì user
                        có thể đã chỉnh manual)

    Returns:
        dict summary
    """
    vault = Path(vault_path).expanduser().resolve()
    if not vault.exists():
        return {"ok": False, "error": f"Vault not found: {vault}"}

    summary: dict = {
        "ok": True,
        "vault": str(vault),
        "agents_refreshed": 0,
        "dept_yaml_refreshed": 0,
        "brain_aliases_added": 0,
        "hubs_regenerated": False,
        "warnings": [],
    }

    # 1. Refresh agent .md files (overwrite, giữ structure)
    if refresh_agents:
        summary["agents_refreshed"] = _refresh_agents(vault)

    # 2. Refresh department.yaml
    if refresh_dept_yaml:
        summary["dept_yaml_refreshed"] = _refresh_dept_yaml(vault)

    # 3. Add aliases vào Brain files (idempotent, giữ body)
    if refresh_brain_aliases:
        summary["brain_aliases_added"] = _add_brain_aliases(vault)

    # 4. Regenerate hubs (nếu user yêu cầu)
    if regenerate_hubs:
        _delete_hubs(vault)
        from core.wikilinks import generate_wikilinks
        wl = generate_wikilinks(vault)
        summary["hubs_regenerated"] = True
        summary["wikilinks"] = wl
    else:
        # Vẫn chạy generator để link agent files mới (idempotent)
        from core.wikilinks import generate_wikilinks
        summary["wikilinks"] = generate_wikilinks(vault)

    return summary


def _refresh_agents(vault: Path) -> int:
    """Copy enriched agents từ source departments/ + packs/ vào vault."""
    count = 0
    src_root = REPO_ROOT / "departments"
    dst_root = vault / "01-Departments"

    if not dst_root.exists():
        return 0

    for src_dept in src_root.iterdir():
        if not src_dept.is_dir() or src_dept.name.startswith("_"):
            continue
        src_agents = src_dept / "agents"
        dst_agents = dst_root / src_dept.name / "agents"
        if not src_agents.exists() or not dst_agents.exists():
            continue
        for src_agent in src_agents.glob("*.md"):
            dst_agent = dst_agents / src_agent.name
            shutil.copy2(src_agent, dst_agent)
            count += 1

    # Packs: chỉ refresh nếu vault đã có pack đó
    packs_root = REPO_ROOT / "packs"
    if packs_root.exists():
        for pack_dir in packs_root.iterdir():
            if not pack_dir.is_dir():
                continue
            for src_dept in (pack_dir / "departments").glob("*"):
                if not src_dept.is_dir():
                    continue
                dst_dept = dst_root / src_dept.name
                if not dst_dept.exists():
                    continue
                src_agents = src_dept / "agents"
                dst_agents = dst_dept / "agents"
                if not src_agents.exists() or not dst_agents.exists():
                    continue
                for src_agent in src_agents.glob("*.md"):
                    shutil.copy2(src_agent, dst_agents / src_agent.name)
                    count += 1
    return count


def _refresh_dept_yaml(vault: Path) -> int:
    count = 0
    dst_root = vault / "01-Departments"
    if not dst_root.exists():
        return 0

    for src_yaml in (REPO_ROOT / "departments").glob("*/department.yaml"):
        dept_code = src_yaml.parent.name
        dst_yaml = dst_root / dept_code / "department.yaml"
        if dst_yaml.exists():
            shutil.copy2(src_yaml, dst_yaml)
            count += 1

    for src_yaml in (REPO_ROOT / "packs").glob("*/departments/*/department.yaml"):
        dept_code = src_yaml.parent.name
        dst_yaml = dst_root / dept_code / "department.yaml"
        if dst_yaml.exists():
            shutil.copy2(src_yaml, dst_yaml)
            count += 1
    return count


def _add_brain_aliases(vault: Path) -> int:
    """Inject aliases vào frontmatter Brain files. Giữ body nguyên vẹn."""
    from core.obsidian.frontmatter import parse as parse_frontmatter

    count = 0
    template_brain = REPO_ROOT / "vault-template" / "00-Brain"
    user_brain = vault / "00-Brain"
    if not template_brain.exists() or not user_brain.exists():
        return 0

    for tpl_file in template_brain.glob("*.md"):
        user_file = user_brain / tpl_file.name
        if not user_file.exists():
            continue
        # Parse template để lấy aliases mới
        tpl_fm, _ = parse_frontmatter(tpl_file.read_text(encoding="utf-8"))
        aliases = tpl_fm.get("aliases")
        if not aliases:
            continue
        # Parse user file, inject aliases nếu chưa có
        user_fm, user_body = parse_frontmatter(user_file.read_text(encoding="utf-8"))
        if "aliases" in user_fm:
            continue
        user_fm["aliases"] = aliases
        new_fm_yaml = yaml.safe_dump(
            user_fm,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        ).strip()
        new_text = f"---\n{new_fm_yaml}\n---\n\n{user_body.lstrip()}"
        user_file.write_text(new_text, encoding="utf-8")
        count += 1
    return count


def _delete_hubs(vault: Path) -> None:
    """Xoá index.md hubs để generator tạo lại."""
    brain_idx = vault / "00-Brain" / "index.md"
    if brain_idx.exists():
        brain_idx.unlink()
    depts_root = vault / "01-Departments"
    if depts_root.exists():
        for d in depts_root.iterdir():
            idx = d / "index.md"
            if idx.exists():
                idx.unlink()

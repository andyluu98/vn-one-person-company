"""Test core.upgrade — refresh vault preserving user data."""
from __future__ import annotations

from core.obsidian.frontmatter import parse as parse_frontmatter
from core.onboard import onboard_vault
from core.upgrade import upgrade_vault


def test_upgrade_refreshes_agents_keeps_brain_content(tmp_path):
    vault = tmp_path / "v"
    onboard_vault(vault_path=vault, packs=[], init_git=False)

    strategy_file = vault / "00-Brain" / "strategy.md"
    user_strategy = strategy_file.read_text(encoding="utf-8") + "\n\n## CEO Notes\nDữ liệu của tôi\n"
    strategy_file.write_text(user_strategy, encoding="utf-8")

    agent_file = vault / "01-Departments" / "03-finance" / "agents" / "cfo.md"
    agent_file.write_text("# Old stub\n", encoding="utf-8")

    result = upgrade_vault(vault_path=vault)

    assert result["ok"] is True
    assert result["agents_refreshed"] > 0
    assert "Dữ liệu của tôi" in strategy_file.read_text(encoding="utf-8")
    assert "Giám đốc Tài chính" in agent_file.read_text(encoding="utf-8")


def test_upgrade_injects_brain_aliases(tmp_path):
    vault = tmp_path / "v"
    onboard_vault(vault_path=vault, packs=[], init_git=False)

    laws_file = vault / "00-Brain" / "laws.md"
    text = laws_file.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    fm.pop("aliases", None)
    import yaml
    new_fm = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False).strip()
    laws_file.write_text(f"---\n{new_fm}\n---\n\n{body}", encoding="utf-8")

    fm_before, _ = parse_frontmatter(laws_file.read_text(encoding="utf-8"))
    assert "aliases" not in fm_before

    result = upgrade_vault(vault_path=vault, refresh_agents=False, refresh_dept_yaml=False)

    fm_after, _ = parse_frontmatter(laws_file.read_text(encoding="utf-8"))
    assert "aliases" in fm_after
    assert "Luật" in fm_after["aliases"]
    assert result["brain_aliases_added"] >= 1


def test_upgrade_regenerate_hubs_recreates_index(tmp_path):
    vault = tmp_path / "v"
    onboard_vault(vault_path=vault, packs=[], init_git=False)

    brain_idx = vault / "00-Brain" / "index.md"
    custom = "# CUSTOM HUB\n"
    brain_idx.write_text(custom, encoding="utf-8")

    result = upgrade_vault(vault_path=vault, regenerate_hubs=True)
    assert result["hubs_regenerated"] is True
    assert "🧠 Brain" in brain_idx.read_text(encoding="utf-8")


def test_upgrade_default_preserves_existing_hubs(tmp_path):
    vault = tmp_path / "v"
    onboard_vault(vault_path=vault, packs=[], init_git=False)

    brain_idx = vault / "00-Brain" / "index.md"
    custom = "# MY CUSTOM HUB\n"
    brain_idx.write_text(custom, encoding="utf-8")

    upgrade_vault(vault_path=vault, regenerate_hubs=False)
    assert brain_idx.read_text(encoding="utf-8") == custom


def test_upgrade_missing_vault_returns_error(tmp_path):
    result = upgrade_vault(vault_path=tmp_path / "nonexistent")
    assert result["ok"] is False
    assert "not found" in result["error"]


def test_onboarded_vault_has_aliases_in_brain(tmp_path):
    vault = tmp_path / "v"
    onboard_vault(vault_path=vault, packs=[], init_git=False)
    fm, _ = parse_frontmatter((vault / "00-Brain" / "laws.md").read_text(encoding="utf-8"))
    assert "aliases" in fm
    assert "Luật" in fm["aliases"]


def test_onboarded_dept_hub_has_aliases(tmp_path):
    vault = tmp_path / "v"
    onboard_vault(vault_path=vault, packs=[], init_git=False)
    hub = (vault / "01-Departments" / "03-finance" / "index.md").read_text(encoding="utf-8")
    assert "aliases:" in hub
    assert "Tài chính" in hub

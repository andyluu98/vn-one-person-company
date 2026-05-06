"""Test core.wikilinks — Brain hub + Dept hubs + agent cross-linking."""
from __future__ import annotations

from core.onboard import onboard_vault
from core.wikilinks import LINK_MARKER, generate_wikilinks


def _bootstrap(tmp_path, packs=None):
    vault = tmp_path / "v"
    onboard_vault(vault_path=vault, packs=packs or [], init_git=False)
    return vault


def test_onboard_creates_brain_hub(tmp_path):
    vault = _bootstrap(tmp_path)
    hub = vault / "00-Brain" / "index.md"
    assert hub.exists()
    text = hub.read_text(encoding="utf-8")
    # Links to all 8 Brain files
    for stem in ("strategy", "products", "budget", "headcount", "state", "laws"):
        assert f"[[{stem}]]" in text
    # Links to departments via path
    assert "[[01-Departments/01-governance/index" in text


def test_onboard_creates_dept_hub_with_agents_and_brain_refs(tmp_path):
    vault = _bootstrap(tmp_path)
    hub = vault / "01-Departments" / "01-governance" / "index.md"
    assert hub.exists()
    text = hub.read_text(encoding="utf-8")
    assert "[[../../00-Brain/index" in text
    assert "[[legal-officer]]" in text
    assert "[[compliance-checker]]" in text
    # Brain reference present
    assert "[[strategy]]" in text


def test_onboard_appends_wikilinks_to_agent_files(tmp_path):
    vault = _bootstrap(tmp_path)
    agent = vault / "01-Departments" / "01-governance" / "agents" / "legal-officer.md"
    text = agent.read_text(encoding="utf-8")
    assert LINK_MARKER in text
    assert "[[../index|" in text
    assert "[[../../../00-Brain/index" in text


def test_wikilinks_idempotent(tmp_path):
    """Re-run generate_wikilinks: agent files don't get duplicate Liên kết blocks."""
    vault = _bootstrap(tmp_path)
    agent = vault / "01-Departments" / "01-governance" / "agents" / "legal-officer.md"
    first = agent.read_text(encoding="utf-8")

    summary = generate_wikilinks(vault)
    # Second run: nothing new should be added
    assert summary == {"brain_hub": False, "dept_hubs": 0, "agents_linked": 0}

    second = agent.read_text(encoding="utf-8")
    assert first == second
    # Marker only appears once
    assert second.count(LINK_MARKER) == 1


def test_wikilinks_with_fnb_pack_covers_kitchen(tmp_path):
    vault = _bootstrap(tmp_path, packs=["fnb"])
    kitchen_hub = vault / "01-Departments" / "13-kitchen" / "index.md"
    assert kitchen_hub.exists()
    # Kitchen agents got linked
    agents_dir = vault / "01-Departments" / "13-kitchen" / "agents"
    if agents_dir.exists():
        for agent_md in agents_dir.glob("*.md"):
            assert LINK_MARKER in agent_md.read_text(encoding="utf-8")


def test_brain_hub_skipped_if_already_exists(tmp_path):
    vault = _bootstrap(tmp_path)
    hub = vault / "00-Brain" / "index.md"
    custom = "# Custom Brain Hub\n"
    hub.write_text(custom, encoding="utf-8")

    summary = generate_wikilinks(vault)
    assert summary["brain_hub"] is False
    assert hub.read_text(encoding="utf-8") == custom

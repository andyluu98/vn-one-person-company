"""Test core.onboard library — pure Python API (no subprocess)."""
from __future__ import annotations

from core.onboard import onboard_vault


def test_onboard_creates_minimal_vault(tmp_path):
    vault = tmp_path / "test-vault"
    result = onboard_vault(vault_path=vault, packs=[], init_git=False)

    assert result["ok"] is True
    assert (vault / "00-Brain" / "strategy.md").exists()
    assert (vault / "00-Templates-Custom" / "README.md").exists()
    assert (vault / "01-Departments").exists()
    assert (vault / "02-Tasks").exists()
    assert (vault / ".vncoderc").exists()
    # Git init disabled
    assert not (vault / ".git").exists()


def test_onboard_with_fnb_pack_installs_kitchen(tmp_path):
    vault = tmp_path / "v"
    result = onboard_vault(vault_path=vault, packs=["fnb"], init_git=False)

    assert "fnb" in result["packs"]
    assert (vault / "01-Departments" / "13-kitchen").exists()


def test_onboard_with_unknown_pack_warns(tmp_path):
    vault = tmp_path / "v"
    result = onboard_vault(
        vault_path=vault, packs=["nonexistent"], init_git=False
    )

    assert result["ok"] is True
    assert any("nonexistent" in w for w in result["warnings"])


def test_onboard_idempotent(tmp_path):
    """Re-running onboard on existing vault is safe."""
    vault = tmp_path / "v"
    onboard_vault(vault_path=vault, packs=[], init_git=False)
    result = onboard_vault(vault_path=vault, packs=[], init_git=False)

    assert result["ok"] is True

"""Test install_mcp — uses tmp_path to avoid touching real Claude Desktop config."""
import json
from pathlib import Path
import pytest
from core.install_mcp import install, uninstall, get_config_path, get_claude_code_config_path, install_for_target
from core.utils.config import save_vault_env


def test_get_config_path_returns_platform_specific(monkeypatch):
    """Path should differ by OS."""
    import platform
    p = get_config_path()
    assert "claude_desktop_config.json" in str(p).lower()
    sys = platform.system()
    if sys == "Windows":
        assert "Claude" in str(p)
    elif sys == "Darwin":
        assert "Library" in str(p)
    else:
        assert ".config" in str(p)


def test_install_creates_config_when_missing(tmp_path):
    cfg = tmp_path / "claude_desktop_config.json"
    result = install(config_path=cfg)

    assert result["ok"] is True
    assert cfg.exists()

    config = json.loads(cfg.read_text(encoding="utf-8"))
    assert "mcpServers" in config
    assert "vn-business-os" in config["mcpServers"]
    assert "command" in config["mcpServers"]["vn-business-os"]


def test_install_preserves_existing_servers(tmp_path):
    cfg = tmp_path / "claude_desktop_config.json"
    cfg.write_text(json.dumps({
        "mcpServers": {
            "other-server": {"command": "node", "args": ["/path/to/other.js"]}
        }
    }), encoding="utf-8")

    install(config_path=cfg)

    config = json.loads(cfg.read_text(encoding="utf-8"))
    assert "other-server" in config["mcpServers"]
    assert "vn-business-os" in config["mcpServers"]


def test_install_creates_backup(tmp_path):
    cfg = tmp_path / "claude_desktop_config.json"
    cfg.write_text('{"mcpServers": {}}', encoding="utf-8")

    result = install(config_path=cfg)
    backup_path = Path(result["backup"])
    assert backup_path.exists()
    assert backup_path.suffix == ".bak"


def test_install_idempotent(tmp_path):
    cfg = tmp_path / "claude_desktop_config.json"
    install(config_path=cfg)
    install(config_path=cfg)  # second run should not error

    config = json.loads(cfg.read_text(encoding="utf-8"))
    # Still only 1 vn-business-os entry (no duplicate)
    assert list(config["mcpServers"].keys()).count("vn-business-os") == 1


def test_install_handles_malformed_json(tmp_path):
    cfg = tmp_path / "claude_desktop_config.json"
    cfg.write_text("{ malformed json", encoding="utf-8")

    result = install(config_path=cfg)
    assert result["ok"] is False
    assert "malformed" in result["error"].lower()


def test_uninstall_removes_entry(tmp_path):
    cfg = tmp_path / "claude_desktop_config.json"
    install(config_path=cfg)

    result = uninstall(config_path=cfg)
    assert result["removed"] is True

    config = json.loads(cfg.read_text(encoding="utf-8"))
    assert "vn-business-os" not in config.get("mcpServers", {})


def test_uninstall_no_config_is_safe(tmp_path):
    cfg = tmp_path / "claude_desktop_config.json"
    result = uninstall(config_path=cfg)
    assert result["ok"] is True
    assert result["removed"] is False


def test_install_injects_env_from_vault(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    save_vault_env(vault, {"TAVILY_API_KEY": "test-key-123"})

    cfg = tmp_path / "claude_desktop_config.json"
    result = install(config_path=cfg, vault_path=vault)

    assert result["ok"] is True
    assert "TAVILY_API_KEY" in result["env_keys_injected"]

    config = json.loads(cfg.read_text(encoding="utf-8"))
    server = config["mcpServers"]["vn-business-os"]
    assert server["env"]["TAVILY_API_KEY"] == "test-key-123"


def test_install_no_vault_no_env_field(tmp_path):
    cfg = tmp_path / "claude_desktop_config.json"
    result = install(config_path=cfg)
    config = json.loads(cfg.read_text(encoding="utf-8"))
    server = config["mcpServers"]["vn-business-os"]
    assert "env" not in server
    assert result["env_keys_injected"] == []


def test_get_claude_code_config_path_returns_dot_claude_json():
    p = get_claude_code_config_path()
    assert p.name == ".claude.json"
    assert p.parent == Path.home()


def test_install_for_target_desktop_only(tmp_path, monkeypatch):
    desktop_cfg = tmp_path / "claude_desktop_config.json"
    cc_cfg = tmp_path / "dot_claude.json"
    monkeypatch.setattr("core.install_mcp.get_config_path", lambda: desktop_cfg)
    monkeypatch.setattr("core.install_mcp.get_claude_code_config_path", lambda: cc_cfg)

    results = install_for_target("desktop", vault_path=None)

    assert results["desktop"]["ok"] is True
    assert desktop_cfg.exists()
    assert not cc_cfg.exists()


def test_install_for_target_claude_code_only(tmp_path, monkeypatch):
    desktop_cfg = tmp_path / "claude_desktop_config.json"
    cc_cfg = tmp_path / "dot_claude.json"
    monkeypatch.setattr("core.install_mcp.get_config_path", lambda: desktop_cfg)
    monkeypatch.setattr("core.install_mcp.get_claude_code_config_path", lambda: cc_cfg)

    results = install_for_target("claude-code", vault_path=None)

    assert results["claude-code"]["ok"] is True
    assert cc_cfg.exists()
    assert not desktop_cfg.exists()


def test_install_for_target_both(tmp_path, monkeypatch):
    desktop_cfg = tmp_path / "claude_desktop_config.json"
    cc_cfg = tmp_path / "dot_claude.json"
    monkeypatch.setattr("core.install_mcp.get_config_path", lambda: desktop_cfg)
    monkeypatch.setattr("core.install_mcp.get_claude_code_config_path", lambda: cc_cfg)

    results = install_for_target("both", vault_path=None)

    assert results["desktop"]["ok"] is True
    assert results["claude-code"]["ok"] is True
    assert desktop_cfg.exists()
    assert cc_cfg.exists()


def test_install_for_target_claude_code_preserves_existing_keys(tmp_path, monkeypatch):
    cc_cfg = tmp_path / "dot_claude.json"
    cc_cfg.write_text(json.dumps({"theme": "dark", "mcpServers": {}}), encoding="utf-8")
    monkeypatch.setattr("core.install_mcp.get_claude_code_config_path", lambda: cc_cfg)

    install_for_target("claude-code", vault_path=None)

    config = json.loads(cc_cfg.read_text(encoding="utf-8"))
    assert config["theme"] == "dark"
    assert "vn-business-os" in config["mcpServers"]


def test_install_for_target_invalid_target_raises():
    with pytest.raises(ValueError, match="target must be"):
        install_for_target("invalid", vault_path=None)


def test_install_for_target_both_partial_failure(tmp_path, monkeypatch):
    """If one target raises, other still succeeds and error is captured in result."""
    desktop_cfg = tmp_path / "claude_desktop_config.json"
    monkeypatch.setattr("core.install_mcp.get_config_path", lambda: desktop_cfg)

    cc_cfg = tmp_path / "dot_claude.json"
    monkeypatch.setattr("core.install_mcp.get_claude_code_config_path", lambda: cc_cfg)

    # Patch install to raise only when called with the claude-code config path
    original_install = install

    def install_with_failure(config_path, vault_path=None, **kwargs):
        if config_path == cc_cfg:
            raise OSError("simulated write failure")
        return original_install(config_path=config_path, vault_path=vault_path, **kwargs)

    monkeypatch.setattr("core.install_mcp.install", install_with_failure)

    results = install_for_target("both", vault_path=None)

    assert results["desktop"]["ok"] is True
    assert results["claude-code"]["ok"] is False
    assert "error" in results["claude-code"]
    assert "simulated write failure" in results["claude-code"]["error"]

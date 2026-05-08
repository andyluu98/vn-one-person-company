"""Test CLI install-mcp --target flag."""
import json
from click.testing import CliRunner
from core.cli import main


def test_install_mcp_default_target_is_both(tmp_path, monkeypatch):
    desktop_cfg = tmp_path / "desktop.json"
    cc_cfg = tmp_path / "cc.json"
    monkeypatch.setattr("core.install_mcp.get_config_path", lambda: desktop_cfg)
    monkeypatch.setattr("core.install_mcp.get_claude_code_config_path", lambda: cc_cfg)

    runner = CliRunner()
    result = runner.invoke(main, ["install-mcp"])

    assert result.exit_code == 0, result.output
    assert desktop_cfg.exists()
    assert cc_cfg.exists()


def test_install_mcp_target_claude_code(tmp_path, monkeypatch):
    desktop_cfg = tmp_path / "desktop.json"
    cc_cfg = tmp_path / "cc.json"
    monkeypatch.setattr("core.install_mcp.get_config_path", lambda: desktop_cfg)
    monkeypatch.setattr("core.install_mcp.get_claude_code_config_path", lambda: cc_cfg)

    runner = CliRunner()
    result = runner.invoke(main, ["install-mcp", "--target", "claude-code"])

    assert result.exit_code == 0, result.output
    assert cc_cfg.exists()
    assert not desktop_cfg.exists()
    assert "Claude Code" in result.output


def test_install_mcp_target_desktop(tmp_path, monkeypatch):
    desktop_cfg = tmp_path / "desktop.json"
    cc_cfg = tmp_path / "cc.json"
    monkeypatch.setattr("core.install_mcp.get_config_path", lambda: desktop_cfg)
    monkeypatch.setattr("core.install_mcp.get_claude_code_config_path", lambda: cc_cfg)

    runner = CliRunner()
    result = runner.invoke(main, ["install-mcp", "--target", "desktop"])

    assert result.exit_code == 0, result.output
    assert desktop_cfg.exists()
    assert not cc_cfg.exists()
    assert "Claude Desktop" in result.output


def test_install_mcp_target_both_shows_both_paths(tmp_path, monkeypatch):
    desktop_cfg = tmp_path / "desktop.json"
    cc_cfg = tmp_path / "cc.json"
    monkeypatch.setattr("core.install_mcp.get_config_path", lambda: desktop_cfg)
    monkeypatch.setattr("core.install_mcp.get_claude_code_config_path", lambda: cc_cfg)

    runner = CliRunner()
    result = runner.invoke(main, ["install-mcp", "--target", "both"])

    assert result.exit_code == 0, result.output
    assert "Claude Desktop" in result.output
    assert "Claude Code" in result.output

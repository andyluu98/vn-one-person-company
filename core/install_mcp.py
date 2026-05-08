"""Install vn-business-os as MCP server in Claude Desktop config.

Cross-platform path detection:
- Windows: %APPDATA%\\Claude\\claude_desktop_config.json
- macOS:   ~/Library/Application Support/Claude/claude_desktop_config.json
- Linux:   ~/.config/Claude/claude_desktop_config.json
"""
from __future__ import annotations
import json
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Optional


def get_config_path() -> Path:
    """Return claude_desktop_config.json path for current OS."""
    system = platform.system()
    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise RuntimeError("APPDATA env var not set")
        return Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def get_server_command() -> tuple[str, list[str]]:
    """Return (command, args) for launching the MCP server.

    Prefer the installed entry point `vn-os-mcp`. Fallback to python -m core.mcp_server.
    """
    vn_mcp = shutil.which("vn-os-mcp")
    if vn_mcp:
        return vn_mcp, []
    # Fallback — needs python in PATH
    return sys.executable, ["-m", "core.mcp_server"]


def get_claude_code_config_path() -> Path:
    """Return ~/.claude.json — global Claude Code MCP config (cross-platform)."""
    return Path.home() / ".claude.json"


def install_for_target(
    target: str = "both",
    vault_path: Optional[Path] = None,
) -> dict:
    """Install MCP server for target: 'desktop', 'claude-code', or 'both'.

    Returns dict with target name as key, install() result as value.
    Each result has 'ok' bool; on exception, {'ok': False, 'error': str(e)}.
    Raises ValueError if target is invalid.
    """
    valid = {"desktop", "claude-code", "both"}
    if target not in valid:
        raise ValueError(f"target must be one of {valid}, got {target!r}")

    results: dict = {}
    if target in ("desktop", "both"):
        try:
            results["desktop"] = install(
                config_path=get_config_path(),
                vault_path=vault_path,
            )
        except Exception as e:
            results["desktop"] = {"ok": False, "error": str(e)}
    if target in ("claude-code", "both"):
        try:
            results["claude-code"] = install(
                config_path=get_claude_code_config_path(),
                vault_path=vault_path,
            )
        except Exception as e:
            results["claude-code"] = {"ok": False, "error": str(e)}
    return results


def install(
    config_path: Optional[Path] = None,
    server_name: str = "vn-business-os",
    vault_path: Optional[Path] = None,
) -> dict:
    """Install (or update) MCP server entry. Returns summary dict.

    Args:
        config_path: Override path to claude_desktop_config.json
        server_name: Name in mcpServers dict
        vault_path: Optional vault để load <vault>/.env (TAVILY_API_KEY, ...)
                    và inject vào `env` của mcpServers entry. Cho phép Claude
                    Desktop launch MCP server với credentials sẵn — search tools
                    không skip silently.
    """
    cfg_path = config_path or get_config_path()
    cfg_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing config (or empty)
    if cfg_path.exists():
        try:
            config = json.loads(cfg_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"ok": False, "error": f"Existing config at {cfg_path} is malformed JSON. Backup + manual fix needed."}
    else:
        config = {}

    # Backup existing config
    backup = None
    if cfg_path.exists():
        backup = cfg_path.with_suffix(".json.bak")
        shutil.copy(cfg_path, backup)

    # Build server entry
    command, args = get_server_command()
    server_entry: dict = {"command": command}
    if args:
        server_entry["args"] = args

    # Inject env từ vault/.env nếu có vault_path
    env_keys_injected: list[str] = []
    if vault_path:
        from core.utils.config import load_vault_env
        keys = load_vault_env(Path(vault_path))
        if keys:
            server_entry["env"] = {k: v for k, v in keys.items() if v}
            env_keys_injected = list(server_entry["env"].keys())

    # Insert into mcpServers
    config.setdefault("mcpServers", {})
    config["mcpServers"][server_name] = server_entry

    # Write back (pretty)
    cfg_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "ok": True,
        "config_path": str(cfg_path),
        "backup": str(backup) if backup else None,
        "server_name": server_name,
        "command": command,
        "args": args,
        "env_keys_injected": env_keys_injected,
    }


def uninstall(config_path: Optional[Path] = None, server_name: str = "vn-business-os") -> dict:
    """Remove MCP server entry. Idempotent."""
    cfg_path = config_path or get_config_path()
    if not cfg_path.exists():
        return {"ok": True, "removed": False, "reason": "config not found"}

    config = json.loads(cfg_path.read_text(encoding="utf-8"))
    servers = config.get("mcpServers", {})

    if server_name not in servers:
        return {"ok": True, "removed": False, "reason": "server not in config"}

    del servers[server_name]
    cfg_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"ok": True, "removed": True, "config_path": str(cfg_path)}

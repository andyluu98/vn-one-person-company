# Design: Claude Code MCP Support

**Date:** 2026-05-08  
**Status:** Approved

## Problem

`vn-os install-mcp` chỉ write vào Claude Desktop config (`claude_desktop_config.json`). Claude Code dùng config riêng (`~/.claude.json`). CEO muốn gõ brief trong Claude Code terminal — tool `vn_run`, `vn_meeting`... phải available qua MCP.

## Solution

Extend `install_mcp.py` + `cli.py` để support Claude Code global MCP config. MCP server không đổi gì — chạy giống nhau trên cả hai host.

## Architecture

Chỉ 2 files thay đổi:

| File | Thay đổi |
|------|----------|
| `core/install_mcp.py` | Thêm `get_claude_code_config_path()` + `write_claude_code_config()` + rename `install_mcp()` → `write_desktop_config()` |
| `core/cli.py` | Thêm `--target [desktop\|claude-code\|both]` vào `install-mcp` command (default: `both`) |
| `adapters/claude-code/install.sh` | Update gọi `vn-os install-mcp --target claude-code` |

## Config Paths

| Host | Config file |
|------|------------|
| Claude Desktop | `%APPDATA%/Claude/claude_desktop_config.json` (Windows) |
| Claude Code | `~/.claude.json` (cross-platform) |

Cả hai dùng cùng key `mcpServers` và cùng JSON format — code tái sử dụng `get_server_command()`.

## `install_mcp.py` Changes

```python
def get_claude_code_config_path() -> Path:
    return Path.home() / ".claude.json"

def write_claude_code_config(vault_root: Path | None = None) -> Path:
    config_path = get_claude_code_config_path()
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    config.setdefault("mcpServers", {})
    command, args = get_server_command()
    entry = {"command": command, "args": args}
    if vault_root:
        entry["env"] = {"VN_OS_VAULT": str(vault_root)}
    config["mcpServers"]["vn-business-os"] = entry
    config_path.write_text(json.dumps(config, indent=2))
    return config_path

def write_desktop_config(vault_root: Path | None = None) -> Path:
    # rename của install_mcp() cũ — logic không đổi
    ...

def install_mcp(target: str = "both", vault_root: Path | None = None) -> None:
    if target in ("desktop", "both"):
        path = write_desktop_config(vault_root)
        print(f"✓ Claude Desktop: {path}")
    if target in ("claude-code", "both"):
        path = write_claude_code_config(vault_root)
        print(f"✓ Claude Code:    {path}")
    print("→ Restart Claude Desktop + Claude Code để áp dụng.")
```

## CLI Usage

```bash
vn-os install-mcp                                       # default: both
vn-os install-mcp --target claude-code
vn-os install-mcp --target desktop
vn-os install-mcp --target both --vault F:/work/xyz-vault
```

## Error Handling

- Config file không tồn tại → tạo mới với `{}`
- `mcpServers` key chưa có → `setdefault`
- `vn-os-mcp` không trên PATH → fallback `python -m core.mcp_server` (logic hiện tại)

## Testing

- Unit test `write_claude_code_config()`: mock `Path.home()`, assert JSON output đúng
- Unit test merge: config đã có `mcpServers` khác → không overwrite entry khác
- Unit test `--target` flag: assert đúng function được gọi

## Out of Scope

- MCP sampling provider không thay đổi
- Skill `adapters/claude-code/skill.md` đã đúng, không cần sửa nội dung
- Claude Code per-project `.mcp.json` (dùng global là đủ)

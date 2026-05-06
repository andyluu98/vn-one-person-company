# Claude Code / Desktop Skill Adapter

Skill cho Claude Code (CLI / desktop). Sau khi cài, CEO gõ tiếng Việt tự nhiên về task DN, skill tự active và call MCP tools.

## Prerequisites

```bash
pip install vn-business-os
vn-os install-mcp        # auto-edit claude_desktop_config.json
# Restart Claude Desktop
```

## Install skill

```bash
bash adapters/claude-code/install.sh
```

## Verify

Trong Claude Desktop / Code session, gõ:
> Tạo chiến dịch QC nhắm khách thu nhập 50tr+

Claude sẽ:
1. Detect skill `vn-business-os` active
2. Call `vn_status(vault)` verify Brain
3. Call `vn_run(brief, vault)` → PAUSE clarification
4. Đọc `03-clarification.md`, hỏi CEO trả lời
5. Continue qua các stages

## Lưu ý

- Cần subscription Claude Pro hoặc Max (Free tier rate limit quá thấp)
- 1 task COMPLEX ≈ 30-40 sampling calls
- Không cần ANTHROPIC_API_KEY (LLM thinking qua subscription)

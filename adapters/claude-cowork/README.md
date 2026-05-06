# Claude Cowork Plugin Adapter

Plugin cho Claude Cowork. Bundle skill `vn-business-os` thành `.plugin` package có thể install vào Cowork workspace.

## Prerequisites

```bash
pip install vn-business-os
vn-os install-mcp        # auto-edit Claude config (Desktop / Code)
# Restart Claude
```

## Build plugin

```bash
bash adapters/claude-cowork/build-plugin.sh
```

Output: `vn-business-os.plugin` ready to install vào Cowork workspace.

## Verify

Sau khi install plugin vào Cowork, gõ tiếng Việt tự nhiên về task DN:
> Tạo chiến dịch QC nhắm khách thu nhập 50tr+

Cowork sẽ activate skill `vn-business-os` và call 7 MCP tools (`vn_status`, `vn_run`, `vn_resume`, `vn_meeting`, `vn_approve`, `vn_execute`, `vn_onboard`).

## Lưu ý

- Cần subscription Claude Pro hoặc Max (Free tier rate limit quá thấp)
- 1 task COMPLEX ≈ 30-40 sampling calls
- Không cần ANTHROPIC_API_KEY (LLM thinking qua subscription)

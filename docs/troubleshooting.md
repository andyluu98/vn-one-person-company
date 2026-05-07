# Troubleshooting — VN One Person Company

Lỗi thường gặp + cách fix.

---

## Cài đặt

### `vn-os: command not found`
- Quên active venv: `.venv\Scripts\activate` (Win) hoặc `source .venv/bin/activate`
- Quên `pip install -e .` (chú ý dấu `.` cuối)
- Verify: `which vn-os` (Linux/Mac) / `where vn-os` (Win)

### `pip install -e .` fail với "Microsoft Visual C++ 14.0 required"
- Cần Build Tools cho Windows: [vs_buildtools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Hoặc: dùng pre-built wheels: `pip install -e . --only-binary :all:`

### Python version
```powershell
python --version
# Nếu < 3.11: cài Python 3.11+ từ python.org
```

---

## MCP Server

### Claude Desktop không thấy `vn_run`/`vn_meeting`/...
1. Verify config:
   ```powershell
   # Windows
   type "$env:APPDATA\Claude\claude_desktop_config.json"
   ```
2. Phải có entry `"vn-business-os": {"command": "vn-os-mcp"}`
3. Restart Claude Desktop **HOÀN TOÀN** (đóng từ system tray, không chỉ close window)
4. Check Claude Desktop logs:
   - Windows: `%APPDATA%\Claude\logs\mcp*.log`
   - macOS: `~/Library/Logs/Claude/mcp*.log`

### MCP server crash on startup
Logs hiển thị Python error → thường là missing dep:
```powershell
# Re-install
pip install -e .
# Test direct
vn-os-mcp
# Phải hang im (đợi MCP messages). Ctrl+C để thoát.
```

### `'dict' object has no attribute 'content_as_list'`
Đã fix trong commit `d4c9a33`. Cập nhật repo:
```powershell
git pull
pip install -e .
# Restart Claude Desktop
```

### `vn_run: 'NoneType' object has no attribute 'session'`
MCP context không được inject. Tools đang chạy ngoài MCP session (vd qua CLI `vn-os run` không hỗ trợ MCP sampling). Dùng MCP tool trong Claude Desktop chat.

---

## Vault setup

### `vn_onboard` timeout (~4 phút)
Đã fix bằng cách bỏ subprocess (commit `ad21206`). Cập nhật repo + restart Claude Desktop.

### Vault path có dấu cách / Unicode
Plugin support nhưng nên tránh. Khuyến nghị:
- ✓ `F:/work/xyz-vault`
- ✓ `C:/Users/admin/vaults/abc`
- ✗ `F:/Tài liệu/vault` (có thể edge case Git/PowerShell)
- ✗ `C:/My Documents/vault` (có space)

### `Vault not found`
- Check đường dẫn thật sự tồn tại: `Test-Path "F:\work\xyz-vault"`
- Plugin expand `~` (home dir) nhưng KHÔNG expand env vars `%USERPROFILE%`

---

## Search/Research

### `tools_skipped: [web_search, vn_law_search, ...]`
Thiếu `TAVILY_API_KEY`. Fix:
```powershell
# Chat: nhập key qua vn_onboard
# HOẶC edit file thủ công:
echo "TAVILY_API_KEY=tvly-xxx" >> "F:/work/xyz-vault/.env"

# Re-install MCP để inject env
vn-os install-mcp --vault "F:/work/xyz-vault"
# Restart Claude Desktop
```

### `Tavily 401 Unauthorized`
Key không hợp lệ hoặc hết hạn. Tạo key mới tại [tavily.com](https://tavily.com/dashboard).

### `Tavily 429 Too Many Requests`
Hết free tier (1000 req/tháng). Options:
- Đợi tháng sau
- Upgrade Tavily plan
- Tạm bật `meeting.use_checkpointer: true` để tránh re-research khi crash

### Search trả về kết quả sai/cũ
Tool cache `<vault>/.cache/tool_cache.db` lưu 24h. Force refresh:
```powershell
Remove-Item "F:/work/xyz-vault/.cache/tool_cache.db"
```

---

## Meeting / Debate

### Meeting hang vô tận
- Check `tools_skipped` trong `vn_status` — nếu 4 Tavily tools skip + brief yêu cầu nhiều research → LLM có thể loop. Bật ít nhất 1 tool.
- LLM rate limit → đã có retry trong P1.3. Nếu vẫn hang → restart Claude Desktop.

### Decision report quá ngắn / generic
- Brain rỗng / placeholder text → meeting không có data thật để debate
- Fix: điền `00-Brain/strategy.md`, `products.md`, `state.md` đầy đủ

### Decision report có cảnh báo "Claims thiếu trích nguồn"
Đây là **feature** (P1.8), không phải bug. CEO review claims đó:
- Nếu claim đúng → bổ sung citation thủ công vào report
- Nếu claim không chắc → CEO ko approve, rerun task với thêm clarification

### `07-decision-report.md` lưu nhưng `.docx` không được render
- Check `08-execution-plan.md` có bảng `## Mau tai lieu can tao` không
- Nếu không → execution plan thiếu, plugin LLM fallback extract template names
- Verify TemplateResolver tìm được template: tên trong bảng phải match `templates-vn/<dept>/<name>.docx` hoặc `<vault>/00-Templates-Custom/<dept>/<name>.docx`

### Tool research luôn trả "skipped" dù có key
- Verify env injection:
  ```powershell
  type "$env:APPDATA\Claude\claude_desktop_config.json" | Select-String "TAVILY"
  ```
- Phải thấy `"TAVILY_API_KEY": "tvly-..."` trong section `env:` của vn-business-os
- Nếu không → re-run `vn-os install-mcp --vault <path>`

---

## Git / Vault sync

### `Git commit failed (Stop 1): ...`
Check `<vault>/.vn-business-os.log`:
```powershell
Get-Content "F:/work/xyz-vault/.vn-business-os.log" -Tail 20
```

Common causes:
- Git chưa init: `cd <vault>; git init`
- Merge conflict do CEO edit + plugin edit cùng file → resolve thủ công
- Permission denied: vault folder read-only → fix permissions

### `<vault>/.env` bị commit lên git
**NGHIÊM TRỌNG.** Fix ngay:
```powershell
cd <vault>
git rm --cached .env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "fix: gitignore .env"
# Rotate keys ngay (Tavily, Anthropic, ...) vì đã expose
```

### Push lên GitHub fail (private repo của CEO)
Plugin chỉ commit local. Push do CEO tự làm:
```powershell
cd <vault>
git remote add origin <your-private-repo-url>
git push -u origin main
```

---

## Performance / Cost

### Cost LLM cao (>$2/task)
- Reduce `meeting.max_debate_rounds: 1`
- Reduce `meeting.max_perspective_rounds: 0` (skip perspective phase)
- `translator_mode: off` thay vì `final_only` (skip translator LLM call)

### Meeting chạy chậm (>15 phút)
- Brain quá lớn → P2.7 đã filter per agent, nhưng nếu Brain >20K chars → consider chia file (`strategy-1.md`, `strategy-2.md`)
- Research tool chậm → reduce queries trong ToolRouter

---

## Plugin upgrade

### Có version mới của plugin
```powershell
cd <plugin-dir>
git pull
pip install -e .

# Refresh existing vault với prompts mới
# Trong Claude chat:
# "Upgrade vault F:/work/xyz-vault"
```

`vn_upgrade` chỉ động:
- Agent .md (refresh prompts)
- Department.yaml (aliases mới)
- Brain frontmatter (inject aliases)

KHÔNG động:
- Brain content (CEO data)
- Tasks/Outputs

### Sau upgrade, re-test
```powershell
python -m pytest tests/ -q
# Phải pass 261+
```

---

## Báo bug

Nếu lỗi không có ở đây, mở [GitHub issue](https://github.com/<owner>/<repo>/issues) với:
- Error message đầy đủ (redact API keys nếu có)
- `vn_status` output
- Plugin version (`git rev-parse HEAD`)
- Python version + OS
- Steps to reproduce

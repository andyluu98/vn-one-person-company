# Báo cáo Fix Lỗi P0 — 2026-05-07

> **Trả lời cho người dùng:** Đã rà soát toàn bộ repo + sửa 7 lỗi mức P0. Tests 180 pass. Commit `a3a7638`.

---

## Lỗi người dùng nêu — đã xác minh

### ❌ "Lúc thiết lập vault không hỏi Tavily/Brave API key"
**ĐÚNG.** `core/onboard.py` cũ không có chỗ nhập API key. Cấu hình `.vncoderc` không có trường lưu key. Trình hướng dẫn CLI `scripts/onboard.py` chỉ hỏi pack + BYOT.

→ **Đã sửa:**
- Hàm `onboard_vault(api_keys={...})` thêm tham số mới
- Trình hướng dẫn CLI hỏi `TAVILY_API_KEY` + `ANTHROPIC_API_KEY` (nhập kín, ẩn ký tự)
- Công cụ MCP `vn_onboard` thêm 4 tham số: `tavily_api_key`, `anthropic_api_key`, `google_api_key`, `openai_api_key`
- Lưu vào `<vault>/.env` (tự động thêm `.env` vào `.gitignore`)

### ❌ "Chức năng tìm kiếm không hoạt động"
**ĐÚNG MỘT PHẦN:**
- Tìm kiếm ĐÃ được nối vào `vn_meeting` (gọi `ResearchPhase.run()` trước khi họp)
- NHƯNG 4 công cụ Tavily (web/luật/địa phương/đối thủ) gặp lỗi xác thực khi không có key → bị nuốt thầm lặng → cuộc họp tiếp tục với findings rỗng → vi phạm RULE 5 trong câm lặng
- 2 công cụ không cần key (`industry_benchmark`, `tax_calculator`) vẫn chạy

→ **Đã sửa:**
- 4 công cụ Tavily có `is_available()` để kiểm tra
- Khi thiếu key: trả về `ToolResult(data={"skipped": True}, notes="Thiếu TAVILY_API_KEY...")` thay vì crash
- ToolRouter chỉ lập kế hoạch cho công cụ có credentials (không lãng phí token LLM)
- `vn_status` báo `tools_live` + `tools_skipped` để CEO biết trước khi chạy

---

## 15 lỗi phát hiện trong audit (chi tiết tại `audit-260507-repo-completeness-vn.md`)

### Mức P0 (7 lỗi) — ĐÃ SỬA trong commit này

| # | File | Lỗi | Cách sửa |
|---|---|---|---|
| 1 | `flow_controller.py:167` | `departments_root` trỏ về REPO thay vì vault → BYOT meeting hỏng | Đổi thành `vault.root / "01-Departments"` |
| 2 | `flow_controller.py:approve_decision` | Stub "(TODO Phase 6)" | Sinh kế hoạch thực thi thật bằng LLM, có bảng tasks/risks/KPIs/templates |
| 3 | `flow_controller.py:execute` | Stub README placeholder | Đọc bảng template → TemplateResolver → DocWriter render .docx/.xlsx → lưu vào `03-Outputs/` |
| 4 | 4 công cụ Tavily | Crash khi thiếu key, fail thầm lặng | `is_available()` + `skipped_result()` graceful |
| 5 | `core/onboard.py` | Không hỏi API key | Tham số `api_keys` mới + lưu vào `<vault>/.env` |
| 6 | `core/install_mcp.py` | Không bơm env vào mcpServers | Cờ `--vault` đọc `<vault>/.env` → bơm `env: {TAVILY_API_KEY: ...}` |
| 7 | `tool_router.py` | Lập kế hoạch cho công cụ không có credentials | Lọc qua `available_tools` |

### Mức P1 (5 lỗi) — Để dành cho phase tiếp theo

- `PerspectivesCollector` bỏ qua prompt enriched theo từng agent (vẫn dùng template chung)
- 12 thư mục phòng ban nhưng plan/router prompt nói "13 core" — lệch 1
- `MCPSamplingProvider` không retry/timeout khi rate limit
- LangGraph `checkpointer=False` hardcode → crash giữa cuộc họp không thể khôi phục
- `GitSync` nuốt exception thầm lặng

### Mức P2 (3 lỗi) — Hoàn thiện sau

- `vn_onboard` đa lượt qua MCP elicitation
- Router JSON-mode để parse deterministic
- `tool_cache.db` riêng từng vault (hiện đang `~/.vn-business-os/`)

---

## Files đã thay đổi (38 files, +11148 dòng)

### Code
- `core/utils/config.py` — `load_vault_env`, `save_vault_env`, `apply_vault_env_to_os`
- `core/tools/base_tool.py` — helper `is_available()` + `skipped_result()`
- `core/tools/{web_search,vn_law_search,vn_local_regulation,competitor_research}.py` — skip graceful
- `core/tools/tool_router.py` — lọc theo available_tools
- `core/orchestrator/research_phase.py` — `list_available_tools` / `list_skipped_tools`
- `core/orchestrator/flow_controller.py` — departments_root + approve_decision + execute (impl thật)
- `core/orchestrator/execution_planner.py` — MỚI (LLM sinh 08-execution-plan.md)
- `core/orchestrator/document_executor.py` — MỚI (DocWriter + TemplateResolver được nối)
- `core/onboard.py` — tham số api_keys
- `core/mcp_server.py` — vn_onboard 4 tham số key, vn_status báo tool availability, _make_fc tự nạp env
- `core/install_mcp.py` — bơm env theo vault_path
- `core/cli.py` — install-mcp cờ --vault
- `scripts/onboard.py` — hỏi API key tương tác (nhập ẩn)

### Tests (+34 mới)
- `tests/unit/test_env_and_tool_skip.py` — 11 tests
- `tests/unit/test_execution_planner.py` — 9 tests
- `tests/unit/test_document_executor.py` — 9 tests
- `tests/unit/test_install_mcp.py` — 2 mới (bơm env)
- `tests/e2e/test_b_campaign_high_income.py` — 4 mới + cập nhật mock

---

## Cách dùng (đã cập nhật)

### Thiết lập vault mới (qua Claude Desktop)
```
Trong chat: "Thiết lập vault cho công ty XYZ tại đường dẫn F:/.../my-company.
Cài pack F&B. Tavily API key của tôi: tvly-xxx"
```
→ Claude gọi `vn_onboard(vault=..., packs=["fnb"], tavily_api_key="tvly-xxx")`
→ Key được lưu vào `<vault>/.env`, `.gitignore` loại trừ file này

### Sau khi onboard, bơm env vào MCP server
**Bước quan trọng:** sau khi lưu key, phải cài lại MCP để Claude Desktop khởi chạy với env:
```bash
vn-os install-mcp --vault "F:/.../my-company"
```
→ Đọc `<vault>/.env` → bơm `env: {TAVILY_API_KEY: ...}` vào `claude_desktop_config.json`
→ Khởi động lại Claude Desktop

### Kiểm tra
Trong chat: "vn_status vault F:/.../my-company"
→ Trả về `tools_live: [web_search, vn_law_search, ...]` (nếu có key)
→ Hoặc `tools_skipped: [{name: web_search, reason: Missing TAVILY_API_KEY}]` nếu thiếu

---

## Tests

**Trước:** 146 passed + 1 skipped
**Sau:** 180 passed + 1 skipped (+34 mới, 0 hồi quy)

```
$ python -m pytest tests/ -q
180 passed, 1 skipped in 14.33s
```

---

## Ma trận Tuân thủ RULES (cập nhật sau fix)

| RULE | Trước | Sau |
|---|---|---|
| 1. Brain-first | ✓ | ✓ |
| 2. Domain-neutral | ✓ | ✓ |
| 3. Single source of truth | Một phần | ✓ (departments lấy từ vault) |
| 4. Ngôn ngữ thân thiện CEO | Một phần | Một phần (P1.6) |
| 5. Live research with citations | **DEGRADED** | ✓ (skip graceful + báo trạng thái) |
| 6. BYOT | **GÃY** | ✓ (cả meeting + execute đều tôn trọng vault) |

---

## Bước tiếp theo cho người dùng

1. **Khởi động lại Claude Desktop** để nạp MCP server mới (8 tools với fixes)
2. **Thử thiết lập vault mới** với cú pháp: "Thiết lập vault... TAVILY key của tôi là..."
3. **Cài lại MCP với --vault** để bơm env:
   ```
   vn-os install-mcp --vault "F:/đường-dẫn/đến/vault"
   ```
4. **Kiểm tra với vn_status** xem `tools_live` có bao nhiêu công cụ

## Còn lại (P1 + P2 — phase tiếp theo)

Xem `audit-260507-repo-completeness-vn.md` mục "Danh sách Fix Theo Ưu tiên". Có thể mở phase-07 để dọn nốt:
- Nối prompt theo từng agent vào PerspectivesCollector
- Giải quyết phòng ban thứ 13
- Retry/timeout trong MCPSamplingProvider
- Bật lại LangGraph checkpointer
- Onboard đa lượt qua MCP elicitation
- Bộ kiểm tra trích nguồn (citation validator)

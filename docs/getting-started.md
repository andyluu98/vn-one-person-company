# Getting Started — VN Business OS

Hướng dẫn từ đầu đến chạy được task đầu tiên. Khoảng **15-20 phút** nếu đã có Claude Desktop + Python 3.11+.

---

## Yêu cầu

| | |
|---|---|
| **Python** | 3.11+ |
| **Claude Desktop** | Bản mới nhất ([download](https://claude.ai/download)) — có subscription Pro/Team |
| **Obsidian** | (khuyến nghị) — để xem vault trực quan |
| **Git** | Bất kỳ version nào |
| **TAVILY_API_KEY** | (tùy chọn) — bật search luật/đối thủ. Free tier 1000 req/tháng tại [tavily.com](https://tavily.com) |
| **Anthropic API key** | **KHÔNG cần** — plugin dùng MCP sampling qua Claude Desktop subscription |

---

## Bước 1 — Cài đặt plugin

```powershell
git clone https://github.com/<owner>/<repo>.git vn-business-os
cd vn-business-os

python -m venv .venv
.venv\Scripts\activate                      # Windows
# source .venv/bin/activate                 # macOS/Linux

pip install -e .
```

Verify:
```powershell
vn-os --help
# Hiển thị: onboard, install-mcp, uninstall-mcp, ...
```

---

## Bước 2 — Cài MCP server vào Claude Desktop

```powershell
vn-os install-mcp
```

Output:
```
✓ Installed MCP server 'vn-business-os'
   Config: C:\Users\<you>\AppData\Roaming\Claude\claude_desktop_config.json
   Backup: ...claude_desktop_config.json.bak

Bước tiếp: Restart Claude Desktop để load MCP server.
```

**→ Đóng hoàn toàn Claude Desktop, mở lại.**

Verify trong Claude Desktop chat:
```
Liệt kê MCP tools có sẵn.
```

Phải thấy 8 tools: `vn_run`, `vn_resume`, `vn_meeting`, `vn_approve`, `vn_execute`, `vn_status`, `vn_onboard`, `vn_upgrade`.

---

## Bước 3 — Tạo vault cho công ty của bạn

Trong Claude Desktop chat:

```
Setup vault cho công ty XYZ tại đường dẫn:
F:\work\xyz-vault

Cài pack F&B (vì XYZ là chuỗi cafe).
TAVILY_API_KEY của tôi: tvly-xxx
```

Claude tự động gọi `vn_onboard(vault=..., packs=["fnb"], tavily_api_key="tvly-xxx")`.

Plugin sẽ:
1. Copy vault scaffold (8 Brain files + 12 phòng ban + 191 template)
2. Cài pack `fnb` (thêm phòng Bếp + An toàn thực phẩm)
3. Sinh wikilinks cho Obsidian graph view
4. Lưu key vào `<vault>/.env` (auto-add vào `.gitignore`)
5. Init Git private repo

Output mẫu:
```yaml
ok: true
vault: F:\work\xyz-vault
steps:
  - Copied scaffold to F:\work\xyz-vault
  - Installed core departments
  - Installed pack fnb
  - Saved 1 API key(s) → .env (TAVILY_API_KEY)
  - Wikilinks: brain_hub=True, dept_hubs=14, agents_linked=40
  - Git initialized
packs: [fnb]
next_steps:
  - Open <vault>/00-Brain/ and fill strategy.md, products.md, ...
```

---

## Bước 4 — Inject API key vào MCP server

**Bắt buộc khi onboard có TAVILY_API_KEY** — để Claude Desktop launch MCP với env.

```powershell
vn-os install-mcp --vault "F:\work\xyz-vault"
```

Output sẽ thêm:
```
   Env injected: TAVILY_API_KEY
```

**→ Restart Claude Desktop lần nữa.**

Verify trong chat:
```
vn_status vault F:\work\xyz-vault
```

Phải thấy:
```yaml
tools_live:
  - web_search
  - vn_law_search
  - vn_local_regulation
  - competitor_research
  - industry_benchmark
  - tax_calculator
tools_skipped: []
```

Nếu `tools_skipped` còn search tools → key chưa được inject. Re-run install-mcp.

---

## Bước 5 — Điền Brain (1 lần)

Mở `<vault>/` trong Obsidian. Mở `00-Brain/`:

| File | Điền gì |
|---|---|
| `strategy.md` | Tầm nhìn 3-5 năm, sứ mệnh, ICP (3 đặc điểm), mục tiêu năm |
| `products.md` | Bảng SP/dịch vụ: \| mã \| tên \| giá \| margin \| trạng thái \| |
| `budget.md` | Tổng ngân sách năm, phân bổ theo phòng |
| `headcount.md` | Phòng nào active (`- 07-marketing`, `- 03-finance`, ...), gap chuyên môn |
| `state.md` | Giai đoạn (seed/growth/mature/pivot), runway, KPI quý |
| `laws.md` | Luật áp dụng — pack đã pre-fill VSATTP, Luật DN 2020, BLLĐ 2019. CEO bổ sung đặc thù |

Nhờ Claude giúp:
```
Đọc Brain hiện tại của vault F:\work\xyz-vault. Gợi ý tôi điền thông tin
chiến lược dựa trên ngành cafe SME.
```

---

## Bước 6 — Chạy task đầu tiên

```
Tôi muốn làm chiến dịch quảng cáo Tết 2026 cho cafe XYZ.
Ngân sách dự kiến 50 triệu, 3 chi nhánh quận 1.
```

Plugin chạy 5 stage tự động:

### Stage 1: `vn_run` (router + clarification)
- Phân loại COMPLEX (3-5 phòng debate)
- Phòng tham gia: `02-strategy`, `03-finance`, `06-sales`, `07-marketing`, `14-food-safety`
- Tạo `03-clarification.md` với 4 câu hỏi
- → Mở file, trả lời checkbox

### Stage 2: `vn_resume`
- Đọc câu trả lời → continue

### Stage 3: `vn_meeting`
- Live research: luật quảng cáo + đối thủ + benchmark
- Họp 5 phòng × Pro + Con + 3 perspective (Growth/Cautious/Balanced)
- Synthesizer + Translator + Citation validator → `07-decision-report.md`

### Stage 4: `vn_approve`
- Sinh `08-execution-plan.md` có:
  - Bảng tasks (owner, deadline, deliverable)
  - Bảng template cần render
  - Risks + mitigation + KPIs

### Stage 5: `vn_execute`
- Render `.docx/.xlsx` từ template → `<vault>/03-Outputs/<task>/`
- CEO mở folder, gửi cho team

---

## Tiếp theo

- [User Guide](user-guide.md) — chi tiết từng stage + ví dụ task khác
- [Configuration](configuration.md) — `.vncoderc`, packs, BYOT
- [Troubleshooting](troubleshooting.md) — lỗi thường gặp
- [Architecture](architecture.md) — kiến trúc + 6 RULES

# VN One Person Company

> **Hệ điều hành AI cho Công ty 1 Người Việt Nam.**
> Bạn là CEO duy nhất — 12+ phòng ban AI agents họp bàn debate, ra quyết định, sinh báo cáo + tài liệu `.docx/.xlsx` tuân thủ luật VN.
> Chạy qua Claude Desktop subscription, **không cần Anthropic API key**.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/built_on-LangGraph-purple.svg)](https://github.com/langchain-ai/langgraph)
[![Tests](https://img.shields.io/badge/tests-261_passed-brightgreen.svg)](#)

---

## ✨ Dành cho ai?

**Solo founder Việt Nam** đang vận hành công ty 1 người (hoặc 2-3 người tinh gọn) muốn:

- 🏢 Có đủ **12+ phòng ban "ảo"** (Pháp chế, Tài chính, Marketing, Vận hành, ...) như công ty 100 người
- ⚖️ Quyết định **dựa trên debate đa chiều** thay vì chỉ 1 góc nhìn của mình
- 📄 Sinh tài liệu **tuân thủ luật VN** (Luật DN 2020, BLLĐ 2019, NĐ 15/2018 VSATTP, NĐ 13/2023 PDPA, ...)
- 🧠 Mọi quyết định + tài liệu **lưu Obsidian + Git** — single source of truth, không lạc giữa Notion/Drive/Excel
- 💰 **Không trả $20-100/tháng cho 5 SaaS** (Notion AI, ChatGPT, Claude API, ...). Plugin chạy qua Claude Desktop subscription duy nhất.

### Tình huống thực tế

| Bạn là | Trước đây | Với VN One Person Company |
|---|---|---|
| Freelancer chuẩn bị mở agency | "Hợp đồng lao động viết sao?" → Google → copy mẫu chung chung → có thể sai luật | Chat: "Tuyển trợ lý 8 triệu/tháng quận 1" → Phòng Pháp lý + Nhân sự debate → HĐLĐ chuẩn TT 200/2014 + BHXH 23.5% |
| Chủ shop online định mở chi nhánh | "Tính ROI thế nào? Đầu tư bao nhiêu là OK?" → đoán | Chat: "Mở chi nhánh 1.2 tỷ Q3" → Phòng Tài chính + Vận hành + Tăng trưởng họp 3 vòng → execution plan có CAPEX, payback period, risks |
| Dev solo mở SaaS | "Privacy policy viết sao cho đúng NĐ 13/2023?" → bí | Chat: "Soạn privacy policy SaaS B2B" → Phòng Pháp lý + Sản phẩm-Công nghệ debate → policy cite điều khoản cụ thể |
| Cafe owner làm chiến dịch Tết | "Ngân sách 50tr chia thế nào?" → cảm tính | Chat: "Chiến dịch Tết 50tr cho 3 cn" → 5 phòng họp → kế hoạch + content calendar + budget breakdown |

→ **Bạn không cần thuê CFO, CMO, COO. Plugin là họ.**

---

## 🏗 Kiến trúc

```
┌────────────────────────────────────────────────────────────────┐
│  CEO chat trong Claude Desktop / Code                           │
│              ↓                                                  │
│  vn_run(brief) → Router phân loại → Đọc Brain DN              │
│              ↓                                                  │
│  Phát hiện gap → Hỏi clarification (có cite Brain)            │
│              ↓                                                  │
│  vn_meeting → Live research (luật, đối thủ, benchmark)        │
│              ↓                                                  │
│  Họp 12 phòng ban → Pro/Con debate → 3 góc nhìn perspective  │
│              ↓                                                  │
│  Synthesizer + Translator (CEO-friendly) + Citation validator │
│              ↓                                                  │
│  vn_approve → Execution plan structured                        │
│              ↓                                                  │
│  vn_execute → Render .docx/.xlsx → 03-Outputs/                │
│              ↓                                                  │
│  Auto-commit Git private repo (Obsidian vault)                │
└────────────────────────────────────────────────────────────────┘
```

### Stack

- **Engine debate**: Python 3.11+ + LangGraph (adapt từ TradingAgents, rename neutral)
- **Knowledge base**: 192 template tiếng Việt + 12 phòng ban core + 3 industry pack
- **Storage**: Obsidian Markdown + Git private (mỗi DN 1 vault)
- **LLM**: MCP sampling qua Claude Desktop (subscription) — KHÔNG cần API key Anthropic
- **Search**: Tavily (free tier 1000 req/tháng) cho luật/đối thủ/web

---

## 🚀 Quick Start

### 1. Cài đặt

```powershell
# Clone repo
git clone https://github.com/<owner>/<repo>.git
cd <repo>

# Tạo venv
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # macOS/Linux

# Install
pip install -e .
```

### 2. Cài MCP server vào Claude Desktop

```powershell
vn-os install-mcp
# Restart Claude Desktop
```

### 3. Tạo vault cho công ty

Trong Claude Desktop chat:
```
Setup vault cho công ty XYZ tại đường dẫn F:/work/xyz-vault.
Cài pack F&B. TAVILY_API_KEY của tôi: tvly-xxx (lấy free tại tavily.com).
```

Claude tự động gọi MCP tool `vn_onboard` để tạo vault scaffold + cài pack + lưu key vào `<vault>/.env` (gitignored).

### 4. Re-install MCP với env injected

```powershell
vn-os install-mcp --vault "F:/work/xyz-vault"
# Restart Claude Desktop lần nữa
```

### 5. Điền Brain (1 lần)

CEO mở `<vault>/00-Brain/` trong Obsidian, điền:
- `strategy.md` — tầm nhìn, sứ mệnh, ICP, mục tiêu năm
- `products.md` — bảng sản phẩm/dịch vụ + giá + margin
- `budget.md` — ngân sách năm + phân bổ phòng ban
- `headcount.md` — phòng nào active, gap chuyên môn
- `state.md` — giai đoạn DN (seed/growth/...), runway

### 6. Chạy task đầu tiên

Trong Claude Desktop chat:
```
Tôi muốn làm chiến dịch quảng cáo Tết cho sản phẩm A.
Tham khảo budget hiện tại + tham vấn pháp lý.
```

Plugin sẽ:
1. Phân loại task → COMPLEX (3-5 phòng debate)
2. Đọc Brain → phát hiện gap (cần ngân sách marketing cụ thể?)
3. Hỏi CEO 3-5 câu clarification
4. Research luật quảng cáo VN + đối thủ
5. Họp pro/con + 3 perspective (Growth/Cautious/Balanced)
6. Sinh `07-decision-report.md` (CEO duyệt)
7. Sinh `08-execution-plan.md` + render `.docx/.xlsx`

---

## 📦 Industry Packs

| Pack | Phòng ban thêm | Tuân thủ |
|---|---|---|
| **F&B** (`fnb`) | Bếp, An toàn thực phẩm | NĐ 15/2018 VSATTP, PCCC TCVN 5738 |
| **Retail** (`retail`) | Kho vận, Logistics | TT 78/2021 hoá đơn ĐT |
| **Tech-SaaS** (`tech-saas`) | Engineering, Design, Data | NĐ 13/2023 PDPA, GDPR |

---

## 📜 6 RULES (bất di bất dịch)

| # | Rule | Implementation |
|---|---|---|
| 1 | **Brain-first** | Không hỏi CEO khi chưa đọc Brain |
| 2 | **Domain-neutral** | Engine ko leak trading/finance jargon |
| 3 | **Single source of truth** | Obsidian vault canonical |
| 4 | **CEO-friendly language** | Translator pipeline (3 modes) |
| 5 | **Live research with citations** | Tools graceful skip + citation validator |
| 6 | **BYOT** | DN custom > pack > default |

---

## 🛠 Configuration

Edit `<vault>/.vncoderc`:

```yaml
vault_path: F:/work/xyz-vault
packs: [fnb]
version: "0.1.0"

# Translator scope (P1.6)
# off | final_only (default) | all_intermediate
translator_mode: final_only

meeting:
  max_debate_rounds: 2
  max_perspective_rounds: 1
  use_checkpointer: false  # P1.4 opt-in crash recovery

llm:
  primary: claude-sonnet-4-6
```

---

## 🧪 Tests

```bash
python -m pytest tests/ -q
# 261 passed, 1 skipped
```

---

## 📚 Documentation

- [`docs/getting-started.md`](docs/getting-started.md) — cài đặt + onboard chi tiết
- [`docs/user-guide.md`](docs/user-guide.md) — flow 5 stage + ví dụ
- [`docs/configuration.md`](docs/configuration.md) — `.vncoderc`, packs, BYOT
- [`docs/troubleshooting.md`](docs/troubleshooting.md) — lỗi thường gặp
- [`docs/architecture.md`](docs/architecture.md) — kiến trúc + RULES + extensibility
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — đóng góp code

---

## 🤝 Đóng góp

PR welcome. Đặc biệt cần:
- Pack mới: Real Estate, Healthcare, Education, Beauty
- Translation: thêm thuật ngữ VN→EN trong glossary
- Test coverage: real-LLM E2E

Xem [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

**Apache License 2.0** — © 2026 VN Business OS Contributors

Xem [LICENSE](LICENSE) cho full text và [NOTICE](NOTICE) cho attribution chi tiết.

Apache 2.0 cho phép sử dụng commercial + modify + redistribute, đồng thời **bảo vệ tên/logo "VN Business OS" khỏi bị fork dùng quảng cáo sản phẩm khác** (Section 6) và đảm bảo người fork phải **ghi rõ các thay đổi** đã làm.

**Credits (đã chi tiết trong [NOTICE](NOTICE)):**
- 192 template tiếng Việt trong `templates-vn/` adapted from `business-builder.plugin`
- Engine debate pattern adapted from [TradingAgents](https://github.com/TauricResearch/TradingAgents) (Apache 2.0)
- Role definitions reference from [agency-agents](https://github.com/msitarzewski/agency-agents)

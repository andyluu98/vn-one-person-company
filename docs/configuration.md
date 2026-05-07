# Configuration — VN Business OS

Các file config chính + cách tinh chỉnh.

---

## Files config

| File | Vị trí | Mục đích | Có commit không? |
|---|---|---|---|
| `.vncoderc` | `<vault>/.vncoderc` hoặc `~/.vncoderc` | Settings (vault path, packs, meeting, translator) | **KHÔNG** (gitignored) |
| `.env` | `<vault>/.env` | API keys (TAVILY, ANTHROPIC, ...) | **KHÔNG** (gitignored) |
| `claude_desktop_config.json` | OS-specific (xem dưới) | MCP server registration | KHÔNG (Claude config) |

### Đường dẫn `claude_desktop_config.json`

| OS | Path |
|---|---|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

---

## `.vncoderc` — full reference

```yaml
# Vault path (auto-set bởi vn_onboard)
vault_path: F:/work/xyz-vault

# Packs đã cài (auto-set bởi vn_onboard)
packs:
  - fnb

version: "0.1.0"

# Translator scope — RULE 4 CEO-friendly language
# off              → KHÔNG simplify
# final_only       → Chỉ final decision report (default)
# all_intermediate → Mọi output: perspectives, debate, final
translator_mode: final_only

# Meeting config
meeting:
  max_perspective_rounds: 1      # Số round Growth/Cautious/Balanced (default 1)
  max_debate_rounds: 2           # Số round Pro/Con (default 2)
  max_perspective_debate_rounds: 1
  total_max: 5                   # Hard limit total LLM calls / meeting
  use_checkpointer: false        # P1.4 — opt-in crash recovery (LangGraph SqliteSaver)

# LLM config (chỉ dùng nếu KHÔNG qua MCP sampling)
llm:
  primary: claude-sonnet-4-6
  secondary: gemini-2-5-pro
  max_retries: 3
  max_tokens_per_task: 100000
  max_cost_usd_per_task: 2.0
```

### Khi nào edit?

- **Không bao giờ** edit `vault_path`, `packs`, `version` — auto bởi vn_onboard
- Thường edit:
  - `translator_mode: all_intermediate` nếu CEO không có team đỡ đọc tech jargon
  - `meeting.max_debate_rounds: 3` nếu muốn debate sâu hơn (cost +50%)
  - `meeting.use_checkpointer: true` nếu cần crash recovery (advanced)

---

## `.env` — API keys

```bash
# Search luật/đối thủ/web (free 1000 req/tháng tại tavily.com)
TAVILY_API_KEY=tvly-xxx

# KHÔNG cần khi dùng MCP sampling qua Claude Desktop
ANTHROPIC_API_KEY=

# Optional fallbacks
GOOGLE_API_KEY=
OPENAI_API_KEY=
BRAVE_API_KEY=
```

### Sau khi thêm/sửa key — BẮT BUỘC

```powershell
vn-os install-mcp --vault "F:\work\xyz-vault"
# Restart Claude Desktop
```

→ Inject env mới vào MCP server. Plugin tự động đọc `<vault>/.env` mỗi request, nhưng MCP server process được Claude Desktop launch ở env startup → re-install bắt buộc.

---

## Industry Packs

### Cài thêm pack
Trong Claude chat:
```
Cài pack retail vào vault F:\work\xyz-vault
```

(Hoặc edit `.vncoderc`, thêm `- retail` vào `packs:`, rồi gọi `vn_upgrade`.)

### Tạo pack mới
Xem [how-to-create-pack.md](how-to-create-pack.md). Tóm tắt:
1. Tạo `packs/<your-pack>/pack.yaml`
2. Thêm departments mới vào `packs/<your-pack>/departments/`
3. (Optional) `brain-template/` override Brain mặc định
4. (Optional) `extends_departments` thêm agents vào core depts

---

## BYOT — Bring Your Own Templates

DN có template hợp đồng/biểu mẫu riêng → import vào `<vault>/00-Templates-Custom/`.

### Cách 1: Onboard time
```
Setup vault. Import template từ folder F:\old-templates.
```

Plugin tự classify file theo keyword:
- `dieu-le-*`, `noi-quy-*` → `01-governance/`
- `phieu-thu-*`, `hoa-don-*` → `03-finance/`
- `jd-*`, `hop-dong-lao-dong-*` → `04-people/`
- `sop-*`, `bao-cao-*` → `05-operations/`
- Khác → `_unsorted/` (CEO sắp thủ công sau)

### Cách 2: Sau khi onboard
Copy file vào `<vault>/00-Templates-Custom/<dept-code>/<file-name>.docx`.

### Cách Plugin chọn template (RULE 6)
Khi `vn_execute` cần render template `kế-hoạch-kinh-doanh`:
1. **DN custom**: `<vault>/00-Templates-Custom/02-strategy/kế-hoạch-kinh-doanh.docx` ← thắng
2. **Pack**: `packs/fnb/templates/kế-hoạch-kinh-doanh.docx`
3. **Default**: `templates-vn/02-strategy/kế-hoạch-kinh-doanh.docx`

---

## Multi-DN setup (consultant pattern)

Một consultant phục vụ nhiều DN → mỗi DN 1 vault riêng:

```
F:/clients/
├── abc-coffee/         # Vault DN 1
│   ├── .env            # TAVILY_API_KEY của ABC
│   ├── .vncoderc
│   ├── 00-Brain/
│   ├── 01-Departments/
│   └── ...
├── xyz-tech/           # Vault DN 2
└── def-retail/         # Vault DN 3
```

Re-install MCP cho từng vault khi work với DN nào (Claude Desktop chỉ đọc 1 env tại 1 thời điểm):
```powershell
vn-os install-mcp --vault "F:\clients\abc-coffee"
# Làm việc với ABC...
vn-os install-mcp --vault "F:\clients\xyz-tech"
# Làm việc với XYZ...
```

Tool cache tách per-vault (P2.3) — không cross-poison.

---

## Advanced — Custom MCP server

Nếu cần wrap MCP với env riêng (vd staging vs prod):

Edit `claude_desktop_config.json` thủ công:
```json
{
  "mcpServers": {
    "vn-business-os-prod": {
      "command": "vn-os-mcp",
      "env": {
        "TAVILY_API_KEY": "tvly-prod",
        "VN_OS_VAULT": "F:/clients/abc-coffee"
      }
    },
    "vn-business-os-staging": {
      "command": "vn-os-mcp",
      "env": {
        "TAVILY_API_KEY": "tvly-staging"
      }
    }
  }
}
```

Restart Claude Desktop → cả 2 MCP servers available trong chat.

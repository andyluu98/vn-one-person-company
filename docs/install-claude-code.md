# Cài đặt VN One Person Company trên Claude Code

> Hướng dẫn chi tiết cho học viên — cài plugin trên **Claude Code** (CLI / terminal), không phải Claude Desktop.

## 0. Yêu cầu

| Yêu cầu | Ghi chú |
|---|---|
| **Claude Code** đã cài + login | Subscription Pro hoặc Max (Free rate limit quá thấp) |
| **Python 3.11+** | Check: `python --version` |
| **Git** | Để clone repo + auto-commit vault |
| **Windows users**: Git Bash hoặc WSL | Để chạy script `install.sh`. Không có thì dùng lệnh thay thế bên dưới. |
| **Tavily API key** (free) | Lấy tại https://tavily.com — free tier 1000 req/tháng |

---

## 1. Clone repo + cài Python package

```bash
# Clone về máy
git clone https://github.com/andyluu98/vn-one-person-company.git
cd vn-one-person-company

# Tạo virtual env (khuyến nghị)
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
# source .venv/bin/activate     # macOS/Linux/Git Bash

# Cài package
pip install -e .
```

Xác minh:
```bash
vn-os --help
# → in ra danh sách lệnh: install-mcp, ...
```

---

## 2. Cài skill + register MCP server vào Claude Code

### Cách A — Script tự động (Linux/macOS/Git Bash)

```bash
bash adapters/claude-code/install.sh
```

Script làm 2 việc:
1. Copy `skill.md` → `~/.claude/skills/vn-business-os/SKILL.md`
2. Chạy `vn-os install-mcp --target claude-code` → thêm entry `vn-business-os` vào `~/.claude.json`

### Cách B — Thủ công (Windows PowerShell, không có Git Bash)

```powershell
# B1: Tạo thư mục skill
mkdir "$env:USERPROFILE\.claude\skills\vn-business-os" -Force

# B2: Copy skill file
Copy-Item adapters\claude-code\skill.md "$env:USERPROFILE\.claude\skills\vn-business-os\SKILL.md"

# B3: Register MCP server
vn-os install-mcp --target claude-code
```

### Kiểm tra cài đặt

```bash
# Xem skill đã copy chưa
ls ~/.claude/skills/vn-business-os/SKILL.md     # Linux/macOS
dir "$env:USERPROFILE\.claude\skills\vn-business-os\SKILL.md"   # Windows

# Xem MCP đã register chưa
cat ~/.claude.json | grep -A 3 "vn-business-os"
```

Phải thấy entry kiểu:
```json
"vn-business-os": {
  "command": "vn-os-mcp"
}
```

### Restart Claude Code

Đóng terminal hiện tại + mở mới. Claude Code đọc `~/.claude.json` lúc khởi động session.

---

## 3. Lần đầu sử dụng — tạo vault cho công ty

Mở Claude Code ở thư mục bất kỳ (vault có thể nằm chỗ khác):

```bash
claude
```

Trong chat session, gõ:

```
Setup vault VN Business OS cho công ty TechCo của tôi.
- Vault path: F:/work/techco-vault
- Industry: Tech-SaaS
- Tavily API key: tvly-xxxxxxxxxxxxxxxx
```

**Claude sẽ:**
1. Detect skill `vn-business-os` active (vì có keyword "Setup vault")
2. Gọi MCP tool `vn_onboard(vault="F:/work/techco-vault", pack="tech-saas")`
3. Tool tạo scaffold:
   ```
   F:/work/techco-vault/
   ├── 00-Brain/          ← CEO sẽ điền
   │   ├── strategy.md
   │   ├── products.md
   │   ├── budget.md
   │   ├── headcount.md
   │   └── state.md
   ├── 01-Departments/    ← 12 phòng ban + pack tech-saas
   ├── 02-Tasks/          ← mỗi task = 1 folder
   ├── 03-Outputs/        ← .docx/.xlsx sinh ra
   ├── .vncoderc          ← config
   └── .env               ← TAVILY_API_KEY (gitignored)
   ```
4. Hỏi tiếp: *"Vault đã tạo. Bạn muốn mình hướng dẫn điền Brain ngay không?"*

**Sau khi vault có Tavily key**, chạy lại lệnh inject env:

```bash
vn-os install-mcp --target claude-code --vault "F:/work/techco-vault"
```

Lệnh này đọc `<vault>/.env` rồi inject vào MCP server entry trong `~/.claude.json` → search tools có credentials sẵn, không skip silently. **Restart Claude Code 1 lần nữa.**

---

## 4. Điền Brain (1 lần, ~30 phút)

Mở `<vault>/00-Brain/` bằng editor (VSCode, Obsidian, nano, ...). Điền 5 file:

| File | Nội dung |
|---|---|
| `strategy.md` | Tầm nhìn, sứ mệnh, ICP, mục tiêu năm |
| `products.md` | Bảng sản phẩm/dịch vụ + giá + margin |
| `budget.md` | Ngân sách năm + phân bổ phòng ban |
| `headcount.md` | Phòng nào active, gap chuyên môn |
| `state.md` | Giai đoạn DN (seed/growth/...), runway |

Mẫu có sẵn trong file scaffold — chỉ cần điền vào.

---

## 5. Chạy task đầu tiên

Trong Claude Code chat:

```
Tôi muốn làm chiến dịch quảng cáo Tết cho sản phẩm A.
Ngân sách 50 triệu, target khách thu nhập 30tr+.
Vault: F:/work/techco-vault
```

→ Xem section [Kịch bản tương tác](#kịch-bản-tương-tác-claude--học-viên) phía dưới.

---

## Kịch bản tương tác Claude ↔ học viên

Đây là **flow chuẩn** học viên sẽ thấy. Show cho học viên trước để họ không bỡ ngỡ.

### Stage 1: Brief → Clarification

**Học viên gõ:**
> Tôi muốn làm chiến dịch quảng cáo Tết cho sản phẩm A. Ngân sách 50 triệu, target khách thu nhập 30tr+. Vault: F:/work/techco-vault

**Claude (tự động):**
1. Gọi `vn_status(vault="F:/work/techco-vault")` → verify Brain
2. Gọi `vn_run(brief, vault)` → tool trả về `{"stage": "PAUSE_CLARIFICATION", "task_folder": "F:/work/techco-vault/02-Tasks/260530-2340-chien-dich-tet/"}`
3. Đọc file `03-clarification.md` trong task folder
4. **Hỏi học viên (tiếng Việt, có cite Brain)**:

```
Theo `00-Brain/strategy.md`, ICP của bạn là "SME 5-50 nhân viên".
Câu hỏi 1: Khách thu nhập 30tr+ có overlap với ICP SME không, hay đây
là segment mới mở rộng?

   [a] Cùng ICP — chỉ filter income
   [b] Segment mới — cần re-positioning

Câu hỏi 2: Theo `00-Brain/budget.md`, marketing budget Q1 còn 80tr.
50tr cho campaign Tết = 62% quota Q1. OK không?

   [a] OK, ưu tiên Tết
   [b] Cắt còn 30tr, để dành Q1 còn lại

Bạn chọn (a) hay (b) cho câu 1?
```

> **Lưu ý quan trọng**: Theo CLAUDE.md, Claude **chỉ hỏi 1 câu tại một thời điểm**. Học viên trả lời xong câu 1 → Claude hỏi câu 2.

**Học viên:**
> Câu 1 chọn a, câu 2 chọn a

**Claude:**
5. Tick `[x]` vào `03-clarification.md` cho lựa chọn của user
6. Gọi `vn_resume(task_folder)` → tiếp Stage 2

---

### Stage 2: Meeting (research + debate)

**Claude (auto, không cần học viên thao tác):**

1. Báo: *"Bắt đầu họp 5 phòng ban: Marketing, Tài chính, Pháp lý, Tăng trưởng, Sản phẩm. Mất khoảng 5-8 phút."*
2. Gọi `vn_meeting(task_folder)` — tool chạy:
   - Research phase (Tavily search luật QC Tết VN, đối thủ, benchmark CTR)
   - 3 perspectives parallel (Growth / Cautious / Balanced)
   - 2-3 round Pro/Con debate
   - Synthesizer tổng hợp
   - Sinh `07-decision-report.md`
3. Đọc decision report, tóm tắt cho học viên:

```
✅ Họp xong. Tóm tắt 07-decision-report.md:

TL;DR: GO with revisions — campaign khả thi, cần điều chỉnh 3 điểm trước launch.

Khuyến nghị: GO with revisions

BLOCKERS (làm trước launch):
1. Đăng ký nội dung QC với Sở TT&TT (theo NĐ 70/2021) — 5 ngày làm việc
2. Landing page cần privacy notice tuân NĐ 13/2023 PDPA
3. Budget breakdown chưa đủ cho remarketing — đề xuất tách 8tr riêng

KPI gates:
- CTR > 1.5%, CPC < 25k VND
- ROAS > 2.5x sau 14 ngày

Câu hỏi cần CEO quyết:
- Có chốt agency Facebook (10tr) hay tự chạy in-house?

Bạn duyệt plan này không? (approve / revise / reject)
```

---

### Stage 3: Approve → Execution plan

**Học viên:**
> Approve, tự chạy in-house

**Claude:**
1. Gọi `vn_approve(task_folder, decisions={"agency": false})`
2. Tool sinh `08-execution-plan.md`
3. Báo: *"Plan duyệt xong. Tiến hành sinh file .docx/.xlsx?"*

**Học viên:**
> OK

---

### Stage 4: Execute → render files

**Claude:**
1. Gọi `vn_execute(task_folder)`
2. Tool render:
   - `kpi-tracker.xlsx` — bảng theo dõi KPI
   - `content-calendar.xlsx` — lịch nội dung 14 ngày
   - `legal-checklist.docx` — checklist tuân thủ
   - `budget-breakdown.xlsx` — chia tiền chi tiết
3. Tự commit vào git private repo của vault
4. Báo: *"Xong. Files ở `F:/work/techco-vault/03-Outputs/260530-2340-chien-dich-tet/`."*

**Tổng thời gian**: 8-15 phút. Học viên ngồi máy ~5 phút (trả lời clarification + duyệt).

---

## Troubleshooting

### Lỗi: `vn-os: command not found`

Chưa activate venv hoặc chưa `pip install -e .`. Chạy:
```bash
.venv\Scripts\activate
pip install -e .
```

### Lỗi: MCP server không xuất hiện trong Claude Code

1. Kiểm tra `~/.claude.json` có entry `vn-business-os` chưa
2. Restart Claude Code (đóng terminal, mở lại)
3. Chạy `claude --mcp-debug` xem log

### Lỗi: Search tools skip silently

Tavily key chưa inject. Chạy lại:
```bash
vn-os install-mcp --target claude-code --vault "<path-to-vault>"
```
Sau đó restart Claude Code.

### Lỗi: Rate limit (subscription quota hết)

- Pro plan ≈ 45 msg/5h → 1 task COMPLEX gần kịch quota
- Đề xuất: nghỉ 1-2h rồi retry, hoặc upgrade Max plan (~225 msg/5h)
- Hoặc bật **lite mode** trong `.vncoderc`:
  ```yaml
  meeting:
    max_debate_rounds: 1
    max_perspective_rounds: 0
  ```
  → Giảm còn ~15 sampling calls/task

### Lỗi: Vault not found

```
Setup vault cho công ty XYZ tại đường dẫn ... trước khi chạy task.
```
Hoặc gọi trực tiếp `vn_onboard` qua MCP tool.

### Windows: `bash: command not found` khi chạy `install.sh`

Dùng Cách B (PowerShell thủ công) ở mục 2.

---

## Checklist cho giảng viên

Trước buổi dạy, kiểm tra học viên đã:

- [ ] Cài Claude Code + login subscription Pro/Max
- [ ] Cài Python 3.11+
- [ ] Cài Git (+ Git Bash nếu Windows)
- [ ] Có Tavily API key (free tier)
- [ ] Clone repo + chạy `pip install -e .` thành công
- [ ] Chạy `vn-os --help` ra được danh sách lệnh
- [ ] Chạy `install.sh` (hoặc Cách B) — verify `~/.claude.json` có entry `vn-business-os`
- [ ] Restart Claude Code
- [ ] Tạo vault test + điền Brain mẫu (có thể dùng vault demo có sẵn)
- [ ] Chạy 1 task SIMPLE để verify end-to-end (vd "Soạn JD lập trình viên 15tr")

---

## Tham khảo thêm

- [`adapters/claude-code/README.md`](../adapters/claude-code/README.md) — adapter overview
- [`adapters/claude-code/skill.md`](../adapters/claude-code/skill.md) — skill definition
- [`docs/user-guide.md`](user-guide.md) — flow 5 stage chi tiết
- [`docs/troubleshooting.md`](troubleshooting.md) — lỗi thường gặp tổng quát
- [`docs/architecture.md`](architecture.md) — kiến trúc + RULES

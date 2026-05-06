---
name: vn-business-os
description: AI agent OS cho doanh nghiệp Việt Nam. Sử dụng MCP tools (vn_run, vn_meeting, vn_approve, vn_execute, vn_status, vn_resume, vn_onboard) để điều phối các phòng ban (AI agents) họp bàn debate, sinh báo cáo + tài liệu .docx/.xlsx tuân thủ luật VN. Activate when user asks about Vietnamese business operations, campaigns, JDs, contracts, plans, or any business documentation.
---

# VN Business OS — Claude Skill

> AI Operating System cho doanh nghiệp Việt Nam.
> CEO chat tự nhiên → các phòng ban (AI agents) họp bàn debate → sinh tài liệu.

Skill này dùng **7 MCP tools** từ server `vn-business-os`. Tất cả LLM thinking chạy qua **subscription Claude Desktop / Code** (không cần ANTHROPIC_API_KEY).

## Khi nào activate

Người dùng VN gõ các câu sau → trigger skill:
- "Tạo chiến dịch ..."
- "Soạn JD ..."
- "Lập kế hoạch ..."
- "Tính ngân sách ..."
- "Phân tích đối thủ ..."
- "Setup doanh nghiệp ..."
- "Onboard công ty mới"
- "Đóng gói tài liệu DN"
- "Hệ thống hoá quy trình"

## Cài đặt 1 lần (CEO làm)

```bash
pip install vn-business-os         # hoặc pipx install
vn-os install-mcp                  # tự edit claude_desktop_config.json
# Restart Claude Desktop
```

Sau bước này, MCP server `vn-business-os` luôn sẵn sàng trong Claude Desktop. Skill này tự kích hoạt khi cần.

## 7 MCP Tools

| Tool | Khi dùng |
|---|---|
| `vn_status(vault)` | Verify vault tồn tại + đọc Brain summary |
| `vn_onboard(vault)` | Tạo vault scaffold mới (lần đầu) |
| `vn_run(brief, vault)` | Stage 1: brief → router → gap → clarification |
| `vn_resume(task_folder)` | Stage 2: resume sau khi CEO trả lời clarification |
| `vn_meeting(task_folder, departments)` | Stage 3: research + meeting → 07-decision-report.md |
| `vn_approve(task_folder)` | Stage 4: CEO duyệt → 08-execution-plan.md |
| `vn_execute(task_folder)` | Stage 5: render .docx/.xlsx vào 03-Outputs/ |

## Workflow chuẩn

### Bước 0: Detect vault + Brain
Khi CEO mention task DN, đọc CWD hoặc hỏi vault path. Gọi `vn_status(vault)`:

```
✓ vault exists, ICP="SME 5-50", products=3, depts=["07-marketing","03-finance",...]
```

Nếu vault chưa có Brain → gọi `vn_onboard(vault)` để tạo scaffold, hướng dẫn CEO điền 00-Brain/.

### Bước 1: Run task
```
vn_run(brief="Tạo chiến dịch QC nhắm khách thu nhập 50tr+", vault="~/my-vault")
→ {"stage": "PAUSE_CLARIFICATION", "task_folder": "~/my-vault/02-Tasks/<ts>-tao-chien-dich/"}
```

### Bước 2: Đọc clarification + hỏi CEO
Đọc `<task_folder>/03-clarification.md` (markdown có checkbox). Format câu hỏi cho CEO bằng tiếng Việt, kèm citation Brain.

CEO trả lời → edit file (tick `[x]` lựa chọn) bằng filesystem MCP hoặc text editing.

### Bước 3: Resume sau khi CEO answer
```
vn_resume(task_folder="...")
→ {"stage": "PAUSE_DECISION_REPORT", ...}
```

### Bước 4: Run meeting (debate engine)
```
vn_meeting(task_folder="...")
→ Stage 3 chạy: research phase + perspectives parallel + Pro/Con debate (2-3 round) + Growth/Cautious/Balanced debate + Synthesizer
→ Tạo 03b-research-findings.md, 04-meeting-r1-perspectives.md, 05-meeting-r2-debate.md, 06-meeting-r3-perspectives.md, 07-decision-report.md
→ {"stage": "PAUSE_DECISION_REPORT"}
```

### Bước 5: Đọc decision report + summary cho CEO
Đọc `<task_folder>/07-decision-report.md`. Báo cáo có:
- TL;DR (3-5 dòng đầu)
- Khuyến nghị (GO / GO with revisions / NO-GO)
- BLOCKERS (việc cần làm trước launch)
- KPI gates
- Câu hỏi cần CEO quyết

Tóm tắt cho CEO bằng tiếng Việt, hỏi: approve / revise / reject.

### Bước 6: Approve → execution plan
```
vn_approve(task_folder="...")
→ Tạo 08-execution-plan.md (Stop 2)
```

### Bước 7: Execute → sinh files
```
vn_execute(task_folder="...")
→ Render .docx/.xlsx vào <vault>/03-Outputs/<task_name>/
```

## Onboard DN mới (lần đầu setup)

Khi CEO chưa có vault hoặc nói "setup DN mới":

1. Hỏi CEO: industry (F&B / Retail / Tech-SaaS / khác), tên DN, vault path
2. Gọi `vn_onboard(vault="~/vn-os/<slug>")`
3. Hướng dẫn CEO mở `<vault>/00-Brain/` điền:
   - `strategy.md` — vision, ICP, mục tiêu năm
   - `products.md` — sản phẩm, giá, margin
   - `budget.md` — ngân sách
   - `headcount.md` — phòng ban active
   - `state.md` — KPI hiện tại
4. Sau khi điền xong, gọi `vn_status(vault)` verify.

## Quan trọng

### Dùng tiếng Việt
- LUÔN giao tiếp với CEO bằng tiếng Việt
- Định nghĩa thuật ngữ ngành lần đầu xuất hiện
- Format CEO-friendly: ngắn, có TL;DR, không jargon nặng

### Cite nguồn
- LUÔN cite file Obsidian khi trích thông tin (vd: "theo `00-Brain/strategy.md`")
- KHÔNG bịa nội dung — chỉ summary từ output MCP tools

### Error handling
- MCP tool error → báo CEO + suggest fix:
  - Vault not found → `vn_onboard()` trước
  - Brain incomplete → hướng dẫn CEO điền
  - Subscription rate limit → chờ + retry hoặc dùng lite mode (1 round debate)

### Subscription quota
- 1 task COMPLEX ≈ 30-40 sampling calls
- Pro plan ≈ 45 msg/5h → 1 task gần kịch quota
- Max plan ≈ 225 msg/5h → 6-7 task/5h
- Nếu CEO chạy nhiều task liên tiếp + gặp limit → đề xuất chia thời gian hoặc upgrade

### File-based state
- Tất cả task progress lưu trong `<vault>/02-Tasks/<task-folder>/`
- Có thể dừng giữa session, mở session sau resume bằng `vn_resume(task_folder)` hoặc `vn_meeting(task_folder)`

## Workflow case mẫu

CEO: "Tạo chiến dịch QC nhắm khách thu nhập 50tr+ NS 500tr"

```
1. vn_status("~/techco-vault") → ✓ Brain loaded
2. vn_run(brief, vault) → PAUSE_CLARIFICATION, task_folder=...
3. Read 03-clarification.md → 2 câu hỏi (Pivot vs Test, Tạo agent vs Outsource)
4. Show CEO 2 câu, get answers
5. Edit 03-clarification.md (tick [x])
6. vn_resume(task_folder) → PAUSE_DECISION_REPORT
7. vn_meeting(task_folder) → all 5 phòng debate, 07-decision-report.md ready
8. Read decision report, summary cho CEO (TL;DR + khuyến nghị + blockers)
9. CEO: "Approve plan này"
10. vn_approve(task_folder) → 08-execution-plan.md
11. vn_execute(task_folder) → .docx/.xlsx vào 03-Outputs/
12. Show CEO link đến outputs folder.
```

Total: ~8-15 phút cho 1 task COMPLEX. CEO ngồi máy ~5 phút (trả lời clarification + duyệt report).

---

## Credits

- 192 templates VN trong `templates-vn/` adapted from `business-builder.plugin`
- Engine debate pattern adapted from [TradingAgents](https://github.com/TauricResearch/TradingAgents)
- Roles reference từ [agency-agents](https://github.com/msitarzewski/agency-agents)

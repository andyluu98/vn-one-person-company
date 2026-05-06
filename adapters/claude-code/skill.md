---
name: vn-business-os
description: AI agent OS cho doanh nghiệp Việt Nam. Chat tự nhiên với CEO, gọi Python CLI điều phối các phòng ban (agents) họp bàn, debate, sinh báo cáo + tài liệu .docx/.xlsx tuân thủ luật VN. Use when user wants to manage business operations, create campaigns, generate JDs, contracts, plans, or any business documentation in Vietnamese context.
---

# VN Business OS — Claude Code Skill

Khi CEO chat với task DN, skill này:

1. Phát hiện vault VN Business OS (folder có `00-Brain/`)
2. Chuyển brief sang Python CLI: `vn-os run --brief "<text>" --vault <path>`
3. Đọc kết quả từ Obsidian vault để báo cáo cho CEO
4. CEO duyệt qua các stop point (clarification, decision, execute)

## Khi user nói các câu sau → trigger skill

- "Tạo chiến dịch ..."
- "Soạn JD ..."
- "Lập kế hoạch ..."
- "Tính ngân sách ..."
- "Đóng gói doanh nghiệp"
- "Hệ thống hóa tài liệu DN"
- "Phân tích đối thủ ..."

## Workflow

### Bước 1: Verify vault
```bash
ls $VAULT/00-Brain/strategy.md
```
Nếu KHÔNG có → đề xuất chạy `vn-os onboard --vault $VAULT`.

### Bước 2: Run task
```bash
vn-os run --brief "<user's brief>" --vault $VAULT
```
Output sẽ tạo folder `02-Tasks/<timestamp>-<slug>/` và pause ở clarification.

### Bước 3: Đọc clarification, hỏi CEO
Đọc `02-Tasks/<task>/03-clarification.md`, hỏi CEO chọn từng câu, edit file (tick checkbox), rồi:
```bash
vn-os meeting <task-folder>
```

### Bước 4: Sau meeting, đọc 07-decision-report.md
Tóm tắt cho CEO. Hỏi: approve/revise/reject.

### Bước 5: Sau approve
```bash
vn-os approve <task-folder>
vn-os execute <task-folder>
```

## Quan trọng

- LUÔN dùng tiếng Việt khi giao tiếp CEO
- LUÔN cite file Obsidian khi trích thông tin (vd: "theo 00-Brain/strategy.md")
- KHÔNG bịa nội dung — chỉ summary từ output Python CLI
- Nếu Python CLI lỗi → báo CEO + suggest debug command

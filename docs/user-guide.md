# User Guide — VN One Person Company

Hướng dẫn sử dụng hàng ngày sau khi đã onboard. Xem [Getting Started](getting-started.md) trước nếu chưa cài.

---

## Flow tổng quan

```
                    ┌─ Stage 1 ─┐         ┌─ Stage 2 ─┐
CEO chat brief ────→│  vn_run   │────────→│ vn_resume │
                    └───────────┘         └───────────┘
                          │                     │
                          ↓                     ↓
                    Tạo task folder      Đọc clarification
                    Phân loại + Brain    answers, continue
                    Sinh clarification

                    ┌─ Stage 3 ─┐         ┌─ Stage 4 ─┐         ┌─ Stage 5 ─┐
                    │ vn_meeting│────────→│ vn_approve│────────→│ vn_execute│
                    └───────────┘         └───────────┘         └───────────┘
                          │                     │                     │
                          ↓                     ↓                     ↓
                    Research + Họp       Sinh execution         Render .docx/
                    debate + Cite        plan structured        .xlsx outputs
                    validator
                          │
                       STOP 1                  STOP 2
                  (CEO duyệt report)     (CEO duyệt execute)
```

**2 stops cần CEO can thiệp:**
- **STOP 1:** sau `vn_meeting` — đọc `07-decision-report.md`, OK → gọi `vn_approve`
- **STOP 2:** sau `vn_approve` — đọc `08-execution-plan.md`, OK → gọi `vn_execute`

CEO có thể edit cả 2 file trước khi qua stage tiếp.

---

## Files trong mỗi task

```
<vault>/02-Tasks/<task-slug>/
├── 00-brief.md                  # Brief gốc của CEO
├── 01-routing.md                # Phân loại + phòng tham gia
├── 02-context.md                # Brain dump used
├── 03-clarification.md          # Câu hỏi CEO (Stage 1)
├── 03-clarification-answered.md # Normalized answers (Stage 2)
├── 03b-research-findings.md     # Live research output (Stage 3)
├── 04-meeting-r1-perspectives.md
├── 05-meeting-debate.md         # Pro/Con transcript
├── 06-meeting-synthesis.md
├── 07-decision-report.md        # ★ STOP 1 — CEO đọc + duyệt
├── 08-execution-plan.md         # ★ STOP 2 — CEO đọc + duyệt
└── 09-execution-summary.md      # Sau Stage 5

<vault>/03-Outputs/<task-slug>/
└── <template-name>.docx/.xlsx   # Tài liệu render thật
```

---

## Ví dụ thực tế

### Task SIMPLE: Soạn JD nhân viên kế toán

```
Tôi cần JD tuyển kế toán viên cho cafe XYZ. Yêu cầu 2 năm kinh nghiệm,
biết MISA, hiểu chế độ kế toán theo TT 200.
```

Plugin:
- Phân loại **SIMPLE** → 1-2 phòng (`04-people`, `03-finance`)
- Brain check: phòng kế toán có active? Nhân sự gap? → OK
- Skip clarification (đủ thông tin)
- Skip meeting (SIMPLE)
- Sinh JD trực tiếp từ template `04-people/refs/jd-template.md` → `.docx`
- ~2 phút, ~$0.10 LLM cost

### Task COMPLEX: Chiến dịch QC Tết

```
Chiến dịch QC Tết 2026 cho cafe XYZ. Ngân sách 50tr, 3 chi nhánh.
Mục tiêu doanh thu Tết +30% YoY.
```

Plugin:
- Phân loại **COMPLEX** → 5 phòng debate
- Brain check → gap về ICP cụ thể (đã định nghĩa "khách văn phòng" nhưng Tết cần khác)
- Clarification 4 câu (mục tiêu doanh thu chi tiết, sản phẩm ưu tiên, ...)
- Research: luật QC Tết, đối thủ Highland/Phúc Long Tết, benchmark F&B holiday
- Họp 5 phòng × 3 perspective × 2 round → 30+ messages
- Decision report ~1500 từ + cảnh báo citations nếu thiếu
- Execution plan có 8 task + 4 template
- Render: kế-hoạch-truyền-thông.docx, ngân-sách-chi-tiết.xlsx, content-calendar.xlsx, FAQ-nhân-viên.docx
- ~10-15 phút, ~$0.80-1.20 LLM cost

### Task STRATEGIC: Mở chi nhánh thứ 4

```
Tôi muốn mở chi nhánh cafe thứ 4 tại quận 7 trong Q3.
Đầu tư khoảng 1.2 tỷ. Hỏi tham vấn pháp lý + tài chính + ops.
```

Plugin:
- Phân loại **STRATEGIC** → 7+ phòng + CEO duyệt giữa chừng
- Clarification kỹ hơn (10+ câu)
- Research: BĐS quận 7, luật mở chi nhánh F&B, benchmark CAPEX
- Meeting nhiều round
- STOP 1 + STOP 2 nghiêm ngặt
- ~25-30 phút, ~$1.5-2.0 LLM cost

---

## Tools chỉ dùng khi cần

### `vn_draft` — fast path cho doc boilerplate
Soạn 1 tài liệu qua 1 LLM call (~10-30s), KHÔNG qua debate engine.

**Use case:** HĐLĐ, JD, nội quy, phiếu thu, SOP đơn giản, thư mời họp...
```
Soạn HĐLĐ trợ lý kế toán cho cafe ABC, lương 10tr, thử việc 2 tháng.
```
Output: `<vault>/02-Tasks/<ts>-draft-<slug>/draft.md`

**KHÔNG dùng** cho quyết định chiến lược / có rủi ro pháp lý lớn → dùng `vn_run` + `vn_meeting`.

### `vn_status`
Inspect vault state — Brain summary + active phòng + tasks + tool availability.
```
vn_status vault F:\work\xyz-vault
```

### `vn_upgrade`
Sau khi pull plugin update mới, refresh vault hiện có:
```
Upgrade vault F:\work\xyz-vault
```
- Refresh agent .md prompts
- Inject Brain aliases mới
- KHÔNG động Brain content / Tasks / Outputs (CEO data)

### `vn_onboard`
Tạo vault mới (xem [Getting Started](getting-started.md)).

---

## Tips chạy hiệu quả

### 1. Brain phải đầy đủ
Plugin Brain-first → Brain rỗng = clarification rất dài. Spend 30 phút điền Brain ban đầu, save sau hàng tuần.

### 2. Translate mode
- `final_only` (default): nhanh, cost thấp, CEO thấy decision report dễ hiểu
- `all_intermediate`: chậm hơn 2-3x nhưng mọi output (perspectives, debate) đều CEO-friendly. Bật nếu CEO không có CTO/CMO đỡ đọc.

Edit `<vault>/.vncoderc`:
```yaml
translator_mode: all_intermediate
```

### 3. Re-run task
Plugin idempotent: nếu task fail giữa chừng, gọi lại MCP tool tương ứng — task folder cũ được resume.

### 4. Edit decision report trước approve
CEO mở `07-decision-report.md`, sửa, lưu → `vn_approve` đọc bản đã sửa.

### 5. Citation cảnh báo
Nếu `07-decision-report.md` có section `## ⚠️ Cảnh báo: Claims thiếu trích nguồn` → review claims đó trước khi approve. Có thể là LLM hallucination.

### 6. Tools skip → bật key
Nếu `vn_status` báo `tools_skipped: [web_search, ...]` → flow vẫn chạy nhưng decision report dựa hoàn toàn vào Brain + LLM common knowledge. Bật TAVILY_API_KEY để search VN luật/đối thủ thật.

---

## Tiếp theo

- [Configuration](configuration.md) — tinh chỉnh `.vncoderc`
- [Troubleshooting](troubleshooting.md) — debug khi lỗi
- [How to create pack](how-to-create-pack.md) — thêm pack ngành mới

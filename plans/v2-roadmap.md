# v2 Roadmap — VN Business OS

> Trạng thái: **Chờ triển khai sau v1 dùng thực tế ≥ 2-4 tuần**
> Ngày tạo: 2026-05-06
> Owner: ltuananhsd@gmail.com

---

## Bối cảnh

v1 (đã ship `phase-06-complete` + tag `v0.1.0`) phá vỡ 4 giới hạn cốt lõi:

| Giới hạn v1 | Giải pháp v2 |
|---|---|
| Phải chạy CLI thủ công từng task | Auto-loop cron |
| Output chỉ có markdown trong Obsidian | Web UI dashboard |
| 1 cài đặt = 1 DN | Multi-DN context switching |
| 3 ngành (F&B, Retail, Tech-SaaS) | 6 pack ngành mới |

**Nguyên tắc:** Đừng build v2 ngay. Dùng v1 ≥ 2-4 tuần → đo pain point → ưu tiên feature theo thứ tự CEO thấy thiếu nhất.

---

## Feature 1 — Auto-loop Cron

**Vấn đề:** CEO phải nhớ gõ `vn-os run --brief ...` mỗi khi cần báo cáo định kỳ.

**Giải pháp:** Cron schedule trong `vault/cron.yaml`, daemon đọc + chạy task tự động.

### Thiết kế

```yaml
# vault/cron.yaml
- schedule: "0 9 * * MON"      # Mỗi sáng thứ 2
  brief: "Báo cáo tuần — doanh thu, churn, gap so KPI"
  auto_approve: true            # SIMPLE → không cần CEO duyệt
  notify: ["email:ceo@dn.vn"]   # nếu có gap CRITICAL

- schedule: "0 9 1 * *"        # Mùng 1 mỗi tháng
  brief: "Đánh giá runway + propose budget tháng tới"
  auto_approve: false           # STRATEGIC → CEO phải duyệt

- schedule: "0 8 * * *"        # Mỗi sáng 8h
  brief: "Check gap luật mới ban hành ảnh hưởng DN"
  auto_approve: true
```

### Module mới
- `core/scheduler/cron_runner.py` — Read cron.yaml, dispatch tasks via FlowController
- `core/scheduler/notifier.py` — Email/Telegram notification khi task xong hoặc cần CEO duyệt
- CLI: `vn-os daemon start|stop|status`

### Effort
~3-5 ngày

---

## Feature 2 — Web UI Dashboard

**Vấn đề:** CEO non-tech phải học CLI commands. Edit markdown trong Obsidian không phải ai cũng quen.

**Giải pháp:** Web app chạy local (`vn-os ui`) hiện UI thay cho CLI.

### Tabs đề xuất

| Tab | Tính năng |
|---|---|
| **Tasks** | List task đang chạy + đã xong, click xem decision report |
| **Brain** | Edit `00-Brain/*.md` qua form (không cần Obsidian) |
| **Approve** | Xem clarification + tick checkbox bằng UI, không edit markdown |
| **Outputs** | Download .docx/.xlsx, preview |
| **Insights** | Dashboard KPI tự sinh từ Brain (MRR chart, runway gauge, food cost trend) |
| **Settings** | API keys, packs installed, cron schedule |

### Stack đề xuất
- **Backend**: FastAPI (wrap FlowController API)
- **Frontend**: Vanilla HTML + HTMX hoặc React (đơn giản, ít dependency)
- **Auth**: local-only HTTP basic, không expose internet
- CLI: `vn-os ui --port 8765`

### Effort
~10-15 ngày (backend API + 6 tabs + design)

---

## Feature 3 — Multi-DN Support

**Vấn đề:** 1 vault = 1 DN. CEO holding 3 DN (quán ăn + shop online + SaaS) phải cài 3 lần.

**Giải pháp:** 1 cài đặt manage nhiều vault, có context switching.

### CLI mới

```bash
vn-os company add quan-an-pho-ngon --vault ~/vaults/quan-an --pack fnb
vn-os company add shop-thoi-trang --vault ~/vaults/shop --pack retail
vn-os company add techco --vault ~/vaults/techco --pack tech-saas

vn-os company list
# - quan-an-pho-ngon  (F&B)   ~/vaults/quan-an
# - shop-thoi-trang   (retail) ~/vaults/shop  
# - techco            (saas)   ~/vaults/techco

vn-os company switch quan-an-pho-ngon
vn-os run --brief "Tính food cost tháng 5"
# → tự load Brain + agents của quán phở

vn-os company switch techco
vn-os run --brief "Phân tích churn Q2"
# → load Brain SaaS
```

### Module mới
- `core/multi_company/registry.py` — `~/.vn-business-os/companies.yaml` lưu list DN
- Modify `core/cli.py` — wrap mọi command với context auto-resolve

### Use cases
- CEO holding nhiều DN
- Agency consulting cho nhiều khách
- Mentor tư vấn nhiều startup
- Family office quản nhiều business

### Effort
~5-7 ngày

---

## Feature 4 — Packs mới (6 ngành)

**Vấn đề:** v1 chỉ có 3 packs. Nhiều ngành phổ biến VN chưa có.

### Packs đề xuất

| Pack | Phòng đặc thù | Compliance VN |
|---|---|---|
| **Real Estate** | sales-broker, property-manager, mortgage-advisor | Luật Kinh doanh BĐS 2014, Luật Đất đai 2024 |
| **Healthcare** | clinical-coordinator, medical-billing, privacy-officer | Luật Khám chữa bệnh 2023, BHYT, Luật Dược |
| **Education** | curriculum-designer, academic-coordinator, parent-relations | Luật Giáo dục 2019, NĐ 86/2018 (giáo dục có yếu tố nước ngoài) |
| **Beauty/Spa** | service-master, retail-product-mgr, hygiene-spa | NĐ 109/2016 (mỹ phẩm), TT 06/2011 (spa) |
| **Auto** | service-advisor, parts-manager, warranty-officer | Luật GTĐB, NĐ 116/2017 (ô tô) |
| **Construction** | project-manager-construction, safety-officer, qs-engineer | Luật Xây dựng 2014, NĐ 06/2021 |

### Pattern
Mỗi pack ~5-10 file, copy template từ F&B/Retail/Tech-SaaS đã có:
- `pack.yaml`
- 1-3 dept folders
- 1-2 agent .md mỗi dept
- `brain-template/strategy.md` (override KPI ngành)
- `compliance_refs:` list luật

### Effort
~1-2 ngày/pack × 6 = ~10 ngày

---

## Feature 5 — Codex + Antigravity adapter (v1.1)

**Đã được liệt kê trong v1.1 nhưng chưa làm:**

- `adapters/codex/system-prompt.md` — Codex CLI integration
- `adapters/antigravity/SKILL.md` — Antigravity adapter

### Effort
~2 ngày (pattern y hệt Claude Code adapter)

---

## Feature 6 — Test case A + C (v1.1)

**Đã liệt kê trong v1.1 nhưng chưa làm:**

- **Test case A**: full onboarding flow (CEO mới → vault sẵn sàng dùng)
- **Test case C**: SIMPLE task — soạn JD trong < 2 phút, không cần họp

### Effort
~2-3 ngày

---

## Feature 7 — Vietnamese spell-check (optional)

**Đã liệt kê trong open questions:**

Tích hợp `pyvi` để check chính tả VN trong outputs. Tránh CEO nhận báo cáo có lỗi typo.

### Effort
~1 ngày

---

## Tổng effort + thứ tự đề xuất

| Phase | Feature | Effort | Lý do ưu tiên |
|---|---|---|---|
| **v1.1** | Test case A + C, Codex adapter, pyvi | ~5-7 ngày | Hoàn thiện scope đã commit trong v1 |
| **v2.0** | Web UI Dashboard | ~10-15 ngày | Pain point lớn nhất nếu CEO non-tech |
| **v2.1** | Auto-loop cron | ~3-5 ngày | Cao value, dễ làm |
| **v2.2** | Multi-DN | ~5-7 ngày | Mở rộng customer segment (agency, holding) |
| **v2.3** | 6 packs mới | ~10 ngày | Mở rộng ngành phục vụ |

**Tổng v1.1 + v2:** ~33-44 ngày FT-equivalent.

---

## Decision framework — khi nào start v2?

Sau ≥ 2-4 tuần dùng v1 thực tế, ghi chú vào `vault/00-Brain/decisions-log.md`:

| Pain point ghi nhận | → Ưu tiên feature |
|---|---|
| "Mỏi tay gõ CLI quá" | Web UI Dashboard |
| "Quên chạy báo cáo tuần" | Auto-loop cron |
| "Muốn dùng cho DN khác của mình" | Multi-DN |
| "Ngành mình khác F&B/Retail/Tech" | Pack mới |
| "Output có lỗi chính tả" | pyvi spell-check |
| "Bạn dùng Codex thay Claude" | Codex adapter |

---

## Anti-patterns — KHÔNG làm

❌ **KHÔNG build v2 trước khi v1 dùng thực tế ≥ 2 tuần.** Pain point dự đoán thường khác pain point thực tế.

❌ **KHÔNG over-engineer Web UI.** Mục tiêu là CEO non-tech dùng được, không phải replicate Notion.

❌ **KHÔNG add packs trước khi có DN demo dùng pack đó.** Mỗi pack cần 1 user thật để test compliance refs đúng.

❌ **KHÔNG break v1 API khi build v2.** Multi-DN phải backward-compatible: single-DN flow vẫn chạy như cũ.

❌ **KHÔNG copy-paste pattern v1 mà không refactor.** Sau 6 phases có thể đã có code lặp — clean up trước khi extend.

---

## Open questions cho v2 (chờ CEO trả lời lúc start)

1. **Web UI auth**: local-only hay support multi-user nội bộ DN?
2. **Cron daemon**: chạy như Windows service / systemd hay cron script đơn giản?
3. **Multi-DN config**: lưu API keys riêng từng DN hay share global?
4. **Pack contribution**: mở source contributor cho packs mới hay tự build hết?
5. **Web UI tech stack**: HTMX (đơn giản) hay React (rich)? Phụ thuộc CEO có dev frontend không.
6. **Notification channels**: chỉ email hay thêm Telegram/Zalo (phổ biến VN)?
7. **pyvi**: thật sự cần hay LLM tự handle chính tả tốt rồi?

---

## Cross-reference

- **v1 SPEC**: `SPEC.md`
- **v1 phase plans**: `plans/phase-01-foundation.md` → `plans/phase-06-adapters-e2e-onboard.md`
- **v1 decisions**: `DECISIONS.md`
- **v1 ship status**: tag `v0.1.0`

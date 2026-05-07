# 🚦 START HERE — Bootstrap cho Claude Code session mới

> **Đọc file này TRƯỚC KHI làm bất cứ việc gì.**
> File này được thiết kế để 1 Claude Code session mới (KHÔNG có context từ session brainstorm) có thể tiếp nối công việc một cách an toàn.

---

## ⚡ Bootstrap nhanh (CEO copy-paste prompt này vào session mới)

Copy nguyên đoạn dưới đây, paste vào Claude Code:

```
TÔI CÓ 1 PROJECT ĐÃ BRAINSTORM VÀ PLAN XONG TRONG SESSION TRƯỚC.

NHIỆM VỤ CỦA BẠN:

Bước 1 — Hiểu context (KHÔNG được skip):
1. Đọc file START-HERE.md (file này) — tổng quan
2. Đọc DECISIONS.md — 8 decisions + 6 RULES bất di bất dịch
3. Đọc README.md — entry point
4. Đọc SPEC.md — design spec đầy đủ
5. Đọc plans/plan.md — overview 6 phase
6. Skim plans/phase-01-foundation.md — biết task đầu tiên

Bước 2 — Verify understanding (BẮT BUỘC):
Sau khi đọc, trả lời cho tôi 4 câu sau (ngắn gọn, mỗi câu 1-2 dòng):
A. Project này build cái gì? (1 câu)
B. 6 RULES là gì? (liệt kê tên thôi)
C. Phase 1 có bao nhiêu task? Task đầu tiên là gì?
D. Stack tech chính là gì?

Bước 3 — Đợi tôi confirm:
Sau khi trả lời 4 câu trên, ĐỪNG làm gì thêm. Đợi tôi nói "OK chính xác, làm tiếp" rồi mới start implementation.

Bước 4 — Implementation:
Khi tôi confirm, dùng skill `superpowers:subagent-driven-development` để chạy Phase 1.
Repo gốc tạo NGAY tại folder hiện tại (KHÔNG tạo subfolder vn-business-os).

LƯU Ý:
- Tôi là CEO/owner (your-email@example.com)
- Mọi code phải tuân thủ 6 RULES trong DECISIONS.md
- Mọi output cho tôi phải tiếng Việt + định nghĩa thuật ngữ + có TL;DR (RULE 4)
```

---

## 📂 Bản đồ folder

```
26. One Company/
├── START-HERE.md         ← FILE NÀY (đọc đầu tiên)
├── README.md             ← overview project + status
├── DECISIONS.md          ← 8 decisions + 6 RULES (CỰC QUAN TRỌNG)
├── SESSION-LOG.md        ← toàn bộ trao đổi session brainstorm
├── SPEC.md               ← design spec hoàn chỉnh
├── NEXT-STEPS.md         ← chi tiết hướng dẫn step-by-step
└── plans/
    ├── plan.md                                      ← overview 6 phase
    ├── phase-01-foundation.md                       ← 12 task
    ├── phase-02-debate-engine.md                    ← 8 task
    ├── phase-03-orchestrator-brain-first.md         ← 9 task
    ├── phase-04-tools-translator.md                 ← 14 task
    ├── phase-05-departments-packs-byot.md           ← 12 task
    └── phase-06-adapters-e2e-onboard.md             ← 10 task
```

---

## 🔑 4 thông tin tối quan trọng (nếu Claude session mới chỉ đọc 1 đoạn → đọc đoạn này)

### 1. Mình là ai?
- **CEO/Owner repo:** `your-email@example.com` (chính là tôi, người đang chat)
- **`references/business-builder.plugin`:** file zip nguồn — chứa 191 template tiếng Việt được vendor vào `templates-vn/`

### 2. Project là gì?
**VN Business OS** — open-source AI agent OS cho DN nhỏ-vừa Việt Nam:
- CEO chat brief → AI agents (phòng ban) họp bàn debate → sinh báo cáo + tài liệu .docx/.xlsx
- Tuân thủ ISO 9001 + Luật DN VN 2020 + BLLĐ 2019 + Luật KT 2015
- Phân loại task: SIMPLE / COMPLEX / STRATEGIC
- Stack: Python + LangGraph + Obsidian + multi-tool entry (Claude Code/Cowork)

### 3. 6 RULES bất di bất dịch
1. **Brain-first clarification** — đọc Brain (`vault/00-Brain/*.md`) TRƯỚC khi hỏi CEO; mỗi câu hỏi PHẢI cite Brain
2. **Domain-neutral engine** — code bóc từ TradingAgents PHẢI rename hết Bull/Bear/trade/finance/ticker
3. **Single source of truth** — Obsidian vault là sự thật, SQLite chỉ cache
4. **CEO-friendly language** — tiếng Việt, định nghĩa thuật ngữ, TL;DR đầu báo cáo
5. **Live research with citations** — search luật/đối thủ/benchmark, cite URL + ngày
6. **BYOT** — template DN custom > pack > default (191 template từ bb-plugin)

### 4. Plan tổng
- 6 phase, 65 task tổng, ~330 step bite-sized
- Phase 1 ~12 task, ~1-2 giờ tool calls
- Approach: Hybrid — bóc engine LangGraph từ TradingAgents + tự code Brain/Clarifier/Tools/Translator
- Test case v1: chiến dịch QC nhắm khách thu nhập 50tr+ (5 phòng họp, 3 vòng debate)

---

## ⚠️ Anti-patterns (để Claude session mới không làm sai)

| ❌ KHÔNG làm | ✅ NÊN làm |
|---|---|
| Skip đọc DECISIONS.md vì "nghĩ đã biết" | Đọc kỹ 6 RULES, cite được khi cần |
| Tạo subfolder `vn-business-os/` | Tạo trực tiếp tại CWD (`26. One Company/`) |
| Tự bịa số liệu / luật VN | Search live qua tools (RULE 5) |
| Output tiếng Anh hoặc full jargon | Tiếng Việt + định nghĩa + TL;DR (RULE 4) |
| Skip check 6 RULES mỗi commit | Run `scripts/dev/check-domain-neutral.sh` |
| Spawn 65 task song song | Sequential — implementer → spec reviewer → quality reviewer |
| Implement không follow plan | Đọc phase file → bám sát task # và step # |
| Hỏi user khi chưa đọc Brain | Brain-first ALWAYS (RULE 1) |

---

## 🆘 Nếu session mới có vẻ không hiểu

CEO có thể paste lại đoạn này:

```
Đợi đã. Hãy đọc lại START-HERE.md + DECISIONS.md từ đầu, đặc biệt là 6 RULES.
Sau đó kể lại cho tôi nghe project này là gì + 6 RULES có ý nghĩa gì.
KHÔNG làm gì khác cho đến khi tôi confirm.
```

Hoặc reset đơn giản hơn:
```
Bạn có vẻ chưa hiểu context. /clear rồi paste lại bootstrap prompt từ START-HERE.md
```

---

## 🎯 Sau khi Phase 1 done

Verify checklist (CEO chạy):

```bash
cd "F:\OneDrive - www.KeyBanQuyen.VN\Documents\GitHub\26. One Company"

# 1. pip install
pip install -e .
# expect: Successfully installed vn-business-os-0.1.0

# 2. CLI work
vn-os --version
# expect: 0.1.0

# 3. Brain reader work
vn-os status --vault tests/fixtures/demo-vault
# expect: green checks for Brain

# 4. Smoke test pass
pytest tests/integration/test_phase01_smoke.py -v
# expect: 4 passed

# 5. Templates vendored
find templates-vn -name "*.md" | wc -l
# expect: 191
```

Nếu 5 checks đều ✅ → Phase 1 done, có thể tiếp Phase 2.

---

## 📌 Note credits (khi public repo)

Bắt buộc ghi credit trong README/LICENSE/NOTICE:
- **191 template tiếng Việt** trong `templates-vn/` adapted from `references/business-builder.plugin`
- **Engine debate pattern** adapted from [TradingAgents](https://github.com/TauricResearch/TradingAgents)
- **Role definitions reference** từ [agency-agents](https://github.com/msitarzewski/agency-agents)

---

**Sẵn sàng. CEO `/compact` rồi paste bootstrap prompt ở đầu file này.**

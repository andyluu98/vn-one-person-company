# Next Steps — Sau khi compact

> Hướng dẫn cho session Claude Code tiếp theo (sau khi `/compact`).

---

## 🎯 Bước 1 — Khởi động session mới

Mở Claude Code session mới tại folder này:
```
F:\OneDrive - www.KeyBanQuyen.VN\Documents\GitHub\26. One Company
```

Paste prompt khởi động:

```
Đọc các file sau theo thứ tự để hiểu context:
1. README.md          — overview project
2. DECISIONS.md       — 6 RULES + 8 decisions đã chốt
3. SESSION-LOG.md     — toàn bộ trao đổi brainstorm
4. SPEC.md            — design spec hoàn chỉnh
5. plans/plan.md      — overview 6 phase
6. plans/phase-01-foundation.md — task chi tiết Phase 1

Sau khi đọc xong, dùng skill superpowers:subagent-driven-development để implement Phase 1.
12 task trong Phase 1 — spawn implementer + 2 reviewer (spec + quality) cho mỗi task.
Repo gốc tạo NGAY tại folder hiện tại (không tạo subfolder vn-business-os).
```

---

## 🔑 Yêu cầu môi trường

Trước khi run, đảm bảo có:

```bash
# Python 3.11+
python --version

# API keys (export trước khi chạy)
export ANTHROPIC_API_KEY=sk-ant-...     # bắt buộc
export TAVILY_API_KEY=tvly-...           # cho Phase 4 (tools)

# Git config (nếu chưa có)
git config --global user.name "<your name>"
git config --global user.email "your-email@example.com"
```

---

## 📋 Kỳ vọng output sau Phase 1

Cấu trúc sau khi Phase 1 done:

```
26. One Company/
├── pyproject.toml
├── README.md (đã có — mình ghi đè khi Phase 1 Task 1)
├── LICENSE (MIT)
├── .gitignore
├── core/
│   ├── __init__.py
│   ├── cli.py
│   ├── brain/
│   │   ├── schema.py
│   │   ├── reader.py
│   │   └── memory.py
│   ├── obsidian/
│   │   ├── frontmatter.py
│   │   └── vault.py
│   ├── agents/
│   │   └── department.py
│   ├── llm/
│   │   └── providers.py
│   └── utils/
│       └── config.py
├── departments/                  # 12 dept folders
├── templates-vn/                 # 191 .md từ bb-plugin (vendored)
├── vault-template/               # Obsidian scaffold
├── tests/
│   ├── unit/                     # ~10 test file
│   ├── integration/
│   │   └── test_phase01_smoke.py
│   └── fixtures/
│       └── demo-vault/
├── scripts/
│   └── dev/
│       ├── vendor-bb-plugin.sh
│       └── create-dept-stubs.sh
├── plans/                        # đã có
├── DECISIONS.md                  # đã có
├── SESSION-LOG.md                # đã có
├── SPEC.md                       # đã có
└── NEXT-STEPS.md                 # file này
```

Verify Phase 1:
```bash
pip install -e .
vn-os --version                    # 0.1.0
vn-os status --vault tests/fixtures/demo-vault   # green checks
pytest tests/integration/test_phase01_smoke.py -v
git tag | grep phase-01-complete
```

---

## ⚠️ Lưu ý quan trọng cho session sau

### 1. Vendor bb-plugin
Phase 1 Task 3 cần file `business-builder.plugin` ở:
```
F:\OneDrive - www.KeyBanQuyen.VN\Documents\GitHub\24. Agent company\business-builder.plugin
```
Hoặc copy file đó sang `26. One Company/` rồi run script.

### 2. KHÔNG để file Python ngoài 200 dòng
Theo development-rules.md global. Mỗi module focused 1 trách nhiệm.

### 3. Domain-neutral check (RULE 2)
Sau Phase 2 (bóc engine từ TradingAgents), MỖI commit phải pass:
```bash
bash scripts/dev/check-domain-neutral.sh
```

### 4. Ngôn ngữ
- System prompt agent: **tiếng Việt 100%**
- Code comment: tiếng Việt OK (CEO Việt)
- Variable / function name: English (Python convention)
- Output cho CEO: **tiếng Việt + định nghĩa thuật ngữ + TL;DR (RULE 4)**

### 5. Test với mock LLM
- CI dùng mock (không tốn API)
- E2E real LLM gated bởi env `RUN_REAL_LLM=1`

---

## 🗺️ Lộ trình tổng

| Phase | Task | Dự kiến |
|:-:|:-:|---|
| 1 | 12 | Sau Phase 1 done → review → quyết tiếp |
| 2 | 8 | Debate engine (LangGraph) |
| 3 | 9 | Orchestrator + Brain-first clarification |
| 4 | 14 | Tools + Translator |
| 5 | 12 | Departments full + 3 packs + BYOT |
| 6 | 10 | Adapters + E2E + Onboard wizard |

Sau khi Phase 6 done → tag `v0.1.0` → ship được v1.

---

## 📞 Tác giả & nguồn tham chiếu

**CEO / Repo owner:** `your-email@example.com`

**Vendored content credit:**
- 191 template tiếng Việt trong `templates-vn/` lấy từ `references/business-builder.plugin`.
- Engine debate (LangGraph pattern) bóc từ **TradingAgents** (TauricResearch).
- Role definitions reference từ **agency-agents** (msitarzewski).

---

## 🚦 TL;DR cho CEO

1. Mọi thứ đã chuẩn bị xong, plan chi tiết 65 task ở `plans/`
2. Session sau chỉ cần paste prompt khởi động ở Bước 1
3. Phase 1 ~1-2 giờ tool calls. Sau đó review rồi quyết tiếp.
4. KHÔNG được vi phạm 6 RULES trong `DECISIONS.md`.

Sẵn sàng. Đợi CEO `/compact` rồi paste prompt.

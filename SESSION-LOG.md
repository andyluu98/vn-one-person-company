# Session Log — Brainstorm "One Person Company" VN

**Khoảng thời gian:** 2026-05-05 22:46 → 2026-05-06 00:56 (Asia/Bangkok)
**CEO (user):** your-email@example.com
**Đối tác AI:** Claude Code (Opus 4.7)
**Mục tiêu:** Brainstorm + thiết kế + plan chi tiết cho repo open-source AI agent OS dành cho doanh nghiệp Việt Nam.

---

## 1. Mạch đối thoại (chronological)

### 1.1 Khám phá repo gốc
CEO yêu cầu đọc dự án `F:\OneDrive\...\24. Agent company`. Mình phát hiện:
- Đây là fork của `msitarzewski/agency-agents` — 144 file `.md` role definitions cho Claude Code, không có code Python.
- Có thêm folder `strategy/` chứa NEXUS Orchestration framework (manual handoff doc).
- Có file `business-builder.plugin` (zip archive) — Claude plugin tiếng Việt với 13 skill (`bb-orchestrator`, `bb-governance`, ..., `bb-growth`) chứa 191 template tài liệu vận hành DN VN tuân thủ ISO 9001 + Luật DN 2020 + BLLĐ 2019 + Luật KT 2015.
- Có PDF hướng dẫn "Business Builder Plugin v0.3.0".
- Có file note `agency-agents thật sự là gì — giải.txt` — phân tích của CEO chỉ ra agency-agents là static prompt library, thiếu strategy propagation, inter-agent memory, auto trigger, state management.

### 1.2 CEO mô tả mong muốn
> "Tôi muốn xây dựng công ty kiểu one person company ở Việt Nam, lấy source Việt Nam template có sẵn làm chính, dữ liệu sẽ được agent tạo ra và lưu trên Obsidian, mỗi con agent sẽ là 1 phòng ban khác nhau... CEO giao việc xuống thì sẽ tự sinh ra dữ liệu mới tự gọi agent các phòng ban họp bàn với nhau rồi cho ra kết quả... AI nói chuyện với nhau để đánh giá rồi làm 1 cái báo cáo, nếu đồng ý thì sẽ thành 1 bản kế hoạch triển khai... có những nghiệp vụ phải phối hợp, có những nghiệp vụ đơn giản... agent sẽ phản biện với nhau."

CEO yêu cầu tham khảo:
- https://github.com/msitarzewski/agency-agents
- https://github.com/TauricResearch/TradingAgents

### 1.3 Mình research kỹ 2 repo
Báo cáo: `plans/reports/researcher-260505-2323-tradingagents-vs-agency-agents.md`. Kết luận:

| | TradingAgents | agency-agents |
|---|---|---|
| Code chạy thật? | ✅ Python+LangGraph | ❌ chỉ markdown |
| Debate thật? | ✅ Bull/Bear + 3-tier risk | ❌ static prompt |
| State persist? | ✅ SQLite checkpoint | ❌ |
| Multi-LLM? | ✅ 8 providers | ❌ |

→ Để build cái CEO muốn (debate thật giữa phòng ban), **PHẢI có code thật như TradingAgents**, không thể dừng ở markdown.

### 1.4 Brainstorm 5 câu (CEO trả lời)

**Q1 — Setup approach:**
A. Clone manual / B. Wizard onboarding / C. SaaS / D. Hybrid A+B
→ **CEO chọn A+B (Hybrid open source)**

**Q2 — Bộ phòng ban:**
A. Fixed 13 / B. Core + industry packs / C. Hoàn toàn động / D. Core + on-demand creator
→ **CEO chọn A+B+D (Core 13 + Packs + On-demand)**

**Q3 — MVP scope:**
A. Core only / B. Core + 1 pack / C. Core + 3 packs (F&B + Retail + Tech) / D. Core + framework
→ **CEO chọn C (Core + 3 packs)**

**Q4 — Auto level:**
A. Manual stepping / B. Semi-auto 2 stops / C. Full-auto / D. Auto-loop cron
→ **CEO chọn B + Brain-first clarification**

CEO bổ sung quan trọng: *"hỏi thì phải dựa vào dữ liệu phòng ban hoặc tình hình hiện tại mới hỏi chứ không phải tự sinh câu hỏi mà không có dữ liệu công ty"*
→ Lock cứng thành **RULE 1 — Brain-first clarification**.

**Q5 — Storage:**
A. Local-only / B. Local + Git private / C. Cloud sync / D. Hybrid / E. Folder thuần
→ **CEO chọn B (Local + Git private)**

### 1.5 Bonus: Stack thực thi
CEO nhắc: *"đối với repo này nó không phải là md không nhé"* → đồng ý không thể dừng ở markdown.

Mình propose 4 options:
A. Python+LangGraph CLI / B. + Web UI / C. Claude Code skill+Python / D. Hybrid Python core + Obsidian + multi-adapter
→ **CEO chọn D + multi-tool entry (Claude Code, Cowork, sau là Codex/Antigravity)**

### 1.6 Approach (3 options)
🅰️ Fork TradingAgents (3 tuần) / 🅱️ Build từ đầu LangGraph (5-6 tuần) / 🅲 Hybrid (4 tuần)
→ **CEO chọn C (Hybrid)** — nhấn mạnh KHÔNG phải DN trade.

→ Lock thành **RULE 2 — Domain-neutral engine**.

### 1.7 Test case v1
A. Onboarding / B. Chiến dịch QC nhắm khách thu nhập 50tr+ / C. Simple JD / D. Cả 3
→ **CEO chọn B trước, sau đó A+C khi B xong**.

CEO nhấn lại RULE 1 lần nữa.

### 1.8 Trình bày design 7 phần (CEO duyệt từng phần)
- Phần 1: Kiến trúc 4 lớp + 3 nguyên tắc → ✅ OK
- Phần 2: Cấu trúc repo → ✅ OK
- Phần 3: Core modules chi tiết → ✅ OK
- Phần 4: Department + Agent + Pack abstraction → ✅ OK ("bạn làm tốt lắm tiếp tục")
- Phần 5: Industry packs nội dung (F&B / Retail / Tech-SaaS) → ✅ OK ("ok tốt lắm")
- Phần 6: Data flow E2E test case B → CEO bổ sung 2 yêu cầu lớn:
  - **CEO-friendly language** (định nghĩa thuật ngữ, TL;DR, dân thường hiểu)
  - **Live research** (luật, đối thủ, benchmark, thuế)
  → Lock thành **RULE 4 + RULE 5**.
- Phần 6.5: Update kiến trúc với Translator + Tools modules → CEO ngầm OK
- Phần 7: Error handling + Testing + Roadmap → CEO ngầm OK

### 1.9 BYOT (CEO bổ sung phút cuối)
> "nếu doanh nghiệp có tài liệu sẵn thì có thể đưa template vào để ra đúng ví dụ như hợp đồng dấu biểu mẫu gì đó... với lại tham khảo cái plugin vì nó sát với doanh nghiệp việt nam đó"

→ Lock thành **RULE 6 — BYOT (Bring Your Own Templates)**.
→ Quyết định bundle 191 template từ bb-plugin vào `templates-vn/` của repo.

### 1.10 Spec doc + plan
- Spec lưu tại: `docs/superpowers/specs/2026-05-06-vn-business-os-design.md` (~330 dòng)
- Plan lưu tại: `plans/260506-0011-vn-business-os/` gồm `plan.md` + 6 phase file (~3500 dòng tổng, 65 task, ~330 step bite-sized)

### 1.11 CEO chọn execution
- Subagent-driven-development → option 1
- Vị trí repo: `F:\OneDrive\...\26. One Company`
- Scope: chưa chốt (4 gói Y/Z/W/X)
- Yêu cầu: **ghi lại toàn bộ + plan đầy đủ vào folder mới + compact session**

---

## 2. Input nguồn (3 file CEO gửi vào session)

### 2.1 `agency-agents thật sự là gì — giải.txt` (CEO viết trước)
- Phân tích: agency-agents là static prompt library, không có inter-agent communication thật.
- Chỉ ra 4 thiếu hụt: strategy propagation, inter-agent memory, trigger tự động, state management.
- Đề xuất: COMPANY_STRATEGY.md + shared memory + orchestrator layer.

### 2.2 `Huong-Dan-Su-Dung-Business-Builder-Plugin-v0.3.0.pdf`
- Tháng 4/2026
- Plugin Business Builder — 13 skill, 191 tài liệu, kiến trúc 5 tầng
- Tuân thủ ISO 9001:2015, EOS/Traction, E-Myth, McKinsey 7S, SYSTEMology, Franchise Ops + Luật DN 2020 + BLLĐ 2019 + Luật KT 2015

### 2.3 `business-builder.plugin` (zip)
- 207 file, ~380KB
- 13 skill folders: bb-orchestrator, bb-governance (19 docs), bb-strategy (18), bb-finance (20), bb-people (22), bb-operations (20), bb-sales (17), bb-marketing (10), bb-customer (12), bb-product-tech (13), bb-training (10), bb-reporting (10), bb-growth (12)

---

## 3. Reference repos đã research

### 3.1 TradingAgents (TauricResearch/TradingAgents)
- **Stack:** Python 3.13, LangGraph, multi-LLM (8 providers), SQLite checkpoint
- **9 agents:** 4 analysts → 2 researchers (Bull/Bear debate) → 1 trader → 3 risk managers (aggressive/conservative/neutral)
- **Debate:** 2 vòng research debate, N vòng risk debate
- **State:** TypedDict (LangGraph MessagesState) + SQLite persistence
- **UI:** Interactive CLI + Python API embedding

### 3.2 agency-agents (msitarzewski/agency-agents)
- **172 markdown role definitions** (academic, design, engineering 29, finance, game-dev, marketing 30, paid-media, product, project-mgmt, sales, specialized 41, strategy, support, testing, spatial-computing)
- **No runtime** — static prompt templates
- **Bash convert.sh + install.sh** convert tới 11 tool (Claude Code, Copilot, Antigravity, Gemini CLI, OpenCode, Cursor, Aider, Windsurf, OpenClaw, Qwen, Kimi)

---

## 4. Quyết định kiến trúc cuối cùng

### 4.1 Kiến trúc 4 lớp
```
LỚP 1 — ENTRY (CEO chat)
  Adapters: Claude Code · Cowork · (v2: Codex/Antigrav)
LỚP 2 — CORE (Python + LangGraph)
  Orchestrator · Brain · Clarifier · Translator
  Meeting (debate) · Tools (research) · LLM
LỚP 3 — STATE
  SQLite (checkpoint) + Obsidian (Git private)
LỚP 4 — OUTPUT
  Markdown reports · .docx/.xlsx · Decisions log
```

### 4.2 Hybrid approach (Approach C)
- **Bóc engine** (graph + state machine + checkpoint) từ TradingAgents → rename neutral hoàn toàn
- **Tự code** Brain layer + Clarifier + Tools + Translator + Adapters + Packs
- **Vendor 191 template** từ bb-plugin → `templates-vn/`

### 4.3 6 RULES (xem `DECISIONS.md` để biết enforce ở đâu)
1. Brain-first clarification
2. Domain-neutral engine
3. Single source of truth (Obsidian)
4. CEO-friendly language
5. Live research with citations
6. BYOT (template DN > pack > default)

### 4.4 Stack tech
- Python 3.11+, LangGraph 0.2+, LangChain core, Pydantic v2
- python-docx, openpyxl, PyYAML
- Tavily (web search), Anthropic SDK (default LLM), google-genai, openai
- pytest, ruff, mypy, click, rich, gitpython
- SQLite checkpoint

### 4.5 Cấu trúc data flow (test case B)
```
brief → router → gap analysis → clarification (PAUSE)
     → research phase (tools parallel)
     → meeting R1 (perspectives parallel) → R2 (Pro/Con debate) → R3 (Growth/Cautious/Balanced)
     → synthesizer (TL;DR + jargon defined)
     → 07-decision-report.md (PAUSE — CEO duyệt)
     → execution dispatcher
     → 08-execution-plan.md (PAUSE — CEO duyệt)
     → doc writer (.docx + .xlsx) → outputs/
     → memory append + git auto-commit
```

Time: 15-25 phút/task COMPLEX. CEO ngồi máy ~10 phút. Cost: ~$0.5-1.5/task.

---

## 5. Plan triển khai (xem `plans/`)

| Phase | File | Tasks | Mục tiêu |
|:-:|---|:-:|---|
| 1 | `phase-01-foundation.md` | 12 | Repo skeleton + Brain + 13 dept stubs + 191 template vendored |
| 2 | `phase-02-debate-engine.md` | 8 | LangGraph + Pro/Con + 3 perspective debators (neutral) |
| 3 | `phase-03-orchestrator-brain-first.md` | 9 | Router + Gap analyzer + Clarifier + FlowController (Stop 1) |
| 4 | `phase-04-tools-translator.md` | 14 | 6 tools live research + Glossary + Simplifier + TL;DR |
| 5 | `phase-05-departments-packs-byot.md` | 12 | 13 dept full + 3 pack + BYOT TemplateResolver + DocWriter |
| 6 | `phase-06-adapters-e2e-onboard.md` | 10 | Wizard + Claude Code/Cowork adapter + E2E test B + CI |

**Total: 65 tasks, ~330 step bite-sized, ~6 tuần FT-equivalent.**

---

## 6. Trạng thái session khi dừng

- ✅ Brainstorm complete
- ✅ Spec written + self-review pass
- ✅ Plan written (65 tasks, 6 phases)
- ✅ Files copied vào `26. One Company/`
- ⏳ **Implementation chưa bắt đầu** (CEO yêu cầu compact trước)

## 7. Hướng dẫn cho session tiếp theo

Xem `NEXT-STEPS.md` (sẽ tạo).

Tóm tắt: prompt session mới với:
> "Đọc README.md + DECISIONS.md + SPEC.md + plans/plan.md trong folder này.
> Bắt đầu Phase 1 implementation tại folder hiện tại theo subagent-driven-development.
> Đọc phase-01-foundation.md để biết task cụ thể."

---

## 8. Đặc điểm quan trọng cần nhớ

- **CEO (người dùng repo này):** `your-email@example.com` — đang xây hệ thống cho DN của mình + dự định open-source.
- `business-builder.plugin` (file zip có sẵn trong `references/`) là nguồn 191 template được vendor vào `templates-vn/`. KHÔNG attribute author cá nhân.
- **CEO ưu tiên:** ngôn ngữ dễ hiểu (RULE 4), không bịa (RULE 5 cite nguồn), tận dụng template VN có sẵn (RULE 6 BYOT + bundle bb-plugin).
- **CEO không thích:** từ chuyên ngành abstract, AI tự bịa số liệu, plugin chỉ generate text mà không debate.
- **CEO yêu cầu:** mọi câu hỏi phải dẫn nguồn Brain, không hỏi linh tinh khi chưa có context DN.

## 9. Files quan trọng đã tạo trong `24. Agent company` (nguồn)

```
24. Agent company/
├── docs/superpowers/specs/
│   └── 2026-05-06-vn-business-os-design.md      # SPEC
├── plans/
│   ├── 260506-0011-vn-business-os/
│   │   ├── plan.md
│   │   └── phase-0[1-6]-*.md                    # 6 phase plans
│   └── reports/
│       └── researcher-260505-2323-tradingagents-vs-agency-agents.md
└── (3 file CEO gửi: agency-agents giải.txt, PDF guide, business-builder.plugin)
```

Tất cả đã được copy / consolidate vào `26. One Company/`.

# Architecture

> Kiến trúc kỹ thuật + 6 RULES + extensibility points. Đối tượng: developer + tech-aware CEO.

## 4 lớp

```
Lớp 1 — ENTRY (CEO chat)
  Adapters: Claude Code, Cowork, Codex (v2), Antigravity (v2)

Lớp 2 — CORE (Python + LangGraph)
  Orchestrator (Router, FlowController) - core/orchestrator/
  Brain (Reader, Schema, GapAnalyzer, Memory) - core/brain/
  Clarifier (QuestionGenerator, ClarificationIO) - core/clarifier/
  Translator (Glossary, Jargon, Simplifier, TLDR) - core/translator/
  Meeting (debate_state, conditional_logic, synthesizer, meeting_graph) - core/meeting/
  Agents (BaseAgent, Pro/Con, Perspective, Department, Registry) - core/agents/
  Tools (web_search, vn_law, competitor, benchmark, tax) - core/tools/
  LLM (multi-provider abstraction) - core/llm/

Lớp 3 — STATE
  SQLite (LangGraph checkpoint) — phục hồi crash only
  Obsidian vault (Git private) — single source of truth (RULE 3)

Lớp 4 — OUTPUT
  Markdown reports trong 02-Tasks/
  .docx/.xlsx trong 03-Outputs/
  Decisions log append-only
```

## Data flow chuẩn

```
CEO brief
  → Brain reader (load 00-Brain/*.md)
  → Router (classify SIMPLE/COMPLEX/STRATEGIC + chọn phòng)
  → Gap analyzer (so brief vs Brain, RULE 1)
  → Clarifier (hỏi CEO, có citation Brain) — STOP nếu cần
  → Research phase (tools parallel, RULE 5)
  → Meeting R1 (perspectives — mỗi phòng song song)
  → Meeting R2 (Pro vs Con, 2-3 lượt)
  → Meeting R3 (Growth/Cautious/Balanced)
  → Synthesizer (decision report, RULE 4)
  → CEO duyệt (Stop 1)
  → Execution dispatcher (plan)
  → CEO duyệt (Stop 2)
  → DocWriter (.docx/.xlsx vào 03-Outputs/)
  → Memory append + Git auto-commit
```

## 6 RULES enforce trong code

| Rule | Module | Enforce point |
|---|---|---|
| 1 — Brain-first | core/clarifier/question_generator.py | `if not gaps: return []` |
| 2 — Domain-neutral | scripts/dev/check-domain-neutral.sh | CI fail nếu thấy bull/bear/trader/ticker |
| 3 — Single source of truth | core/obsidian/vault.py | Tất cả I/O qua ObsidianVault |
| 4 — CEO-friendly language | core/translator/pipeline.py | jargon detector + simplifier + TL;DR |
| 5 — Live research with citations | core/tools/base_tool.py | ToolResult.sources + retrieved_at bắt buộc |
| 6 — BYOT | core/obsidian/template_resolver.py | Custom > pack > default order |

## Stack

- Python 3.11+
- LangGraph 0.2+ (state graph + checkpointer)
- Pydantic v2 (schema validation)
- Obsidian Markdown (vault format)
- SQLite (checkpoint + tool cache)
- python-docx + openpyxl (output rendering)
- Tavily API (web search + VN law/local regulation)
- **MCP Sampling** qua Claude Desktop subscription (default — KHÔNG cần API key)
- Anthropic SDK (fallback nếu chạy ngoài MCP)
- Optional: Google Gemini, OpenAI fallbacks

## v0.2.0 architecture: MCP Sampling

```
┌─ Claude Desktop GUI ───────────────────────────┐
│  CEO chat với Claude Sonnet                    │
│       ↓                                         │
│  Claude calls MCP tool vn_meeting               │
│       ↓                                         │
│  ┌─ MCP Server (vn-business-os) ─────────────┐ │
│  │  FlowController.run_meeting()             │ │
│  │       ↓                                    │ │
│  │  llm.complete(messages)                    │ │
│  │       ↓                                    │ │
│  │  MCPSamplingProvider                       │ │
│  │       ↓                                    │ │
│  │  ctx.session.create_message(...)  ─────┐  │ │
│  └────────────────────────────────────────┼──┘ │
│                                            ↓    │
│  Sampling request returns to Claude       │    │
│  Claude generates response                │    │
│  Response back to MCP server  ←───────────┘    │
└─────────────────────────────────────────────────┘
```

→ Plugin chạy bên trong Claude Desktop session, mỗi LLM call route qua subscription user. Không cần API key Anthropic.

## Cost budget

| Component | Per task COMPLEX |
|---|---|
| Router classify | ~$0.01 |
| Gap analysis | ~$0.05 |
| Question gen | ~$0.02 |
| Tool calls (3 tools) | ~$0.10 |
| Perspectives (5 phòng × 1 turn) | ~$0.30 |
| Pro/Con debate (2 round × 2 = 4 turns) | ~$0.40 |
| Perspective debate (3 voices × 1 round) | ~$0.30 |
| Synthesizer | ~$0.20 |
| Translator (simplify + TL;DR) | ~$0.10 |
| **Total** | **~$1.50/task** |
| Limit | <$2.00/task |

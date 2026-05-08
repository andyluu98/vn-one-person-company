# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

AI Operating System cho solo founder VN. CEO chat → 12+ phòng ban AI agents debate → ra quyết định → sinh `.docx/.xlsx` tuân thủ luật VN. Chạy qua MCP sampling trong Claude Desktop — không cần Anthropic API key riêng.

## Commands

```bash
# Install (dev)
python -m venv .venv && .venv/Scripts/activate  # Windows
pip install -e ".[dev]"

# Cài MCP vào Claude Desktop
vn-os install-mcp
vn-os install-mcp --vault "F:/work/xyz-vault"   # inject vault path

# Run tests
python -m pytest tests/ -q                        # all (261 tests)
python -m pytest tests/unit/test_router.py -q     # single file
python -m pytest tests/unit/ -q                   # unit only
python -m pytest tests/integration/ -q            # integration only

# Lint / format
ruff check core/ tests/
ruff format core/ tests/

# CLI (development)
vn-os status --vault <path>
vn-os run "brief" --vault <path>
```

## Architecture

### 5-Stage Flow

```
vn_run → PAUSE_CLARIFICATION → vn_resume → vn_meeting
       → PAUSE_DECISION_REPORT → vn_approve → vn_execute → DONE
```

`FlowController` (`core/orchestrator/flow_controller.py`) điều phối toàn bộ. Hai điểm dừng bắt buộc CEO duyệt trước khi tiếp.

### Core modules

| Module | Vai trò |
|--------|---------|
| `core/brain/` | Đọc vault `00-Brain/` → `BrainContext` (strategy, products, budget, headcount) |
| `core/clarifier/` | Phát hiện gap trong Brain → sinh câu hỏi có citation, ghi `03-clarification.md` |
| `core/orchestrator/` | Router phân loại task, FlowController, research phase, execution planner |
| `core/meeting/` | LangGraph debate graph — Pro/Con Advocate rounds → Perspective Debators → Synthesizer |
| `core/agents/` | Agent loader + registry, base agent, pack loader |
| `core/translator/` | Jargon detector → simplifier → TL;DR (3 modes: off/final_only/all_intermediate) |
| `core/tools/` | `vn_law_search`, `competitor_research`, `tax_calculator`, `web_search`, etc. Cache 24h. |
| `core/obsidian/` | Vault read/write, wikilinks, template resolver (BYOT 3-level priority) |
| `core/llm/providers.py` | `MCPSamplingProvider` (Claude Desktop), `ClaudeProvider` (direct API), `DeepSeekProvider` |

### LLM routing

Ưu tiên: MCP sampling (qua Claude Desktop session) → env `ANTHROPIC_API_KEY` → `GOOGLE_API_KEY` → `OPENAI_API_KEY`. Config trong `<vault>/.vncoderc`.

### Departments + Packs

- `departments/` — 12 phòng ban core (01-governance … 12-growth), mỗi phòng có `config.yaml` + prompt templates
- `packs/` — industry overlays: `fnb/`, `retail/`, `tech-saas/` (thêm phòng + templates ngành)
- `templates-vn/` — 192 template mặc định (thấp nhất trong BYOT chain)

### Vault structure (runtime)

```
<vault>/
├── 00-Brain/          strategy.md, products.md, budget.md, headcount.md, state.md
├── 00-Templates-Custom/   CEO custom templates (ưu tiên cao nhất — BYOT)
├── 02-Tasks/<slug>/   01-brief.md, 03-clarification.md, 07-decision-report.md, 08-execution-plan.md
├── 03-Outputs/        .docx, .xlsx rendered
└── .vncoderc          vault config (packs, translator_mode, meeting rounds)
```

## 6 RULES (không được vi phạm)

1. **Brain-first** — Đọc Brain trước khi hỏi CEO. Hỏi phải có citation `file:section`. Nếu Brain đủ thì không hỏi.
2. **Domain-neutral** — Không để jargon TradingAgents leak (trade/market/Bull/Bear/ticker). CI check: `scripts/dev/check-domain-neutral.sh`.
3. **Single source of truth** — Obsidian vault là canonical. SQLite chỉ crash-recovery cache.
4. **CEO-friendly** — Output tiếng Việt, có TL;DR, định nghĩa thuật ngữ lần đầu, tránh jargon kỹ thuật.
5. **Live research + citations** — Tools phải trả `ToolResult.sources: list[str]` + `retrieved_at`. Cache 24h.
6. **BYOT** — Template priority: `vault/00-Templates-Custom/` > pack refs > `repo/templates-vn/`.

## Key patterns

**Adding a new tool** — Kế thừa `core/tools/base_tool.py`, return `ToolResult` với `sources` + `retrieved_at`. Register trong `core/tools/__init__.py`.

**Adding a department** — Tạo folder `departments/XX-name/` với `config.yaml`. Agent tự load qua `AgentLoader`.

**Adding a pack** — Tạo folder `packs/<name>/` với `config.yaml` + override templates. CEO enable qua `.vncoderc`.

**Template resolver** — `core/obsidian/template_resolver.py` check 3 paths theo đúng BYOT order.

**Tests** — Unit tests mock LLM (không real API call). Integration tests dùng `tests/fixtures/`. E2E tests trong `tests/e2e/` skip nếu không có `TAVILY_API_KEY`.

# Audit Repo — Đối chiếu Code với Plans

**Ngày audit:** 2026-05-07
**Kiểm tra bởi:** code-reviewer (chế độ Staff Engineer)
**Phạm vi:** core/, departments/, packs/, adapters/, tests/, plans/

---

## Tóm tắt điều hành

**Trạng thái tổng:** **Có Lỗ hổng — chạy được nhưng nhiều cam kết bị thiếu**

Tests pass (146/147), MCP server boot OK, end-to-end mocked test debate work. Nhưng nhiều tính năng quảng cáo trong plans + skill.md đang **stub hoặc gãy thầm lặng**:

### 3 vấn đề nghiêm trọng nhất

1. **Search wired nhưng KHÔNG có credentials** — 4/6 tools (web_search, vn_law_search, vn_local_regulation, competitor_research) cần `TAVILY_API_KEY`. `onboard_vault()` không bao giờ hỏi key. `install_mcp.py` không inject vào `claude_desktop_config.json -> env`. Live research sẽ fail mỗi khi ToolRouter chọn Tavily-backed tool. Crash mode: `tavily.TavilyClient(api_key="")` raise auth error → ResearchPhase swallow vào `error` field per query → meeting tiếp tục với findings rỗng → RULE 5 vi phạm thầm lặng.

2. **`vn_approve` và `vn_execute` là stubs** — `flow_controller.approve_decision()` ghi placeholder "(TODO Phase 6)"; `flow_controller.execute()` ghi `README.md` "(TODO Phase 6: render .docx/.xlsx via DocWriter)". DocWriter + TemplateResolver implement đầy đủ trong `core/obsidian/` nhưng **không được wire**. Phase 5 + 6 cam kết "DN-VN .docx/.xlsx output" KHÔNG tồn tại. `skill.md` Step 7 quảng cáo action không chạy.

3. **Meeting đọc departments từ REPO không từ VAULT** — `flow_controller.run_meeting:167` hard-code `Path(__file__).parent.parent.parent / "departments"`. Custom packs/BYOT departments cài trong `<vault>/01-Departments/` KHÔNG được load làm participants. RULE 6 (BYOT) gãy ở meeting layer. `PackLoader` class định nghĩa nhưng không import ở đâu trong production flow.

### 3 điểm mạnh nhất

1. **Engine debate vững** — Pro/Con + 3 perspective debators + Synthesizer + LangGraph state machine implement TradingAgents pattern đúng với neutral renaming đầy đủ. Test domain leakage (`test_domain_neutral.py`) enforced.

2. **Brain layer sạch** — `BrainReader` + `GapAnalyzer` + `QuestionGenerator` + `Clarifier` chain work end-to-end với citations, idempotent, test tốt (~30 tests).

3. **MCP sampling architecture đúng** — `MCPSamplingProvider` correctly tách system role vào `system_prompt` kwarg (fix gần đây), handle async/sync coroutines, fallback gracefully cho mocks. 8 MCP tools registered.

---

## Đánh giá theo Phase

### Phase 1 Foundation: **PARTIAL**
- **Đã làm:** pyproject, README, vault-template, BrainReader/Schema/GapAnalyzer/Memory, 12 dept stubs + agents, 191 templates vendored.
- **Thiếu:** Plan hứa **13 phòng core**; chỉ có **12 thư mục** (`01-governance`..`12-growth`) — không có phòng thứ 13. Plan footnote nhắc "13" nhiều lần; routing prompt cũng nói "13".
- **Bugs:** không có ở layer này.

### Phase 2 Debate Engine: **DONE**
- **Đã làm:** MeetingState, conditional_logic, checkpointer (sqlite saver), Pro/Con/Perspective debators, Synthesizer, MeetingGraph (LangGraph). Neutral rename enforce + test.
- **Thiếu:** không có gì đáng kể.
- **Bug:** `meeting_graph.py:173` gọi `MeetingGraph(checkpointer=False)` — disable persistent state. Comment nói "to avoid SQLite issues" nhưng không follow-up. Resume sau crash mid-meeting không thể.

### Phase 3 Orchestrator + Brain-first: **PARTIAL**
- **Đã làm:** Router, GapAnalyzer integration, QuestionGenerator, ClarificationIO, FlowController (run/resume_after_clarification/run_meeting).
- **Thiếu:** `resume_after_clarification` trả về `PAUSE_DECISION_REPORT` với message "Phase 4+5 sẽ wire research + meeting" — nghĩa là **resume KHÔNG auto-trigger meeting**. CEO/AI phải explicit gọi `vn_meeting`. Skill.md doc đúng nên chức năng OK, nhưng mâu thuẫn ý plan "2-stop flow" (có 3rd manual step).
- **Bug:** `flow_controller.run` gọi `Router(rules_path=classifier_rules.yaml)` — không error handling nếu YAML hỏng.

### Phase 4 Tools + Translator: **PARTIAL — DEGRADED**
- **Đã làm:** BaseTool, ToolCache, ToolRouter, 6 tools (web/law/local/competitor/benchmark/tax), Translator pipeline (Glossary + JargonDetector + Simplifier + TLDR), `terms_dictionary.yaml`.
- **Thiếu/Gãy:**
  - **Không có API key plumbing** (xem Search Audit phía dưới). 4 Tavily tools fail thầm lặng khi thiếu key.
  - Không có fallback khi Tavily import fail (vd user không cài `tavily` extra). `from tavily import TavilyClient` lazy bên trong `run()` per tool — ImportError propagate.
  - `industry_benchmark` data path hardcode — không graceful nếu `data/benchmarks-vn.yaml` thiếu.
- **Bug:** `tool_router.plan()` `re.search(r"\{.*\}", raw, re.DOTALL)` — first `{` đến last `}` — work nhưng nếu LLM emit nhiều JSON object (vd example + answer), parse sai block. Không request JSON-mode.

### Phase 5 Departments + Packs + BYOT: **PARTIAL**
- **Đã làm:** 12 departments với agent .md prompts, 3 packs (fnb/retail/tech-saas), `DepartmentLoader`, `PackLoader`, `TemplateResolver`, `DocWriter`.
- **Wired:** Department prompts load chỉ cho `name_vn` — **enriched per-agent prompts KHÔNG dùng trong PerspectivesCollector** (dùng generic `PERSPECTIVE_PROMPT` template).
- **Thiếu/Gãy:**
  - `PackLoader` là dead code (không import ngoài file).
  - `DocWriter` + `TemplateResolver` không wire vào `flow_controller.execute()`.
  - BYOT meeting integration gãy (departments_root hard-code repo).
  - Pack `adds_departments` như `13-kitchen` (fnb), `13-warehouse` (retail) cài vào vault nhưng `Router` prompt vẫn hardcode `13-XX` placeholder, depend LLM pick đúng codes từ heuristic `active_departments`.

### Phase 6 Adapters + E2E + Onboard: **PARTIAL**
- **Đã làm:** `scripts/onboard.py` (CLI wizard), `core/onboard.py` (lib), `adapters/claude-code/skill.md`, `adapters/claude-cowork/`, MCP install/uninstall, E2E `test_b_campaign_high_income.py` (mocked LLM).
- **Thiếu/Gãy:**
  - Wizard KHÔNG hỏi **bất kỳ** API key nào (Anthropic, Tavily, Google, OpenAI). User phải tự `export TAVILY_API_KEY=...` SAU onboard.
  - Khi MCP server launch bởi Claude Desktop, kế thừa env Claude Desktop process — thường rỗng cho các keys này. Kết quả: subscription-based LLM work (qua MCP sampling), nhưng tools cần Tavily silently 401.
  - `claude-cowork` adapter có shell scripts nhưng không test integration.
  - `test_real_llm.py` có nhưng skipped/optional (không proof real LLM run pass E2E trong CI).
  - `vn_approve` + `vn_execute` stubs (xem Critical issue #2) → E2E test chỉ verify đến `07-decision-report.md`; "produces .docx/.xlsx" trong `plan.md` Definition of Done không validate.

---

## Audit Search/Research (NGHIÊM TRỌNG — trả lời concern user)

### Tools available
6 đăng ký trong `core/orchestrator/research_phase.py:TOOL_REGISTRY`:
- `web_search` — Tavily
- `vn_law_search` — Tavily restrict thuvienphapluat.vn etc.
- `vn_local_regulation` — Tavily restrict chinhphu.vn etc.
- `competitor_research` — Tavily
- `industry_benchmark` — local YAML curated data (không cần API key)
- `tax_calculator` — pure Python compute (không cần API key)

### API key plumbing
- Tất cả 4 Tavily tools: `os.getenv("TAVILY_API_KEY", "")` (default empty string).
- `core/utils/config.py:Config` KHÔNG có field cho API keys; `.vncoderc` chỉ chứa `vault_path`, `packs`, `version`.
- `core/onboard.py:onboard_vault` — không bao giờ prompt, không bao giờ ghi API key đâu cả.
- `scripts/onboard.py` interactive wizard — chỉ hỏi pack codes + BYOT path, **không hỏi API keys**.
- `core/install_mcp.py:install` — ghi `mcpServers[name] = {command, args}` only; **KHÔNG set `env: {...}`**, nên MCP server kế thừa env Claude Desktop process (thường thiếu TAVILY_API_KEY trên Windows/macOS GUI launch trừ khi user set system-wide trước launch).
- README.md bảo user `export TAVILY_API_KEY=...` nhưng đây là shell-scoped — Claude Desktop GUI launch ignore shell rc trên macOS/Windows.

### Có thực sự được call trong flow? — Trace
1. CEO gọi `vn_run(brief, vault)` → `FlowController.run()`. **KHÔNG call ResearchPhase**. Chỉ Router + GapAnalyzer + QuestionGenerator. Trả về `PAUSE_CLARIFICATION` hoặc `PAUSE_DECISION_REPORT`.
2. CEO trả lời → `vn_resume(task_folder)` → `resume_after_clarification()`. **Cũng KHÔNG call ResearchPhase**. Chỉ normalize answers và trả `PAUSE_DECISION_REPORT`.
3. CEO/AI gọi `vn_meeting(task_folder)` → `run_meeting()` — ĐÂY mới call `ResearchPhase.run()` (line 159-164) TRƯỚC build meeting graph.
4. Trong ResearchPhase: `tool_router.plan(brief, brain_summary)` hỏi LLM tool nào chạy → `TOOL_REGISTRY[name]()` instantiate → `tool.run(query)`.
5. Mỗi Tavily tool: `from tavily import TavilyClient` + `TavilyClient(api_key="")` → `client.search(...)` → 401 / network error → caught bởi ResearchPhase try/except → record là `{"query": q, "error": str(e)}` trong findings.
6. Synthesizer đọc `state["research_findings"]` và stringify 3000 chars đầu — nhưng nếu mọi entry là `{"error": ...}`, report không có research thật, RULE 5 vi phạm thầm lặng. CEO thấy decision report chỉ cite Brain + LLM "common knowledge".

**Kết luận:** Search CÓ trong flow, nhưng chỉ khi `vn_meeting` chạy, VÀ chỉ thành công cho `industry_benchmark`/`tax_calculator` không cần API key.

Quan sát #2 của user (flow đi thẳng vào meeting không research) — **đúng một phần**:
- Research xảy ra trong `vn_meeting`, không phải stage riêng. Nên nếu AI gọi `vn_meeting` ngay sau clarification, research chạy.
- NHƯNG nếu AI trong Claude Desktop bypass `vn_meeting` (tự ghi decision, ignore MCP tool flow), không có research nào. Skill.md rõ rằng vn_meeting phải được call, nhưng enforce phụ thuộc AI obedience.
- Cũng: nếu Tavily key thiếu, kể cả `vn_meeting` chạy, mọi web research fail thầm lặng.

### Onboard có hỏi keys không?
**KHÔNG.** CLI wizard chỉ hỏi pack selection + BYOT path. MCP `vn_onboard` tool chỉ expose `vault` + `packs` parameters. `.vncoderc` schema không có section `api_keys`.

### Vấn đề
- Không graceful degradation: tools nên detect missing key và return `ToolResult(data={"skipped": "no API key"}, sources=[], notes="Set TAVILY_API_KEY")` thay vì crash vào Tavily client.
- ToolRouter prompt không biết tool nào credentialed; sẽ plan tools fail.
- Không có cách CEO cung cấp key mà không edit shell rc / claude_desktop_config.json bằng tay.
- `vn_status` không report tool availability — không thể bảo CEO trước "live research disabled, chỉ benchmark+tax work".

### Khuyến nghị
1. **Thêm step API key vào onboard** — cả CLI wizard và MCP `vn_onboard` chấp nhận `tavily_api_key` arg optional, save vào `<vault>/.env` (gitignored) hoặc `~/.vn-business-os/keys.yaml`.
2. **Tools phải check key + skip gracefully** — `if not self.api_key: return ToolResult(data={"skipped": True}, sources=[], notes="Missing TAVILY_API_KEY")`. ToolRouter cũng cần biết qua method `available_tools()` filter theo credential presence.
3. **`install_mcp.py` hỗ trợ env injection** — đọc keys từ `~/.vn-business-os/keys.yaml` và ghi `env: {TAVILY_API_KEY: ...}` vào mcpServers entry để Claude Desktop launch MCP với env đúng.
4. **`vn_status` report tool availability** — return `{"tools_live": [...], "tools_skipped": [{"name":..., "reason":...}], ...}`.
5. **Skill.md include preflight** — instruct AI gọi `vn_status` trước `vn_meeting`, cảnh báo CEO nếu `tools_skipped` chứa tools quan trọng cho domain task (vd legal advice không có `vn_law_search`).

---

## Audit Onboarding

### `core/onboard.py` làm gì
1. Copy `vault-template/` → `<vault>`
2. Copy 12 core depts → `<vault>/01-Departments/`
3. Cài packs đã chọn (thêm 13-XX departments + brain-template overrides)
4. BYOT import optional (keyword classifier vào department subfolders)
5. Git init (best-effort)
6. Generate wikilinks (Brain hub, Dept hubs, agent cross-links)
7. Save `.vncoderc` với `{vault_path, packs, version: "0.1.0"}`

### Không làm gì
- Không hỏi tên công ty, ngành (chỉ dùng làm pack code), tên CEO, fiscal year start, etc.
- Không hỏi hoặc save **bất kỳ API key** (Anthropic, Tavily, Google, OpenAI).
- Không validate vault writable trước khi copy.
- Không check `vault-template/` integrity (vd mọi `00-Brain/*.md` expected có không).
- Không setup `.gitignore` rules cho file sensitive (template có `.gitignore` nhưng không patch company-specific exclusions).
- Không init Brain content từ CEO answers — Brain `.md` để placeholder template, CEO phải edit thủ công sau.

### `vn_onboard` MCP issues
- File ops sync trong MCP request thread — `shutil.copytree` 191 templates có thể mất nhiều giây. Comment nói "fixes Claude Desktop timeout issue" qua no-subprocess approach, nhưng file IO blocking thực sự chưa giải quyết.
- Không support `elicitation` follow-up CEO questions trong onboard (vd "Ngành nào?", "Đã có template chưa?"). MCP elicitation protocol bị ignore — `vn_onboard` one-shot.
- Trả về `next_steps` text nhưng không structured "needs_action" để AI drive multi-turn onboard.

### Khuyến nghị
- Thêm step API key (xem rec Search Audit).
- Chạy `shutil.copytree` trong `asyncio.to_thread` nếu elicit từ async MCP context.
- Thêm `vn_onboard_step1`, `vn_onboard_step2` tools cho multi-turn wizard, HOẶC dùng MCP elicitation (FastMCP gần đây support).
- `vn_status` cảnh báo nếu Brain files vẫn chứa placeholder template text (vd `<điền ICP>`).

---

## Tính toàn vẹn Agent / Flow

### Agent prompts
- 12 dept folders × nhiều agent .md mỗi folder — frontmatter schema phong phú (`expertise`, `required_refs`, `required_tools`, `model_override`, `temperature`).
- `AgentLoader` parse đúng + tested.
- **NHƯNG** `PerspectivesCollector` ignore per-agent prompts — dùng generic template `PERSPECTIVE_PROMPT.format(dept_name=dept.name_vn)`. Rich agent prompts không bao giờ dùng trong meetings thực.
- `routing_rules.keywords → agent` trong `department.yaml` cũng unused — không có code path pick agent cụ thể trong department dựa brief.

### Multi-turn debate
- Pro/Con: state machine alternate đúng trong `conditional_logic.next_pro_con_node` đến `count >= max_debate_rounds` (default 2).
- Perspective: Growth → Cautious → Balanced cycle đến `max_perspective_debate_rounds` (default 1).
- Cả 2 honor `state["judge_decision"]` early exit nhưng không code nào set — judge feature inert.

### Synthesizer
- Đọc tất cả perspectives + debates + research → invoke LLM với structured prompt.
- Output stuff vào field `final_report`. Translator pipeline apply (RULE 4) trước khi ghi `07-decision-report.md`.
- Không source-citation enforce check — synthesizer rely LLM cite, không post-validation.

### Brain context handling
- `BrainContext.model_dump()` dump nguyên vào `state["brain_context"]` và yaml-dump vào mọi agent system message — lớn cho DN to. Không filter per-agent.
- Brain summary dùng trong ToolRouter slice 3000 chars; trong Synthesizer cũng 3000. Reasonable nhưng không log khi truncate.

---

## Audit v2 MCP

### Trạng thái 8 MCP tools
| Tool | Status | Ghi chú |
|---|---|---|
| `vn_run` | OK | call FlowController.run; return task_folder + stage |
| `vn_resume` | OK | đọc checkboxes; không trigger meeting |
| `vn_meeting` | OK với caveats | run Research+Meeting; tool key issues + departments_root bug |
| `vn_approve` | **STUB** | ghi placeholder "(TODO)" |
| `vn_execute` | **STUB** | chỉ ghi README.md |
| `vn_status` | OK | không LLM, return Brain summary + tasks |
| `vn_onboard` | OK | sync file copy, block request thread; không hỏi API key |
| `vn_upgrade` | OK | refresh agent prompts + dept yaml + Brain aliases |

### Sampling provider
- Vừa có fix `system role` (commit d4c9a33) — `_split_system` extract system content đúng.
- `_run_sync(coro)` dùng ThreadPoolExecutor + `asyncio.run` khi call trong running loop — work nhưng spawn thread per call (perf cost, ~50ms each).
- `_extract_text` handle cả `TextContent` object và dict shapes — robust.
- Không retry khi rate limit (Anthropic 429 từ MCP host's subscription quota) — single failed call kill toàn flow.
- Không timeout — long sampling có thể hang vô tận.

### Bugs Claude Desktop thực (potential, chưa observed)
- `vn_meeting` chạy `ThreadPoolExecutor` cho parallel research + parallel perspectives. Bên trong `MCPSamplingProvider.complete`, sync→async bridging spawn threads per call. Với 5 perspectives + N research queries concurrent, dễ oversubscribe MCP host's sampling rate limit. Không backpressure.
- LangGraph state checkpointer hardcode disable (`checkpointer=False`). Crash mid-meeting → mất hết progress. Không cách resume.

### Tests
- `test_mcp_sampling_provider.py` — unit tests với mocks
- `test_mcp_server_tools.py` integration với FastMCP test harness
- `test_mcp_server_e2e.py` end-to-end qua stdio transport
- `test_real_llm.py` — gated bởi env var (real Anthropic key) — likely không run trong CI

---

## Ma trận Tuân thủ 6 RULES

| RULE | Trạng thái | Bằng chứng | Lỗ hổng |
|---|---|---|---|
| 1. Brain-first | ENFORCED | `flow_controller.run` đọc Brain → GapAnalyzer → SAU ĐÓ mới clarification | Không |
| 2. Domain-neutral | ENFORCED | `test_domain_neutral.py` check không Bull/Bear/trade/portfolio trong outputs; debate state dùng `pro_history`/`con_history`/`growth_history` etc. | Không |
| 3. Single source of truth | PARTIAL | Obsidian vault canonical, mọi write qua ObsidianVault. NHƯNG meeting đọc dept defs từ REPO không VAULT — divergence có thể sau upgrade. | Fix departments_root về vault path |
| 4. CEO-friendly language | PARTIAL | TranslatorPipeline apply cho final report. NHƯNG clarification questions, perspectives, debate transcripts — không simplify, surface to CEO nếu AI show | Apply translator cho clarification UI text + perspective summaries |
| 5. Live research with citations | **DEGRADED** | ResearchPhase + ToolRouter wired, sources field trên mỗi ToolResult — nhưng Tavily tools fail thầm lặng không API key. Synthesizer rely LLM cite, không validate | API key plumbing + skip-gracefully + cite validator |
| 6. BYOT | **GÃY ở meeting layer** | onboard import BYOT files vào `00-Templates-Custom/`, nhưng template_resolver không được load bởi execute() (đang stub). Meeting cũng bypass vault depts. | Fix departments_root + wire template_resolver vào execute |

---

## Bugs Nghiêm trọng đã Phát hiện

1. **`core/orchestrator/flow_controller.py:167`** — `departments_root = Path(__file__).parent.parent.parent / "departments"`. Hardcode repo path; ignore `<vault>/01-Departments/`. Custom packs/BYOT depts không trong meeting.
2. **`core/orchestrator/flow_controller.py:241-252`** — `approve_decision()` ghi stub "(TODO Phase 6)". Plan hứa real execution-plan generation.
3. **`core/orchestrator/flow_controller.py:254-267`** — `execute()` ghi README placeholder. DocWriter không bao giờ invoke.
4. **`core/tools/web_search.py:14` (và 3 sibling tools)** — `os.getenv("TAVILY_API_KEY", "")` default empty string. `TavilyClient(api_key="")` constructor hoặc `client.search` đầu raise auth error. Caught bởi ResearchPhase try/except và silently turn into `{"error": ...}` per query. RULE 5 vi phạm vô hình.
5. **`core/onboard.py:onboard_vault`** — không nhận API key parameters. `.vncoderc` schema không có key fields. CEO không có cách in-flow cung cấp credentials.
6. **`core/install_mcp.py:install`** — không ghi `env: {...}` vào mcpServers entry. MCP server launch bởi Claude Desktop kế thừa env rỗng trên Windows/macOS GUI launch.
7. **`core/orchestrator/perspectives_collector.py:54`** — dùng generic `PERSPECTIVE_PROMPT`, ignore per-agent enriched prompts loaded bởi `AgentLoader`. Effort enrichment Phase 5 không hiệu quả runtime.
8. **`core/agents/pack_loader.py:29`** — `PackLoader` class defined, không bao giờ import elsewhere. Dead code hoặc thiếu wiring.
9. **`core/meeting/meeting_graph.py:173`** — `checkpointer=False` hardcode với comment "to avoid SQLite issues". Crash mid-meeting unrecoverable.
10. **`core/orchestrator/flow_controller.py:202-207`** — `GitSync.commit` gọi với `try/except: pass`. Silently swallow mọi errors bao gồm config errors, permission errors, no-git-installed errors. CEO không bao giờ biết commit fail.
11. **`departments/`** — chỉ 12 directories. Plan + router prompt nói "13 core". Thiếu 1 hoặc naming off-by-one.
12. **`core/orchestrator/flow_controller.py:63`** — `Router(self.llm, rules_path=rules_path)` nếu `classifier_rules.yaml` malformed, sẽ crash trước user-friendly error. Không defensive load.
13. **`core/orchestrator/research_phase.py:39`** — `tool_cls()` instantiate không args. Tools cần province (vn_local_regulation) không thể nhận từ ToolRouter plan vì ToolCall TypedDict chỉ có `tool` + `queries`. Province phải encode trong query string.
14. **`core/translator/pipeline.py:apply`** — apply simplifier+TLDR nhưng không try/except. Nếu Simplifier LLM call fail, decision report write cũng fail.
15. **`core/llm/providers.py:MCPSamplingProvider.complete`** — không retry rate limit, không timeout. Single 429 từ Anthropic kill toàn vn_meeting flow.

---

## Danh sách Fix Theo Ưu tiên

### P0 (PHẢI fix — features broken hoặc silently violate advertised behavior)
- **P0.1** Wire `DocWriter` + `TemplateResolver` vào `flow_controller.execute()`. Generate real .docx/.xlsx từ `08-execution-plan.md` và templates. Phase 5/6 acceptance.
- **P0.2** Implement `flow_controller.approve_decision()` đúng — generate execution plan qua LLM + structured spec, không stub.
- **P0.3** Fix `flow_controller.run_meeting:167` — `departments_root` phải là `<vault>/01-Departments/` (với fallback về repo cho missing dept). Restore RULE 6 BYOT cho meetings.
- **P0.4** Tools phải skip gracefully khi `TAVILY_API_KEY` rỗng: return `ToolResult(data={"skipped": True}, notes="No TAVILY_API_KEY — set in vault/.env")` thay vì crash vào TavilyClient.
- **P0.5** ToolRouter: filter plan chỉ tools credentialed. Thêm `available_tools()` introspection.
- **P0.6** Onboard: hỏi API keys (CLI wizard + MCP `vn_onboard` thêm `api_keys` param). Save vào `<vault>/.env` (trong `.gitignore`) + load qua `python-dotenv` ở FlowController init.
- **P0.7** `install_mcp.py` inject `env: {TAVILY_API_KEY: ..., ANTHROPIC_API_KEY?: ...}` từ `<vault>/.env` hoặc `~/.vn-business-os/keys.yaml` vào mcpServers entry.

### P1 (NÊN fix — correctness + UX)
- **P1.1** Wire per-agent enriched prompts trong `PerspectivesCollector` — load AgentDefinition cho `dept.default_speaker` và dùng system_prompt đó thay vì generic template.
- **P1.2** Thêm phòng thứ 13 hoặc fix mọi reference ("12 phòng core" everywhere — README, plan, router prompt, skill.md).
- **P1.3** Thêm retry-with-backoff + timeout vào `MCPSamplingProvider.complete` — handle 429/timeout gracefully.
- **P1.4** Re-enable LangGraph checkpointer (root cause SQLite issue, fix it). Resume mid-meeting sau crash.
- **P1.5** `vn_status` report `tools_live` / `tools_skipped` dựa credential presence.
- **P1.6** Apply translator cho perspectives + debate transcripts trước show CEO (hiện chỉ synthesizer output simplified — round summaries show raw).
- **P1.7** Drop swallow `GitSync` exceptions silently — log vào `<vault>/.vn-business-os.log` để CEO thấy commits không xảy ra tại sao.
- **P1.8** Thêm citation validator post-Synthesizer — flag claims không có `[source: ...]` markers.

### P2 (NICE to fix)
- **P2.1** Multi-turn `vn_onboard` qua MCP elicitation cho industry/CEO/keys/BYOT.
- **P2.2** `Router` JSON-mode khi support — eliminate brittle regex.
- **P2.3** `tool_cache.db` per-vault không per-user (hiện `~/.vn-business-os/`); else cache poisoning giữa companies.
- **P2.4** Real-LLM E2E test trong CI (gate by env, nhưng actually run).
- **P2.5** PackLoader integration hoặc removal — dead code là smell.
- **P2.6** `flow_controller._slugify` cho phép leading/trailing dashes từ non-ASCII (Vietnamese accents) → fallback "task". Dùng `unicodedata.normalize` cho proper Vietnamese-safe slugs.
- **P2.7** Brain context filter per agent (hôm nay mọi agent thấy Brain dump đầy đủ → token waste với DN to).
- **P2.8** Thêm MCP `tools_changed` notification khi `vn_onboard` để Claude Desktop refresh tool list.

---

## Câu hỏi mở

1. Phải số 13-department là plan revision sớm (vd "11-reporting + 12-growth + 1 phòng 13 đã merge"), hay thật sự thiếu phòng? Phòng nào? `agency-agents` reference vs `business-builder.plugin` source — count khác giữa 2.
2. Expectation user "search chạy auto trước meeting" — vd `vn_resume` có nên call ResearchPhase, không chỉ `vn_meeting`? Plans phrase "research then meeting" như 1 stage; current code tách dưới `vn_meeting`. UX intent unclear.
3. API keys nên live per-vault (`<vault>/.env`) hay global (`~/.vn-business-os/keys.yaml`)? Per-vault feel right cho multi-DN consultants nhưng more friction; global đơn giản hơn.
4. Strategy rate-limit `MCPSamplingProvider` — plugin nên auto-degrade về "lite mode" (1 round debate) khi subscription gần quota, hay fail loudly?
5. Tại sao `checkpointer=False` hardcode? SQLite issue gốc là gì? Cần investigate trước re-enable.
6. `install_mcp` ghi absolute path của `sys.executable` vào config — gãy nếu user dùng pyenv/venv bị remove. Có nên ghi `python -m core.mcp_server` và rely PATH?

---

**Trạng thái:** DONE_WITH_CONCERNS
**Tóm tắt:** Repo internal consistent và tests pass, nhưng nhiều Phase 5/6 deliverables là stubs (vn_approve, vn_execute, doc rendering) và live-research feature có credential plumbing gaps nghiêm trọng match user-reported behavior. RULE 5 + RULE 6 compromised at runtime.
**Concerns/Blockers:** P0 fixes required trước khi claim v0.2 production-ready. Khuyến nghị mở phase mới phase-07-credentials-and-execution để close gaps trước broader release.

# Báo cáo Fix Lỗi P1 — 2026-05-07

> **Trạng thái:** ✅ DONE. Tests **243 passed**, 1 skipped (+63 mới so với P0). Commit `8868986`.

---

## 7 lỗi P1 — Đã sửa

### P1.1 — PerspectivesCollector dùng prompt theo từng agent

**Trước:** 38 agent prompts đã enriched (CFO biết VAS, head-chef biết food cost, ...) nhưng `PerspectivesCollector` bỏ qua, vẫn dùng template chung `PERSPECTIVE_PROMPT.format(dept_name=...)` → công sức Phase 5 vô ích.

**Sau:**
- Load `AgentDefinition` cho `dept.default_speaker` qua `AgentLoader`
- Đường dẫn tìm: `<departments_root>/<dept>/agents/<default_speaker>.md` → `<vault>/01-Departments/<dept>/agents/<default_speaker>.md`
- Dùng `agent_def.system_prompt` (body của file .md) làm system message
- Fallback graceful: nếu agent file thiếu → dùng generic template (không gãy flow)

**Tests:** 8 tests mới (`test_perspectives_collector_enriched.py`)

---

### P1.2 — Đối chiếu "12 vs 13" phòng ban

**Trước:** Plan + router prompt + README nhắc "13 phòng core" nhưng thực tế chỉ có 12 directories. Lệch 1 → LLM confuse.

**Sau:**
- `plans/plan.md`: "13 phòng core" → "12 phòng core (+ pack-specific 13-XX)"
- `core/agents/registry.py` docstring đã cập nhật
- Router prompt đã rõ: "01-..12-... + pack-specific 13-XX"

---

### P1.3 — MCPSamplingProvider retry + timeout

**Trước:** Khi Anthropic 429 (hết quota subscription) hoặc timeout → 1 lần fail kill cả flow `vn_meeting`. Không retry.

**Sau:**
- `max_retries=3`, `timeout_seconds=120`, exponential backoff
- `_is_retryable()` nhận diện: rate limit / 429 / timeout / connection / 503 / 502
- Non-retryable errors (vd `ValueError`) fail nhanh không retry

**Tests:** 3 tests mới (rate limit retry, non-retryable, max retries giveup)

---

### P1.4 — LangGraph checkpointer opt-in

**Trước:** `checkpointer=False` hardcode trong `flow_controller.py` với comment "to avoid SQLite issues" — không thể recover khi crash giữa cuộc họp.

**Sau:**
- `meeting.use_checkpointer` config option (default `False` để giữ behavior cũ)
- Khi user bật `meeting.use_checkpointer: true` trong `.vncoderc`:
  - Thử init `make_checkpointer()` (SqliteSaver)
  - Nếu fail (LangGraph version mismatch, SQLite locked, ...) → log warning, fallback off
- **Lưu ý:** vẫn cần investigate sâu hơn để xác định root cause SQLite issue và bật default ON. Hiện tại opt-in là an toàn nhất.

---

### P1.6 — Translator scope qua config

**Trước:** Translator chỉ apply cho final report. Clarification questions, perspective outputs, debate transcripts vẫn dùng thuật ngữ kỹ thuật → CEO khó hiểu.

**Sau:**
- `translator_mode` config: `"off"` | `"final_only"` (default) | `"all_intermediate"`
- `"all_intermediate"`: wrap perspectives + pro/con outputs qua translator trước khi append vào state
- Default vẫn `"final_only"` để giữ behavior cũ — CEO opt-in qua `.vncoderc`
- Performance: `"all_intermediate"` tăng cost LLM (mỗi output → 1 call translator), nên user chủ động chọn

**Tests:** 12 tests mới (`test_translator_mode_config.py`)

---

### P1.7 — GitSync log thay vì nuốt thầm

**Trước:** `try: GitSync.commit(...) except: pass` → CEO không biết tại sao Git commit fail (permission, no git, conflict, ...).

**Sau:**
- `FlowController._log_warning()` ghi vào `<vault>/.vn-business-os.log`
- Format: `[YYYY-MM-DD HH:MM:SS] WARN: Git commit failed (Stop 1): <error message>`
- CEO mở file log để biết chính xác lý do

---

### P1.8 — Citation validator post-synthesizer

**Trước:** Synthesizer rely LLM tự cite — không validate → có thể bịa số liệu/luật mà không có nguồn.

**Sau:** `core/orchestrator/citation_validator.py`
- Detect numeric claims (`%`, `VND`, `USD`, `triệu`) không có `[source: ...]` marker
- Detect legal references (Nghị định/Thông tư/Luật/Quyết định) không có cite
- Recognize Brain file refs (`strategy.md`, `laws.md`, ...) là valid citation
- Common-knowledge phrases được miễn (vd "Tết là dịp tiêu thụ lớn")
- Append section `## ⚠️ Cảnh báo: Claims thiếu trích nguồn` vào decision report nếu phát hiện
- Idempotent: chạy lại không append duplicate
- Wire vào `flow_controller.run_meeting()` ngay sau Synthesizer ghi `07-decision-report.md`
- Flag count xuất hiện trong `FlowResult.message`

**Tests:** 40 tests mới (`test_citation_validator.py`)

---

## Files thay đổi

### Core
- `core/orchestrator/perspectives_collector.py` — full rewrite (vault_root param + AgentLoader integration)
- `core/orchestrator/flow_controller.py` — translator wrap + CitationValidator wire + `_log_warning` + checkpointer opt-in
- `core/orchestrator/citation_validator.py` — **MỚI** (CitationValidator + CitationFlag + regex heuristics)
- `core/llm/providers.py` — retry + timeout
- `core/utils/config.py` — TranslatorMode + use_checkpointer fields
- `core/agents/registry.py` — docstring update
- `plans/plan.md` — "12 vs 13" reconcile

### Tests (+63 mới)
- `tests/unit/test_perspectives_collector_enriched.py` — 8 tests
- `tests/unit/test_translator_mode_config.py` — 12 tests
- `tests/unit/test_citation_validator.py` — 40 tests
- `tests/unit/test_mcp_sampling_provider.py` — +3 tests (retry behavior)

---

## Tests

| | Trước P1 | Sau P1 |
|---|---|---|
| Passed | 180 | **243** |
| Skipped | 1 | 1 |
| Net new | — | +63 |
| Regressions | — | 0 |

```
$ python -m pytest tests/ -q
243 passed, 1 skipped in 17.68s
```

---

## Cách dùng các option mới

### Translator mode (cho ngôn ngữ thân thiện CEO toàn flow)

Edit `<vault>/.vncoderc` (hoặc `~/.vncoderc`):

```yaml
translator_mode: all_intermediate
```

→ Mọi output (perspectives, debate, final report) đều được simplify sang ngôn ngữ CEO-friendly. Cost LLM tăng (~2-3x) nhưng dễ hiểu hơn nhiều.

### Checkpointer (crash recovery)

```yaml
meeting:
  use_checkpointer: true
```

→ LangGraph lưu state debate vào `~/.vn-business-os/checkpoints.db`. Crash giữa cuộc họp → có thể resume (cần kiểm tra thực tế với LangGraph version cụ thể). Nếu init fail, plugin tự fallback off + log.

### Xem log warnings

```powershell
Get-Content "F:\.../my-vault/.vn-business-os.log" -Tail 20
```

---

## Còn lại — P2 (nice-to-have)

Xem `audit-260507-repo-completeness-vn.md` mục P2:
- Multi-turn `vn_onboard` qua MCP elicitation
- Router JSON-mode
- `tool_cache.db` per-vault
- Real-LLM E2E test trong CI
- PackLoader integration hoặc removal
- Slug Vietnamese-aware
- Brain context filter per agent
- MCP `tools_changed` notification

P2 không blocking — plugin production-ready cho beta test với P0 + P1 hiện tại.

---

## Bước tiếp theo cho người dùng

1. **Restart Claude Desktop** để load MCP server mới
2. **(Tùy chọn) Bật translator mode all_intermediate:**
   - Edit `<vault>/.vncoderc` thêm `translator_mode: all_intermediate`
3. **Test flow đầy đủ:**
   - Setup vault → vn_run → vn_resume → vn_meeting → vn_approve → vn_execute
   - Kiểm tra `07-decision-report.md` có section "⚠️ Cảnh báo: Claims thiếu trích nguồn" hay không
   - Kiểm tra `03-Outputs/<task>/*.docx` được render
4. **Báo cáo nếu lỗi gì** — sẵn sàng fix tiếp

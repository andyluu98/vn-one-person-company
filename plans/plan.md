# VN Business OS — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build open-source AI agent OS cho DN nhỏ-vừa Việt Nam — CEO giao việc qua chat, agents (phòng ban) họp bàn debate, sinh báo cáo + tài liệu .docx/.xlsx tuân thủ luật VN.

**Architecture:** Python + LangGraph (bóc engine debate từ TradingAgents, rename neutral) + Obsidian vault (Markdown + Git private) + multi-tool adapters (Claude Code, Cowork). 4 lớp: Entry / Core / State / Output. 6 RULES bất di bất dịch (Brain-first, Domain-neutral, Single source of truth, CEO-friendly language, Live research, BYOT).

**Tech Stack:** Python 3.13, LangGraph 0.2+, LangChain core, Pydantic v2, SQLite, python-docx, openpyxl, PyYAML, Tavily/Serper API, Anthropic SDK (default), google-genai, openai SDK, pytest, ruff, mypy.

**Spec reference:** `docs/superpowers/specs/2026-05-06-vn-business-os-design.md`

---

## Phase Overview

| # | Phase | Mục tiêu | Status |
|---|---|---|:-:|
| 1 | [Foundation](phase-01-foundation.md) | Repo skeleton + Brain layer + 12 dept stubs + vendor 191 template | ⏳ |
| 2 | [Debate Engine](phase-02-debate-engine.md) | Bóc meeting_graph từ TradingAgents → neutral + checkpointer | ⏳ |
| 3 | [Orchestrator + Brain-first](phase-03-orchestrator-brain-first.md) | Router + Gap analyzer + Clarifier + Flow controller (2 stops) | ⏳ |
| 4 | [Tools + Translator](phase-04-tools-translator.md) | 6 tool live research + translator (jargon + TL;DR) | ⏳ |
| 5 | [Departments + Packs + BYOT](phase-05-departments-packs-byot.md) | Full 13 phòng + 3 pack + template resolver + doc writer | ⏳ |
| 6 | [Adapters + E2E + Onboard](phase-06-adapters-e2e-onboard.md) | Claude Code/Cowork adapter + wizard + test case B pass | ⏳ |

## Six RULES (enforce trong code)

1. 🔒 **Brain-first clarification** — không hỏi CEO khi chưa đọc Brain
2. 🔒 **Domain-neutral engine** — không trade/finance leak
3. 🔒 **Single source of truth** — Obsidian vault là sự thật
4. 🔒 **CEO-friendly language** — tiếng Việt + định nghĩa thuật ngữ + TL;DR
5. 🔒 **Live research with citations** — search luật/đối thủ/benchmark, cite nguồn
6. 🔒 **BYOT (Bring Your Own Templates)** — DN custom > pack > default

## Key Dependencies

- Phase 1 → blocks all
- Phase 2 → blocks Phase 3 (meeting needs checkpointer + state)
- Phase 3 → blocks Phase 4, 5 (flow controller integrates everything)
- Phase 4 → blocks Phase 5 (departments dùng tools + translator)
- Phase 5 → blocks Phase 6 (E2E test cần đầy đủ depts)

## File Structure (sẽ tạo)

Xem chi tiết trong từng phase. Tóm tắt:
- `core/` — Python engine (~4800 LoC)
- `departments/` — 12 phòng core (+ pack-specific 13-XX) (YAML + agent .md)
- `packs/` — 3 industry pack
- `templates-vn/` — 191 template vendored từ bb-plugin
- `vault-template/` — Obsidian scaffold
- `adapters/` — Claude Code + Cowork
- `tests/` — unit + integration + e2e
- `docs/` — getting started + how-to-create-pack

## Definition of Done v1

- [ ] Repo public, README VN đầy đủ
- [ ] `pip install -e .` work Win/Mac/Linux
- [ ] Wizard sinh vault valid
- [ ] Test case B (chiến dịch QC) chạy E2E < 25 phút, < $2
- [ ] 12 phòng core (+ pack-specific 13-XX) có agents thật
- [ ] 3 pack (F&B, Retail, Tech-SaaS) chạy được test riêng
- [ ] BYOT demo work
- [ ] 6 RULES enforced + có test
- [ ] Claude Code + Cowork adapter E2E
- [ ] `docs/getting-started.md` cho non-tech CEO

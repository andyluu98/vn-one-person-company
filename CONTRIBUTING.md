# Đóng góp cho VN One Person Company

Cảm ơn bạn quan tâm! Đây là hướng dẫn ngắn để tham gia phát triển.

## Setup môi trường dev

```bash
git clone https://github.com/<owner>/<repo>.git
cd <repo>
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -e ".[dev]"
```

## Chạy tests

```bash
python -m pytest tests/ -q
```

Tất cả 261+ tests phải pass trước khi gửi PR.

## Coding standards

- **Python 3.11+**, type hints bắt buộc cho public API
- **Tiếng Việt** trong: agent prompts, output reports, user-facing strings
- **Tiếng Anh** trong: code comments (technical), variable names, commit messages
- **kebab-case** cho file Python, **snake_case** cho function/variable
- File nhỏ (<200 dòng), modular hóa nếu lớn
- KHÔNG hardcode API keys, paths cá nhân

## Quy tắc 6 RULES (bất di bất dịch)

1. **Brain-first** — không hỏi CEO khi chưa đọc Brain
2. **Domain-neutral** — KHÔNG leak finance/trading thuật ngữ
3. **Single source of truth** — Obsidian vault canonical
4. **CEO-friendly language** — translator pipeline cho output
5. **Live research with citations** — search có cite + validator
6. **BYOT** — DN custom > pack > default

PR vi phạm RULES sẽ bị reject.

## Quy trình PR

1. Fork + branch: `feat/<feature>` hoặc `fix/<bug>`
2. Implement + tests (TDD khuyến khích)
3. Commit: conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`)
4. KHÔNG đề cập AI/Claude trong commit message
5. PR mô tả rõ: vấn đề, giải pháp, RULES nào áp dụng
6. CI phải xanh

## Cấu trúc thư mục

```
core/                 # Python engine
├── brain/            # Brain layer (reader, gap, schema)
├── agents/           # Agent loaders + base
├── meeting/          # LangGraph debate engine
├── orchestrator/     # FlowController + Router + tools
├── tools/            # 6 research tools
├── translator/       # CEO-friendly language pipeline
├── obsidian/         # Vault I/O + DocWriter + Git
└── llm/              # LLM provider abstraction (MCP sampling, Anthropic)
departments/          # 12 core phòng ban (YAML + agent .md)
packs/                # Industry packs (F&B, Retail, Tech-SaaS)
templates-vn/         # 191 template VN-compliant
vault-template/       # Obsidian scaffold cho onboard
adapters/             # Claude Code/Cowork integration
tests/                # unit / integration / e2e
docs/                 # User docs
plans/                # Implementation plans (dev notes)
```

## Cách thêm Pack mới

Xem `docs/how-to-create-pack.md` (sẽ viết).

## Cách thêm Tool research

1. Tạo `core/tools/<name>.py` extends `BaseTool`
2. Implement `is_available()` (check key/dep)
3. Implement `run(query, **kwargs) -> ToolResult`
4. Đăng ký vào `core/orchestrator/research_phase.py:TOOL_REGISTRY`
5. Update `core/tools/tool_router.py:_FULL_TOOL_DESCRIPTIONS`
6. Test (`tests/unit/test_tool_<name>.py`)

## Báo bug / đề xuất feature

Mở issue trên GitHub với template phù hợp.

## License

Đóng góp đồng nghĩa bạn đồng ý code release dưới **Apache License 2.0** (xem [LICENSE](LICENSE) và [NOTICE](NOTICE)).

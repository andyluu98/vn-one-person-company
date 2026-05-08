# Roadmap — VN One Person Company

> Hướng đi từ alpha (chỉ founder dùng) đến v1 public open-source (5-10 dev contribute) đến SaaS thực sự (chủ DN non-tech dùng).

**Cập nhật:** 2026-05-08
**Trạng thái hiện tại:** Alpha — chạy được trên máy founder với DeepSeek, nhưng nhiều bug blocker cho dev khác.

---

## 🎯 Mục tiêu sản phẩm

**Mục tiêu cuối:** Open-source tool cho freelancer + chủ DN 1 người Việt Nam vận hành đầy đủ phòng ban "ảo" qua AI agents debate, mà chỉ tốn 200-500k/tháng (DeepSeek API + Claude Pro subscription).

**Người dùng mục tiêu:**

| Phase | Persona | Yêu cầu của họ |
|---|---|---|
| Alpha (now) | Founder + 1-2 dev contributor | Đọc code được, không cần doc |
| v1 (1-2 tháng) | 5-10 dev VN tự setup cho DN của mình | README + setup guide tốt, error rõ ràng |
| v2 (3-6 tháng) | Founder non-tech (qua web app) | Zero install, browser thôi |
| v3 (6-12 tháng) | Mass adoption (1000+ DN) | Multi-tenant SaaS, billing |

---

## 📋 Phase v1 — Dev-Friendly (1-2 tháng)

Target: dev khác clone repo về, làm theo README, dùng được cho DN của mình mà **không cần hỏi maintainer**.

### 🔴 P0 — BLOCKER (phải xong trước v1 release)

| # | Việc | Status | Effort | Owner |
|---|---|---|---|---|
| 1 | Multi-LLM provider chính thức (DeepSeek/OpenAI/Gemini, không chỉ Anthropic) | 🟡 Done 80% (DeepSeek) | 2 giờ còn lại | TBD |
| 2 | CLI commands load `vault/.env` đúng cách | ✅ Done | - | - |
| 3 | DeepSeek thinking mode toggle (default OFF cho meeting tốc độ) | ✅ Done | - | - |
| 4 | Brain parser khoan dung — accept `## Tầm nhìn (3-5 năm)`, không chỉ `## Tầm nhìn` | ❌ TODO | 2 giờ | TBD |
| 5 | Error messages tiếng Việt thay vì Python traceback | ❌ TODO | 4 giờ | TBD |
| 6 | `vn-os doctor` command — verify env, .vncoderc, .env, brain → checklist | ❌ TODO | 3 giờ | TBD |
| 7 | LangGraph version pin (đang dùng 0.2.0+ — version churn cao) | ❌ TODO | 1 giờ | TBD |
| 8 | Tests pass với DeepSeek provider (hiện 261 tests, có thể có hardcoded Anthropic) | ❌ TODO | 4 giờ | TBD |

### 🟡 P1 — CRITICAL (cần để dev khác dùng được smooth)

| # | Việc | Status | Effort |
|---|---|---|---|
| 9 | Brain wizard CLI — `vn-os brain-wizard` hỏi 16 câu → tự fill 8 file | ❌ TODO | 1 ngày |
| 10 | Task templates — `vn-os run --template hop-dong-lao-dong` | ❌ TODO | 1 ngày |
| 11 | Better progress indicator — "Đang gọi 7 phòng họp... (3/7)" | ❌ TODO | 0.5 ngày |
| 12 | Resumable tasks — meeting fail giữa chừng có thể resume | ❌ TODO | 1 ngày |
| 13 | Cost tracker per task — in cost USD sau khi xong | ❌ TODO | 0.5 ngày |
| 14 | README cập nhật (DeepSeek setup, examples, troubleshooting) | ❌ TODO | 0.5 ngày |
| 15 | `examples/` folder với 3 vault sample (F&B, Retail, Tech-SaaS) đã fill Brain | ❌ TODO | 1 ngày |
| 16 | Demo video 5 phút trên Youtube (setup + chạy 1 task end-to-end) | ❌ TODO | 0.5 ngày |

### 🟢 P2 — NICE-TO-HAVE (sau khi v1 release)

| # | Việc | Effort |
|---|---|---|
| 17 | Docker image | 1 ngày |
| 18 | GitHub Actions CI (test trên Win/Mac/Linux) | 1 ngày |
| 19 | Cookbook — examples cho 5-10 ngành ngoài v1 packs | 1 tuần |
| 20 | Contributor guide chi tiết hơn `CONTRIBUTING.md` hiện tại | 1 ngày |

---

## 🐛 Bugs đã phát hiện trong session 2026-05-08

> Session debug end-to-end với vault Sao Việt + Cowork + CLI.

| # | Bug | Severity | Repro | Fix |
|---|---|---|---|---|
| B1 | `vn_run`, `vn_draft` qua MCP timeout 60s (Cowork client cap) | 🔴 Critical | Gọi vn_draft với brief bất kỳ qua Cowork | Document limitation. Khuyến nghị CLI cho task heavy. |
| B2 | CLI `run/resume/meeting/approve/execute` không gọi `apply_vault_env_to_os` → DEEPSEEK_API_KEY không vào env | 🔴 Critical | Tạo vault/.env, chạy vn-os run | ✅ Patched 2026-05-08 |
| B3 | `core/llm/providers.py` chỉ có ClaudeProvider + MCPSamplingProvider, không có OpenAI/Gemini/DeepSeek dù pyproject.toml có dep | 🔴 Critical | Set OPENAI_API_KEY → vẫn dùng Anthropic | ✅ Patched (DeepSeek). OpenAI/Gemini TODO. |
| B4 | DeepSeek v4-pro thinking mode default ON → meeting có 7 LLM calls × 30-90s = 5-10 phút | 🟡 High | vn-os meeting với DeepSeek | ✅ Patched (extra_body disable thinking) |
| B5 | Brain parser yêu cầu heading exact `## Tầm nhìn`, fail với `## Tầm nhìn (3-5 năm)` | 🟡 High | Heading có suffix | TODO P0-#4 |
| B6 | `vault-template/01-Departments/` không có sẵn — phải clone từ `repo/departments/` | 🟢 Medium | Onboard vault mới | TODO — fix `vn_onboard` |
| B7 | `obsidian_delete_file` qua Obsidian REST API timeout cho folder (chỉ work với file) | 🟢 Medium | MCP delete folder | Document — khuyến nghị xóa qua Obsidian app |

---

## 📊 Decisions đã chốt trong session 2026-05-08

1. **Default LLM:** DeepSeek v4-pro (thay vì Claude Sonnet) — rẻ ~10x, đủ chất lượng cho task vận hành.
2. **Fallback:** Anthropic API (cần ANTHROPIC_API_KEY trong .env). MCP sampling chỉ dùng cho dev experience qua Claude Desktop.
3. **Workflow chính:** CLI (vn-os) thay vì MCP tool calls — tránh Cowork 60s timeout cho task heavy.
4. **Thinking mode:** Default OFF cho meeting (tốc độ). User opt-in qua config nếu muốn deep reasoning.

---

## 🚀 Phase v2 — Non-Tech Founder (3-6 tháng)

Target: chủ quán phở 50 tuổi, không biết code, dùng được qua web browser.

| # | Việc | Effort |
|---|---|---|
| 21 | Web UI Streamlit/Next.js — chat interface | 2 tuần |
| 22 | Onboarding wizard — chọn ngành → tự apply pack → fill Brain qua form | 1 tuần |
| 23 | Visual brain editor — drag-drop, không cần Markdown | 2 tuần |
| 24 | Auth + multi-tenant — mỗi user 1 vault | 1 tuần |
| 25 | Deploy hosted version — vn-os.vn (custom domain VN) | 1 tuần |
| 26 | Stripe billing — free tier 5 task/tháng, pro 200k/tháng | 1 tuần |

---

## 🌐 Phase v3 — Mass Adoption (6-12 tháng)

Target: 1000+ DN VN dùng. Marketing + community.

| # | Việc |
|---|---|
| 27 | Mobile app (React Native) |
| 28 | Vietnamese spell-check + accent fix |
| 29 | Plugin marketplace — DN bán template, share pack |
| 30 | Integration: Misa, Sapo, KiotViet, Shopee API |
| 31 | Multi-language (Cambodia, Lao, ...) |

---

## 🤝 Cách contribute

Hiện tại repo cần:

1. **Code reviewers** — review PR fix bugs P0/P1
2. **Test với DN khác** — chạy vault thật của bạn, log bugs vào issue
3. **Doc translation** — README hiện chỉ tiếng Việt
4. **Industry pack contribute** — mở pack cho ngành mới (Healthcare, Edu, Real Estate)
5. **Template contribute** — mỗi pack cần 30-50 template chất lượng

Mở issue: https://github.com/<owner>/<repo>/issues
Discord/Zalo community: TBD (nếu cần)

---

## 📜 License + Sustainability

- **License:** MIT (đã chốt)
- **Sustainability model:** TBD — có thể combine open-source core + paid hosted SaaS (BSL hoặc COSS pattern)
- **Maintainer commitment:** Founder cam kết maintain ít nhất 6 tháng đầu

---

## 📌 Tóm gọn trạng thái hiện tại

✅ **Đã hoạt động:**
- Brain reader/parser (với format chặt)
- 13 phòng core + F&B pack scaffold
- DeepSeek provider (sau patch session 2026-05-08)
- CLI run stage 1 (router + gap analyzer)
- Obsidian MCP integration cho doc viewing/editing

🟡 **Cần fix gấp:**
- 6 P0 blockers list trên
- Meeting stage chưa verify được end-to-end (LangGraph + 7 agents debate)
- Onboarding cho dev mới chưa polished

🔴 **Chưa làm:**
- Tất cả P1 (wizard, templates, progress, resumable)
- Tất cả v2 (web UI)
- Test coverage cho non-Anthropic provider

---

**Next step ngay:** Verify meeting stage chạy được với DeepSeek + thinking mode disabled. Nếu fail → cần debug LangGraph compatibility với non-Anthropic provider.

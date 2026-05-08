"""MCP server wrapping vn-business-os FlowController as MCP tools.

Khi chạy trong Claude Desktop / Code, mọi LLM call route qua MCP sampling
(MCPSamplingProvider) — dùng subscription của user, không cần ANTHROPIC_API_KEY.

Run:
    python -m core.mcp_server          # stdio transport
    vn-os-mcp                          # via console_script (after install)

Tools registered (9):
    vn_run         — Stage 1: brief → router → gap → clarify (PAUSE)
    vn_resume      — Stage 2: resume after CEO answers clarification
    vn_meeting     — Stage 3: research + meeting → 07-decision-report.md (Stop 1)
    vn_approve     — Stage 4: CEO approves → 08-execution-plan.md (Stop 2)
    vn_execute     — Stage 5: render .docx/.xlsx into 03-Outputs/
    vn_draft       — Single LLM call cho boilerplate (HĐLĐ, JD, nội quy...) — fast path
    vn_status      — inspect vault (Brain summary + tasks)
    vn_onboard     — run onboard wizard creating new vault scaffold
    vn_upgrade     — refresh existing vault với enriched prompts + aliases
"""
from __future__ import annotations
import os
import re
from pathlib import Path

from mcp.server.fastmcp import Context, FastMCP

from core.brain.reader import BrainReader
from core.llm.providers import MCPSamplingProvider
from core.obsidian.vault import ObsidianVault
from core.onboard import onboard_vault
from core.orchestrator.flow_controller import FlowController
from core.upgrade import upgrade_vault


mcp = FastMCP("vn-business-os")


def _make_fc(vault_root: str, ctx: Context) -> FlowController:
    """Build FlowController bound to current MCP request session.

    `ctx.session` is the ServerSession exposing async `create_message(...)` —
    MCPSamplingProvider routes complete() through it (sampling protocol).

    Cũng load vault/.env (TAVILY_API_KEY, ...) vào os.environ để tools tìm thấy.
    """
    from core.utils.config import apply_vault_env_to_os
    apply_vault_env_to_os(Path(vault_root))

    session = ctx.session
    llm = MCPSamplingProvider(session)
    return FlowController(vault_root=Path(vault_root), llm=llm)


def _vault_root_from_task(task_folder: Path) -> Path:
    """Task folders live at <vault>/02-Tasks/<slug>/ — climb 2 levels."""
    return task_folder.parent.parent


@mcp.tool()
async def vn_run(brief: str, vault: str, ctx: Context) -> dict:
    """Stage 1: brief → router → gap → clarification (PAUSE).

    ⏱️ Duration: 20-50s (2-3 LLM calls). Borderline với Cowork 60s timeout.
    Nếu fail qua chat → chạy qua PowerShell `vn-os run --vault <path> --brief "..."`.

    Returns task_folder path + stage. If stage == PAUSE_CLARIFICATION,
    CEO needs to answer questions in 03-clarification.md before vn_resume.
    """
    fc = _make_fc(vault, ctx)
    result = await fc.arun(brief)
    return {
        "stage": result.stage.value,
        "task_folder": str(result.task_folder),
        "message": result.message,
    }


@mcp.tool()
def vn_resume(task_folder: str, ctx: Context) -> dict:
    """Stage 2: resume after CEO answers 03-clarification.md.

    Validates all questions answered, writes 03-clarification-answered.md.
    """
    folder = Path(task_folder)
    fc = _make_fc(str(_vault_root_from_task(folder)), ctx)
    result = fc.resume_after_clarification(folder)
    return {
        "stage": result.stage.value,
        "task_folder": str(result.task_folder),
        "message": result.message,
    }


@mcp.tool()
def vn_meeting(
    task_folder: str,
    ctx: Context,
    departments: list[str] | None = None,
) -> dict:
    """Stage 3: research + meeting (Pro/Con + Perspective) + synthesizer.

    ⚠️ TIMEOUT WARNING: Tool này chạy 7+ LLM calls tuần tự (60-180s).
    KHÔNG dùng được qua Cowork/Claude Desktop (60s timeout hard cap).
    Khuyến nghị: Chạy qua PowerShell `vn-os meeting <task_folder>` hoặc
    Claude Code CLI (set MCP_TOOL_TIMEOUT=300000).

    Auto-extracts departments from 01-routing.md if not provided.
    Output: 07-decision-report.md (Stop 1).
    """
    folder = Path(task_folder)
    fc = _make_fc(str(_vault_root_from_task(folder)), ctx)

    if not departments:
        routing_path = folder / "01-routing.md"
        if not routing_path.exists():
            return {
                "stage": "ERROR",
                "task_folder": str(folder),
                "message": "01-routing.md not found — run vn_run first",
            }
        m = re.search(r"\*\*Departments:\*\*\s*(.+)", routing_path.read_text(encoding="utf-8"))
        if not m:
            return {
                "stage": "ERROR",
                "task_folder": str(folder),
                "message": "Cannot parse Departments from 01-routing.md",
            }
        departments = [d.strip() for d in m.group(1).split(",") if d.strip()]

    result = fc.run_meeting(folder, departments=departments)
    return {
        "stage": result.stage.value,
        "task_folder": str(result.task_folder),
        "message": result.message,
    }


@mcp.tool()
def vn_approve(task_folder: str, ctx: Context) -> dict:
    """Stage 4: CEO approves decision report → 08-execution-plan.md (Stop 2)."""
    folder = Path(task_folder)
    fc = _make_fc(str(_vault_root_from_task(folder)), ctx)
    result = fc.approve_decision(folder)
    return {
        "stage": result.stage.value,
        "task_folder": str(result.task_folder),
        "message": result.message,
    }


@mcp.tool()
def vn_execute(task_folder: str, ctx: Context) -> dict:
    """Stage 5: render outputs (.docx/.xlsx) into vault/03-Outputs/<task>/."""
    folder = Path(task_folder)
    fc = _make_fc(str(_vault_root_from_task(folder)), ctx)
    result = fc.execute(folder)
    return {
        "stage": result.stage.value,
        "task_folder": str(result.task_folder),
        "message": result.message,
    }


@mcp.tool()
async def vn_draft(
    brief: str,
    vault: str,
    ctx: Context,
    doc_type: str = "tài liệu",
) -> dict:
    """Fast path: soạn 1 tài liệu boilerplate qua 1 LLM call (không debate).

    ⏱️ Duration: 10-30s (1 LLM call). OK qua Cowork timeout 60s
    cho doc ngắn (HD, JD, SOP). Doc dài có thể borderline.

    Dùng cho: HĐLĐ, JD, nội quy, phiếu thu, SOP đơn giản, thư mời họp...
    KHÔNG dùng cho: quyết định chiến lược, doc rủi ro pháp lý cao.

    Trade-off: nhanh (~10-30s thay vì 1-3 phút của vn_run+vn_meeting)
    nhưng KHÔNG qua multi-perspective review.

    Args:
        brief: Yêu cầu cụ thể (vd "HĐLĐ trợ lý kế toán cafe ABC, lương 10tr").
        vault: Vault path.
        doc_type: Loại doc (vd "hợp đồng lao động", "JD", "nội quy", "phiếu thu").

    Returns dict {task_folder, draft_path, message}.
    """
    from core.orchestrator.draft import adraft_document
    from core.utils.config import apply_vault_env_to_os

    vault_path = Path(vault)
    apply_vault_env_to_os(vault_path)

    llm = MCPSamplingProvider(ctx.session)
    return await adraft_document(
        brief=brief,
        vault_root=vault_path,
        llm=llm,
        doc_type=doc_type,
    )


@mcp.tool()
def vn_status(vault: str = "") -> dict:
    """Inspect vault — Brain summary + active depts + tasks + tool availability.

    ⚡ Duration: <1s (no LLM call). Luôn OK qua Cowork.

    Vault resolution: nếu không truyền, đọc từ env var VN_OS_DEFAULT_VAULT
    (set trên Windows qua: setx VN_OS_DEFAULT_VAULT "F:\\vaults\\<TênDN>").

    Live research tools (web/luật/địa phương/đối thủ) chỉ chạy khi có
    TAVILY_API_KEY. vn_status báo rõ tool nào đang sẵn sàng vs skipped để CEO biết
    decision report sẽ dựa research thật hay chỉ Brain + LLM knowledge.
    """
    # Fallback: nếu không truyền vault, đọc từ env VN_OS_DEFAULT_VAULT
    if not vault:
        vault = os.environ.get("VN_OS_DEFAULT_VAULT", "")
        if not vault:
            return {
                "error": (
                    "Không tìm thấy vault path. Cách fix: "
                    "(1) Truyền tham số vault='F:\\vaults\\<TênDN>', HOẶC "
                    "(2) Set env var: setx VN_OS_DEFAULT_VAULT 'F:\\vaults\\<TênDN>' "
                    "rồi restart Claude Desktop."
                ),
            }
    vault_path = Path(vault)

    # Apply vault/.env to os.environ trước khi check tool availability
    from core.utils.config import apply_vault_env_to_os
    apply_vault_env_to_os(vault_path)

    try:
        brain = BrainReader(vault_path).load()
    except FileNotFoundError as e:
        return {"error": str(e), "vault": vault}

    vault_obj = ObsidianVault(vault_path)
    tasks = vault_obj.list_tasks()

    from core.orchestrator.research_phase import (
        list_available_tools, list_skipped_tools,
    )

    # P2.5: Báo packs đã cài + compliance refs (PackLoader integration)
    packs_info: list[dict] = []
    try:
        from core.agents.pack_loader import PackLoader
        from core.utils.config import load_vault_env
        # Đọc .vncoderc của vault để biết packs đã cài
        vncoderc = vault_path / ".vncoderc"
        installed_codes: list[str] = []
        if vncoderc.exists():
            import yaml
            cfg = yaml.safe_load(vncoderc.read_text(encoding="utf-8")) or {}
            installed_codes = cfg.get("packs", []) or []
        repo = Path(__file__).parent.parent
        loader = PackLoader(repo / "packs")
        for code in installed_codes:
            try:
                pack = loader.load(code)
                packs_info.append({
                    "code": pack.code,
                    "name": pack.name,
                    "version": pack.version,
                    "compliance_refs": pack.compliance_refs,
                })
            except FileNotFoundError:
                pass
    except Exception:  # noqa: BLE001
        pass

    workflow_rules = """🚨 QUY TẮC PHÂN TASK BẮT BUỘC (Claude tự áp dụng):

✅ TASK NHẸ — Bạn (Claude) LÀM TRỰC TIẾP trong chat (gọi MCP tools):
   - vn_status (xem trạng thái vault) — luôn OK
   - obsidian_* (đọc/sửa file vault) — luôn OK
   - Tư vấn dựa trên Brain context (KHÔNG gọi vn_run/vn_meeting/vn_draft)

❌ TASK NẶNG — Bạn KHÔNG ĐƯỢC gọi tool, chỉ sinh command PowerShell cho user paste:
   - vn_run — 20-50s, borderline với Cowork 60s timeout
   - vn_meeting — 7+ LLM calls (60-180s), TIMEOUT chắc chắn
   - vn_approve — có LLM call, TIMEOUT
   - vn_draft — DeepSeek thực tế > 60s, TIMEOUT
   - vn_resume — có LLM call, TIMEOUT

Khi user yêu cầu task NẶNG (soạn doc, debate, brainstorm, phân tích chiến lược):
   1. KHÔNG gọi tool MCP — chỉ sinh command PowerShell
   2. Format command sẵn copy-paste với cú pháp NGẮN:
      cd "<vault_path>"
      $vnos = "<repo>\\.venv\\Scripts\\vn-os.exe"
      & $vnos run "<brief content>"           # KHÔNG cần --vault --brief
      & $vnos meeting "<task_folder>"
      & $vnos approve "<task_folder>"
      & $vnos execute "<task_folder>"
      
      ⚠️ ĐỪNG dùng cú pháp dài kiểu: & $vnos run --vault . --brief "..."
      → CLI chấp nhận cả 2 nhưng cú pháp ngắn dễ đọc + ít sai hơn.
   3. Báo thời gian ước tính
   4. Hướng dẫn user vào Obsidian xem kết quả tại 02-Tasks/<folder>/
   5. Đợi user báo "xong" → đọc file qua obsidian_get_file_contents → tóm tắt

Tham khảo chi tiết: F:\\.work\\vn-one-person-company\\README-USER.md (Phần 3)
"""

    return {
        "vault": str(vault_path),
        "icp": brain.strategy.icp[:200],
        "vision": brain.strategy.vision[:200],
        "products": len(brain.products),
        "active_departments": brain.headcount.active_departments,
        "state": brain.state,
        "active_tasks": [t.name for t in tasks],
        "tools_live": list_available_tools(),
        "tools_skipped": list_skipped_tools(),
        "packs": packs_info,
        "_workflow_rules": workflow_rules,
    }


@mcp.tool()
def vn_onboard(
    vault: str,
    packs: list[str] | None = None,
    tavily_api_key: str = "",
    anthropic_api_key: str = "",
    google_api_key: str = "",
    openai_api_key: str = "",
) -> dict:
    """Create vault scaffold for new company.

    Calls core.onboard.onboard_vault directly (no subprocess).

    Args:
        vault: Path where vault will be created
        packs: Optional list of pack codes (fnb, retail, tech-saas)
        tavily_api_key: KHUYẾN NGHỊ — bật 4 search tools (luật/đối thủ/web/địa phương).
                        Lấy free tier tại https://tavily.com (1000 req/tháng miễn phí).
                        Nếu để trống: search tools sẽ skip gracefully — flow vẫn chạy
                        nhưng decision report dựa hoàn toàn vào Brain + LLM knowledge.
        anthropic_api_key: Optional fallback nếu không dùng MCP sampling
        google_api_key: Optional cho Gemini fallback
        openai_api_key: Optional cho GPT fallback

    Returns dict với steps, packs, warnings, next_steps, api_keys_saved.
    """
    keys = {
        "TAVILY_API_KEY": tavily_api_key,
        "ANTHROPIC_API_KEY": anthropic_api_key,
        "GOOGLE_API_KEY": google_api_key,
        "OPENAI_API_KEY": openai_api_key,
    }
    return onboard_vault(
        vault_path=vault,
        packs=packs or [],
        init_git=True,
        api_keys=keys,
    )


@mcp.tool()
def vn_upgrade(
    vault: str,
    refresh_agents: bool = True,
    refresh_dept_yaml: bool = True,
    refresh_brain_aliases: bool = True,
    regenerate_hubs: bool = False,
) -> dict:
    """Upgrade vault hiện có lên phiên bản plugin mới.

    Refresh agent prompts, department YAML, Brain aliases. KHÔNG động đến
    Brain content (CEO đã điền), Tasks, Outputs.

    Args:
        vault: Đường dẫn vault hiện có
        refresh_agents: Ghi đè agent .md files với enriched prompts mới
        refresh_dept_yaml: Ghi đè department.yaml (aliases_vn, routing rules)
        refresh_brain_aliases: Inject aliases vào frontmatter Brain files
        regenerate_hubs: Xoá index.md cũ + tạo lại (mặc định KHÔNG)

    Returns dict với count file refreshed + warnings.
    """
    return upgrade_vault(
        vault_path=vault,
        refresh_agents=refresh_agents,
        refresh_dept_yaml=refresh_dept_yaml,
        refresh_brain_aliases=refresh_brain_aliases,
        regenerate_hubs=regenerate_hubs,
    )


def main() -> None:
    """Entry point — run MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()

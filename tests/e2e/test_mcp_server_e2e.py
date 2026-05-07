"""E2E test: MCP server tools flow with mocked sampling.

Verifies user can run vn-business-os entirely qua MCP (not subprocess CLI),
proving v0.2.0 architecture works.
"""
import asyncio
import json
import shutil
from pathlib import Path
from unittest.mock import MagicMock
import pytest


REPO = Path(__file__).parent.parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "techco-vault"


def _make_ctx(responses: list[str]):
    """Build mock Context with sampling responses queue.

    Mock shape matches integration test: `resp.content` is a single object
    with `.text` (matches MCPSamplingProvider._extract_text fallback chain).
    """
    mock_session = MagicMock()

    response_objs = []
    for text in responses:
        r = MagicMock()
        r.content = MagicMock()
        r.content.text = text
        response_objs.append(r)

    # Pad with sensible default for any extra calls (defensive).
    default = MagicMock()
    default.content = MagicMock()
    default.content.text = "{}"
    mock_session.create_message.side_effect = response_objs + [default] * 20

    ctx = MagicMock()
    ctx.session = mock_session
    ctx.request_context.session = mock_session
    return ctx, mock_session


def test_mcp_vn_status_no_llm(tmp_path):
    """vn_status doesn't need LLM — just reads Brain."""
    vault = tmp_path / "vault"
    shutil.copytree(FIXTURE, vault)

    from core.mcp_server import vn_status
    result = vn_status(str(vault))

    assert "icp" in result
    assert result["products"] == 3
    # Active departments may be empty depending on Brain state — accept either.
    assert isinstance(result["active_departments"], list)


def test_mcp_vn_run_routes_via_sampling(tmp_path):
    """vn_run must call session.create_message (not Anthropic API directly)."""
    vault = tmp_path / "vault"
    shutil.copytree(FIXTURE, vault)
    (vault / "02-Tasks").mkdir(exist_ok=True)

    # Pre-canned responses for: router (JSON), gap_analysis ([])
    ctx, mock_session = _make_ctx([
        '{"class": "SIMPLE", "departments": ["04-people"], "reasoning": "JD task"}',
        '[]',  # No gaps → skip clarification
    ])

    from core.mcp_server import vn_run
    result = asyncio.run(vn_run(brief="Soạn JD kế toán trưởng", vault=str(vault), ctx=ctx))

    assert "stage" in result
    assert "task_folder" in result
    assert mock_session.create_message.called
    # Verify task folder created
    task_folder = Path(result["task_folder"])
    assert task_folder.exists()
    assert (task_folder / "00-brief.md").exists()
    assert (task_folder / "01-routing.md").exists()


def test_mcp_full_flow_brief_to_clarification_pause(tmp_path):
    """Full flow: vn_run → PAUSE_CLARIFICATION with questions written."""
    vault = tmp_path / "vault"
    shutil.copytree(FIXTURE, vault)
    (vault / "02-Tasks").mkdir(exist_ok=True)

    ctx, mock_session = _make_ctx([
        # Router: COMPLEX
        json.dumps({
            "class": "COMPLEX",
            "departments": ["07-marketing", "03-finance"],
            "reasoning": "campaign",
        }),
        # Gap analysis: 1 gap
        json.dumps([{
            "field": "ICP", "severity": "CRITICAL",
            "current_value": "SME", "brief_value": "khách 50tr+",
            "reason": "Brief lệch", "citation": "00-Brain/strategy.md",
        }]),
        # Question gen
        json.dumps([{
            "text": "Pivot hay test?",
            "citation": "00-Brain/strategy.md",
            "choices": ["Pivot", "Test"],
            "severity": "CRITICAL", "free_text": False,
        }]),
    ])

    from core.mcp_server import vn_run
    result = asyncio.run(vn_run(
        brief="Tạo chiến dịch QC nhắm khách thu nhập 50tr+",
        vault=str(vault),
        ctx=ctx,
    ))

    assert result["stage"] == "PAUSE_CLARIFICATION"
    task_folder = Path(result["task_folder"])
    assert (task_folder / "03-clarification.md").exists()

    clarif = (task_folder / "03-clarification.md").read_text(encoding="utf-8")
    # RULE 1: citation present
    assert "00-Brain/strategy.md" in clarif


def test_mcp_no_anthropic_api_key_needed(tmp_path, monkeypatch):
    """Verify ANTHROPIC_API_KEY env not required when using MCP sampling."""
    vault = tmp_path / "vault"
    shutil.copytree(FIXTURE, vault)
    (vault / "02-Tasks").mkdir(exist_ok=True)

    # Remove ANTHROPIC_API_KEY from env
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    ctx, mock_session = _make_ctx([
        '{"class": "SIMPLE", "departments": ["04-people"], "reasoning": "x"}',
        '[]',
    ])

    from core.mcp_server import vn_run
    result = asyncio.run(vn_run(brief="test", vault=str(vault), ctx=ctx))

    # Must succeed without API key — proves MCP sampling path is used
    assert "stage" in result
    assert mock_session.create_message.called


def test_install_mcp_then_uninstall_roundtrip(tmp_path):
    """install-mcp followed by uninstall-mcp leaves config clean."""
    cfg = tmp_path / "claude_desktop_config.json"

    from core.install_mcp import install, uninstall

    install_result = install(config_path=cfg)
    assert install_result["ok"] is True

    # Read config — vn-business-os entry exists
    config = json.loads(cfg.read_text(encoding="utf-8"))
    assert "vn-business-os" in config["mcpServers"]

    # Uninstall
    uninstall_result = uninstall(config_path=cfg)
    assert uninstall_result["removed"] is True

    # Config still valid JSON, vn-business-os removed
    config_after = json.loads(cfg.read_text(encoding="utf-8"))
    assert "vn-business-os" not in config_after.get("mcpServers", {})

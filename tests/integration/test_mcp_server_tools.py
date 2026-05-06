"""Test MCP server tool registration + basic invocation with mocked Context.

Verifies:
- module imports + 8 tools registered with FastMCP
- vn_status reads Brain summary from fixture vault (no LLM)
- vn_run routes LLM calls via MCPSamplingProvider → ctx.session.create_message
"""
from __future__ import annotations
import asyncio
import json
import shutil
from pathlib import Path
from unittest.mock import MagicMock

import pytest


REPO = Path(__file__).parent.parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "techco-vault"


def test_mcp_server_imports():
    """Server module imports + all 8 tool fns exposed."""
    from core.mcp_server import (
        mcp,
        vn_run,
        vn_resume,
        vn_meeting,
        vn_approve,
        vn_execute,
        vn_status,
        vn_onboard,
        vn_upgrade,
    )
    assert mcp.name == "vn-business-os"


def test_mcp_server_has_8_tools():
    """FastMCP.list_tools() returns the 8 registered tools."""
    from core.mcp_server import mcp

    tools = asyncio.run(mcp.list_tools())
    names = sorted(t.name for t in tools)
    assert names == sorted([
        "vn_run",
        "vn_resume",
        "vn_meeting",
        "vn_approve",
        "vn_execute",
        "vn_status",
        "vn_onboard",
        "vn_upgrade",
    ])


def test_mcp_tool_schemas_exclude_context_param():
    """Context parameter must be auto-injected, not exposed in inputSchema."""
    from core.mcp_server import mcp

    tools = asyncio.run(mcp.list_tools())
    by_name = {t.name: t for t in tools}

    # vn_run: brief + vault, NO ctx
    vn_run_props = set(by_name["vn_run"].inputSchema.get("properties", {}).keys())
    assert vn_run_props == {"brief", "vault"}

    # vn_status: only vault (no ctx — it's pure)
    vn_status_props = set(by_name["vn_status"].inputSchema.get("properties", {}).keys())
    assert vn_status_props == {"vault"}


def test_vn_status_returns_brain_summary(tmp_path):
    """vn_status reads Brain from fixture vault — pure, no LLM/session."""
    vault = tmp_path / "vault"
    shutil.copytree(FIXTURE, vault)

    from core.mcp_server import vn_status

    result = vn_status(str(vault))

    assert "icp" in result
    assert "SME" in result["icp"]
    assert result["products"] == 3
    assert result["state"] in {"growth", "seed", "mature", "pre-seed", "pivot", "unknown"}
    assert isinstance(result["active_departments"], list)
    assert isinstance(result["active_tasks"], list)


def test_vn_run_routes_llm_via_mcp_sampling_provider(tmp_path):
    """vn_run must build FlowController with MCPSamplingProvider bound to ctx.session.

    Proof: mock session.create_message gets called by Router/GapAnalyzer through
    the provider chain.
    """
    vault = tmp_path / "vault"
    shutil.copytree(FIXTURE, vault)
    (vault / "02-Tasks").mkdir(exist_ok=True)

    # Build mock session — sync create_message returning fake responses.
    # MCPSamplingProvider auto-awaits if result is awaitable; sync MagicMock
    # returns are NOT awaitable, so provider takes the fallback path.
    mock_session = MagicMock()

    def make_resp(text: str):
        resp = MagicMock()
        resp.content = MagicMock()
        resp.content.text = text
        return resp

    # Sequential responses: router (JSON classification), then gap_analyzer (no gaps).
    # If more LLM calls happen, MagicMock will keep returning a sensible default.
    fake_responses = [
        make_resp(json.dumps({
            "class": "SIMPLE",
            "departments": ["04-people"],
            "reasoning": "JD task",
        })),
        make_resp("[]"),  # no gaps → skip clarification
    ]
    mock_session.create_message.side_effect = fake_responses + [make_resp("{}")] * 10

    mock_ctx = MagicMock()
    mock_ctx.session = mock_session

    from core.mcp_server import vn_run

    result = vn_run(brief="Soạn JD kế toán", vault=str(vault), ctx=mock_ctx)

    assert "stage" in result
    assert "task_folder" in result
    # Proof MCPSamplingProvider routed correctly through ctx.session
    assert mock_session.create_message.called
    # task folder created in vault
    assert Path(result["task_folder"]).exists()

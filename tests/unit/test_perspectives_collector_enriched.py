"""Tests for P1.1 — PerspectivesCollector loads per-agent enriched prompts."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.meeting.debate_state import new_meeting_state
from core.orchestrator.perspectives_collector import (
    PERSPECTIVE_PROMPT,
    PerspectivesCollector,
    _STANCE_SUFFIX,
)


# ── helpers ──────────────────────────────────────────────────────────────


def _make_llm(response: str = "mock-response") -> MagicMock:
    llm = MagicMock()
    llm.complete = MagicMock(return_value=response)
    return llm


REPO_ROOT = Path(__file__).parent.parent.parent


# ── Task 1: enriched agent prompt ────────────────────────────────────────


class TestEnrichedPromptLoading:
    """PerspectivesCollector should use agent .md body when file exists."""

    def test_uses_generic_prompt_when_no_agent_file(self, tmp_path):
        """Fallback to PERSPECTIVE_PROMPT when agent .md missing."""
        # Create minimal department structure without agents/ dir
        dept_dir = tmp_path / "07-marketing"
        dept_dir.mkdir()
        (dept_dir / "department.yaml").write_text(
            "code: 07-marketing\nname_vn: Marketing\ntier: 2\n"
            "description: Phong Marketing\nagents: []\ndefault_speaker: cmo\n",
            encoding="utf-8",
        )

        llm = _make_llm()
        collector = PerspectivesCollector(departments_root=tmp_path, llm=llm)
        state = new_meeting_state(brief="test brief", departments=["07-marketing"])
        result = collector.collect(state)

        assert "07-marketing" in result["perspectives"]
        # Verify LLM was called with generic fallback (system contains dept name)
        call_args = llm.complete.call_args
        messages = call_args[0][0]
        system_content = messages[0]["content"]
        assert "Marketing" in system_content
        # Should NOT contain enriched suffix when falling back
        assert _STANCE_SUFFIX.strip()[:30] not in system_content

    def test_uses_enriched_prompt_when_agent_file_exists(self, tmp_path):
        """Use agent .md system_prompt body when file present."""
        dept_dir = tmp_path / "03-finance"
        agents_dir = dept_dir / "agents"
        agents_dir.mkdir(parents=True)
        (dept_dir / "department.yaml").write_text(
            "code: 03-finance\nname_vn: Tài chính\ntier: 2\n"
            "description: Finance\nagents: [cfo]\ndefault_speaker: cfo\n",
            encoding="utf-8",
        )
        (agents_dir / "cfo.md").write_text(
            "---\nid: cfo\nname_vn: CFO\ndepartment: 03-finance\n---\n"
            "Bạn là CFO chuyên nghiệp với expertise về P&L, cash flow.",
            encoding="utf-8",
        )

        llm = _make_llm()
        collector = PerspectivesCollector(departments_root=tmp_path, llm=llm)
        state = new_meeting_state(brief="test brief", departments=["03-finance"])
        result = collector.collect(state)

        assert "03-finance" in result["perspectives"]
        call_args = llm.complete.call_args
        messages = call_args[0][0]
        system_content = messages[0]["content"]
        # Enriched body should be in system message
        assert "Bạn là CFO chuyên nghiệp" in system_content
        # Stance suffix appended
        assert "NHIỆM VỤ TRONG CUỘC HỌP" in system_content

    def test_fallback_when_agent_file_has_no_body(self, tmp_path):
        """Fallback to generic prompt when .md body is empty."""
        dept_dir = tmp_path / "03-finance"
        agents_dir = dept_dir / "agents"
        agents_dir.mkdir(parents=True)
        (dept_dir / "department.yaml").write_text(
            "code: 03-finance\nname_vn: Tài chính\ntier: 2\n"
            "description: Finance\nagents: [cfo]\ndefault_speaker: cfo\n",
            encoding="utf-8",
        )
        # .md with frontmatter but empty body
        (agents_dir / "cfo.md").write_text(
            "---\nid: cfo\nname_vn: CFO\ndepartment: 03-finance\n---\n",
            encoding="utf-8",
        )

        llm = _make_llm()
        collector = PerspectivesCollector(departments_root=tmp_path, llm=llm)
        state = new_meeting_state(brief="test brief", departments=["03-finance"])
        result = collector.collect(state)

        assert "03-finance" in result["perspectives"]
        call_args = llm.complete.call_args
        messages = call_args[0][0]
        system_content = messages[0]["content"]
        # Generic fallback used — dept name present
        assert "Tài chính" in system_content

    def test_fallback_on_parse_error(self, tmp_path):
        """Fallback gracefully when agent .md has malformed frontmatter."""
        dept_dir = tmp_path / "03-finance"
        agents_dir = dept_dir / "agents"
        agents_dir.mkdir(parents=True)
        (dept_dir / "department.yaml").write_text(
            "code: 03-finance\nname_vn: Tài chính\ntier: 2\n"
            "description: Finance\nagents: [cfo]\ndefault_speaker: cfo\n",
            encoding="utf-8",
        )
        # Missing 'id' field — AgentLoader raises ValueError
        (agents_dir / "cfo.md").write_text(
            "---\nname_vn: CFO\ndepartment: 03-finance\n---\nSome body text.",
            encoding="utf-8",
        )

        llm = _make_llm()
        collector = PerspectivesCollector(departments_root=tmp_path, llm=llm)
        state = new_meeting_state(brief="test brief", departments=["03-finance"])
        # Should NOT raise — graceful degradation
        result = collector.collect(state)
        assert "03-finance" in result["perspectives"]

    def test_unknown_department_returns_placeholder(self, tmp_path):
        """Missing department returns placeholder string, not exception."""
        llm = _make_llm()
        collector = PerspectivesCollector(departments_root=tmp_path, llm=llm)
        state = new_meeting_state(brief="test", departments=["99-unknown"])
        result = collector.collect(state)

        text = result["perspectives"].get("99-unknown", "")
        assert "99-unknown" in text or "chua ton tai" in text

    def test_vault_root_fallback_for_agent_path(self, tmp_path):
        """vault_root param allows finding agent .md in vault when not in departments_root."""
        # Simulated: departments_root = repo/departments (no agents/ there)
        repo_depts = tmp_path / "repo_departments"
        dept_dir = repo_depts / "03-finance"
        dept_dir.mkdir(parents=True)
        (dept_dir / "department.yaml").write_text(
            "code: 03-finance\nname_vn: Tài chính\ntier: 2\n"
            "description: Finance\nagents: [cfo]\ndefault_speaker: cfo\n",
            encoding="utf-8",
        )
        # Agent .md lives in vault, not repo
        vault_root = tmp_path / "vault"
        vault_agents_dir = vault_root / "01-Departments" / "03-finance" / "agents"
        vault_agents_dir.mkdir(parents=True)
        (vault_agents_dir / "cfo.md").write_text(
            "---\nid: cfo\nname_vn: CFO\ndepartment: 03-finance\n---\n"
            "CFO từ vault với enriched prompt.",
            encoding="utf-8",
        )

        llm = _make_llm()
        collector = PerspectivesCollector(
            departments_root=repo_depts, llm=llm, vault_root=vault_root
        )
        state = new_meeting_state(brief="brief", departments=["03-finance"])
        result = collector.collect(state)

        call_args = llm.complete.call_args
        system_content = call_args[0][0][0]["content"]
        assert "CFO từ vault với enriched prompt." in system_content

    def test_multiple_departments_parallel(self, tmp_path):
        """Collector handles multiple departments in parallel correctly."""
        for code, name in [("01-governance", "Quản trị"), ("07-marketing", "Marketing")]:
            d = tmp_path / code
            d.mkdir()
            # default_speaker must be a non-null string in Department model
            (d / "department.yaml").write_text(
                f'code: {code}\nname_vn: "{name}"\ntier: 1\n'
                f'description: "{name}"\nagents: []\ndefault_speaker: ""\n',
                encoding="utf-8",
            )

        llm = _make_llm("dept response")
        collector = PerspectivesCollector(departments_root=tmp_path, llm=llm)
        state = new_meeting_state(
            brief="brief", departments=["01-governance", "07-marketing"]
        )
        result = collector.collect(state)

        assert "01-governance" in result["perspectives"]
        assert "07-marketing" in result["perspectives"]
        assert llm.complete.call_count == 2

    def test_uses_repo_departments_for_real_dept(self):
        """Integration: collector works against real repo departments/ folder."""
        llm = _make_llm("response from real dept")
        collector = PerspectivesCollector(
            departments_root=REPO_ROOT / "departments", llm=llm
        )
        state = new_meeting_state(brief="expand product line", departments=["07-marketing"])
        result = collector.collect(state)

        assert "07-marketing" in result["perspectives"]
        assert llm.complete.call_count == 1
        # Verify messages were actually passed
        messages = llm.complete.call_args[0][0]
        assert any(m["role"] == "system" for m in messages)
        system_msg = next(m for m in messages if m["role"] == "system")
        # With enriched cmo.md present, body should appear; without it, generic fallback
        assert len(system_msg["content"]) > 20

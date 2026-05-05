"""Integration test: full graph end-to-end with mocked LLM."""
from unittest.mock import MagicMock
from core.meeting.meeting_graph import MeetingGraph
from core.meeting.debate_state import new_meeting_state


def test_meeting_runs_end_to_end_mocked():
    """Run full graph với mocked LLM (no API call, no checkpointer)."""

    def fake_complete(messages, model=None):
        sys = messages[0]["content"]
        if "Pro Advocate" in sys:
            return "GO. Cơ hội rõ ràng."
        if "Con Advocate" in sys:
            return "Cảnh báo rủi ro X."
        if "TĂNG TRƯỞNG" in sys:
            return "Triển khai mạnh."
        if "THẬN TRỌNG" in sys:
            return "Có gates rõ."
        if "CÂN BẰNG" in sys:
            return "Pilot 4 tuần."
        if "tổng hợp" in sys.lower() or "Synthesizer" in sys or "báo cáo quyết định" in sys.lower():
            return "## 📌 Tóm lại\nGO with revisions.\n\n## Chi tiết\n..."
        return "..."

    mock_llm = MagicMock()
    mock_llm.complete.side_effect = fake_complete

    def mock_perspectives(state):
        return {"perspectives": {
            "07-marketing": "Đề xuất triển khai",
            "03-finance": "Cẩn thận ngân sách",
        }}

    # Pass checkpointer=False to disable persistence (faster + no temp files)
    graph = MeetingGraph(
        llm=mock_llm,
        perspectives_collector=mock_perspectives,
        checkpointer=False,
    )

    state = new_meeting_state(
        brief="Test campaign",
        departments=["07-marketing", "03-finance"],
        max_rounds=1,
        task_id="test-001",
    )

    # When no checkpointer, no thread_id needed
    result = graph.build().invoke(state)

    assert result["perspectives"]["07-marketing"] == "Đề xuất triển khai"
    assert len(result["pro_con_debate"]["pro_history"]) >= 1
    assert len(result["pro_con_debate"]["con_history"]) >= 1
    assert len(result["perspective_debate"]["growth_history"]) >= 1
    assert result["final_report"] is not None
    assert "Tóm lại" in result["final_report"]

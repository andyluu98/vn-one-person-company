"""Test MCPSamplingProvider — mock MCP server context.

Real SDK API (mcp>=1.0.0):
- ServerSession.create_message is async
- Takes list[SamplingMessage] + ModelPreferences
- Returns CreateMessageResult with .content = TextContent

Provider adapts dict input → MCP types when SDK is installed.
Tests use MagicMock — sync return values, response shape varies.
"""
from unittest.mock import MagicMock

from core.llm.providers import LLMProvider, MCPSamplingProvider


def test_implements_llm_provider_protocol():
    """MCPSamplingProvider must satisfy LLMProvider Protocol."""
    server = MagicMock()
    p = MCPSamplingProvider(server)
    assert isinstance(p, LLMProvider)
    assert p.name == "mcp-sampling"


def test_complete_calls_server_create_message():
    server = MagicMock()
    fake_response = MagicMock()
    fake_response.content = [MagicMock(text="Tôi đồng ý.")]
    server.create_message.return_value = fake_response

    p = MCPSamplingProvider(server)
    result = p.complete([{"role": "user", "content": "test"}])

    assert "đồng ý" in result
    server.create_message.assert_called_once()


def test_complete_passes_model_hint():
    server = MagicMock()
    fake = MagicMock()
    fake.content = [MagicMock(text="ok")]
    server.create_message.return_value = fake

    p = MCPSamplingProvider(server)
    p.complete([{"role": "user", "content": "x"}], model="claude-opus-4-7")

    call = server.create_message.call_args
    # Provider builds ModelPreferences object (real SDK) or dict (fallback).
    # Either way, model name appears in serialized form.
    kwargs = call.kwargs if call.kwargs else {}
    prefs = kwargs.get("model_preferences")
    serialized = (
        prefs.model_dump_json() if hasattr(prefs, "model_dump_json") else str(prefs)
    )
    assert "claude-opus-4-7" in serialized


def test_default_model_is_sonnet_4_6():
    server = MagicMock()
    fake = MagicMock()
    fake.content = [MagicMock(text="ok")]
    server.create_message.return_value = fake

    p = MCPSamplingProvider(server)
    p.complete([{"role": "user", "content": "x"}])

    call = server.create_message.call_args
    kwargs = call.kwargs if call.kwargs else {}
    prefs = kwargs.get("model_preferences")
    serialized = (
        prefs.model_dump_json() if hasattr(prefs, "model_dump_json") else str(prefs)
    )
    assert "claude-sonnet-4-6" in serialized


def test_dict_response_shape():
    """Adapt: server might return dict instead of object."""
    server = MagicMock()
    server.create_message.return_value = {
        "content": [{"text": "dict shape response"}]
    }

    p = MCPSamplingProvider(server)
    result = p.complete([{"role": "user", "content": "x"}])
    assert "dict shape" in result


def test_system_role_extracted_to_system_prompt_kwarg():
    """MCP SamplingMessage.role chỉ user|assistant.

    Provider phải tách role='system' thành kwarg system_prompt riêng để
    SamplingMessage construction không fail validation.
    """
    server = MagicMock()
    fake = MagicMock()
    fake.content = [MagicMock(text="ok")]
    server.create_message.return_value = fake

    p = MCPSamplingProvider(server)
    p.complete([
        {"role": "system", "content": "Bạn là CFO VN."},
        {"role": "user", "content": "Hỏi về P&L"},
    ])

    call = server.create_message.call_args
    kwargs = call.kwargs if call.kwargs else {}

    assert kwargs.get("system_prompt") == "Bạn là CFO VN."

    msgs = kwargs.get("messages")
    assert len(msgs) == 1
    role = msgs[0].role if hasattr(msgs[0], "role") else msgs[0]["role"]
    assert role == "user"


def test_multiple_system_messages_joined(monkeypatch):
    server = MagicMock()
    fake = MagicMock()
    fake.content = [MagicMock(text="ok")]
    server.create_message.return_value = fake

    p = MCPSamplingProvider(server)
    p.complete([
        {"role": "system", "content": "Phần 1"},
        {"role": "system", "content": "Phần 2"},
        {"role": "user", "content": "Câu hỏi"},
    ])

    call = server.create_message.call_args
    kwargs = call.kwargs if call.kwargs else {}
    sp = kwargs.get("system_prompt", "")
    assert "Phần 1" in sp
    assert "Phần 2" in sp


def test_no_system_prompt_kwarg_when_only_user_messages():
    server = MagicMock()
    fake = MagicMock()
    fake.content = [MagicMock(text="ok")]
    server.create_message.return_value = fake

    p = MCPSamplingProvider(server)
    p.complete([{"role": "user", "content": "Hi"}])

    call = server.create_message.call_args
    kwargs = call.kwargs if call.kwargs else {}
    assert "system_prompt" not in kwargs

"""Multi-provider LLM abstraction (stub — full impl in Phase 4)."""
from __future__ import annotations
import asyncio
import inspect
import os
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    name: str

    def complete(self, messages: list[dict], model: str | None = None) -> str:
        ...


class ClaudeProvider:
    name = "claude"

    def __init__(self, api_key: str | None = None, default_model: str = "claude-sonnet-4-6"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.default_model = default_model

    def complete(self, messages: list[dict], model: str | None = None) -> str:
        from anthropic import Anthropic
        client = Anthropic(api_key=self.api_key)
        resp = client.messages.create(
            model=model or self.default_model,
            max_tokens=4096,
            messages=messages,
        )
        return resp.content[0].text


class MCPSamplingProvider:
    """LLM provider routing complete() qua MCP sampling protocol.

    Cho phép vn-business-os chạy bên trong Claude Desktop / Code session,
    dùng subscription thay vì API key.

    Spec: https://modelcontextprotocol.io/docs/concepts/sampling

    Yêu cầu: instance có method `create_message` (async or sync) — typically
    `mcp.server.session.ServerSession` truy cập qua `server.request_context.session`.

    Real MCP SDK API (mcp>=1.0.0):
        await session.create_message(
            messages=[SamplingMessage(role=..., content=TextContent(...))],
            max_tokens=4096,
            model_preferences=ModelPreferences(hints=[ModelHint(name=...)]),
        ) -> CreateMessageResult(content=TextContent(text=...), ...)
    """
    name = "mcp-sampling"

    def __init__(self, mcp_server: Any, default_model: str = "claude-sonnet-4-6"):
        """
        mcp_server: object exposing `create_message(...)` — real MCP `ServerSession`
                    or a duck-typed compatible object (mock-friendly for testing).
        """
        self.server = mcp_server
        self.default_model = default_model

    def complete(self, messages: list[dict], model: str | None = None) -> str:
        """Send sampling request via MCP, return response text.

        MCP SamplingMessage chỉ chấp nhận role 'user'/'assistant' — system message
        phải tách vào kwarg `system_prompt` riêng. Hàm này tự gộp & tách.
        """
        system_prompt, conv_messages = self._split_system(messages)
        sampling_messages, model_prefs = self._build_request_payload(
            conv_messages, model
        )

        kwargs: dict[str, Any] = {
            "messages": sampling_messages,
            "model_preferences": model_prefs,
            "max_tokens": 4096,
        }
        if system_prompt:
            kwargs["system_prompt"] = system_prompt

        result = self.server.create_message(**kwargs)

        # ServerSession.create_message is async — auto-await if needed.
        if inspect.isawaitable(result):
            result = self._run_sync(result)

        return self._extract_text(result)

    @staticmethod
    def _split_system(messages: list[dict]) -> tuple[str, list[dict]]:
        """Tách messages có role='system' thành system_prompt string + remaining.

        Nếu nhiều system messages → join bằng "\n\n". Đảm bảo conv_messages chỉ
        chứa user/assistant.
        """
        system_parts: list[str] = []
        rest: list[dict] = []
        for m in messages:
            if m.get("role") == "system":
                system_parts.append(str(m.get("content", "")))
            else:
                rest.append(m)
        return "\n\n".join(system_parts), rest

    def _build_request_payload(
        self, messages: list[dict], model: str | None
    ) -> tuple[Any, Any]:
        """Build request payload using MCP types when available, else raw dict.

        Returns (sampling_messages, model_preferences). Falls back to plain
        dicts/strings if mcp.types import fails — keeps unit tests w/ MagicMock
        servers working without the real SDK.
        """
        model_name = model or self.default_model
        try:
            from mcp.types import (
                ModelHint,
                ModelPreferences,
                SamplingMessage,
                TextContent,
            )
            sampling_msgs = [
                SamplingMessage(
                    role=m["role"],
                    content=TextContent(type="text", text=str(m["content"])),
                )
                for m in messages
            ]
            prefs = ModelPreferences(hints=[ModelHint(name=model_name)])
            return sampling_msgs, prefs
        except Exception:
            # Fallback used in tests with mock server.
            return messages, {"hints": [{"name": model_name}]}

    @staticmethod
    def _run_sync(coro: Any) -> Any:
        """Run coroutine to completion from sync context."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Inside an active loop — schedule and wait via new loop.
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, coro).result()
        except RuntimeError:
            pass
        return asyncio.run(coro)

    @staticmethod
    def _extract_text(result: Any) -> str:
        """Pull text from MCP CreateMessageResult or dict response shape."""
        content = result.content if hasattr(result, "content") else result["content"]

        # MCP SDK returns single TextContent (not list). Tests use list shape.
        if isinstance(content, list):
            first = content[0]
            return first.text if hasattr(first, "text") else first["text"]
        if hasattr(content, "text"):
            return content.text
        if isinstance(content, dict):
            return content["text"]
        return str(content)


def get_default_provider() -> LLMProvider:
    return ClaudeProvider()

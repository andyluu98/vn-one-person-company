"""Multi-provider LLM abstraction (stub — full impl in Phase 4)."""
from __future__ import annotations
import asyncio
import inspect
import os
from typing import Any, Protocol, runtime_checkable


async def _wrap_with_timeout(coro: Any, timeout: float) -> Any:
    """Wrap coroutine với asyncio timeout. Raises asyncio.TimeoutError nếu hết hạn."""
    return await asyncio.wait_for(coro, timeout=timeout)


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

    async def acomplete(self, messages: list[dict], model: str | None = None) -> str:
        import asyncio
        return await asyncio.to_thread(self.complete, messages, model)


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

    def __init__(
        self,
        mcp_server: Any,
        default_model: str = "claude-sonnet-4-6",
        max_retries: int = 3,
        timeout_seconds: float = 120.0,
        retry_initial_delay: float = 1.0,
    ):
        """
        mcp_server: object exposing `create_message(...)` — real MCP `ServerSession`
                    or a duck-typed compatible object (mock-friendly for testing).
        max_retries: retries cho transient errors (rate limit, timeout, network)
        timeout_seconds: hard timeout cho mỗi sampling call
        retry_initial_delay: backoff delay đầu tiên (sec); double mỗi retry
        """
        self.server = mcp_server
        self.default_model = default_model
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.retry_initial_delay = retry_initial_delay

    @staticmethod
    def _is_retryable(exc: BaseException) -> bool:
        """Xác định exception nào nên retry (rate limit / timeout / transient network).

        Nhận diện qua tên class hoặc message — cover Anthropic, MCP, asyncio, httpx.
        """
        name = type(exc).__name__.lower()
        msg = str(exc).lower()
        if "ratelimit" in name or "429" in msg or "rate limit" in msg:
            return True
        if "timeout" in name or "timeout" in msg or "timed out" in msg:
            return True
        if "connection" in name or "connection" in msg:
            return True
        if "overloaded" in msg or "503" in msg or "502" in msg:
            return True
        return False

    def complete(self, messages: list[dict], model: str | None = None) -> str:
        """Send sampling request via MCP với retry-with-backoff + timeout.

        MCP SamplingMessage chỉ chấp nhận role 'user'/'assistant' — system message
        tách vào kwarg `system_prompt`. Retry cho rate limit/timeout/network errors.
        """
        last_exc: BaseException | None = None
        delay = self.retry_initial_delay

        for attempt in range(self.max_retries + 1):
            try:
                return self._do_complete(messages, model)
            except Exception as e:  # noqa: BLE001
                last_exc = e
                if attempt >= self.max_retries or not self._is_retryable(e):
                    raise
                import time
                time.sleep(delay)
                delay *= 2  # exponential backoff

        # Unreachable — but Python static analysis happier with explicit raise
        raise last_exc or RuntimeError("MCPSamplingProvider.complete failed")

    def _do_complete(self, messages: list[dict], model: str | None) -> str:
        """1 attempt — không retry, có timeout."""
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

        # ServerSession.create_message is async — auto-await với timeout.
        if inspect.isawaitable(result):
            result = self._run_sync_with_timeout(result, self.timeout_seconds)

        return self._extract_text(result)

    async def acomplete(self, messages: list[dict], model: str | None = None) -> str:
        """Async version — dùng trong async MCP tool functions để tránh deadlock.

        FastMCP gọi sync tool trực tiếp trên event loop, nên complete() bị deadlock
        khi cố chạy create_message() trong ThreadPoolExecutor mới. acomplete() await
        create_message() trực tiếp trên event loop hiện tại — không có threading.
        """
        last_exc: BaseException | None = None
        delay = self.retry_initial_delay

        for attempt in range(self.max_retries + 1):
            try:
                return await self._do_acomplete(messages, model)
            except Exception as e:  # noqa: BLE001
                last_exc = e
                if attempt >= self.max_retries or not self._is_retryable(e):
                    raise
                import asyncio
                await asyncio.sleep(delay)
                delay *= 2

        raise last_exc or RuntimeError("MCPSamplingProvider.acomplete failed")

    async def _do_acomplete(self, messages: list[dict], model: str | None) -> str:
        """1 async attempt — await create_message() trực tiếp."""
        system_prompt, conv_messages = self._split_system(messages)
        sampling_messages, model_prefs = self._build_request_payload(conv_messages, model)

        kwargs: dict[str, Any] = {
            "messages": sampling_messages,
            "model_preferences": model_prefs,
            "max_tokens": 4096,
        }
        if system_prompt:
            kwargs["system_prompt"] = system_prompt

        result = self.server.create_message(**kwargs)
        if inspect.isawaitable(result):
            result = await result
        return self._extract_text(result)

    @staticmethod
    def _run_sync_with_timeout(coro: Any, timeout: float) -> Any:
        """Run coroutine sync với hard timeout."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, _wrap_with_timeout(coro, timeout))
                    return future.result()
        except RuntimeError:
            pass
        return asyncio.run(_wrap_with_timeout(coro, timeout))

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

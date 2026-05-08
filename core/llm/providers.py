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
        max_retries: int = 4,
        timeout_seconds: float = 120.0,
        retry_initial_delay: float = 1.0,
        rate_limit_initial_delay: float = 15.0,
    ):
        """
        mcp_server: object exposing `create_message(...)` — real MCP `ServerSession`
                    or a duck-typed compatible object (mock-friendly for testing).
        max_retries: retries cho transient errors (rate limit, timeout, network)
        timeout_seconds: hard timeout cho mỗi sampling call
        retry_initial_delay: backoff delay (sec) cho transient errors (timeout/network);
                             double mỗi retry
        rate_limit_initial_delay: backoff delay (sec) cho rate limit (429); double mỗi
                                  retry. Anthropic reset window ~60s → cần wait dài hơn.
                                  Default 15s → 30s → 60s → 120s = total ~225s đủ qua 1
                                  reset window.
        """
        self.server = mcp_server
        self.default_model = default_model
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.retry_initial_delay = retry_initial_delay
        self.rate_limit_initial_delay = rate_limit_initial_delay

    @staticmethod
    def _is_rate_limit(exc: BaseException) -> bool:
        """429 / rate limit specifically — cần backoff dài hơn other transients."""
        name = type(exc).__name__.lower()
        msg = str(exc).lower()
        return "ratelimit" in name or "429" in msg or "rate limit" in msg

    @classmethod
    def _is_retryable(cls, exc: BaseException) -> bool:
        """Xác định exception nào nên retry (rate limit / timeout / transient network).

        Nhận diện qua tên class hoặc message — cover Anthropic, MCP, asyncio, httpx.
        """
        if cls._is_rate_limit(exc):
            return True
        name = type(exc).__name__.lower()
        msg = str(exc).lower()
        if "timeout" in name or "timeout" in msg or "timed out" in msg:
            return True
        if "connection" in name or "connection" in msg:
            return True
        if "overloaded" in msg or "503" in msg or "502" in msg:
            return True
        return False

    def _initial_delay_for(self, exc: BaseException) -> float:
        """Pick initial backoff: longer for 429, shorter for other transients."""
        return self.rate_limit_initial_delay if self._is_rate_limit(exc) else self.retry_initial_delay

    def complete(self, messages: list[dict], model: str | None = None) -> str:
        """Send sampling request via MCP với retry-with-backoff + timeout.

        MCP SamplingMessage chỉ chấp nhận role 'user'/'assistant' — system message
        tách vào kwarg `system_prompt`. Retry cho rate limit/timeout/network errors.
        Backoff cho 429 dài hơn (15s base) so với transient (1s base) — Anthropic
        rate limit reset ~60s, cần wait đủ qua reset window.
        """
        last_exc: BaseException | None = None
        delay: float | None = None  # set theo error type ở exception handler

        for attempt in range(self.max_retries + 1):
            try:
                return self._do_complete(messages, model)
            except Exception as e:  # noqa: BLE001
                last_exc = e
                if attempt >= self.max_retries or not self._is_retryable(e):
                    raise
                if delay is None:
                    delay = self._initial_delay_for(e)
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
        Backoff cho 429 dài hơn (15s base) so với transient (1s base).
        """
        last_exc: BaseException | None = None
        delay: float | None = None

        for attempt in range(self.max_retries + 1):
            try:
                return await self._do_acomplete(messages, model)
            except Exception as e:  # noqa: BLE001
                last_exc = e
                if attempt >= self.max_retries or not self._is_retryable(e):
                    raise
                if delay is None:
                    delay = self._initial_delay_for(e)
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


class DeepSeekProvider:
    """LLM provider for DeepSeek API (OpenAI-compatible).

    Endpoint: https://api.deepseek.com (OpenAI-compat) hoặc /anthropic
    Models: deepseek-v4-pro (default, premium), deepseek-v4-flash (rẻ ~6x).
    Rẻ ~10x so với Claude, hợp DN nhỏ VN.
    """
    name = "deepseek"

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = "deepseek-v4-pro",
        base_url: str = "https://api.deepseek.com",
    ):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.default_model = default_model
        self.base_url = base_url

    def complete(self, messages: list[dict], model: str | None = None) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        # DeepSeek v4-pro mặc định thinking mode ON (chậm + tốn token).
        # Tắt qua extra_body để response nhanh hơn 3-5x cho meeting nodes.
        resp = client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            max_tokens=4096,
            extra_body={"thinking": {"type": "disabled"}},
        )
        return resp.choices[0].message.content or ""

    async def acomplete(self, messages: list[dict], model: str | None = None) -> str:
        return await asyncio.to_thread(self.complete, messages, model)


def get_default_provider() -> LLMProvider:
    """Pick provider based on env vars (priority: DeepSeek > Anthropic).

    DeepSeek ưu tiên vì rẻ ~10x — phù hợp DN nhỏ VN.
    Set DEEPSEEK_API_KEY trong vault/.env hoặc os.environ để dùng DeepSeek.
    Fallback Anthropic nếu chỉ có ANTHROPIC_API_KEY.
    """
    if os.getenv("DEEPSEEK_API_KEY"):
        return DeepSeekProvider()
    return ClaudeProvider()

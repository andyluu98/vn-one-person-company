"""Multi-provider LLM abstraction (stub — full impl in Phase 4)."""
from __future__ import annotations
import os
from typing import Protocol, runtime_checkable


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


def get_default_provider() -> ClaudeProvider:
    return ClaudeProvider()

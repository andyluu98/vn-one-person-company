"""Web search via Tavily API."""
from __future__ import annotations
import os
from pathlib import Path
from core.tools.base_tool import BaseTool, ToolResult
from core.tools.tool_cache import ToolCache


class WebSearch(BaseTool):
    name = "web_search"
    description = "Search web cho thông tin general."

    def __init__(self, api_key: str | None = None, cache_path: Path | None = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY", "")
        self.cache = ToolCache(
            cache_path or Path.home() / ".vn-business-os" / "tool_cache.db",
            ttl_seconds=self.cache_ttl_seconds,
        )

    def run(self, query: str, max_results: int = 5, **kwargs) -> ToolResult:
        cache_hit = self.cache.get(query, source=self.name)
        if cache_hit:
            return ToolResult(
                data=cache_hit, sources=cache_hit.get("urls", []),
                cached=True, notes="cache hit",
            )

        from tavily import TavilyClient
        client = TavilyClient(api_key=self.api_key)
        resp = client.search(query=query, max_results=max_results, include_answer=True)

        urls = [r["url"] for r in resp.get("results", [])]
        data = {
            "answer": resp.get("answer", ""),
            "results": resp.get("results", []),
            "urls": urls,
        }
        self.cache.set(query, data, source=self.name)

        return ToolResult(data=data, sources=urls, notes=f"max_results={max_results}")

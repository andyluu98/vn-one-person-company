"""Profile đối thủ public info."""
from __future__ import annotations
import os
from pathlib import Path
from core.tools.base_tool import BaseTool, ToolResult
from core.tools.tool_cache import ToolCache


class CompetitorResearch(BaseTool):
    name = "competitor_research"
    description = "Research đối thủ ngành VN — pricing, kênh, vị thế."

    def __init__(self, api_key: str | None = None, cache_path: Path | None = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY", "")
        self.cache = ToolCache(cache_path or Path.home() / ".vn-business-os" / "tool_cache.db")

    def run(self, query: str, country: str = "VN", **kwargs) -> ToolResult:
        full_query = f"{query} đối thủ cạnh tranh {country}"
        cache_hit = self.cache.get(full_query, source=self.name)
        if cache_hit:
            return ToolResult(data=cache_hit, sources=cache_hit.get("urls", []),
                              cached=True, notes="cache hit")

        from tavily import TavilyClient
        client = TavilyClient(api_key=self.api_key)
        resp = client.search(query=full_query, max_results=8, include_answer=True)
        urls = [r["url"] for r in resp.get("results", [])]
        data = {
            "answer": resp.get("answer", ""),
            "competitors_found": [r.get("title", "") for r in resp.get("results", [])],
            "urls": urls,
            "raw_results": resp.get("results", []),
        }
        self.cache.set(full_query, data, source=self.name)
        return ToolResult(data=data, sources=urls)

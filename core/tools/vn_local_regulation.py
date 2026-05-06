"""Quy định địa phương VN."""
from __future__ import annotations
import os
from pathlib import Path
from core.tools.base_tool import BaseTool, ToolResult
from core.tools.tool_cache import ToolCache


TRUSTED_LOCAL_DOMAINS = [
    "chinhphu.vn", "moj.gov.vn",
    "tphcm.gov.vn", "hanoi.gov.vn", "danang.gov.vn",
]


class VNLocalRegulation(BaseTool):
    name = "vn_local_regulation"
    description = "Quy định địa phương VN — Sở/UBND tỉnh."

    def __init__(self, api_key: str | None = None, cache_path: Path | None = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY", "")
        self.cache = ToolCache(cache_path or Path.home() / ".vn-business-os" / "tool_cache.db")

    def run(self, query: str, province: str = "", **kwargs) -> ToolResult:
        full_q = f"{query} {province}".strip()
        hit = self.cache.get(full_q, source=self.name)
        if hit:
            return ToolResult(data=hit, sources=hit.get("urls", []), cached=True)

        from tavily import TavilyClient
        client = TavilyClient(api_key=self.api_key)
        resp = client.search(
            query=full_q, max_results=6,
            include_domains=TRUSTED_LOCAL_DOMAINS, include_answer=True,
        )
        urls = [r["url"] for r in resp.get("results", [])]
        data = {"answer": resp.get("answer", ""), "results": resp.get("results", []), "urls": urls}
        self.cache.set(full_q, data, source=self.name)
        return ToolResult(data=data, sources=urls)

import time
from core.tools.tool_cache import ToolCache


def test_cache_get_set(tmp_path):
    cache = ToolCache(tmp_path / "cache.db", ttl_seconds=3600)
    cache.set("query1", {"data": "result"}, source="tavily")
    hit = cache.get("query1", source="tavily")
    assert hit is not None
    assert hit["data"] == "result"


def test_cache_miss_after_ttl(tmp_path):
    cache = ToolCache(tmp_path / "cache.db", ttl_seconds=1)
    cache.set("q2", {"x": 1}, source="s")
    time.sleep(2)
    assert cache.get("q2", source="s") is None

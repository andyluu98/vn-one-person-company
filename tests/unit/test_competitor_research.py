from unittest.mock import patch, MagicMock
from core.tools.competitor_research import CompetitorResearch


def test_extracts_competitors_from_query(tmp_path):
    fake = {"results": [
        {"url": "https://base.vn", "title": "Base.vn", "content": "..."},
        {"url": "https://misa.vn", "title": "Misa AMIS", "content": "..."},
    ], "answer": "Top SaaS quản lý SME VN..."}
    with patch("tavily.TavilyClient") as M:
        c = MagicMock(); c.search.return_value = fake; M.return_value = c
        tool = CompetitorResearch(api_key="x", cache_path=tmp_path / "c.db")
        r = tool.run("SaaS quản lý SME VN")

    assert len(r.sources) == 2
    assert "base.vn" in r.sources[0]

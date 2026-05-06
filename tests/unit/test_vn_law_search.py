from unittest.mock import patch, MagicMock
from core.tools.vn_law_search import VNLawSearch


def test_vn_law_search_filters_by_trusted_sites(tmp_path):
    fake_results = {
        "results": [
            {"url": "https://thuvienphapluat.vn/luat-quang-cao-2012", "title": "Luật QC 2012", "content": "..."},
            {"url": "https://luatvietnam.vn/123", "title": "Luật DN", "content": "..."},
        ],
        "answer": "Quy định QC...",
    }
    with patch("tavily.TavilyClient") as M:
        c = MagicMock(); c.search.return_value = fake_results
        M.return_value = c

        tool = VNLawSearch(api_key="fake", cache_path=tmp_path / "c.db")
        result = tool.run("luật quảng cáo SaaS B2B")

    assert all("thuvienphapluat" in u or "luatvietnam" in u or "vbpl" in u
               for u in result.sources)
    assert result.data["answer"]

from unittest.mock import patch, MagicMock
from core.tools.vn_local_regulation import VNLocalRegulation


def test_local_reg_searches_government_sites(tmp_path):
    fake = {"results": [{"url": "https://hanoi.gov.vn/x", "title": "T", "content": "..."}],
            "answer": "..."}
    with patch("tavily.TavilyClient") as M:
        c = MagicMock(); c.search.return_value = fake; M.return_value = c
        tool = VNLocalRegulation(api_key="x", cache_path=tmp_path / "c.db")
        r = tool.run("giấy phép kinh doanh", province="Hà Nội")
    assert "hanoi.gov.vn" in r.sources[0]

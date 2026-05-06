from unittest.mock import patch, MagicMock
from core.tools.web_search import WebSearch


def test_web_search_returns_sources(tmp_path):
    fake_results = {
        "results": [
            {"url": "https://example.com/a", "title": "A", "content": "..."},
            {"url": "https://example.com/b", "title": "B", "content": "..."},
        ],
        "answer": "summary text",
    }
    with patch("tavily.TavilyClient") as MockTavily:
        client = MagicMock()
        client.search.return_value = fake_results
        MockTavily.return_value = client

        ws = WebSearch(api_key="fake", cache_path=tmp_path / "c.db")
        result = ws.run("CAC SaaS B2B Vietnam 2026")

    assert len(result.sources) == 2
    assert "summary" in result.data.get("answer", "")


def test_web_search_uses_cache_on_second_call(tmp_path):
    fake_results = {"results": [{"url": "u", "title": "t", "content": "c"}], "answer": "ans"}
    with patch("tavily.TavilyClient") as MockTavily:
        client = MagicMock()
        client.search.return_value = fake_results
        MockTavily.return_value = client

        ws = WebSearch(api_key="fake", cache_path=tmp_path / "c.db")
        ws.run("query A")
        ws.run("query A")

        assert client.search.call_count == 1

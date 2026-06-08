"""web_search/web_fetch must not be ambient — only on search/current/URL intent (#2684).

Regression: they were in ALWAYS_AVAILABLE, so a trivial agent-mode prompt
('test', 'yo') surfaced/triggered SearXNG web search. They are now exposed
only via the web keyword hint or a URL in the prompt.
"""
from src.tool_index import ToolIndex, ALWAYS_AVAILABLE


def _tools_for(query: str) -> set:
    # Bypass the embedding-backed __init__; get_tools_for_query only needs
    # retrieve() + the class-level hint tables.
    idx = object.__new__(ToolIndex)
    idx.retrieve = lambda q, k=8: set()
    return idx.get_tools_for_query(query)


def test_web_tools_not_always_available():
    assert "web_search" not in ALWAYS_AVAILABLE
    assert "web_fetch" not in ALWAYS_AVAILABLE


def test_trivial_prompt_has_no_web_tools():
    for q in ("test", "yo", "hello", "thanks"):
        tools = _tools_for(q)
        assert "web_search" not in tools, q
        assert "web_fetch" not in tools, q


def test_search_intent_surfaces_web_search():
    for q in ("search for the latest python release",
              "what's the latest news on mars",
              "look up the current weather"):
        assert "web_search" in _tools_for(q), q


def test_url_in_prompt_surfaces_web_fetch():
    for q in ("check example.com", "open https://news.ycombinator.com", "read www.python.org"):
        tools = _tools_for(q)
        assert "web_fetch" in tools, q

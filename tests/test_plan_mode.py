"""Plan mode gating regression tests.

Plan mode restricts the agent to read-only/inspection tools so it can investigate
and propose a plan without mutating anything. These pin the security-relevant
contract:

- The read-only allowlist contains only inspection tools (no writes/sends/manage_*).
- `plan_mode_disabled_tools()` blocks every mutating tool and never blocks an
  allowlisted one.
- It fails CLOSED: if the tool-schema universe can't be loaded, it still blocks a
  known-mutating set rather than returning nothing (which would allow mutations).

Pure-function tests — no FastAPI app boot, no DB.
"""

from src.tool_security import (
    PLAN_MODE_READONLY_TOOLS,
    _PLAN_MODE_FALLBACK_BLOCK,
    plan_mode_disabled_tools,
)


def test_allowlist_has_no_obvious_mutating_tools():
    # Sanity: the read-only allowlist must not contain mutating/external tools.
    mutating_markers = ("write_", "send_", "manage_", "create_", "edit_", "delete_")
    for name in PLAN_MODE_READONLY_TOOLS:
        assert not name.startswith(mutating_markers), f"{name} should not be read-only"


def test_plan_mode_blocks_mutating_tools():
    disabled = plan_mode_disabled_tools()
    # A representative spread of mutating/external tools must be blocked.
    for name in (
        "write_file", "send_email", "reply_to_email", "manage_memory",
        "manage_settings", "create_document", "edit_document", "download_model",
        "generate_image", "trigger_research",
    ):
        assert name in disabled, f"{name} must be blocked in plan mode"


def test_plan_mode_allows_readonly_tools():
    disabled = plan_mode_disabled_tools()
    # Investigation tools (incl. intentionally-allowed bash/python) stay enabled.
    for name in ("read_file", "web_search", "web_fetch", "search_chats", "bash", "python"):
        assert name not in disabled, f"{name} should be usable in plan mode"


def test_disabled_never_intersects_allowlist():
    assert plan_mode_disabled_tools() & PLAN_MODE_READONLY_TOOLS == set()


def test_mcp_readonly_classification():
    from src.mcp_manager import mcp_tool_is_readonly as ro
    # Server-provided hints win over the name heuristic.
    assert ro({"name": "zap", "annotations": {"readOnlyHint": True}}) is True
    assert ro({"name": "list_things", "annotations": {"readOnlyHint": False}}) is False
    assert ro({"name": "get_x", "annotations": {"destructiveHint": True}}) is False
    # No hint → leading-verb heuristic, fail closed for ambiguous names.
    assert ro({"name": "list_files"}) is True
    assert ro({"name": "search_docs"}) is True
    assert ro({"name": "send_message"}) is False
    assert ro({"name": "frobnicate"}) is False


def test_fail_closed_fallback_blocks_mutations(monkeypatch):
    # If the schema universe can't load, we must still block (fail closed), not
    # return an empty set that would silently allow every mutating tool.
    import src.tool_security as ts

    def _boom():
        raise ImportError("simulated circular import failure")

    # Force the dynamic path to fail by making the lazy import explode.
    monkeypatch.setitem(
        __import__("sys").modules, "src.agent_tools", None
    )
    disabled = ts.plan_mode_disabled_tools()
    assert disabled, "plan mode must never fail open (empty disabled set)"
    assert "write_file" in disabled
    assert "send_email" in disabled
    assert disabled == set(_PLAN_MODE_FALLBACK_BLOCK)

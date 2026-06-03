"""Tests for AGENTS.md / CLAUDE.md project-instruction loading."""
import os
import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/test_proj_instr.db")

from src.agent_loop import _load_project_instructions, _PROJECT_INSTRUCTIONS_MAX


def test_none_when_no_file(tmp_path):
    assert _load_project_instructions(str(tmp_path)) == ""


def test_loads_agents_md(tmp_path):
    (tmp_path / "AGENTS.md").write_text("Prefer ruff. Don't touch /vendor.")
    out = _load_project_instructions(str(tmp_path))
    assert "PROJECT INSTRUCTIONS (from AGENTS.md)" in out
    assert "Prefer ruff" in out


def test_falls_back_to_claude_md(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("Use tabs. Run make test.")
    out = _load_project_instructions(str(tmp_path))
    assert "from CLAUDE.md" in out
    assert "Use tabs" in out


def test_agents_md_takes_precedence(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("claude content")
    (tmp_path / "AGENTS.md").write_text("agents content")
    out = _load_project_instructions(str(tmp_path))
    assert "from AGENTS.md" in out
    assert "agents content" in out
    assert "claude content" not in out  # first match only


def test_empty_file_skipped(tmp_path):
    (tmp_path / "AGENTS.md").write_text("   \n  ")
    (tmp_path / "CLAUDE.md").write_text("real content here")
    out = _load_project_instructions(str(tmp_path))
    # blank AGENTS.md is skipped, CLAUDE.md used
    assert "real content here" in out
    assert "from CLAUDE.md" in out


def test_oversize_truncated(tmp_path):
    (tmp_path / "AGENTS.md").write_text("x" * (_PROJECT_INSTRUCTIONS_MAX + 5000))
    out = _load_project_instructions(str(tmp_path))
    assert "[truncated]" in out
    assert len(out) < _PROJECT_INSTRUCTIONS_MAX + 500


def test_safe_on_bad_input():
    assert _load_project_instructions("") == ""
    assert _load_project_instructions("/no/such/dir") == ""


def test_root_only_no_parent_climb(tmp_path):
    # A file in a PARENT must not be picked up from a child workspace.
    (tmp_path / "AGENTS.md").write_text("parent instructions")
    child = tmp_path / "sub"
    child.mkdir()
    assert _load_project_instructions(str(child)) == ""

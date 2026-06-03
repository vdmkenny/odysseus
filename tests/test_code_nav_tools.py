"""Tests for the code-navigation tools (grep, glob, ls) + read_file line range."""
import os
import asyncio
import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/test_code_nav.db")

from src.tool_execution import _direct_fallback


def _run(tool, content, workspace=None):
    return asyncio.run(_direct_fallback(tool, content, workspace=workspace))


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "a.py").write_text("import os\n# needle here\nprint('x')\n")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.txt").write_text("nothing\nNEEDLE upper\n")
    # junk that must be skipped
    g = tmp_path / ".git"
    g.mkdir()
    (g / "config").write_text("needle in git\n")
    nm = tmp_path / "node_modules"
    nm.mkdir()
    (nm / "dep.py").write_text("needle in dep\n")
    return tmp_path


# ── grep ────────────────────────────────────────────────────────────────────

def test_grep_finds_match(repo):
    r = _run("grep", '{"pattern": "needle"}', workspace=str(repo))
    assert r["exit_code"] == 0
    assert "a.py:2:" in r["output"]


def test_grep_skips_junk_dirs(repo):
    r = _run("grep", '{"pattern": "needle"}', workspace=str(repo))
    # .git/ and node_modules/ must not appear (rg honours .gitignore-ish; python
    # fallback uses the skip set)
    assert ".git/config" not in r["output"]
    assert "node_modules" not in r["output"]


def test_grep_ignore_case(repo):
    r = _run("grep", '{"pattern": "needle", "ignore_case": true}', workspace=str(repo))
    assert "b.txt:2:" in r["output"]  # "NEEDLE upper"


def test_grep_glob_filter(repo):
    r = _run("grep", '{"pattern": "needle", "ignore_case": true, "glob": "*.py"}', workspace=str(repo))
    assert "a.py" in r["output"]
    assert "b.txt" not in r["output"]


def test_grep_no_match(repo):
    r = _run("grep", '{"pattern": "zzzznotfound"}', workspace=str(repo))
    assert r["exit_code"] == 0
    assert "No matches" in r["output"]


def test_grep_requires_pattern(repo):
    r = _run("grep", '{}', workspace=str(repo))
    assert r["exit_code"] == 1
    assert "pattern is required" in r["error"]


def test_grep_path_outside_workspace_rejected(repo):
    r = _run("grep", '{"pattern": "x", "path": "/etc"}', workspace=str(repo))
    assert r["exit_code"] == 1
    assert "outside the workspace" in r["error"]


def test_grep_python_fallback_when_no_rg(repo, monkeypatch):
    # Force the no-ripgrep path: which() returns None.
    import shutil
    monkeypatch.setattr(shutil, "which", lambda name: None)
    r = _run("grep", '{"pattern": "needle"}', workspace=str(repo))
    assert r["exit_code"] == 0
    assert "a.py:2:" in r["output"]
    assert "node_modules" not in r["output"]  # fallback skip set
    assert ".git/config" not in r["output"]


# ── glob ────────────────────────────────────────────────────────────────────

def test_glob_py(repo):
    r = _run("glob", '{"pattern": "*.py"}', workspace=str(repo))
    assert r["exit_code"] == 0
    assert "a.py" in r["output"]


def test_glob_recursive_skips_junk(repo):
    r = _run("glob", '{"pattern": "**/*.py"}', workspace=str(repo))
    assert "a.py" in r["output"]
    assert "node_modules" not in r["output"]  # junk dir filtered


def test_glob_requires_pattern(repo):
    r = _run("glob", '{}', workspace=str(repo))
    assert r["exit_code"] == 1


# ── ls ──────────────────────────────────────────────────────────────────────

def test_ls_lists_entries(repo):
    r = _run("ls", '{}', workspace=str(repo))
    assert r["exit_code"] == 0
    assert "a.py" in r["output"]
    assert "sub/" in r["output"]          # dir marked with trailing slash
    assert ".git" not in r["output"]      # hidden skipped


def test_ls_path_outside_rejected(repo):
    r = _run("ls", '{"path": "/etc"}', workspace=str(repo))
    assert r["exit_code"] == 1
    assert "outside the workspace" in r["error"]


# ── read_file line range ─────────────────────────────────────────────────────

def test_read_file_offset_limit(repo):
    f = repo / "lines.txt"
    f.write_text("\n".join(f"line{i}" for i in range(1, 11)) + "\n")
    r = _run("read_file", '{"path": "lines.txt", "offset": 3, "limit": 2}', workspace=str(repo))
    assert r["exit_code"] == 0
    assert r["output"] == "line3\nline4\n"


def test_read_file_plain_path_backcompat(repo):
    r = _run("read_file", "a.py", workspace=str(repo))
    assert r["exit_code"] == 0
    assert "needle" in r["output"]

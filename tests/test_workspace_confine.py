"""Workspace confinement: file tools are hard-bounded to the workspace folder
(layered on upstream's sensitive-path policy); bash runs with cwd there."""
import os
import tempfile

import pytest

from src.tool_execution import _resolve_tool_path_in_workspace, _direct_fallback


def test_workspace_resolver_confines():
    ws = tempfile.mkdtemp()
    open(os.path.join(ws, "a.txt"), "w").write("x")
    real = os.path.realpath(os.path.join(ws, "a.txt"))
    # relative path resolves under the workspace
    assert _resolve_tool_path_in_workspace(ws, "a.txt") == real
    # absolute path inside the workspace is allowed
    assert _resolve_tool_path_in_workspace(ws, os.path.join(ws, "a.txt")) == real
    # absolute path outside is rejected
    with pytest.raises(ValueError):
        _resolve_tool_path_in_workspace(ws, "/etc/hosts")
    # parent-escape is rejected
    with pytest.raises(ValueError):
        _resolve_tool_path_in_workspace(ws, "../../etc/passwd")


def test_workspace_resolver_blocks_sensitive():
    """Upstream's sensitive-file deny list still applies inside the workspace."""
    ws = tempfile.mkdtemp()
    os.makedirs(os.path.join(ws, ".ssh"), exist_ok=True)
    with pytest.raises(ValueError):
        _resolve_tool_path_in_workspace(ws, ".ssh/authorized_keys")


@pytest.mark.asyncio
async def test_read_write_confined_in_workspace():
    ws = tempfile.mkdtemp()
    # Write inside the workspace (relative path) succeeds.
    res = await _direct_fallback("write_file", "note.txt\nhello", workspace=ws)
    assert res["exit_code"] == 0
    assert os.path.isfile(os.path.join(ws, "note.txt"))
    # Read it back.
    res = await _direct_fallback("read_file", "note.txt", workspace=ws)
    assert res["exit_code"] == 0 and res["output"] == "hello"
    # Reading outside the workspace is rejected.
    res = await _direct_fallback("read_file", "/etc/hosts", workspace=ws)
    assert res["exit_code"] == 1 and "outside the workspace" in res["error"]
    # Writing outside is rejected (file must not be created).
    res = await _direct_fallback("write_file", "/etc/_ws_escape.txt\nx", workspace=ws)
    assert res["exit_code"] == 1 and "outside the workspace" in res["error"]


def test_browse_is_admin_gated(monkeypatch):
    """The directory-browser endpoint must refuse non-admin callers."""
    from fastapi import HTTPException
    import routes.workspace_routes as wr

    router = wr.setup_workspace_routes()
    browse = next(r.endpoint for r in router.routes if r.path == "/api/workspace/browse")

    monkeypatch.setattr(wr, "get_current_user", lambda req: "bob")
    monkeypatch.setattr(wr, "owner_is_admin_or_single_user", lambda owner: False)
    with pytest.raises(HTTPException) as ei:
        browse(request=object(), path="/")
    assert ei.value.status_code == 403

    # Admin / single-user is allowed.
    monkeypatch.setattr(wr, "owner_is_admin_or_single_user", lambda owner: True)
    out = browse(request=object(), path=os.path.expanduser("~"))
    assert "dirs" in out and "path" in out
    assert all("name" in d and "path" in d for d in out["dirs"])


@pytest.mark.asyncio
async def test_bash_runs_with_workspace_cwd():
    ws = tempfile.mkdtemp()
    res = await _direct_fallback("bash", "pwd", workspace=ws)
    assert res["exit_code"] == 0
    assert os.path.realpath(res["output"].strip()) == os.path.realpath(ws)

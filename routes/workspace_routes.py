"""Workspace API — browse server directories to pick a tool workspace folder."""
import os
import shutil
import subprocess
from fastapi import APIRouter, Request, HTTPException, Query

from src.auth_helpers import get_current_user
from src.tool_security import owner_is_admin_or_single_user


def setup_workspace_routes():
    router = APIRouter(prefix="/api/workspace", tags=["workspace"])

    @router.get("/browse")
    def browse(request: Request, path: str = Query(default="")):
        """List subdirectories of `path` (default: home) so the UI can navigate
        the server filesystem and pick a workspace folder. Directories only.

        ADMIN-ONLY: this enumerates the server filesystem, so it is gated the
        same way the file/shell tools are (read_file/write_file/bash are in
        NON_ADMIN_BLOCKED_TOOLS). A non-admin who can't use those tools must not
        be able to map the host's directory tree either.
        """
        owner = get_current_user(request)
        if not owner_is_admin_or_single_user(owner):
            raise HTTPException(status_code=403, detail="Workspace browsing is admin-only")

        # Resolve symlinks so the reported path is canonical and the UI navigates
        # real directories (defends against symlink games in displayed paths).
        target = os.path.realpath(os.path.expanduser(path.strip() or "~"))
        if not os.path.isdir(target):
            target = os.path.realpath(os.path.expanduser("~"))

        dirs = []
        try:
            with os.scandir(target) as it:
                for entry in it:
                    try:
                        # Don't follow symlinks when classifying — a symlinked
                        # dir is skipped rather than letting the browser wander
                        # off via a link. Hidden entries are omitted.
                        if entry.is_dir(follow_symlinks=False) and not entry.name.startswith("."):
                            # Build the child path server-side with os.path.join
                            # so it's correct on Windows (backslashes) and Linux.
                            dirs.append({"name": entry.name, "path": os.path.join(target, entry.name)})
                    except OSError:
                        continue
        except (PermissionError, OSError):
            dirs = []

        parent = os.path.dirname(target)
        return {
            "path": target,
            "parent": parent if parent and parent != target else None,
            "dirs": sorted(dirs, key=lambda d: d["name"].lower()),
        }

    @router.get("/git-branch")
    def git_branch(request: Request, path: str = Query(default="")):
        """Return the checked-out git branch for `path` (the active workspace) or,
        when no path is given, the project data dir. Used by the chat input to
        show the current branch.

        ADMIN-ONLY (same as /browse — it reads the server filesystem). Silently
        reports ``{repo: false}`` when git isn't installed or the directory isn't
        a git repo, so the UI can simply hide the indicator.
        """
        owner = get_current_user(request)
        if not owner_is_admin_or_single_user(owner):
            raise HTTPException(status_code=403, detail="Workspace info is admin-only")

        # Resolve target: the workspace path if supplied, else the data dir.
        raw = (path or "").strip()
        if raw:
            target = os.path.realpath(os.path.expanduser(raw))
        else:
            from src.constants import DATA_DIR
            target = os.path.realpath(DATA_DIR)
        if not os.path.isdir(target):
            return {"repo": False}

        # No git tooling → silently report "not a repo" (feature is best-effort).
        git = shutil.which("git")
        if not git:
            return {"repo": False}

        def _git(*args):
            return subprocess.run(
                [git, "-C", target, *args],
                capture_output=True, text=True, timeout=3,
            )

        try:
            # Only treat `target` as a repo when it IS the repo's top level —
            # not when it merely sits inside one (e.g. the data dir living under
            # the app's own checkout). Don't climb to an ancestor repo.
            top = _git("rev-parse", "--show-toplevel")
            if top.returncode != 0:
                return {"repo": False}  # not a git repo
            if os.path.realpath((top.stdout or "").strip()) != target:
                return {"repo": False}  # repo is an ancestor, not this dir
            r = _git("rev-parse", "--abbrev-ref", "HEAD")
            if r.returncode != 0:
                return {"repo": False}  # other git error
            branch = (r.stdout or "").strip()
            if branch == "HEAD":
                # Detached HEAD — report the short commit instead.
                rs = _git("rev-parse", "--short", "HEAD")
                sha = (rs.stdout or "").strip()
                return {"repo": True, "branch": sha or "HEAD", "detached": True}
            if not branch:
                return {"repo": False}
            return {"repo": True, "branch": branch, "detached": False}
        except (subprocess.TimeoutExpired, OSError):
            return {"repo": False}

    return router

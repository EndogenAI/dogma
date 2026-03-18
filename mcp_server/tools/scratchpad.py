"""mcp_server/tools/scratchpad.py — MCP tool implementations for session management.

Tools:
    prune_scratchpad — Initialise or inspect today's session scratchpad file.

Inputs:
    prune_scratchpad:
        branch   : str  — branch slug for the scratchpad folder (default: current git branch)
        dry_run  : bool — if True, only check status without writing (default: False)

Outputs:
    prune_scratchpad: {
        "ok":        bool,
        "file_path": str | None,   # path to today's <branch>/<date>.md file
        "exists":    bool,         # whether the file already existed before this call
        "lines":     int | None,   # current line count (None if dry_run and not yet created)
        "errors":    list[str],
    }

Usage:
    result = prune_scratchpad()                       # init today's scratchpad
    result = prune_scratchpad(branch="feat/my-feat")  # explicit branch slug
    result = prune_scratchpad(dry_run=True)           # status check only
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from mcp_server._security import REPO_ROOT, validate_repo_path


def _current_branch() -> str:
    """Return the current git branch slug (slashes replaced by hyphens)."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=10,
    )
    if result.returncode != 0:
        return "unknown"
    branch = result.stdout.strip()
    return re.sub(r"[^a-zA-Z0-9._-]", "-", branch)


def prune_scratchpad(branch: str = "", dry_run: bool = False) -> dict:
    """Initialise or inspect the session scratchpad for the current branch.

    Calls prune_scratchpad.py --init (or --check-only for dry_run) to manage
    the per-branch per-day Markdown scratchpad under .tmp/<branch>/<date>.md.

    Args:
        branch: Branch slug for the scratchpad folder. If empty, auto-detects
                the current git branch.
        dry_run: If True, passes --check-only and does not create or modify files.

    Returns:
        {"ok": bool, "file_path": str | None, "exists": bool, "lines": int | None,
         "errors": list[str]}
    """
    slug = branch.strip() or _current_branch()
    # Sanitise the slug to prevent path traversal
    slug = re.sub(r"\.\./|^\./", "", slug)  # strip ../ and ./

    script = str(REPO_ROOT / "scripts" / "prune_scratchpad.py")
    args = [sys.executable, script]

    # If caller specifies a branch, force prune_scratchpad.py to target that
    # branch's per-day file via --file so branch selection is explicit.
    if branch.strip():
        file_path = Path(REPO_ROOT) / ".tmp" / slug / f"{date.today().isoformat()}.md"
        try:
            validate_repo_path(str(file_path))
        except ValueError as exc:
            return {"ok": False, "file_path": None, "exists": False, "lines": None, "errors": [str(exc)]}
        args.extend(["--file", str(file_path)])

    if dry_run:
        args.append("--check-only")
    else:
        args.append("--init")

    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=30,
    )

    file_path: str | None = None
    exists = False
    lines: int | None = None

    for line in (result.stdout + result.stderr).splitlines():
        # prune_scratchpad.py outputs the scratchpad path on success
        if ".tmp/" in line and ".md" in line:
            candidate = re.search(r"\.tmp/[^\s]+\.md", line)
            if candidate:
                file_path = candidate.group(0)
        if "already exists" in line.lower() or "initialized" in line.lower() or "found" in line.lower():
            exists = "already exists" in line.lower() or "found" in line.lower()
        if m := re.search(r"(\d+)\s+lines?", line):
            lines = int(m.group(1))

    errors = []
    if result.returncode != 0:
        errors = [ln for ln in (result.stdout + result.stderr).splitlines() if ln.strip()]

    return {
        "ok": result.returncode == 0,
        "file_path": file_path,
        "exists": exists,
        "lines": lines,
        "errors": errors,
    }

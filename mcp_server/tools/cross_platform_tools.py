"""mcp_server/tools/cross_platform_tools.py — MCP tool implementations for cross-platform path handling.

Tools:
    normalize_path    — Normalize a path string cross-platform via pathlib, expanding env-var tokens.
    resolve_env_path  — Read an env-var expected to contain a path, normalize it, return empty string if unset.

Inputs:
    normalize_path:
        path_str : str — a raw path string, may contain env-var tokens like $HOME, $PWD

    resolve_env_path:
        key     : str — environment variable name
        default : str — value to return when the variable is unset (default: "")

Outputs:
    normalize_path:   str — normalized, absolute-if-possible path string
    resolve_env_path: str — normalized path, or default if env-var is not set

Usage:
    result = normalize_path("$HOME/projects/dogma")
    result = resolve_env_path("REPO_ROOT", default="/tmp")
"""

from __future__ import annotations

import os
from typing import Any

__all__ = [
    "normalize_path",
    "resolve_env_path",
]


def normalize_path(path_str: str) -> str:
    """Normalize a cross-platform path string, expanding environment-variable tokens.

    Expands tokens such as $HOME, $PWD, and %USERPROFILE% via os.path.expandvars,
    then normalizes separators and resolves redundant components (.. / .) using
    pathlib.Path.

    Args:
        path_str: A raw path string, potentially containing env-var tokens.

    Returns:
        A normalized path string. Separators are normalized for the current OS.
        Symlinks are NOT resolved — use pathlib.Path.resolve() if needed.
    """
    expanded = os.path.expandvars(path_str)
    # Use abspath + normpath to match suggestion and OS expectations
    return os.path.abspath(os.path.normpath(expanded))


def resolve_env_path(key: str, default: str = "") -> dict[str, Any]:
    """Read an environment variable expected to hold a path and normalize it.

    If the variable is set and non-empty, expands and normalizes its value via
    normalize_path(). If the variable is unset or empty, returns `default`.

    Args:
        key: Environment variable name (e.g. "REPO_ROOT", "HOME").
        default: Value to return when the variable is not set or is empty.

    Returns:
        Dict following {ok, errors, result} contract.
    """
    raw = os.environ.get(key, "")
    if not raw:
        return {"ok": True, "errors": [], "result": default}
    try:
        norm = normalize_path(raw)
        return {"ok": True, "errors": [], "result": norm}
    except Exception as exc:
        return {"ok": False, "errors": [str(exc)], "result": ""}

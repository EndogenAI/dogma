"""tests/test_mcp_cross_platform.py — Tests for MCP cross-platform standardization (#336)

Tests verify that MCP server tools use cross-platform path handling correctly:
1. REPO_ROOT calculation is cross-platform
2. normalize_path handles env vars correctly
3. resolve_env_path returns structured output
4. Integration: MCP tools work on both Unix and Windows paths
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from mcp_server._security import REPO_ROOT, validate_repo_path
from mcp_server.tools.cross_platform_tools import normalize_path, resolve_env_path


def test_repo_root_is_absolute():
    """Test that REPO_ROOT is an absolute path regardless of platform."""
    assert REPO_ROOT.is_absolute()
    assert (REPO_ROOT / "mcp_server").exists()


def test_normalize_path_expands_env_vars():
    """Test normalize_path expands $HOME and other env vars."""
    with patch.dict(os.environ, {"TEST_VAR": "/tmp/test"}):
        result = normalize_path("$TEST_VAR/subdir")
        assert "/tmp/test" in result
        assert "subdir" in result
        assert "$TEST_VAR" not in result


def test_normalize_path_handles_relative_paths():
    """Test normalize_path converts relative paths to absolute."""
    result = normalize_path("./scripts")
    assert os.path.isabs(result)
    assert "scripts" in result


@pytest.mark.io
def test_resolve_env_path_returns_structured():
    """Test resolve_env_path returns dict with ok/errors/result."""
    with patch.dict(os.environ, {"TEST_PATH": "/tmp/test"}):
        result = resolve_env_path("TEST_PATH")

        assert isinstance(result, dict)
        assert "ok" in result
        assert "errors" in result
        assert "result" in result
        assert result["ok"] is True
        assert result["errors"] == []
        assert "/tmp/test" in result["result"]


def test_resolve_env_path_returns_default_when_unset():
    """Test resolve_env_path returns default when env var is not set."""
    result = resolve_env_path("NONEXISTENT_VAR", default="/fallback")

    assert result["ok"] is True
    assert result["result"] == "/fallback"


def test_validate_repo_path_accepts_valid_paths():
    """Test validate_repo_path allows paths within REPO_ROOT."""
    valid_path = str(REPO_ROOT / "scripts" / "test.py")
    resolved = validate_repo_path(valid_path)

    assert resolved.is_relative_to(REPO_ROOT)
    assert "scripts" in str(resolved)


def test_validate_repo_path_rejects_traversal():
    """Test validate_repo_path blocks path traversal attempts."""
    with pytest.raises(ValueError, match="resolves outside the repository root"):
        validate_repo_path("../../etc/passwd")


@pytest.mark.integration
def test_mcp_tools_use_cross_platform_paths():
    """Integration test: verify MCP tools handle paths cross-platform."""
    from mcp_server.tools.validation import validate_agent_file

    # Use a relative path that should resolve cross-platform
    result = validate_agent_file(".github/agents/executive-orchestrator.agent.md")

    # Should not crash with path errors; may fail validation but structure correct
    assert "ok" in result
    assert "errors" in result
    assert isinstance(result["errors"], list)

"""tests/test_mcp_server.py — Tests for the dogma governance MCP server.

Tests validate each tool function directly (they are plain Python callables —
the MCP layer is just a thin decorator over them). subprocess.run is mocked
throughout for fast, isolated unit tests.

Coverage groups:
    - _security.py: validate_repo_path, validate_url
    - tools/validation.py: validate_agent_file, validate_synthesis, check_substrate
    - tools/scaffolding.py: scaffold_agent, scaffold_workplan
    - tools/research.py: run_research_scout, query_docs
    - tools/scratchpad.py: prune_scratchpad
    - dogma_server.py: importable + mcp instance exists with 8 tools registered
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent


def _completed(returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    """Build a fake CompletedProcess for mocking."""
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


# ---------------------------------------------------------------------------
# Security helpers
# ---------------------------------------------------------------------------


class TestValidateRepoPath:
    def test_absolute_path_within_repo_passes(self):
        from mcp_server._security import validate_repo_path

        result = validate_repo_path(str(REPO_ROOT / "AGENTS.md"))
        assert result == (REPO_ROOT / "AGENTS.md").resolve()

    def test_relative_path_within_repo_passes(self, monkeypatch, tmp_path):
        # Create a temp file that is genuinely inside a sub-directory of the package
        from mcp_server._security import REPO_ROOT as SERVER_ROOT
        from mcp_server._security import validate_repo_path

        target = SERVER_ROOT / "mcp_server" / "_security.py"
        result = validate_repo_path(str(target))
        assert result.is_relative_to(SERVER_ROOT)

    def test_path_traversal_raises(self):
        from mcp_server._security import validate_repo_path

        with pytest.raises(ValueError, match="outside the repository root"):
            validate_repo_path("/etc/passwd")

    def test_dotdot_traversal_raises(self):
        from mcp_server._security import validate_repo_path

        with pytest.raises(ValueError, match="outside the repository root"):
            validate_repo_path(str(REPO_ROOT / ".." / ".." / "etc" / "passwd"))


class TestValidateUrl:
    def test_https_public_url_passes(self, monkeypatch):
        import socket

        from mcp_server._security import validate_url

        # Mock DNS resolution so the test is hermetic and not network-dependent.
        monkeypatch.setattr(
            socket,
            "getaddrinfo",
            lambda *a, **kw: [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 0))],
        )
        result = validate_url("https://www.example.com/page")
        assert result == "https://www.example.com/page"

    def test_http_rejected(self):
        from mcp_server._security import validate_url

        with pytest.raises(ValueError, match="scheme"):
            validate_url("http://www.example.com/page")

    def test_ftp_rejected(self):
        from mcp_server._security import validate_url

        with pytest.raises(ValueError, match="scheme"):
            validate_url("ftp://files.example.com/data")

    def test_private_ip_rejected(self):
        from mcp_server._security import validate_url

        with pytest.raises(ValueError, match="private/internal IP"):
            validate_url("https://192.168.1.1/admin")

    def test_loopback_rejected(self):
        from mcp_server._security import validate_url

        with pytest.raises(ValueError, match="private/internal IP"):
            validate_url("https://127.0.0.1/secret")

    def test_fe80_ipv6_link_local_rejected(self):
        from mcp_server._security import validate_url

        with pytest.raises(ValueError, match="link-local"):
            validate_url("https://[fe80::1%eth0]/page")

    def test_no_hostname_rejected(self):
        from mcp_server._security import validate_url

        with pytest.raises(ValueError, match="hostname"):
            validate_url("https:///path/to/resource")


# ---------------------------------------------------------------------------
# Validation tools
# ---------------------------------------------------------------------------


class TestValidateAgentFile:
    def test_valid_file_returns_ok_true(self, tmp_path, mocker):
        from mcp_server.tools.validation import validate_agent_file

        dummy = tmp_path / "test.agent.md"
        dummy.write_text("# dummy")
        mocker.patch("mcp_server.tools.validation._run_script", return_value=_completed(0, "All good"))
        mocker.patch("mcp_server.tools.validation.validate_repo_path", return_value=dummy)
        result = validate_agent_file(str(dummy))
        assert result["ok"] is True
        assert "file_path" in result

    def test_invalid_file_returns_ok_false_with_errors(self, tmp_path, mocker):
        from mcp_server.tools.validation import validate_agent_file

        dummy = tmp_path / "bad.agent.md"
        dummy.write_text("malformed")
        mocker.patch(
            "mcp_server.tools.validation._run_script",
            return_value=_completed(1, "", "ERROR: missing frontmatter"),
        )
        mocker.patch("mcp_server.tools.validation.validate_repo_path", return_value=dummy)
        result = validate_agent_file(str(dummy))
        assert result["ok"] is False
        assert any("ERROR" in e for e in result["errors"])

    def test_path_traversal_caught(self):
        from mcp_server.tools.validation import validate_agent_file

        result = validate_agent_file("/etc/passwd")
        assert result["ok"] is False
        assert any("outside the repository root" in e for e in result["errors"])


class TestValidateSynthesis:
    def test_valid_synthesis_returns_ok_true(self, tmp_path, mocker):
        from mcp_server.tools.validation import validate_synthesis

        dummy = tmp_path / "doc.md"
        dummy.write_text("content")
        mocker.patch("mcp_server.tools.validation._run_script", return_value=_completed(0, "OK"))
        mocker.patch("mcp_server.tools.validation.validate_repo_path", return_value=dummy)
        result = validate_synthesis(str(dummy))
        assert result["ok"] is True

    def test_invalid_synthesis_returns_ok_false(self, tmp_path, mocker):
        from mcp_server.tools.validation import validate_synthesis

        dummy = tmp_path / "doc.md"
        dummy.write_text("stub")
        mocker.patch(
            "mcp_server.tools.validation._run_script",
            return_value=_completed(1, "FAIL: missing Executive Summary"),
        )
        mocker.patch("mcp_server.tools.validation.validate_repo_path", return_value=dummy)
        result = validate_synthesis(str(dummy))
        assert result["ok"] is False

    def test_path_traversal_caught(self):
        from mcp_server.tools.validation import validate_synthesis

        result = validate_synthesis("/etc/passwd")
        assert result["ok"] is False
        assert any("outside the repository root" in e for e in result["errors"])

    def test_min_lines_passed_to_script(self, tmp_path, mocker):
        from mcp_server.tools.validation import validate_synthesis

        dummy = tmp_path / "doc.md"
        dummy.write_text("x")
        captured_args: list = []

        def fake_run(args):
            captured_args.extend(args)
            return _completed(0)

        mocker.patch("mcp_server.tools.validation._run_script", side_effect=fake_run)
        mocker.patch("mcp_server.tools.validation.validate_repo_path", return_value=dummy)
        validate_synthesis(str(dummy), min_lines=120)

        assert "--min-lines" in captured_args
        assert "120" in captured_args


class TestCheckSubstrate:
    def test_healthy_substrate_returns_ok_true(self, mocker):
        from mcp_server.tools.validation import check_substrate

        mocker.patch("mcp_server.tools.validation._run_script", return_value=_completed(0, "All checks passed"))
        result = check_substrate()
        assert result["ok"] is True
        assert "report" in result

    def test_unhealthy_substrate_returns_ok_false(self, mocker):
        from mcp_server.tools.validation import check_substrate

        mocker.patch(
            "mcp_server.tools.validation._run_script",
            return_value=_completed(1, "BLOCK: missing MANIFESTO.md section"),
        )
        result = check_substrate()
        assert result["ok"] is False
        assert any("BLOCK" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# Scaffolding tools
# ---------------------------------------------------------------------------


class TestScaffoldAgent:
    def test_valid_scaffold_returns_output_path(self, mocker):
        from mcp_server.tools.scaffolding import scaffold_agent

        mocker.patch(
            "mcp_server.tools.scaffolding._run_script",
            return_value=_completed(0, "Created: .github/agents/test-research.agent.md"),
        )
        result = scaffold_agent("Test Research", "A test agent for research tasks")
        assert result["ok"] is True
        assert result["output_path"] is not None
        assert "agent.md" in result["output_path"]

    def test_description_too_long_rejected(self):
        from mcp_server.tools.scaffolding import scaffold_agent

        result = scaffold_agent("Agent", "x" * 201)
        assert result["ok"] is False
        assert any("200" in e for e in result["errors"])

    def test_invalid_posture_rejected(self):
        from mcp_server.tools.scaffolding import scaffold_agent

        result = scaffold_agent("Agent", "A valid description", posture="superadmin")
        assert result["ok"] is False
        assert any("posture" in e for e in result["errors"])

    def test_script_failure_returns_ok_false(self, mocker):
        from mcp_server.tools.scaffolding import scaffold_agent

        mocker.patch(
            "mcp_server.tools.scaffolding._run_script", return_value=_completed(1, "", "ERROR: name already exists")
        )
        result = scaffold_agent("Existing Agent", "Valid description", posture="readonly")
        assert result["ok"] is False

    def test_valid_postures_accepted(self, mocker):
        from mcp_server.tools.scaffolding import scaffold_agent

        for posture in ("readonly", "creator", "full"):
            mocker.patch(
                "mcp_server.tools.scaffolding._run_script",
                return_value=_completed(0, "Created: .github/agents/x.agent.md"),
            )
            result = scaffold_agent("Agent", "Description", posture=posture)
            assert result["ok"] is True


class TestScaffoldWorkplan:
    def test_valid_slug_creates_workplan(self, mocker):
        from mcp_server.tools.scaffolding import scaffold_workplan

        mocker.patch(
            "mcp_server.tools.scaffolding._run_script",
            return_value=_completed(0, "Created: docs/plans/2026-03-17-my-sprint.md"),
        )
        result = scaffold_workplan("my-sprint")
        assert result["ok"] is True
        assert result["output_path"] is not None

    def test_invalid_slug_rejected(self):
        from mcp_server.tools.scaffolding import scaffold_workplan

        result = scaffold_workplan("../etc/shadow")
        assert result["ok"] is False
        assert result["errors"]

    def test_issues_passed_to_script(self, mocker):
        from mcp_server.tools.scaffolding import scaffold_workplan

        captured: list = []

        def fake_run(args):
            captured.extend(args)
            return _completed(0, "Created: docs/plans/2026-03-17-sprint.md")

        mocker.patch("mcp_server.tools.scaffolding._run_script", side_effect=fake_run)
        scaffold_workplan("sprint", issues="42,43")

        assert "--issues" in captured
        assert "42,43" in captured

    def test_script_failure_returns_ok_false(self, mocker):
        from mcp_server.tools.scaffolding import scaffold_workplan

        mocker.patch(
            "mcp_server.tools.scaffolding._run_script", return_value=_completed(1, "", "ERROR: workplan exists")
        )
        result = scaffold_workplan("existing-sprint")
        assert result["ok"] is False


# ---------------------------------------------------------------------------
# Research tools
# ---------------------------------------------------------------------------


class TestRunResearchScout:
    def test_valid_https_url_succeeds(self, mocker):
        from mcp_server.tools.research import run_research_scout

        mocker.patch("mcp_server.tools.research.validate_url", return_value="https://example.com/doc")
        mocker.patch(
            "mcp_server.tools.research._run_script",
            return_value=_completed(0, "Cached at .cache/sources/example.md"),
        )
        result = run_research_scout("https://example.com/doc")
        assert result["ok"] is True
        assert result["cache_path"] is not None

    def test_invalid_url_returns_ok_false(self, mocker):
        from mcp_server.tools.research import run_research_scout

        mocker.patch("mcp_server.tools.research.validate_url", side_effect=ValueError("scheme not allowed"))
        result = run_research_scout("http://evil.local/data")
        assert result["ok"] is False
        assert "scheme" in result["errors"][0]

    def test_fetch_failure_returns_ok_false(self, mocker):
        from mcp_server.tools.research import run_research_scout

        mocker.patch("mcp_server.tools.research.validate_url", return_value="https://example.com/doc")
        mocker.patch("mcp_server.tools.research._run_script", return_value=_completed(1, "", "error: network timeout"))
        result = run_research_scout("https://example.com/doc")
        assert result["ok"] is False
        assert result["errors"]

    def test_force_flag_passed_to_script(self, mocker):
        from mcp_server.tools.research import run_research_scout

        captured: list = []

        def fake_run(args, timeout=60):
            captured.extend(args)
            return _completed(0, ".cache/sources/example.md")

        mocker.patch("mcp_server.tools.research.validate_url", return_value="https://example.com/doc")
        mocker.patch("mcp_server.tools.research._run_script", side_effect=fake_run)
        run_research_scout("https://example.com/doc", force=True)
        assert "--force" in captured


class TestQueryDocs:
    def test_valid_query_returns_results(self, mocker):
        from mcp_server.tools.research import query_docs

        fake_results = [{"title": "AGENTS.md", "score": 0.9, "snippet": "Endogenous-First"}]
        mocker.patch("mcp_server.tools.research._run_script", return_value=_completed(0, json.dumps(fake_results)))
        result = query_docs("Endogenous-First axiom")
        assert result["ok"] is True
        assert len(result["results"]) == 1

    def test_invalid_scope_rejected(self):
        from mcp_server.tools.research import query_docs

        result = query_docs("query", scope="invalid_scope")
        assert result["ok"] is False
        assert any("scope" in e.lower() for e in result["errors"])

    def test_valid_scopes_accepted(self, mocker):
        from mcp_server.tools.research import query_docs

        for scope in ("manifesto", "agents", "guides", "research", "toolchain", "skills", "all"):
            mocker.patch("mcp_server.tools.research._run_script", return_value=_completed(0, "[]"))
            result = query_docs("test", scope=scope)
            assert result["ok"] is True

    def test_script_failure_returns_ok_false(self, mocker):
        from mcp_server.tools.research import query_docs

        mocker.patch("mcp_server.tools.research._run_script", return_value=_completed(1, "", "ERROR: index not found"))
        result = query_docs("something")
        assert result["ok"] is False

    def test_top_n_passed_to_script(self, mocker):
        from mcp_server.tools.research import query_docs

        captured: list = []

        def fake_run(args, timeout=60):
            captured.extend(args)
            return _completed(0, "[]")

        mocker.patch("mcp_server.tools.research._run_script", side_effect=fake_run)
        query_docs("test", top_n=10)
        assert "--top-n" in captured
        assert "10" in captured


# ---------------------------------------------------------------------------
# Scratchpad tool
# ---------------------------------------------------------------------------


class TestPruneScratchpad:
    def test_init_creates_file(self, mocker):
        from mcp_server.tools.scratchpad import prune_scratchpad

        mocker.patch("subprocess.run", return_value=_completed(0, "Initialized .tmp/main/2026-03-17.md"))
        result = prune_scratchpad()
        assert result["ok"] is True

    def test_dry_run_passes_check_only_flag(self, mocker):
        from mcp_server.tools.scratchpad import prune_scratchpad

        captured_args: list = []

        def fake_run(args, **kwargs):
            captured_args.extend(args)
            return _completed(0, ".tmp/main/2026-03-17.md already exists, 42 lines")

        mocker.patch("subprocess.run", side_effect=fake_run)
        result = prune_scratchpad(dry_run=True)
        assert "--check-only" in captured_args
        assert result["ok"] is True

    def test_explicit_branch_passed_through(self, mocker):
        from mcp_server.tools.scratchpad import prune_scratchpad

        # When branch is provided, no git call is made; subprocess.run receives --init
        call_count = [0]

        def fake_run(args, **kwargs):
            call_count[0] += 1
            if args[0] == "git":
                return _completed(0, "")  # git call for branch detection
            return _completed(0, ".tmp/feat-my-branch/2026-03-17.md")

        mocker.patch("subprocess.run", side_effect=fake_run)
        result = prune_scratchpad(branch="feat-my-branch")
        assert result["ok"] is True

    def test_script_failure_returns_ok_false(self, mocker):
        from mcp_server.tools.scratchpad import prune_scratchpad

        def fake_run(args, **kwargs):
            if "git" in args[0]:
                return _completed(0, "main")
            return _completed(1, "", "ERROR: could not create directory")

        mocker.patch("subprocess.run", side_effect=fake_run)
        result = prune_scratchpad()
        assert result["ok"] is False
        assert result["errors"]


# ---------------------------------------------------------------------------
# Server smoke test
# ---------------------------------------------------------------------------


class TestDogmaServerImport:
    def test_server_importable(self):
        """dogma_server.py should import without error and expose mcp instance."""
        import importlib

        mod = importlib.import_module("mcp_server.dogma_server")
        assert hasattr(mod, "mcp"), "Expected 'mcp' FastMCP instance"

    def test_server_registers_eight_tools(self):
        """The mcp server should register exactly 8 tools."""
        import importlib

        mod = importlib.import_module("mcp_server.dogma_server")
        # FastMCP stores tools in ._tool_manager or ._tools; check both conventions
        tool_manager = getattr(mod.mcp, "_tool_manager", None)
        if tool_manager is not None:
            tools = getattr(tool_manager, "_tools", {})
        else:
            tools = getattr(mod.mcp, "_tools", {})
        assert len(tools) == 8, f"Expected 8 tools, found {len(tools)}: {list(tools.keys())}"

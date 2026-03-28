"""End-to-end style integration tests for canonical MCP tools.

These tests exercise the tool callables directly while monkeypatching long-running
or external-facing internals for deterministic local execution.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, cast

import pytest

from mcp_server.tools import research, scaffolding, scratchpad, validation

pytestmark = pytest.mark.integration


def _completed(returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    """Build a fake CompletedProcess payload for tool subprocess stubs."""
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


@pytest.fixture
def deterministic_tool_mocks(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Make tool internals deterministic and local-only for query-case execution."""

    def _validation_run(args: list[str]) -> subprocess.CompletedProcess:
        script_name = Path(args[0]).name if args else ""
        if script_name == "check_substrate_health.py":
            return _completed(0, "PASS: substrate healthy\n")
        if script_name == "validate_agent_files.py":
            return _completed(0, "Validation OK\n")
        if script_name == "validate_synthesis.py":
            return _completed(0, "Synthesis OK\n")
        return _completed(1, stderr="ERROR: unknown validation script")

    def _scaffolding_run(args: list[str]) -> subprocess.CompletedProcess:
        script_name = Path(args[0]).name if args else ""
        if script_name == "scaffold_agent.py":
            generated = tmp_path / "generated-e2e.agent.md"
            return _completed(0, f"Created: {generated}\n")
        if script_name == "scaffold_workplan.py":
            return _completed(0, "Created: docs/plans/2026-03-28-e2e-workplan.md\n")
        return _completed(1, stderr="ERROR: unknown scaffolding script")

    def _research_run(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:  # noqa: ARG001
        script_name = Path(args[0]).name if args else ""
        if script_name == "fetch_source.py":
            return _completed(0, "Cached source at .cache/sources/e2e-source.md\n")
        if script_name == "query_docs.py":
            query = args[1] if len(args) > 1 else ""
            payload = [
                {
                    "path": "docs/guides/agents.md",
                    "score": 0.82,
                    "snippet": f"match for {query.strip() or 'empty-query'}",
                }
            ]
            return _completed(0, json.dumps(payload))
        return _completed(1, stderr="ERROR: unknown research script")

    def _scratchpad_run(
        args: list[str],
        capture_output: bool,
        text: bool,
        cwd: str,
        timeout: int,
    ) -> subprocess.CompletedProcess:  # noqa: ARG001
        return _completed(0, "Initialized .tmp/e2e-branch/2026-03-28.md with 12 lines\n")

    monkeypatch.setattr(validation, "_run_script", _validation_run)
    monkeypatch.setattr(scaffolding, "_run_script", _scaffolding_run)
    monkeypatch.setattr(research, "_run_script", _research_run)
    monkeypatch.setattr(research, "validate_url", lambda url: url)
    monkeypatch.setattr(scratchpad.subprocess, "run", _scratchpad_run)


QUERY_CASE_MATRIX: list[dict[str, Any]] = [
    {
        "case_id": "e2e_check_substrate_directive",
        "tool": "check_substrate",
        "variant": {"phrasing_style": "directive", "context_depth": "low", "ambiguity": "low"},
    },
    {
        "case_id": "e2e_check_substrate_contextual",
        "tool": "check_substrate",
        "variant": {"phrasing_style": "contextual", "context_depth": "high", "ambiguity": "medium"},
    },
    {
        "case_id": "e2e_validate_agent_file_precise",
        "tool": "validate_agent_file",
        "input": {"file_path": ".github/agents/executive-orchestrator.agent.md"},
        "variant": {"phrasing_style": "precise", "context_depth": "medium", "ambiguity": "low"},
    },
    {
        "case_id": "e2e_validate_agent_file_loose",
        "tool": "validate_agent_file",
        "input": {"file_path": ".github/agents/review.agent.md"},
        "variant": {"phrasing_style": "natural", "context_depth": "low", "ambiguity": "medium"},
    },
    {
        "case_id": "e2e_validate_synthesis_strict",
        "tool": "validate_synthesis",
        "input": {"file_path": "docs/research/llm-strategic-advice-quality.md", "min_lines": 80},
        "variant": {"phrasing_style": "strict", "context_depth": "high", "ambiguity": "low"},
    },
    {
        "case_id": "e2e_validate_synthesis_lenient",
        "tool": "validate_synthesis",
        "input": {"file_path": "docs/research/ai-cognitive-load.md", "min_lines": 40},
        "variant": {"phrasing_style": "lenient", "context_depth": "medium", "ambiguity": "low"},
    },
    {
        "case_id": "e2e_scaffold_agent_structured",
        "tool": "scaffold_agent",
        "input": {
            "name": "E2E Validation Agent",
            "description": "Agent scaffold for deterministic MCP integration tests.",
            "area": "tests",
            "posture": "readonly",
        },
        "variant": {"phrasing_style": "structured", "context_depth": "medium", "ambiguity": "low"},
    },
    {
        "case_id": "e2e_scaffold_agent_ambiguous_request",
        "tool": "scaffold_agent",
        "input": {
            "name": "E2E Planner Agent",
            "description": "Create a planning-focused agent with broad guidance language.",
            "area": "planning",
            "posture": "creator",
        },
        "variant": {"phrasing_style": "broad", "context_depth": "high", "ambiguity": "high"},
    },
    {
        "case_id": "e2e_scaffold_workplan_issue_dense",
        "tool": "scaffold_workplan",
        "input": {"slug": "mcp-e2e-suite", "issues": "494,33"},
        "variant": {"phrasing_style": "issue-driven", "context_depth": "high", "ambiguity": "low"},
    },
    {
        "case_id": "e2e_scaffold_workplan_minimal",
        "tool": "scaffold_workplan",
        "input": {"slug": "mcp-e2e-minimal", "issues": ""},
        "variant": {"phrasing_style": "minimal", "context_depth": "low", "ambiguity": "medium"},
    },
    {
        "case_id": "e2e_run_research_scout_specific",
        "tool": "run_research_scout",
        "input": {"url": "https://modelcontextprotocol.io/docs/overview", "force": False},
        "variant": {"phrasing_style": "specific", "context_depth": "medium", "ambiguity": "low"},
    },
    {
        "case_id": "e2e_run_research_scout_refresh",
        "tool": "run_research_scout",
        "input": {"url": "https://example.com/research-note", "force": True},
        "variant": {"phrasing_style": "refresh", "context_depth": "low", "ambiguity": "medium"},
    },
    {
        "case_id": "e2e_query_docs_precise_scope",
        "tool": "query_docs",
        "input": {"query": "session start encoding checkpoint", "scope": "guides", "top_n": 3},
        "variant": {"phrasing_style": "precise", "context_depth": "high", "ambiguity": "low"},
    },
    {
        "case_id": "e2e_query_docs_broad_scope",
        "tool": "query_docs",
        "input": {"query": "how should an agent start", "scope": "all", "top_n": 2},
        "variant": {"phrasing_style": "broad", "context_depth": "low", "ambiguity": "high"},
    },
    {
        "case_id": "e2e_prune_scratchpad_init",
        "tool": "prune_scratchpad",
        "input": {"branch": "e2e-branch", "dry_run": False},
        "variant": {"phrasing_style": "init", "context_depth": "medium", "ambiguity": "low"},
    },
    {
        "case_id": "e2e_prune_scratchpad_check_only",
        "tool": "prune_scratchpad",
        "input": {"branch": "e2e-branch", "dry_run": True},
        "variant": {"phrasing_style": "status", "context_depth": "low", "ambiguity": "low"},
    },
]


def _run_tool_case(case: dict[str, Any]) -> dict[str, Any]:
    tool = cast(str, case["tool"])
    params = cast(dict[str, Any], case.get("input", {}))

    if tool == "check_substrate":
        return validation.check_substrate()
    if tool == "validate_agent_file":
        return validation.validate_agent_file(**params)
    if tool == "validate_synthesis":
        return validation.validate_synthesis(**params)
    if tool == "scaffold_agent":
        return scaffolding.scaffold_agent(**params)
    if tool == "scaffold_workplan":
        return scaffolding.scaffold_workplan(**params)
    if tool == "run_research_scout":
        return research.run_research_scout(**params)
    if tool == "query_docs":
        return research.query_docs(**params)
    if tool == "prune_scratchpad":
        return scratchpad.prune_scratchpad(**params)

    raise AssertionError(f"Unsupported tool in matrix: {tool}")


def _assert_tool_specific_fields(tool_name: str, result: dict[str, Any]) -> None:
    """Validate per-tool result schema fields beyond ok/errors."""
    if tool_name == "check_substrate":
        assert isinstance(result.get("report"), str)
        assert result["report"]
        return

    if tool_name in {"validate_agent_file", "validate_synthesis"}:
        assert isinstance(result.get("file_path"), str)
        assert result["file_path"]
        return

    if tool_name in {"scaffold_agent", "scaffold_workplan"}:
        assert isinstance(result.get("output_path"), str)
        assert result["output_path"]
        return

    if tool_name == "run_research_scout":
        assert isinstance(result.get("url"), str)
        assert result["url"].startswith("https://")
        assert isinstance(result.get("cache_path"), str)
        assert result["cache_path"]
        return

    if tool_name == "query_docs":
        assert isinstance(result.get("results"), list)
        assert result["results"]
        return

    if tool_name == "prune_scratchpad":
        assert isinstance(result.get("file_path"), str)
        assert isinstance(result.get("exists"), bool)
        return

    raise AssertionError(f"Unhandled tool schema assertion for {tool_name}")


@pytest.mark.io
@pytest.mark.parametrize("case", QUERY_CASE_MATRIX, ids=[str(case["case_id"]) for case in QUERY_CASE_MATRIX])
def test_mcp_e2e_query_case_matrix(case: dict[str, Any], deterministic_tool_mocks: None) -> None:
    """Execute all matrix cases against canonical tool callables."""
    case_id = cast(str, case["case_id"])
    tool_name = cast(str, case["tool"])

    assert case_id.startswith(f"e2e_{tool_name}_")

    result = _run_tool_case(case)

    assert isinstance(result, dict)
    assert result.get("ok") is True
    assert "errors" in result
    assert isinstance(result["errors"], list)
    _assert_tool_specific_fields(tool_name, result)


def test_mcp_e2e_matrix_has_two_variants_per_tool() -> None:
    """Guard that every canonical tool has at least two query/input variants."""
    counts: dict[str, int] = {}
    for case in QUERY_CASE_MATRIX:
        tool = str(case["tool"])
        counts[tool] = counts.get(tool, 0) + 1

    expected_tools = {
        "check_substrate",
        "validate_agent_file",
        "validate_synthesis",
        "scaffold_agent",
        "scaffold_workplan",
        "run_research_scout",
        "query_docs",
        "prune_scratchpad",
    }

    assert set(counts) == expected_tools
    assert all(counts[tool] >= 2 for tool in expected_tools)


@pytest.mark.io
def test_mcp_e2e_cross_tool_scaffold_then_validate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Cross-tool workflow: scaffold an agent, then validate the generated path."""
    generated = tmp_path / "cross-tool.agent.md"
    generated.write_text(
        "---\nname: Cross\ndescription: Cross tool\ntools: [search]\nhandoffs: []\n---\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        scaffolding,
        "_run_script",
        lambda args: _completed(0, f"Created: {generated}\n"),
    )
    monkeypatch.setattr(validation, "validate_repo_path", lambda file_path: Path(file_path).resolve())
    monkeypatch.setattr(validation, "_run_script", lambda args: _completed(0, "Validation OK\n"))

    scaffolded = scaffolding.scaffold_agent(
        name="Cross Tool Agent",
        description="Generated for cross-tool MCP test.",
        area="tests",
        posture="readonly",
    )
    assert scaffolded["ok"] is True
    assert scaffolded["output_path"] == str(generated)

    validated = validation.validate_agent_file(scaffolded["output_path"])
    assert validated["ok"] is True
    assert validated["file_path"] == str(generated.resolve())


def test_mcp_e2e_validate_tools_reject_invalid_paths() -> None:
    """Invalid path edge case for both validate_* tools."""
    invalid = "/tmp/outside-repo.md"

    agent_result = validation.validate_agent_file(invalid)
    synthesis_result = validation.validate_synthesis(invalid)

    assert agent_result["ok"] is False
    assert synthesis_result["ok"] is False
    assert agent_result["errors"]
    assert synthesis_result["errors"]


def test_mcp_e2e_run_research_scout_invalid_scheme() -> None:
    """Invalid URL scheme should fail fast with structured errors."""
    result = research.run_research_scout("http://example.com/not-https")

    assert result["ok"] is False
    assert result["cache_path"] is None
    assert result["errors"]


def test_mcp_e2e_query_docs_empty_query_graceful(monkeypatch: pytest.MonkeyPatch) -> None:
    """Empty query returns a structured response without crashing."""
    monkeypatch.setattr(research, "_run_script", lambda args: _completed(0, "[]"))

    result = research.query_docs(query="", scope="all", top_n=5)

    assert result["ok"] is True
    assert isinstance(result["results"], list)
    assert result["results"] == []
    assert result["errors"] == []

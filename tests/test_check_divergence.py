"""
tests/test_check_divergence.py
-------------------------------
Tests for scripts/check_divergence.py — cookiecutter template drift detector.

Covers:
- Happy path: derived repo identical to template → exit 0, no drift
- Drift detection: derived repo missing a hook ID → drift reported
- --check flag: exit 1 when drift is present
- --dry-run: no comparison performed, exit 0
- --export-hgt: YAML output includes drifted/changed sections
- Invalid --repo path: exit 2 with error message
- compare_agents_md: removed/added headings, missing files
- compare_precommit: removed/added hook IDs, missing files
- compare_pyproject: missing required sections, missing file
- check_client_values: absent client-values.yml flagged
- extract helpers: h2 headings, hook IDs, pyproject sections
- has_drift: detects added/removed/changed; clean on empty
- build_hgt_candidates: maps results to candidate list
- format_report: contains DRIFT / NO DRIFT summary

All tests use tmp_path fixtures for file I/O isolation (hermetic).
Coverage target: ≥80% of scripts/check_divergence.py
"""

from __future__ import annotations

import importlib.util
import io
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Module loader
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def cd_mod():
    """Load scripts/check_divergence.py via importlib for in-process testing."""
    spec = importlib.util.spec_from_file_location(
        "check_divergence",
        Path(__file__).parent.parent / "scripts" / "check_divergence.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

_AGENTS_MD_TEMPLATE = """\
# AGENTS.md

## Guiding Constraints

## Programmatic-First Principle

## Toolchain Reference

## Guardrails
"""

_AGENTS_MD_DERIVED_IDENTICAL = _AGENTS_MD_TEMPLATE

_AGENTS_MD_DERIVED_MISSING = """\
# AGENTS.md

## Guiding Constraints

## Guardrails
"""

_AGENTS_MD_DERIVED_EXTRA = """\
# AGENTS.md

## Guiding Constraints

## Programmatic-First Principle

## Toolchain Reference

## Guardrails

## My Custom Section
"""

_PRECOMMIT_TEMPLATE = """\
repos:
  - repo: local
    hooks:
      - id: ruff
      - id: validate-synthesis
      - id: no-heredoc-writes
"""

_PRECOMMIT_DERIVED_IDENTICAL = _PRECOMMIT_TEMPLATE

_PRECOMMIT_DERIVED_MISSING_HOOK = """\
repos:
  - repo: local
    hooks:
      - id: ruff
"""

_PRECOMMIT_DERIVED_EXTRA_HOOK = """\
repos:
  - repo: local
    hooks:
      - id: ruff
      - id: validate-synthesis
      - id: no-heredoc-writes
      - id: custom-hook
"""

_PYPROJECT_FULL = """\
[project]
name = "test"

[tool.pytest.ini_options]
testpaths = ["tests"]
"""

_PYPROJECT_MISSING_PYTEST = """\
[project]
name = "test"
"""

_CLIENT_VALUES = """\
# client-values.yml
deployment_layer: test
"""


def _make_template(tmp_path: Path, agents: str, precommit: str) -> Path:
    """Write template-side files to a directory."""
    d = tmp_path / "template"
    d.mkdir()
    (d / "AGENTS.md").write_text(agents, encoding="utf-8")
    (d / ".pre-commit-config.yaml").write_text(precommit, encoding="utf-8")
    return d


def _make_derived(
    tmp_path: Path,
    *,
    agents: str | None = None,
    precommit: str | None = None,
    pyproject: str | None = None,
    client_values: bool = True,
) -> Path:
    """Write derived-repo-side files to a directory."""
    d = tmp_path / "derived"
    d.mkdir(exist_ok=True)
    if agents is not None:
        (d / "AGENTS.md").write_text(agents, encoding="utf-8")
    if precommit is not None:
        (d / ".pre-commit-config.yaml").write_text(precommit, encoding="utf-8")
    if pyproject is not None:
        (d / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    if client_values:
        (d / "client-values.yml").write_text(_CLIENT_VALUES, encoding="utf-8")
    return d


# ---------------------------------------------------------------------------
# Extraction helper tests
# ---------------------------------------------------------------------------


def test_extract_h2_headings(cd_mod):
    text = "# Title\n## Section One\nSome text\n## Section Two\n### Sub\n"
    result = cd_mod.extract_h2_headings(text)
    assert result == ["Section One", "Section Two"]


def test_extract_hook_ids(cd_mod):
    text = _PRECOMMIT_TEMPLATE
    result = cd_mod.extract_hook_ids(text)
    assert set(result) == {"ruff", "validate-synthesis", "no-heredoc-writes"}


def test_extract_pyproject_sections(cd_mod):
    text = _PYPROJECT_FULL
    result = cd_mod.extract_pyproject_sections(text)
    assert "project" in result
    assert "tool.pytest.ini_options" in result


# ---------------------------------------------------------------------------
# has_drift
# ---------------------------------------------------------------------------


def test_has_drift_clean(cd_mod):
    results = [{"file": "x", "added": [], "removed": [], "changed": [], "errors": []}]
    assert cd_mod.has_drift(results) is False


def test_has_drift_removed(cd_mod):
    results = [{"file": "x", "added": [], "removed": ["something"], "changed": [], "errors": []}]
    assert cd_mod.has_drift(results) is True


def test_has_drift_added(cd_mod):
    results = [{"file": "x", "added": ["something"], "removed": [], "changed": [], "errors": []}]
    assert cd_mod.has_drift(results) is True


def test_has_drift_with_errors(cd_mod):
    """has_drift() treats non-empty errors as drift so CI fails when comparisons error."""
    results = [{"file": "x", "added": [], "removed": [], "changed": [], "errors": ["read error"]}]
    assert cd_mod.has_drift(results) is True


# ---------------------------------------------------------------------------
# build_hgt_candidates
# ---------------------------------------------------------------------------


def test_build_hgt_candidates(cd_mod):
    results = [
        {"file": "AGENTS.md", "added": ["New Section"], "removed": ["Old Section"], "changed": [], "errors": []},
        {"file": ".pre-commit-config.yaml", "added": [], "removed": [], "changed": ["hook-id"], "errors": []},
    ]
    candidates = cd_mod.build_hgt_candidates(results)
    assert {"file": "AGENTS.md", "type": "added", "section": "New Section"} in candidates
    assert {"file": "AGENTS.md", "type": "removed", "section": "Old Section"} in candidates
    assert {"file": ".pre-commit-config.yaml", "type": "changed", "section": "hook-id"} in candidates


# ---------------------------------------------------------------------------
# compare_agents_md
# ---------------------------------------------------------------------------


def test_compare_agents_md_identical(cd_mod, tmp_path, monkeypatch):
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = _make_derived(tmp_path, agents=_AGENTS_MD_DERIVED_IDENTICAL)
    monkeypatch.setattr(cd_mod, "TEMPLATE_ROOT", template)
    result = cd_mod.compare_agents_md(template, derived)
    assert result["removed"] == []
    assert result["added"] == []
    assert result["errors"] == []


def test_compare_agents_md_removed(cd_mod, tmp_path, monkeypatch):
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = _make_derived(tmp_path, agents=_AGENTS_MD_DERIVED_MISSING)
    monkeypatch.setattr(cd_mod, "TEMPLATE_ROOT", template)
    result = cd_mod.compare_agents_md(template, derived)
    assert "Programmatic-First Principle" in result["removed"]
    assert "Toolchain Reference" in result["removed"]
    assert result["added"] == []


def test_compare_agents_md_added(cd_mod, tmp_path, monkeypatch):
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = _make_derived(tmp_path, agents=_AGENTS_MD_DERIVED_EXTRA)
    monkeypatch.setattr(cd_mod, "TEMPLATE_ROOT", template)
    result = cd_mod.compare_agents_md(template, derived)
    assert "My Custom Section" in result["added"]
    assert result["removed"] == []


def test_compare_agents_md_missing_derived(cd_mod, tmp_path):
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = tmp_path / "empty_derived"
    derived.mkdir()
    result = cd_mod.compare_agents_md(template, derived)
    assert any("not found" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# compare_precommit
# ---------------------------------------------------------------------------


def test_compare_precommit_identical(cd_mod, tmp_path):
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = _make_derived(tmp_path, precommit=_PRECOMMIT_DERIVED_IDENTICAL)
    result = cd_mod.compare_precommit(template, derived)
    assert result["removed"] == []
    assert result["added"] == []
    assert result["errors"] == []


def test_compare_precommit_missing_hook(cd_mod, tmp_path):
    """Derived repo missing hook IDs from template → drift reported."""
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = _make_derived(tmp_path, precommit=_PRECOMMIT_DERIVED_MISSING_HOOK)
    result = cd_mod.compare_precommit(template, derived)
    assert "validate-synthesis" in result["removed"]
    assert "no-heredoc-writes" in result["removed"]
    assert result["added"] == []


def test_compare_precommit_extra_hook(cd_mod, tmp_path):
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = _make_derived(tmp_path, precommit=_PRECOMMIT_DERIVED_EXTRA_HOOK)
    result = cd_mod.compare_precommit(template, derived)
    assert "custom-hook" in result["added"]
    assert result["removed"] == []


def test_compare_precommit_missing_derived(cd_mod, tmp_path):
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = tmp_path / "empty_derived2"
    derived.mkdir()
    result = cd_mod.compare_precommit(template, derived)
    assert any("not found" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# compare_pyproject
# ---------------------------------------------------------------------------


def test_compare_pyproject_full(cd_mod, tmp_path):
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = _make_derived(tmp_path, pyproject=_PYPROJECT_FULL)
    result = cd_mod.compare_pyproject(template, derived)
    assert result["removed"] == []
    assert result["errors"] == []


def test_compare_pyproject_missing_section(cd_mod, tmp_path):
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = _make_derived(tmp_path, pyproject=_PYPROJECT_MISSING_PYTEST)
    result = cd_mod.compare_pyproject(template, derived)
    assert "tool.pytest.ini_options" in result["removed"]


def test_compare_pyproject_missing_file(cd_mod, tmp_path):
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = tmp_path / "empty_derived3"
    derived.mkdir()
    result = cd_mod.compare_pyproject(template, derived)
    assert any("not found" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# check_client_values
# ---------------------------------------------------------------------------


def test_check_client_values_present(cd_mod, tmp_path):
    derived = _make_derived(tmp_path, client_values=True)
    result = cd_mod.check_client_values(derived)
    assert result["removed"] == []


def test_check_client_values_absent(cd_mod, tmp_path):
    derived = _make_derived(tmp_path, client_values=False)
    result = cd_mod.check_client_values(derived)
    assert result["removed"] != []
    assert any("absent" in item for item in result["removed"])


# ---------------------------------------------------------------------------
# format_report
# ---------------------------------------------------------------------------


def test_format_report_no_drift(cd_mod):
    results = [
        {"file": "AGENTS.md", "added": [], "removed": [], "changed": [], "errors": []},
    ]
    report = cd_mod.format_report(results)
    assert "NO DRIFT" in report
    assert "AGENTS.md: OK" in report


def test_format_report_drift(cd_mod):
    results = [
        {"file": "AGENTS.md", "added": [], "removed": ["Missing Section"], "changed": [], "errors": []},
    ]
    report = cd_mod.format_report(results)
    assert "DRIFT DETECTED" in report
    assert "AGENTS.md: DRIFT" in report
    assert "Missing Section" in report


# ---------------------------------------------------------------------------
# main() integration tests
# ---------------------------------------------------------------------------


def _run_main(cd_mod, args: list[str], monkeypatch, tmp_path) -> tuple[int, str]:
    """Run main() with captured stdout, returns (exit_code, stdout_text)."""
    buf = io.StringIO()
    with patch("sys.stdout", buf):
        # Redirect stderr too to suppress error messages in test output
        with patch("sys.stderr", io.StringIO()):
            code = cd_mod.main(args)
    return code, buf.getvalue()


def test_main_invalid_repo(cd_mod, tmp_path, monkeypatch):
    """Invalid --repo path → exit 2."""
    nonexistent = str(tmp_path / "does_not_exist")
    # stderr suppressed; just check exit code
    buf = io.StringIO()
    with patch("sys.stderr", buf):
        code = cd_mod.main(["--repo", nonexistent])
    assert code == 2
    assert "does not exist" in buf.getvalue()


def test_main_dry_run(cd_mod, tmp_path, monkeypatch):
    """--dry-run: no comparison, exit 0."""
    derived = _make_derived(tmp_path)
    code, output = _run_main(cd_mod, ["--repo", str(derived), "--dry-run"], monkeypatch, tmp_path)
    assert code == 0
    assert "Dry run" in output
    assert "AGENTS.md" in output


def test_main_no_drift_exit_0(cd_mod, tmp_path, monkeypatch):
    """When derived repo matches template artefacts, exit 0."""
    # Build a minimal derived repo that is identical to what compare_* expects
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = _make_derived(
        tmp_path,
        agents=_AGENTS_MD_TEMPLATE,
        precommit=_PRECOMMIT_TEMPLATE,
        pyproject=_PYPROJECT_FULL,
        client_values=True,
    )
    monkeypatch.setattr(cd_mod, "TEMPLATE_ROOT", template)
    code, output = _run_main(cd_mod, ["--repo", str(derived), "--check"], monkeypatch, tmp_path)
    assert code == 0
    assert "NO DRIFT" in output


def test_main_drift_check_exits_1(cd_mod, tmp_path, monkeypatch):
    """--check exits 1 when drift detected (missing hook in derived repo)."""
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = _make_derived(
        tmp_path,
        agents=_AGENTS_MD_TEMPLATE,
        precommit=_PRECOMMIT_DERIVED_MISSING_HOOK,
        pyproject=_PYPROJECT_FULL,
        client_values=True,
    )
    monkeypatch.setattr(cd_mod, "TEMPLATE_ROOT", template)
    code, output = _run_main(cd_mod, ["--repo", str(derived), "--check"], monkeypatch, tmp_path)
    assert code == 1
    assert "DRIFT" in output


def test_main_drift_no_check_exits_0(cd_mod, tmp_path, monkeypatch):
    """Without --check, drift is reported but exit 0."""
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = _make_derived(
        tmp_path,
        agents=_AGENTS_MD_TEMPLATE,
        precommit=_PRECOMMIT_DERIVED_MISSING_HOOK,
        pyproject=_PYPROJECT_FULL,
        client_values=True,
    )
    monkeypatch.setattr(cd_mod, "TEMPLATE_ROOT", template)
    code, output = _run_main(cd_mod, ["--repo", str(derived)], monkeypatch, tmp_path)
    assert code == 0
    assert "DRIFT" in output


def test_main_export_hgt(cd_mod, tmp_path, monkeypatch):
    """--export-hgt: YAML candidates output when drift exists."""
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = _make_derived(
        tmp_path,
        agents=_AGENTS_MD_DERIVED_MISSING,
        precommit=_PRECOMMIT_TEMPLATE,
        pyproject=_PYPROJECT_FULL,
        client_values=True,
    )
    monkeypatch.setattr(cd_mod, "TEMPLATE_ROOT", template)
    code, output = _run_main(cd_mod, ["--repo", str(derived), "--export-hgt"], monkeypatch, tmp_path)
    assert code == 0
    assert "HGT Candidates" in output
    assert "AGENTS.md" in output


def test_main_export_hgt_no_drift_empty(cd_mod, tmp_path, monkeypatch):
    """--export-hgt with no drift: HGT Candidates section present but empty list."""
    template = _make_template(tmp_path, _AGENTS_MD_TEMPLATE, _PRECOMMIT_TEMPLATE)
    derived = _make_derived(
        tmp_path,
        agents=_AGENTS_MD_TEMPLATE,
        precommit=_PRECOMMIT_TEMPLATE,
        pyproject=_PYPROJECT_FULL,
        client_values=True,
    )
    monkeypatch.setattr(cd_mod, "TEMPLATE_ROOT", template)
    code, output = _run_main(cd_mod, ["--repo", str(derived), "--export-hgt"], monkeypatch, tmp_path)
    assert code == 0
    assert "HGT Candidates" in output

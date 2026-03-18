"""
tests/test_audit_provenance.py
------------------------------
Tests for scripts/audit_provenance.py — value signal provenance auditor.

Covers: audit_file, build_report, format_summary, main() (via importlib and
argv monkeypatching). All tests are pure-Python, no external dependencies.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module loader fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def prov_mod():
    """Load scripts/audit_provenance.py via importlib for in-process testing."""
    spec = importlib.util.spec_from_file_location(
        "audit_provenance",
        Path(__file__).parent.parent / "scripts" / "audit_provenance.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_manifesto(tmp_path: Path, extra_headings: list[str] | None = None) -> Path:
    """Write a minimal MANIFESTO.md with the canonical axiom headings."""
    headings = [
        "### 1. Endogenous-First",
        "### 2. Algorithms Before Tokens",
        "### 3. Local Compute-First",
        "### 4. Programmatic-First",
        "### 5. Documentation-First",
        "### 6. Minimal Posture",
    ]
    if extra_headings:
        headings.extend(extra_headings)
    manifesto = tmp_path / "MANIFESTO.md"
    manifesto.write_text("\n\n".join(headings) + "\n", encoding="utf-8")
    return manifesto


def _write_agent(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestHappyPath:
    """test_happy_path: valid governs: citation -> zero unverifiable, not orphaned."""

    @pytest.mark.io
    def test_happy_path(self, prov_mod, tmp_path):
        manifesto = _write_manifesto(tmp_path)
        agent = _write_agent(
            tmp_path,
            "good.agent.md",
            "---\nname: Good\ndescription: x\ntools: []\nx-governs:\n  - endogenous-first\n---\nBody.\n",
        )
        known = prov_mod.extract_manifesto_axioms(manifesto)
        result = prov_mod.audit_file(agent, known)
        assert result["orphaned"] is False
        assert result["unverifiable"] == []
        assert "endogenous-first" in result["citations"]


class TestOrphanedFile:
    """test_orphaned_file: no x-governs: field -> orphaned=True."""

    @pytest.mark.io
    def test_orphaned_file(self, prov_mod, tmp_path):
        manifesto = _write_manifesto(tmp_path)
        agent = _write_agent(
            tmp_path,
            "orphan.agent.md",
            "---\nname: Orphan\ndescription: y\ntools: []\n---\nNo governs.\n",
        )
        known = prov_mod.extract_manifesto_axioms(manifesto)
        result = prov_mod.audit_file(agent, known)
        assert result["orphaned"] is True
        assert result["citations"] == []
        assert result["unverifiable"] == []


class TestUnverifiableCitation:
    """test_unverifiable_citation: x-governs: [fake-axiom-xyz] -> unverifiable non-empty."""

    @pytest.mark.io
    def test_unverifiable_citation(self, prov_mod, tmp_path):
        manifesto = _write_manifesto(tmp_path)
        agent = _write_agent(
            tmp_path,
            "bad.agent.md",
            "---\nname: Bad\ndescription: z\ntools: []\nx-governs:\n  - fake-axiom-xyz\n---\nBody.\n",
        )
        known = prov_mod.extract_manifesto_axioms(manifesto)
        result = prov_mod.audit_file(agent, known)
        assert result["orphaned"] is False
        assert "fake-axiom-xyz" in result["unverifiable"]


class TestJsonOutputSchema:
    """test_json_output_schema: run on tmp agents dir -> JSON has all required keys."""

    @pytest.mark.io
    def test_json_output_schema(self, prov_mod, tmp_path):
        manifesto = _write_manifesto(tmp_path)
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        _write_agent(
            agents_dir,
            "a.agent.md",
            "---\nname: A\ndescription: a\ntools: []\nx-governs:\n  - endogenous-first\n---\nBody.\n",
        )
        report = prov_mod.build_report(agents_dir, manifesto)
        assert "files" in report
        assert "fleet_citation_coverage_pct" in report
        assert "total_unverifiable" in report
        assert isinstance(report["files"], list)
        assert len(report["files"]) == 1
        file_entry = report["files"][0]
        for key in ("path", "citations", "orphaned", "unverifiable"):
            assert key in file_entry, f"missing key: {key}"


class TestMainExits0Advisory:
    """test_main_exits_0_advisory: always exits 0 even when orphaned files present."""

    @pytest.mark.io
    def test_main_exits_0_advisory(self, prov_mod, tmp_path):
        manifesto = _write_manifesto(tmp_path)
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        _write_agent(
            agents_dir,
            "orphan.agent.md",
            "---\nname: Orphan\ndescription: x\ntools: []\n---\nNo governs.\n",
        )
        exit_code = prov_mod.main(
            [
                "--agents-dir",
                str(agents_dir),
                "--manifesto",
                str(manifesto),
            ]
        )
        assert exit_code == 0


class TestFleetCoveragePct:
    """test_fleet_coverage_pct: 1 file with x-governs, 1 without -> 50.0%."""

    @pytest.mark.io
    def test_fleet_coverage_pct(self, prov_mod, tmp_path):
        manifesto = _write_manifesto(tmp_path)
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        _write_agent(
            agents_dir,
            "governed.agent.md",
            "---\nname: G\ndescription: g\ntools: []\nx-governs:\n  - endogenous-first\n---\nBody.\n",
        )
        _write_agent(
            agents_dir,
            "orphan.agent.md",
            "---\nname: O\ndescription: o\ntools: []\n---\nNo governs.\n",
        )
        report = prov_mod.build_report(agents_dir, manifesto)
        assert report["fleet_citation_coverage_pct"] == 50.0


class TestSummaryFormat:
    """test_summary_format: --format summary produces output containing file path info."""

    @pytest.mark.io
    def test_summary_format(self, prov_mod, tmp_path, capsys):
        manifesto = _write_manifesto(tmp_path)
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        _write_agent(
            agents_dir,
            "myagent.agent.md",
            "---\nname: M\ndescription: m\ntools: []\nx-governs:\n  - endogenous-first\n---\nBody.\n",
        )
        exit_code = prov_mod.main(
            [
                "--agents-dir",
                str(agents_dir),
                "--manifesto",
                str(manifesto),
                "--format",
                "summary",
            ]
        )
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "myagent.agent.md" in captured.out
        assert "Fleet citation coverage" in captured.out

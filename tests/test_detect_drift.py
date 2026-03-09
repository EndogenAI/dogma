"""
tests/test_detect_drift.py
--------------------------
Tests for scripts/detect_drift.py — watermark-phrase drift detection.

Covers: score_agent_file, build_report, format_summary, main() (via importlib
and argv monkeypatching). All tests are pure-Python, no external dependencies.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module loader fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def drift_mod():
    """Load scripts/detect_drift.py via importlib for in-process testing."""
    spec = importlib.util.spec_from_file_location(
        "detect_drift",
        Path(__file__).parent.parent / "scripts" / "detect_drift.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Unit tests for score_agent_file
# ---------------------------------------------------------------------------


class TestScoreAgentFile:
    """Tests for the per-agent scoring function."""

    @pytest.mark.io
    def test_perfect_score_all_watermarks_present(self, drift_mod, tmp_path):
        """Agent file with all 6 watermarks returns drift_score=1.0."""
        body = "\n".join(
            [
                "---\nname: Full Agent\ndescription: x\ntools: []\n---",
                "Endogenous-First is the governing axiom.",
                "Algorithms Before Tokens guides our design.",
                "Local Compute-First reduces cloud dependency.",
                "encode-before-act is the operational pattern.",
                "morphogenetic seed is embedded through inheritance.",
                "programmatic-first is our default posture.",
            ]
        )
        agent_file = tmp_path / "full.agent.md"
        agent_file.write_text(body)
        result = drift_mod.score_agent_file(agent_file)
        assert result["drift_score"] == 1.0
        assert result["missing"] == []

    @pytest.mark.io
    def test_zero_score_no_watermarks(self, drift_mod, tmp_path):
        """Agent file with no watermarks returns drift_score=0.0."""
        agent_file = tmp_path / "empty.agent.md"
        agent_file.write_text("---\nname: X\ndescription: y\ntools: []\n---\nNo references here.\n")
        result = drift_mod.score_agent_file(agent_file)
        assert result["drift_score"] == 0.0
        assert len(result["missing"]) == 6

    @pytest.mark.io
    def test_partial_score(self, drift_mod, tmp_path):
        """Agent file with 3 of 6 watermarks returns drift_score=0.5."""
        body = (
            "---\nname: Partial\ndescription: x\ntools: []\n---\n"
            "Endogenous-First is key.\n"
            "Algorithms Before Tokens matters.\n"
            "Local Compute-First preferred.\n"
        )
        agent_file = tmp_path / "partial.agent.md"
        agent_file.write_text(body)
        result = drift_mod.score_agent_file(agent_file)
        assert result["drift_score"] == pytest.approx(0.5)
        assert len(result["missing"]) == 3

    @pytest.mark.io
    def test_case_insensitive_matching(self, drift_mod, tmp_path):
        """Watermark matching is case-insensitive."""
        agent_file = tmp_path / "lower.agent.md"
        agent_file.write_text(
            "---\nname: Y\ndescription: y\ntools: []\n---\n"
            "endogenous-first governs all.\nalgorithms before tokens.\n"
            "local compute-first.\nencode-before-act.\nmorphogenetic seed.\nprogrammatic-first.\n"
        )
        result = drift_mod.score_agent_file(agent_file)
        assert result["drift_score"] == 1.0

    @pytest.mark.io
    def test_phrase_in_frontmatter_not_counted(self, drift_mod, tmp_path):
        """Watermark phrases in YAML frontmatter (before body) are NOT counted."""
        # All phrases in frontmatter only, body is empty
        frontmatter = (
            "---\n"
            "name: Frontmatter Only\n"
            "description: Endogenous-First Algorithms Before Tokens Local Compute-First\n"
            "tools: []\n"
            "---\n"
            "No body watermarks here.\n"
        )
        agent_file = tmp_path / "fm-only.agent.md"
        agent_file.write_text(frontmatter)
        result = drift_mod.score_agent_file(agent_file)
        # Frontmatter is stripped — score should be 0 or reflect body only
        assert result["drift_score"] == 0.0

    @pytest.mark.io
    def test_unreadable_file_returns_zero_score(self, drift_mod, tmp_path):
        """OSError on read returns score=0.0 with all phrases in missing."""
        missing_file = tmp_path / "nonexistent.agent.md"
        result = drift_mod.score_agent_file(missing_file)
        assert result["drift_score"] == 0.0
        assert len(result["missing"]) == 6


# ---------------------------------------------------------------------------
# Unit tests for build_report
# ---------------------------------------------------------------------------


class TestBuildReport:
    """Tests for fleet-wide report assembly."""

    def test_fleet_avg_computed(self, drift_mod):
        """build_report computes correct fleet average."""
        results = [
            {"file": "a.md", "drift_score": 1.0, "missing": []},
            {"file": "b.md", "drift_score": 0.5, "missing": ["x"]},
        ]
        report = drift_mod.build_report(results, 0.33)
        assert report["fleet_avg"] == pytest.approx(0.75)

    def test_below_threshold_list(self, drift_mod):
        """build_report populates below_threshold with files under threshold."""
        results = [
            {"file": "good.md", "drift_score": 0.8, "missing": []},
            {"file": "bad.md", "drift_score": 0.2, "missing": ["x", "y"]},
        ]
        report = drift_mod.build_report(results, 0.33)
        assert "bad.md" in report["below_threshold"]
        assert "good.md" not in report["below_threshold"]

    def test_empty_results_no_division_error(self, drift_mod):
        """build_report handles empty agent list without division-by-zero."""
        report = drift_mod.build_report([], 0.33)
        assert report["fleet_avg"] == 0.0
        assert report["below_threshold"] == []


# ---------------------------------------------------------------------------
# Unit tests for format_summary
# ---------------------------------------------------------------------------


class TestFormatSummary:
    """Tests for human-readable summary output."""

    def test_summary_includes_score_and_file(self, drift_mod):
        """format_summary includes drift score and file name for each agent."""
        report = {
            "agents": [{"file": "agents/test.agent.md", "drift_score": 0.8, "missing": []}],
            "fleet_avg": 0.8,
            "below_threshold": [],
        }
        output = drift_mod.format_summary(report, 0.33)
        assert "test.agent.md" in output
        assert "0.80" in output

    def test_summary_warns_below_threshold(self, drift_mod):
        """format_summary marks below-threshold agents with WARN."""
        report = {
            "agents": [{"file": "low.agent.md", "drift_score": 0.17, "missing": ["x"]}],
            "fleet_avg": 0.17,
            "below_threshold": ["low.agent.md"],
        }
        output = drift_mod.format_summary(report, 0.33)
        assert "WARN" in output


# ---------------------------------------------------------------------------
# Integration tests for main()
# ---------------------------------------------------------------------------


class TestMain:
    """Tests for the main() entry point."""

    @pytest.mark.io
    def test_main_exits_0_with_valid_agents_dir(self, drift_mod, tmp_path, monkeypatch):
        """main() returns 0 when agents directory exists (even if empty)."""
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (tmp_path / "AGENTS.md").write_text("# Root\n")
        monkeypatch.setattr(sys, "argv", ["detect_drift.py", "--agents-dir", str(agents_dir)])
        ret = drift_mod.main()
        assert ret == 0

    @pytest.mark.io
    def test_main_exits_1_missing_agents_dir(self, drift_mod, tmp_path, monkeypatch):
        """main() returns 1 when --agents-dir does not exist."""
        monkeypatch.setattr(sys, "argv", ["detect_drift.py", "--agents-dir", str(tmp_path / "no-such")])
        ret = drift_mod.main()
        assert ret == 1

    @pytest.mark.io
    def test_main_fail_below_triggers_exit_1(self, drift_mod, tmp_path, monkeypatch):
        """main() returns 1 when agent score is below --fail-below threshold."""
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (tmp_path / "AGENTS.md").write_text("# Root\n")
        (agents_dir / "empty.agent.md").write_text("---\nname: Empty\ndescription: x\ntools: []\n---\nNo watermarks.\n")
        monkeypatch.setattr(
            sys,
            "argv",
            ["detect_drift.py", "--agents-dir", str(agents_dir), "--fail-below", "0.5"],
        )
        ret = drift_mod.main()
        assert ret == 1

    @pytest.mark.io
    def test_main_no_fail_below_exits_0_even_with_low_score(self, drift_mod, tmp_path, monkeypatch):
        """main() returns 0 when --fail-below is not set (advisory only)."""
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (tmp_path / "AGENTS.md").write_text("# Root\n")
        (agents_dir / "empty.agent.md").write_text("---\nname: Empty\ndescription: x\ntools: []\n---\nNo watermarks.\n")
        monkeypatch.setattr(sys, "argv", ["detect_drift.py", "--agents-dir", str(agents_dir)])
        ret = drift_mod.main()
        assert ret == 0

    @pytest.mark.io
    def test_main_json_output_schema(self, drift_mod, tmp_path, monkeypatch):
        """main() JSON output contains required top-level keys."""
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (tmp_path / "AGENTS.md").write_text("# Root\n")
        (agents_dir / "a.agent.md").write_text("---\nname: A\ndescription: x\ntools: []\n---\nEndogenous-First.\n")
        out_file = tmp_path / "report.json"
        monkeypatch.setattr(
            sys,
            "argv",
            ["detect_drift.py", "--agents-dir", str(agents_dir), "--output", str(out_file)],
        )
        ret = drift_mod.main()
        assert ret == 0
        data = json.loads(out_file.read_text())
        assert "agents" in data
        assert "fleet_avg" in data
        assert "below_threshold" in data

    @pytest.mark.io
    def test_main_summary_format(self, drift_mod, tmp_path, monkeypatch, capsys):
        """main() --format summary produces human-readable output."""
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (tmp_path / "AGENTS.md").write_text("# Root\n")
        (agents_dir / "s.agent.md").write_text(
            "---\nname: S\ndescription: x\ntools: []\n---\n"
            "Endogenous-First. Algorithms Before Tokens. Local Compute-First.\n"
        )
        monkeypatch.setattr(
            sys,
            "argv",
            ["detect_drift.py", "--agents-dir", str(agents_dir), "--format", "summary"],
        )
        ret = drift_mod.main()
        assert ret == 0
        captured = capsys.readouterr()
        assert "Fleet average" in captured.out

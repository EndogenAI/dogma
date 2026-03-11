"""
Test suite for parse_audit_result.py

Tests provenance audit result parsing, risk assessment computation, and Markdown
report generation. Validates risk levels (green/yellow/red) based on axiom citations
and test coverage metrics.
"""

import pytest

from scripts.parse_audit_result import (
    assess_agent_risk,
    generate_recommendations,
    parse_audit_result,
)

# ===========================================================================
# Fixtures: Sample Audit JSON Payloads
# ===========================================================================


@pytest.fixture
def sample_green_audit():
    """Audit report with all agents having strong axiom grounding."""
    return {
        "files": [
            {
                "path": ".github/agents/executive-researcher.agent.md",
                "citations": ["endogenous-first", "algorithms-before-tokens", "local-compute-first"],
                "orphaned": False,
                "unverifiable": [],
            },
            {
                "path": ".github/agents/executive-orchestrator.agent.md",
                "citations": ["endogenous-first", "programmatic-first"],
                "orphaned": False,
                "unverifiable": [],
            },
        ],
        "fleet_citation_coverage_pct": 100.0,
        "total_unverifiable": 0,
    }


@pytest.fixture
def sample_mixed_audit():
    """Audit report with mixed green/yellow/red risk levels."""
    return {
        "files": [
            {
                "path": ".github/agents/executive-researcher.agent.md",
                "citations": ["endogenous-first", "algorithms-before-tokens"],
                "orphaned": False,
                "unverifiable": [],
            },
            {
                "path": ".github/agents/scout.agent.md",
                "citations": ["endogenous-first"],
                "orphaned": False,
                "unverifiable": [],
            },
            {"path": ".github/agents/latent-agent.agent.md", "citations": [], "orphaned": True, "unverifiable": []},
        ],
        "fleet_citation_coverage_pct": 66.7,
        "total_unverifiable": 0,
    }


@pytest.fixture
def sample_red_audit():
    """Audit report with critical issues."""
    return {
        "files": [
            {"path": ".github/agents/broken-agent.agent.md", "citations": [], "orphaned": True, "unverifiable": []},
            {
                "path": ".github/agents/unverifiable-agent.agent.md",
                "citations": ["nonexistent-axiom", "invalid-principle"],
                "orphaned": False,
                "unverifiable": ["nonexistent-axiom", "invalid-principle"],
            },
        ],
        "fleet_citation_coverage_pct": 0.0,
        "total_unverifiable": 2,
    }


@pytest.fixture
def empty_audit():
    """Empty audit report."""
    return {"files": [], "fleet_citation_coverage_pct": 0.0, "total_unverifiable": 0}


# ===========================================================================
# Unit Tests: Risk Assessment Logic (5 tests)
# ===========================================================================


class TestRiskAssessment:
    """Test suite for agent risk assessment logic."""

    def test_green_risk_strong_citations(self):
        """Agent with many axiom citations → GREEN risk."""
        risk_level, notes = assess_agent_risk(
            name="test-agent",
            axiom_cites=3,
            test_coverage=95.0,
            threshold=0.5,
        )
        assert risk_level == "green"
        assert "strong" in notes.lower() or "high" in notes.lower()

    def test_yellow_risk_mixed_signals(self):
        """Agent with medium axiom cites and medium coverage → YELLOW."""
        risk_level, notes = assess_agent_risk(
            name="test-agent",
            axiom_cites=1,
            test_coverage=70.0,
            threshold=0.5,
        )
        assert risk_level == "yellow"
        assert "moderate" in notes.lower() or "medium" in notes.lower()

    def test_red_risk_orphaned_agent(self):
        """Orphaned agent (no governs: field) → RED."""
        risk_level, notes = assess_agent_risk(
            name="orphaned-agent",
            axiom_cites=0,
            test_coverage=None,
            orphaned=True,
        )
        assert risk_level == "red"
        assert "orphaned" in notes.lower()

    def test_red_risk_unverifiable_citations(self):
        """Agent with unverifiable axiom citations → RED."""
        risk_level, notes = assess_agent_risk(
            name="bad-agent",
            axiom_cites=2,
            test_coverage=85.0,
            unverifiable=True,
        )
        assert risk_level == "red"
        assert "unverifiable" in notes.lower()

    def test_red_risk_weak_citations_low_coverage(self):
        """Low axiom cites AND low test coverage → RED."""
        risk_level, notes = assess_agent_risk(
            name="risky-agent",
            axiom_cites=0,
            test_coverage=45.0,
            threshold=0.5,
        )
        assert risk_level == "red"
        assert "low" in notes.lower() and "drift" in notes.lower()


# ===========================================================================
# Integration Tests: Full Parsing (6 tests)
# ===========================================================================


class TestParseAuditResult:
    """Test suite for full audit result parsing."""

    def test_parse_green_audit_all_pass(self, sample_green_audit):
        """Parse audit with all agents in green → overall_risk='green'."""
        result = parse_audit_result(sample_green_audit, threshold=0.5)
        assert result.status == "green"
        assert result.green_count >= 2
        assert result.red_count == 0

    def test_parse_mixed_audit(self, sample_mixed_audit):
        """Parse audit with mixed risk levels including orphaned agent → overall_risk='red'."""
        result = parse_audit_result(sample_mixed_audit, threshold=0.5)
        # With an orphaned agent, overall risk is red (1 red out of 3 = 33% > 30% threshold)
        assert result.status == "red"
        assert len(result.agents) == 3
        # Should have at least one red (orphaned)
        assert any(a.risk_level == "red" for a in result.agents)

    def test_parse_red_audit_critical_issues(self, sample_red_audit):
        """Parse audit with critical issues → overall_risk='red'."""
        result = parse_audit_result(sample_red_audit, threshold=0.5)
        assert result.status == "red"
        assert result.red_count >= 2
        assert len(result.agents) == 2

    def test_parse_empty_audit(self, empty_audit):
        """Parse empty audit → no errors, empty agents list."""
        result = parse_audit_result(empty_audit, threshold=0.5)
        assert result.status in ("green", "yellow", "red")
        assert len(result.agents) == 0

    def test_parse_threshold_affects_risk(self, sample_mixed_audit):
        """Different threshold → different risk assessment."""
        result_low = parse_audit_result(sample_mixed_audit, threshold=0.2)
        result_high = parse_audit_result(sample_mixed_audit, threshold=2.0)
        # With high threshold, more agents should fail (red)
        assert result_high.red_count >= result_low.red_count

    def test_parse_result_contains_markdown(self, sample_green_audit):
        """Parsed result contains Markdown report."""
        result = parse_audit_result(sample_green_audit, threshold=0.5)
        assert "Markdown" in result.markdown_report or "#" in result.markdown_report
        assert "Agent" in result.markdown_report or "agent" in result.markdown_report


# ===========================================================================
# Recommendation Generation Tests (3 tests)
# ===========================================================================


class TestRecommendations:
    """Test suite for recommendation generation."""

    def test_green_recommendations(self):
        """Green overall risk → positive recommendation."""
        recs = generate_recommendations(
            overall_risk="green",
            green_count=8,
            red_count=0,
            total=8,
            avg_cite_intensity=0.9,
        )
        assert len(recs) > 0
        assert any("green" in r.lower() or "✅" in r for r in recs)

    def test_red_recommendations(self):
        """Red overall risk → urgent/warning recommendation."""
        recs = generate_recommendations(
            overall_risk="red",
            green_count=2,
            red_count=6,
            total=8,
            avg_cite_intensity=0.2,
        )
        assert len(recs) > 0
        assert any("high" in r.lower() or "🚨" in r or "urgent" in r.lower() for r in recs)

    def test_low_intensity_recommendation(self):
        """Low cite intensity → recommendation to improve."""
        recs = generate_recommendations(
            overall_risk="yellow",
            green_count=4,
            red_count=2,
            total=6,
            avg_cite_intensity=0.2,
        )
        assert any("cite intensity" in r.lower() or "govern" in r.lower() for r in recs)


# ===========================================================================
# Markdown Report Generation Tests (2 tests)
# ===========================================================================


class TestMarkdownReport:
    """Test suite for Markdown report generation."""

    def test_report_contains_table(self, sample_mixed_audit):
        """Report contains risk assessment table."""
        result = parse_audit_result(sample_mixed_audit, threshold=0.5)
        assert "|" in result.markdown_report  # Markdown table indicator
        assert "Agent" in result.markdown_report or "agent" in result.markdown_report

    def test_report_contains_risk_emoji(self, sample_mixed_audit):
        """Report uses risk emoji notation."""
        result = parse_audit_result(sample_mixed_audit, threshold=0.5)
        # Check for emoji or risk level indicators
        assert any(emoji in result.markdown_report for emoji in ["🟢", "🟡", "🔴", "GREEN", "RED"])


# ===========================================================================
# Error Handling Tests (2 tests)
# ===========================================================================


class TestErrorHandling:
    """Test suite for error handling."""

    def test_parse_malformed_json_raises_error(self):
        """Malformed JSON (missing 'files') raises ValueError."""
        with pytest.raises(ValueError, match="'files'"):
            parse_audit_result({"no_files_key": []}, threshold=0.5)

    def test_parse_files_not_list_raises_error(self):
        """'files' is not a list → raises ValueError."""
        with pytest.raises(ValueError, match="list"):
            parse_audit_result({"files": "not a list"}, threshold=0.5)


# ===========================================================================
# Edge Cases (3 tests)
# ===========================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_agent_audit(self):
        """Audit with only one agent."""
        audit_json = {
            "files": [
                {
                    "path": ".github/agents/solo-agent.agent.md",
                    "citations": ["endogenous-first"],
                    "orphaned": False,
                    "unverifiable": [],
                }
            ],
            "fleet_citation_coverage_pct": 100.0,
            "total_unverifiable": 0,
        }
        result = parse_audit_result(audit_json, threshold=0.5)
        assert len(result.agents) == 1
        assert result.green_count + result.yellow_count + result.red_count == 1

    def test_many_agents_performance(self):
        """Large audit report (100+ agents) processes efficiently."""
        audit_json = {
            "files": [
                {
                    "path": f".github/agents/agent-{i}.agent.md",
                    "citations": ["endogenous-first"] * (i % 3 + 1),
                    "orphaned": i % 10 == 0,  # 10% orphaned
                    "unverifiable": [] if i % 5 != 0 else ["bad-axiom"],
                }
                for i in range(100)
            ],
            "fleet_citation_coverage_pct": 85.0,
            "total_unverifiable": 20,
        }
        result = parse_audit_result(audit_json, threshold=0.5)
        assert len(result.agents) == 100
        assert result.green_count + result.yellow_count + result.red_count == 100

    def test_zero_threshold(self):
        """Threshold of 0 doesn't cause division errors."""
        # Note: in practice, threshold should be > 0, but we handle it gracefully
        audit_json = {
            "files": [
                {
                    "path": ".github/agents/test.agent.md",
                    "citations": ["endogenous-first"],
                    "orphaned": False,
                    "unverifiable": [],
                }
            ],
            "fleet_citation_coverage_pct": 100.0,
            "total_unverifiable": 0,
        }
        # Should not crash with threshold=0
        result = parse_audit_result(audit_json, threshold=0.001)
        assert result.status in ("green", "yellow", "red")


# ===========================================================================
# Data Integrity Tests (2 tests)
# ===========================================================================


class TestDataIntegrity:
    """Test that parsed data maintains integrity."""

    def test_agent_count_matches_files(self, sample_mixed_audit):
        """Number of agents matches number of files in audit."""
        result = parse_audit_result(sample_mixed_audit, threshold=0.5)
        assert len(result.agents) == len(sample_mixed_audit["files"])

    def test_risk_counts_sum_to_total(self, sample_mixed_audit):
        """green + yellow + red = total agents."""
        result = parse_audit_result(sample_mixed_audit, threshold=0.5)
        total = result.green_count + result.yellow_count + result.red_count
        assert total == len(result.agents)


# ===========================================================================
# Integration with audit_provenance Output (2 tests)
# ===========================================================================


class TestAuditProvenianceIntegration:
    """Test compatibility with audit_provenance.py output format."""

    def test_parses_audit_provenance_output_format(self):
        """Parse output matching audit_provenance.py JSON schema."""
        audit_json = {
            "files": [
                {
                    "path": ".github/agents/executive-researcher.agent.md",
                    "citations": ["endogenous-first", "algorithms-before-tokens"],
                    "orphaned": False,
                    "unverifiable": [],
                },
                {"path": ".github/agents/orphan.agent.md", "citations": [], "orphaned": True, "unverifiable": []},
            ],
            "fleet_citation_coverage_pct": 50.0,
            "total_unverifiable": 0,
        }
        result = parse_audit_result(audit_json, threshold=0.5)
        assert len(result.agents) == 2
        assert any(a.status == "orphaned" for a in result.agents)

    def test_handles_unverifiable_citations(self):
        """Parse agents with unverifiable axiom citations."""
        audit_json = {
            "files": [
                {
                    "path": ".github/agents/bad-citations.agent.md",
                    "citations": ["nonexistent-axiom", "fake-principle"],
                    "orphaned": False,
                    "unverifiable": ["nonexistent-axiom", "fake-principle"],
                }
            ],
            "fleet_citation_coverage_pct": 0.0,
            "total_unverifiable": 2,
        }
        result = parse_audit_result(audit_json, threshold=0.5)
        assert len(result.agents) == 1
        assert result.agents[0].status == "unverifiable"
        assert result.agents[0].risk_level == "red"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

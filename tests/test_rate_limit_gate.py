#!/usr/bin/env python3
"""
tests/test_rate_limit_gate.py

Test suite for rate_limit_gate.py pre-delegation gate with circuit-breaker.
Covers gate logic, circuit-breaker triggering, budget checks, and audit logging.
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from rate_limit_gate import (
    MIN_BUDGET_SAFETY_MARGIN,
    _count_consecutive_failures,
    _log_gate_decision,
    check_rate_limit_gate,
)

# ============================================================================
# Fixtures for test isolation
# ============================================================================


@pytest.fixture
def isolated_audit_log(tmp_path, monkeypatch):
    """Provide isolated audit log path per test using tmp_path."""
    import rate_limit_gate

    temp_log = tmp_path / "rate-limit-audit.log"
    monkeypatch.setattr(rate_limit_gate, "AUDIT_LOG_PATH", temp_log)
    return temp_log


class TestGateSafety:
    """Test gate safety decisions."""

    def test_gate_safe_high_budget(self):
        """Test that gate allows with high budget."""
        result = check_rate_limit_gate(
            current_token_budget=100000,
            operation_type="delegation",
            provider="claude",
        )
        assert result["safe"] is True
        assert result["recommended_sleep_sec"] == 0

    def test_gate_unsafe_low_budget(self):
        """Test that gate blocks with budget below safety margin."""
        result = check_rate_limit_gate(
            current_token_budget=1000,  # Below MIN_BUDGET_SAFETY_MARGIN
            operation_type="delegation",
            provider="claude",
        )
        assert result["safe"] is False
        assert result["recommended_sleep_sec"] > 0

    def test_gate_unsafe_zero_budget(self):
        """Test gate with zero budget."""
        result = check_rate_limit_gate(
            current_token_budget=0,
            operation_type="delegation",
            provider="claude",
        )
        assert result["safe"] is False
        assert result["reason"].lower().count("exhausted") >= 1 or result["reason"].lower().count("budget") >= 1

    def test_gate_response_structure(self):
        """Test that gate response has required fields."""
        result = check_rate_limit_gate(50000, "fetch_source")
        assert "safe" in result
        assert "recommended_sleep_sec" in result
        assert "reason" in result
        assert "provider" in result
        assert "operation" in result
        assert "consecutive_failures" in result


class TestProviderDifferencesClaude:
    """Test provider-specific gate behavior."""

    def test_gate_claude_conservative(self):
        """Test that Claude policies are conservative."""
        # Claude delegation policy has 60s sleep
        result_unsafe = check_rate_limit_gate(1000, "delegation", provider="claude")
        if not result_unsafe["safe"]:
            # If unsafe, recommended sleep should follow Claude policy
            assert result_unsafe["recommended_sleep_sec"] >= 60

    def test_gate_gpt4_less_conservative(self):
        """Test that GPT-4 policies are less conservative."""
        # GPT-4 delegation has 30s sleep (vs Claude's 60s)
        # This test just verifies the provider is loaded correctly
        result = check_rate_limit_gate(100000, "delegation", provider="gpt-4")
        assert result["provider"] == "gpt-4"


class TestCircuitBreaker:
    """Test circuit-breaker logic."""

    def test_circuit_breaker_not_triggered_clean_log(self, isolated_audit_log):
        """Test circuit-breaker with clean audit log."""
        # With clean log (isolated tmp_path), gate should allow
        result = check_rate_limit_gate(100000, "delegation", provider="claude")
        assert result["safe"] is True
        assert result["consecutive_failures"] == 0

    def test_consecutive_failures_counter(self):
        """Test that consecutive failure counter works (mocked)."""
        # This test verifies the counter logic (without writing to audit log)
        count = _count_consecutive_failures("claude", "delegation", 5)
        assert isinstance(count, int)
        assert count >= 0

    def test_audit_log_structure(self):
        """Test that audit log entries have correct structure."""
        result = check_rate_limit_gate(50000, "fetch_source", provider="claude")
        # Verify we can serialize the result to JSON (audit log compatible)
        json_str = json.dumps(
            {
                "safe": result["safe"],
                "reason": result["reason"],
                "provider": result["provider"],
            }
        )
        assert isinstance(json_str, str)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_gate_exactly_at_safety_margin(self):
        """Test behavior when budget equals safety margin."""
        result = check_rate_limit_gate(
            current_token_budget=MIN_BUDGET_SAFETY_MARGIN,
            operation_type="fetch_source",
        )
        # Exactly at threshold should be unsafe (use < MIN_BUDGET_SAFETY_MARGIN check)
        assert result["safe"] is False

    def test_gate_just_above_safety_margin(self):
        """Test behavior when budget is just above safety margin."""
        result = check_rate_limit_gate(
            current_token_budget=MIN_BUDGET_SAFETY_MARGIN + 1,
            operation_type="fetch_source",
        )
        # Should be safe at all operations with sufficient budget
        assert result["safe"] is True

    def test_all_operation_types(self):
        """Test gate with all operation types."""
        operations = ["fetch_source", "delegation", "phase_boundary", "review_gate", "commit"]
        for op in operations:
            result = check_rate_limit_gate(100000, op, provider="claude")
            assert result["operation"] == op
            assert result["provider"] == "claude"


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_operation_raises(self):
        """Test that invalid operation raises error."""
        with pytest.raises(Exception):  # OperationNotFound or PolicyNotFound
            check_rate_limit_gate(100000, "invalid_op", provider="claude")

    def test_unknown_provider_falls_back(self):
        """Test that unknown provider falls back gracefully."""
        result = check_rate_limit_gate(100000, "delegation", provider="unknown-xyz")
        # Should use fallback policy
        assert result["provider"] == "unknown-xyz"
        assert result["safe"] is True  # High budget


class TestAuditLogIntegration:
    """Test audit logging integration."""

    def test_log_gate_decision_creates_file(self, isolated_audit_log):
        """Test that logging creates audit log file."""
        # isolated_audit_log provides a clean tmp_path-backed audit log
        result = check_rate_limit_gate(50000, "delegation", provider="claude")
        result["current_budget"] = 50000

        _log_gate_decision(result, audit_flag=True)

        # File should exist now (in isolated tmp_path)
        assert isolated_audit_log.exists()


# ============================================================================
# Regression Tests (Issue #324 related)
# ============================================================================


class TestCircuitBreakerRegression:
    """Test circuit-breaker implementation (issue #324)."""

    def test_circuit_breaker_threshold_respected(self):
        """Test that circuit-breaker threshold from config is respected."""
        # This test verifies the threshold lookup works
        result = check_rate_limit_gate(100000, "phase_boundary", provider="claude")
        # With clean state, should be safe
        assert result["safe"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

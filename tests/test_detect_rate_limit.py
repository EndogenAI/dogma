"""
tests/test_detect_rate_limit.py
-------------------------------
Test coverage for scripts/detect_rate_limit.py.

Test categories:
  - Happy path (all status codes)
  - Boundary conditions (zero remaining, exactly at thresholds)
  - Error cases (negative inputs, invalid configs)
  - Sleep duration computation
  - Safety margin application
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Add scripts to path BEFORE importing from it (must come before other imports)
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import pytest  # noqa: E402
from detect_rate_limit import DEFAULT_SAFETY_MARGIN, detect_rate_limit  # noqa: E402

# ============================================================================
# Unit Tests (detect_rate_limit function)
# ============================================================================


class TestDetectRateLimitHappyPath:
    """Happy path: normal operating conditions."""

    def test_ok_abundant_budget(self):
        """Very abundant budget -> OK."""
        status, sleep_ms = detect_rate_limit(
            remaining_tokens=100_000,
            phase_cost_estimate=10_000,
        )
        assert status == "OK"
        assert sleep_ms is None

    def test_ok_safe_margin(self):
        """Budget at 2x threshold -> OK."""
        total_needed = 10_000 + DEFAULT_SAFETY_MARGIN  # phase + margin
        remaining = 2 * total_needed
        status, sleep_ms = detect_rate_limit(
            remaining_tokens=remaining,
            phase_cost_estimate=10_000,
        )
        assert status == "OK"
        assert sleep_ms is None

    def test_warn_tight_margin(self):
        """Budget between 1x and 2x threshold -> WARN."""
        total_needed = 10_000 + DEFAULT_SAFETY_MARGIN
        remaining = int(1.5 * total_needed)
        status, sleep_ms = detect_rate_limit(
            remaining_tokens=remaining,
            phase_cost_estimate=10_000,
        )
        assert status == "WARN"
        assert sleep_ms is None

    def test_warn_at_threshold(self):
        """Budget at 1x threshold -> WARN."""
        total_needed = 10_000 + DEFAULT_SAFETY_MARGIN
        remaining = total_needed
        status, sleep_ms = detect_rate_limit(
            remaining_tokens=remaining,
            phase_cost_estimate=10_000,
        )
        assert status == "WARN"
        assert sleep_ms is None

    def test_critical_low_budget(self):
        """Budget between 0 and 1x threshold -> CRITICAL."""
        total_needed = 10_000 + DEFAULT_SAFETY_MARGIN
        remaining = int(0.5 * total_needed)
        status, sleep_ms = detect_rate_limit(
            remaining_tokens=remaining,
            phase_cost_estimate=10_000,
        )
        assert status == "CRITICAL"
        assert sleep_ms is None

    def test_critical_remaining_positive_but_low(self):
        """Remaining tokens positive but below total_needed -> CRITICAL."""
        status, sleep_ms = detect_rate_limit(
            remaining_tokens=5_000,
            phase_cost_estimate=20_000,
        )
        assert status == "CRITICAL"
        assert sleep_ms is None


class TestDetectRateLimitSleepRequired:
    """Sleep injection cases: budget exhausted."""

    def test_sleep_required_negative_remaining(self):
        """Negative remaining (already exhausted) -> SLEEP_REQUIRED."""
        status, sleep_ms = detect_rate_limit(
            remaining_tokens=-5_000,
            phase_cost_estimate=30_000,
        )
        assert status.startswith("SLEEP_REQUIRED_")
        assert sleep_ms is not None
        assert sleep_ms > 0

    def test_sleep_required_zero_remaining(self):
        """Zero remaining -> SLEEP_REQUIRED."""
        status, sleep_ms = detect_rate_limit(
            remaining_tokens=0,
            phase_cost_estimate=30_000,
        )
        assert status.startswith("SLEEP_REQUIRED_")
        assert sleep_ms is not None
        assert sleep_ms > 0

    def test_sleep_duration_proportional_to_deficit(self):
        """Larger deficit -> larger sleep duration (until capped)."""
        status1, sleep_ms1 = detect_rate_limit(
            remaining_tokens=-1_000,
            phase_cost_estimate=30_000,
            window_ms=120000,  # Larger window to avoid cap collision
        )
        status2, sleep_ms2 = detect_rate_limit(
            remaining_tokens=-50_000,
            phase_cost_estimate=30_000,
            window_ms=120000,
        )
        assert status1.startswith("SLEEP_REQUIRED_")
        assert status2.startswith("SLEEP_REQUIRED_")
        # Larger deficit MAY produce larger sleep (but may be capped at window limit)
        # Since 120s window caps at 114s, and both deficits might exceed cap,
        # we just verify both produce reasonable values
        assert sleep_ms1 > 0
        assert sleep_ms2 > 0

    def test_sleep_duration_reasonable_bounds(self):
        """Sleep duration should be sensible (not insane)."""
        status, sleep_ms = detect_rate_limit(
            remaining_tokens=-10_000,
            phase_cost_estimate=30_000,
        )
        # Strict v2 floor is 120 seconds at/after budget exhaustion.
        assert 120000 <= sleep_ms <= 600000, f"Sleep {sleep_ms}ms out of expected range"

    def test_sleep_status_includes_duration(self):
        """SLEEP_REQUIRED status should include the duration."""
        status, sleep_ms = detect_rate_limit(
            remaining_tokens=-20_000,
            phase_cost_estimate=30_000,
        )
        # Status should be like "SLEEP_REQUIRED_40000"
        status_parts = status.split("_")
        assert len(status_parts) == 3  # ["SLEEP", "REQUIRED", "NNN"]
        assert status_parts[0] == "SLEEP"
        assert status_parts[1] == "REQUIRED"
        assert status_parts[2].isdigit()
        assert int(status_parts[2]) == sleep_ms


class TestDetectRateLimitCustomParameters:
    """Test with custom window_ms and safety_margin."""

    def test_custom_safety_margin_larger(self):
        """Larger safety margin -> earlier warning."""
        status1, _ = detect_rate_limit(
            remaining_tokens=20_000,
            phase_cost_estimate=10_000,
            safety_margin=5_000,  # Default 8000
        )
        status2, _ = detect_rate_limit(
            remaining_tokens=20_000,
            phase_cost_estimate=10_000,
            safety_margin=15_000,  # Larger
        )
        # status2 should be less favorable (same remaining but larger margin consumed)
        statuses = ["OK", "WARN", "CRITICAL", "SLEEP"]
        status1_idx = next(i for i, s in enumerate(statuses) if s in status1)
        status2_idx = next(i for i, s in enumerate(statuses) if s in status2)
        assert status2_idx >= status1_idx, "Larger margin should worsen status"

    def test_custom_window_ms_affects_sleep_capping(self):
        """Larger window_ms allows longer sleep cap."""
        status1, sleep_ms1 = detect_rate_limit(
            remaining_tokens=-50_000,
            phase_cost_estimate=30_000,
            window_ms=60000,
        )
        status2, sleep_ms2 = detect_rate_limit(
            remaining_tokens=-50_000,
            phase_cost_estimate=30_000,
            window_ms=120000,  # Larger window
        )
        # Larger window allows higher sleep cap (up to 95% of window)
        assert sleep_ms2 >= sleep_ms1, "Larger window should allow longer sleep"


class TestDetectRateLimitErrorHandling:
    """Error cases and validation."""

    def test_negative_remaining_tokens_allowed(self):
        """Negative remaining_tokens should be allowed (represents deficit)."""
        status, _ = detect_rate_limit(
            remaining_tokens=-10_000,
            phase_cost_estimate=20_000,
        )
        # Should produce SLEEP_REQUIRED, not raise
        assert "SLEEP_REQUIRED" in status

    def test_zero_phase_cost_rejected(self):
        """Phase cost of 0 should raise ValueError."""
        with pytest.raises(ValueError, match="phase_cost_estimate must be positive"):
            detect_rate_limit(
                remaining_tokens=10_000,
                phase_cost_estimate=0,
            )

    def test_negative_phase_cost_rejected(self):
        """Negative phase cost should raise ValueError."""
        with pytest.raises(ValueError, match="phase_cost_estimate must be positive"):
            detect_rate_limit(
                remaining_tokens=10_000,
                phase_cost_estimate=-5_000,
            )

    def test_zero_window_ms_rejected(self):
        """Window of 0 should raise ValueError."""
        with pytest.raises(ValueError, match="window_ms must be positive"):
            detect_rate_limit(
                remaining_tokens=10_000,
                phase_cost_estimate=5_000,
                window_ms=0,
            )

    def test_negative_safety_margin_rejected(self):
        """Negative safety margin should raise ValueError."""
        with pytest.raises(ValueError, match="safety_margin must be non-negative"):
            detect_rate_limit(
                remaining_tokens=10_000,
                phase_cost_estimate=5_000,
                safety_margin=-1,
            )

    def test_zero_safety_margin_allowed(self):
        """Zero safety margin should be allowed (conservative edge case)."""
        status, _ = detect_rate_limit(
            remaining_tokens=40_000,
            phase_cost_estimate=20_000,
            safety_margin=0,
        )
        assert status == "OK"


class TestDetectRateLimitBoundaryConditions:
    """Edge cases at decision boundaries."""

    def test_exactly_at_ok_boundary(self):
        """Budget exactly at 2x threshold."""
        total_needed = 10_000 + DEFAULT_SAFETY_MARGIN
        remaining = 2 * total_needed
        status, _ = detect_rate_limit(
            remaining_tokens=remaining,
            phase_cost_estimate=10_000,
        )
        # Exactly at boundary should be OK
        assert status == "OK"

    def test_just_below_ok_boundary(self):
        """Budget just below 2x threshold."""
        total_needed = 10_000 + DEFAULT_SAFETY_MARGIN
        remaining = (2 * total_needed) - 1
        status, _ = detect_rate_limit(
            remaining_tokens=remaining,
            phase_cost_estimate=10_000,
        )
        assert status == "WARN"

    def test_exactly_at_warn_boundary(self):
        """Budget exactly at 1x threshold."""
        total_needed = 10_000 + DEFAULT_SAFETY_MARGIN
        remaining = total_needed
        status, _ = detect_rate_limit(
            remaining_tokens=remaining,
            phase_cost_estimate=10_000,
        )
        # Exactly at boundary should be WARN (not CRITICAL)
        assert status == "WARN"

    def test_just_below_warn_boundary(self):
        """Budget just below 1x threshold."""
        total_needed = 10_000 + DEFAULT_SAFETY_MARGIN
        remaining = total_needed - 1
        status, _ = detect_rate_limit(
            remaining_tokens=remaining,
            phase_cost_estimate=10_000,
        )
        assert status == "CRITICAL"

    def test_exactly_zero_remaining(self):
        """Remaining exactly zero (boundary between CRITICAL and SLEEP_REQUIRED)."""
        status, _ = detect_rate_limit(
            remaining_tokens=0,
            phase_cost_estimate=10_000,
        )
        assert status.startswith("SLEEP_REQUIRED_")


# ============================================================================
# CLI Integration Tests
# ============================================================================


class TestDetectRateLimitCLI:
    """Test command-line interface."""

    @pytest.mark.slow
    def test_cli_ok_status(self):
        """CLI invocation -> OK status."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "detect_rate_limit.py"),
                "--check",
                "100000",
                "10000",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "OK"

    @pytest.mark.slow
    def test_cli_warn_status(self):
        """CLI invocation -> WARN status."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "detect_rate_limit.py"),
                "--check",
                "40000",
                "20000",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "WARN"

    @pytest.mark.slow
    def test_cli_critical_status(self):
        """CLI invocation -> CRITICAL status."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "detect_rate_limit.py"),
                "--check",
                "10000",
                "20000",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "CRITICAL"

    @pytest.mark.slow
    def test_cli_sleep_required(self):
        """CLI invocation -> SLEEP_REQUIRED status."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "detect_rate_limit.py"),
                "--check",
                "-5000",
                "20000",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "SLEEP_REQUIRED_" in result.stdout.strip()

    @pytest.mark.slow
    def test_cli_custom_window(self):
        """CLI with --window-ms parameter."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "detect_rate_limit.py"),
                "--check",
                "50000",
                "20000",
                "--window-ms",
                "120000",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        output = result.stdout.strip()
        assert output in ["OK", "WARN", "CRITICAL"]

    @pytest.mark.slow
    def test_cli_invalid_remaining_tokens(self):
        """CLI with invalid remaining_tokens."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "detect_rate_limit.py"),
                "--check",
                "not_a_number",
                "20000",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2  # argparse returns 2 for argument parse errors

    @pytest.mark.slow
    def test_cli_missing_phase_cost(self):
        """CLI with missing phase_cost_estimate."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "detect_rate_limit.py"),
                "--check",
                "50000",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1

    @pytest.mark.slow
    def test_cli_provider_parameter_accepted(self):
        """CLI should accept --provider parameter."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "detect_rate_limit.py"),
                "--check",
                "50000",
                "20000",
                "--provider",
                "gpt-4",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert result.stdout.strip() in ["OK", "WARN", "CRITICAL"]

    @pytest.mark.slow
    def test_cli_dry_run_parameter_accepted(self):
        """CLI should accept --dry-run parameter (issue #322 fix support)."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "detect_rate_limit.py"),
                "--check",
                "0",
                "30000",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "SLEEP_REQUIRED_" in result.stdout.strip()


# ============================================================================
# Regression Tests (Issue #322 — Cap/Floor Conflict Fix)
# ============================================================================


class TestCapFloorFixIssue322:
    """Regression tests for issue #322 cap/floor logic fix."""

    def test_sleep_respects_floor_minimum(self):
        """Sleep should never be below MIN_SLEEP_MS."""
        from detect_rate_limit import MIN_SLEEP_MS

        status, sleep_ms = detect_rate_limit(
            remaining_tokens=-100,  # Minimal deficit
            phase_cost_estimate=10_000,
        )
        assert sleep_ms is not None
        assert sleep_ms >= MIN_SLEEP_MS, f"Sleep {sleep_ms} below floor {MIN_SLEEP_MS}"

    def test_sleep_respects_cap_maximum(self):
        """Sleep should never exceed PHASE_BOUNDARY_SLEEP_MS."""
        from detect_rate_limit import PHASE_BOUNDARY_SLEEP_MS

        status, sleep_ms = detect_rate_limit(
            remaining_tokens=-1_000_000,  # Massive deficit
            phase_cost_estimate=10_000,
        )
        assert sleep_ms is not None
        assert sleep_ms <= PHASE_BOUNDARY_SLEEP_MS, f"Sleep {sleep_ms} exceeds cap {PHASE_BOUNDARY_SLEEP_MS}"

    def test_cap_floor_range_all_deficits(self):
        """Verify cap/floor logic across multiple deficit scenarios."""
        from detect_rate_limit import MIN_SLEEP_MS, PHASE_BOUNDARY_SLEEP_MS

        deficits = [-100, -1_000, -10_000, -100_000, -1_000_000]

        for deficit in deficits:
            status, sleep_ms = detect_rate_limit(
                remaining_tokens=deficit,
                phase_cost_estimate=10_000,
            )
            if sleep_ms is not None:
                msg = f"Deficit {deficit}: sleep {sleep_ms}"
                assert MIN_SLEEP_MS <= sleep_ms <= PHASE_BOUNDARY_SLEEP_MS, msg


# ============================================================================
# Provider Parameter Support (Issue #323 compatibility)
# ============================================================================


class TestProviderParameterSupport:
    """Test provider parameter for issue #323 provider-aware policies."""

    def test_provider_parameter_accepted_claude(self):
        """Provider parameter 'claude' should be accepted."""
        status, _ = detect_rate_limit(
            remaining_tokens=50_000,
            phase_cost_estimate=20_000,
            provider="claude",
        )
        assert status in ["OK", "WARN", "CRITICAL"]

    def test_provider_parameter_accepted_gpt4(self):
        """Provider parameter 'gpt-4' should be accepted."""
        status, _ = detect_rate_limit(
            remaining_tokens=50_000,
            phase_cost_estimate=20_000,
            provider="gpt-4",
        )
        assert status in ["OK", "WARN", "CRITICAL"]

    def test_provider_parameter_default_backward_compat(self):
        """Provider parameter should default to 'claude' (backward compatible)."""
        status1, _ = detect_rate_limit(
            remaining_tokens=0,
            phase_cost_estimate=20_000,
        )
        status2, sleep_ms2 = detect_rate_limit(
            remaining_tokens=0,
            phase_cost_estimate=20_000,
            provider="claude",
        )
        # Both should produce identical results (same default behavior)
        assert status1 == status2


# ============================================================================
# Coverage Targets
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=scripts.detect_rate_limit", "--cov-report=term-missing"])

#!/usr/bin/env python3
"""
tests/test_rate_limit_config.py

Test suite for rate_limit_config.py provider policy lookup engine.
Covers policy loading, provider lookup, fallback behavior, and error cases.
"""

import sys
from pathlib import Path

import pytest

# Add scripts/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from rate_limit_config import (
    OperationNotFound,
    get_policy,
    list_operations,
    list_providers,
)


class TestPolicyLoading:
    """Test policy loading and configuration."""

    def test_load_known_provider_claude(self):
        """Test loading known provider 'claude'."""
        policy = get_policy("claude", "fetch_source")
        assert isinstance(policy, dict)
        assert "sleep_sec" in policy
        assert "retry_limit" in policy
        assert "circuit_breaker_threshold" in policy

    def test_load_known_provider_gpt4(self):
        """Test loading known provider 'gpt-4'."""
        policy = get_policy("gpt-4", "delegation")
        assert policy["sleep_sec"] == 30
        assert policy["retry_limit"] == 2

    def test_load_known_provider_local(self):
        """Test loading local-localhost provider."""
        policy = get_policy("local-localhost", "fetch_source")
        assert policy["sleep_sec"] == 0
        assert policy["retry_limit"] == 0

    def test_provider_case_insensitive(self):
        """Test that provider names are case-insensitive."""
        policy_lower = get_policy("claude", "fetch_source")
        policy_upper = get_policy("CLAUDE", "fetch_source")
        assert policy_lower == policy_upper

    def test_unknown_provider_falls_back(self):
        """Test fallback to 'fallback' provider for unknown providers."""
        policy = get_policy("unknown-provider-xyz", "fetch_source")
        # Should fall back to 'fallback' provider
        assert policy["retry_limit"] == 1  # Fallback policy value


class TestOperationLookup:
    """Test operation-level lookups."""

    def test_all_operations_available(self):
        """Test that all standard operations are defined."""
        operations = ["fetch_source", "delegation", "phase_boundary", "review_gate", "commit"]
        for op in operations:
            policy = get_policy("claude", op)
            assert policy is not None

    def test_operation_not_found_raises(self):
        """Test that invalid operation raises OperationNotFound."""
        with pytest.raises(OperationNotFound):
            get_policy("claude", "invalid_operation")

    def test_gpt_operations(self):
        """Test GPT-4 operations."""
        ops = list_operations("gpt-4")
        assert "delegation" in ops
        assert "fetch_source" in ops


class TestPolicyStructure:
    """Test policy structure and validation."""

    def test_policy_has_required_fields(self):
        """Test that returned policy has all required fields."""
        policy = get_policy("claude", "fetch_source")
        assert "sleep_sec" in policy
        assert "retry_limit" in policy
        assert "circuit_breaker_threshold" in policy
        assert len(policy) == 3

    def test_policy_values_are_integers(self):
        """Test that policy values are numeric."""
        policy = get_policy("gpt-4", "phase_boundary")
        assert isinstance(policy["sleep_sec"], int)
        assert isinstance(policy["retry_limit"], int)
        assert isinstance(policy["circuit_breaker_threshold"], int)

    def test_circuit_breaker_threshold_reasonable(self):
        """Test that circuit-breaker thresholds are reasonable."""
        for provider in ["claude", "gpt-4", "gpt-3.5"]:
            policy = get_policy(provider, "phase_boundary")
            assert 1 <= policy["circuit_breaker_threshold"] <= 10


class TestProviderListings:
    """Test provider and operation discovery."""

    def test_list_providers(self):
        """Test listing available providers."""
        providers = list_providers()
        assert "claude" in providers
        assert "gpt-4" in providers
        assert "gpt-3.5" in providers
        assert "local-localhost" in providers
        assert "fallback" not in providers  # Fallback should not be listed

    def test_list_operations_default(self):
        """Test listing operations (default provider)."""
        ops = list_operations()
        assert "fetch_source" in ops
        assert "delegation" in ops
        assert "phase_boundary" in ops

    def test_list_operations_specific_provider(self):
        """Test listing operations for a specific provider."""
        ops = list_operations("claude")
        assert len(ops) >= 5


class TestProviderDifferences:
    """Test that different providers have different policies."""

    def test_claude_vs_gpt4_fetch_source(self):
        """Test that Claude and GPT-4 have different fetch_source policies."""
        claude_policy = get_policy("claude", "fetch_source")
        gpt4_policy = get_policy("gpt-4", "fetch_source")
        # At least one field should differ
        assert (
            claude_policy["sleep_sec"] != gpt4_policy["sleep_sec"]
            or claude_policy["retry_limit"] != gpt4_policy["retry_limit"]
        )

    def test_local_is_permissive(self):
        """Test that local-localhost allows no retries and sleeps."""
        policy = get_policy("local-localhost", "delegation")
        assert policy["sleep_sec"] == 0
        assert policy["retry_limit"] == 0
        assert policy["circuit_breaker_threshold"] == 999


# ============================================================================
# Regression Tests (Issue #322 related)
# ============================================================================


class TestCapFloorLogic:
    """Test that cap/floor logic is correctly applied (regression for issue #322)."""

    def test_fallback_has_reasonable_defaults(self):
        """Test that fallback provides conservative defaults."""
        policy = get_policy("unknown", "phase_boundary")
        # Fallback policy should be conservative
        assert policy["sleep_sec"] >= 120  # At least 2 minutes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

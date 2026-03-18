#!/usr/bin/env python3
"""
rate_limit_config.py
--------------------
Purpose:
    Load provider-specific rate-limit policies from data/rate-limit-profiles.yml
    and expose a single-entry-point policy lookup function.

    This module implements the provider policy engine for Sprint 18+
    (issue #323 — provider-aware rate-limit policy profiles).

Inputs:
    - data/rate-limit-profiles.yml (YAML file with provider definitions)
    - Provider name (e.g., 'claude', 'gpt-4')
    - Operation type (e.g., 'fetch_source', 'delegation', 'phase_boundary')

Outputs:
    - Policy dict: {sleep_sec, retry_limit, circuit_breaker_threshold}
    - Raises PolicyNotFound or OperationNotFound on lookup failure

Usage Examples:
    from rate_limit_config import get_policy

    # Get Claude policy for a source fetch
    policy = get_policy('claude', 'fetch_source')
    # Returns: {'sleep_sec': 30, 'retry_limit': 2, 'circuit_breaker_threshold': 4}

    # Get policy for unknown operation (raises OperationNotFound)
    policy = get_policy('gpt-4', 'unknown_op')  # Raises OperationNotFound

    # Get policy for unknown provider (falls back to 'fallback')
    policy = get_policy('unknown-provider', 'delegation')
    # Returns fallback policy for delegation

Exit Codes:
    N/A (library module; no CLI)

Notes:
    - Thread-safe: Config is loaded once at module import, not per-call
    - Fallback provider ('fallback' in profiles) used for unknown providers
    - Raises PolicyNotFound if provider not in config + fallback fails
    - Raises OperationNotFound if operation not in provider profile

Integration:
    - Called by rate_limit_gate.py before computing pre-delegation budgets
    - Supports dynamic provider discovery (no hardcoded list)
    - Based on research in docs/research/rate-limit-detection-api.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, TypedDict

import yaml

# ============================================================================
# Type Definitions
# ============================================================================


class RateLimitPolicy(TypedDict):
    """Single rate-limit policy for an operation."""

    sleep_sec: int
    retry_limit: int
    circuit_breaker_threshold: int


OperationType = Literal[
    "fetch_source",
    "delegation",
    "phase_boundary",
    "review_gate",
    "commit",
]

# ============================================================================
# Exceptions
# ============================================================================


class PolicyNotFound(Exception):
    """Raised when provider is not found (and fallback also fails)."""

    pass


class OperationNotFound(Exception):
    """Raised when operation is not defined for a provider."""

    pass


# ============================================================================
# Config Loading
# ============================================================================


def _load_profiles() -> dict:
    """Load rate-limit profiles from data/rate-limit-profiles.yml."""
    profile_path = Path(__file__).parent.parent / "data" / "rate-limit-profiles.yml"

    if not profile_path.exists():
        raise FileNotFoundError(f"rate-limit-profiles.yml not found at {profile_path}")

    with open(profile_path, "r") as f:
        data = yaml.safe_load(f)

    if not data or "providers" not in data:
        raise ValueError("rate-limit-profiles.yml must have a 'providers' key")

    # Load providers and merge in top-level fallback if present
    profiles = data["providers"].copy()
    if "fallback" in data:
        profiles["fallback"] = data["fallback"]
    return profiles


# Global profiles cache (loaded once at module import)
_PROFILES = _load_profiles()


# ============================================================================
# Public API
# ============================================================================


def get_policy(provider: str, operation: OperationType) -> RateLimitPolicy:
    """
    Look up a rate-limit policy for a given provider and operation.

    Args:
        provider: Provider name (e.g., 'claude', 'gpt-4', 'gpt-3.5', 'local-localhost')
        operation: Operation type (one of OperationType literal values)

    Returns:
        RateLimitPolicy: {sleep_sec, retry_limit, circuit_breaker_threshold}

    Raises:
        OperationNotFound: If operation is not defined for the provider
        PolicyNotFound: If provider is unknown and fallback also fails
    """

    # Normalize provider name (lowercase, strip whitespace)
    provider_normalized = provider.strip().lower()

    # Try to find provider in profiles
    if provider_normalized in _PROFILES:
        provider_data = _PROFILES[provider_normalized]
    else:
        # Fall back to 'fallback' provider if available
        if "fallback" not in _PROFILES:
            raise PolicyNotFound(f"Provider '{provider}' not found and no 'fallback' policy defined")
        provider_data = _PROFILES["fallback"]

    # Look up operation within the provider
    if "policies" not in provider_data:
        raise ValueError(f"Provider '{provider}' has no 'policies' key")

    policies = provider_data["policies"]
    if operation not in policies:
        available = ", ".join(sorted(policies.keys()))
        raise OperationNotFound(f"Operation '{operation}' not found for provider '{provider}'. Available: {available}")

    policy = policies[operation]

    # Validate policy structure
    required_fields = {"sleep_sec", "retry_limit", "circuit_breaker_threshold"}
    if not all(field in policy for field in required_fields):
        raise ValueError(
            f"Policy for provider '{provider}', operation '{operation}' "
            f"missing required fields: {required_fields - set(policy.keys())}"
        )

    return {
        "sleep_sec": policy["sleep_sec"],
        "retry_limit": policy["retry_limit"],
        "circuit_breaker_threshold": policy["circuit_breaker_threshold"],
    }


def list_providers() -> list[str]:
    """Return a list of available provider names (excluding 'fallback')."""
    return [name for name in _PROFILES.keys() if name != "fallback"]


def list_operations(provider: str | None = None) -> list[str]:
    """
    List available operations for a provider.

    Args:
        provider: Provider name. If None, returns operations from the first listed provider.

    Returns:
        List of operation names
    """
    if provider is None:
        # Use first provider that's not 'fallback'
        provider = next((name for name in _PROFILES.keys() if name != "fallback"), "fallback")

    provider_normalized = provider.strip().lower()
    if provider_normalized not in _PROFILES:
        raise PolicyNotFound(f"Provider '{provider}' not found")

    provider_data = _PROFILES[provider_normalized]
    if "policies" not in provider_data:
        return []

    return list(provider_data["policies"].keys())

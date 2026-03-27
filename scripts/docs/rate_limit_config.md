# `rate\_limit\_config`

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

## Usage

```bash
    from rate_limit_config import get_policy

    # Get Claude policy for a source fetch
    policy = get_policy('claude', 'fetch_source')
    # Returns: {'sleep_sec': 30, 'retry_limit': 2, 'circuit_breaker_threshold': 4}

    # Get policy for unknown operation (raises OperationNotFound)
    policy = get_policy('gpt-4', 'unknown_op')  # Raises OperationNotFound

    # Get policy for unknown provider (falls back to 'fallback')
    policy = get_policy('unknown-provider', 'delegation')
    # Returns fallback policy for delegation
```

<!-- hash:a9842f688b55232a -->

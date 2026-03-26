# `rate\_limit\_gate`

rate_limit_gate.py
------------------
Purpose:
    Pre-delegation rate-limit gate: check current budget and provider policy,
    recommend safe/unsafe decision for the next operation.

    Implements the circuit-breaker pattern for repeated rate-limit failures
    (issue #324 — adaptive escalation + circuit-breaker).

    Logs all gate decisions to audit trail if --audit-log flag is set.

Inputs:
    current_token_budget: Tokens remaining in current rate-limit window
    operation_type: Operation about to execute ('fetch_source', 'delegation', etc.)
    --provider: Provider name (default: 'claude')
    --audit-log: Log gate decision to scratchpad + .cache/rate-limit-audit.log

Outputs (stdout):
    JSON dict: {
        "safe": true|false,
        "recommended_sleep_sec": int,
        "reason": str,
        "provider": str,
        "operation": str,
    }

Exit Codes:
    0  Gate decision computed successfully
    1  Error (invalid args, config load failure)

Usage Examples:
    # Check if safe to proceed with delegation using 40k tokens
    uv run python scripts/rate_limit_gate.py 40000 delegation --provider claude

    # With audit logging
    uv run python scripts/rate_limit_gate.py 20000 phase_boundary --provider gpt-4 --audit-log

    # Without audit logging (default)
    uv run python scripts/rate_limit_gate.py 30000 fetch_source --provider claude

Notes:
    - Circuit-breaker: if N consecutive rate-limits in last M minutes, return safe=false
    - Audit log persists across sessions (append mode)
    - JSON output can be parsed by orchestrators for conditional logic
    - Backward compatible with detect_rate_limit.py (does not depend on it)

Integration:
    - Called by Executive Orchestrator before every delegation
    - Integrated into phase-gate-sequence.py at step 2 (pre-phase checkpoint)
    - Drives pre-delegation decision in orchestration loops
    - Based on research in docs/research/rate-limit-detection-api.md (Tier 2)

## Usage

```bash
    # Check if safe to proceed with delegation using 40k tokens
    uv run python scripts/rate_limit_gate.py 40000 delegation --provider claude

    # With audit logging
    uv run python scripts/rate_limit_gate.py 20000 phase_boundary --provider gpt-4 --audit-log

    # Without audit logging (default)
    uv run python scripts/rate_limit_gate.py 30000 fetch_source --provider claude
```

<!-- hash:ad7845ca561b4f87 -->

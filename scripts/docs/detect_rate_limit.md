# `detect\_rate\_limit`

detect_rate_limit.py
--------------------
Purpose:
    Detect approaching rate-limit exhaustion and recommend protective action
    (sleep injection, phase deferral). Parses provider-specific rate-limit semantics
    and estimates budget availability for the next delegation phase.

    Implements Tier 1 budget tracking from rate-limit-detection-api.md.
    Supports provider-aware policy profiles (issue #323).

Inputs (--check mode):
    remaining_tokens   — tokens available in current rate-limit window
    phase_cost_estimate — estimated tokens for the next phase (from historical prior_phase_costs)
    --provider         — provider name ('claude', 'gpt-4', 'gpt-3.5', 'local-localhost', default: 'claude')
    --window-ms        — rate-limit window duration in milliseconds (default: 60000)
    --safety-margin    — additional token buffer (default: 15000)

Outputs:
    Single line to stdout:
        OK                    — Sufficient budget (remaining > 2× total_needed)
        WARN                  — Tight budget (1× < remaining ≤ 2× total_needed)
        CRITICAL              — Low budget (0 < remaining ≤ 1× total_needed)
        SLEEP_REQUIRED_NNN    — Must sleep NNN milliseconds before proceeding
        ERROR_*               — Configuration or calculation error

Exit Codes:
    0  Action computed successfully (all statuses)
    1  Error (invalid arguments, calculation failure)

Usage Examples:
    # Check if 50k tokens remaining can support a 30k-token phase (backward compatible)
    uv run python scripts/detect_rate_limit.py --check 50000 30000
    # Output: OK

    # Check with provider parameter
    uv run python scripts/detect_rate_limit.py --check 40000 20000 --provider gpt-4

Notes:
    - Based on research in docs/research/rate-limit-detection-api.md
    - Tier 1: Simple token-based budgeting (immediate phase boundary check)
    - Tier 2+: Would add historical phase cost tracking and predictive modeling
    - All times in milliseconds for consistency with anthropic-sdk-py retry-after headers
    - Issue #322 fix: cap/floor logic now respects provider policies correctly (no strict max conflict)

## Usage

```bash
    # Check if 50k tokens remaining can support a 30k-token phase (backward compatible)
    uv run python scripts/detect_rate_limit.py --check 50000 30000
    # Output: OK

    # Check with provider parameter
    uv run python scripts/detect_rate_limit.py --check 40000 20000 --provider gpt-4
```

<!-- hash:23ed77255aabe30d -->

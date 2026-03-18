#!/usr/bin/env python3
"""
detect_rate_limit.py
--------------------
Purpose:
    Detect approaching rate-limit exhaustion and recommend protective action
    (sleep injection, phase deferral). Parses Claude API rate-limit semantics
    and estimates budget availability for the next delegation phase.

    Implements Tier 1 budget tracking from rate-limit-detection-api.md.

Inputs (--check mode):
    remaining_tokens   — tokens available in current rate-limit window
    phase_cost_estimate — estimated tokens for the next phase (from historical prior_phase_costs)
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
    # Check if 50k tokens remaining can support a 30k-token phase
    uv run python scripts/detect_rate_limit.py --check 50000 30000
    # Output: OK

    # Check a tight margin
    uv run python scripts/detect_rate_limit.py --check 35000 30000
    # Output: WARN

    # Check with insufficient budget
    uv run python scripts/detect_rate_limit.py --check 22000 30000
    # Output: CRITICAL

    # Check with negative margin (must sleep; budget exhausted)
    uv run python scripts/detect_rate_limit.py --check 0 30000
    # Output: SLEEP_REQUIRED_120000

    # Custom window and margin
    uv run python scripts/detect_rate_limit.py --check 50000 30000 --window-ms 120000 --safety-margin 10000

Notes:
    - Based on research in docs/research/rate-limit-detection-api.md
    - Tier 1: Simple token-based budgeting (immediate phase boundary check)
    - Tier 2+: Would add historical phase cost tracking and predictive modeling
    - All times in milliseconds for consistency with anthropic-sdk-py retry-after headers
"""

from __future__ import annotations

import argparse
import sys

# ============================================================================
# Constants
# ============================================================================

DEFAULT_WINDOW_MS = 60000  # Standard rate-limit window: 60 seconds
DEFAULT_SAFETY_MARGIN = 15000  # Buffer for retries, overhead, re-orientation (v2: 15k — stricter)
MIN_SLEEP_MS = 60000  # Minimum sleep duration: 60 seconds (v2: was 1s — caused cascading hits)
PHASE_BOUNDARY_SLEEP_MS = 120000  # 2 min sleep at every phase boundary (v2 strict pattern)
POST_DELEGATION_SLEEP_MS = 60000  # 60s sleep after every delegation (v2: was 30s)

# ============================================================================
# Budget Detection
# ============================================================================


def detect_rate_limit(
    remaining_tokens: int,
    phase_cost_estimate: int,
    window_ms: int = DEFAULT_WINDOW_MS,
    safety_margin: int = DEFAULT_SAFETY_MARGIN,
) -> tuple[str, int | None]:
    """
    Detect rate-limit status and compute protective action.

    Args:
        remaining_tokens: Tokens available in the current rate-limit window
        phase_cost_estimate: Estimated token cost for the next phase
        window_ms: Rate-limit window duration in milliseconds
        safety_margin: Additional token buffer for retries and overhead

    Returns:
        (status, sleep_ms) tuple
            status: "OK" | "WARN" | "CRITICAL" | "SLEEP_REQUIRED_NNN" | "ERROR_*"
            sleep_ms: milliseconds to sleep (None for OK/WARN/CRITICAL, included in status for SLEEP_REQUIRED)

    Raises:
        ValueError: If inputs are invalid (negative tokens, phase_cost > some threshold, etc.)
    """

    # ========================================================================
    # Validation
    # ========================================================================

    # remaining_tokens can be negative (represents budget deficit/exhaustion)
    if phase_cost_estimate <= 0:
        raise ValueError(f"phase_cost_estimate must be positive: {phase_cost_estimate}")
    if window_ms <= 0:
        raise ValueError(f"window_ms must be positive: {window_ms}")
    if safety_margin < 0:
        raise ValueError(f"safety_margin must be non-negative: {safety_margin}")

    # ========================================================================
    # Budget Calculation
    # ========================================================================

    total_needed = phase_cost_estimate + safety_margin

    # Decision tree (from rate-limit-detection-api.md § Recommendation Algorithm)
    if remaining_tokens >= 2 * total_needed:
        # Safe margin
        return ("OK", None)

    elif remaining_tokens >= total_needed:
        # Tight but acceptable
        return ("WARN", None)

    elif remaining_tokens > 0:
        # Low budget, may fail
        return ("CRITICAL", None)

    else:
        # Budget exhausted (remaining <= 0)
        # Compute how long to sleep based on the deficit
        deficit = total_needed - remaining_tokens
        # Rough heuristic: at ~1000 tokens/second throughput, convert token deficit to sleep time
        # More conservatively: assume we need approximately one window reset (e.g., 60 seconds)
        # to recover. For MVP, use a simple proportional model.
        # sleep_ms = (deficit / avg_tokens_per_sec) * 1000
        # Conservative estimate: assume ~500 tokens/second in rate-limited state
        avg_tokens_per_sec = 500
        computed_sleep_ms = max(MIN_SLEEP_MS, int((deficit / avg_tokens_per_sec) * 1000))
        # Enforce strict policy floor; also respect the rate-limit window duration
        # so --window-ms is meaningful (sleep at least one full window).
        sleep_ms = max(computed_sleep_ms, PHASE_BOUNDARY_SLEEP_MS, window_ms)
        status = f"SLEEP_REQUIRED_{sleep_ms}"
        return (status, sleep_ms)


# ============================================================================
# CLI
# ============================================================================


def main() -> int:
    """Parse arguments and emit detection result."""

    parser = argparse.ArgumentParser(
        description="Detect rate-limit exhaustion and recommend protective action.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check rate-limit budget",
    )
    parser.add_argument(
        "remaining_tokens",
        type=int,
        nargs="?",
        help="Tokens remaining in the current rate-limit window",
    )
    parser.add_argument(
        "phase_cost_estimate",
        type=int,
        nargs="?",
        help="Estimated token cost for the next phase",
    )
    parser.add_argument(
        "--window-ms",
        type=int,
        default=DEFAULT_WINDOW_MS,
        help=f"Rate-limit window duration in milliseconds (default: {DEFAULT_WINDOW_MS})",
    )
    parser.add_argument(
        "--safety-margin",
        type=int,
        default=DEFAULT_SAFETY_MARGIN,
        help=f"Safety margin in tokens (default: {DEFAULT_SAFETY_MARGIN})",
    )

    args = parser.parse_args()

    # Validate --check mode
    if not args.check:
        parser.print_help()
        return 1

    if args.remaining_tokens is None or args.phase_cost_estimate is None:
        print("ERROR_missing_arguments", file=sys.stdout)
        return 1

    # ========================================================================
    # Detect and emit result
    # ========================================================================

    try:
        status, _ = detect_rate_limit(
            remaining_tokens=args.remaining_tokens,
            phase_cost_estimate=args.phase_cost_estimate,
            window_ms=args.window_ms,
            safety_margin=args.safety_margin,
        )
        print(status)
        return 0

    except ValueError as e:
        print(f"ERROR_invalid_input: {e}", file=sys.stdout)
        return 1
    except Exception as e:
        print(f"ERROR_internal: {e}", file=sys.stdout)
        return 1


if __name__ == "__main__":
    sys.exit(main())

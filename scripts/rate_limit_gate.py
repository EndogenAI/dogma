#!/usr/bin/env python3
"""
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

    # Dry-run mode (shows what would be logged without side effects)
    uv run python scripts/rate_limit_gate.py 30000 fetch_source --provider claude --dry-run

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
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from rate_limit_config import OperationNotFound, OperationType, PolicyNotFound, get_policy

# ============================================================================
# Constants
# ============================================================================

AUDIT_LOG_PATH = Path(__file__).parent.parent / ".cache" / "rate-limit-audit.log"
CIRCUIT_BREAKER_WINDOW_MIN = 5  # Look back 5 minutes for consecutive failures
MIN_BUDGET_SAFETY_MARGIN = 5000  # Reserve 5k tokens for overhead


# ============================================================================
# Circuit Breaker
# ============================================================================


def _read_audit_log() -> list[dict]:
    """Read existing audit log entries."""
    if not AUDIT_LOG_PATH.exists():
        return []

    entries = []
    try:
        with open(AUDIT_LOG_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass  # Skip malformed lines
    except Exception:
        pass  # Non-fatal log read failure

    return entries


def _count_consecutive_failures(provider: str, operation: str, threshold_minutes: int) -> int:
    """
    Count consecutive rate-limit failures in recent audit log.

    Scans the audit log from most recent backward and counts consecutive entries where:
    - provider matches the given provider
    - operation matches the given operation
    - decision is 'rate_limit_blocked' (circuit-breaker triggered, not safe)

    Stops counting on the first non-matching entry OR entry outside the time window.
    NOTE: This counts consecutive failures for the SAME provider/operation combination.
    If different operations are interspersed, the count resets.

    Returns the count of consecutive "rate_limit_blocked" entries within threshold_minutes.
    """
    entries = _read_audit_log()
    if not entries:
        return 0

    cutoff_time = datetime.now() - timedelta(minutes=threshold_minutes)
    consecutive_count = 0

    # Scan from most recent backward, count consecutive "rate_limit_blocked" entries
    for entry in reversed(entries):
        try:
            entry_time = datetime.fromisoformat(entry.get("timestamp", "1970-01-01T00:00:00"))
            if entry_time < cutoff_time:
                break

            if (
                entry.get("provider") == provider
                and entry.get("operation") == operation
                and entry.get("decision") == "rate_limit_blocked"
            ):
                consecutive_count += 1
            else:
                # Break on first non-matching or non-rate-limit entry
                # This ensures we only count consecutive failures, not all-time failures
                break
        except (ValueError, KeyError):
            pass

    return consecutive_count


# ============================================================================
# Gate Logic
# ============================================================================


def check_rate_limit_gate(
    current_token_budget: int,
    operation_type: OperationType,
    provider: str = "claude",
) -> dict[str, Any]:
    """
    Check whether it's safe to proceed with an operation.

    Args:
        current_token_budget: Tokens available in current window
        operation_type: Type of operation to check
        provider: Provider name (default: 'claude')

    Returns:
        {
            "safe": bool,
            "recommended_sleep_sec": int,
            "reason": str,
            "provider": str,
            "operation": str,
            "consecutive_failures": int,
        }

    Raises:
        OperationNotFound: If operation is not in provider policy
        PolicyNotFound: If provider not found and no fallback
    """

    # Load policy
    try:
        policy = get_policy(provider, operation_type)
    except (OperationNotFound, PolicyNotFound) as e:
        raise type(e)(f"Failed to load policy: {e}") from e

    # Check circuit breaker
    consecutive_failures = _count_consecutive_failures(
        provider,
        operation_type,
        CIRCUIT_BREAKER_WINDOW_MIN,
    )
    circuit_breaker_threshold = policy["circuit_breaker_threshold"]

    if consecutive_failures >= circuit_breaker_threshold:
        return {
            "safe": False,
            "recommended_sleep_sec": policy["sleep_sec"] * 2,  # Double sleep for circuit break
            "reason": (
                f"Circuit breaker triggered: {consecutive_failures} consecutive"
                f" failures in last {CIRCUIT_BREAKER_WINDOW_MIN}min"
            ),
            "provider": provider,
            "operation": operation_type,
            "consecutive_failures": consecutive_failures,
        }

    # Check budget (≤ to treat exactly-at-margin as exhausted — margin must be reserved)
    if current_token_budget <= MIN_BUDGET_SAFETY_MARGIN:
        return {
            "safe": False,
            "recommended_sleep_sec": policy["sleep_sec"],
            "reason": f"Budget exhausted: {current_token_budget} <= {MIN_BUDGET_SAFETY_MARGIN}",
            "provider": provider,
            "operation": operation_type,
            "consecutive_failures": consecutive_failures,
        }

    # Safe to proceed
    return {
        "safe": True,
        "recommended_sleep_sec": 0,
        "reason": f"Safe: {current_token_budget} tokens available, {policy['retry_limit']} retries allowed",
        "provider": provider,
        "operation": operation_type,
        "consecutive_failures": consecutive_failures,
    }


# ============================================================================
# Audit Logging
# ============================================================================


def _log_gate_decision(decision_dict: dict, audit_flag: bool = False) -> None:
    """Write gate decision to audit log (if audit_flag is True)."""
    if not audit_flag:
        return

    # Ensure .cache/ exists
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Prepare log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "decision": "rate_limit_safe" if decision_dict["safe"] else "rate_limit_blocked",
        "provider": decision_dict["provider"],
        "operation": decision_dict["operation"],
        "consecutive_failures": decision_dict["consecutive_failures"],
        "budget": decision_dict.get("current_budget"),
        "reason": decision_dict["reason"],
    }

    # Append to audit log (JSONL format)
    try:
        with open(AUDIT_LOG_PATH, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Warning: Failed to write audit log: {e}", file=sys.stderr)


# ============================================================================
# CLI
# ============================================================================


def main() -> int:
    """Parse arguments and emit gate decision."""

    parser = argparse.ArgumentParser(
        description="Pre-delegation rate-limit gate with circuit-breaker.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "current_token_budget",
        type=int,
        help="Tokens remaining in current rate-limit window",
    )
    parser.add_argument(
        "operation_type",
        help="Type of operation (fetch_source, delegation, phase_boundary, review_gate, commit)",
    )
    parser.add_argument(
        "--provider",
        default="claude",
        help="Provider name (default: claude)",
    )
    parser.add_argument(
        "--audit-log",
        action="store_true",
        help="Log gate decision to audit trail",
    )

    args = parser.parse_args()

    try:
        result = check_rate_limit_gate(
            current_token_budget=args.current_token_budget,
            operation_type=args.operation_type,
            provider=args.provider,
        )

        # Add current budget to result for logging
        result["current_budget"] = args.current_token_budget

        # Log if requested
        if args.audit_log:
            _log_gate_decision(result, audit_flag=True)

        # Emit result as JSON
        print(json.dumps(result))
        return 0

    except (OperationNotFound, PolicyNotFound, ValueError) as e:
        error_result = {
            "safe": False,
            "error": str(e),
            "provider": args.provider,
            "operation": args.operation_type,
        }
        print(json.dumps(error_result))
        return 1
    except Exception as e:
        error_result = {
            "safe": False,
            "error": f"Internal error: {e}",
        }
        print(json.dumps(error_result))
        return 1


if __name__ == "__main__":
    sys.exit(main())

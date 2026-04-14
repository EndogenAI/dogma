#!/usr/bin/env python3
"""
Log session events to .cache/session-events.jsonl event stream.

Appends structured event records for queryable provenance tracking:
scratchpad → commits → issues/PRs. Validates against schema before writing.

Purpose:
  - Lightweight provenance tracking without full OpenTelemetry infrastructure
  - OTel-compatible schema (migration path to issue #554)
  - Queryable via jq, Python, or future visualization tools

Usage:
  # Log a phase completion with commit
  uv run python scripts/log_session_event.py \\
    --type phase_complete \\
    --phase "Phase 7" \\
    --agent "Executive Scripter" \\
    --issue 552 \\
    --commit 208ff28 \\
    --deliverables "scripts/log_session_event.py,data/session-events-schema.yml"

  # Log a session start
  uv run python scripts/log_session_event.py \\
    --type session_start \\
    --agent "Executive Orchestrator" \\
    --issue 551,552 \\
    --notes "Starting Open Harness sprint"

  # Log a delegation
  uv run python scripts/log_session_event.py \\
    --type delegation \\
    --phase "Phase 6" \\
    --agent "Executive Orchestrator" \\
    --notes "Delegated to Research Scout"

Query examples:
  # Events for issue 552
  jq '.[] | select(.issue == 552 or (.issue | type == "array" and contains([552])))' \\
    .cache/session-events.jsonl

  # All commits in last 7 days
  jq 'select(.commit_sha != null and (.timestamp | fromdateiso8601) > (now - 604800))' \\
    .cache/session-events.jsonl

  # Events by phase
  jq 'select(.phase == "Phase 4")' .cache/session-events.jsonl

Exit codes:
  0 — Event logged successfully
  1 — Validation failed (invalid event_type, missing required fields, schema violation)
  2 — Usage error (invalid arguments)

Derived from: docs/plans/2026-04-13-open-harness-sprint.md Phase 7
Owner issue: #552
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# Allow tests (and CI) to override the events file path via env var
# so tests stay hermetic and never dirty the real .cache/ directory.
_default_events_file = Path(__file__).parent.parent / ".cache" / "session-events.jsonl"
EVENTS_FILE: Path = Path(os.environ["DOGMA_EVENTS_FILE"]) if "DOGMA_EVENTS_FILE" in os.environ else _default_events_file


def load_schema() -> dict[str, Any]:
    """Load the JSON schema from data/session-events-schema.yml."""
    schema_path = Path(__file__).parent.parent / "data" / "session-events-schema.yml"
    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}", file=sys.stderr)
        sys.exit(1)

    with schema_path.open("r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)

    return schema


def validate_event(event: dict[str, Any], schema: dict[str, Any]) -> tuple[bool, str]:
    """
    Validate event against schema.

    Returns:
        (is_valid, error_message)
    """
    # Check required fields
    required = schema.get("required", [])
    for field in required:
        if field not in event:
            return False, f"Missing required field: {field}"

    # Check event_type enum
    if "event_type" in event:
        allowed_types = schema["properties"]["event_type"]["enum"]
        if event["event_type"] not in allowed_types:
            return False, f"Invalid event_type: {event['event_type']}. Must be one of: {', '.join(allowed_types)}"

    # Check timestamp format (basic ISO 8601 check)
    if "timestamp" in event:
        try:
            datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            return False, f"Invalid timestamp format: {event['timestamp']}. Must be ISO 8601"

    # Validate optional field types when present (non-None values)
    issue_val = event.get("issue")
    if issue_val is not None:
        if not isinstance(issue_val, (int, list)):
            return False, f"'issue' must be an int or list of ints, got {type(issue_val).__name__}"
        if isinstance(issue_val, list) and not all(isinstance(i, int) for i in issue_val):
            return False, "'issue' list must contain only ints"

    commit_sha_val = event.get("commit_sha")
    if commit_sha_val is not None:
        if not isinstance(commit_sha_val, str) or not commit_sha_val.strip():
            return False, "'commit_sha' must be a non-empty string"

    deliverables_val = event.get("deliverables")
    if deliverables_val is not None:
        if not isinstance(deliverables_val, list):
            return False, f"'deliverables' must be a list, got {type(deliverables_val).__name__}"

    return True, ""


def get_current_branch() -> str:
    """Get current git branch name."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Log session events to .cache/session-events.jsonl",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Phase completion
  %(prog)s --type phase_complete --phase "Phase 7" --agent "Executive Scripter" \\
    --issue 552 --commit 208ff28 --deliverables "file1.py,file2.yml"

  # Session start
  %(prog)s --type session_start --agent "Executive Orchestrator" \\
    --issue 551,552 --notes "Sprint kickoff"
        """,
    )

    parser.add_argument(
        "--type",
        required=True,
        help="Event type (session_start, phase_complete, delegation, commit, review, etc.)",
    )
    parser.add_argument(
        "--branch",
        help="Git branch name (default: current branch)",
    )
    parser.add_argument(
        "--phase",
        help="Phase identifier (e.g., 'Phase 1', 'Phase 2 Review')",
    )
    parser.add_argument(
        "--agent",
        help="Agent name (e.g., 'Executive Scripter')",
    )
    parser.add_argument(
        "--issue",
        help="GitHub issue number(s), comma-separated for multiple",
    )
    parser.add_argument(
        "--commit",
        help="Git commit SHA (short or full)",
    )
    parser.add_argument(
        "--pr",
        type=int,
        help="Pull request number",
    )
    parser.add_argument(
        "--deliverables",
        help="Comma-separated list of deliverable paths or descriptions",
    )
    parser.add_argument(
        "--notes",
        help="Optional free-text notes",
    )

    args = parser.parse_args()

    # Load schema
    schema = load_schema()

    # Build event object
    event: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": args.type,
        "branch": args.branch or get_current_branch(),
    }

    # Add optional fields
    if args.phase:
        event["phase"] = args.phase
    else:
        event["phase"] = None

    if args.agent:
        event["agent"] = args.agent
    else:
        event["agent"] = None

    # Parse issue (can be single int or array)
    if args.issue:
        issues = args.issue.split(",")
        if len(issues) == 1:
            event["issue"] = int(issues[0])
        else:
            event["issue"] = [int(i.strip()) for i in issues]
    else:
        event["issue"] = None

    event["commit_sha"] = args.commit or None
    event["pr_number"] = args.pr or None

    # Parse deliverables
    if args.deliverables:
        event["deliverables"] = [d.strip() for d in args.deliverables.split(",")]
    else:
        event["deliverables"] = None

    event["notes"] = args.notes or None

    # Validate
    is_valid, error_msg = validate_event(event, schema)
    if not is_valid:
        print(f"Validation error: {error_msg}", file=sys.stderr)
        return 1

    # Ensure the events directory exists (supports tmp_path in tests)
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Append to JSONL
    with EVENTS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    print(f"✓ Event logged: {args.type} ({event['timestamp']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# `token\_spin\_detector`

token_spin_detector.py — Detect runaway repeated command invocations (token spinning).

Purpose
-------
Context rot from unmanaged token accumulation degrades reasoning quality.
Token-spinning — an agent repeatedly invoking the same tool/command without
progress — is a specific failure mode documented in Xu et al. (2512.05470):
quadratic attention cost means even moderate repetition carries outsized
token overhead.

This script reads the PREEXEC governor audit log produced by
preexec_audit_log.py and detects "spinning": the same command executed
≥N times within a sliding time window.  It is *detection-only*: it never
blocks command execution.  Blocking layers can be added later by callers
that act on the exit code.

This script was introduced as part of Sprint 13 (automation-observability,
issue #156) per the Programmatic-First principle in AGENTS.md.

Inputs
------
- --log FILE           Path to the audit log (default: .tmp/preexec_audit.log)
- --threshold N        Invocations of the same command within the window to
                       consider "spinning" (default: 5)
- --window SECONDS     Sliding window size in seconds (default: 60)
- --check              Exit 0 if no spinning detected; exit 2 if spinning found.
                       Offending commands are printed to stderr.
- --dry-run            Print what would be flagged without changing the exit code.

Outputs
-------
- Spinning commands printed to stderr when detected in --check mode.
- --dry-run: same output as --check but always exits 0.

Usage Examples
--------------
# Check for spinning with defaults (exits 2 if spinning found)
uv run python scripts/token_spin_detector.py --check

# Use a custom threshold and window
uv run python scripts/token_spin_detector.py --check --threshold 3 --window 30

# Dry run: show what would be flagged, always exit 0
uv run python scripts/token_spin_detector.py --dry-run

# Point at a non-default audit log
uv run python scripts/token_spin_detector.py --check --log .tmp/other.log

Exit Codes
----------
0  No spinning detected (or --dry-run)
1  Usage / IO error
2  Spinning detected (--check mode only)

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:9d36603ab5be6e72 -->

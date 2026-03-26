# `preexec\_audit\_log`

preexec_audit_log.py — PREEXEC governor audit log writer and summariser.

Purpose
-------
Extend the PREEXEC governor concept by recording bash subshell invocations to
a structured audit log.  When PREEXEC_GOVERNOR_ENABLED is set in the environment,
the governor intercepts commands before execution.  This script provides the
*recording* half: each intercepted invocation is appended as a JSON line to the
audit log so that downstream tooling (e.g. token_spin_detector.py) can analyse
usage patterns without blocking execution.

The script is *audit-only*: it never blocks command execution.

This script was introduced as part of Sprint 13 (automation-observability,
issue #157) to provide structured visibility into PREEXEC governor activity.
Per the Programmatic-First principle in AGENTS.md, audit logging that was being
done ad-hoc across sessions is now encoded as a committed script.

Inputs
------
- --log FILE        Path to the audit log (default: .tmp/preexec_audit.log)
- --command TEXT    Command being audited (required unless --summary)
- --cwd TEXT        Working directory at invocation time (default: current $PWD)
- --governor-value  Value of PREEXEC_GOVERNOR_ENABLED env var (default: from env)
- --summary         Print a count of logged invocations grouped by command prefix

Outputs
-------
- Appends a single JSON line to the audit log on each non-summary invocation.
- --summary: prints a table of command-prefix counts to stdout.

Usage Examples
--------------
# Record a command invocation
uv run python scripts/preexec_audit_log.py --command "uv run pytest" --cwd /tmp

# Record with an explicit governor value
uv run python scripts/preexec_audit_log.py --command "bash -c 'ls'" --governor-value 1

# Summarise the audit log
uv run python scripts/preexec_audit_log.py --summary

# Summarise a non-default log
uv run python scripts/preexec_audit_log.py --summary --log .tmp/other.log

Exit Codes
----------
0  Success
1  Missing required argument / IO error

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:cfc64fb94153a637 -->

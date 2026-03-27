# `export\_project\_state`

scripts/export_project_state.py — Export GitHub project state to JSON.

Purpose
-------
Queries the GitHub CLI for the current repository's issue list and label list,
then writes a structured JSON snapshot to disk.  Intended to be called by the
``snapshot-issues`` CI workflow on a cron schedule so later sessions can read
project state locally without incurring gh API calls.

Inputs
------
- GitHub CLI (``gh``) authenticated and in PATH
- Optionally: ``--output PATH`` to override the default cache location

Outputs
-------
- JSON file at ``--output`` path (default: ``.cache/github/project_state.json``)
  Shape::

    {
      "issues": [{"number": N, "title": "...", "state": "open|closed",
                  "labels": [{"name": "...", "color": "...", "description": "..."}]}],
      "labels": [{"name": "...", "color": "...", "description": "..."}],
      "generated_at": "2026-03-13T06:00:00+00:00"
    }

- stdout: status messages (suppressed on success with --quiet)
- stderr: error details

Flags
-----
--output PATH   Destination file path.
                Default: .cache/github/project_state.json
--fields FIELDS Comma-separated list of top-level output fields to include.
                Known: issues, labels. Default: all fields.
                Case-insensitive.
--check         Print cache age and exit 0 if fresh (<4 h), exit 1 if stale/absent.
--quiet         Suppress informational stdout messages.
--help          Show this help and exit.

Exit codes
----------
0  Success (or --check with fresh cache).
1  gh CLI error, write failure, or --check with stale/absent cache.

Usage examples
--------------
# Export to default cache location
uv run python scripts/export_project_state.py

# Export to a custom path
uv run python scripts/export_project_state.py --output /tmp/state.json

# Check whether the cache is fresh (<4 h old)
uv run python scripts/export_project_state.py --check

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:9615dc894af29027 -->

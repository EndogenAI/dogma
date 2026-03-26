# `bulk\_github\_operations`

scripts/bulk_github_operations.py — Batch GitHub issue/PR write operations.

Purpose
-------
Execute a list of GitHub issue and PR write operations (create, edit, close)
from a structured spec file, with rate-limit throttling between calls.
All operations route through the ``gh`` CLI via subprocess with list-of-args
(never shell=True). A ``--dry-run`` flag prints every planned command without
executing any ``gh`` calls — mandatory safety gate before a bulk run.

Inputs
------
- Operation spec: JSON or YAML file passed via ``--input FILE``, or JSON
  piped to stdin. Each operation is a dict with keys:
  - ``op``: one of ``issue-create``, ``issue-edit``, ``issue-close``, ``pr-edit``
  - ``target``: issue/PR number (integer), or null for ``issue-create``
  - ``params``: dict of operation-specific parameters (see below)

  Supported params per operation:

  issue-create  title (str), body (str), labels (list[str]),
                milestone (str|int), assignee (str)
  issue-edit    add-labels (list[str]), remove-labels (list[str]),
                labels (list[str] — alias for add-labels),
                milestone (str|int), assignee (str)
  issue-close   (no params required)
  pr-edit       add-labels (list[str]), remove-labels (list[str]),
                labels (list[str] — alias for add-labels),
                milestone (str|int), assignee (str)

Outputs
-------
- stdout: JSON array of result objects, one per operation::

    [{"op": "issue-close", "target": 42, "status": "ok", "error": null}, ...]

  Dry-run results have ``status == "dry-run"`` and include a ``"cmd"`` field
  showing the exact command that *would* be run.
- stderr: one progress line per operation (``[OK]``, ``[FAIL]``, ``[DRY-RUN]``)

Flags
-----
--input PATH          JSON or YAML file containing the operation list.
                      Omit to read JSON from stdin.
--dry-run             Print planned commands; make no gh calls. Exit 0 on valid
                      input; exit 2 on parse/validation errors even in dry-run mode.
--rate-limit-delay N  Seconds to sleep between operations. Default: 0.5.
--help                Show this help and exit.

Exit codes
----------
0  All operations succeeded (or --dry-run completed).
1  One or more operations failed.
2  Invalid input (parse error, unknown op type, missing required param).

Usage examples
--------------
# Dry-run from a JSON spec file
uv run python scripts/bulk_github_operations.py --input ops.json --dry-run

# Execute from a YAML spec file with 1 s between ops
uv run python scripts/bulk_github_operations.py --input ops.yaml --rate-limit-delay 1.0

# Pipe JSON spec from stdin
echo '[{"op":"issue-close","target":99,"params":{}}]' | \
    uv run python scripts/bulk_github_operations.py --dry-run

# Dry-run, then re-run for real (two-step safety pattern)
uv run python scripts/bulk_github_operations.py --input ops.json --dry-run
uv run python scripts/bulk_github_operations.py --input ops.json

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:290aafc80f8eef33 -->

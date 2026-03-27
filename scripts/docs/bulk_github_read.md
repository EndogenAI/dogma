# `bulk\_github\_read`

scripts/bulk_github_read.py — Batch GitHub issue/PR metadata reads.

Purpose
-------
Fetch structured metadata for one or more GitHub issues and/or pull requests,
then format the results as a table, JSON, or CSV. All fetches route through
the ``gh`` CLI via subprocess with list-of-args (never shell=True). Supports
reading individual items by number, or running a GitHub search query.

Inputs
------
- ``--issues NUMBERS``  Comma-separated issue numbers to fetch (e.g. 1,2,3).
- ``--prs NUMBERS``     Comma-separated PR numbers to fetch.
- ``--query QUERY``     GitHub search string (passed to ``gh issue list --search``).
  At least one of the above is required.

Outputs
-------
- stdout: formatted results (table by default; JSON or CSV via ``--format``).
- stderr: error messages on fetch failure.

Flags
-----
--issues NUMBERS   Comma-separated issue numbers.
--prs NUMBERS      Comma-separated PR numbers.
--query QUERY      GitHub search string for issue list.
--fields FIELDS    Comma-separated field names to include in output.
                   Default: number,title,state,labels,milestone,assignee
--format FORMAT    Output format: table | json | csv. Default: table.
--help             Show this help and exit.

Exit codes
----------
0  All fetches succeeded.
1  One or more fetches failed (gh error, network issue, etc.).

Usage examples
--------------
# Fetch issues 1, 5, and 10 as a table
uv run python scripts/bulk_github_read.py --issues 1,5,10

# Fetch PR 42 as JSON
uv run python scripts/bulk_github_read.py --prs 42 --format json

# Search for open bugs and export as CSV
uv run python scripts/bulk_github_read.py --query "is:open label:type:bug" --format csv

# Fetch specific fields only
uv run python scripts/bulk_github_read.py --issues 1,2 --fields number,title,state

# Mix issues and PRs
uv run python scripts/bulk_github_read.py --issues 10,11 --prs 5 --format json

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:e81f32b67bddce0b -->

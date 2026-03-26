# `enrich\_research\_issues`

enrich_research_issues.py — Detect and enrich bare-bones type:research GitHub issues.

Bare-bones heuristic: body length ≤ 300 chars AND no "## Acceptance Criteria" heading.

Usage:
    uv run python scripts/enrich_research_issues.py           # inspect only (default, dry-run)
    uv run python scripts/enrich_research_issues.py --apply   # post enrichment comment

Exit codes:
    0 — completed (0 or more issues found)
    1 — GitHub API error or authentication failure
    2 — script usage error (bad args)

## Usage

```bash
    uv run python scripts/enrich_research_issues.py           # inspect only (default, dry-run)
    uv run python scripts/enrich_research_issues.py --apply   # post enrichment comment
```

<!-- hash:a01bbdd5829b31fe -->

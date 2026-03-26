# `check\_readiness\_matrix`

Check that files with readiness claims include a capability matrix.

Purpose:
    Validate that any file containing readiness/ready/complete claims includes
    a capability matrix. Implements AGENTS.md § Readiness Language Guard and
    readiness-false-positive-analysis.md Recommendation 2.

Inputs:
    files   : list of file paths to check (positional args)
    --fix   : no-op flag for pre-commit compatibility (reserved)
    --strict: fail if any dimension has status "partial" (default: only fail on missing)

Outputs:
    Exit 0  : no violations found
    Exit 1  : one or more files contain readiness claims without capability matrix
    Stdout  : list of violations with file path and line number

Usage:
    uv run python scripts/check_readiness_matrix.py docs/plans/*.md
    uv run python scripts/check_readiness_matrix.py --strict docs/plans/foo.md

## Usage

```bash
    uv run python scripts/check_readiness_matrix.py docs/plans/*.md
    uv run python scripts/check_readiness_matrix.py --strict docs/plans/foo.md
```

<!-- hash:fbff8cffc85e3194 -->

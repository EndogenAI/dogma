# `check\_divergence`

check_divergence.py — Detect drift between a derived repo and the dogma template.

Purpose:
    Compares governance artefacts in a derived (cookiecutter-instantiated) repository
    against the local dogma template to surface structural divergence. Useful as a
    CI gate on derived repos to ensure they remain aligned with upstream governance.

Inputs:
    --repo PATH       Path to the derived repository root (required)
    --check           Exit 1 if any drift is found (CI gate mode)
    --dry-run         Print what would be compared without reading file contents; exit 0
    --export-hgt      Emit a YAML list of drift items as "HGT candidates" — sections
                      that changed in the derived repo vs template, potential upstream
                      learnings for dogma itself

Outputs:
    Text drift-delta report (added/removed/changed per artefact) printed to stdout.
    With --export-hgt: YAML candidate list appended to stdout after the report.

Artefacts compared:
    1. AGENTS.md              — H2 headings present in dogma vs derived repo
    2. .pre-commit-config.yaml — hook IDs present in dogma vs derived repo
    3. pyproject.toml         — presence of [project] and [tool.pytest.ini_options] sections
    4. client-values.yml      — file presence in derived repo root

Exit codes:
    0   No drift found (or --dry-run)
    1   Drift found with --check flag
    2   Error: invalid --repo path or unexpected I/O failure

Usage examples:
    uv run python scripts/check_divergence.py --repo ../my-project --check
    uv run python scripts/check_divergence.py --repo ../my-project --dry-run
    uv run python scripts/check_divergence.py --repo ../my-project --export-hgt

## Usage

```bash
    uv run python scripts/check_divergence.py --repo ../my-project --check
    uv run python scripts/check_divergence.py --repo ../my-project --dry-run
    uv run python scripts/check_divergence.py --repo ../my-project --export-hgt
```

<!-- hash:ee80fe4d73741eec -->

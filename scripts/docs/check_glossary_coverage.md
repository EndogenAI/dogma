# `check\_glossary\_coverage`

scripts/check_glossary_coverage.py

Bold-term glossary coverage scanner.

Purpose:
    Extract all **term** (double-asterisk bold) patterns from governance docs,
    then verify each term appears as a heading or bold entry in docs/glossary.md.
    Reports missing terms and a coverage percentage.

Inputs:
    --files     Paths to governance docs to scan (default: AGENTS.md, MANIFESTO.md,
                docs/guides/*.md relative to workspace root)
    --glossary  Path to glossary file (default: docs/glossary.md)
    --check     Exit 1 if any terms are missing from the glossary
    --fix       Append stub entries for missing terms (idempotent — does not re-add
                terms already present)

Outputs:
    stdout: Coverage report with missing terms and coverage percentage.
    docs/glossary.md: (when --fix) stub entries appended for missing terms.

Exit codes:
    0   All terms covered (or --check not used)
    1   Missing terms found (with --check flag)

Usage examples:
    # Report coverage using defaults
    uv run python scripts/check_glossary_coverage.py

    # Check and exit 1 if gaps found
    uv run python scripts/check_glossary_coverage.py --check

    # Scan specific files
    uv run python scripts/check_glossary_coverage.py --files AGENTS.md MANIFESTO.md

    # Fix: add stubs for missing terms
    uv run python scripts/check_glossary_coverage.py --fix

## Usage

```bash
    # Report coverage using defaults
    uv run python scripts/check_glossary_coverage.py

    # Check and exit 1 if gaps found
    uv run python scripts/check_glossary_coverage.py --check

    # Scan specific files
    uv run python scripts/check_glossary_coverage.py --files AGENTS.md MANIFESTO.md

    # Fix: add stubs for missing terms
    uv run python scripts/check_glossary_coverage.py --fix
```

<!-- hash:a4758aba1d7746b2 -->

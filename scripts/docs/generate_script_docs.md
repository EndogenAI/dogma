# `generate\_script\_docs`

scripts/generate_script_docs.py

Purpose:
    Generate per-script Markdown documentation from module-level docstrings.
    For each .py file in scripts/, extract the module docstring and write a
    corresponding Markdown file to scripts/docs/<script-name>.md.

Inputs:
    scripts/*.py  — Python scripts with module-level docstrings.

Outputs:
    scripts/docs/<script-name>.md  — one Markdown file per script.

Flags:
    --check    Verify that all scripts/docs/*.md files are up to date (compare
               docstring hash). Exit 1 if stale; prints list of stale files.
    --dry-run  Print what would be written without writing any files.

CLI usage:
    uv run python scripts/generate_script_docs.py
    uv run python scripts/generate_script_docs.py --dry-run
    uv run python scripts/generate_script_docs.py --check
    uv run python scripts/generate_script_docs.py --scripts-dir scripts

Exit codes:
    0  All docs generated (or up to date for --check).
    1  --check found stale documentation, or an error occurred.

## Usage

```bash
    uv run python scripts/generate_script_docs.py
    uv run python scripts/generate_script_docs.py --dry-run
    uv run python scripts/generate_script_docs.py --check
    uv run python scripts/generate_script_docs.py --scripts-dir scripts
```

<!-- hash:f9b8f25b97e75ccb -->

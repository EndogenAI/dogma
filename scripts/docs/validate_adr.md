# `validate\_adr`

scripts/validate_adr.py

Validates Architecture Decision Record (ADR) files in docs/decisions/.

Purpose:
    Enforce a consistent structure for ADR files: YAML frontmatter with required
    metadata fields, required section headings, and minimum body length.
    Designed for pre-commit pass_filenames: true (accepts nargs='+').

Inputs:
    files: One or more paths to ADR Markdown files.

Outputs:
    stdout: Per-file PASS/FAIL report with specific error messages.
    Exit 0 if all files pass, exit 1 if any file fails.

Exit codes:
    0  All files passed validation.
    1  One or more files failed validation.

Usage examples:
    # Validate a single ADR
    uv run python scripts/validate_adr.py docs/decisions/ADR-001-uv-package-manager.md

    # Validate all ADRs
    uv run python scripts/validate_adr.py docs/decisions/ADR-*.md

    # Used by pre-commit (pass_filenames: true)
    uv run python scripts/validate_adr.py docs/decisions/ADR-003-xml-hybrid-agent-format.md

## Usage

```bash
    # Validate a single ADR
    uv run python scripts/validate_adr.py docs/decisions/ADR-001-uv-package-manager.md

    # Validate all ADRs
    uv run python scripts/validate_adr.py docs/decisions/ADR-*.md

    # Used by pre-commit (pass_filenames: true)
    uv run python scripts/validate_adr.py docs/decisions/ADR-003-xml-hybrid-agent-format.md
```

<!-- hash:515f4b922eca6960 -->

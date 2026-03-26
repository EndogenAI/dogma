# `validate\_synthesis`

scripts/validate_synthesis.py

Programmatic quality gate for synthesis documents — equivalent to Claude Code's
TaskCompleted hook. Validate before any Research Archivist commit.

Purpose:
    Enforce a minimum quality bar on D3 per-source synthesis reports
    (docs/research/sources/<slug>.md) and D4 issue synthesis documents
        (docs/research/<slug>.md and nested subdirectories, excluding sources and
        OPEN_RESEARCH.md) before they are committed as Final artifacts.

    Detects document type automatically:
      - D3 (per-source synthesis): file path contains /sources/
            - D4 (issue synthesis):      file path is under docs/research/, excluding
                                                                     /sources/ content and OPEN_RESEARCH.md

Checks (D3 per-source synthesizer output):
    1. File exists and is readable.
    2. File has at least MIN_LINES (default: 80) non-blank lines.
    3. All 8 required section headings are present.
    4. YAML frontmatter contains the required fields: url (or source_url),
       cache_path, slug, title.

Checks (D4 issue synthesis):
    1. File exists and is readable.
    2. File has at least MIN_LINES (default: 80) non-blank lines.
     3. Required numbered headings include Executive Summary, Hypothesis
         Validation, and Pattern Catalog, and the document must contain at least
         4 H2 headings overall.
    4. YAML frontmatter contains: title, status.

Inputs:
    <file>         Path to the synthesis file to validate.  (positional, required)
    --min-lines    Minimum non-blank line count.            (default: 80)
    --strict       Reserved for future use — currently a no-op flag.

Outputs:
    stdout:  Human-readable pass/fail summary with specific gap list.
    stderr:  Nothing (all output goes to stdout for easy capture).

Exit codes:
    0  All checks passed.
    1  One or more checks failed — specific gap(s) reported to stdout.

Usage examples:
    # Validate a D3 per-source synthesis report
    uv run python scripts/validate_synthesis.py docs/research/sources/anthropic-building-effective-agents.md

    # Validate a D4 issue synthesis
    uv run python scripts/validate_synthesis.py docs/research/agent-fleet-design-patterns.md

    # Require a higher minimum line count
    uv run python scripts/validate_synthesis.py docs/research/sources/my-source.md --min-lines 150

    # Integrate into archivist workflow (non-zero exit blocks commit)
    uv run python scripts/validate_synthesis.py "$FILE" || exit 1

## Usage

```bash
    # Validate a D3 per-source synthesis report
    uv run python scripts/validate_synthesis.py docs/research/sources/anthropic-building-effective-agents.md

    # Validate a D4 issue synthesis
    uv run python scripts/validate_synthesis.py docs/research/agent-fleet-design-patterns.md

    # Require a higher minimum line count
    uv run python scripts/validate_synthesis.py docs/research/sources/my-source.md --min-lines 150

    # Integrate into archivist workflow (non-zero exit blocks commit)
    uv run python scripts/validate_synthesis.py "$FILE" || exit 1
```

<!-- hash:ad711f17bf7a7cb0 -->

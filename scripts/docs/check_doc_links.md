# `check\_doc\_links`

check_doc_links.py — Validate that relative file links in Markdown docs resolve.

Purpose
-------
Scan Markdown files for relative file links (e.g. `[text](../path/to/file.md)`)
and verify that each linked path exists on disk relative to the source file.

This catches the common failure mode where a doc in `docs/guides/` references
`.github/agents/AGENTS.md` (wrong — resolves to `docs/guides/.github/...`)
instead of `../../.github/agents/AGENTS.md` (correct).

Only checks file:// style relative links — skips http/https URLs, anchors (#),
and mailto: links. Those are the responsibility of lychee in CI.

Inputs
------
Positional arguments: one or more Markdown file paths to check.
If none given, scans docs/**/*.md and CONTRIBUTING.md README.md CHANGELOG.md.

Outputs
-------
Prints broken links to stderr. Exits 0 if all links resolve, 1 if any are broken.

Usage
-----
# Check specific files:
uv run python scripts/check_doc_links.py docs/research/agent-taxonomy.md

# Check all docs (default):
uv run python scripts/check_doc_links.py

# Used as pre-commit hook (filenames passed by pre-commit):
python3 scripts/check_doc_links.py docs/guides/agents.md docs/research/foo.md

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:364c2bef4b232238 -->

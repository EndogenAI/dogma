# `format\_citations`

format_citations.py — Render ACM-style citations from a bibliography YAML file.

Purpose
-------
Read structured source metadata from `docs/research/bibliography.yaml` and render
ACM SIG Proceedings-style reference list entries as Markdown. Supports articles,
books, conference papers, technical reports, theses, and web resources.

Also supports:
- Listing all entries with their citation keys
- Looking up a single entry by key
- Generating an inline citation tag [AuthorYear] for use in documents

ACM Citation Format Examples
-----------------------------
Article:
  [1] Donald E. Knuth. 1984. Literate Programming. The Computer Journal 27, 2 (1984), 97–111.
      DOI: https://doi.org/10.1093/comjnl/27.2.97

Book:
  [2] Christopher Alexander, Sara Ishikawa, and Murray Silverstein. 1977. A Pattern Language.
      Oxford University Press, New York, NY.

Conference paper:
  [3] Nathan Ensmenger. 2010. Making Programming Masculine. In Gender Codes. IEEE, 115–141.

Web resource:
  [4] Douglas C. Engelbart. 1962. Augmenting Human Intellect: A Conceptual Framework.
      SRI Summary Report AFOSR-3223. Retrieved 2026-03-07 from
      https://www.dougengelbart.org/content/view/138

Inputs
------
bibliography.yaml  Structured YAML file with source entries (default:
                   docs/research/bibliography.yaml)

Outputs
-------
- Numbered ACM-style reference list rendered as Markdown (stdout)
- Optionally: a single entry by key (--key <id>)
- Optionally: inline citation tag only (--inline <id>)

Usage Examples
--------------
# Render full reference list
uv run python scripts/format_citations.py

# Use a custom bibliography file
uv run python scripts/format_citations.py --bibliography /path/to/bib.yaml

# Render a single entry by key
uv run python scripts/format_citations.py --key knuth1984

# Get the inline citation tag for a key
uv run python scripts/format_citations.py --inline knuth1984

# List all keys
uv run python scripts/format_citations.py --list

Exit Codes
----------
0  Success
1  Bibliography file not found or malformed; requested key not found

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:25c97dea31ced0ac -->

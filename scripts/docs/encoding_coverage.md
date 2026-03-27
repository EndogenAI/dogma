# `encoding\_coverage`

scripts/encoding_coverage.py

Checks MANIFESTO.md and AGENTS.md to determine whether each named principle
and axiom has all four [4,1] encoding forms present.

Encoding forms:
    F1 = verbal description   — at least one substantive paragraph in the
                                principle's section body
    F2 = canonical example    — labeled ``**Canonical example**:`` block
    F3 = anti-pattern         — labeled ``**Anti-pattern**`` block
    F4 = programmatic gate    — labeled ``**Programmatic gate**:`` OR an
                                explicit reference to a script/hook/CI mechanism

Purpose:
    Produce a Markdown coverage table as a baseline for tracking encoding
    completeness of every MANIFESTO principle.  Gaps in F2–F4 signal
    principles where knowledge is verbally described but has not been
    concretized into examples, anti-patterns, or enforcement mechanisms.

Inputs:
    --manifesto PATH   Path to MANIFESTO.md (default: MANIFESTO.md)
    --agents PATH      Path to AGENTS.md    (default: AGENTS.md)

Outputs:
    Markdown table written to stdout.  Exits 0 on success, 1 on a missing
    input file.

Exit codes:
    0  Table generated successfully.
    1  One or more input files not found — error written to stderr.

Usage:
    uv run python scripts/encoding_coverage.py --manifesto MANIFESTO.md --agents AGENTS.md

## Usage

```bash
    uv run python scripts/encoding_coverage.py --manifesto MANIFESTO.md --agents AGENTS.md
```

<!-- hash:142060cd71a0d7bf -->

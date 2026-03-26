# `assess\_doc\_quality`

scripts/assess_doc_quality.py

Composite document quality scorer — readability, structure, and completeness.

Purpose:
    Assess the quality of a Markdown documentation file using three weighted
    sub-scores:
        - Readability  (30%): Flesch-Kincaid grade level (textstat)
        - Structural   (40%): heading density, table count, list/code-block ratio
        - Completeness (30%): citation count, bold terms, labeled canonical blocks

    Composite score = 0.3 × readability_score + 0.4 × structural_score + 0.3 × completeness_score

    Each sub-score is normalized 0–100 where 100 = ideal.

    CALIBRATION NOTE: Before using this script as any enforcement gate, calibrate
    the normalization thresholds against at least 10 representative docs from the
    corpus. Current thresholds are initial estimates. Do NOT add this script as a
    CI FAIL gate until calibration is complete.

    Formula details:
        readability_score:  FK grade ≤ 12 → 100; grade ≥ 20 → 0; linear interpolation.
        structural_score:   avg of (heading_density/2.0 * 100, tables/2 * 100,
                            list_code_ratio/0.30 * 100) — each capped at 100.
        completeness_score: avg of (citation_density/5.0 * 100, bold_density/10.0 * 100,
                            labeled_blocks/3.0 * 100) — each capped at 100.

Inputs:
    file            Path to a Markdown file to assess (positional)
    --output json   Output all sub-scores and composite as JSON
    --delta FILE    Path to .reading-level-targets.yml for FK grade delta comparison

Outputs:
    stdout: Human-readable score report, or JSON (--output json).

Exit codes:
    0   Assessment complete (advisory only — does not fail on low scores)
    1   File not found

Usage examples:
    uv run python scripts/assess_doc_quality.py docs/glossary.md
    uv run python scripts/assess_doc_quality.py AGENTS.md --output json
    uv run python scripts/assess_doc_quality.py docs/research/my-doc.md \
        --delta .reading-level-targets.yml

## Usage

```bash
    uv run python scripts/assess_doc_quality.py docs/glossary.md
    uv run python scripts/assess_doc_quality.py AGENTS.md --output json
    uv run python scripts/assess_doc_quality.py docs/research/my-doc.md \
        --delta .reading-level-targets.yml
```

<!-- hash:4c2901516892847e -->

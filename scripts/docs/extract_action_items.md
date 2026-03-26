# `extract\_action\_items`

scripts/extract_action_items.py

Purpose:
    Scan D4 research docs (docs/research/*.md) for action items and deduplicate
    near-duplicate items using BM25 similarity (falling back to Jaccard if
    rank_bm25 is unavailable).

Inputs:
    docs/research/*.md  — research documents scanned for action item patterns.

Outputs:
    Markdown table to stdout or --output FILE:
        | Source Doc | Action Item | Similarity Score (if deduped) |

Patterns detected:
    - Lines starting with `- [ ]`
    - Lines starting with `**Action:**`
    - Lines starting with `**Recommendation:**`
    - Lines inside a `## Recommendations` section

CLI usage:
    uv run python scripts/extract_action_items.py
    uv run python scripts/extract_action_items.py --output actions.md
    uv run python scripts/extract_action_items.py --threshold 0.85
    uv run python scripts/extract_action_items.py --research-dir docs/research

Exit codes:
    0  Completed successfully (even if no items found).
    1  Error reading files.

## Usage

```bash
    uv run python scripts/extract_action_items.py
    uv run python scripts/extract_action_items.py --output actions.md
    uv run python scripts/extract_action_items.py --threshold 0.85
    uv run python scripts/extract_action_items.py --research-dir docs/research
```

<!-- hash:ae03b551c780b527 -->

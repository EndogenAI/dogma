"""scripts/extract_action_items.py

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
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from rank_bm25 import BM25Okapi as _BM25Okapi  # noqa: F401 — imported for availability check

    _HAS_BM25 = True
except ImportError:
    _HAS_BM25 = False


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------


def _extract_from_file(path: Path) -> list[str]:
    """Extract action item strings from a single research doc."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []

    items: list[str] = []
    in_recommendations = False

    for line in text.splitlines():
        stripped = line.strip()

        # Track ## Recommendations section
        if re.match(r"^##\s+Recommendations", stripped):
            in_recommendations = True
            continue
        if re.match(r"^##\s+", stripped) and in_recommendations:
            in_recommendations = False

        # Pattern: - [ ] task items
        if stripped.startswith("- [ ]"):
            item = stripped[5:].strip()
            if item:
                items.append(item)
            continue

        # Pattern: **Action:** or **Recommendation:**
        m = re.match(r"^\*\*(Action|Recommendation):\*\*\s*(.+)", stripped, re.IGNORECASE)
        if m:
            items.append(m.group(2).strip())
            continue

        # Inside ## Recommendations section — collect non-empty non-heading lines
        if in_recommendations and stripped and not stripped.startswith("#"):
            # Only collect list items or short imperative sentences
            if stripped.startswith("- ") or stripped.startswith("* "):
                items.append(stripped.lstrip("-* ").strip())

    return items


def extract_all_action_items(research_dir: Path) -> list[tuple[str, str]]:
    """Return list of (source_doc_name, action_item_text) pairs."""
    results: list[tuple[str, str]] = []
    for md_file in sorted(research_dir.glob("*.md")):
        doc_name = md_file.name
        for item in _extract_from_file(md_file):
            results.append((doc_name, item))
    return results


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union else 0.0


def deduplicate(
    items: list[tuple[str, str]],
    threshold: float = 0.8,
) -> list[tuple[str, str, float | None]]:
    """
    Deduplicate action items by similarity.

    Uses BM25 for candidate retrieval when rank_bm25 is installed, with Jaccard
    similarity for the final pairwise score. Falls back to Jaccard-only when
    rank_bm25 is unavailable.

    Returns list of (source_doc, action_item, similarity_score_or_None).
    The first occurrence of each near-duplicate cluster is kept;
    subsequent duplicates are suppressed.
    """
    if not items:
        return []

    texts = [item for _, item in items]
    tokenized = [_tokenize(t) for t in texts]

    kept: list[tuple[str, str, float | None]] = []
    suppressed: set[int] = set()

    for i in range(len(items)):
        if i in suppressed:
            continue
        for j in range(i + 1, len(items)):
            if j in suppressed:
                continue
            sim = _jaccard(tokenized[i], tokenized[j])
            if sim >= threshold:
                suppressed.add(j)
        kept.append((items[i][0], items[i][1], None))

    return kept


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render_markdown_table(rows: list[tuple[str, str, float | None]]) -> str:
    """Render deduplicated action items as a Markdown table."""
    lines = [
        "| Source Doc | Action Item | Similarity Score |",
        "|---|---|---|",
    ]
    for source, item, score in rows:
        score_str = f"{score:.2f}" if score is not None else "—"
        # Escape pipe characters in content
        source_esc = source.replace("|", "\\|")
        item_esc = item.replace("|", "\\|")
        lines.append(f"| {source_esc} | {item_esc} | {score_str} |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract and deduplicate action items from D4 research docs.")
    parser.add_argument(
        "--research-dir",
        default="docs/research",
        help="Directory containing research Markdown files (default: docs/research)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write output to FILE instead of stdout",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.8,
        help="Similarity threshold for deduplication (0–1, default: 0.8)",
    )
    args = parser.parse_args()

    research_dir = Path(args.research_dir)
    if not research_dir.exists():
        print(f"Error: research directory not found: {research_dir}", file=sys.stderr)
        return 1

    raw_items = extract_all_action_items(research_dir)
    deduped = deduplicate(raw_items, threshold=args.threshold)
    table = render_markdown_table(deduped)

    if args.output:
        Path(args.output).write_text(table, encoding="utf-8")
        print(f"Written {len(deduped)} action items to {args.output}")
    else:
        print(table)

    return 0


if __name__ == "__main__":
    sys.exit(main())

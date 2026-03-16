"""scripts/assess_doc_quality.py

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
    uv run python scripts/assess_doc_quality.py docs/research/my-doc.md \\
        --delta .reading-level-targets.yml
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import textstat
from markdown_it import MarkdownIt

# ---------------------------------------------------------------------------
# Sub-scorers
# ---------------------------------------------------------------------------


def _word_count(text: str) -> int:
    return len(text.split())


def readability_score(text: str) -> tuple[float, float]:
    """
    Compute Flesch-Kincaid grade (FK) and normalise 0–100.

    Target grade 12 → score 100; grade ≥ 20 → score 0; linear interpolation.
    Lower FK grade = more readable = better score.

    Returns:
        (fk_grade, normalised_score_0_100)
    """
    if len(text.strip()) < 10:
        return 0.0, 100.0
    fk = textstat.flesch_kincaid_grade(text)
    TARGET_GRADE = 12.0
    WORST_GRADE = 20.0
    if fk <= TARGET_GRADE:
        score = 100.0
    elif fk >= WORST_GRADE:
        score = 0.0
    else:
        score = 100.0 * (1 - (fk - TARGET_GRADE) / (WORST_GRADE - TARGET_GRADE))
    return round(fk, 1), round(score, 1)


def structural_score(text: str, md: MarkdownIt) -> tuple[dict, float]:
    """
    Compute structural sub-score from heading density, table count, list/code ratio.

    Normalization thresholds (initial estimates — calibrate against corpus before
    enforcing):
        heading_density: ≥ 2.0 headings/1000 words → 100
        table_count:     ≥ 2 tables → 100
        list_code_ratio: ≥ 30% of block tokens → 100

    Returns:
        (metrics_dict, normalised_score_0_100)
    """
    tokens = md.parse(text)
    words = _word_count(text)

    heading_count = sum(1 for t in tokens if t.type == "heading_open")
    table_count = sum(1 for t in tokens if t.type == "table_open")
    list_open_count = sum(1 for t in tokens if t.type in ("bullet_list_open", "ordered_list_open"))
    fence_count = sum(1 for t in tokens if t.type == "fence")

    heading_density = (heading_count / words * 1000) if words > 0 else 0.0
    structural_tokens = list_open_count + fence_count
    block_tokens = sum(
        1
        for t in tokens
        if t.type
        in (
            "heading_open",
            "table_open",
            "fence",
            "bullet_list_open",
            "ordered_list_open",
            "paragraph_open",
            "hr",
            "blockquote_open",
        )
    )
    list_code_ratio = (structural_tokens / block_tokens) if block_tokens > 0 else 0.0

    hd_score = min(100.0, heading_density / 2.0 * 100)
    tbl_score = min(100.0, table_count / 2.0 * 100)
    lc_score = min(100.0, list_code_ratio / 0.30 * 100)

    composite = (hd_score + tbl_score + lc_score) / 3.0

    metrics = {
        "heading_density_per_1000": round(heading_density, 2),
        "table_count": table_count,
        "list_open_count": list_open_count,
        "fence_count": fence_count,
        "list_code_ratio": round(list_code_ratio, 3),
    }
    return metrics, round(composite, 1)


def completeness_score(text: str) -> tuple[dict, float]:
    """
    Compute completeness sub-score from citation density, bold terms, labeled blocks.

    Normalization thresholds:
        citation_density: ≥ 5 lines/1000 words with [link]() → 100
        bold_density:     ≥ 10 **bold** terms/1000 words → 100
        labeled_blocks:   ≥ 3 **Canonical example** or **Anti-pattern** lines → 100

    Returns:
        (metrics_dict, normalised_score_0_100)
    """
    lines = text.splitlines()
    words = _word_count(text)

    if words == 0:
        return {
            "citation_lines": 0,
            "citation_density_per_1000": 0.0,
            "bold_terms": 0,
            "bold_density_per_1000": 0.0,
            "labeled_blocks": 0,
        }, 0.0

    citation_lines = sum(1 for line in lines if re.search(r"\[.+\]\(", line))
    bold_terms = len(re.findall(r"\*\*[^*\n]{2,}\*\*", text))
    labeled_blocks = sum(
        1 for line in lines if re.match(r"\*\*(Canonical example|Anti-pattern)\*\*", line, re.IGNORECASE)
    )

    citation_density = citation_lines / words * 1000
    bold_density = bold_terms / words * 1000

    cit_score = min(100.0, citation_density / 5.0 * 100)
    bold_score = min(100.0, bold_density / 10.0 * 100)
    labeled_score = min(100.0, labeled_blocks / 3.0 * 100)

    composite = (cit_score + bold_score + labeled_score) / 3.0

    metrics = {
        "citation_lines": citation_lines,
        "citation_density_per_1000": round(citation_density, 2),
        "bold_terms": bold_terms,
        "bold_density_per_1000": round(bold_density, 2),
        "labeled_blocks": labeled_blocks,
    }
    return metrics, round(composite, 1)


# ---------------------------------------------------------------------------
# Delta mode
# ---------------------------------------------------------------------------


def load_reading_level_targets(targets_path: Path) -> dict:
    """Load .reading-level-targets.yml; return empty dict if file is absent or unreadable."""
    if not targets_path.exists():
        return {}
    try:
        import yaml  # type: ignore[import-untyped]

        return yaml.safe_load(targets_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def compute_delta(fk_grade: float, file_path: str, targets: dict) -> str | None:
    """Return a human-readable delta string, or None if no target is defined.

    Supports two targets-file schemas:
    - Flat: ``{filename: grade_target, "default": grade_target}``
    - Nested: ``{substrates: {name: {path_pattern, target_grade_min, target_grade_max}}}``
      (as produced by ``data/reading-level-targets.yml``)
    """
    from fnmatch import fnmatch

    # Handle nested substrates schema (data/reading-level-targets.yml)
    if "substrates" in targets:
        substrate_data = targets["substrates"]
        if isinstance(substrate_data, dict):
            normalized = file_path.replace("\\", "/")
            basename = normalized.rsplit("/", 1)[-1]
            for substrate_info in substrate_data.values():
                if not isinstance(substrate_info, dict):
                    continue
                pattern = substrate_info.get("path_pattern", "")
                if pattern and (fnmatch(normalized, pattern) or fnmatch(basename, pattern)):
                    t_min = substrate_info.get("target_grade_min")
                    t_max = substrate_info.get("target_grade_max")
                    if t_min is None or t_max is None:
                        return None
                    t_mid = (float(t_min) + float(t_max)) / 2
                    delta = fk_grade - t_mid
                    direction = "above" if delta > 0 else "below"
                    return (
                        f"FK grade {fk_grade:.1f} vs target {t_min}\u2013{t_max}"
                        f" \u2192 {abs(delta):.1f} {direction} target midpoint"
                    )
        return None

    # Flat schema: {file_name: target} or {"default": target}
    file_name = file_path.replace("\\", "/").rsplit("/", 1)[-1]
    target = targets.get(file_name) or targets.get("default")
    if target is None:
        return None
    delta = fk_grade - float(target)
    direction = "above" if delta > 0 else "below"
    return f"FK grade {fk_grade:.1f} vs target {target} → {abs(delta):.1f} {direction} target"


# ---------------------------------------------------------------------------
# Assessment
# ---------------------------------------------------------------------------


def assess(file_path: Path, delta_path: Path | None = None) -> dict:
    """Run full assessment on file_path; return results dict."""
    text = file_path.read_text(encoding="utf-8", errors="replace")
    md = MarkdownIt()

    fk_grade, r_score = readability_score(text)
    struct_metrics, s_score = structural_score(text, md)
    completeness_metrics, c_score = completeness_score(text)

    composite = round(0.3 * r_score + 0.4 * s_score + 0.3 * c_score, 1)

    result: dict = {
        "file": str(file_path),
        "word_count": _word_count(text),
        "readability": {
            "fk_grade": fk_grade,
            "score": r_score,
            "weight": 0.3,
        },
        "structural": {
            "metrics": struct_metrics,
            "score": s_score,
            "weight": 0.4,
        },
        "completeness": {
            "metrics": completeness_metrics,
            "score": c_score,
            "weight": 0.3,
        },
        "composite_score": composite,
    }

    if delta_path is not None:
        targets = load_reading_level_targets(delta_path)
        result["delta"] = compute_delta(fk_grade, str(file_path), targets)

    return result


def print_human(result: dict) -> None:
    print(f"File: {result['file']}  ({result['word_count']} words)")
    print(f"Composite score: {result['composite_score']:.1f} / 100\n")
    r = result["readability"]
    print(f"  Readability  (30%): {r['score']:.1f}  [FK grade {r['fk_grade']}]")
    s = result["structural"]
    sm = s["metrics"]
    print(
        f"  Structural   (40%): {s['score']:.1f}"
        f"  [headings/1000w={sm['heading_density_per_1000']}, tables={sm['table_count']}]"
    )
    c = result["completeness"]
    cm = c["metrics"]
    print(
        f"  Completeness (30%): {c['score']:.1f}"
        f"  [citations={cm['citation_lines']}, bold={cm['bold_terms']}, labeled={cm['labeled_blocks']}]"
    )
    if result.get("delta"):
        print(f"\n  Delta: {result['delta']}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Composite readability/structure/completeness scorer for Markdown docs"
    )
    parser.add_argument("file", help="Path to Markdown file to assess")
    parser.add_argument(
        "--output",
        choices=["json"],
        default=None,
        help="Output format (default: human-readable)",
    )
    parser.add_argument(
        "--delta",
        default=None,
        metavar="TARGETS_FILE",
        help="Path to .reading-level-targets.yml for FK grade delta comparison",
    )
    args = parser.parse_args(argv)

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        return 1

    delta_path = Path(args.delta) if args.delta else None
    result = assess(file_path, delta_path)

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print_human(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())

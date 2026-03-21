"""scripts/audit_recommendation_status.py

Audits the recommendation status across all finalized synthesis documents in
docs/research/, cross-references them against GitHub issues with the
``source:research`` label, and writes suggested frontmatter patch files to
data/retrofit-patches/<doc-slug>.yml.

Purpose:
    Implements Phase 4 of the Recommendation Provenance sprint (issue #409).
    Reads each finalized D4 document, extracts its ``## Recommendations``
    section (body text, not frontmatter), fuzzy-matches each item against
    GitHub issues that carry the ``source:research`` label, and suggests a
    status (completed, accepted, deferred) for each recommendation.  Outputs
    patch files to data/retrofit-patches/ for human review before Phase 6
    patch application.

Inputs:
    docs/research/*.md       — all finalized synthesis docs (status: Final)
    GitHub issues            — issues with label 'source:research' (via gh CLI)
    --dry-run                — print suggestions to stdout; do not write files
    --doc <path>             — audit a single doc instead of all docs
    --no-github              — skip GitHub API calls; mark all recs as deferred
    --docs-dir <path>        — override docs/research directory (default: repo root)
    --patches-dir <path>     — override data/retrofit-patches directory

Outputs:
    data/retrofit-patches/<doc-slug>.yml   — one patch suggestion file per doc
    stdout: audit summary table at end of run

Exit codes:
    0   Audit completed successfully (--dry-run also exits 0).
    1   Fatal error (docs-dir not found, --doc path not found, etc.).

Usage examples:
    # Audit all finalized docs and write patch files
    uv run python scripts/audit_recommendation_status.py

    # Preview without writing files
    uv run python scripts/audit_recommendation_status.py --dry-run

    # Audit a single doc
    uv run python scripts/audit_recommendation_status.py --doc docs/research/civic-ai-governance.md

    # Offline / CI mode — skip GitHub API calls
    uv run python scripts/audit_recommendation_status.py --no-github
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_DOCS_DIR = _REPO_ROOT / "docs" / "research"
_DEFAULT_PATCHES_DIR = _REPO_ROOT / "data" / "retrofit-patches"
_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

# Files that exist under docs/research/ but are not D4 synthesis documents.
_EXCLUDED_FILENAMES = {"OPEN_RESEARCH.md"}

# Consecutive-word overlap thresholds
_HIGH_CONFIDENCE_THRESHOLD = 5  # ≥ 5 consecutive shared words → high confidence
_MEDIUM_CONFIDENCE_THRESHOLD = 3  # ≥ 3 consecutive shared words → medium (or low floor)


# ---------------------------------------------------------------------------
# Frontmatter & slug helpers (shared pattern with index_recommendations.py)
# ---------------------------------------------------------------------------


def _parse_frontmatter_yaml(text: str, file_path: Path) -> dict[str, Any] | None:
    """Parse the YAML frontmatter block from *text*.

    Returns the parsed dict, ``{}`` if no frontmatter, or ``None`` on parse
    error (caller should warn and skip).
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    try:
        result = yaml.safe_load(match.group(1))
        return result or {}
    except yaml.YAMLError as exc:
        print(
            f"WARNING: Malformed YAML frontmatter in {file_path} — skipping: {exc}",
            file=sys.stderr,
        )
        return None


def _doc_slug(doc_path: Path, docs_dir: Path) -> str:
    """Return a stable slug for *doc_path* relative to *docs_dir*."""
    try:
        rel = doc_path.relative_to(docs_dir)
        return rel.stem
    except ValueError:
        return doc_path.stem


# ---------------------------------------------------------------------------
# Recommendation extraction
# ---------------------------------------------------------------------------


def _extract_recommendations_section(text: str) -> str:
    """Extract the body text of the ``## Recommendations`` section.

    Returns everything between the ``## Recommendations`` heading and the
    next ``## `` heading (or EOF), stripped.
    """
    lines = text.split("\n")
    in_section = False
    section_lines: list[str] = []

    for line in lines:
        if re.match(r"^## Recommendations\s*$", line):
            in_section = True
            continue
        if in_section and re.match(r"^## ", line):
            break
        if in_section:
            section_lines.append(line)

    return "\n".join(section_lines).strip()


def _extract_recommendation_items(section_text: str) -> list[str]:
    """Extract individual recommendation items (numbered or bulleted).

    Handles:
    - Numbered lists: ``1. text`` or ``1) text``
    - Bullet lists:   ``- text`` or ``* text``
    - Multi-line items (continuation lines)
    """
    items: list[str] = []
    current_item: list[str] = []

    for line in section_text.split("\n"):
        numbered = re.match(r"^\s*\d+[.)]\s+(.+)", line)
        bulleted = re.match(r"^\s{0,3}[-*]\s+(.+)", line)

        if numbered or bulleted:
            if current_item:
                items.append(" ".join(current_item))
            text = (numbered or bulleted).group(1)  # type: ignore[union-attr]
            current_item = [text.strip()]
        elif current_item and line.strip():
            # Continuation line for current item
            current_item.append(line.strip())
        elif not line.strip() and current_item:
            # Blank line terminates current item
            items.append(" ".join(current_item))
            current_item = []
        # else: blank with no active item, or non-list structural line — skip

    if current_item:
        items.append(" ".join(current_item))

    return items


# ---------------------------------------------------------------------------
# ID and title generation
# ---------------------------------------------------------------------------


def _make_rec_id(slug: str, idx: int) -> str:
    """Generate a stable recommendation ID: ``rec-<slug>-NNN``."""
    return f"rec-{slug}-{idx:03d}"


def _make_rec_title(text: str) -> str:
    """Create a short display title from recommendation text.

    Takes the first sentence (up to the first sentence-ending punctuation
    after stripping Markdown) or ≤ 60 characters, whichever is shorter.
    """
    # Strip bold Markdown: **text** → text
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    # Strip Markdown links: [label](url) → label
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = cleaned.strip()

    # First sentence
    sentence_match = re.match(r"^([^.!?]+[.!?])", cleaned)
    title = sentence_match.group(1).strip() if sentence_match else cleaned

    if len(title) > 60:
        title = title[:57] + "..."
    return title


# ---------------------------------------------------------------------------
# Fuzzy matching
# ---------------------------------------------------------------------------


def _max_consecutive_overlap(text1: str, text2: str) -> int:
    """Find the maximum number of consecutive shared words between two texts.

    Case-insensitive word comparison (punctuation stripped).
    """
    words1 = re.findall(r"\b\w+\b", text1.lower())
    words2 = re.findall(r"\b\w+\b", text2.lower())

    if not words1 or not words2:
        return 0

    max_len = 0
    for i in range(len(words1)):
        for j in range(len(words2)):
            k = 0
            while i + k < len(words1) and j + k < len(words2) and words1[i + k] == words2[j + k]:
                k += 1
            if k > max_len:
                max_len = k
    return max_len


def _match_recommendation(rec_text: str, issues: list[dict[str, Any]]) -> dict[str, Any]:
    """Match a recommendation text against a list of GitHub issues.

    Returns a dict with keys:
        ``best_issue``        — highest-overlap issue, or ``None``
        ``confidence``        — ``"high"`` | ``"medium"`` | ``"low"``
        ``suggested_status``  — ``"completed"`` | ``"accepted"`` | ``"deferred"``
        ``match_note``        — human-readable description (reviewer-only)
    """
    candidates: list[tuple[dict[str, Any], int]] = []

    for issue in issues:
        title_overlap = _max_consecutive_overlap(rec_text, issue.get("title") or "")
        # Limit body scan to first 800 chars to reduce noise
        body_text = (issue.get("body") or "")[:800]
        body_overlap = _max_consecutive_overlap(rec_text, body_text)
        best_overlap = max(title_overlap, body_overlap)

        if best_overlap >= _MEDIUM_CONFIDENCE_THRESHOLD:
            candidates.append((issue, best_overlap))

    # Sort by overlap score descending
    candidates.sort(key=lambda x: x[1], reverse=True)

    if not candidates:
        return {
            "best_issue": None,
            "confidence": "low",
            "suggested_status": "deferred",
            "match_note": "No matching issue found",
        }

    best_issue, best_overlap = candidates[0]

    if len(candidates) > 1:
        # Multiple matches — ambiguous; suggest deferred for manual review
        issue_nums = ", ".join(f"#{iss['number']}" for iss, _ in candidates[:5])
        confidence = "medium" if best_overlap >= _HIGH_CONFIDENCE_THRESHOLD else "low"
        return {
            "best_issue": best_issue,
            "confidence": confidence,
            "suggested_status": "deferred",
            "match_note": f"Multiple matches: {issue_nums} — manual review needed",
        }

    # Single match
    if best_overlap >= _HIGH_CONFIDENCE_THRESHOLD:
        confidence = "high"
    else:
        confidence = "medium"

    suggested_status = "completed" if best_issue["state"].lower() == "closed" else "accepted"
    title_preview = (best_issue.get("title") or "")[:50]
    match_note = f"Matched issue #{best_issue['number']}: '{title_preview}' (consecutive word overlap: {best_overlap})"

    return {
        "best_issue": best_issue,
        "confidence": confidence,
        "suggested_status": suggested_status,
        "match_note": match_note,
    }


# ---------------------------------------------------------------------------
# GitHub issue fetching
# ---------------------------------------------------------------------------


def _fetch_github_issues() -> list[dict[str, Any]]:
    """Fetch all issues with ``source:research`` label via the gh CLI."""
    result = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--label",
            "source:research",
            "--limit",
            "200",
            "--state",
            "all",
            "--json",
            "number,title,body,labels,state",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(
            f"WARNING: gh issue list failed: {result.stderr.strip()}",
            file=sys.stderr,
        )
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"WARNING: Could not parse gh output: {exc}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# Per-document audit
# ---------------------------------------------------------------------------


def _audit_doc(
    doc_path: Path,
    docs_dir: Path,
    issues: list[dict[str, Any]],
    no_github: bool,
) -> dict[str, Any] | None:
    """Audit a single doc and return patch data, or ``None`` if skipped.

    A doc is skipped if: YAML frontmatter is malformed, ``status`` is not
    ``Final``, the ``## Recommendations`` section is absent, or no items
    can be extracted from that section.
    """
    text = doc_path.read_text(encoding="utf-8")
    frontmatter = _parse_frontmatter_yaml(text, doc_path)
    if frontmatter is None:
        return None
    if str(frontmatter.get("status", "")).strip() != "Final":
        return None

    slug = _doc_slug(doc_path, docs_dir)

    try:
        doc_rel = str(doc_path.relative_to(_REPO_ROOT))
    except ValueError:
        doc_rel = str(doc_path)

    section = _extract_recommendations_section(text)
    if not section:
        return None

    items = _extract_recommendation_items(section)
    if not items:
        return None

    generated_at = datetime.now(timezone.utc).isoformat()

    # Confidence rank for doc-level summary
    _rank = {"low": 0, "medium": 1, "high": 2}
    best_doc_confidence = "low"

    recommendations: list[dict[str, Any]] = []
    for idx, item_text in enumerate(items, 1):
        rec_id = _make_rec_id(slug, idx)
        title = _make_rec_title(item_text)

        if no_github:
            rec_entry: dict[str, Any] = {
                "id": rec_id,
                "title": title,
                "status": "deferred",
                "linked_issue": None,
                "decision_ref": "",
                "_match_note": "GitHub API calls skipped (--no-github mode)",
                "_confidence": "low",
            }
        else:
            match_result = _match_recommendation(item_text, issues)
            confidence = match_result["confidence"]
            best_issue = match_result["best_issue"]

            if _rank.get(confidence, 0) > _rank.get(best_doc_confidence, 0):
                best_doc_confidence = confidence

            rec_entry = {
                "id": rec_id,
                "title": title,
                "status": match_result["suggested_status"],
                "linked_issue": best_issue["number"] if best_issue else None,
                "decision_ref": "",
                "_match_note": match_result["match_note"],
                "_confidence": confidence,
            }

        recommendations.append(rec_entry)

    doc_match_confidence = "low" if no_github else best_doc_confidence

    return {
        "doc": doc_rel,
        "doc_slug": slug,
        "generated_at": generated_at,
        "match_confidence": doc_match_confidence,
        "recommendations": recommendations,
    }


# ---------------------------------------------------------------------------
# Document scanning
# ---------------------------------------------------------------------------


def _scan_finalized_docs(docs_dir: Path) -> list[Path]:
    """Return all ``status: Final`` docs under *docs_dir*, sorted."""
    finalized: list[Path] = []
    for md_path in sorted(docs_dir.glob("*.md")):
        if md_path.name in _EXCLUDED_FILENAMES:
            continue
        if not md_path.is_file():
            continue
        text = md_path.read_text(encoding="utf-8")
        frontmatter = _parse_frontmatter_yaml(text, md_path)
        if frontmatter is None:
            continue
        if str(frontmatter.get("status", "")).strip() == "Final":
            finalized.append(md_path)
    return finalized


# ---------------------------------------------------------------------------
# Patch file I/O
# ---------------------------------------------------------------------------


def _write_patch_file(
    patch_data: dict[str, Any],
    patches_dir: Path,
    dry_run: bool,
) -> None:
    """Write a YAML patch file or print to stdout when *dry_run* is True."""
    slug = patch_data["doc_slug"]
    header = (
        f"# Suggested patch for {patch_data['doc']}\n# Review and edit before applying with Phase 6 patch application\n"
    )
    yaml_body = yaml.dump(
        patch_data,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )
    content = header + yaml_body

    if dry_run:
        print(f"\n--- {slug}.yml ---")
        print(content)
    else:
        patches_dir.mkdir(parents=True, exist_ok=True)
        patch_path = patches_dir / f"{slug}.yml"
        patch_path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:  # noqa: PLR0911
    """CLI entry point.  Returns an exit code (0 = success, 1 = error)."""
    parser = argparse.ArgumentParser(
        description="Audit recommendation status across finalized synthesis docs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print suggestions to stdout; do not write patch files",
    )
    parser.add_argument(
        "--doc",
        metavar="PATH",
        help="Audit a single doc instead of scanning all finalized docs",
    )
    parser.add_argument(
        "--no-github",
        action="store_true",
        help="Skip GitHub API calls; mark all recommendations as deferred",
    )
    parser.add_argument(
        "--docs-dir",
        metavar="PATH",
        default=None,
        help="Override docs/research directory (default: <repo-root>/docs/research)",
    )
    parser.add_argument(
        "--patches-dir",
        metavar="PATH",
        default=None,
        help="Override data/retrofit-patches directory",
    )

    args = parser.parse_args(argv)

    docs_dir = Path(args.docs_dir) if args.docs_dir else _DEFAULT_DOCS_DIR
    patches_dir = Path(args.patches_dir) if args.patches_dir else _DEFAULT_PATCHES_DIR

    if not docs_dir.exists():
        print(f"ERROR: docs-dir not found: {docs_dir}", file=sys.stderr)
        return 1

    # Determine which docs to process
    if args.doc:
        doc_path = Path(args.doc)
        if not doc_path.is_file():
            print(f"ERROR: --doc path not found: {doc_path}", file=sys.stderr)
            return 1
        doc_paths = [doc_path]
    else:
        doc_paths = _scan_finalized_docs(docs_dir)

    # Fetch GitHub issues (unless --no-github)
    issues: list[dict[str, Any]] = []
    if not args.no_github:
        print("Fetching GitHub issues with source:research label…", flush=True)
        issues = _fetch_github_issues()
        print(f"Fetched {len(issues)} issues.", flush=True)

    # Audit each doc and collect patch data
    patch_data_list: list[dict[str, Any]] = []
    skipped = 0

    for doc_path in doc_paths:
        patch_data = _audit_doc(doc_path, docs_dir, issues, args.no_github)
        if patch_data is None:
            skipped += 1
            continue
        patch_data_list.append(patch_data)
        _write_patch_file(patch_data, patches_dir, args.dry_run)

    # Summary statistics
    total_docs = len(patch_data_list)
    all_recs = [r for p in patch_data_list for r in p["recommendations"]]
    total_recs = len(all_recs)

    high_count = sum(1 for r in all_recs if r.get("_confidence") == "high")
    medium_count = sum(1 for r in all_recs if r.get("_confidence") == "medium")
    low_count = sum(1 for r in all_recs if r.get("_confidence") == "low")

    action = "Dry-run complete" if args.dry_run else "Audit complete"
    print(f"\n{action} — {total_docs} docs, {total_recs} recommendations ({skipped} skipped)")
    if not args.no_github:
        print(f"  High confidence matches:   {high_count}")
        print(f"  Medium confidence matches: {medium_count}")
        print(f"  Low/no match:              {low_count}")
    else:
        print("  (GitHub skipped — all recommendations marked as deferred)")
    if not args.dry_run:
        print(f"  Patch files written to {patches_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

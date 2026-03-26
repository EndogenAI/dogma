"""Apply approved provenance annotation patches to finalized research docs.

Purpose:
    Read YAML patch files from data/retrofit-patches/ and apply approved patches
    to their target research documents. Patches update the recommendations: frontmatter
    field. This script filters patches by status (approved-for-adoption) and tracks
    success/failure with structured JSON output.

Inputs:
    data/retrofit-patches/*.yml   Patch files with doc target and status.
    docs/research/*.md            Research documents with YAML frontmatter.

Outputs:
    Modified research docs with updated recommendations: frontmatter.
    Structured JSON report: provenance-patches-applied-<date>.json
    Exit code: 0 on full success, 1 if any patches failed.

Usage:
    uv run python scripts/apply_provenance_patches.py
    uv run python scripts/apply_provenance_patches.py --dry-run
    uv run python scripts/apply_provenance_patches.py --status-filter approved-for-adoption

Exit codes:
    0   All eligible patches applied successfully, or dry-run completed.
    1   One or more patches could not be applied.
    2   Invalid CLI usage.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)


def _parse_frontmatter_document(text: str, doc_path: Path) -> tuple[dict[str, Any], str] | None:
    """Return parsed frontmatter and body for *doc_path*, or None on failure."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return None

    frontmatter_text = match.group(1)
    try:
        frontmatter = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError:
        return None

    if not isinstance(frontmatter, dict):
        return None

    return frontmatter, text[match.end() :]


def _clean_recommendations(recommendations: list[Any]) -> list[dict[str, Any]]:
    """Strip patch-only metadata from recommendation entries."""
    clean_recs: list[dict[str, Any]] = []
    for recommendation in recommendations:
        if not isinstance(recommendation, dict):
            continue
        clean_recs.append(
            {key: value for key, value in recommendation.items() if key not in {"_match_note", "_confidence"}}
        )
    return clean_recs


def _repo_root() -> Path:
    """Return the repository root for this script."""
    return Path(__file__).resolve().parent.parent


def _rel(path: Path, repo_root: Path) -> str:
    """Return *path* relative to *repo_root* for portable report output."""
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def apply_patches(
    patch_dir: Path | None = None,
    *,
    status_filter: str | None = None,
    dry_run: bool = False,
) -> tuple[int, list[dict[str, Any]]]:
    """Apply all eligible patches and return (exit_code, results_list)."""
    repo_root = _repo_root()
    if patch_dir is None:
        patch_dir = repo_root / "data" / "retrofit-patches"
    elif not patch_dir.is_absolute():
        patch_dir = repo_root / patch_dir

    results: list[dict[str, Any]] = []
    had_errors = False

    patch_files = sorted(patch_dir.glob("*.yml"))
    if not patch_files:
        print(f"Warning: No patch files found in {patch_dir}")
        return 0, results

    for patch_path in patch_files:
        try:
            patch_data = yaml.safe_load(patch_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            result = {
                "patch_id": patch_path.stem,
                "document": "unknown",
                "status": "ERROR",
                "error": f"YAML parse error: {exc}",
            }
            results.append(result)
            had_errors = True
            continue

        if not isinstance(patch_data, dict):
            result = {
                "patch_id": patch_path.stem,
                "document": "unknown",
                "status": "ERROR",
                "error": "Patch file must decode to a mapping",
            }
            results.append(result)
            had_errors = True
            continue

        # Check approval status if filter is specified
        if status_filter:
            patch_status = patch_data.get("status", "pending")
            if patch_status != status_filter:
                result = {
                    "patch_id": patch_path.stem,
                    "document": patch_data.get("doc", "unknown"),
                    "status": "SKIPPED",
                    "reason": f"Patch status '{patch_status}' does not match filter '{status_filter}'",
                }
                results.append(result)
                continue

        doc_value = patch_data.get("doc")
        if not isinstance(doc_value, str) or not doc_value.strip():
            result = {
                "patch_id": patch_path.stem,
                "document": "unknown",
                "status": "ERROR",
                "error": "Patch missing required 'doc' field",
            }
            results.append(result)
            had_errors = True
            continue

        doc_path = Path(doc_value)
        if not doc_path.is_absolute():
            doc_path = repo_root / doc_path

        if not doc_path.exists():
            result = {
                "patch_id": patch_path.stem,
                "document": _rel(doc_path, repo_root),
                "status": "ERROR",
                "error": "Target document does not exist",
            }
            results.append(result)
            had_errors = True
            continue

        recommendations = patch_data.get("recommendations", [])
        if not isinstance(recommendations, list):
            result = {
                "patch_id": patch_path.stem,
                "document": _rel(doc_path, repo_root),
                "status": "ERROR",
                "error": "Field 'recommendations' must be a YAML list",
            }
            results.append(result)
            had_errors = True
            continue

        if not recommendations:
            result = {
                "patch_id": patch_path.stem,
                "document": _rel(doc_path, repo_root),
                "status": "SKIPPED",
                "reason": "Patch has no recommendations to apply",
            }
            results.append(result)
            continue

        clean_recs = _clean_recommendations(recommendations)
        if recommendations and not clean_recs:
            result = {
                "patch_id": patch_path.stem,
                "document": _rel(doc_path, repo_root),
                "status": "ERROR",
                "error": "Recommendations list contained no valid mappings",
            }
            results.append(result)
            had_errors = True
            continue

        try:
            content = doc_path.read_text(encoding="utf-8")
        except OSError as exc:
            result = {
                "patch_id": patch_path.stem,
                "document": _rel(doc_path, repo_root),
                "status": "ERROR",
                "error": f"Cannot read document: {exc}",
            }
            results.append(result)
            had_errors = True
            continue

        parsed = _parse_frontmatter_document(content, doc_path)
        if parsed is None:
            result = {
                "patch_id": patch_path.stem,
                "document": _rel(doc_path, repo_root),
                "status": "ERROR",
                "error": "Document has malformed frontmatter",
            }
            results.append(result)
            had_errors = True
            continue

        frontmatter, body = parsed
        old_rec_count = len(frontmatter.get("recommendations", []))
        frontmatter["recommendations"] = clean_recs

        try:
            new_frontmatter_text = yaml.dump(frontmatter, sort_keys=False, allow_unicode=True)
            new_content = f"---\n{new_frontmatter_text}---\n{body}"

            if not dry_run:
                doc_path.write_text(new_content, encoding="utf-8")

            result = {
                "patch_id": patch_path.stem,
                "document": _rel(doc_path, repo_root),
                "status": "APPLIED" if not dry_run else "WOULD_APPLY",
                "old_recommendation_count": old_rec_count,
                "new_recommendation_count": len(clean_recs),
                "change_summary": f"Updated {len(clean_recs)} recommendations",
            }
            results.append(result)

        except Exception as exc:
            result = {
                "patch_id": patch_path.stem,
                "document": _rel(doc_path, repo_root),
                "status": "ERROR",
                "error": f"Write error: {exc}",
            }
            results.append(result)
            had_errors = True

    return (1 if had_errors else 0, results)


def main() -> int:
    """Entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Apply approved provenance patches to finalized research docs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--patch-dir",
        type=Path,
        default=None,
        help="Path to patches directory (default: data/retrofit-patches)",
    )
    parser.add_argument(
        "--status-filter",
        type=str,
        default="approved-for-adoption",
        help="Only apply patches with this status (default: approved-for-adoption)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview patches without modifying documents",
    )
    parser.add_argument(
        "--json-report",
        type=Path,
        default=None,
        help="Write structured JSON report to this path (default: provenance-patches-applied-<date>.json)",
    )

    args = parser.parse_args()

    # Apply patches
    exit_code, results = apply_patches(
        patch_dir=args.patch_dir,
        status_filter=args.status_filter,
        dry_run=args.dry_run,
    )

    # Determine report filename
    if args.json_report:
        report_path = args.json_report
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
        report_path = Path(f"provenance-patches-applied-{date_str}.json")

    # Write report
    report = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": args.dry_run,
        "status_filter": args.status_filter,
        "total_patches": len(results),
        "applied_count": sum(1 for r in results if r["status"] == "APPLIED"),
        "would_apply_count": sum(1 for r in results if r["status"] == "WOULD_APPLY"),
        "skipped_count": sum(1 for r in results if r["status"] == "SKIPPED"),
        "error_count": sum(1 for r in results if r["status"] == "ERROR"),
        "patches": results,
    }

    try:
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Report: {report_path}")
        print(f"  Applied: {report['applied_count']}")
        print(f"  Would Apply: {report['would_apply_count']}")
        print(f"  Skipped: {report['skipped_count']}")
        print(f"  Errors: {report['error_count']}")
    except OSError as exc:
        print(f"Warning: Could not write report: {exc}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

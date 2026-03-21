"""scripts/index_recommendations.py

Scans all finalized synthesis documents in docs/research/ and writes a structured
registry of their ``recommendations:`` frontmatter entries to
``data/recommendations-registry.yml``.

Purpose:
    Provide a single, machine-readable index of every recommendation recorded in
    the synthesis corpus so that provenance can be queried programmatically — e.g.
    "which recommendations are untracked?", "which are still open?", "which issue
    closed rec-X?".  This implements the Programmatic-First principle from
    AGENTS.md: provenance data that was previously inferred interactively from
    issue threads is now encoded as structured YAML and kept in sync by CI.

Inputs:
    docs/research/*.md          — all finalized D4 synthesis documents
                                   (must have ``status: Final`` in frontmatter)
    --docs-dir <path>           — override the docs/research search root
                                   (default: <repo-root>/docs/research)

Outputs:
    data/recommendations-registry.yml  — YAML registry (written by default run)

Exit codes:
    0   Success (default / --dry-run / --check-fresh)
    0   Warning printed for docs with malformed YAML frontmatter (warn-and-skip behavior)
    1   --check mode: registry is stale (or missing)

Usage examples:
    # Write the registry
    uv run python scripts/index_recommendations.py

    # Preview without writing
    uv run python scripts/index_recommendations.py --dry-run

    # CI gate: exit 1 if registry is stale
    uv run python scripts/index_recommendations.py --check

    # Override docs directory (useful for testing)
    uv run python scripts/index_recommendations.py --docs-dir /tmp/test-docs
"""

from __future__ import annotations

import argparse
import re
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
_REGISTRY_PATH = _REPO_ROOT / "data" / "recommendations-registry.yml"
_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

# Files that exist under docs/research/ but are not D4 synthesis documents.
_EXCLUDED_FILENAMES = {"OPEN_RESEARCH.md"}


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------


def _parse_frontmatter_yaml(text: str, file_path: Path) -> dict[str, Any] | None:
    """Parse the YAML frontmatter block from *text*.

    Returns the parsed dict, or ``None`` if the YAML is malformed (caller should
    emit a warning and skip the file).  Returns ``{}`` if no frontmatter block exists.
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


# ---------------------------------------------------------------------------
# Document scanning
# ---------------------------------------------------------------------------


def _doc_slug(doc_path: Path, docs_dir: Path) -> str:
    """Return a stable slug for *doc_path* relative to *docs_dir*."""
    rel = doc_path.relative_to(docs_dir)
    return rel.stem


def scan_docs(docs_dir: Path) -> tuple[list[dict[str, Any]], list[str], int, int]:
    """Scan *docs_dir* for finalized synthesis docs with recommendations.

    Returns:
        records:              list of recommendation record dicts ready for the registry
        warnings:             list of warning strings for docs missing a recommendations block
        docs_scanned:         count of finalized docs successfully scanned
        docs_with_recs:       count of finalized docs that have a recommendations block
    """
    records: list[dict[str, Any]] = []
    warnings: list[str] = []
    docs_scanned = 0
    docs_with_recs = 0

    md_files = sorted(docs_dir.glob("*.md"))

    for md_path in md_files:
        if md_path.name in _EXCLUDED_FILENAMES:
            continue
        # Skip sub-directories (sources/)
        if not md_path.is_file():
            continue

        text = md_path.read_text(encoding="utf-8")
        frontmatter = _parse_frontmatter_yaml(text, md_path)
        if frontmatter is None:
            # Malformed YAML — warning already printed; skip this file
            continue

        if str(frontmatter.get("status", "")).strip() != "Final":
            continue

        docs_scanned += 1

        recs = frontmatter.get("recommendations")
        if not recs:
            warnings.append(f"WARNING: {md_path} has no recommendations: block (may need retrofit)")
            continue

        docs_with_recs += 1
        slug = _doc_slug(md_path, docs_dir)
        try:
            doc_rel = str(md_path.relative_to(_REPO_ROOT))
        except ValueError:
            # Path is outside repo root (e.g. during testing with tmp_path)
            doc_rel = str(md_path)

        for entry in recs:
            record: dict[str, Any] = {
                "doc": doc_rel,
                "doc_slug": slug,
                "id": entry.get("id", ""),
                "title": entry.get("title", ""),
                "status": entry.get("status", ""),
                "linked_issue": entry.get("linked_issue", None),
                "decision_ref": entry.get("decision_ref", ""),
            }
            records.append(record)

    return records, warnings, docs_scanned, docs_with_recs


# ---------------------------------------------------------------------------
# Registry I/O
# ---------------------------------------------------------------------------


def _build_registry(
    records: list[dict[str, Any]],
    docs_scanned: int,
    docs_with_recommendations: int,
    generated_at: str,
) -> dict[str, Any]:
    return {
        "generated_at": generated_at,
        "docs_scanned": docs_scanned,
        "docs_with_recommendations": docs_with_recommendations,
        "recommendations": records,
    }


def _registry_header() -> str:
    return (
        "# Auto-generated by scripts/index_recommendations.py — do not edit manually\n"
        "# Run: uv run python scripts/index_recommendations.py\n"
    )


def _serialize_registry(registry: dict[str, Any]) -> str:
    """Serialize *registry* to YAML text with a comment header."""
    return _registry_header() + yaml.dump(
        registry,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )


def _load_existing_registry(path: Path) -> dict[str, Any] | None:
    """Load and parse the existing registry file, or return None if absent/invalid."""
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
        # Strip comment lines before parsing
        yaml_text = "\n".join(line for line in text.splitlines() if not line.startswith("#"))
        return yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError:
        return None


def _is_stale(
    current_records: list[dict[str, Any]],
    existing_registry: dict[str, Any] | None,
) -> bool:
    """Return True if *existing_registry* does not match *current_records*."""
    if existing_registry is None:
        return True
    existing_recs = existing_registry.get("recommendations") or []

    # Compare as sorted lists of (id, status, linked_issue, decision_ref) tuples
    # to ignore generated_at timestamp differences.
    def _key(r: dict[str, Any]) -> tuple:
        return (
            r.get("doc", ""),
            r.get("id", ""),
            r.get("title", ""),
            r.get("status", ""),
            str(r.get("linked_issue", "")),
            r.get("decision_ref", ""),
        )

    return sorted(current_records, key=_key) != sorted(existing_recs, key=_key)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:  # noqa: C901
    parser = argparse.ArgumentParser(description="Index recommendations from finalized synthesis docs.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without writing the registry file.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 0 if registry is up to date; exit 1 if stale or missing.",
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=_DEFAULT_DOCS_DIR,
        help="Directory to scan for finalized synthesis docs (default: docs/research/).",
    )
    args = parser.parse_args(argv)

    docs_dir: Path = args.docs_dir.resolve()
    if not docs_dir.is_dir():
        print(f"ERROR: docs-dir does not exist: {docs_dir}", file=sys.stderr)
        return 1

    # Scan docs
    records, warnings, docs_scanned, docs_with_recs = scan_docs(docs_dir)

    # Emit warnings
    for warning in warnings:
        print(warning)

    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    registry = _build_registry(records, docs_scanned, docs_with_recs, generated_at)
    serialized = _serialize_registry(registry)

    if args.check:
        existing = _load_existing_registry(_REGISTRY_PATH)
        if _is_stale(records, existing):
            print(
                "STALE: recommendations-registry.yml is out of date. "
                "Run: uv run python scripts/index_recommendations.py"
            )
            return 1
        print("OK: recommendations-registry.yml is up to date.")
        return 0

    if args.dry_run:
        print("[DRY RUN] Would write data/recommendations-registry.yml:")
        print(serialized)
        print(
            f"[DRY RUN] {docs_scanned} docs scanned, "
            f"{docs_with_recs} with recommendations, "
            f"{len(records)} total recommendation entries."
        )
        return 0

    # Write registry
    _REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    _REGISTRY_PATH.write_text(serialized, encoding="utf-8")
    print(
        f"Wrote data/recommendations-registry.yml — "
        f"{docs_scanned} docs scanned, "
        f"{docs_with_recs} with recommendations, "
        f"{len(records)} total recommendation entries."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

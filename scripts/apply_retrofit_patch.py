"""Apply recommendation retrofit patches to research docs.

Purpose:
    Read YAML patch files from data/retrofit-patches/ and replace each target
    research document's ``recommendations:`` frontmatter list with the patch's
    authoritative recommendation list after removing patch-only metadata.

Inputs:
    data/retrofit-patches/*.yml   Patch files with an authoritative ``doc`` field.
    docs/research/*.md            Research documents with YAML frontmatter.

Outputs:
    Updated research documents with refreshed ``recommendations:`` frontmatter,
    or a dry-run preview of the files that would be rewritten.

Usage:
    uv run python scripts/apply_retrofit_patch.py
    uv run python scripts/apply_retrofit_patch.py --dry-run
    uv run python scripts/apply_retrofit_patch.py --patch-dir data/retrofit-patches

Exit codes:
    0   All eligible patches applied successfully, or dry-run completed without errors.
    1   One or more patches could not be applied because a patch file or target
        document was invalid.
    2   Invalid CLI usage (handled by argparse).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)


def _parse_frontmatter_document(text: str, doc_path: Path) -> tuple[dict[str, Any], str] | None:
    """Return parsed frontmatter and body for *doc_path*, or None on failure."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        print(f"Error: {doc_path} has malformed frontmatter.")
        return None

    frontmatter_text = match.group(1)
    try:
        frontmatter = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError as exc:
        print(f"Error parsing frontmatter in {doc_path}: {exc}")
        print("Frontmatter content:")
        print(frontmatter_text)
        return None

    if not isinstance(frontmatter, dict):
        print(f"Error: frontmatter in {doc_path} must decode to a mapping.")
        return None

    return frontmatter, text[match.end() :]


def _clean_recommendations(recommendations: list[Any], patch_path: Path) -> list[dict[str, Any]]:
    """Strip patch-only metadata from recommendation entries."""
    clean_recs: list[dict[str, Any]] = []
    for index, recommendation in enumerate(recommendations, start=1):
        if not isinstance(recommendation, dict):
            print(
                f"Warning: {patch_path} recommendations[{index}] is {type(recommendation).__name__}, "
                "expected mapping; skipping."
            )
            continue
        clean_recs.append(
            {key: value for key, value in recommendation.items() if key not in {"_match_note", "_confidence"}}
        )
    return clean_recs


def _repo_root() -> Path:
    """Return the repository root for this script."""
    return Path(__file__).resolve().parent.parent


def patch_docs(patch_dir: Path | None = None, *, dry_run: bool = False) -> int:
    """Apply all retrofit patch files found in *patch_dir* and return an exit code."""
    repo_root = _repo_root()
    if patch_dir is None:
        patch_dir = repo_root / "data" / "retrofit-patches"
    elif not patch_dir.is_absolute():
        patch_dir = repo_root / patch_dir

    had_errors = False

    for patch_path in sorted(patch_dir.glob("*.yml")):
        print(f"Applying {patch_path.name}...")
        try:
            patch_data = yaml.safe_load(patch_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            print(f"Error parsing {patch_path}: {exc}")
            had_errors = True
            continue

        if not isinstance(patch_data, dict):
            print(f"Error: {patch_path} must decode to a mapping.")
            had_errors = True
            continue

        doc_value = patch_data.get("doc")
        if not isinstance(doc_value, str) or not doc_value.strip():
            print(f"Error: {patch_path} missing required 'doc' field.")
            had_errors = True
            continue

        doc_path = Path(doc_value)
        if not doc_path.is_absolute():
            doc_path = repo_root / doc_path

        if not doc_path.exists():
            print(f"Warning: Document {doc_path} does not exist.")
            had_errors = True
            continue

        recommendations = patch_data.get("recommendations", [])
        if not isinstance(recommendations, list):
            print(f"Error: {patch_path} field 'recommendations' must be a YAML list.")
            had_errors = True
            continue
        if not recommendations:
            continue

        clean_recs = _clean_recommendations(recommendations, patch_path)
        if recommendations and not clean_recs:
            print(
                f"Error: {patch_path} recommendations list contained no valid mappings; "
                "leaving target document unchanged."
            )
            had_errors = True
            continue

        content = doc_path.read_text(encoding="utf-8")
        parsed = _parse_frontmatter_document(content, doc_path)
        if parsed is None:
            had_errors = True
            continue

        frontmatter, body = parsed
        frontmatter["recommendations"] = clean_recs

        new_frontmatter_text = yaml.dump(frontmatter, sort_keys=False, allow_unicode=True)
        new_content = f"---\n{new_frontmatter_text}---\n{body}"
        if dry_run:
            print(f"Dry run: would patch {doc_path.name}")
            continue

        doc_path.write_text(new_content, encoding="utf-8")
        print(f"Patched {doc_path.name}")

    return 1 if had_errors else 0


def _build_parser() -> argparse.ArgumentParser:
    """Return the CLI parser for the retrofit patch applier."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument(
        "--patch-dir",
        type=Path,
        default=None,
        help="Directory containing retrofit patch YAML files. Defaults to data/retrofit-patches/.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate patches and print which documents would be rewritten without modifying files.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    return patch_docs(args.patch_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())

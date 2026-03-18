"""
annotate_provenance.py
----------------------
Purpose:
    Scans Markdown and .agent.md files in a given scope for MANIFESTO.md axiom
    name mentions in the file body and suggests (or writes in-place) a 'x-governs:'
    YAML frontmatter annotation linking the file to the axioms it references.

    Enacts Pattern P1 (File-Level Provenance via x-governs: Annotation) from
    docs/research/value-provenance.md: makes the chain-of-custody relationship
    between agent files and foundational axioms explicit and machine-checkable.

    Controlled vocabulary: axiom names are sourced from MANIFESTO.md H2/H3 headings
    (primary) and the link registry concepts (supplementary). No axiom names are
    hardcoded as literals in this script.

Inputs:
    --scope       PATH   File or directory to annotate (default: .github/agents/)
    --dry-run            Preview proposed annotations; write nothing
    --registry    PATH   Path to link registry YAML (default: data/link_registry.yml)
    --manifesto   PATH   Path to MANIFESTO.md for axiom vocabulary
                         (default: auto-resolved MANIFESTO.md at repo root)
    --no-recurse         Process only files directly in --scope (no subdirectories)

Outputs:
    For each file that receives (or would receive) a x-governs: annotation:
        [ANNOTATE] path/to/file.md  x-governs: [axiom-one, axiom-two]
    For files already annotated:
        [SKIP] path/to/file.md  already has x-governs:
    For files with no axiom mentions:
        [SKIP] path/to/file.md  no axiom mentions found
    Summary line: "N files annotated (or would annotate), M files skipped"

Exit codes:
    0: success (annotations applied or previewed)
    1: error (registry not found, MANIFESTO.md not found, scope not found, or I/O failure)

Usage examples:
    uv run python scripts/annotate_provenance.py --dry-run
    uv run python scripts/annotate_provenance.py --scope .github/agents/ --dry-run
    uv run python scripts/annotate_provenance.py --scope docs/guides/testing.md
    uv run python scripts/annotate_provenance.py --scope docs/ --no-recurse
    uv run python scripts/annotate_provenance.py --registry data/link_registry.yml --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

import yaml

# ---------------------------------------------------------------------------
# Repo root resolution
# ---------------------------------------------------------------------------


def find_repo_root() -> Path:
    """Walk up from this file until pyproject.toml is found."""
    for parent in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


# ---------------------------------------------------------------------------
# Axiom vocabulary
# ---------------------------------------------------------------------------


class Axiom(NamedTuple):
    display_name: str  # original heading text after stripping numeric prefix
    norm_name: str  # lowercase-hyphenated form used in x-governs: values


def _strip_numeric_prefix(heading: str) -> str:
    """Strip leading numeric/symbol prefixes like '1. ', '2) ', inline markup."""
    heading = re.sub(r"[`*_]", "", heading).strip()
    return re.sub(r"^[0-9]+(?:\.[0-9]+)*\s*[\.\)]?\s*", "", heading)


def _normalise(name: str) -> str:
    """Convert a display name to lowercase-hyphenated form."""
    return re.sub(r"\s+", "-", name.strip()).lower()


def load_axioms_from_manifesto(manifesto_path: Path) -> list[Axiom]:
    """Extract axioms from H2/H3 headings in MANIFESTO.md."""
    text = manifesto_path.read_text(encoding="utf-8")
    headings = re.findall(r"^#{2,3}\s+(.+)$", text, re.MULTILINE)
    result: list[Axiom] = []
    for h in headings:
        display = _strip_numeric_prefix(h)
        if display:
            result.append(Axiom(display_name=display, norm_name=_normalise(display)))
    return result


def load_axioms_from_registry(registry_path: Path) -> list[Axiom]:
    """Extract concept names from link registry as supplementary axiom source."""
    if not registry_path.exists():
        return []
    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return []
    result: list[Axiom] = []
    for entry in data.get("concepts", []):
        concept = entry.get("concept", "")
        if concept:
            result.append(Axiom(display_name=concept, norm_name=_normalise(concept)))
    return result


def merge_axioms(manifesto_axioms: list[Axiom], registry_axioms: list[Axiom]) -> list[Axiom]:
    """Merge axiom lists, deduplicating by norm_name. Manifesto takes precedence."""
    seen: set[str] = set()
    result: list[Axiom] = []
    for a in manifesto_axioms + registry_axioms:
        if a.norm_name not in seen:
            seen.add(a.norm_name)
            result.append(a)
    return result


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------


def extract_frontmatter(text: str) -> tuple[str | None, int]:
    """Return (raw_yaml_text, body_start_index) or (None, 0) if no frontmatter."""
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.DOTALL)
    if match:
        return match.group(1), match.end()
    return None, 0


def has_x_governs_annotation(text: str) -> bool:
    """Return True if text has a non-empty x-governs: frontmatter field."""
    fm_raw, _ = extract_frontmatter(text)
    if fm_raw is None:
        return False
    try:
        fm_data = yaml.safe_load(fm_raw) or {}
    except yaml.YAMLError:
        # Fallback: regex check
        return bool(re.search(r"^x-governs\s*:", fm_raw, re.MULTILINE))
    x_governs = fm_data.get("x-governs")
    if x_governs is None:
        return False
    if isinstance(x_governs, list):
        return len(x_governs) > 0
    return bool(str(x_governs).strip())


# ---------------------------------------------------------------------------
# Axiom mention detection
# ---------------------------------------------------------------------------


def find_axiom_mentions(body: str, axioms: list[Axiom]) -> list[Axiom]:
    """Return axioms whose display_name appears in body (case-insensitive, word-boundary)."""
    found: list[Axiom] = []
    for axiom in axioms:
        pattern = r"\b" + re.escape(axiom.display_name) + r"\b"
        if re.search(pattern, body, re.IGNORECASE):
            found.append(axiom)
    return found


# ---------------------------------------------------------------------------
# Governs annotation writing
# ---------------------------------------------------------------------------


def build_x_governs_block(axioms: list[Axiom]) -> str:
    """Build a YAML x-governs: block string (without trailing newline)."""
    lines = ["x-governs:"]
    for a in axioms:
        lines.append(f"  - {a.norm_name}")
    return "\n".join(lines)


def insert_x_governs_into_frontmatter(text: str, x_governs_block: str) -> str:
    """Insert x-governs: block before the closing --- of existing frontmatter."""
    match = re.match(r"^(---\r?\n.*?)(\r?\n---\r?\n?)", text, re.DOTALL)
    if match:
        fm_content = match.group(1)
        closing = match.group(2)
        rest = text[match.end() :]
        return fm_content + "\n" + x_governs_block + closing + rest
    return text


def prepend_frontmatter(text: str, x_governs_block: str) -> str:
    """Prepend a new frontmatter block to a file that has none."""
    return f"---\n{x_governs_block}\n---\n\n" + text


def apply_x_governs_annotation(text: str, axioms: list[Axiom]) -> str:
    """Add x-governs: annotation to file content. Returns modified text."""
    x_governs_block = build_x_governs_block(axioms)
    fm_raw, _ = extract_frontmatter(text)
    if fm_raw is not None:
        return insert_x_governs_into_frontmatter(text, x_governs_block)
    return prepend_frontmatter(text, x_governs_block)


# ---------------------------------------------------------------------------
# File processing
# ---------------------------------------------------------------------------


def process_file(
    filepath: Path,
    axioms: list[Axiom],
    dry_run: bool,
) -> tuple[str, list[str]]:
    """Process a single file for x-governs: annotation.

    Returns (status, suggested_axiom_norms) where status is one of:
      'annotated'            — annotation written (or would be, if dry_run)
      'skipped_existing'     — file already has x-governs:
      'skipped_no_mentions'  — no axiom mentions found in body
      'error'                — I/O or read error
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"WARNING: cannot read {filepath}: {exc}", file=sys.stderr)
        return "error", []

    if has_x_governs_annotation(text):
        return "skipped_existing", []

    _, fm_end = extract_frontmatter(text)
    body = text[fm_end:]
    found = find_axiom_mentions(body, axioms)

    if not found:
        return "skipped_no_mentions", []

    if not dry_run:
        new_text = apply_x_governs_annotation(text, found)
        try:
            filepath.write_text(new_text, encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: cannot write {filepath}: {exc}", file=sys.stderr)
            return "error", []

    return "annotated", [a.norm_name for a in found]


def collect_files(scope: Path, no_recurse: bool) -> list[Path]:
    """Collect .md and .agent.md files in scope."""
    if scope.is_file():
        return [scope]
    glob_fn = scope.glob if no_recurse else scope.rglob
    return sorted(glob_fn("*.md"))


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    repo_root = find_repo_root()
    parser = argparse.ArgumentParser(
        description="Annotate files with x-governs: frontmatter based on MANIFESTO.md axiom mentions."
    )
    parser.add_argument(
        "--scope",
        default=str(repo_root / ".github" / "agents"),
        help="File or directory to annotate (default: .github/agents/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview proposed annotations; write nothing",
    )
    parser.add_argument(
        "--registry",
        default=str(repo_root / "data" / "link_registry.yml"),
        help="Path to link registry YAML (default: data/link_registry.yml)",
    )
    parser.add_argument(
        "--manifesto",
        default=str(repo_root / "MANIFESTO.md"),
        help="Path to MANIFESTO.md for axiom vocabulary (default: repo root MANIFESTO.md)",
    )
    parser.add_argument(
        "--no-recurse",
        action="store_true",
        help="Process only files directly in --scope (no subdirectories)",
    )
    args = parser.parse_args(argv)

    registry_path = Path(args.registry)
    if not registry_path.exists():
        print(f"ERROR: registry not found: {registry_path}", file=sys.stderr)
        return 1

    manifesto_path = Path(args.manifesto)
    if not manifesto_path.exists():
        print(f"ERROR: MANIFESTO.md not found: {manifesto_path}", file=sys.stderr)
        return 1

    manifesto_axioms = load_axioms_from_manifesto(manifesto_path)
    registry_axioms = load_axioms_from_registry(registry_path)
    axioms = merge_axioms(manifesto_axioms, registry_axioms)

    scope_path = Path(args.scope)
    if not scope_path.exists():
        print(f"ERROR: scope not found: {scope_path}", file=sys.stderr)
        return 1

    files = collect_files(scope_path, args.no_recurse)
    annotated = 0
    skipped = 0

    for filepath in files:
        status, suggested = process_file(filepath, axioms, args.dry_run)
        try:
            display_path = filepath.relative_to(repo_root)
        except ValueError:
            display_path = filepath

        if status == "annotated":
            annotated += 1
            label = "[DRY RUN] Would annotate" if args.dry_run else "[ANNOTATE]"
            print(f"{label} {display_path}  x-governs: [{', '.join(suggested)}]")
        elif status == "skipped_existing":
            skipped += 1
            print(f"[SKIP] {display_path}  already has x-governs:")
        elif status == "skipped_no_mentions":
            skipped += 1
            print(f"[SKIP] {display_path}  no axiom mentions found")

    action = "would annotate" if args.dry_run else "annotated"
    print(f"\n{annotated} files {action}, {skipped} files skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())

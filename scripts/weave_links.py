"""
weave_links.py
--------------
Purpose:
    Programmatically injects Markdown cross-reference links across the
    EndogenAI/Workflows documentation corpus. Reads a YAML concept registry
    (data/link_registry.yml) and wraps every unlinked occurrence of a registered
    concept name with [concept](canonical_source).

    Enacts the Documentation-First principle from AGENTS.md: every change to a
    workflow, agent, or script must be accompanied by clear, navigable
    documentation — and the documentation itself warrants tooling investment.

Inputs:
    --scope       File or directory path to process (default: docs/)
    --dry-run     Preview injections without writing files
    --registry    Path to link registry YAML (default: data/link_registry.yml)

Outputs:
    Prints "N injections in M files" to stdout.
    With --dry-run: also prints diff lines showing what would change.

Idempotency guarantee:
    Running weave_links.py twice on the same corpus produces no diff on the
    second run. The is_already_linked() guard checks for an existing Markdown
    link before each injection.

Exit codes:
    0: success
    1: registry not found or schema error

Usage examples:
    uv run python scripts/weave_links.py --dry-run
    uv run python scripts/weave_links.py --scope docs/guides/
    uv run python scripts/weave_links.py --scope docs/guides/testing.md --dry-run
    uv run python scripts/weave_links.py --registry data/link_registry.yml
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

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
# Registry loading
# ---------------------------------------------------------------------------


def load_registry(path: Path) -> list[dict]:
    """Load and validate the link registry YAML.

    Each entry must have: concept, canonical_source, aliases.
    scopes is optional (default: all files).
    Raises KeyError if a required field is missing.
    Raises ValueError if canonical_source is not a safe relative path or https:// URL.
    """
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    entries = data.get("concepts", [])
    _safe_path = re.compile(r"^[a-zA-Z0-9_.][a-zA-Z0-9_./# -]*$")
    for entry in entries:
        for required in ("concept", "canonical_source", "aliases"):
            if required not in entry:
                raise KeyError(f"Registry entry missing required field: {required!r}")
        src = entry["canonical_source"]
        if src.startswith("https://"):
            pass  # always valid
        elif src.startswith("/") or src.startswith("//"):
            raise ValueError(f"Unsafe canonical_source {src!r}: absolute/scheme-relative paths not allowed")
        elif not _safe_path.match(src):
            raise ValueError(f"Unsafe canonical_source {src!r}: must be a relative path or https:// URL")
    return entries


# ---------------------------------------------------------------------------
# Idempotency guard
# ---------------------------------------------------------------------------


def is_already_linked(line: str, canonical_source: str) -> bool:
    """Return True if line already contains a Markdown link to canonical_source."""
    escaped = re.escape(canonical_source)
    return bool(re.search(r"\[.*?\]\(" + escaped, line))


def is_inside_any_link(line: str, match: re.Match) -> bool:  # type: ignore[type-arg]
    """Return True if the matched span is already inside a Markdown link construct.

    Prevents injecting link text inside existing link text or URL spans, which
    would produce nested/broken Markdown like [[text](A)](B).
    """
    before = line[: match.start()]
    after = line[match.end() :]
    # Inside link text: [...<match>...](url) — unclosed [ before and ]( immediately after
    if "[" in before and re.search(r"^\s*\]\(", after):
        return True
    # Inside link URL: [text](...<match>...) — unclosed ]( before, no closing ) yet
    if re.search(r"\]\([^\)]*$", before):
        return True
    return False


# ---------------------------------------------------------------------------
# Mention detection
# ---------------------------------------------------------------------------


def find_mentions(text: str, entry: dict) -> list[tuple]:
    """Return (line_number, matched_term) for unlinked concept/alias occurrences.

    Skips lines where is_already_linked() is True.
    Case-insensitive word-boundary matching.
    """
    canonical_source = entry["canonical_source"]
    terms = [entry["concept"]] + list(entry.get("aliases", []))
    results = []
    for i, line in enumerate(text.splitlines(), 1):
        if is_already_linked(line, canonical_source):
            continue
        for term in terms:
            if re.search(r"\b" + re.escape(term) + r"\b", line, re.IGNORECASE):
                results.append((i, term))
                break  # one report per line
    return results


# ---------------------------------------------------------------------------
# Link injection
# ---------------------------------------------------------------------------


def inject_link(text: str, entry: dict, dry_run: bool) -> tuple[str, list[str]]:
    """Wrap the FIRST unlinked occurrence of concept per paragraph.

    Returns (modified_text, diff_lines).
    If dry_run=True, text is returned unchanged but diff_lines reflects what
    would change.
    Idempotent: second call on already-wrapped text produces zero diff.
    """
    concept = entry["concept"]
    canonical_source = entry["canonical_source"]
    terms = [concept] + list(entry.get("aliases", []))

    diff_lines: list[str] = []
    paragraphs = text.split("\n\n")
    new_paragraphs: list[str] = []

    for para in paragraphs:
        new_para = para
        for term in terms:
            pattern = r"\b" + re.escape(term) + r"\b"
            para_lines = para.splitlines()
            modified = False
            for j, line in enumerate(para_lines):
                if is_already_linked(line, canonical_source):
                    continue
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    if is_inside_any_link(line, match):
                        continue
                    matched_text = match.group(0)
                    new_line = line[: match.start()] + f"[{matched_text}]({canonical_source})" + line[match.end() :]
                    diff_lines.append(f"- {line}")
                    diff_lines.append(f"+ {new_line}")
                    para_lines[j] = new_line
                    new_para = "\n".join(para_lines)
                    modified = True
                    break  # first occurrence in paragraph only
            if modified:
                break  # first matching term wins
        new_paragraphs.append(new_para)

    result_text = "\n\n".join(new_paragraphs)
    if dry_run:
        return text, diff_lines
    return result_text, diff_lines


# ---------------------------------------------------------------------------
# Canonical source path resolution
# ---------------------------------------------------------------------------


def resolve_canonical_source(canonical_source: str, filepath: Path, repo_root: Path) -> str:
    """Compute a Markdown-safe relative link path from filepath to canonical_source.

    canonical_source is repo-root-relative (e.g. 'MANIFESTO.md', 'docs/guides/agents.md').
    Returns a POSIX relative path suitable for use in Markdown links.
    https:// sources are returned unchanged.
    """
    if canonical_source.startswith("https://"):
        return canonical_source
    # Split off any #fragment
    parts = canonical_source.split("#", 1)
    path_part = parts[0]
    fragment = "#" + parts[1] if len(parts) > 1 else ""
    target = repo_root / path_part
    rel = os.path.relpath(str(target), str(filepath.parent))
    return rel.replace("\\", "/") + fragment


# ---------------------------------------------------------------------------
# File processing
# ---------------------------------------------------------------------------


def weave_file(filepath: Path, registry: list[dict], dry_run: bool, repo_root: Path) -> int:
    """Apply link injection for all registry entries to a single file.

    Checks filepath is within an entry's scopes before injecting.
    Writes file only if not dry_run and changes exist.
    Returns count of injections made.
    """
    text = filepath.read_text(encoding="utf-8")
    modified_text = text
    total_injections = 0

    for entry in registry:
        scopes = entry.get("scopes")
        if scopes:
            try:
                rel_str = filepath.relative_to(repo_root).as_posix()
            except ValueError:
                continue
            if not any(rel_str.startswith(s) for s in scopes):
                continue

        resolved_entry = {
            **entry,
            "canonical_source": resolve_canonical_source(entry["canonical_source"], filepath, repo_root),
        }
        new_text, diffs = inject_link(modified_text, resolved_entry, dry_run=False)
        total_injections += len(diffs) // 2
        modified_text = new_text

    if not dry_run and modified_text != text:
        filepath.write_text(modified_text, encoding="utf-8")

    return total_injections


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Weave cross-reference links across the EndogenAI/Workflows corpus.")
    parser.add_argument(
        "--scope",
        default="docs/",
        help="File or directory path to process (default: docs/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview injections without writing files",
    )
    parser.add_argument(
        "--registry",
        default="data/link_registry.yml",
        help="Path to link registry YAML (default: data/link_registry.yml)",
    )
    args = parser.parse_args()

    repo_root = find_repo_root()
    registry_path = Path(args.registry) if Path(args.registry).is_absolute() else repo_root / args.registry
    if not registry_path.exists():
        print(f"Registry not found: {registry_path}", file=sys.stderr)
        sys.exit(1)

    registry = load_registry(registry_path)

    scope_path = Path(args.scope) if Path(args.scope).is_absolute() else repo_root / args.scope
    try:
        scope_path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        print(f"Error: --scope '{args.scope}' resolves outside the repository root.", file=sys.stderr)
        sys.exit(1)
    if scope_path.is_file():
        md_files = [scope_path]
    else:
        md_files = sorted(scope_path.glob("**/*.md"))

    total_injections = 0
    files_modified = 0

    for md_file in md_files:
        if args.dry_run:
            # Apply entries sequentially (mirroring non-dry-run) to get accurate diffs
            text = md_file.read_text(encoding="utf-8")
            diffs_all: list[str] = []
            for entry in registry:
                scopes = entry.get("scopes")
                if scopes:
                    try:
                        rel_str = md_file.relative_to(repo_root).as_posix()
                    except ValueError:
                        continue
                    if not any(rel_str.startswith(s) for s in scopes):
                        continue
                resolved_entry = {
                    **entry,
                    "canonical_source": resolve_canonical_source(entry["canonical_source"], md_file, repo_root),
                }
                new_text, diffs = inject_link(text, resolved_entry, dry_run=False)
                diffs_all.extend(diffs)
                text = new_text  # apply sequentially to mirror actual run
            if diffs_all:
                print(f"--- {md_file.relative_to(repo_root)}")
                for line in diffs_all:
                    print(line)
                total_injections += len(diffs_all) // 2
                files_modified += 1
        else:
            injections = weave_file(md_file, registry, dry_run=False, repo_root=repo_root)
            if injections > 0:
                total_injections += injections
                files_modified += 1

    print(f"{total_injections} injections in {files_modified} files")
    sys.exit(0)


if __name__ == "__main__":
    main()

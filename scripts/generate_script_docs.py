"""scripts/generate_script_docs.py

Purpose:
    Generate per-script Markdown documentation from module-level docstrings.
    For each .py file in scripts/, extract the module docstring and write a
    corresponding Markdown file to scripts/docs/<script-name>.md.

Inputs:
    scripts/*.py  — Python scripts with module-level docstrings.

Outputs:
    scripts/docs/<script-name>.md  — one Markdown file per script.

Flags:
    --check    Verify that all scripts/docs/*.md files are up to date (compare
               docstring hash). Exit 1 if stale; prints list of stale files.
    --dry-run  Print what would be written without writing any files.

CLI usage:
    uv run python scripts/generate_script_docs.py
    uv run python scripts/generate_script_docs.py --dry-run
    uv run python scripts/generate_script_docs.py --check
    uv run python scripts/generate_script_docs.py --scripts-dir scripts

Exit codes:
    0  All docs generated (or up to date for --check).
    1  --check found stale documentation, or an error occurred.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Docstring extraction
# ---------------------------------------------------------------------------


def extract_module_docstring(py_file: Path) -> str:
    """Return the module-level docstring from a Python file, or empty string."""
    try:
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source)
        return ast.get_docstring(tree) or ""
    except (SyntaxError, OSError):
        return ""


def _extract_usage(docstring: str) -> str:
    """
    Pull the usage example(s) from a docstring.

    Looks for a line containing 'usage' (case-insensitive) followed by
    subsequent lines. Returns the block as a fenced code snippet, or a
    placeholder if nothing is found.
    """
    lines = docstring.splitlines()
    usage_lines: list[str] = []
    in_usage = False
    for line in lines:
        if re.search(r"\busage\b", line, re.IGNORECASE) and ":" in line:
            in_usage = True
            continue
        if in_usage:
            # Stop at blank line followed by another section header
            if line.strip() == "" and usage_lines:
                # peek ahead — if empty we keep collecting
                usage_lines.append(line)
            elif re.match(r"^[A-Z][a-zA-Z ]+:", line):
                break
            else:
                usage_lines.append(line)

    # Strip trailing blank lines
    while usage_lines and not usage_lines[-1].strip():
        usage_lines.pop()

    if usage_lines:
        return "```bash\n" + "\n".join(usage_lines) + "\n```"
    return "```bash\n# No usage example found in docstring\n```"


# ---------------------------------------------------------------------------
# Doc generation
# ---------------------------------------------------------------------------


def _docstring_hash(docstring: str) -> str:
    return hashlib.sha256(docstring.encode()).hexdigest()[:16]


def _render_doc(script_name: str, docstring: str) -> str:
    """Render a Markdown doc for a script."""
    title = script_name.replace("_", r"\_")
    usage_block = _extract_usage(docstring)
    body = docstring.strip() if docstring else "_No module docstring found._"
    return f"# `{title}`\n\n{body}\n\n## Usage\n\n{usage_block}\n\n<!-- hash:{_docstring_hash(docstring)} -->\n"


def _current_hash_from_doc(doc_path: Path) -> str | None:
    """Extract the stored hash comment from an existing doc file."""
    if not doc_path.exists():
        return None
    text = doc_path.read_text(encoding="utf-8")
    m = re.search(r"<!-- hash:([0-9a-f]+) -->", text)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def run(
    scripts_dir: Path,
    docs_dir: Path,
    dry_run: bool = False,
    check: bool = False,
) -> int:
    """
    Core logic for doc generation / staleness check.

    Returns 0 on success, 1 if stale files found (check mode) or errors.
    """
    py_files = sorted(scripts_dir.glob("*.py"))
    stale: list[str] = []
    written: list[str] = []

    for py_file in py_files:
        script_name = py_file.stem
        docstring = extract_module_docstring(py_file)
        current_hash = _docstring_hash(docstring)
        doc_path = docs_dir / f"{script_name}.md"

        if check:
            stored_hash = _current_hash_from_doc(doc_path)
            if stored_hash != current_hash:
                stale.append(str(doc_path))
        elif dry_run:
            print(f"[DRY RUN] Would write: {doc_path}")
        else:
            content = _render_doc(script_name, docstring)
            docs_dir.mkdir(parents=True, exist_ok=True)
            doc_path.write_text(content, encoding="utf-8")
            written.append(str(doc_path))

    if check:
        if stale:
            print(f"Stale documentation ({len(stale)} file(s)):")
            for f in stale:
                print(f"  {f}")
            return 1
        else:
            print("All script documentation is up to date.")
            return 0

    if not dry_run:
        print(f"Generated {len(written)} documentation file(s).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate per-script Markdown docs from module docstrings.")
    parser.add_argument(
        "--scripts-dir",
        default="scripts",
        help="Directory containing Python scripts (default: scripts)",
    )
    parser.add_argument(
        "--docs-dir",
        default="scripts/docs",
        help="Output directory for generated Markdown (default: scripts/docs)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without writing any files",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify docs are up to date; exit 1 if stale",
    )
    args = parser.parse_args()

    if args.dry_run and args.check:
        print("Error: --dry-run and --check are mutually exclusive", file=sys.stderr)
        return 1

    return run(
        scripts_dir=Path(args.scripts_dir),
        docs_dir=Path(args.docs_dir),
        dry_run=args.dry_run,
        check=args.check,
    )


if __name__ == "__main__":
    sys.exit(main())

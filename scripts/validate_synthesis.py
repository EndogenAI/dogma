"""scripts/validate_synthesis.py

Programmatic quality gate for synthesis documents — equivalent to Claude Code's
TaskCompleted hook. Validate before any Research Archivist commit.

Purpose:
    Enforce a minimum quality bar on D3 per-source synthesis reports
    (docs/research/sources/<slug>.md) and D4 issue synthesis documents
    (docs/research/<slug>.md) before they are committed as Final artifacts.

    Detects document type automatically:
      - D3 (per-source synthesis): file path contains /sources/
      - D4 (issue synthesis):      file path does not contain /sources/

Checks (D3 per-source synthesizer output):
    1. File exists and is readable.
    2. File has at least MIN_LINES (default: 80) non-blank lines.
    3. All 8 required section headings are present.
    4. YAML frontmatter contains the required fields: url (or source_url),
       cache_path, slug, title.

Checks (D4 issue synthesis):
    1. File exists and is readable.
    2. File has at least MIN_LINES (default: 80) non-blank lines.
    3. All required section headings are present (## Executive Summary through
       ## Project Relevance, or any ≥ 4 ## headings if the file uses a custom layout).
    4. YAML frontmatter contains: title, status.

Inputs:
    <file>         Path to the synthesis file to validate.  (positional, required)
    --min-lines    Minimum non-blank line count.            (default: 80)
    --strict       Reserved for future use — currently a no-op flag.

Outputs:
    stdout:  Human-readable pass/fail summary with specific gap list.
    stderr:  Nothing (all output goes to stdout for easy capture).

Exit codes:
    0  All checks passed.
    1  One or more checks failed — specific gap(s) reported to stdout.

Usage examples:
    # Validate a D3 per-source synthesis report
    uv run python scripts/validate_synthesis.py docs/research/sources/anthropic-building-effective-agents.md

    # Validate a D4 issue synthesis
    uv run python scripts/validate_synthesis.py docs/research/agent-fleet-design-patterns.md

    # Require a higher minimum line count
    uv run python scripts/validate_synthesis.py docs/research/sources/my-source.md --min-lines 150

    # Integrate into archivist workflow (non-zero exit blocks commit)
    uv run python scripts/validate_synthesis.py "$FILE" || exit 1
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Required section headings
# ---------------------------------------------------------------------------

# D3 section headings — validated by fuzzy keyword matching to accept both
# numbered ("## 1. Citation") and unnumbered ("## Citation") formats.
# Format: (description, [accepted_keyword_variants...])
D3_REQUIRED_SECTIONS: list[tuple[str, list[str]]] = [
    ("Citation", ["citation"]),
    ("Research Question", ["research question"]),
    ("Theoretical Framework", ["theoretical"]),
    ("Methodology", ["methodology", "source type"]),
    ("Key Claims", ["key claims", "key findings"]),
    ("Critical Assessment", ["critical assessment"]),
    ("Cross-Source Connections", ["cross-source", "connection to other"]),
    ("Project Relevance", ["project relevance", "relevance to endogenai"]),
]

D4_REQUIRED_HEADINGS: list[str] = [
    "## 1. Executive Summary",
    "## 2. Hypothesis Validation",
    "## 3. Pattern Catalog",
]

# D4 files use numbered sections; we check the first few and count the rest.
D4_MIN_HEADING_COUNT = 4

# Required frontmatter keys per document type.
D3_REQUIRED_FRONTMATTER: list[str] = ["slug", "title", "cache_path"]
D3_URL_KEYS: list[str] = ["url", "source_url"]  # accept either alias

D4_REQUIRED_FRONTMATTER: list[str] = ["title", "status"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def parse_frontmatter(text: str) -> dict[str, str]:
    """Return a flat dict of YAML frontmatter key → raw string value.

    Uses regex rather than a full YAML parser to avoid adding a dependency.
    Multi-line values and lists are preserved as raw strings for presence checks.
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fm: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()
    return fm


def extract_headings(text: str) -> list[str]:
    """Return all Markdown H2 headings (## ...) found in the document body."""
    body_start = 0
    # Skip past frontmatter if present
    fm_match = _FRONTMATTER_RE.match(text)
    if fm_match:
        body_start = fm_match.end()
    body = text[body_start:]
    return [line.rstrip() for line in body.splitlines() if line.startswith("## ")]


def non_blank_line_count(text: str) -> int:
    """Count non-blank lines in the document (including frontmatter)."""
    return sum(1 for line in text.splitlines() if line.strip())


def is_d3(file_path: Path) -> bool:
    """True if *file_path* points to a D3 per-source synthesis document."""
    # D3 files live under .../sources/
    return "sources" in file_path.parts


# Axiom names that must have an adjacent MANIFESTO.md §N reference on the same line.
_AXIOM_NAMES: tuple[str, ...] = (
    "Endogenous-First",
    "Algorithms Before Tokens",
    "Local Compute-First",
)


def check_final_status_modified(file_path: Path, allow_final_edit: bool) -> None:
    """Warn when a Final- or Published-status doc has uncommitted modifications.

    Detects modification via ``git diff --name-only HEAD`` (compares working tree
    and staging area to HEAD). Prints a WARNING unless *allow_final_edit* is True.
    Does NOT call sys.exit — advisory only.

    Args:
        file_path: Path to the synthesis document.
        allow_final_edit: When True, suppress the warning (--allow-final-edit flag).
    """
    fm = parse_frontmatter(file_path.read_text(encoding="utf-8"))
    status = fm.get("status", "").strip().lower()
    if status not in ("final", "published"):
        return

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        modified_files = result.stdout.strip().splitlines()
    except FileNotFoundError:
        return  # git not available — skip check

    # git diff returns repo-relative paths; resolve both sides for comparison.
    try:
        cwd = Path.cwd()
        resolved_target = file_path.resolve()
        is_modified = any((cwd / Path(f)).resolve() == resolved_target for f in modified_files)
    except Exception:
        return

    if is_modified and not allow_final_edit:
        print(
            "WARNING: Final-status research doc modified — manual review gate recommended "
            "before committing. Use --allow-final-edit to suppress."
        )


def check_axiom_citations(lines: list[str], filepath: str) -> None:
    """Warn when an axiom name appears without a MANIFESTO.md §-reference on the same line.

    Prints WARN messages to stdout for each bare axiom name found.
    Does NOT call sys.exit — this is advisory only.

    Args:
        lines: List of text lines from the document.
        filepath: Path string used in warning messages.
    """
    for i, line in enumerate(lines, start=1):
        for axiom in _AXIOM_NAMES:
            if axiom in line and "MANIFESTO.md §" not in line:
                print(f"WARN: bare axiom name without §-reference: line {i} in {filepath}")


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------


def validate(file_path: Path, min_lines: int) -> tuple[bool, list[str]]:
    """Validate *file_path*. Returns (passed, list_of_failure_messages)."""
    failures: list[str] = []

    # --- Check 1: file exists ---
    if not file_path.exists():
        return False, [f"File not found: {file_path}"]
    if not file_path.is_file():
        return False, [f"Path is not a file: {file_path}"]

    text = file_path.read_text(encoding="utf-8")

    # --- Check 2: minimum non-blank line count ---
    actual_lines = non_blank_line_count(text)
    if actual_lines < min_lines:
        failures.append(f"Line count too low: {actual_lines} non-blank lines (minimum: {min_lines})")

    # --- Check 3: required section headings ---
    present_headings = extract_headings(text)
    present_set = set(present_headings)

    if is_d3(file_path):
        heading_text_lower = [h.lower() for h in present_headings]
        for section_name, keywords in D3_REQUIRED_SECTIONS:
            matched = any(kw in h for kw in keywords for h in heading_text_lower)
            if not matched:
                failures.append(
                    f"Missing required D3 section '{section_name}' (expected a heading matching one of: {keywords})"
                )
    else:
        # D4: check the first required headings and enforce a minimum count
        for heading in D4_REQUIRED_HEADINGS:
            if heading not in present_set:
                # Accept that D4 file may use different numbered titles; look for
                # any heading containing the same keyword.
                keyword = heading.split(".", 1)[-1].strip()
                if not any(keyword.lower() in h.lower() for h in present_headings):
                    failures.append(f"Missing required section heading: '{heading}'")
        if len(present_headings) < D4_MIN_HEADING_COUNT:
            failures.append(
                f"D4 synthesis must have ≥ {D4_MIN_HEADING_COUNT} ## headings; found {len(present_headings)}"
            )

    # --- Check 4: required frontmatter fields ---
    fm = parse_frontmatter(text)
    if not fm:
        failures.append("No YAML frontmatter found (expected --- block at top of file)")
    else:
        if is_d3(file_path):
            for key in D3_REQUIRED_FRONTMATTER:
                if not fm.get(key):
                    failures.append(f"Missing or empty frontmatter field: '{key}'")
            # Accept either 'url' or 'source_url'
            if not any(fm.get(k) for k in D3_URL_KEYS):
                failures.append(f"Missing frontmatter URL field: one of {D3_URL_KEYS} must be present and non-empty")
        else:
            for key in D4_REQUIRED_FRONTMATTER:
                if not fm.get(key):
                    failures.append(f"Missing or empty frontmatter field: '{key}'")

    passed = len(failures) == 0
    return passed, failures


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a D3/D4 synthesis document before archiving.",
        epilog="Exit 0 = pass. Exit 1 = one or more checks failed.",
    )
    parser.add_argument(
        "files",
        metavar="<file>",
        nargs="+",
        help="Path(s) to synthesis document(s) to validate. Accepts multiple files.",
    )
    parser.add_argument(
        "--min-lines",
        type=int,
        default=80,
        metavar="N",
        help="Minimum non-blank line count (default: 80).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Reserved for future use — currently a no-op.",
    )
    parser.add_argument(
        "--allow-final-edit",
        action="store_true",
        help="Suppress the WARNING emitted when a Final- or Published-status doc is modified.",
    )
    args = parser.parse_args()

    overall_passed = True
    for file_arg in args.files:
        file_path = Path(file_arg)
        doc_type = "D3 (per-source)" if is_d3(file_path) else "D4 (issue synthesis)"

        print(f"validate_synthesis: {file_path}  [{doc_type}]")

        passed, failures = validate(file_path, args.min_lines)

        # For D4 documents, run advisory axiom citation check (warn-only, non-blocking).
        if not is_d3(file_path) and file_path.exists():
            check_axiom_citations(file_path.read_text(encoding="utf-8").splitlines(), str(file_path))

        # For D4 documents, warn if a Final/Published doc has been modified without --allow-final-edit.
        if not is_d3(file_path) and file_path.exists():
            check_final_status_modified(file_path, args.allow_final_edit)

        if passed:
            print("PASS — all checks passed.")
        else:
            print(f"FAIL — {len(failures)} check(s) failed:")
            for i, msg in enumerate(failures, 1):
                print(f"  {i}. {msg}")
            overall_passed = False

    sys.exit(0 if overall_passed else 1)


if __name__ == "__main__":
    main()

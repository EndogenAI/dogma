"""
audit_provenance.py
-------------------
Purpose:
    Audits the endogenic substrate for value signal provenance. Reads agent
    files and checks whether each file's instructions trace their signal
    provenance back to foundational MANIFESTO.md axioms via a 'x-governs:'
    frontmatter annotation.

    Provenance annotation format (in .agent.md YAML frontmatter):
        x-governs:
          - endogenous-first
          - programmatic-first

    Orphaned files: .agent.md files with no 'x-governs:' frontmatter field.
    Unverifiable citations: axiom names in 'x-governs:' not found in MANIFESTO.md.

Inputs:
    --agents-dir  PATH   Directory of .agent.md files (default: .github/agents/)
    --manifesto   PATH   Path to MANIFESTO.md for axiom name validation
                         (default: auto-resolved MANIFESTO.md at repo root)
    --output      FILE   Write JSON report to this file (default: stdout)
    --format      json|summary  Output format (default: json)

Outputs:
    JSON report:
    {
        "files": [
            {
                "path": str,
                "citations": [str],      # axiom names found in x-governs:
                "orphaned": bool,        # True if no x-governs: field at all
                "unverifiable": [str]    # axiom names not in MANIFESTO.md
            }
        ],
        "fleet_citation_coverage_pct": float,  # % of files with x-governs:
        "total_unverifiable": int
    }
    Exit code: 0 on success; non-zero on configuration or runtime errors.

Usage examples:
    uv run python scripts/audit_provenance.py
    uv run python scripts/audit_provenance.py --format summary
    uv run python scripts/audit_provenance.py --output /tmp/provenance.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo root resolution
# ---------------------------------------------------------------------------


def find_repo_root() -> Path:
    """Walk up from this file until AGENTS.md is found."""
    candidate = Path(__file__).resolve().parent
    while candidate != candidate.parent:
        if (candidate / "AGENTS.md").exists():
            return candidate
        candidate = candidate.parent
    return Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Frontmatter parsing (inlined from generate_agent_manifest.py)
# ---------------------------------------------------------------------------


def extract_frontmatter(text: str) -> str | None:
    """Return the raw YAML text between leading '---' fences, or None."""
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    return match.group(1) if match else None


def parse_simple_yaml(yaml_text: str) -> dict:
    """
    Parse a subset of YAML: top-level scalar strings and flat string lists.
    Does NOT support nested objects, multi-line strings, anchors, or tags.
    """
    result: dict = {}
    lines = yaml_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        key_match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)", line)
        if key_match:
            key = key_match.group(1)
            value = key_match.group(2).strip()
            if value:
                # Key: value — if it matches x-governs, we want to support both keys
                # for backward compatibility during normalization phase (Phase 0)
                # but we'll normalize them to 'x-governs' internally
                target_key = "x-governs" if key in ("governs", "x-governs") else key
                result[target_key] = value.strip("\"'")
                i += 1
            else:
                items: list[str] = []
                target_key = "x-governs" if key in ("governs", "x-governs") else key
                i += 1
                while i < len(lines):
                    item_match = re.match(r"^\s+-\s+(.*)", lines[i])
                    if item_match:
                        items.append(item_match.group(1).strip().strip("\"'"))
                        i += 1
                    elif not lines[i].strip():
                        i += 1
                    elif lines[i][0] in (" ", "\t"):
                        i += 1
                    else:
                        break
                result[target_key] = items
        else:
            i += 1
    return result


# ---------------------------------------------------------------------------
# Axiom extraction from MANIFESTO.md
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^#{2,3}\s+(.+)$", re.MULTILINE)


def _normalise_axiom_name(heading: str) -> str:
    """
    Normalise a Markdown heading to a lowercase-hyphenated axiom name.
    E.g. 'Algorithms Before Tokens' -> 'algorithms-before-tokens'
         'Endogenous-First'         -> 'endogenous-first'
         '1. Endogenous-First'      -> 'endogenous-first'
    """
    # Strip any inline Markdown (bold, code, etc.)
    heading = re.sub(r"[`*_]", "", heading)
    heading = heading.strip()
    # Strip leading numeric prefixes like "1. ", "1.2. ", "2) "
    heading = re.sub(r"^[0-9]+(?:\.[0-9]+)*\s*[\.\)]?\s*", "", heading)
    # Replace spaces (and existing hyphens) normalise to single hyphens
    heading = re.sub(r"\s+", "-", heading)
    return heading.lower()


def extract_manifesto_axioms(manifesto_path: Path) -> set[str]:
    """Return the set of normalised H2/H3 heading names from MANIFESTO.md."""
    text = manifesto_path.read_text(encoding="utf-8")
    headings = _HEADING_RE.findall(text)
    return {_normalise_axiom_name(h) for h in headings}


# ---------------------------------------------------------------------------
# Per-file audit
# ---------------------------------------------------------------------------


def audit_file(agent_path: Path, known_axioms: set[str]) -> dict:
    """
    Audit a single .agent.md file for provenance annotations.

    Returns a dict with keys: path, citations, orphaned, unverifiable.
    """
    try:
        text = agent_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"WARNING: cannot read {agent_path}: {exc}", file=sys.stderr)
        return {"path": str(agent_path), "citations": [], "orphaned": True, "unverifiable": []}
    fm_raw = extract_frontmatter(text)
    fm = parse_simple_yaml(fm_raw) if fm_raw else {}

    governs_value = fm.get("x-governs")

    if governs_value is None:
        # No 'x-governs:' key at all — orphaned
        return {
            "path": str(agent_path),
            "citations": [],
            "orphaned": True,
            "unverifiable": [],
        }

    # x-governs: may be a scalar string (single axiom) or a list
    if isinstance(governs_value, str):
        citations = [governs_value]
    else:
        citations = list(governs_value)

    normalised = [_normalise_axiom_name(c) for c in citations]
    unverifiable = [c for c in normalised if c not in known_axioms]

    return {
        "path": str(agent_path),
        "citations": normalised,
        "orphaned": False,
        "unverifiable": unverifiable,
    }


# ---------------------------------------------------------------------------
# Report building
# ---------------------------------------------------------------------------


def build_report(agents_dir: Path, manifesto_path: Path) -> dict:
    """Build the full provenance report dict."""
    agent_files = sorted(agents_dir.glob("*.agent.md"))
    known_axioms = extract_manifesto_axioms(manifesto_path)

    file_results = [audit_file(f, known_axioms) for f in agent_files]

    total = len(file_results)
    files_with_governs = sum(1 for r in file_results if not r["orphaned"])
    coverage_pct = (files_with_governs / total * 100) if total > 0 else 0.0
    total_unverifiable = sum(len(r["unverifiable"]) for r in file_results)

    return {
        "files": file_results,
        "fleet_citation_coverage_pct": round(coverage_pct, 1),
        "total_unverifiable": total_unverifiable,
    }


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def format_summary(report: dict) -> str:
    """Return a human-readable summary string."""
    lines: list[str] = []
    for entry in report["files"]:
        path = entry["path"]
        if entry["orphaned"]:
            status = "✗"
            detail = "no x-governs: field"
        elif entry["unverifiable"]:
            status = "⚠️"
            detail = f"unverifiable: {', '.join(entry['unverifiable'])}"
        else:
            status = "✓"
            detail = ", ".join(entry["citations"]) or "(empty list)"
        lines.append(f"  {status}  {path}  [{detail}]")

    lines.append("")
    lines.append(
        f"Fleet citation coverage: {report['fleet_citation_coverage_pct']}%  "
        f"| Total unverifiable: {report['total_unverifiable']}"
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    repo_root = find_repo_root()

    parser = argparse.ArgumentParser(description="Audit .agent.md files for x-governs: provenance annotations.")
    parser.add_argument(
        "--agents-dir",
        type=Path,
        default=repo_root / ".github" / "agents",
        help="Directory of .agent.md files (default: .github/agents/)",
    )
    parser.add_argument(
        "--scope",
        type=Path,
        default=None,
        help="Alias for --agents-dir: directory of .agent.md files to audit",
    )
    parser.add_argument(
        "--manifesto",
        type=Path,
        default=repo_root / "MANIFESTO.md",
        help="Path to MANIFESTO.md (default: repo root MANIFESTO.md)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write report to this file (default: stdout)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format: json (default) or summary",
    )

    args = parser.parse_args(argv)

    # --scope is an alias for --agents-dir
    agents_dir = args.scope if args.scope is not None else args.agents_dir

    if not agents_dir.is_dir():
        print(f"ERROR: agents directory not found: {agents_dir}", file=sys.stderr)
        return 1

    if not args.manifesto.is_file():
        print(f"ERROR: MANIFESTO.md not found: {args.manifesto}", file=sys.stderr)
        return 1

    report = build_report(agents_dir, args.manifesto)

    if args.format == "summary":
        output_text = format_summary(report)
    else:
        output_text = json.dumps(report, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_text, encoding="utf-8")
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())

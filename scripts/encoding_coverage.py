"""scripts/encoding_coverage.py

Checks MANIFESTO.md and AGENTS.md to determine whether each named principle
and axiom has all four [4,1] encoding forms present.

Encoding forms:
    F1 = verbal description   — at least one substantive paragraph in the
                                principle's section body
    F2 = canonical example    — labeled ``**Canonical example**:`` block
    F3 = anti-pattern         — labeled ``**Anti-pattern**`` block
    F4 = programmatic gate    — labeled ``**Programmatic gate**:`` OR an
                                explicit reference to a script/hook/CI mechanism

Purpose:
    Produce a Markdown coverage table as a baseline for tracking encoding
    completeness of every MANIFESTO principle.  Gaps in F2–F4 signal
    principles where knowledge is verbally described but has not been
    concretized into examples, anti-patterns, or enforcement mechanisms.

Inputs:
    --manifesto PATH   Path to MANIFESTO.md (default: MANIFESTO.md)
    --agents PATH      Path to AGENTS.md    (default: AGENTS.md)

Outputs:
    Markdown table written to stdout.  Exits 0 on success, 1 on a missing
    input file.

Exit codes:
    0  Table generated successfully.
    1  One or more input files not found — error written to stderr.

Usage:
    uv run python scripts/encoding_coverage.py --manifesto MANIFESTO.md --agents AGENTS.md
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Principle registry
# ---------------------------------------------------------------------------


@dataclass
class Principle:
    name: str
    layer: str


#: All named principles extracted from MANIFESTO.md in document order.
PRINCIPLES: list[Principle] = [
    Principle("Endogenous-First", "Axiom 1"),
    Principle("Algorithms Before Tokens", "Axiom 2"),
    Principle("Local Compute-First", "Axiom 3"),
    Principle("Programmatic-First", "Cross-cutting"),
    Principle("Documentation-First", "Cross-cutting"),
    Principle("Adopt Over Author", "Cross-cutting"),
    Principle("Self-Governance & Guardrails", "Cross-cutting"),
    Principle("Compress Context, Not Content", "Cross-cutting"),
    Principle("Isolate Invocations, Parallelize Safely", "Cross-cutting"),
    Principle("Validate & Gate, Always", "Cross-cutting"),
    Principle("Minimal Posture", "Cross-cutting"),
    Principle("Testing-First", "Cross-cutting"),
]


# ---------------------------------------------------------------------------
# Detection patterns
# ---------------------------------------------------------------------------

# F1 — a line of ≥40 printable characters that is not a heading, blockquote,
#       list item, table row, code fence, or blank line.
_F1_PARA_RE = re.compile(
    r"^(?![ \t]*[>|#\-\*`])[A-Za-z\(\"'].{39,}$",
    re.MULTILINE,
)

# F2 — explicit canonical-example label (bold, case-insensitive)
_CANONICAL_EXAMPLE_RE = re.compile(r"\*\*canonical example\*\*", re.IGNORECASE)

# F3 — explicit anti-pattern label (bold, case-insensitive; may include a
#       parenthesised sub-label before the colon)
_ANTI_PATTERN_RE = re.compile(r"\*\*anti-pattern", re.IGNORECASE)

# F4 — explicit programmatic-gate label OR an unambiguous enforcement reference
_PROGRAMMATIC_GATE_RE = re.compile(
    r"\*\*programmatic gate\*\*"
    r"|scripts/\S+\.py"
    r"|pre-commit hook"
    r"|pre-push hook"
    r"|`uv run pytest"
    r"|CI step"
    r"|`uv run python",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Section extraction
# ---------------------------------------------------------------------------


def extract_h3_section(text: str, principle_name: str) -> str:
    """Return the body of the first H3 section whose title contains *principle_name*.

    Searches for the heading using a case-insensitive substring match so that
    numbering prefixes ("1. Endogenous-First") and parenthesised suffixes
    ("Adopt Over Author (Avoid Reinventing the Wheel)") are handled
    transparently.

    Returns an empty string if no matching heading is found.
    """
    escaped = re.escape(principle_name)
    heading_re = re.compile(
        rf"^###\s+.*{escaped}.*$",
        re.MULTILINE | re.IGNORECASE,
    )
    m = heading_re.search(text)
    if not m:
        return ""

    start = m.end()
    # Terminate at the next ## or ### heading
    next_heading_re = re.compile(r"^#{2,3}\s+", re.MULTILINE)
    nx = next_heading_re.search(text, start)
    end = nx.start() if nx else len(text)
    return text[start:end]


def _agents_context(agents_text: str, principle_name: str) -> str:
    """Return up to ~3 000 characters of AGENTS.md surrounding each mention of
    *principle_name*, for use as a supplementary F2–F4 source."""
    pattern = re.compile(re.escape(principle_name), re.IGNORECASE)
    snippets: list[str] = []
    for m in pattern.finditer(agents_text):
        start = max(0, m.start() - 600)
        end = min(len(agents_text), m.end() + 600)
        snippets.append(agents_text[start:end])
    return "\n".join(snippets)


# ---------------------------------------------------------------------------
# Coverage checks
# ---------------------------------------------------------------------------


def check_coverage(
    section_body: str,
    agents_text: str,
    principle_name: str,
) -> tuple[bool, bool, bool, bool]:
    """Return (F1, F2, F3, F4) coverage flags for *principle_name*.

    F1 is evaluated against the MANIFESTO section body only.
    F2–F4 are evaluated against the section body first; if absent there, the
    nearby AGENTS.md context is also checked to capture cross-document encoding.
    """
    ctx = _agents_context(agents_text, principle_name)

    f1 = bool(_F1_PARA_RE.search(section_body)) if section_body else False
    f2 = bool(_CANONICAL_EXAMPLE_RE.search(section_body) or _CANONICAL_EXAMPLE_RE.search(ctx))
    f3 = bool(_ANTI_PATTERN_RE.search(section_body) or _ANTI_PATTERN_RE.search(ctx))
    f4 = bool(_PROGRAMMATIC_GATE_RE.search(section_body) or _PROGRAMMATIC_GATE_RE.search(ctx))

    return f1, f2, f3, f4


# ---------------------------------------------------------------------------
# Table rendering
# ---------------------------------------------------------------------------

_TICK = "✓"
_CROSS = "✗"


def _cell(flag: bool) -> str:
    return _TICK if flag else _CROSS


def build_table(manifesto_text: str, agents_text: str) -> str:
    """Return the complete Markdown coverage table as a string."""
    header = "| Principle | Layer | F1 Desc | F2 Canonical | F3 Anti-pattern | F4 Programmatic | Score |"
    separator = "|-----------|-------|---------|--------------|-----------------|-----------------|-------|"
    rows: list[str] = [header, separator]

    for p in PRINCIPLES:
        section = extract_h3_section(manifesto_text, p.name)
        f1, f2, f3, f4 = check_coverage(section, agents_text, p.name)
        score = sum([f1, f2, f3, f4])
        rows.append(f"| {p.name} | {p.layer} | {_cell(f1)} | {_cell(f2)} | {_cell(f3)} | {_cell(f4)} | {score}/4 |")

    return "\n".join(rows)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check MANIFESTO F1-F4 encoding coverage for named principles.")
    parser.add_argument(
        "--manifesto",
        default="MANIFESTO.md",
        help="Path to MANIFESTO.md (default: MANIFESTO.md)",
    )
    parser.add_argument(
        "--agents",
        default="AGENTS.md",
        help="Path to AGENTS.md (default: AGENTS.md)",
    )
    args = parser.parse_args(argv)

    manifesto_path = Path(args.manifesto)
    agents_path = Path(args.agents)

    missing = [p for p in (manifesto_path, agents_path) if not p.exists()]
    if missing:
        for p in missing:
            print(f"Error: file not found: {p}", file=sys.stderr)
        return 1

    manifesto_text = manifesto_path.read_text(encoding="utf-8")
    agents_text = agents_path.read_text(encoding="utf-8")

    print(build_table(manifesto_text, agents_text))
    return 0


if __name__ == "__main__":
    sys.exit(main())

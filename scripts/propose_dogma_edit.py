"""
propose_dogma_edit.py
---------------------
Propose dogma edits to the endogenic substrate using the back-propagation protocol.

Inputs:
  --input <session-file>    Path to a scratchpad session .md file
  --tier T1|T2|T3          Stability tier of the affected section
  --affected-axiom <str>   Name/heading of the affected axiom or section
  --proposed-delta <str>   Brief description of proposed text change (use "-" for stdin)
  --output <path>          Output path for the ADR-style Markdown proposal (default: stdout)

Outputs:
  ADR-style Markdown proposal with Date, Tier, Current Text, Proposed Text,
  Evidence, Coherence Check, Status sections.

Usage:
  uv run python scripts/propose_dogma_edit.py \\
    --input .tmp/feat-value-encoding-fidelity/2026-03-09.md \\
    --tier T3 \\
    --affected-axiom "Focus-on-Descent" \\
    --proposed-delta "Add signal-preservation rules for canonical examples" \\
    --output /tmp/proposal.md

Exit codes:
  0 — Success, or coherence fails on a tier other than T1
  1 — Coherence check fails and tier is T1 (blocking)
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

# Ensure scripts/ directory is on sys.path so sibling modules are importable
# regardless of invocation context (direct run, importlib in tests, etc.)
_SCRIPTS_DIR = Path(__file__).parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from audit_provenance import extract_manifesto_axioms  # noqa: E402, F401
from detect_drift import WATERMARK_PHRASES  # noqa: E402

# ---------------------------------------------------------------------------
# Tier metadata
# ---------------------------------------------------------------------------


def load_stability_tiers() -> dict[str, dict]:
    """
    Return hardcoded stability tier metadata matching dogma-neuroplasticity.md §Pattern Catalog C1.

    Returns a dict keyed by tier identifier (T1/T2/T3), each with:
      - name: human-readable tier name
      - session_threshold: number of independent session signals required
      - requires_adr: whether a formal ADR in docs/decisions/ is mandatory
      - substrate: canonical file/section location for this tier
    """
    return {
        "T1": {
            "name": "Axioms",
            "session_threshold": 3,
            "requires_adr": True,
            "substrate": "MANIFESTO.md §axioms",
        },
        "T2": {
            "name": "Guiding Principles",
            "session_threshold": 3,
            "requires_adr": True,
            "substrate": "MANIFESTO.md non-axiom sections + AGENTS.md §1",
        },
        "T3": {
            "name": "Operational Constraints",
            "session_threshold": 2,
            "requires_adr": False,
            "substrate": "AGENTS.md operational sections",
        },
    }


# ---------------------------------------------------------------------------
# Evidence extraction
# ---------------------------------------------------------------------------


def extract_evidence(session_text: str) -> list[str]:
    """
    Return all lines in session_text containing any WATERMARK_PHRASE (case-insensitive).

    Imports WATERMARK_PHRASES from detect_drift — does not reimplement the constant.
    Returns [] for empty input.

    Args:
        session_text: Full text of a scratchpad session Markdown file.

    Returns:
        List of lines (with original whitespace preserved) that contain a phrase.
    """
    if not session_text:
        return []
    results = []
    for line in session_text.splitlines():
        line_lower = line.lower()
        if any(phrase.lower() in line_lower for phrase in WATERMARK_PHRASES):
            results.append(line)
    return results


# ---------------------------------------------------------------------------
# Coherence check
# ---------------------------------------------------------------------------


def check_coherence(tier: str, proposed_delta: str, tiers: dict) -> dict:
    """
    Check coherence of a proposed delta against the stability tier model.

    passes is False when the proposed delta contains a WATERMARK_PHRASE AND
    the context indicates removal intent ("remove", "delete", or "drop").
    This check is blocking only for T1 (main() returns exit code 1).

    Args:
        tier: One of "T1", "T2", "T3".
        proposed_delta: Brief text description of the proposed change.
        tiers: Tier metadata dict from load_stability_tiers().

    Returns:
        {
            "passes": bool,
            "session_threshold": int,
            "requires_adr": bool,
            "inheriting_layers": list[str],
        }
    """
    tier_meta = tiers[tier]
    delta_lower = proposed_delta.lower()

    # Determine inheriting layers that require review after an edit
    if tier == "T1":
        inheriting_layers = ["AGENTS.md", ".github/agents/*.agent.md"]
    elif tier == "T2":
        inheriting_layers = ["AGENTS.md"]
    else:
        inheriting_layers = []

    # Fail if proposed delta removes a watermark phrase
    removal_keywords = {"remove", "delete", "drop"}
    has_removal_intent = any(kw in delta_lower for kw in removal_keywords)
    has_watermark = any(phrase.lower() in delta_lower for phrase in WATERMARK_PHRASES)

    passes = not (has_watermark and has_removal_intent)

    return {
        "passes": passes,
        "session_threshold": tier_meta["session_threshold"],
        "requires_adr": tier_meta["requires_adr"],
        "inheriting_layers": inheriting_layers,
    }


# ---------------------------------------------------------------------------
# Proposal generation
# ---------------------------------------------------------------------------


def generate_proposal(
    tier: str,
    affected_axiom: str,
    proposed_delta: str,
    evidence: list[str],
    coherence: dict,
    tiers: dict,
) -> str:
    """
    Generate an ADR-style Markdown proposal using the Pattern C3 template
    from dogma-neuroplasticity.md §Pattern Catalog.

    Args:
        tier: One of "T1", "T2", "T3".
        affected_axiom: Name/heading of the affected axiom or section.
        proposed_delta: Brief description of the proposed text change.
        evidence: List of session-file lines containing watermark phrases.
        coherence: Result dict from check_coherence().
        tiers: Tier metadata dict from load_stability_tiers().

    Returns:
        Complete ADR-style Markdown string ready to write to a file or stdout.
    """
    today = datetime.date.today().isoformat()
    tier_name = tiers[tier]["name"]

    if evidence:
        evidence_block = "\n".join(f"- {line.strip()}" for line in evidence)
    else:
        evidence_block = "No watermark phrases found in session file."

    inheriting = coherence["inheriting_layers"]
    inheriting_str = ", ".join(inheriting) if inheriting else "(none)"
    result_str = "Passes" if coherence["passes"] else "Fails"

    return (
        f"# DEP-DRAFT: {affected_axiom}\n\n"
        f"**Date**: {today}\n"
        f"**Tier**: {tier} — {tier_name}\n"
        f"**Affected section**: {affected_axiom}\n"
        f"**Status**: Proposed\n\n"
        f"## Current Text\n\n"
        f"> <replace with exact verbatim quote before submitting>\n\n"
        f"## Proposed Text\n\n"
        f"{proposed_delta}\n\n"
        f"## Evidence\n\n"
        f"{evidence_block}\n\n"
        f"## Coherence Check\n\n"
        f"- **Watermark phrase check**: passes={coherence['passes']}\n"
        f"- **Session threshold**: {coherence['session_threshold']} signals required\n"
        f"- **Requires ADR**: {coherence['requires_adr']}\n"
        f"- **Inheriting layers requiring review**: {inheriting_str}\n"
        f"- **Result**: {result_str}\n\n"
        f"## Consequences\n\n"
        f"Review inheriting layers listed above after applying this edit.\n\n"
        f"## References\n\n"
        f"- Stability tier model: docs/research/dogma-neuroplasticity.md §Pattern Catalog\n"
        f"- Back-propagation protocol: docs/research/dogma-neuroplasticity.md §Pattern C2\n"
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """
    CLI entry point for propose_dogma_edit.py.

    Returns:
        0 on success, or when coherence fails for a non-T1 tier.
        1 if coherence check fails and tier is T1 (blocking).
        1 if the session file cannot be read.
    """
    parser = argparse.ArgumentParser(
        description=("Propose a dogma edit to the endogenic substrate using the back-propagation protocol.")
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to a scratchpad session .md file.",
    )
    parser.add_argument(
        "--tier",
        choices=["T1", "T2", "T3"],
        required=True,
        help="Stability tier of the affected section.",
    )
    parser.add_argument(
        "--affected-axiom",
        required=True,
        help="Name/heading of the affected axiom or section.",
    )
    parser.add_argument(
        "--proposed-delta",
        default="-",
        help="Brief description of proposed text change; '-' reads from stdin.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for the ADR-style Markdown proposal (default: stdout).",
    )

    args = parser.parse_args(argv)

    # Read proposed delta (stdin if "-")
    if args.proposed_delta == "-":
        proposed_delta = sys.stdin.read().strip()
    else:
        proposed_delta = args.proposed_delta

    # Load tier metadata
    tiers = load_stability_tiers()

    # Read session file
    try:
        session_text = args.input.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Cannot read session file {args.input}: {exc}", file=sys.stderr)
        return 1

    # Extract evidence, check coherence, generate proposal
    evidence = extract_evidence(session_text)
    coherence = check_coherence(args.tier, proposed_delta, tiers)
    proposal = generate_proposal(
        tier=args.tier,
        affected_axiom=args.affected_axiom,
        proposed_delta=proposed_delta,
        evidence=evidence,
        coherence=coherence,
        tiers=tiers,
    )

    # Write output
    if args.output:
        args.output.write_text(proposal, encoding="utf-8")
    else:
        print(proposal)

    # T1 coherence failure is blocking (exit 1)
    if not coherence["passes"] and args.tier == "T1":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

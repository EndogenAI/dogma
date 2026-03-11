"""
validate_handoff_permeability.py
--------------------------------

Purpose:
    Validates that cross-substrate handoffs preserve required signal types per
    membrane layer in agent fleet communication. Implements the signal preservation
    rules from AGENTS.md § Agent Communication → Focus-on-Descent / Compression-on-Ascent.

    Membranes in agent fleet communication enforce signal preservation while allowing
    context compression. This function validates that critical knowledge (Canonical
    examples, axiom citations) survives handoffs even when narrative context is
    compressed. This prevents value-encoding drift and ensures endogenous knowledge
    remains intact across delegation boundaries.

Inputs:
    --handoff-file PATH      Path to markdown file containing handoff text
    --membrane-type TYPE     One of: scout-to-synthesizer, synthesizer-to-reviewer,
                             reviewer-to-archivist
    --required-signals LIST  Comma-separated signal types to validate (optional;
                             defaults to all signals for membrane type)
    --output FILE            Write JSON report to file (default: stdout)
    --format json|text       Output format (default: json)

Outputs:
    JSON report:
    {
        "status": "pass" | "fail",
        "membrane_type": str,
        "missing_signals": [str],      # signal types not found
        "found_signals": [str],        # signal types detected
        "signal_counts": {             # detailed counts per signal type
            "canonical_example": int,
            "anti_pattern": int,
            "axiom_citation": int,
            "source_url": int
        },
        "warnings": [str],             # non-critical issues
        "report": str                  # human-readable markdown report
    }
    Exit code: 0 on success (pass or fail verdict clear); 1 on configuration error.

Usage examples:
    uv run python scripts/validate_handoff_permeability.py \\
        --handoff-file .tmp/branch/2026-03-10.md \\
        --membrane-type scout-to-synthesizer

    uv run python scripts/validate_handoff_permeability.py \\
        --handoff-file /tmp/handoff.md \\
        --membrane-type synthesizer-to-reviewer \\
        --format text
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable, Optional


# ===========================================================================
# Signal Detection Definitions
# ===========================================================================

@dataclass
class MembraneSpec:
    """Specification of which signals must be preserved in a given membrane."""
    name: str
    required_signals: list[str]  # must be ≥1 match
    compressible_signals: list[str]  # optional; warn if completely absent


MEMBRANE_SPECS = {
    "scout-to-synthesizer": MembraneSpec(
        name="Scout → Synthesizer",
        required_signals=["canonical_example", "anti_pattern", "axiom_citation", "source_url"],
        compressible_signals=["background_prose", "exploratory_notes"],
    ),
    "synthesizer-to-reviewer": MembraneSpec(
        name="Synthesizer → Reviewer",
        required_signals=["canonical_example", "anti_pattern", "synthesis_structure", "metrics"],
        compressible_signals=["literature_survey_depth"],
    ),
    "reviewer-to-archivist": MembraneSpec(
        name="Reviewer → Archivist",
        required_signals=["verdict", "rationale_summary"],
        compressible_signals=["line_by_line_comments", "exploratory_discussion"],
    ),
}


@dataclass
class SignalPattern:
    """Regex pattern and validation logic for a signal type."""
    name: str
    regex: str
    description: str
    specificity_check: Optional[Callable] = None  # callable(match_text) -> bool


SIGNAL_PATTERNS = {
    "canonical_example": SignalPattern(
        name="canonical_example",
        regex=r"\*\*Canonical example\*\*:\s*(.+?)(?=\n\n|\n##|$)",
        description="Labeled canonical example from AGENTS.md signal preservation rules",
        specificity_check=lambda text: not re.search(
            r"(this is good|very good|works well|bad|wrong|incorrect)(?:\s|$)",
            text.lower()
        ) and len(text) > 20,
    ),
    "anti_pattern": SignalPattern(
        name="anti_pattern",
        regex=r"\*\*Anti-pattern\*\*:\s*(.+?)(?=\n\n|\n##|$)",
        description="Labeled anti-pattern from AGENTS.md signal preservation rules",
        specificity_check=lambda text: len(text) > 15 and not re.search(
            r"^(bad|wrong|avoid)$", text.lower().strip()
        ),
    ),
    "axiom_citation": SignalPattern(
        name="axiom_citation",
        regex=r"(MANIFESTO\.md|Endogenous-First|Algorithms Before Tokens|Local Compute-First|Documentation-First|Minimal Posture|Programmatic-First)",
        description="Explicit mention of foundational MANIFESTO.md axioms or principles",
        specificity_check=None,
    ),
    "source_url": SignalPattern(
        name="source_url",
        regex=r"\[.+?\]\(https?:\/\/[^\)]+\)",
        description="Markdown link to an external/internal documentation source",
        specificity_check=None,
    ),
    "verdict": SignalPattern(
        name="verdict",
        regex=r"(?:(?:^|\n\n)\s*(?:APPROVED|REQUEST CHANGES|approved|request changes)(?:\s|$))|(?:(?:\*{0,2}Status\*{0,2}|\*{0,2}Verdict\*{0,2}|\*{0,2}Decision\*{0,2})\s*:\s*(?:APPROVED|REQUEST CHANGES|approved|request changes))",
        description="Explicit verdict from review gate (for reviewer-to-archivist membrane)",
        specificity_check=None,
    ),
    "rationale_summary": SignalPattern(
        name="rationale_summary",
        regex=r"(?i)(rationale|reason|decision)(?:\s+\w+)*:\s*(.{30,}?)(?=\n|$)",
        description="Brief summary of decision rationale",
        specificity_check=None,
    ),
    "synthesis_structure": SignalPattern(
        name="synthesis_structure",
        regex=r"(## Executive Summary|## Pattern Catalog|## Recommendations)",
        description="Presence of synthesis document structure sections",
        specificity_check=None,
    ),
    "metrics": SignalPattern(
        name="metrics",
        regex=r"(\d+\%|\d+\.?\d* (?:agents|scripts|findings|hours)|metric|coverage|count)",
        description="Quantitative metrics or measurements",
        specificity_check=None,
    ),
    "line_by_line_comments": SignalPattern(
        name="line_by_line_comments",
        regex=r"(?i)(line-by-line|line by line|paragraph.{0,20}?assessment|detailed.{0,20}?comment|^- Line \d+:)",
        description="Detailed line-by-line or paragraph-by-paragraph review comments (should be compressed)",
        specificity_check=None,
    ),
    "exploratory_notes": SignalPattern(
        name="exploratory_notes",
        regex=r"(?i)(exploratory|preliminary|draft|working notes|rough|raw findings)",
        description="Exploratory notes and raw research material (appropriate for compression)",
        specificity_check=None,
    ),
    "background_prose": SignalPattern(
        name="background_prose",
        regex=r"(?i)(background|context|history|literature survey|related work)",
        description="Background contextual prose (appropriate for compression)",
        specificity_check=None,
    ),
}


# ===========================================================================
# Main Validation Function
# ===========================================================================

@dataclass
class ValidationResult:
    """Result of handoff permeability validation."""
    status: str  # "pass" | "fail"
    membrane_type: str
    missing_signals: list[str]
    found_signals: list[str]
    signal_counts: dict[str, int]
    warnings: list[str]
    report: str


def validate_handoff_permeability(
    handoff_text: str,
    membrane_type: str,
    required_signals: Optional[list[str]] = None,
) -> ValidationResult:
    """
    Validate that a handoff section preserves required signals for a given membrane type.

    This function implements the signal preservation rules from AGENTS.md:
    - Scout→Synthesizer: preserve Canonical example, Anti-pattern, axiom citations, source URLs
    - Synthesizer→Reviewer: preserve synthesis structure, metrics
    - Reviewer→Archivist: preserve verdict and rationale

    Args:
        handoff_text: Markdown text from a handoff section (e.g., "## Phase N Output" content).
                     This is the raw text between headings or section boundaries.
        membrane_type: One of ("scout-to-synthesizer", "synthesizer-to-reviewer",
                      "reviewer-to-archivist"). Determines which signals are required.
        required_signals: List of signal types to validate. If None, defaults to all
                         required signals for the given membrane_type.

    Returns:
        ValidationResult with status ("pass"/"fail"), missing/found signals, and report.

    Raises:
        ValueError: If membrane_type is not recognized.

    Example:
        >>> handoff = '''## Output
        >>> **Canonical example**: validate_synthesis.py enforces D4 structure...
        >>> **Anti-pattern**: Returning raw search history without compression
        >>> See MANIFESTO.md § Endogenous-First
        >>> [source](https://example.com)
        >>> '''
        >>> result = validate_handoff_permeability(handoff, "scout-to-synthesizer")
        >>> assert result.status == "pass"
    """

    if membrane_type not in MEMBRANE_SPECS:
        raise ValueError(
            f"Unknown membrane_type: {membrane_type}. "
            f"Must be one of: {', '.join(MEMBRANE_SPECS.keys())}"
        )

    spec = MEMBRANE_SPECS[membrane_type]

    # Use provided required_signals or default to spec
    if required_signals is None:
        required_signals = spec.required_signals
    else:
        # Validate that all requested signals are valid
        valid_signals = set(SIGNAL_PATTERNS.keys())
        invalid = set(required_signals) - valid_signals
        if invalid:
            raise ValueError(
                f"Invalid signal types: {', '.join(invalid)}. "
                f"Must be one of: {', '.join(valid_signals)}"
            )

    # Detect signal presence and count
    signal_counts = {}
    found_signals = []
    missing_signals = []
    warnings = []

    for signal_type in required_signals:
        pattern_spec = SIGNAL_PATTERNS[signal_type]
        matches = re.findall(pattern_spec.regex, handoff_text, re.DOTALL | re.IGNORECASE)

        # Validate specificity if checker provided
        valid_matches = matches
        if pattern_spec.specificity_check:
            valid_matches = [
                m for m in matches
                if pattern_spec.specificity_check(m if isinstance(m, str) else m[0])
            ]

        signal_counts[signal_type] = len(valid_matches)

        if len(valid_matches) > 0:
            found_signals.append(signal_type)
        else:
            missing_signals.append(signal_type)

    # Check compressible signals (warn based on presence/absence pattern)
    for signal_type in spec.compressible_signals:
        if signal_type in SIGNAL_PATTERNS:
            pattern_spec = SIGNAL_PATTERNS[signal_type]
            matches = re.findall(pattern_spec.regex, handoff_text, re.DOTALL | re.IGNORECASE)
            signal_counts[signal_type] = len(matches)

            # line_by_line_comments should warn if PRESENT (uncompressed)
            # exploratory_notes/discussion should warn if ABSENT (missing context)
            if signal_type == "line_by_line_comments" and len(matches) > 0:
                warnings.append(
                    f"⚠️ Uncompressed content detected: {signal_type} at high volume ({len(matches)} matches). "
                    f"Recommend compression per Compression-on-Ascent rule."
                )
            elif signal_type != "line_by_line_comments" and len(matches) == 0:
                warnings.append(
                    f"Compressible signal '{signal_type}' completely absent (not critical, but notable)"
                )

    # Determine pass/fail status: all required signals must be present
    status = "pass" if len(missing_signals) == 0 else "fail"

    # Generate human-readable report
    report = generate_permeability_report(
        membrane_type=membrane_type,
        status=status,
        found_signals=found_signals,
        missing_signals=missing_signals,
        signal_counts=signal_counts,
        warnings=warnings,
    )

    return ValidationResult(
        status=status,
        membrane_type=membrane_type,
        missing_signals=missing_signals,
        found_signals=found_signals,
        signal_counts=signal_counts,
        warnings=warnings,
        report=report,
    )


# ===========================================================================
# Report Generation
# ===========================================================================

def generate_permeability_report(
    membrane_type: str,
    status: str,
    found_signals: list[str],
    missing_signals: list[str],
    signal_counts: dict[str, int],
    warnings: list[str],
) -> str:
    """Generate a human-readable Markdown report of permeability validation."""

    spec = MEMBRANE_SPECS[membrane_type]

    lines = [
        f"# Handoff Permeability Validation Report",
        f"",
        f"**Membrane**: {spec.name} ({membrane_type})",
        f"**Status**: `{status.upper()}`",
        f"",
        f"## Summary",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Required signals | {len(spec.required_signals)} |",
        f"| Signals found | {len(found_signals)} |",
        f"| Signals missing | {len(missing_signals)} |",
        f"",
    ]

    if found_signals:
        lines.extend([
            f"## ✅ Preserved Signals",
            f"",
        ])
        for signal_type in found_signals:
            count = signal_counts.get(signal_type, 0)
            pattern_spec = SIGNAL_PATTERNS.get(signal_type)
            desc = pattern_spec.description if pattern_spec else ""
            lines.append(f"- **{signal_type}**: {count} occurrence(s) — {desc}")
        lines.append("")

    if missing_signals:
        lines.extend([
            f"## ❌ Missing Signals (Required)",
            f"",
        ])
        for signal_type in missing_signals:
            pattern_spec = SIGNAL_PATTERNS.get(signal_type)
            desc = pattern_spec.description if pattern_spec else ""
            lines.append(f"- **{signal_type}**: {desc}")
        lines.append("")

    if warnings:
        lines.extend([
            f"## ⚠️ Warnings",
            f"",
        ])
        for warning in warnings:
            lines.append(f"- {warning}")
        lines.append("")

    lines.extend([
        f"## Interpretation",
        f"",
    ])

    if status == "pass":
        lines.append(
            f"✅ **PASS**: Handoff preserves all required signals for {spec.name} membrane. "
            f"Signal degradation risk is low; values should propagate through the delegation boundary."
        )
    else:
        missing_str = ", ".join(f"`{s}`" for s in missing_signals)
        lines.append(
            f"❌ **FAIL**: Handoff is missing required signals: {missing_str}. "
            f"These signals must be preserved to prevent value-encoding drift across the delegation boundary. "
            f"See AGENTS.md § Focus-on-Descent / Compression-on-Ascent for signal preservation rules."
        )

    lines.append("")
    lines.extend([
        f"## Reference: AGENTS.md Signal Preservation Rules",
        f"",
        f"From [`AGENTS.md`](../../AGENTS.md) § Agent Communication → Focus-on-Descent / Compression-on-Ascent:",
        f"",
        f"> When compressing findings, preserve all labeled `**Canonical example**:` and `**Anti-pattern**:` ",
        f"> instances verbatim — compress surrounding context, not concrete illustrations. Retain at least 2 ",
        f"> explicit MANIFESTO.md axiom citations (by name + section reference) as anchors.",
    ])

    return "\n".join(lines)


# ===========================================================================
# CLI Entry Point
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Validate handoff signal preservation across agent fleet membranes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--handoff-file",
        type=str,
        required=True,
        help="Path to markdown file containing handoff text",
    )
    parser.add_argument(
        "--membrane-type",
        type=str,
        required=True,
        choices=list(MEMBRANE_SPECS.keys()),
        help="Membrane type across which the handoff occurs",
    )
    parser.add_argument(
        "--required-signals",
        type=str,
        default=None,
        help="Comma-separated list of signal types to validate (optional); defaults to all for membrane",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Write JSON report to file (default: stdout)",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "text"],
        default="json",
        help="Output format",
    )

    args = parser.parse_args()

    # Validate file exists
    handoff_file = Path(args.handoff_file)
    if not handoff_file.exists():
        print(f"Error: handoff file not found: {handoff_file}", file=sys.stderr)
        sys.exit(1)

    # Read handoff text
    try:
        handoff_text = handoff_file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading handoff file: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse required_signals if provided
    required_signals = None
    if args.required_signals:
        required_signals = [s.strip() for s in args.required_signals.split(",")]

    # Validate
    try:
        result = validate_handoff_permeability(
            handoff_text=handoff_text,
            membrane_type=args.membrane_type,
            required_signals=required_signals,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Format output
    if args.format == "json":
        output_dict = asdict(result)
        output_str = json.dumps(output_dict, indent=2)
    else:
        output_str = result.report

    # Write output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output_str, encoding="utf-8")
        print(f"Report written to: {args.output}", file=sys.stderr)
    else:
        print(output_str)

    # Exit with appropriate code
    sys.exit(0 if result.status == "pass" else 0)  # Always exit 0; status in JSON


if __name__ == "__main__":
    main()

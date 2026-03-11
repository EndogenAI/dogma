"""
parse_audit_result.py
---------------------

Purpose:
    Converts JSON provenance audit output (from audit_provenance.py) into human-readable
    Markdown reports and risk assessment tables suitable for PR comments and CI logs.

    Implements provenance risk assessment per docs/research/enforcement-tier-mapping.md
    and docs/research/bubble-clusters-substrate.md § Pattern B4 — Provenance Transparency.

    Risk levels are computed based on:
    - axiom_cite_count: Number of MANIFESTO.md citations in agent governing: field
    - test_coverage: Code coverage % of agent-associated test files
    - Activity level: Age since last modification over 90 days

    Thresholds (configurable, default baseline in gap-analysis-bubble-clusters.md § R8):
    - Green (Low risk): cite_count > threshold × 0.8 AND coverage > 80%
    - Yellow (Medium risk): cite_count between threshold × 0.5 and 0.8, OR coverage 60–80%
    - Red (High risk): cite_count < threshold × 0.5 AND coverage < 60%

Inputs:
    --audit-report FILE   Path to JSON report from audit_provenance.py
    --threshold FLOAT     Baseline citation threshold (default: 0.5; see docs/research/gap-analysis...)
    --pr-comment          Generate PR comment file at /tmp/audit-comment.md
    --output FILE         Write JSON risk assessment to file (default: stdout if --pr-comment)

Outputs:
    JSON risk assessment:
    {
        "status": "green" | "yellow" | "red",
        "summary": {
            "agents_analyzed": int,
            "green_count": int,
            "yellow_count": int,
            "red_count": int,
            "avg_cite_intensity": float,  # average cites per agent
            "overall_risk": str
        },
        "agents": [
            {
                "name": str,
                "status": str,
                "risk_level": str,
                "axiom_cites": int,
                "test_coverage": float | null,
                "notes": str
            },
            ...
        ],
        "recommendations": [str],
        "markdown_report": str
    }
    Exit code: 0 on success; 1 on error.

Usage examples:
    uv run python scripts/audit_provenance.py --output /tmp/audit.json
    uv run python scripts/parse_audit_result.py /tmp/audit.json --threshold 0.5

    # For PR commenting:
    uv run python scripts/parse_audit_result.py /tmp/audit.json --pr-comment
    gh pr comment --body-file /tmp/audit-comment.md
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# ===========================================================================
# Data Classes & Risk Assessment
# ===========================================================================


@dataclass
class AgentRiskAssessment:
    """Risk assessment for a single agent."""

    name: str
    status: str  # "orphaned" | "unverifiable" | "verified"
    axiom_cites: int
    test_coverage: Optional[float]  # % coverage, or None if unknown
    risk_level: str  # "green" | "yellow" | "red"
    notes: str  # human-readable assessment


@dataclass
class OverallRiskAssessment:
    """Aggregate risk assessment across all agents."""

    status: str  # "green" | "yellow" | "red"
    agents: list[AgentRiskAssessment]
    green_count: int
    yellow_count: int
    red_count: int
    avg_cite_intensity: float
    recommendations: list[str]
    markdown_report: str


# ===========================================================================
# Risk Computation
# ===========================================================================


def assess_agent_risk(
    name: str,
    axiom_cites: int,
    test_coverage: Optional[float],
    threshold: float = 0.5,
    orphaned: bool = False,
    unverifiable: bool = False,
) -> tuple[str, str]:
    """
    Compute risk level for a single agent.

    Args:
        name: Agent name
        axiom_cites: Count of MANIFESTO.md citations in 'governs:' field
        test_coverage: % coverage of associated tests, or None if unknown
        threshold: Baseline citation count threshold (0–1 normalized)
        orphaned: True if agent missing 'governs:' field
        unverifiable: True if agent has unverifiable axiom citations

    Returns:
        tuple of (risk_level, notes_string)
        where risk_level ∈ {"green", "yellow", "red"}
    """

    if orphaned:
        return ("red", "Orphaned: no 'governs:' field in agent spec. Cannot verify grounding in MANIFESTO.md.")

    if unverifiable:
        return ("red", f"Unverifiable axiom citations. References {axiom_cites} axiom(s) not found in MANIFESTO.md.")

    # Normalize cite counts to a 0–1 intensity scale
    # Assume threshold ~= normal expected cite count
    cite_intensity = axiom_cites / max(1, threshold * 2)  # 2x threshold = 1.0
    cite_intensity = min(1.0, cite_intensity)  # Cap at 1.0

    # Determine risk levels based on cite intensity + test coverage
    cite_threshold_high = threshold * 0.8
    cite_threshold_low = threshold * 0.5
    coverage_high = 80.0
    coverage_medium = 60.0

    # Green: strong citation intensity AND high coverage
    if axiom_cites > cite_threshold_high:
        if test_coverage is None or test_coverage > coverage_high:
            coverage_msg = (
                "High test coverage." if test_coverage and test_coverage > coverage_high else "No test data available."
            )
            return (
                "green",
                f"Strong axiom grounding ({axiom_cites} cite(s), {cite_intensity:.1%} intensity). {coverage_msg}",
            )

    # Red: weak citation intensity AND low coverage
    if axiom_cites < cite_threshold_low and (test_coverage is None or test_coverage < coverage_medium):
        return (
            "red",
            f"Low axiom grounding ({axiom_cites} cite(s), {cite_intensity:.1%} intensity) and "
            f"{'low test coverage ({:.0f}%)'.format(test_coverage) if test_coverage else 'no test data'}. "
            f"High drift risk; recommend axiom grounding review.",
        )

    # Yellow: everything else (mixed signals)
    coverage_note = f"coverage {test_coverage:.0f}%" if test_coverage else "no test data"
    return (
        "yellow",
        f"Moderate axiom grounding ({axiom_cites} cite(s), {cite_intensity:.1%} intensity), "
        f"{coverage_note}. Monitor for drift.",
    )


# ===========================================================================
# Main Parsing Function
# ===========================================================================


def parse_audit_result(
    audit_json: dict,
    threshold: float = 0.5,
) -> OverallRiskAssessment:
    """
    Parse provenance audit JSON output and generate risk assessment.

    Args:
        audit_json: Dict from audit_provenance.py output JSON
                   (keys: "files", "fleet_citation_coverage_pct", "total_unverifiable")
        threshold: Baseline axiom citation threshold (0–1 scale, default 0.5)

    Returns:
        OverallRiskAssessment with agent assessments, summary stats, and Markdown report.

    Raises:
        ValueError: If audit_json is malformed.
    """

    if "files" not in audit_json:
        raise ValueError("Missing 'files' key in audit report")

    files = audit_json.get("files", [])
    if not isinstance(files, list):
        raise ValueError("'files' must be a list")

    # Assess each agent
    assessments: list[AgentRiskAssessment] = []
    green_count = 0
    yellow_count = 0
    red_count = 0

    for file_entry in files:
        name = file_entry.get("path", "unknown")
        if name.endswith(".agent.md"):
            name = Path(name).stem  # Extract agent name from filename

        citations = file_entry.get("citations", [])
        axiom_cites = len(citations)
        orphaned = file_entry.get("orphaned", False)
        unverifiable_list = file_entry.get("unverifiable", [])

        # Assume no test coverage data from audit_provenance.py (can extend later)
        test_coverage = None

        risk_level, notes = assess_agent_risk(
            name=name,
            axiom_cites=axiom_cites,
            test_coverage=test_coverage,
            threshold=threshold,
            orphaned=orphaned,
            unverifiable=len(unverifiable_list) > 0,
        )

        if risk_level == "green":
            green_count += 1
        elif risk_level == "yellow":
            yellow_count += 1
        else:
            red_count += 1

        assessments.append(
            AgentRiskAssessment(
                name=name,
                status="orphaned" if orphaned else ("unverifiable" if unverifiable_list else "verified"),
                axiom_cites=axiom_cites,
                test_coverage=test_coverage,
                risk_level=risk_level,
                notes=notes,
            )
        )

    # Compute aggregate metrics
    total = len(assessments)
    avg_cite_intensity = sum(a.axiom_cites for a in assessments) / max(1, total)

    # Determine overall risk
    if green_count / max(1, total) > 0.7:
        overall_risk = "green"
    elif red_count / max(1, total) > 0.3:
        overall_risk = "red"
    else:
        overall_risk = "yellow"

    # Generate recommendations
    recommendations = generate_recommendations(
        overall_risk=overall_risk,
        green_count=green_count,
        red_count=red_count,
        total=total,
        avg_cite_intensity=avg_cite_intensity,
    )

    # Generate Markdown report
    markdown_report = generate_markdown_report(
        assessments=assessments,
        overall_risk=overall_risk,
        green_count=green_count,
        yellow_count=yellow_count,
        red_count=red_count,
        avg_cite_intensity=avg_cite_intensity,
        recommendations=recommendations,
    )

    return OverallRiskAssessment(
        status=overall_risk,
        agents=assessments,
        green_count=green_count,
        yellow_count=yellow_count,
        red_count=red_count,
        avg_cite_intensity=avg_cite_intensity,
        recommendations=recommendations,
        markdown_report=markdown_report,
    )


# ===========================================================================
# Recommendation Generation
# ===========================================================================


def generate_recommendations(
    overall_risk: str,
    green_count: int,
    red_count: int,
    total: int,
    avg_cite_intensity: float,
) -> list[str]:
    """Generate actionable recommendations based on risk profile."""

    recommendations = []

    if overall_risk == "red":
        recommendations.append(
            f"🚨 HIGH DRIFT RISK: {red_count}/{total} agents have weak axiom grounding. "
            f"Recommend immediate axiom citation audit and cross-reference densification."
        )
    elif overall_risk == "yellow":
        recommendations.append(
            f"⚠️  MEDIUM DRIFT RISK: {red_count}/{total} agents need grounding review. "
            f"Monitor cite intensity and test coverage trends."
        )
    else:
        recommendations.append(
            f"✅ GREEN: {green_count}/{total} agents have strong axiom grounding. "
            f"Maintain cite intensity ({avg_cite_intensity:.1f} avg)."
        )

    if avg_cite_intensity < 0.5:
        recommendations.append(
            f"Low average axiom cite intensity ({avg_cite_intensity:.1f}). "
            f"Consider citing specific MANIFESTO.md sections in agent 'governs:' fields."
        )

    return recommendations


# ===========================================================================
# Markdown Report Generation
# ===========================================================================


def generate_markdown_report(
    assessments: list[AgentRiskAssessment],
    overall_risk: str,
    green_count: int,
    yellow_count: int,
    red_count: int,
    avg_cite_intensity: float,
    recommendations: list[str],
) -> str:
    """Generate human-readable Markdown report."""

    risk_emoji = {
        "green": "🟢",
        "yellow": "🟡",
        "red": "🔴",
    }

    lines = [
        "# Provenance Audit Report",
        "",
        f"**Overall Risk Level**: {risk_emoji.get(overall_risk, '?')} **{overall_risk.upper()}**",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Agents Analyzed | {len(assessments)} |",
        f"| Green (Low Risk) | {green_count} |",
        f"| Yellow (Medium Risk) | {yellow_count} |",
        f"| Red (High Risk) | {red_count} |",
        f"| Avg Axiom Cite Intensity | {avg_cite_intensity:.2f} |",
        "",
    ]

    if recommendations:
        lines.extend(
            [
                "## Recommendations",
                "",
            ]
        )
        for rec in recommendations:
            lines.append(f"- {rec}")
        lines.append("")

    lines.extend(
        [
            "## Agent Risk Assessment",
            "",
            "| Agent | Status | Risk | Cites | Notes |",
            "|-------|--------|------|-------|-------|",
        ]
    )

    for assessment in sorted(assessments, key=lambda a: ("red", "yellow", "green").index(a.risk_level)):
        emoji = risk_emoji.get(assessment.risk_level, "?")
        # Truncate notes if too long
        notes_short = assessment.notes[:80] + "..." if len(assessment.notes) > 80 else assessment.notes
        lines.append(
            f"| {assessment.name} | {assessment.status} | "
            f"{emoji} {assessment.risk_level} | {assessment.axiom_cites} | {notes_short} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- **Green**: Strong axiom grounding; low risk of value-encoding drift",
            "- **Yellow**: Mixed signals; monitor cite intensity and test coverage trends",
            "- **Red**: Weak axiom grounding; high drift risk; recommend immediate review",
            "",
            "See [`docs/research/values-encoding.md`](../../docs/research/values-encoding.md) "
            "and [`docs/research/enforcement-tier-mapping.md`](../../docs/research/enforcement-tier-mapping.md) "
            "for detailed methodology.",
        ]
    )

    return "\n".join(lines)


# ===========================================================================
# CLI Entry Point
# ===========================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Parse provenance audit JSON and generate risk assessment Markdown.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "audit_report",
        type=str,
        help="Path to JSON report from audit_provenance.py",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Baseline axiom citation threshold (default: 0.5)",
    )
    parser.add_argument(
        "--pr-comment",
        action="store_true",
        help="Generate PR comment file at /tmp/audit-comment.md",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Write JSON risk assessment to file (default: stdout if --pr-comment, else JSON)",
    )

    args = parser.parse_args()

    # Read audit report
    audit_file = Path(args.audit_report)
    if not audit_file.exists():
        print(f"Error: audit report not found: {audit_file}", file=sys.stderr)
        sys.exit(1)

    try:
        audit_json = json.loads(audit_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse and assess
    try:
        result = parse_audit_result(audit_json, threshold=args.threshold)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.pr_comment:
        # Write markdown to PR comment file
        comment_file = Path("/tmp/audit-comment.md")
        comment_file.write_text(result.markdown_report, encoding="utf-8")
        print(f"PR comment written to: {comment_file}", file=sys.stderr)

    # Always write JSON to output file if specified, or stdout
    output_dict = {
        "status": result.status,
        "summary": {
            "agents_analyzed": len(result.agents),
            "green_count": result.green_count,
            "yellow_count": result.yellow_count,
            "red_count": result.red_count,
            "avg_cite_intensity": result.avg_cite_intensity,
            "overall_risk": result.status,
        },
        "agents": [
            {
                "name": a.name,
                "status": a.status,
                "risk_level": a.risk_level,
                "axiom_cites": a.axiom_cites,
                "test_coverage": a.test_coverage,
                "notes": a.notes,
            }
            for a in result.agents
        ],
        "recommendations": result.recommendations,
        "markdown_report": result.markdown_report,
    }

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(output_dict, indent=2), encoding="utf-8")
        print(f"JSON report written to: {args.output}", file=sys.stderr)
    else:
        print(json.dumps(output_dict, indent=2))

    sys.exit(0)


if __name__ == "__main__":
    main()

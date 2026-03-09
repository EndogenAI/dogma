"""
detect_drift.py
---------------
Purpose:
    Detects value-encoding drift in .agent.md files by measuring the presence
    of canonical watermark phrases from MANIFESTO.md axioms. A low score
    indicates the agent file may have drifted from foundational values.

Inputs:
    --agents-dir  PATH   Directory of .agent.md files (default: .github/agents/)
    --threshold   FLOAT  Warn if any agent's drift score falls below this value
                         (default: 0.33)
    --fail-below  FLOAT  Exit 1 if any agent scores below this threshold
                         (optional; default: disabled — advisory only)
    --output      FILE   Write JSON report to this file (default: stdout)
    --format      json|summary  Output format (default: json)

Outputs:
    JSON report: { "agents": [{"file", "drift_score", "missing"}],
                   "fleet_avg", "below_threshold" }
    Summary (--format summary): one line per agent with score and status
    Exit code: 0 if all agents meet --fail-below threshold (or no --fail-below
               set); 1 if any agent falls below --fail-below.

Usage examples:
    uv run python scripts/detect_drift.py
    uv run python scripts/detect_drift.py --format summary
    uv run python scripts/detect_drift.py --fail-below 0.5 --output /tmp/drift.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WATERMARK_PHRASES: tuple[str, ...] = (
    "Endogenous-First",
    "Algorithms Before Tokens",
    "Local Compute-First",
    "encode-before-act",
    "morphogenetic seed",
    "programmatic-first",
)

_DEFAULT_THRESHOLD = 0.33


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def score_agent_file(path: Path) -> dict:
    """
    Read one .agent.md file and compute its watermark drift score.

    Returns a dict:
        {
            "file":        str   — repo-relative or absolute path as string
            "drift_score": float — matched_phrases / len(WATERMARK_PHRASES)
            "missing":     list[str] — phrases absent from the body
        }
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"WARNING: Cannot read {path}: {exc}", file=sys.stderr)
        return {"file": str(path), "drift_score": 0.0, "missing": list(WATERMARK_PHRASES)}

    # Strip YAML frontmatter if present (everything between leading --- fences)
    body = re.sub(r"^---\r?\n.*?\r?\n---\r?\n", "", text, count=1, flags=re.DOTALL)
    body_lower = body.lower()

    missing = [p for p in WATERMARK_PHRASES if p.lower() not in body_lower]
    matched = len(WATERMARK_PHRASES) - len(missing)
    score = matched / len(WATERMARK_PHRASES)

    return {"file": str(path), "drift_score": round(score, 4), "missing": missing}


def build_report(results: list[dict], threshold: float) -> dict:
    """
    Assemble the fleet-wide drift report from per-agent results.
    """
    fleet_avg = sum(r["drift_score"] for r in results) / len(results) if results else 0.0
    below = [r["file"] for r in results if r["drift_score"] < threshold]
    return {
        "agents": results,
        "fleet_avg": round(fleet_avg, 4),
        "below_threshold": below,
    }


def format_summary(report: dict, threshold: float) -> str:
    """Render a human-readable one-line-per-agent summary."""
    lines = []
    for agent in report["agents"]:
        status = "⚠️  WARN" if agent["drift_score"] < threshold else "✓  OK  "
        missing_str = f"  missing: {agent['missing']}" if agent["missing"] else ""
        lines.append(f"{status}  score={agent['drift_score']:.2f}  {agent['file']}{missing_str}")
    lines.append(f"\nFleet average drift score: {report['fleet_avg']:.4f}")
    if report["below_threshold"]:
        lines.append(f"Below threshold ({threshold}): {len(report['below_threshold'])} agent(s)")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect value-encoding drift in .agent.md files via watermark-phrase analysis."
    )
    parser.add_argument(
        "--agents-dir",
        default=None,
        metavar="DIR",
        help="Directory of .agent.md files. Default: .github/agents/",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=_DEFAULT_THRESHOLD,
        metavar="FLOAT",
        help=f"Warn if score below threshold (default: {_DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--fail-below",
        type=float,
        default=None,
        metavar="FLOAT",
        help="Exit 1 if any agent score falls below this value (default: disabled)",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="FILE",
        help="Write JSON report to this file. Default: stdout",
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format: json (default) or summary",
    )
    args = parser.parse_args()

    # Locate agents directory
    if args.agents_dir:
        agents_dir = Path(args.agents_dir).expanduser().resolve()
    else:
        # Walk up from script location to find repo root
        candidate = Path(__file__).resolve().parent
        while candidate != candidate.parent:
            if (candidate / "AGENTS.md").exists():
                agents_dir = candidate / ".github" / "agents"
                break
            candidate = candidate.parent
        else:
            agents_dir = Path(__file__).resolve().parent.parent / ".github" / "agents"

    if not agents_dir.is_dir():
        print(f"ERROR: Agents directory not found: {agents_dir}", file=sys.stderr)
        return 1

    agent_files = sorted(agents_dir.glob("*.agent.md"))
    if not agent_files:
        print(f"WARNING: No .agent.md files found in {agents_dir}", file=sys.stderr)

    results = [score_agent_file(f) for f in agent_files]

    # Warn about below-threshold agents
    threshold = args.threshold
    for r in results:
        if r["drift_score"] < threshold:
            print(
                f"WARNING: {r['file']} drift_score={r['drift_score']:.4f} "
                f"(below {threshold}) — missing: {r['missing']}",
                file=sys.stderr,
            )

    report = build_report(results, threshold)

    # Render output
    if args.format == "summary":
        output_text = format_summary(report, threshold) + "\n"
    else:
        output_text = json.dumps(report, indent=2) + "\n"

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_text, encoding="utf-8")
        print(f"Drift report: {len(results)} agents → {out_path}", file=sys.stderr)
    else:
        sys.stdout.write(output_text)
        print(
            f"Drift report: {len(results)} agents, fleet_avg={report['fleet_avg']:.4f}",
            file=sys.stderr,
        )

    # --fail-below exit logic
    if args.fail_below is not None:
        if any(r["drift_score"] < args.fail_below for r in results):
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

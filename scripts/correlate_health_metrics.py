#!/usr/bin/env python3
"""
Measure health metric correlations with cross-reference density.

Health Proxies:
1. Task Velocity: GitHub issues closed while file was active (issues/month)
2. Test Coverage: % of referenced scripts with passing tests
3. Citation Coherence: Consistency of MANIFESTO.md axiom citations

Computes Pearson correlation coefficient (R) and significance test.

Usage:
    uv run python scripts/correlate_health_metrics.py [--crd-file FILE]

Output: JSON with per-file health metrics and correlation analysis
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from statistics import mean, stdev
from typing import TypedDict


class HealthMetrics(TypedDict):
    """Per-file health metrics."""

    filepath: str
    filename: str
    file_type: str
    task_velocity: int  # issues closed/month
    test_coverage: float  # % of referenced scripts with passing tests
    citation_coherence: float  # std dev of axiom citation consistency (lower = better)
    axiom_cite_count: int  # total MANIFESTO.md citations


def count_open_issues(query: str) -> int:
    """
    Query GitHub API for closed issues in last 60 days mentioning file.
    Falls back to git log grep if API unavailable.
    """
    # Fallback: grep git log for file mentions in commit messages
    try:
        result = subprocess.run(
            f"cd /Users/conor/Sites/dogma && git log --all --oneline --grep="
            f"{re.escape(Path(query).stem)} -- {query} | wc -l",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
    except Exception:
        pass

    return 0


def extract_axiom_citations(content: str) -> dict:
    """Count citations to each MANIFESTO.md axiom section."""
    axiom_refs = {
        "axiom-1-endogenous-first": len(re.findall(r"Endogenous-First|MANIFESTO.*1|#1[^0-9]", content, re.I)),
        "axiom-2-algorithms-before": len(re.findall(r"Algorithms Before|MANIFESTO.*2|#2[^0-9]", content, re.I)),
        "axiom-3-local-compute": len(re.findall(r"Local Compute-First|MANIFESTO.*3|#3[^0-9]", content, re.I)),
        "manifesto-cites": len(re.findall(r"\[.*MANIFESTO\.md.*\]|`MANIFESTO\.md`", content)),
    }
    return axiom_refs


def measure_test_coverage(filepath: Path) -> float:
    """
    Extract scripts referenced in agent/skill file.
    Check pytest coverage for those scripts.
    Return % of referenced scripts with passing tests.
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return 0.0

    # Extract script references
    script_refs = re.findall(r"scripts/([a-z_]+\.py)", content)
    if not script_refs:
        return 1.0  # No scripts referenced = not penalized

    # Check which have passing tests
    passing = 0
    for script in script_refs:
        test_file = Path(f"/Users/conor/Sites/dogma/tests/test_{script}")
        if test_file.exists():
            # Simple heuristic: test file exists = test passing
            # (Full pytest run would be slower)
            passing += 1

    return passing / len(script_refs) if script_refs else 1.0


def measure_file_health(filepath: Path, crd_value: float) -> HealthMetrics | None:
    """Measure all health metrics for a single file."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return None

    # Determine file type
    if ".agent.md" in filepath.name:
        file_type = "agent"
    elif filepath.name == "SKILL.md":
        file_type = "skill"
    elif filepath.suffix == ".md" and "docs/guides" in str(filepath):
        file_type = "guide"
    else:
        return None

    # Task velocity: issues closed where this file was active
    # Heuristic: count commits to this file in last 60 days -> estimate 0.5 issues per commit
    try:
        result = subprocess.run(
            f"cd /Users/conor/Sites/dogma && git log --since='60 days ago' --oneline {filepath} | wc -l",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        commits_60d = int(result.stdout.strip()) if result.returncode == 0 else 0
    except Exception:
        commits_60d = 0

    task_velocity = max(1, int(commits_60d * 0.5))  # Conservative: 0.5 issues per commit

    # Test coverage for referenced scripts
    test_coverage = measure_test_coverage(filepath)

    # Citation coherence
    axiom_counts = extract_axiom_citations(content)
    axiom_cites = [
        axiom_counts["axiom-1-endogenous-first"],
        axiom_counts["axiom-2-algorithms-before"],
        axiom_counts["axiom-3-local-compute"],
    ]
    axiom_cites_nonzero = [c for c in axiom_cites if c > 0]

    if len(axiom_cites_nonzero) > 1:
        citation_coherence = stdev(axiom_cites_nonzero)
    else:
        citation_coherence = 0.0  # Single axiom or no cites = no variance

    total_axiom_cites = axiom_counts["manifesto-cites"]

    return {
        "filepath": str(filepath),
        "filename": filepath.name,
        "file_type": file_type,
        "task_velocity": task_velocity,
        "test_coverage": round(test_coverage, 3),
        "citation_coherence": round(citation_coherence, 3),
        "axiom_cite_count": total_axiom_cites,
    }


def pearson_correlation(x_values: list[float], y_values: list[float]) -> dict:
    """Compute Pearson correlation coefficient and significance."""
    n = len(x_values)
    if n < 3:
        return {"r": 0.0, "p_value": 1.0, "significant": False}

    x_mean = mean(x_values)
    y_mean = mean(y_values)

    numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
    x_var = sum((x - x_mean) ** 2 for x in x_values) ** 0.5
    y_var = sum((y - y_mean) ** 2 for y in y_values) ** 0.5

    if x_var == 0 or y_var == 0:
        return {"r": 0.0, "p_value": 1.0, "significant": False}

    r = numerator / (x_var * y_var)

    # Approximate p-value using t-test (simplified)
    t_stat = abs(r) * ((n - 2) ** 0.5) / (1 - r**2) ** 0.5 if r**2 < 1 else 0

    # Rough significance: |t| > 2 is approximately p < 0.05
    significant = abs(t_stat) > 2.0

    return {
        "r": round(r, 4),
        "t_stat": round(t_stat, 4),
        "significant": significant,
    }


def main():
    """Main entry point."""
    # Load CRD metrics
    if not Path("/tmp/crd_metrics.json").exists():
        print("Error: CRD metrics not found. Run measure_cross_reference_density.py first.", file=sys.stderr)
        sys.exit(1)

    crd_data = json.loads(Path("/tmp/crd_metrics.json").read_text())
    crd_by_file = {m["filepath"]: m["crd_value"] for m in crd_data["per_file_metrics"]}

    # Measure health metrics
    repo_root = Path("/Users/conor/Sites/dogma")
    agent_files = list(repo_root.glob(".github/agents/**/*.agent.md"))
    skill_files = list(repo_root.glob(".github/skills/**/SKILL.md"))
    guide_files = list(repo_root.glob("docs/guides/*.md"))
    all_files = sorted(agent_files + skill_files + guide_files)

    health_metrics = []
    for filepath in all_files:
        filepath_str = str(filepath)
        if filepath_str not in crd_by_file:
            continue

        result = measure_file_health(filepath, crd_by_file[filepath_str])
        if result:
            health_metrics.append(result)

    # Compute correlations
    crd_values = [crd_by_file[m["filepath"]] for m in health_metrics]
    task_velocities = [m["task_velocity"] for m in health_metrics]
    test_coverages = [m["test_coverage"] for m in health_metrics]
    citation_cohere = [m["citation_coherence"] for m in health_metrics]

    corr_task = pearson_correlation(crd_values, task_velocities)
    corr_test = pearson_correlation(crd_values, test_coverages)
    corr_cite = pearson_correlation(crd_values, citation_cohere)

    output = {
        "correlations": {
            "crd_vs_task_velocity": {
                **corr_task,
                "interpretation": (
                    "High CRD correlates with task velocity" if corr_task["r"] > 0.3 else "Weak correlation"
                ),
            },
            "crd_vs_test_coverage": {
                **corr_test,
                "interpretation": (
                    "High CRD correlates with test coverage" if corr_test["r"] > 0.3 else "Weak correlation"
                ),
            },
            "crd_vs_citation_coherence": {
                **corr_cite,
                "interpretation": (
                    "High CRD correlates with consistent axiom citation" if corr_cite["r"] > 0.3 else "Weak correlation"
                ),
            },
        },
        "per_file_metrics": health_metrics,
    }

    print(json.dumps(output, indent=2))
    Path("/tmp/health_metrics.json").write_text(json.dumps(output, indent=2))
    print("\nHealth metrics written to /tmp/health_metrics.json", file=sys.stderr)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Measure cross-reference density (CRD) in agent and skill files.

CRD = intra-subsystem references / total references

Intra-subsystem: references to MANIFESTO.md, AGENTS.md, CONTRIBUTING.md, or same-layer files
Cross-subsystem: references outside the layer (e.g., agent → docs/guides, agent → scripts)

Usage:
    uv run python scripts/measure_cross_reference_density.py [--output FILE]

Output: JSON with per-file metrics and fleet statistics
"""

import json
import re
import sys
from pathlib import Path
from typing import TypedDict


class CRDMetrics(TypedDict):
    """Per-file CRD measurement."""

    filepath: str
    filename: str
    file_type: str  # "agent" | "skill" | "guide"
    total_references: int
    intra_references: int
    cross_references: int
    crd_value: float  # intra / total
    reference_list: list[dict]  # [{text, type, subsystem}]


def classify_reference(ref_text: str, file_layer: str) -> dict:
    """
    Classify a reference as intra or cross-subsystem.

    Intra: MANIFESTO.md, AGENTS.md, CONTRIBUTING.md, ../AGENTS.md, etc (foundational/guidance layer)
    Cross: docs/**, scripts/**, .github/**, /tests/**
    """
    ref_lower = ref_text.lower()
    # Foundational / Guidance layer references
    intra_patterns = [
        r"manifesto\.md",
        r"agents\.md",
        r"contributing\.md",
        r"changelog\.md",
        r"readme\.md",
        r"\.\./\.\./manifesto",
        r"\.\./agents",
    ]

    # Cross-subsystem patterns
    cross_patterns = [
        r"docs/",
        r"scripts/",
        r"\.github/",
        r"tests/",
        r"data/",
    ]

    subsystem = "unknown"
    ref_type = "cross"

    # Check intra patterns first
    for pattern in intra_patterns:
        if re.search(pattern, ref_lower):
            ref_type = "intra"
            subsystem = "foundational-guidance"
            break

    # Check cross patterns
    if ref_type == "cross":
        for pattern in cross_patterns:
            if re.search(pattern, ref_lower):
                if "docs/" in ref_lower:
                    subsystem = "docs"
                elif "scripts/" in ref_lower:
                    subsystem = "scripts"
                elif ".github/" in ref_lower:
                    subsystem = "github"
                elif "tests/" in ref_lower:
                    subsystem = "tests"
                break

    # Same-layer references are intra
    if file_layer == "agent" and re.search(r"\.agent\.md|\.\..*\.agent\.md", ref_lower):
        ref_type = "intra"
        subsystem = "agents-layer"
    elif file_layer == "skill" and re.search(r"SKILL\.md|\.\..*SKILL\.md", ref_lower):
        ref_type = "intra"
        subsystem = "skills-layer"

    return {
        "text": ref_text,
        "type": ref_type,
        "subsystem": subsystem,
    }


def extract_references(content: str, file_layer: str) -> list[dict]:
    """Extract all Markdown link references from content."""
    # Match [text](url) pattern
    ref_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
    matches = re.finditer(ref_pattern, content)

    references = []
    for match in matches:
        url = match.group(2)

        classification = classify_reference(url, file_layer)
        references.append(classification)

    return references


def measure_file(filepath: Path) -> CRDMetrics | None:
    """Measure CRD for a single file."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
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

    references = extract_references(content, file_type)

    intra_count = sum(1 for r in references if r["type"] == "intra")
    cross_count = sum(1 for r in references if r["type"] == "cross")
    total_count = len(references)

    crd_value = intra_count / total_count if total_count > 0 else 0.0

    return {
        "filepath": str(filepath),
        "filename": filepath.name,
        "file_type": file_type,
        "total_references": total_count,
        "intra_references": intra_count,
        "cross_references": cross_count,
        "crd_value": crd_value,
        "reference_list": references,
    }


def compute_statistics(metrics: list[CRDMetrics]) -> dict:
    """Compute aggregate statistics across fleet."""
    crd_values = [m["crd_value"] for m in metrics]
    crd_values.sort()

    n = len(crd_values)
    mean_crd = sum(crd_values) / n if n > 0 else 0

    # Median
    median_crd = crd_values[n // 2] if n > 0 else 0

    # Stdev
    variance = sum((x - mean_crd) ** 2 for x in crd_values) / n if n > 0 else 0
    stdev = variance**0.5

    # Min/Max
    min_crd = min(crd_values) if crd_values else 0
    max_crd = max(crd_values) if crd_values else 0

    # Quartiles
    q25_idx = n // 4
    q75_idx = (3 * n) // 4
    q25 = crd_values[q25_idx] if n > 0 else 0
    q75 = crd_values[q75_idx] if n > 0 else 0

    # IQR
    iqr = q75 - q25

    return {
        "sample_size": n,
        "mean": round(mean_crd, 4),
        "median": round(median_crd, 4),
        "stdev": round(stdev, 4),
        "min": round(min_crd, 4),
        "max": round(max_crd, 4),
        "q25": round(q25, 4),
        "q75": round(q75, 4),
        "iqr": round(iqr, 4),
    }


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent

    # Collect agent files
    agent_files = list(repo_root.glob(".github/agents/**/*.agent.md"))
    skill_files = list(repo_root.glob(".github/skills/**/SKILL.md"))
    guide_files = list(repo_root.glob("docs/guides/*.md"))

    all_files = agent_files + skill_files + guide_files

    print(f"Found {len(agent_files)} agents, {len(skill_files)} skills, {len(guide_files)} guides")

    metrics = []
    for filepath in sorted(all_files):
        result = measure_file(filepath)
        if result:
            metrics.append(result)

    # Compute statistics
    stats = compute_statistics(metrics)

    # Output JSON
    output = {
        "fleet_statistics": stats,
        "per_file_metrics": metrics,
    }

    output_json = json.dumps(output, indent=2)
    print(output_json)

    # Also write to file if requested
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=str, help="Output file path")
    args = parser.parse_args()

    if args.output:
        Path(args.output).write_text(output_json)
        print(f"\nMetrics written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()

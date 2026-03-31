#!/usr/bin/env python3
"""
check_fleet_antipatterns.py — Detect fleet anti-patterns in the agent fleet.

Purpose:
    Detects structural anti-patterns in the EndogenAI agent fleet:
    - Circular delegation cycles (agents delegate in a loop)
    - Orphaned agents (no inbound or outbound delegations)
    - Posture bloat (agents with >9 tools violating Miller's Law)
    - Disconnected components (isolated agent clusters)

Inputs:
    --coupling-report PATH  — JSON coupling report from analyse_fleet_coupling.py (optional).
                              If not provided, runs analyse_fleet_coupling.py automatically.
    --agents-dir PATH       — Agent files directory (default: .github/agents/).
    --dry-run               — Show what would be checked without failing.

Outputs:
    Prints detected anti-patterns to stdout.
    Exit code 0 if no anti-patterns detected; 1 if any detected; 2 on I/O error.

Usage:
    # Run with auto-generated coupling report:
    uv run python scripts/check_fleet_antipatterns.py

    # Run with existing coupling report:
    uv run python scripts/check_fleet_antipatterns.py --coupling-report /tmp/coupling.json

    # Dry-run mode:
    uv run python scripts/check_fleet_antipatterns.py --dry-run

Exit codes:
    0 — success: no anti-patterns detected
    1 — anti-pattern detected (circular delegation, orphaned agent, posture bloat, disconnected)
    2 — I/O error or missing dependencies
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import networkx as nx
import yaml


def _get_root() -> Path:
    """Return the workspace root (parent of scripts/). Monkeypatched in tests."""
    return Path(__file__).resolve().parent.parent


def load_coupling_data(report_path: Path | None, root: Path) -> dict | None:
    """Load or generate NK coupling data.

    Args:
        report_path: Path to existing coupling JSON report, or None to generate.
        root: Workspace root path.

    Returns:
        Coupling data dict, or None on error.
    """
    if report_path and report_path.exists():
        try:
            with report_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            print(f"ERROR: Failed to load {report_path}: {exc}", file=sys.stderr)
            return None

    # Generate coupling report
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "analyse_fleet_coupling.py"),
                "--format",
                "json",
                "--output",
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print(f"ERROR: analyse_fleet_coupling.py failed: {result.stderr}", file=sys.stderr)
            return None

        with tmp_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        print(f"ERROR: Failed to generate coupling report: {exc}", file=sys.stderr)
        return None
    finally:
        tmp_path.unlink(missing_ok=True)


def build_delegation_graph(coupling_data: dict, root: Path) -> nx.DiGraph:
    """Build directed delegation graph from coupling data and agent files.

    Args:
        coupling_data: NK coupling report dict.
        root: Workspace root path.

    Returns:
        NetworkX directed graph with agents as nodes and delegation as edges.
    """
    graph = nx.DiGraph()

    # Add all agents as nodes
    for agent in coupling_data.get("agents", []):
        graph.add_node(agent["name"])

    # Parse agent files for handoff relationships
    agents_dir = root / ".github" / "agents"
    if not agents_dir.exists():
        return graph

    for agent_file in agents_dir.glob("*.agent.md"):
        try:
            text = agent_file.read_text(encoding="utf-8")
            frontmatter = _parse_yaml_frontmatter(text)
            source_name = frontmatter.get("name")
            if not source_name:
                continue

            handoffs = frontmatter.get("handoffs", [])
            for handoff in handoffs:
                if isinstance(handoff, dict):
                    target = handoff.get("agent") or handoff.get("label") or ""
                elif isinstance(handoff, str):
                    target = handoff
                else:
                    continue

                target = target.strip()
                if target and source_name != target:
                    graph.add_edge(source_name, target)
        except Exception:
            continue

    return graph


def _parse_yaml_frontmatter(text: str) -> dict:
    """Extract and parse YAML frontmatter from an .agent.md file."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return {}


def detect_circular_delegation(graph: nx.DiGraph) -> list[list[str]]:
    """Detect circular delegation cycles using NetworkX.

    Args:
        graph: Directed delegation graph.

    Returns:
        List of cycles, each cycle is a list of agent names.
    """
    try:
        cycles = list(nx.simple_cycles(graph))
        return cycles
    except Exception:
        return []


def detect_orphaned_agents(graph: nx.DiGraph) -> list[str]:
    """Detect orphaned agents (in-degree = 0 AND out-degree = 0).

    Args:
        graph: Directed delegation graph.

    Returns:
        List of orphaned agent names.
    """
    orphaned = []
    for node in graph.nodes():
        if graph.in_degree(node) == 0 and graph.out_degree(node) == 0:
            orphaned.append(node)
    return orphaned


def detect_posture_bloat(root: Path) -> list[tuple[str, int]]:
    """Detect agents with >9 tools (violates Miller's Law).

    Args:
        root: Workspace root path.

    Returns:
        List of tuples (agent_name, tool_count).
    """
    bloated = []
    agents_dir = root / ".github" / "agents"
    if not agents_dir.exists():
        return bloated

    for agent_file in agents_dir.glob("*.agent.md"):
        try:
            text = agent_file.read_text(encoding="utf-8")
            frontmatter = _parse_yaml_frontmatter(text)
            name = frontmatter.get("name")
            tools = frontmatter.get("tools", [])

            if name and isinstance(tools, list) and len(tools) > 9:
                bloated.append((name, len(tools)))
        except Exception:
            continue

    return bloated


def detect_disconnected_components(graph: nx.DiGraph) -> list[list[str]]:
    """Detect disconnected components (isolated agent clusters).

    Args:
        graph: Directed delegation graph.

    Returns:
        List of components, each component is a list of agent names.
        Returns empty list if graph is fully connected or has ≤1 component.
    """
    try:
        undirected = graph.to_undirected()
        components = list(nx.connected_components(undirected))
        # Only flag if multiple disconnected components exist
        if len(components) > 1:
            return [sorted(list(comp)) for comp in components]
        return []
    except Exception:
        return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect fleet anti-patterns in the agent fleet.")
    parser.add_argument(
        "--coupling-report",
        type=Path,
        help="Path to JSON coupling report from analyse_fleet_coupling.py.",
    )
    parser.add_argument(
        "--agents-dir",
        type=Path,
        default=None,
        help="Agent files directory (default: .github/agents/).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be checked without failing.",
    )
    args = parser.parse_args()

    root = _get_root()

    # Load or generate coupling data
    coupling_data = load_coupling_data(args.coupling_report, root)
    if coupling_data is None:
        return 2

    # Build delegation graph
    graph = build_delegation_graph(coupling_data, root)

    # Run anti-pattern detections
    antipatterns_found = False

    # 1. Circular delegation
    cycles = detect_circular_delegation(graph)
    if cycles:
        antipatterns_found = True
        print("⚠ CIRCULAR DELEGATION DETECTED:")
        for cycle in cycles:
            print(f"  → {' → '.join(cycle + [cycle[0]])}")
        print()

    # 2. Orphaned agents
    orphaned = detect_orphaned_agents(graph)
    if orphaned:
        antipatterns_found = True
        print("⚠ ORPHANED AGENTS DETECTED:")
        for agent in orphaned:
            print(f"  → {agent}")
        print()

    # 3. Posture bloat
    bloated = detect_posture_bloat(root)
    if bloated:
        antipatterns_found = True
        print("⚠ POSTURE BLOAT DETECTED (>9 tools):")
        for agent_name, tool_count in bloated:
            print(f"  → {agent_name}: {tool_count} tools")
        print()

    # 4. Disconnected components
    components = detect_disconnected_components(graph)
    if components:
        antipatterns_found = True
        print("⚠ DISCONNECTED COMPONENTS DETECTED:")
        for i, comp in enumerate(components, 1):
            print(f"  Component {i}: {', '.join(comp)}")
        print()

    if args.dry_run:
        print("[DRY RUN] No exit code set.")
        return 0

    if antipatterns_found:
        print("Fleet anti-patterns detected. See output above.")
        return 1

    print("✓ No fleet anti-patterns detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

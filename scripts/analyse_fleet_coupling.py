"""scripts/analyse_fleet_coupling.py — NK K-coupling analysis for the agent fleet

Purpose:
    Computes K-coupling metrics for the EndogenAI agent fleet using the
    Kauffman NK model formalisation from Sprint 12:
        - N = number of agents
        - K per agent = number of distinct agents it directly delegates to
          OR receives delegation from (in-degree + out-degree in the
          delegation graph)
        - High-K nodes (K > threshold) are structural bottlenecks
        - Modularity Q via Newman-Girvan community detection (NetworkX)

    Implemented as a quarterly audit script; output integrates with
    ``check_substrate_health.py``.

Source:
    ``docs/research/h2-nk-model-formalization.md``
    ``docs/research/intelligence-architecture-synthesis.md``
    GitHub issue #291

Inputs:
    data/delegation-gate.yml     — delegation routes per agent
    .github/agents/*.agent.md   — agent files with ``handoffs:`` YAML blocks
    --agents-dir PATH            — agent files dir (default: .github/agents/)
    --delegation-gate PATH       — delegation-gate.yml (default: data/delegation-gate.yml)
    --threshold INT              — high-K warning threshold (default: 6)
    --format json|table|summary  — output format (default: table)
    --output FILE                — write JSON report to file (optional)

Outputs:
    JSON report:
        {
          "n_agents": int,
          "mean_k": float,
          "k_critical": float,
          "modularity_q": float | null,
          "regime": "ordered" | "chaotic" | "edge_of_chaos",
          "agents": [{"name": str, "k": int, "in_degree": int, "out_degree": int,
                       "bottleneck": bool}],
          "high_k_nodes": [str],
          "communities": [[str]] | null
        }
    Table: formatted ASCII summary
    Summary: one-line fleet health string

Exit codes:
    0 — success
    1 — argument/parse error or missing required files

Usage:
    uv run python scripts/analyse_fleet_coupling.py
    uv run python scripts/analyse_fleet_coupling.py --format json
    uv run python scripts/analyse_fleet_coupling.py --threshold 5 --format summary
    uv run python scripts/analyse_fleet_coupling.py --output /tmp/coupling.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
DEFAULT_AGENTS_DIR = REPO_ROOT / ".github" / "agents"
DEFAULT_DELEGATION_GATE = REPO_ROOT / "data" / "delegation-gate.yml"


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _load_yaml_frontmatter(text: str) -> dict:
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


def _parse_handoff_names(handoffs: list) -> list[str]:
    """Extract target agent names from a handoffs list.

    Handles both dict form ({agent: "Name", ...}) and plain string form.
    """
    names: list[str] = []
    for h in handoffs:
        if isinstance(h, dict):
            agent_name = h.get("agent") or h.get("label") or ""
            if agent_name:
                names.append(str(agent_name).strip())
        elif isinstance(h, str):
            names.append(h.strip())
    return names


def load_agents_from_files(agents_dir: Path) -> dict[str, list[str]]:
    """Return {agent_name: [handoff_targets]} parsed from .agent.md frontmatter."""
    routes: dict[str, list[str]] = {}
    for path in agents_dir.glob("*.agent.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        fm = _load_yaml_frontmatter(text)
        name = fm.get("name")
        if not name:
            # Fall back to capitalised filename slug
            name = path.stem.replace("-", " ").title()
        handoffs = fm.get("handoffs", [])
        routes[str(name)] = _parse_handoff_names(handoffs)
    return routes


def load_delegation_gate(gate_path: Path) -> dict[str, list[str]]:
    """Parse data/delegation-gate.yml → {agent_slug: [target_slugs]}."""
    if not gate_path.exists():
        return {}
    with gate_path.open() as f:
        data = yaml.safe_load(f) or {}
    routes = data.get("delegation_routes", {})
    return {k: v or [] for k, v in routes.items()}


def merge_routes(file_routes: dict[str, list[str]], gate_routes: dict[str, list[str]]) -> dict[str, list[str]]:
    """Union of routes from both sources keyed by agent name."""
    merged: dict[str, list[str]] = defaultdict(set)  # type: ignore[assignment]
    for agent, targets in file_routes.items():
        merged[agent] |= set(targets)  # type: ignore[operator]
    for agent, targets in gate_routes.items():
        merged[agent] |= set(targets)  # type: ignore[operator]
    return {k: sorted(v) for k, v in merged.items()}  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Graph + metrics
# ---------------------------------------------------------------------------


def build_graph(routes: dict[str, list[str]]):  # type: ignore[return]
    """Build a directed NetworkX graph from the delegation route map."""
    import networkx as nx  # noqa: PLC0415

    G = nx.DiGraph()
    all_agents = set(routes.keys())
    for targets in routes.values():
        all_agents |= set(targets)
    G.add_nodes_from(all_agents)
    for agent, targets in routes.items():
        for target in targets:
            if target and target != agent:
                G.add_edge(agent, target)
    return G


def compute_k_metrics(graph, threshold: int) -> dict:
    """Compute NK K-coupling metrics from a directed delegation graph."""
    import networkx as nx  # noqa: PLC0415

    agents_list = sorted(graph.nodes())
    n = len(agents_list)

    agent_metrics = []
    for agent in agents_list:
        out_deg = graph.out_degree(agent)
        in_deg = graph.in_degree(agent)
        k = out_deg + in_deg
        agent_metrics.append(
            {
                "name": agent,
                "k": k,
                "in_degree": in_deg,
                "out_degree": out_deg,
                "bottleneck": k > threshold,
            }
        )

    k_values = [m["k"] for m in agent_metrics]
    mean_k = sum(k_values) / n if n else 0.0
    k_critical = 2.0  # Derrida critical point for Boolean NK networks; ≈2 for real networks

    # Regime classification (Kauffman NK model)
    if mean_k < k_critical:
        regime = "ordered"
    elif mean_k > k_critical * 2:
        regime = "chaotic"
    else:
        regime = "edge_of_chaos"

    high_k_nodes = [m["name"] for m in agent_metrics if m["bottleneck"]]

    # Modularity Q via Louvain community detection on undirected projection
    modularity_q: float | None = None
    communities: list[list[str]] | None = None
    try:
        undirected = graph.to_undirected()
        comms = list(nx.community.louvain_communities(undirected, seed=42))
        # Q formula: sum_c [ L_c/m - (d_c/2m)^2 ]
        modularity_q = round(nx.community.modularity(undirected, comms), 4)
        communities = [sorted(c) for c in comms]
    except Exception:
        pass

    return {
        "n_agents": n,
        "mean_k": round(mean_k, 3),
        "k_critical": k_critical,
        "modularity_q": modularity_q,
        "regime": regime,
        "agents": sorted(agent_metrics, key=lambda x: x["k"], reverse=True),
        "high_k_nodes": high_k_nodes,
        "communities": communities,
    }


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------


def format_table(report: dict) -> str:
    lines = [
        "═" * 70,
        f"  Agent Fleet NK Coupling Report   (N={report['n_agents']}, "
        f"mean_K={report['mean_k']:.2f}, regime={report['regime']})",
        "─" * 70,
    ]
    if report.get("modularity_q") is not None:
        lines.append(f"  Modularity Q = {report['modularity_q']:.4f}")
    lines.append("")

    header = f"  {'AGENT':<35} {'K':>4} {'IN':>4} {'OUT':>4}  FLAG"
    lines += [header, "  " + "-" * 60]

    for m in report["agents"]:
        flag = "⚠ HIGH-K BOTTLENECK" if m["bottleneck"] else ""
        lines.append(f"  {m['name']:<35} {m['k']:>4} {m['in_degree']:>4} {m['out_degree']:>4}  {flag}")

    lines.append("")
    if report["high_k_nodes"]:
        lines.append(f"  High-K nodes ({len(report['high_k_nodes'])}): {', '.join(report['high_k_nodes'])}")
    else:
        lines.append("  No high-K bottleneck nodes detected.")

    lines.append("═" * 70)
    return "\n".join(lines)


def format_summary(report: dict) -> str:
    flag = "⚠ BOTTLENECKS DETECTED" if report["high_k_nodes"] else "✅ fleet healthy"
    return (
        f"N={report['n_agents']} mean_K={report['mean_k']:.2f} "
        f"regime={report['regime']} Q={report.get('modularity_q')} "
        f"high_k={report['high_k_nodes']} — {flag}"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="analyse_fleet_coupling.py",
        description="NK K-coupling analysis for the agent fleet.",
    )
    parser.add_argument("--agents-dir", default=str(DEFAULT_AGENTS_DIR))
    parser.add_argument("--delegation-gate", default=str(DEFAULT_DELEGATION_GATE))
    parser.add_argument("--threshold", type=int, default=6, help="High-K warning threshold (default: 6)")
    parser.add_argument("--format", choices=["json", "table", "summary"], default="table")
    parser.add_argument("--output", help="Write JSON report to this file")

    args = parser.parse_args(argv)
    agents_dir = Path(args.agents_dir)
    gate_path = Path(args.delegation_gate)

    if not agents_dir.exists():
        print(f"ERROR: agents directory not found: {agents_dir}", file=sys.stderr)
        return 1

    file_routes = load_agents_from_files(agents_dir)
    gate_routes = load_delegation_gate(gate_path)
    merged = merge_routes(file_routes, gate_routes)

    graph = build_graph(merged)
    report = compute_k_metrics(graph, args.threshold)

    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2))
        print(f"Report written to {args.output}")

    if args.format == "json":
        print(json.dumps(report, indent=2))
    elif args.format == "summary":
        print(format_summary(report))
    else:
        print(format_table(report))

    return 0


if __name__ == "__main__":
    sys.exit(main())

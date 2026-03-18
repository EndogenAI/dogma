"""scripts/suggest_routing.py — GPS-style delegation routing from task description

Purpose:
    Accepts a free-text task description and produces an ordered delegation
    sequence for the agent fleet. The algorithm:

        1. Map task keywords → governance_boundary categories via
           ``data/task-type-classifier.yml`` (keyword matching)
        2. Load the delegation graph from ``data/delegation-gate.yml``
        3. Produce a topological sort of matched agents using the DAG structure
           (O(V+E) time — Kahn's algorithm)
        4. Annotate each step with the governing axiom from
           ``data/amplification-table.yml`` and FSM gate requirements from
           ``data/phase-gate-fsm.yml``
        5. Output as JSON (machine) or Markdown table (human) via --format flag

Design:
    - Topological sort (not Dijkstra) is correct for DAG delegation sequencing.
    - Keyword matching is case-insensitive substring match; first-match wins for
      category.  Multi-category tasks produce multiple steps in dependency order.

Source:
    ``docs/research/semantic-encoding-modes-contextual-routing.md``
    ``docs/research/intelligence-architecture-synthesis.md``
    GitHub issue #292

Inputs:
    TASK (positional)             — free-text task description
    --classifier PATH             — task-type-classifier.yml (default: data/)
    --delegation-gate PATH        — delegation-gate.yml (default: data/)
    --amplification-table PATH    — amplification-table.yml (default: data/)
    --fsm PATH                    — phase-gate-fsm.yml (default: data/)
    --format json|markdown|table  — output format (default: table)
    --all-steps                   — include non-matched steps in order (full routing)

Outputs:
    Ordered delegation sequence with:
        - Step number
        - Agent name
        - Category / task type
        - Governing axiom
        - FSM gate requirement (if any)

Exit codes:
    0 — success (matched ≥1 routing step)
    1 — argument error or no data files found
    2 — no matching routing steps found (task description not recognised)

Usage:
    uv run python scripts/suggest_routing.py "implement suggest_routing.py script"
    uv run python scripts/suggest_routing.py "research MCP server architecture" --format json
    uv run python scripts/suggest_routing.py "commit Sprint 17 changes" --format markdown
    uv run python scripts/suggest_routing.py "plan the next sprint phases" --all-steps
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data"

DEFAULT_CLASSIFIER = DATA_DIR / "task-type-classifier.yml"
DEFAULT_GATE = DATA_DIR / "delegation-gate.yml"
DEFAULT_AMPLIFICATION = DATA_DIR / "amplification-table.yml"
DEFAULT_FSM = DATA_DIR / "phase-gate-fsm.yml"

ROUTE_TO_AGENT = {
    "Orchestrator": "Executive Orchestrator",
    "Docs": "Executive Docs",
    "Researcher": "Executive Researcher",
    "Scripter": "Executive Scripter",
    "Automator": "Executive Automator",
    "PM": "Executive PM",
    "Fleet": "Executive Fleet",
    "Planner": "Executive Planner",
    "Review": "Review",
    "GitHub": "GitHub",
    "Issue Triage": "Issue Triage",
    "CI Monitor": "CI Monitor",
    "Test Coordinator": "Test Coordinator",
    "Security Researcher": "Security Researcher",
}


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------


def load_classifier(path: Path) -> list[dict]:
    with path.open() as f:
        return yaml.safe_load(f) or []


def load_delegation_gate(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    with path.open() as f:
        data = yaml.safe_load(f) or {}
    return {k: v or [] for k, v in data.get("delegation_routes", {}).items()}


def load_amplification_table(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as f:
        return yaml.safe_load(f) or []


def load_fsm(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open() as f:
        return yaml.safe_load(f) or {}


# ---------------------------------------------------------------------------
# Keyword matching
# ---------------------------------------------------------------------------


def match_categories(task_desc: str, classifier: list[dict]) -> list[dict]:
    """Return classifier entries whose keywords appear in task_desc (case-insensitive)."""
    task_lower = task_desc.lower()
    matched = []
    seen_categories: set[str] = set()
    for entry in classifier:
        if entry["category"] in seen_categories:
            continue
        for kw in entry.get("keywords", []):
            if re.search(r"\b" + re.escape(kw.lower()) + r"\b", task_lower):
                matched.append(entry)
                seen_categories.add(entry["category"])
                break
    return matched


def get_axiom_for_category(amplification_table: list[dict], category: str) -> str:
    """Look up the governing axiom for a task category keyword."""
    for row in amplification_table:
        for kw in row.get("keyword_list", []):
            if kw.lower() in category.lower():
                return row.get("amplify", "Algorithms-Before-Tokens")
    return "Algorithms-Before-Tokens"


# ---------------------------------------------------------------------------
# Topological sort
# ---------------------------------------------------------------------------

# Fixed agent ordering derived from delegation topology (Orchestrator → specialists → GitHub)
# This is the canonical topo order for the EndogenAI fleet DAG.
AGENT_TOPO_ORDER = [
    "Executive Planner",
    "Executive Researcher",
    "Research Scout",
    "Research Synthesizer",
    "Research Reviewer",
    "Research Archivist",
    "Executive Docs",
    "Executive Scripter",
    "Executive Automator",
    "Executive Fleet",
    "Executive PM",
    "Issue Triage",
    "CI Monitor",
    "Test Coordinator",
    "Security Researcher",
    "Review",
    "Executive Orchestrator",
    "GitHub",
]


def _fsm_transition_guard(fsm: dict, state: str, event: str) -> str | None:
    """Return guard text for a given state/event in data/phase-gate-fsm.yml."""
    states = fsm.get("fsm", {}).get("states", {})
    transitions = states.get(state, {}).get("transitions", [])
    for t in transitions:
        if t.get("event") == event:
            guard = (t.get("guard") or "").strip()
            return guard or None
    return None


def _build_agent_edges(delegation_gate: dict[str, list[str]]) -> list[tuple[str, str]]:
    """Build DAG edges in full agent names from data/delegation-gate.yml routes."""
    edges: list[tuple[str, str]] = []
    for src, targets in delegation_gate.items():
        src_agent = ROUTE_TO_AGENT.get(src, src)
        for dst in targets:
            dst_agent = ROUTE_TO_AGENT.get(dst, dst)
            edges.append((src_agent, dst_agent))
    return edges


def topo_sort_agents(matched_entries: list[dict], delegation_gate: dict[str, list[str]] | None = None) -> list[dict]:
    """Sort matched entries using delegation DAG edges; fall back to canonical order."""
    matched_agents = {e["agent"]: e for e in matched_entries}
    ordered_agents = [a for a in AGENT_TOPO_ORDER if a in matched_agents]

    if not delegation_gate:
        result = [matched_agents[a] for a in ordered_agents]
        in_result = {e["agent"] for e in result}
        for entry in matched_entries:
            if entry["agent"] not in in_result:
                result.append(entry)
        return result

    matched = set(matched_agents.keys())
    indegree = {a: 0 for a in matched}
    graph = {a: [] for a in matched}
    for src, dst in _build_agent_edges(delegation_gate):
        if src in matched and dst in matched:
            graph[src].append(dst)
            indegree[dst] += 1

    # Kahn with canonical order as deterministic tie-breaker.
    queue = [a for a in AGENT_TOPO_ORDER if a in matched and indegree[a] == 0]
    seen = set(queue)
    for a in sorted(matched):
        if indegree[a] == 0 and a not in seen:
            queue.append(a)
            seen.add(a)

    sorted_agents: list[str] = []
    while queue:
        current = queue.pop(0)
        sorted_agents.append(current)
        for nxt in graph.get(current, []):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    # Cycle safety: append remaining in canonical order.
    remaining = [a for a in AGENT_TOPO_ORDER if a in matched and a not in sorted_agents]
    for a in sorted(matched):
        if a not in sorted_agents and a not in remaining:
            remaining.append(a)
    sorted_agents.extend(remaining)

    return [matched_agents[a] for a in sorted_agents]


# ---------------------------------------------------------------------------
# FSM gate lookup
# ---------------------------------------------------------------------------


def get_fsm_gate(fsm: dict, step_index: int, total_steps: int) -> str:
    """Return the FSM gate requirement relevant to a step in the sequence."""
    init_guard = _fsm_transition_guard(fsm, "INIT", "plan_committed")
    review_guard = _fsm_transition_guard(fsm, "GATE_CHECK", "review_approved")
    close_guard = _fsm_transition_guard(fsm, "COMMIT", "all_phases_complete")

    init_gate = f"plan_committed ({init_guard})" if init_guard else "plan_committed"
    review_gate = f"review_approved ({review_guard})" if review_guard else "review_approved"
    close_gate = f"all_phases_complete ({close_guard})" if close_guard else "all_phases_complete"

    if step_index == 0:
        return init_gate
    if step_index < total_steps - 1:
        return review_gate
    return close_gate


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------


def format_table(steps: list[dict]) -> str:
    lines = [
        "═" * 90,
        "  Suggested Delegation Sequence",
        "─" * 90,
        f"  {'#':<4} {'AGENT':<30} {'CATEGORY':<16} {'AXIOM':<30} FSM GATE",
        "  " + "-" * 84,
    ]
    for s in steps:
        lines.append(
            f"  {s['step']:<4} {s['agent']:<30} {s['category']:<16} {s['axiom'][:28]:<30} {s['fsm_gate'][:32]}"
        )
    lines.append("═" * 90)
    return "\n".join(lines)


def format_markdown(steps: list[dict]) -> str:
    lines = [
        "## Suggested Delegation Sequence",
        "",
        "| # | Agent | Category | Governing Axiom | FSM Gate |",
        "|---|-------|----------|-----------------|----------|",
    ]
    for s in steps:
        lines.append(f"| {s['step']} | **{s['agent']}** | {s['category']} | {s['axiom']} | {s['fsm_gate']} |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_steps(
    task_desc: str,
    classifier: list[dict],
    amplification_table: list[dict],
    fsm: dict,
    include_all: bool = False,
) -> list[dict]:
    """Build the ordered routing steps for a task description."""
    if include_all:
        matched = classifier
    else:
        matched = match_categories(task_desc, classifier)

    if not matched:
        return []

    sorted_entries = topo_sort_agents(matched)
    total = len(sorted_entries)

    steps = []
    for i, entry in enumerate(sorted_entries):
        axiom = entry.get("axiom") or get_axiom_for_category(amplification_table, entry["category"])
        steps.append(
            {
                "step": i + 1,
                "agent": entry["agent"],
                "category": entry["category"],
                "description": entry.get("description", ""),
                "axiom": axiom,
                "fsm_gate": get_fsm_gate(fsm, i, total),
            }
        )
    return steps


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="suggest_routing.py",
        description="GPS-style delegation routing from task description.",
    )
    parser.add_argument("task", nargs="?", default="", help="Free-text task description")
    parser.add_argument("--classifier", default=str(DEFAULT_CLASSIFIER))
    parser.add_argument("--delegation-gate", default=str(DEFAULT_GATE))
    parser.add_argument("--amplification-table", default=str(DEFAULT_AMPLIFICATION))
    parser.add_argument("--fsm", default=str(DEFAULT_FSM))
    parser.add_argument("--format", choices=["table", "json", "markdown"], default="table")
    parser.add_argument("--all-steps", action="store_true", help="Include all categories in order")

    args = parser.parse_args(argv)

    if not args.task and not args.all_steps:
        parser.error("TASK description is required (or use --all-steps)")

    classifier_path = Path(args.classifier)
    if not classifier_path.exists():
        print(f"ERROR: classifier not found: {classifier_path}", file=sys.stderr)
        return 1

    classifier = load_classifier(classifier_path)
    amplification_table = load_amplification_table(Path(args.amplification_table))
    fsm = load_fsm(Path(args.fsm))
    delegation_gate = load_delegation_gate(Path(args.delegation_gate))

    steps = build_steps(args.task, classifier, amplification_table, fsm, args.all_steps)
    if steps:
        sortable = [
            {
                "agent": s["agent"],
                "category": s["category"],
                "axiom": s["axiom"],
                "description": s["description"],
            }
            for s in steps
        ]
        sorted_entries = topo_sort_agents(sortable, delegation_gate)
        total = len(sorted_entries)
        rebuilt = []
        for i, entry in enumerate(sorted_entries):
            rebuilt.append(
                {
                    "step": i + 1,
                    "agent": entry["agent"],
                    "category": entry["category"],
                    "description": entry.get("description", ""),
                    "axiom": entry["axiom"],
                    "fsm_gate": get_fsm_gate(fsm, i, total),
                }
            )
        steps = rebuilt

    if not steps:
        print(f"No routing steps matched for: '{args.task}'", file=sys.stderr)
        print("Tip: try --all-steps to see the full fleet routing order.", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(steps, indent=2))
    elif args.format == "markdown":
        print(format_markdown(steps))
    else:
        print(format_table(steps))

    return 0


if __name__ == "__main__":
    sys.exit(main())

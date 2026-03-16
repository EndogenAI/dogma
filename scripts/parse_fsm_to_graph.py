"""parse_fsm_to_graph.py — FSM-to-NetworkX path analysis + CI invariant check.

Purpose:
    Load the EndogenAI phase-gate FSM from data/phase-gate-fsm.yml into a
    NetworkX DiGraph, expose reachability queries, and run a CI invariant check
    that every terminal state is reachable from the initial state.

Inputs:
    data/phase-gate-fsm.yml  — YAML file with ``fsm.states`` and
                               ``fsm.initial_state`` keys.

Outputs:
    Exit 0  — all invariant checks pass (--validate) or reachable (--query).
    Exit 1  — invariant violated (--validate) or not reachable (--query).

Usage:
    # Validate: every terminal state is reachable from the initial state
    uv run python scripts/parse_fsm_to_graph.py --validate

    # Query: is CLOSED reachable from INIT?
    uv run python scripts/parse_fsm_to_graph.py --query INIT CLOSED

    # Query: is PHASE_RUNNING reachable from GATE_CHECK?
    uv run python scripts/parse_fsm_to_graph.py --query GATE_CHECK PHASE_RUNNING

Exit Codes:
    0 — success / reachable
    1 — invariant violation / not reachable
    2 — file not found or YAML parse error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import networkx as nx
import yaml

_DEFAULT_FSM_PATH = Path(__file__).parent.parent / "data" / "phase-gate-fsm.yml"


def load_graph(fsm_path: Path = _DEFAULT_FSM_PATH) -> tuple[nx.DiGraph, str]:
    """Load a phase-gate FSM YAML file and return (DiGraph, initial_state).

    Nodes are FSM state names (strings).
    Edges carry an ``event`` attribute from the transition definition.

    Raises:
        FileNotFoundError: if fsm_path does not exist.
        KeyError: if required YAML keys are missing.
        yaml.YAMLError: if the file is not valid YAML.
    """
    if not fsm_path.exists():
        raise FileNotFoundError(f"FSM file not found: {fsm_path}")

    with fsm_path.open() as fh:
        raw = yaml.safe_load(fh)

    fsm = raw["fsm"]
    initial_state: str = fsm["initial_state"]
    states: dict = fsm["states"]

    graph = nx.DiGraph()
    for state_name, state_def in states.items():
        graph.add_node(state_name)
        transitions = state_def.get("transitions") or []
        for transition in transitions:
            next_state = transition["next_state"]
            event = transition.get("event", "")
            graph.add_edge(state_name, next_state, event=event)

    return graph, initial_state


def reachable(graph: nx.DiGraph, from_state: str, to_state: str) -> bool:
    """Return True if *to_state* is reachable from *from_state* in *graph*."""
    if from_state not in graph:
        return False
    if to_state not in graph:
        return False
    return nx.has_path(graph, from_state, to_state)


def validate_fsm(graph: nx.DiGraph, initial_state: str) -> list[str]:
    """Check that every terminal state is reachable from *initial_state*.

    A terminal state is one with no outgoing edges.

    Returns:
        A list of unreachable terminal state names; empty list means all pass.
    """
    terminal_states = [n for n in graph.nodes if graph.out_degree(n) == 0]
    unreachable_terminals = [s for s in terminal_states if not reachable(graph, initial_state, s)]
    return unreachable_terminals


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FSM-to-NetworkX path analysis and CI invariant check.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--fsm",
        type=Path,
        default=_DEFAULT_FSM_PATH,
        metavar="PATH",
        help="Path to the FSM YAML file (default: data/phase-gate-fsm.yml)",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--validate",
        action="store_true",
        help=(
            "Check that every terminal state is reachable from the initial state. Exit 0 on pass, exit 1 on failure."
        ),
    )
    group.add_argument(
        "--query",
        nargs=2,
        metavar=("FROM", "TO"),
        help="Check if TO is reachable from FROM. Exit 0 if reachable, exit 1 if not.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:  # pragma: no cover
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        graph, initial_state = load_graph(args.fsm)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except (KeyError, yaml.YAMLError) as exc:
        print(f"ERROR: Failed to parse FSM YAML: {exc}", file=sys.stderr)
        return 2

    if args.validate:
        failures = validate_fsm(graph, initial_state)
        if failures:
            print(
                f"FAIL: {len(failures)} terminal state(s) unreachable from '{initial_state}':",
                file=sys.stderr,
            )
            for state in failures:
                print(f"  - {state}", file=sys.stderr)
            return 1
        print(
            f"PASS: all terminal states reachable from '{initial_state}' "
            f"({graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges)"
        )
        return 0

    # --query FROM TO
    from_state, to_state = args.query
    if reachable(graph, from_state, to_state):
        print(f"REACHABLE: '{from_state}' → '{to_state}'")
        return 0
    else:
        print(f"NOT REACHABLE: '{from_state}' → '{to_state}'")
        return 1


if __name__ == "__main__":
    sys.exit(main())

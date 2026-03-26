# `parse\_fsm\_to\_graph`

parse_fsm_to_graph.py — FSM-to-NetworkX path analysis + CI invariant check.

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

## Usage

```bash
    # Validate: every terminal state is reachable from the initial state
    uv run python scripts/parse_fsm_to_graph.py --validate

    # Query: is CLOSED reachable from INIT?
    uv run python scripts/parse_fsm_to_graph.py --query INIT CLOSED

    # Query: is PHASE_RUNNING reachable from GATE_CHECK?
    uv run python scripts/parse_fsm_to_graph.py --query GATE_CHECK PHASE_RUNNING
```

<!-- hash:a71c949aeda4569e -->

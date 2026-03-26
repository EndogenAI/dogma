# `suggest\_routing`

scripts/suggest_routing.py — GPS-style delegation routing from task description

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

## Usage

```bash
    uv run python scripts/suggest_routing.py "implement suggest_routing.py script"
    uv run python scripts/suggest_routing.py "research MCP server architecture" --format json
    uv run python scripts/suggest_routing.py "commit Sprint 17 changes" --format markdown
    uv run python scripts/suggest_routing.py "plan the next sprint phases" --all-steps
```

<!-- hash:161ea5af0f4ce806 -->

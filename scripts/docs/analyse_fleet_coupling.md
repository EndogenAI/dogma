# `analyse\_fleet\_coupling`

scripts/analyse_fleet_coupling.py — NK K-coupling analysis for the agent fleet

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

## Usage

```bash
    uv run python scripts/analyse_fleet_coupling.py
    uv run python scripts/analyse_fleet_coupling.py --format json
    uv run python scripts/analyse_fleet_coupling.py --threshold 5 --format summary
    uv run python scripts/analyse_fleet_coupling.py --output /tmp/coupling.json
```

<!-- hash:9cc9ee7b07aafc08 -->

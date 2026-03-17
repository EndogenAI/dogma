"""tests/test_analyse_fleet_coupling.py — Tests for scripts/analyse_fleet_coupling.py

Tests cover:
    - load_agents_from_files: parses handoffs from .agent.md frontmatter
    - load_delegation_gate: parses data/delegation-gate.yml
    - merge_routes: unions both sources
    - build_graph: produces a directed NetworkX graph
    - compute_k_metrics: K values, high-K detection, regime classification
    - format_table / format_summary: output formatting
    - main CLI: table, json, summary formats; --threshold; --output
"""

from __future__ import annotations

import json

import pytest

from scripts.analyse_fleet_coupling import (
    build_graph,
    compute_k_metrics,
    format_summary,
    format_table,
    load_agents_from_files,
    load_delegation_gate,
    main,
    merge_routes,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def agents_dir(tmp_path):
    """Create a minimal .github/agents/ directory with test .agent.md files."""
    d = tmp_path / "agents"
    d.mkdir()

    (d / "orchestrator.agent.md").write_text(
        "---\nname: Orchestrator\ndescription: Test orchestrator\n"
        "handoffs:\n  - agent: Docs\n  - agent: Scripter\n  - agent: Review\n---\n# Body\n",
        encoding="utf-8",
    )
    (d / "docs.agent.md").write_text(
        "---\nname: Docs\ndescription: Test docs\nhandoffs:\n  - agent: Orchestrator\n---\n# Body\n",
        encoding="utf-8",
    )
    (d / "scripter.agent.md").write_text(
        "---\nname: Scripter\ndescription: Test scripter\nhandoffs:\n  - agent: Orchestrator\n---\n# Body\n",
        encoding="utf-8",
    )
    (d / "review.agent.md").write_text(
        "---\nname: Review\ndescription: Test review\nhandoffs: []\n---\n# Body\n",
        encoding="utf-8",
    )
    return d


@pytest.fixture()
def gate_file(tmp_path):
    """Create a minimal delegation-gate.yml."""
    gate = tmp_path / "delegation-gate.yml"
    gate.write_text(
        "delegation_routes:\n  Orchestrator:\n    - Docs\n    - Scripter\n  Docs: []\n  Scripter: []\n  Review: []\n",
        encoding="utf-8",
    )
    return gate


# ---------------------------------------------------------------------------
# load_agents_from_files
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_load_agents_names(agents_dir):
    routes = load_agents_from_files(agents_dir)
    assert "Orchestrator" in routes
    assert "Docs" in routes
    assert "Review" in routes


@pytest.mark.io
def test_load_agents_handoffs(agents_dir):
    routes = load_agents_from_files(agents_dir)
    assert "Docs" in routes["Orchestrator"]
    assert "Scripter" in routes["Orchestrator"]


@pytest.mark.io
def test_load_agents_empty_handoffs(agents_dir):
    routes = load_agents_from_files(agents_dir)
    assert routes["Review"] == []


@pytest.mark.io
def test_load_agents_missing_dir(tmp_path):
    routes = load_agents_from_files(tmp_path / "nonexistent")
    assert routes == {}


# ---------------------------------------------------------------------------
# load_delegation_gate
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_load_gate_routes(gate_file):
    routes = load_delegation_gate(gate_file)
    assert "Orchestrator" in routes
    assert "Docs" in routes["Orchestrator"]


@pytest.mark.io
def test_load_gate_missing_file(tmp_path):
    routes = load_delegation_gate(tmp_path / "missing.yml")
    assert routes == {}


# ---------------------------------------------------------------------------
# merge_routes
# ---------------------------------------------------------------------------


def test_merge_routes_union():
    file_routes = {"A": ["B"], "B": []}
    gate_routes = {"A": ["C"], "C": []}
    merged = merge_routes(file_routes, gate_routes)
    assert set(merged["A"]) == {"B", "C"}
    assert "C" in merged


def test_merge_routes_no_duplicates():
    file_routes = {"A": ["B", "C"]}
    gate_routes = {"A": ["B", "D"]}
    merged = merge_routes(file_routes, gate_routes)
    assert merged["A"].count("B") == 1


# ---------------------------------------------------------------------------
# build_graph
# ---------------------------------------------------------------------------


def test_build_graph_nodes():
    routes = {"A": ["B", "C"], "B": ["A"], "C": []}
    G = build_graph(routes)
    assert "A" in G.nodes
    assert "B" in G.nodes
    assert "C" in G.nodes


def test_build_graph_edges():
    routes = {"A": ["B"], "B": []}
    G = build_graph(routes)
    assert G.has_edge("A", "B")
    assert not G.has_edge("B", "A")


def test_build_graph_no_self_loops():
    routes = {"A": ["A", "B"]}
    G = build_graph(routes)
    assert not G.has_edge("A", "A")


# ---------------------------------------------------------------------------
# compute_k_metrics
# ---------------------------------------------------------------------------


def test_compute_k_metrics_basic():
    routes = {"A": ["B", "C"], "B": ["A"], "C": []}
    G = build_graph(routes)
    report = compute_k_metrics(G, threshold=6)
    assert report["n_agents"] == 3
    assert report["mean_k"] > 0
    assert isinstance(report["agents"], list)
    assert isinstance(report["high_k_nodes"], list)


def test_compute_k_ordered_regime():
    """A star graph with low K should be in ordered regime."""
    routes = {"Hub": ["A", "B"], "A": [], "B": []}
    G = build_graph(routes)
    report = compute_k_metrics(G, threshold=6)
    # mean_K = (4+1+1)/3 = 2.0 → edge_of_chaos or ordered
    assert report["regime"] in {"ordered", "edge_of_chaos"}


def test_compute_k_high_k_detection():
    """An agent with K > threshold should be flagged."""
    routes = {
        "HubAgent": ["A", "B", "C", "D", "E", "F", "G"],
        "A": [],
        "B": [],
        "C": [],
        "D": [],
        "E": [],
        "F": [],
        "G": [],
    }
    G = build_graph(routes)
    report = compute_k_metrics(G, threshold=6)
    assert "HubAgent" in report["high_k_nodes"]


def test_compute_k_no_high_k():
    routes = {"A": ["B"], "B": []}
    G = build_graph(routes)
    report = compute_k_metrics(G, threshold=6)
    assert report["high_k_nodes"] == []


# ---------------------------------------------------------------------------
# output formatters
# ---------------------------------------------------------------------------


def test_format_table_contains_agent_name():
    routes = {"TestAgent": ["OtherAgent"], "OtherAgent": []}
    G = build_graph(routes)
    report = compute_k_metrics(G, threshold=6)
    output = format_table(report)
    assert "TestAgent" in output
    assert "Coupling Report" in output


def test_format_summary_healthy():
    routes = {"A": ["B"], "B": []}
    G = build_graph(routes)
    report = compute_k_metrics(G, threshold=6)
    summary = format_summary(report)
    assert "healthy" in summary.lower() or "bottleneck" in summary.lower()


# ---------------------------------------------------------------------------
# main CLI
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_main_table(agents_dir, gate_file, capsys):
    rc = main(["--agents-dir", str(agents_dir), "--delegation-gate", str(gate_file)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Coupling Report" in out


@pytest.mark.io
def test_main_json(agents_dir, gate_file, capsys):
    rc = main(["--agents-dir", str(agents_dir), "--delegation-gate", str(gate_file), "--format", "json"])
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "n_agents" in data
    assert "agents" in data


@pytest.mark.io
def test_main_summary(agents_dir, gate_file, capsys):
    rc = main(["--agents-dir", str(agents_dir), "--delegation-gate", str(gate_file), "--format", "summary"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "mean_K" in out


@pytest.mark.io
def test_main_threshold(agents_dir, gate_file, capsys):
    rc = main(["--agents-dir", str(agents_dir), "--delegation-gate", str(gate_file), "--threshold", "2"])
    assert rc == 0


@pytest.mark.io
def test_main_output_file(agents_dir, gate_file, tmp_path):
    out_file = tmp_path / "coupling.json"
    rc = main(
        [
            "--agents-dir",
            str(agents_dir),
            "--delegation-gate",
            str(gate_file),
            "--format",
            "json",
            "--output",
            str(out_file),
        ]
    )
    assert rc == 0
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert "n_agents" in data


@pytest.mark.io
def test_main_missing_agents_dir(tmp_path):
    rc = main(["--agents-dir", str(tmp_path / "nonexistent")])
    assert rc == 1

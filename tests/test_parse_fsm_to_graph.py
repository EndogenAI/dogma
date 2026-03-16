"""Tests for scripts/parse_fsm_to_graph.py."""

from __future__ import annotations

from pathlib import Path

import networkx as nx
import pytest
import yaml

from scripts.parse_fsm_to_graph import load_graph, reachable, validate_fsm

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def real_fsm_path() -> Path:
    """Return the path to the real phase-gate-fsm.yml."""
    return Path(__file__).parent.parent / "data" / "phase-gate-fsm.yml"


@pytest.fixture()
def simple_fsm_yaml(tmp_path: Path) -> Path:
    """Write a minimal valid FSM with one terminal state reachable from INIT."""
    content = {
        "fsm": {
            "name": "test-fsm",
            "initial_state": "INIT",
            "states": {
                "INIT": {
                    "description": "Start",
                    "transitions": [{"event": "start", "next_state": "DONE"}],
                },
                "DONE": {
                    "description": "Terminal",
                    "transitions": [],
                },
            },
        }
    }
    path = tmp_path / "fsm.yml"
    path.write_text(yaml.dump(content))
    return path


@pytest.fixture()
def unreachable_terminal_fsm_yaml(tmp_path: Path) -> Path:
    """FSM where ORPHAN is a terminal state unreachable from INIT."""
    content = {
        "fsm": {
            "name": "test-unreachable",
            "initial_state": "INIT",
            "states": {
                "INIT": {
                    "description": "Start",
                    "transitions": [{"event": "go", "next_state": "DONE"}],
                },
                "DONE": {
                    "description": "Reachable terminal",
                    "transitions": [],
                },
                "ORPHAN": {
                    "description": "Unreachable terminal — no incoming edges",
                    "transitions": [],
                },
            },
        }
    }
    path = tmp_path / "fsm_bad.yml"
    path.write_text(yaml.dump(content))
    return path


# ---------------------------------------------------------------------------
# Happy path — real FSM
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_load_real_fsm_builds_graph(real_fsm_path: Path) -> None:
    """load_graph() on the real YAML produces a DiGraph with expected nodes."""
    graph, initial_state = load_graph(real_fsm_path)
    assert isinstance(graph, nx.DiGraph)
    assert initial_state == "INIT"
    assert "INIT" in graph
    assert "CLOSED" in graph
    assert graph.number_of_nodes() >= 5


@pytest.mark.io
def test_real_fsm_closed_reachable_from_init(real_fsm_path: Path) -> None:
    """CLOSED is reachable from INIT in the real FSM."""
    graph, initial_state = load_graph(real_fsm_path)
    assert reachable(graph, initial_state, "CLOSED") is True


@pytest.mark.io
def test_real_fsm_validate_passes(real_fsm_path: Path) -> None:
    """validate_fsm() returns empty list for the real FSM (all terminals reachable)."""
    graph, initial_state = load_graph(real_fsm_path)
    failures = validate_fsm(graph, initial_state)
    assert failures == [], f"Unexpected unreachable terminals: {failures}"


# ---------------------------------------------------------------------------
# reachable() — unit tests (no file I/O)
# ---------------------------------------------------------------------------


def test_reachable_direct_edge() -> None:
    """reachable() returns True when a direct edge exists."""
    g = nx.DiGraph()
    g.add_edge("A", "B", event="e1")
    assert reachable(g, "A", "B") is True


def test_reachable_transitive() -> None:
    """reachable() returns True for a transitively reachable node."""
    g = nx.DiGraph()
    g.add_edge("A", "B", event="e1")
    g.add_edge("B", "C", event="e2")
    assert reachable(g, "A", "C") is True


def test_not_reachable_missing_path() -> None:
    """reachable() returns False when no path exists."""
    g = nx.DiGraph()
    g.add_node("A")
    g.add_node("B")
    assert reachable(g, "A", "B") is False


def test_not_reachable_unknown_node() -> None:
    """reachable() returns False when either node is absent."""
    g = nx.DiGraph()
    g.add_node("A")
    assert reachable(g, "A", "MISSING") is False
    assert reachable(g, "MISSING", "A") is False


def test_reachable_self() -> None:
    """reachable() returns True for same-node query (trivially reachable)."""
    g = nx.DiGraph()
    g.add_node("A")
    assert reachable(g, "A", "A") is True


# ---------------------------------------------------------------------------
# validate_fsm() — invariant violation
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_validate_detects_unreachable_terminal(unreachable_terminal_fsm_yaml: Path) -> None:
    """validate_fsm() returns the unreachable terminal state name."""
    graph, initial_state = load_graph(unreachable_terminal_fsm_yaml)
    failures = validate_fsm(graph, initial_state)
    assert "ORPHAN" in failures
    assert "DONE" not in failures


@pytest.mark.io
def test_validate_passes_simple_fsm(simple_fsm_yaml: Path) -> None:
    """validate_fsm() returns empty list when all terminal states are reachable."""
    graph, initial_state = load_graph(simple_fsm_yaml)
    failures = validate_fsm(graph, initial_state)
    assert failures == []


# ---------------------------------------------------------------------------
# load_graph() error cases
# ---------------------------------------------------------------------------


def test_load_graph_missing_file(tmp_path: Path) -> None:
    """load_graph() raises FileNotFoundError for a non-existent path."""
    with pytest.raises(FileNotFoundError):
        load_graph(tmp_path / "nonexistent.yml")


def test_load_graph_invalid_yaml(tmp_path: Path) -> None:
    """load_graph() raises yaml.YAMLError for malformed YAML."""
    bad = tmp_path / "bad.yml"
    bad.write_text(": invalid: yaml: [\n")
    with pytest.raises(yaml.YAMLError):
        load_graph(bad)


def test_load_graph_missing_fsm_key(tmp_path: Path) -> None:
    """load_graph() raises KeyError when 'fsm' top-level key is absent."""
    bad = tmp_path / "no_fsm.yml"
    bad.write_text(yaml.dump({"not_fsm": {}}))
    with pytest.raises(KeyError):
        load_graph(bad)


# ---------------------------------------------------------------------------
# Edge labels
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_edge_event_labels_present(simple_fsm_yaml: Path) -> None:
    """Edges carry an 'event' attribute matching the YAML transition event."""
    graph, _ = load_graph(simple_fsm_yaml)
    edge_data = graph.get_edge_data("INIT", "DONE")
    assert edge_data is not None
    assert edge_data["event"] == "start"

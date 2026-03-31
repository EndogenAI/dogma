"""tests/test_check_fleet_antipatterns.py — Unit tests for check_fleet_antipatterns.py"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import networkx as nx
import pytest

# Import the script module
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

import check_fleet_antipatterns as cfp  # noqa: E402

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_root(tmp_path: Path) -> Path:
    """Create a mock workspace root with agent files."""
    agents_dir = tmp_path / ".github" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def sample_coupling_data() -> dict:
    """Sample coupling report JSON."""
    return {
        "n_agents": 4,
        "mean_k": 2.0,
        "k_critical": 2.0,
        "modularity_q": 0.45,
        "regime": "ordered",
        "agents": [
            {"name": "Agent A", "k": 2, "in_degree": 1, "out_degree": 1, "bottleneck": False},
            {"name": "Agent B", "k": 2, "in_degree": 1, "out_degree": 1, "bottleneck": False},
            {"name": "Agent C", "k": 2, "in_degree": 1, "out_degree": 1, "bottleneck": False},
            {"name": "Agent D", "k": 0, "in_degree": 0, "out_degree": 0, "bottleneck": False},
        ],
        "high_k_nodes": [],
        "communities": [["Agent A", "Agent B", "Agent C"], ["Agent D"]],
    }


@pytest.fixture
def clean_graph() -> nx.DiGraph:
    """Create a clean delegation graph with no anti-patterns."""
    graph = nx.DiGraph()
    graph.add_edge("Agent A", "Agent B")
    graph.add_edge("Agent B", "Agent C")
    return graph


@pytest.fixture
def circular_graph() -> nx.DiGraph:
    """Create a delegation graph with circular delegation."""
    graph = nx.DiGraph()
    graph.add_edge("Agent A", "Agent B")
    graph.add_edge("Agent B", "Agent C")
    graph.add_edge("Agent C", "Agent A")  # Cycle: A → B → C → A
    return graph


@pytest.fixture
def orphaned_graph() -> nx.DiGraph:
    """Create a delegation graph with orphaned agents."""
    graph = nx.DiGraph()
    graph.add_node("Agent A")  # Connected
    graph.add_node("Agent B")  # Connected
    graph.add_node("Agent C")  # Orphaned (no edges)
    graph.add_edge("Agent A", "Agent B")
    return graph


@pytest.fixture
def disconnected_graph() -> nx.DiGraph:
    """Create a delegation graph with disconnected components."""
    graph = nx.DiGraph()
    # Component 1
    graph.add_edge("Agent A", "Agent B")
    # Component 2 (disconnected)
    graph.add_edge("Agent C", "Agent D")
    return graph


# ---------------------------------------------------------------------------
# Test load_coupling_data
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_load_coupling_data_from_file(tmp_path: Path, sample_coupling_data: dict):
    """Test loading coupling data from existing JSON file."""
    report_path = tmp_path / "coupling.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(sample_coupling_data, f)

    data = cfp.load_coupling_data(report_path, tmp_path)
    assert data == sample_coupling_data


@pytest.mark.io
def test_load_coupling_data_file_missing(tmp_path: Path):
    """Test loading coupling data when file doesn't exist."""
    report_path = tmp_path / "nonexistent.json"

    with patch("subprocess.run") as mock_run:
        # Simulate successful script run
        mock_run.return_value = MagicMock(returncode=0)
        with patch("builtins.open", side_effect=FileNotFoundError):
            data = cfp.load_coupling_data(report_path, tmp_path)
            assert data is None


@pytest.mark.io
def test_load_coupling_data_generate(tmp_path: Path, sample_coupling_data: dict):
    """Test generating coupling data when no report provided."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_file.__enter__.return_value.read.return_value = json.dumps(sample_coupling_data)
            mock_open.return_value = mock_file

            # Mock json.load to return sample data
            with patch("json.load", return_value=sample_coupling_data):
                data = cfp.load_coupling_data(None, tmp_path)
                assert data == sample_coupling_data


# ---------------------------------------------------------------------------
# Test detect_circular_delegation
# ---------------------------------------------------------------------------


def test_detect_circular_delegation_none(clean_graph: nx.DiGraph):
    """Test circular delegation detection with no cycles."""
    cycles = cfp.detect_circular_delegation(clean_graph)
    assert cycles == []


def test_detect_circular_delegation_found(circular_graph: nx.DiGraph):
    """Test circular delegation detection with cycles present."""
    cycles = cfp.detect_circular_delegation(circular_graph)
    assert len(cycles) == 1
    assert set(cycles[0]) == {"Agent A", "Agent B", "Agent C"}


def test_detect_circular_delegation_multiple():
    """Test circular delegation detection with multiple cycles."""
    graph = nx.DiGraph()
    # Cycle 1: A → B → A
    graph.add_edge("Agent A", "Agent B")
    graph.add_edge("Agent B", "Agent A")
    # Cycle 2: C → D → C
    graph.add_edge("Agent C", "Agent D")
    graph.add_edge("Agent D", "Agent C")

    cycles = cfp.detect_circular_delegation(graph)
    assert len(cycles) == 2


# ---------------------------------------------------------------------------
# Test detect_orphaned_agents
# ---------------------------------------------------------------------------


def test_detect_orphaned_agents_none(clean_graph: nx.DiGraph):
    """Test orphaned agent detection with no orphans."""
    orphaned = cfp.detect_orphaned_agents(clean_graph)
    assert orphaned == []


def test_detect_orphaned_agents_found(orphaned_graph: nx.DiGraph):
    """Test orphaned agent detection with orphans present."""
    orphaned = cfp.detect_orphaned_agents(orphaned_graph)
    assert "Agent C" in orphaned
    assert len(orphaned) == 1


def test_detect_orphaned_agents_partial_connection():
    """Test that agents with only in-degree or only out-degree are not orphaned."""
    graph = nx.DiGraph()
    graph.add_node("Agent A")  # Orphaned
    graph.add_node("Agent B")  # Has out-degree only
    graph.add_node("Agent C")  # Has in-degree only
    graph.add_edge("Agent B", "Agent C")

    orphaned = cfp.detect_orphaned_agents(graph)
    assert orphaned == ["Agent A"]


# ---------------------------------------------------------------------------
# Test detect_posture_bloat
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_detect_posture_bloat_none(mock_root: Path):
    """Test posture bloat detection with no violations."""
    agents_dir = mock_root / ".github" / "agents"
    agent_file = agents_dir / "test.agent.md"
    agent_file.write_text(
        "---\nname: Test Agent\ntools: [read, search, edit]\n---\n\nContent",
        encoding="utf-8",
    )

    bloated = cfp.detect_posture_bloat(mock_root)
    assert bloated == []


@pytest.mark.io
def test_detect_posture_bloat_found(mock_root: Path):
    """Test posture bloat detection with >9 tools."""
    agents_dir = mock_root / ".github" / "agents"
    agent_file = agents_dir / "bloated.agent.md"
    tools = ["tool" + str(i) for i in range(12)]
    agent_file.write_text(
        f"---\nname: Bloated Agent\ntools: {tools}\n---\n\nContent",
        encoding="utf-8",
    )

    bloated = cfp.detect_posture_bloat(mock_root)
    assert len(bloated) == 1
    assert bloated[0][0] == "Bloated Agent"
    assert bloated[0][1] == 12


@pytest.mark.io
def test_detect_posture_bloat_exactly_nine(mock_root: Path):
    """Test that exactly 9 tools is not bloat."""
    agents_dir = mock_root / ".github" / "agents"
    agent_file = agents_dir / "test.agent.md"
    tools = ["tool" + str(i) for i in range(9)]
    agent_file.write_text(
        f"---\nname: Test Agent\ntools: {tools}\n---\n\nContent",
        encoding="utf-8",
    )

    bloated = cfp.detect_posture_bloat(mock_root)
    assert bloated == []


@pytest.mark.io
def test_detect_posture_bloat_missing_dir(mock_root: Path):
    """Test posture bloat detection when agents dir doesn't exist."""
    # Don't create agents_dir
    (mock_root / ".github" / "agents").rmdir()
    (mock_root / ".github").rmdir()

    bloated = cfp.detect_posture_bloat(mock_root)
    assert bloated == []


# ---------------------------------------------------------------------------
# Test detect_disconnected_components
# ---------------------------------------------------------------------------


def test_detect_disconnected_components_none(clean_graph: nx.DiGraph):
    """Test disconnected components detection with fully connected graph."""
    components = cfp.detect_disconnected_components(clean_graph)
    assert components == []


def test_detect_disconnected_components_found(disconnected_graph: nx.DiGraph):
    """Test disconnected components detection with isolated clusters."""
    components = cfp.detect_disconnected_components(disconnected_graph)
    assert len(components) == 2
    assert {"Agent A", "Agent B"} in [set(comp) for comp in components]
    assert {"Agent C", "Agent D"} in [set(comp) for comp in components]


def test_detect_disconnected_components_single_node():
    """Test disconnected components with single isolated nodes."""
    graph = nx.DiGraph()
    graph.add_node("Agent A")
    graph.add_node("Agent B")
    graph.add_node("Agent C")
    graph.add_edge("Agent A", "Agent B")

    components = cfp.detect_disconnected_components(graph)
    assert len(components) == 2


# ---------------------------------------------------------------------------
# Test build_delegation_graph
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_build_delegation_graph(mock_root: Path, sample_coupling_data: dict):
    """Test building delegation graph from coupling data and agent files."""
    agents_dir = mock_root / ".github" / "agents"

    # Create agent files with handoffs
    (agents_dir / "agent-a.agent.md").write_text(
        "---\nname: Agent A\nhandoffs:\n  - agent: Agent B\n---\nContent",
        encoding="utf-8",
    )
    (agents_dir / "agent-b.agent.md").write_text(
        "---\nname: Agent B\nhandoffs:\n  - agent: Agent C\n---\nContent",
        encoding="utf-8",
    )

    graph = cfp.build_delegation_graph(sample_coupling_data, mock_root)

    assert "Agent A" in graph.nodes()
    assert "Agent B" in graph.nodes()
    assert graph.has_edge("Agent A", "Agent B")
    assert graph.has_edge("Agent B", "Agent C")


@pytest.mark.io
def test_build_delegation_graph_no_agents_dir(mock_root: Path, sample_coupling_data: dict):
    """Test building delegation graph when agents dir doesn't exist."""
    (mock_root / ".github" / "agents").rmdir()
    (mock_root / ".github").rmdir()

    graph = cfp.build_delegation_graph(sample_coupling_data, mock_root)

    # Should still add nodes from coupling data
    assert "Agent A" in graph.nodes()
    assert "Agent B" in graph.nodes()


# ---------------------------------------------------------------------------
# Test main function
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_main_no_antipatterns(mock_root: Path, capsys):
    """Test main function with no anti-patterns."""
    agents_dir = mock_root / ".github" / "agents"
    (agents_dir / "agent-a.agent.md").write_text(
        "---\nname: Agent A\ntools: [read, search]\nhandoffs:\n  - agent: Agent B\n---\n",
        encoding="utf-8",
    )
    (agents_dir / "agent-b.agent.md").write_text(
        "---\nname: Agent B\ntools: [read]\nhandoffs: []\n---\n",
        encoding="utf-8",
    )

    # Custom coupling data with only agents that have corresponding files
    coupling_data = {
        "n_agents": 2,
        "mean_k": 1.0,
        "k_critical": 1.5,
        "modularity_q": 0.5,
        "regime": "ordered",
        "agents": [
            {"name": "Agent A", "k": 1, "in_degree": 0, "out_degree": 1, "bottleneck": False},
            {"name": "Agent B", "k": 1, "in_degree": 1, "out_degree": 0, "bottleneck": False},
        ],
        "high_k_nodes": [],
        "communities": [["Agent A", "Agent B"]],
    }

    coupling_path = mock_root / "coupling.json"
    with coupling_path.open("w", encoding="utf-8") as f:
        json.dump(coupling_data, f)

    with patch.object(cfp, "_get_root", return_value=mock_root):
        with patch("sys.argv", ["check_fleet_antipatterns.py", "--coupling-report", str(coupling_path)]):
            exit_code = cfp.main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "No fleet anti-patterns detected" in captured.out


@pytest.mark.io
def test_main_circular_delegation(mock_root: Path, sample_coupling_data: dict, capsys):
    """Test main function detecting circular delegation."""
    agents_dir = mock_root / ".github" / "agents"
    # Create circular delegation: A → B → C → A
    (agents_dir / "agent-a.agent.md").write_text(
        "---\nname: Agent A\ntools: [read]\nhandoffs:\n  - agent: Agent B\n---\n",
        encoding="utf-8",
    )
    (agents_dir / "agent-b.agent.md").write_text(
        "---\nname: Agent B\ntools: [read]\nhandoffs:\n  - agent: Agent C\n---\n",
        encoding="utf-8",
    )
    (agents_dir / "agent-c.agent.md").write_text(
        "---\nname: Agent C\ntools: [read]\nhandoffs:\n  - agent: Agent A\n---\n",
        encoding="utf-8",
    )

    coupling_path = mock_root / "coupling.json"
    with coupling_path.open("w", encoding="utf-8") as f:
        json.dump(sample_coupling_data, f)

    with patch.object(cfp, "_get_root", return_value=mock_root):
        with patch("sys.argv", ["check_fleet_antipatterns.py", "--coupling-report", str(coupling_path)]):
            exit_code = cfp.main()

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "CIRCULAR DELEGATION DETECTED" in captured.out


@pytest.mark.io
def test_main_posture_bloat(mock_root: Path, sample_coupling_data: dict, capsys):
    """Test main function detecting posture bloat."""
    agents_dir = mock_root / ".github" / "agents"
    tools = ["tool" + str(i) for i in range(15)]
    (agents_dir / "bloated.agent.md").write_text(
        f"---\nname: Bloated Agent\ntools: {tools}\nhandoffs: []\n---\n",
        encoding="utf-8",
    )

    coupling_path = mock_root / "coupling.json"
    with coupling_path.open("w", encoding="utf-8") as f:
        json.dump(sample_coupling_data, f)

    with patch.object(cfp, "_get_root", return_value=mock_root):
        with patch("sys.argv", ["check_fleet_antipatterns.py", "--coupling-report", str(coupling_path)]):
            exit_code = cfp.main()

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "POSTURE BLOAT DETECTED" in captured.out
    assert "15 tools" in captured.out


@pytest.mark.io
def test_main_dry_run(mock_root: Path, sample_coupling_data: dict, capsys):
    """Test main function in dry-run mode."""
    agents_dir = mock_root / ".github" / "agents"
    tools = ["tool" + str(i) for i in range(12)]
    (agents_dir / "bloated.agent.md").write_text(
        f"---\nname: Bloated Agent\ntools: {tools}\nhandoffs: []\n---\n",
        encoding="utf-8",
    )

    coupling_path = mock_root / "coupling.json"
    with coupling_path.open("w", encoding="utf-8") as f:
        json.dump(sample_coupling_data, f)

    with patch.object(cfp, "_get_root", return_value=mock_root):
        with patch("sys.argv", ["check_fleet_antipatterns.py", "--coupling-report", str(coupling_path), "--dry-run"]):
            exit_code = cfp.main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "[DRY RUN]" in captured.out
    assert "POSTURE BLOAT DETECTED" in captured.out


@pytest.mark.io
def test_main_missing_coupling_data(mock_root: Path, capsys):
    """Test main function when coupling data cannot be loaded."""
    with patch.object(cfp, "_get_root", return_value=mock_root):
        with patch.object(cfp, "load_coupling_data", return_value=None):
            with patch("sys.argv", ["check_fleet_antipatterns.py"]):
                exit_code = cfp.main()

    assert exit_code == 2

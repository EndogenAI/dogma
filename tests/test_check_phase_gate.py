"""Tests for scripts/check_phase_gate.py."""

import subprocess
import sys
from pathlib import Path

import pytest

# Import business logic functions directly
from scripts.check_phase_gate import get_states, load_fsm

SCRIPT = Path(__file__).parent.parent / "scripts" / "check_phase_gate.py"
FSM_FILE = Path(__file__).parent.parent / "data" / "phase-gate-fsm.yml"


class TestMain:
    """Unit tests for main() CLI function."""

    def test_main_list_states(self, monkeypatch, capsys):
        """Test main() with --list-states."""
        monkeypatch.setattr("sys.argv", ["check_phase_gate.py", "--list-states", "--fsm-file", str(FSM_FILE)])

        from scripts.check_phase_gate import main

        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0

        captured = capsys.readouterr()
        assert "INIT" in captured.out

    def test_main_no_state_prints_help(self, monkeypatch):
        """Test main() without --state or --list-states exits 1."""
        monkeypatch.setattr("sys.argv", ["check_phase_gate.py", "--fsm-file", str(FSM_FILE)])

        from scripts.check_phase_gate import main

        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1

    def test_main_unknown_state_exits_1(self, monkeypatch):
        """Test main() with unknown state exits 1."""
        monkeypatch.setattr("sys.argv", ["check_phase_gate.py", "--state", "UNKNOWN", "--fsm-file", str(FSM_FILE)])

        from scripts.check_phase_gate import main

        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1

    def test_main_valid_transition_exits_0(self, monkeypatch):
        """Test main() with valid transition exits 0."""
        monkeypatch.setattr(
            "sys.argv",
            [
                "check_phase_gate.py",
                "--state",
                "PHASE_RUNNING",
                "--event",
                "phase_deliverable_returned",
                "--fsm-file",
                str(FSM_FILE),
            ],
        )

        from scripts.check_phase_gate import main

        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0


class TestLoadFsm:
    """Unit tests for load_fsm() function."""

    def test_load_valid_fsm(self):
        """load_fsm() returns dict from valid YAML file."""
        fsm_data = load_fsm(str(FSM_FILE))
        assert isinstance(fsm_data, dict)
        assert "fsm" in fsm_data

    def test_load_nonexistent_file_exits(self, tmp_path):
        """load_fsm() exits with code 2 for nonexistent file."""
        nonexistent = tmp_path / "nonexistent.yml"

        with pytest.raises(SystemExit) as excinfo:
            load_fsm(str(nonexistent))
        assert excinfo.value.code == 2

    def test_load_invalid_yaml_exits(self, tmp_path):
        """load_fsm() exits with code 2 for malformed YAML."""
        invalid_yaml = tmp_path / "invalid.yml"
        invalid_yaml.write_text("{ invalid yaml content")

        with pytest.raises(SystemExit) as excinfo:
            load_fsm(str(invalid_yaml))
        assert excinfo.value.code == 2

    def test_load_non_dict_yaml_exits(self, tmp_path):
        """load_fsm() exits with code 2 if YAML is not a dict."""
        non_dict_yaml = tmp_path / "list.yml"
        non_dict_yaml.write_text("- item1\n- item2")

        with pytest.raises(SystemExit) as excinfo:
            load_fsm(str(non_dict_yaml))
        assert excinfo.value.code == 2


class TestGetStates:
    """Unit tests for get_states() function."""

    def test_get_states_from_valid_fsm(self):
        """get_states() extracts states dict from FSM data."""
        fsm_data = load_fsm(str(FSM_FILE))
        states = get_states(fsm_data)

        assert isinstance(states, dict)
        assert "INIT" in states
        assert "PHASE_RUNNING" in states
        assert "GATE_CHECK" in states

    def test_get_states_empty_if_missing(self):
        """get_states() returns empty dict if states key missing."""
        fsm_data = {"fsm": {}}
        states = get_states(fsm_data)
        assert states == {}


class TestTransitionValidation:
    """Unit tests for transition validation logic."""

    def test_valid_transition_exists(self):
        """Known valid state+event combination is found."""
        fsm_data = load_fsm(str(FSM_FILE))
        states = get_states(fsm_data)

        # PHASE_RUNNING should have phase_deliverable_returned event
        phase_running = states.get("PHASE_RUNNING")
        assert phase_running is not None

        transitions = phase_running.get("transitions", [])
        event_names = [t.get("event") for t in transitions]
        assert "phase_deliverable_returned" in event_names

    def test_transition_has_next_state(self):
        """Transition includes next_state field."""
        fsm_data = load_fsm(str(FSM_FILE))
        states = get_states(fsm_data)

        phase_running = states["PHASE_RUNNING"]
        transitions = phase_running.get("transitions", [])

        # Find phase_deliverable_returned transition
        transition = next((t for t in transitions if t.get("event") == "phase_deliverable_returned"), None)

        assert transition is not None
        assert "next_state" in transition
        assert transition["next_state"] == "GATE_CHECK"

    def test_all_states_have_valid_structure(self):
        """All states in FSM have valid structure."""
        fsm_data = load_fsm(str(FSM_FILE))
        states = get_states(fsm_data)

        for state_name, state_def in states.items():
            # Each state should be a dict
            assert isinstance(state_def, dict), f"State {state_name} is not a dict"

            # Transitions field should be a list (or missing for terminal states)
            if "transitions" in state_def:
                assert isinstance(state_def["transitions"], list)

    def test_init_state_exists(self):
        """INIT state exists and has plan_committed event."""
        fsm_data = load_fsm(str(FSM_FILE))
        states = get_states(fsm_data)

        assert "INIT" in states
        init_state = states["INIT"]
        transitions = init_state.get("transitions", [])
        event_names = [t.get("event") for t in transitions]
        assert "plan_committed" in event_names


@pytest.mark.integration
class TestCheckPhaseGateIntegration:
    """Integration tests using subprocess (smoke tests)."""

    def test_cli_list_states_exits_0(self):
        """--list-states returns exit code 0 and outputs known state names."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--list-states", "--fsm-file", str(FSM_FILE)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        output = result.stdout
        assert "INIT" in output
        assert "PHASE_RUNNING" in output
        assert "GATE_CHECK" in output

    def test_cli_valid_transition(self):
        """Known valid state+event combination returns exit code 0."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--state",
                "PHASE_RUNNING",
                "--event",
                "phase_deliverable_returned",
                "--fsm-file",
                str(FSM_FILE),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "VALID" in result.stdout

    def test_cli_invalid_event_exits_1(self):
        """Nonexistent event for a known state returns exit code 1."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--state",
                "PHASE_RUNNING",
                "--event",
                "nonexistent_event_xyz",
                "--fsm-file",
                str(FSM_FILE),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "INVALID" in result.stdout

"""Tests for scripts/check_phase_gate.py."""

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "check_phase_gate.py"
FSM_FILE = Path(__file__).parent.parent / "data" / "phase-gate-fsm.yml"


def run_script(*args: str) -> subprocess.CompletedProcess:
    """Run check_phase_gate.py with the given args and return the result."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


@pytest.mark.io
def test_list_states_exits_0():
    """--list-states returns exit code 0 and outputs known state names."""
    result = run_script("--list-states", "--fsm-file", str(FSM_FILE))
    assert result.returncode == 0
    output = result.stdout
    assert "INIT" in output
    assert "PHASE_RUNNING" in output
    assert "GATE_CHECK" in output
    assert "COMPACT_CHECK" in output
    assert "COMMIT" in output
    assert "CLOSED" in output


@pytest.mark.io
def test_valid_transition():
    """Known valid state+event combination returns exit code 0."""
    result = run_script(
        "--state",
        "PHASE_RUNNING",
        "--event",
        "phase_deliverable_returned",
        "--fsm-file",
        str(FSM_FILE),
    )
    assert result.returncode == 0
    assert "VALID" in result.stdout
    assert "PHASE_RUNNING" in result.stdout
    assert "phase_deliverable_returned" in result.stdout
    assert "GATE_CHECK" in result.stdout


@pytest.mark.io
def test_invalid_event_exits_1():
    """Nonexistent event for a known state returns exit code 1."""
    result = run_script(
        "--state",
        "PHASE_RUNNING",
        "--event",
        "nonexistent_event_xyz",
        "--fsm-file",
        str(FSM_FILE),
    )
    assert result.returncode == 1
    assert "INVALID" in result.stdout


@pytest.mark.io
def test_unknown_state_exits_1():
    """Unknown state name returns exit code 1."""
    result = run_script(
        "--state",
        "UNKNOWN_STATE_XYZ",
        "--fsm-file",
        str(FSM_FILE),
    )
    assert result.returncode == 1
    assert "INVALID" in result.stderr


def test_missing_fsm_file_exits_2():
    """Nonexistent --fsm-file path returns exit code 2."""
    result = run_script(
        "--list-states",
        "--fsm-file",
        "/nonexistent/path/to/fsm.yml",
    )
    assert result.returncode == 2
    assert "not found" in result.stderr


@pytest.mark.io
def test_list_events_for_state():
    """--state INIT with no --event lists events and exits 0."""
    result = run_script(
        "--state",
        "INIT",
        "--fsm-file",
        str(FSM_FILE),
    )
    assert result.returncode == 0
    assert "plan_committed" in result.stdout
    assert "INIT" in result.stdout

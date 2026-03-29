"""Tests for scripts/start_dashboard.py.

Covers launcher exit-code semantics and startup-failure cleanup behavior.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture(scope="module")
def sd_mod():
    """Load scripts/start_dashboard.py via importlib for in-process testing."""
    spec = importlib.util.spec_from_file_location(
        "start_dashboard",
        Path(__file__).parent.parent / "scripts" / "start_dashboard.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _DummyProc:
    def __init__(self, poll_value=None):
        self._poll_value = poll_value
        self.terminated = False
        self.killed = False

    def poll(self):
        return self._poll_value

    def terminate(self):
        self.terminated = True

    def wait(self, timeout=None):
        return None

    def kill(self):
        self.killed = True


@pytest.mark.integration
def test_spawn_processes_terminates_sidecar_if_frontend_spawn_fails(sd_mod):
    sidecar = _DummyProc()

    with patch("subprocess.Popen", side_effect=[sidecar, OSError("npm missing")]):
        with patch.object(sd_mod, "_terminate") as mock_terminate:
            with pytest.raises(OSError):
                sd_mod._spawn_processes(Path("."))
            mock_terminate.assert_called_once_with(sidecar)


@pytest.mark.integration
def test_main_returns_nonzero_when_child_process_fails(sd_mod, monkeypatch):
    sidecar = _DummyProc(poll_value=1)
    frontend = _DummyProc(poll_value=None)

    monkeypatch.setattr(sd_mod.Path, "exists", lambda _self: True)
    monkeypatch.setattr(sd_mod, "_spawn_processes", lambda _repo_root: (sidecar, frontend))

    rc = sd_mod.main()

    assert rc == 1


@pytest.mark.integration
def test_main_returns_zero_on_keyboard_interrupt(sd_mod, monkeypatch):
    sidecar = _DummyProc(poll_value=None)
    frontend = _DummyProc(poll_value=None)

    monkeypatch.setattr(sd_mod.Path, "exists", lambda _self: True)
    monkeypatch.setattr(sd_mod, "_spawn_processes", lambda _repo_root: (sidecar, frontend))

    def _raise_keyboard_interrupt(_seconds):
        raise KeyboardInterrupt()

    monkeypatch.setattr(sd_mod.time, "sleep", _raise_keyboard_interrupt)

    rc = sd_mod.main()

    assert rc == 0

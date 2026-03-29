"""Tests for scripts/start_dashboard.py.

Covers launcher exit-code semantics, startup-failure cleanup behavior,
and --development flag passthrough to uvicorn.
"""

from __future__ import annotations

import importlib.util
import sys
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
    monkeypatch.setattr(sd_mod, "_spawn_processes", lambda _repo_root, **_kw: (sidecar, frontend))
    monkeypatch.setattr(sys, "argv", ["start_dashboard.py"])

    rc = sd_mod.main()

    assert rc == 1


@pytest.mark.integration
def test_main_returns_zero_on_keyboard_interrupt(sd_mod, monkeypatch):
    sidecar = _DummyProc(poll_value=None)
    frontend = _DummyProc(poll_value=None)

    monkeypatch.setattr(sd_mod.Path, "exists", lambda _self: True)
    monkeypatch.setattr(sd_mod, "_spawn_processes", lambda _repo_root, **_kw: (sidecar, frontend))
    monkeypatch.setattr(sys, "argv", ["start_dashboard.py"])

    def _raise_keyboard_interrupt(_seconds):
        raise KeyboardInterrupt()

    monkeypatch.setattr(sd_mod.time, "sleep", _raise_keyboard_interrupt)

    rc = sd_mod.main()

    assert rc == 0


@pytest.mark.integration
def test_spawn_processes_includes_reload_flag_in_dev_mode(sd_mod):
    """--development flag must add --reload to the uvicorn command."""
    sidecar = _DummyProc()
    frontend = _DummyProc()

    captured_cmds = []

    def _popen(cmd, **kwargs):
        captured_cmds.append(list(cmd))
        return sidecar if "uvicorn" in cmd else frontend

    with patch("subprocess.Popen", side_effect=_popen):
        sd_mod._spawn_processes(Path("."), development=True)

    assert any("uvicorn" in c for c in captured_cmds[0]), "sidecar cmd missing"
    assert "--reload" in captured_cmds[0], "--reload not added in dev mode"


@pytest.mark.integration
def test_spawn_processes_excludes_reload_flag_in_prod_mode(sd_mod):
    """Without --development, uvicorn must NOT receive --reload."""
    sidecar = _DummyProc()
    frontend = _DummyProc()

    captured_cmds = []

    def _popen(cmd, **kwargs):
        captured_cmds.append(list(cmd))
        return sidecar if "uvicorn" in cmd else frontend

    with patch("subprocess.Popen", side_effect=_popen):
        sd_mod._spawn_processes(Path("."), development=False)

    assert "--reload" not in captured_cmds[0], "--reload present without dev flag"


@pytest.mark.integration
def test_main_dev_flag_propagates_to_spawn(sd_mod, monkeypatch):
    """-d / --development flag in argv is forwarded to _spawn_processes."""
    sidecar = _DummyProc(poll_value=None)
    frontend = _DummyProc(poll_value=None)

    seen_kwargs = {}

    def _fake_spawn(repo_root, *, development=False):
        seen_kwargs["development"] = development
        return sidecar, frontend

    monkeypatch.setattr(sd_mod.Path, "exists", lambda _self: True)
    monkeypatch.setattr(sd_mod, "_spawn_processes", _fake_spawn)
    monkeypatch.setattr(sys, "argv", ["start_dashboard.py", "--development"])

    def _interrupt(_seconds):
        raise KeyboardInterrupt()

    monkeypatch.setattr(sd_mod.time, "sleep", _interrupt)

    sd_mod.main()

    assert seen_kwargs.get("development") is True, "development flag not forwarded"

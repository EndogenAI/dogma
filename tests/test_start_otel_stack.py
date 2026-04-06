"""Tests for scripts/start_otel_stack.py — OTel Collector + Jaeger stack launcher."""

from __future__ import annotations

import urllib.error
from unittest.mock import MagicMock, patch

import pytest


def _load() -> object:
    import importlib.util

    spec = importlib.util.spec_from_file_location("start_otel_stack", "scripts/start_otel_stack.py")
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def test_stop_flag_runs_docker_compose_down() -> None:
    mod = _load()
    with patch("subprocess.run") as mock_run:
        with pytest.raises(SystemExit) as exc_info:
            mod.main(["--stop"])
        assert exc_info.value.code == 0
        mock_run.assert_called_once_with(["docker", "compose", "down"], check=True)


def test_ready_when_jaeger_responds() -> None:
    mod = _load()

    mock_response = MagicMock()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)

    with (
        patch("subprocess.run"),
        patch("urllib.request.urlopen", return_value=mock_response),
    ):
        with pytest.raises(SystemExit) as exc_info:
            mod.main([])
        assert exc_info.value.code == 0


def test_timeout_when_jaeger_never_responds() -> None:
    mod = _load()

    # Copilot comment #3035069968: patch _wait_for_jaeger directly to avoid default-arg binding issue
    with (
        patch("subprocess.run"),
        patch.object(mod, "_wait_for_jaeger", return_value=False) as mock_wait,
    ):
        with pytest.raises(SystemExit) as exc_info:
            mod.main([])
        assert exc_info.value.code == 1
        # Verify _wait_for_jaeger was actually called
        mock_wait.assert_called_once()


def test_wait_for_jaeger_retries_on_connection_error() -> None:
    """Coverage: _wait_for_jaeger retry loop."""
    mod = _load()

    with (
        patch("urllib.request.urlopen", side_effect=urllib.error.URLError("refused")),
        patch("time.sleep") as mock_sleep,
    ):
        result = mod._wait_for_jaeger(max_retries=3, sleep=0.1)

    assert result is False
    assert mock_sleep.call_count == 3


def test_wait_for_jaeger_succeeds_on_first_try() -> None:
    """Coverage: _wait_for_jaeger success path."""
    mod = _load()

    mock_response = MagicMock()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_response):
        result = mod._wait_for_jaeger(max_retries=1, sleep=0.0)

    assert result is True


def test_run_compose_exits_with_code_2_when_docker_not_found() -> None:
    """Coverage: _run_compose FileNotFoundError handling."""
    mod = _load()

    with (
        patch("subprocess.run", side_effect=FileNotFoundError("docker not found")),
        pytest.raises(SystemExit) as exc_info,
    ):
        mod._run_compose(["up", "-d"])

    assert exc_info.value.code == 2


def test_help_flag_returns_zero() -> None:
    """Coverage: argparse help path."""
    mod = _load()

    with pytest.raises(SystemExit) as exc_info:
        mod.main(["--help"])

    assert exc_info.value.code == 0

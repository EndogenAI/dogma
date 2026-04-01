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

    with (
        patch("subprocess.run"),
        patch("urllib.request.urlopen", side_effect=urllib.error.URLError("refused")),
        patch.object(mod, "MAX_RETRIES", 2),
        patch("time.sleep"),
    ):
        with pytest.raises(SystemExit) as exc_info:
            mod.main([])
        assert exc_info.value.code == 1

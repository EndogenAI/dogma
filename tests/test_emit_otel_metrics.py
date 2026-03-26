import argparse
from unittest.mock import patch

from scripts.emit_otel_metrics import emit_metrics


def test_emit_metrics_input_tokens():
    args = argparse.Namespace(metric="input_tokens", value=10, model="claude-3-sonnet", system=None, dry_run=False)
    with patch("scripts.emit_otel_metrics.input_tokens_counter") as mock_counter:
        emit_metrics(args)
        mock_counter.add.assert_called_once_with(10, {"gen_ai.request.model": "claude-3-sonnet"})


def test_emit_metrics_output_tokens():
    args = argparse.Namespace(metric="output_tokens", value=5, model="claude-3-sonnet", system=None, dry_run=False)
    with patch("scripts.emit_otel_metrics.output_tokens_counter") as mock_counter:
        emit_metrics(args)
        mock_counter.add.assert_called_once_with(5, {"gen_ai.request.model": "claude-3-sonnet"})


def test_emit_metrics_duration():
    args = argparse.Namespace(metric="duration", value=250.0, model="claude-3-sonnet", system=None, dry_run=False)
    with patch("scripts.emit_otel_metrics.request_duration") as mock_histogram:
        emit_metrics(args)
        mock_histogram.record.assert_called_once_with(250.0, {"gen_ai.request.model": "claude-3-sonnet"})


def test_emit_metrics_status():
    args = argparse.Namespace(metric="status", value=0, model=None, system="phase-gate", dry_run=False)
    # The status metric uses an observable gauge pattern; check global state
    with patch("scripts.emit_otel_metrics.system_health_gauge"):
        emit_metrics(args)
        from scripts.emit_otel_metrics import _system_health_val

        assert _system_health_val == 0


def test_emit_metrics_dry_run(capsys):
    args = argparse.Namespace(metric="input_tokens", value=10.0, model="claude-3-sonnet", system="otel", dry_run=True)
    emit_metrics(args)
    captured = capsys.readouterr()
    assert "[DRY-RUN] Metric definition: input_tokens" in captured.out
    assert "Value: 10.0" in captured.out


def test_main_cli():
    import sys

    from scripts.emit_otel_metrics import main

    test_args = ["scripts/emit_otel_metrics.py", "--metric", "input_tokens", "--value", "10", "--dry-run"]
    with patch.object(sys, "argv", test_args):
        with patch("scripts.emit_otel_metrics.emit_metrics") as mock_emit:
            main()
            assert mock_emit.called

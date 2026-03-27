#!/usr/bin/env python3
"""
Emit OTel metrics for LLM usage and system health.
Implements Phase 4D: OTel Metrics.

Usage:
    uv run python scripts/emit_otel_metrics.py --metric input_tokens --value 10 --model claude-3-sonnet
    uv run python scripts/emit_otel_metrics.py --metric status --value 1 --system phase-gate
"""

import argparse
import json
import os
import sys

# Suppress OTel SDK warning and console output logs during metric setup
os.environ["OTEL_PYTHON_METER_PROVIDER"] = "sdk_meter_provider"

try:
    from opentelemetry import metrics
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
except ImportError:
    # Try alternate OTLP exporter if grpc not available
    try:
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
    except ImportError:
        OTLPMetricExporter = None

    if "ConsoleMetricExporter" not in locals():
        print("Error: opentelemetry-api and opentelemetry-sdk are required.")
        sys.exit(1)

# Argument parsing early to handle dry-run before SDK setup if possible
# (But meter setup is global here, so we'll just handle it in main/emit)


def setup_otel(dry_run=False):
    """Set up OTel provider and reader."""
    if dry_run:
        # Return a dummy meter for dry-run
        class DummyMeter:
            def create_counter(self, *args, **kwargs):
                return type("Dummy", (), {"add": lambda self, *a, **k: None})()

            def create_histogram(self, *args, **kwargs):
                return type("Dummy", (), {"record": lambda self, *a, **k: None})()

            def create_observable_gauge(self, *args, **kwargs):
                return None

        return DummyMeter()

    reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
    provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(provider)
    return metrics.get_meter("dogma.otel.metrics")


# Global variables for metrics (will be initialized in main)
meter = None
input_tokens_histogram = None
output_tokens_histogram = None
request_duration = None
system_health_gauge = None
_reader = None

_system_health_val = 1


def get_system_health(options):
    return [metrics.Observation(_system_health_val)]


def init_metrics(m, dry_run=False):
    global input_tokens_histogram, output_tokens_histogram, request_duration, system_health_gauge
    input_tokens_histogram = m.create_histogram(
        "gen_ai.usage.input_tokens", unit="1", description="Number of input tokens"
    )
    output_tokens_histogram = m.create_histogram(
        "gen_ai.usage.output_tokens", unit="1", description="Number of output tokens"
    )
    request_duration = m.create_histogram(
        "gen_ai.client.operation.duration", unit="ms", description="Duration of the LLM request in milliseconds"
    )
    if not dry_run:
        system_health_gauge = m.create_observable_gauge(
            "system.health.status",
            callbacks=[get_system_health],
            description="System health status (1=Healthy, 0=Degraded/Critical)",
        )


def emit_metrics(args: argparse.Namespace):
    """Emit the requested metric."""
    global _system_health_val

    attributes = {}
    if args.model:
        attributes["gen_ai.request.model"] = args.model
    if args.system:
        attributes["system.name"] = args.system

    # Metric type and unit lookup for dry-run/consistent emission
    metric_info = {
        "input_tokens": {"type": "Histogram", "unit": "1", "description": "Number of input tokens"},
        "output_tokens": {"type": "Histogram", "unit": "1", "description": "Number of output tokens"},
        "duration": {
            "type": "Histogram",
            "unit": "ms",
            "description": "Duration of the LLM request in milliseconds",
        },
        "status": {
            "type": "ObservableGauge",
            "unit": "1",
            "description": "System health status (1=Healthy, 0=Degraded/Critical)",
        },
    }

    if args.dry_run:
        info = metric_info.get(args.metric, {})
        output = {
            "metric": f"gen_ai.usage.{args.metric}"
            if "tokens" in args.metric
            else ("gen_ai.client.operation.duration" if args.metric == "duration" else "system.health.status"),
            "description": info.get("description"),
            "type": info.get("type"),
            "unit": info.get("unit"),
            "value": args.value,
            "attributes": attributes,
        }
        print(json.dumps(output, indent=2))
        return

    if args.metric == "input_tokens":
        input_tokens_histogram.record(int(args.value), attributes)
    elif args.metric == "output_tokens":
        output_tokens_histogram.record(int(args.value), attributes)
    elif args.metric == "duration":
        request_duration.record(float(args.value), attributes)
    elif args.metric == "status":
        _system_health_val = int(args.value)
        # Observable gauge refreshes on collection/export

    # Force collection for CLI output visibility if not status (status is async)
    if not args.dry_run and args.metric != "status" and _reader and hasattr(_reader, "collect"):
        _reader.collect()


def main():
    parser = argparse.ArgumentParser(description="Emit OTel metrics.")
    parser.add_argument("--metric", choices=["input_tokens", "output_tokens", "duration", "status"], required=True)
    parser.add_argument("--value", type=float, required=True, help="Metric value")
    parser.add_argument("--model", type=str, help="Model name for GenAI metrics")
    parser.add_argument("--system", type=str, help="System name for health metrics")
    parser.add_argument("--dry-run", action="store_true", help="Print definitions without emitting")

    args = parser.parse_args()

    global meter, _reader
    if not args.dry_run:
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader

        endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        if endpoint and OTLPMetricExporter:
            exporter = OTLPMetricExporter(endpoint=endpoint)
        else:
            exporter = ConsoleMetricExporter()

        _reader = PeriodicExportingMetricReader(exporter)
        provider = MeterProvider(metric_readers=[_reader])
        metrics.set_meter_provider(provider)
        meter = metrics.get_meter("dogma.otel.metrics")
    else:
        # Dummy meter
        class DummyMeter:
            def create_counter(self, *a, **k):
                return type("D", (), {"add": lambda s, *args, **kwargs: None})()

            def create_histogram(self, *a, **k):
                return type("D", (), {"record": lambda s, *args, **kwargs: None})()

            def create_observable_gauge(self, *a, **k):
                return None

        meter = DummyMeter()

    init_metrics(meter, dry_run=args.dry_run)
    emit_metrics(args)


if __name__ == "__main__":
    main()

"""Tests for scripts/aggregate_session_costs.py."""

import json
import subprocess
from datetime import date
from pathlib import Path

import pytest

from scripts.aggregate_session_costs import aggregate_log, main
from scripts.session_cost_log import REQUIRED_RECORD_KEYS, log_session_cost, read_log

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE_FIXTURE = Path("tests/fixtures/baseline_data/session_cost_log_baseline.json")
BASELINE_SNAPSHOT = Path("tests/fixtures/baseline_data/aggregate_session_costs_baseline_snapshot.json")


@pytest.mark.io
def test_aggregate_log_happy_path_with_inclusive_date_bounds(tmp_path):
    """Aggregation groups by model and phase and includes boundary dates."""
    log_file = tmp_path / "session_cost_log.json"
    log_session_cost(
        "session-1",
        "claude-sonnet-4",
        100,
        50,
        "Phase 1",
        "2026-03-27T10:00:00Z",
        log_file=log_file,
    )
    log_session_cost(
        "session-2",
        "claude-sonnet-4",
        150,
        75,
        "Phase 1",
        "2026-03-28T11:00:00Z",
        log_file=log_file,
    )
    log_session_cost(
        "session-3",
        "gpt-5.4",
        80,
        40,
        "Phase 2",
        "2026-03-29T11:00:00Z",
        log_file=log_file,
    )

    payload = aggregate_log(
        log_file=log_file,
        start_date=date(2026, 3, 27),
        end_date=date(2026, 3, 28),
    )

    assert payload["source_boundary"]["accepted_source"] == "Exact six-field session_cost_log records only"
    assert payload["source_boundary"]["malformed_entry_policy"] == "fail-fast"
    assert payload["date_range"]["bounds"] == "inclusive"
    assert payload["output_boundary"].startswith("Grouped aggregate data for later Phase 2 seeding only")
    assert payload["groups"] == [
        {
            "model": "claude-sonnet-4",
            "phase": "Phase 1",
            "record_count": 2,
            "tokens_in": 250,
            "tokens_out": 125,
        }
    ]


@pytest.mark.io
def test_aggregate_log_empty_log_returns_no_groups(tmp_path):
    """A missing or empty source log should produce an empty aggregate payload."""
    log_file = tmp_path / "missing-session-cost-log.json"

    payload = aggregate_log(log_file=log_file)

    assert payload["groups"] == []
    assert payload["log_file"] == str(log_file)


@pytest.mark.io
def test_aggregate_log_fails_fast_on_malformed_entry(tmp_path):
    """Malformed source entries should fail fast rather than being skipped."""
    log_file = tmp_path / "session_cost_log.json"
    log_file.write_text(
        json.dumps(
            [
                {
                    "session_id": "session-1",
                    "model": "claude-sonnet-4",
                    "tokens_in": 100,
                    "tokens_out": 50,
                    "timestamp": "2026-03-27T10:00:00Z",
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="record at index 0"):
        aggregate_log(log_file=log_file)


@pytest.mark.io
def test_committed_baseline_fixture_uses_exact_six_field_records():
    """The committed Phase 2 baseline input stays within the accepted source boundary."""
    records = read_log(log_file=REPO_ROOT / BASELINE_FIXTURE)

    assert records
    assert all(set(record.keys()) == set(REQUIRED_RECORD_KEYS) for record in records)


@pytest.mark.io
def test_committed_baseline_snapshot_matches_deterministic_rerun():
    """The committed Phase 2 snapshot reruns deterministically from the canonical fixture."""
    expected_snapshot = json.loads((REPO_ROOT / BASELINE_SNAPSHOT).read_text(encoding="utf-8"))

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/aggregate_session_costs.py",
            "--log-file",
            str(BASELINE_FIXTURE),
            "--start-date",
            "2026-03-27",
            "--end-date",
            "2026-03-28",
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )

    assert result.returncode == 0, result.stderr

    actual_snapshot = json.loads(result.stdout)

    assert expected_snapshot["groups"], "Committed baseline snapshot must be non-empty"
    assert actual_snapshot["groups"], "Rerun baseline snapshot must be non-empty"
    assert actual_snapshot == expected_snapshot


@pytest.mark.parametrize("raw_value", ["2026/03/27", "2026-02-30", "not-a-date"])
def test_main_rejects_invalid_yyyy_mm_dd_date_args(monkeypatch, capsys, raw_value):
    """CLI date arguments must use valid YYYY-MM-DD values."""
    monkeypatch.setattr(
        "sys.argv",
        ["aggregate_session_costs.py", "--start-date", raw_value],
    )

    exit_code = main()

    assert exit_code == 1
    assert capsys.readouterr().err.strip() == "Error: --start-date must be YYYY-MM-DD"


@pytest.mark.io
def test_main_rejects_reversed_start_end_date_bounds(tmp_path, monkeypatch, capsys):
    """The CLI rejects reversed inclusive date bounds."""
    log_file = tmp_path / "missing-session-cost-log.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "aggregate_session_costs.py",
            "--log-file",
            str(log_file),
            "--start-date",
            "2026-03-29",
            "--end-date",
            "2026-03-27",
        ],
    )

    exit_code = main()

    assert exit_code == 1
    assert capsys.readouterr().err.strip() == "Error: start date must be less than or equal to end date"

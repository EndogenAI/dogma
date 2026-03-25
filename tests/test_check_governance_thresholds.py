"""tests/test_check_governance_thresholds.py

Tests for scripts/check_governance_thresholds.py

Covers:
1. test_load_thresholds_happy_path
2. test_load_thresholds_missing_file_raises
3. test_load_thresholds_malformed_yaml_raises
4. test_load_thresholds_non_mapping_raises
5. test_evaluate_encoding_coverage_passes
6. test_evaluate_encoding_coverage_fails_below_threshold
7. test_evaluate_encoding_coverage_zero_rows_fails
8. test_evaluate_crd_passes
9. test_evaluate_crd_fails_below_threshold
10. test_main_all_pass_exit_0
11. test_main_threshold_breach_exit_1
12. test_main_missing_input_file_exit_2
13. test_main_bad_thresholds_exit_2
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest
import yaml

thresholds_mod = importlib.import_module("scripts.check_governance_thresholds")
load_thresholds = thresholds_mod.load_thresholds
evaluate_encoding_coverage = thresholds_mod.evaluate_encoding_coverage
evaluate_crd = thresholds_mod.evaluate_crd
main = thresholds_mod.main

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_GOOD_THRESHOLDS = {
    "encoding_coverage": {"min_principles_passing": 0.60},
    "cross_reference_density": {"min_mean_crd": 0.30},
}

_ENCODING_OUTPUT_PASSING = "| Endogenous-First | 3/4 |\n| Algorithms | 4/4 |\n| Local-Compute | 2/4 |\n"

_ENCODING_OUTPUT_FAILING = "| Endogenous-First | 1/4 |\n| Algorithms | 0/4 |\n| Local-Compute | 1/4 |\n"

_CRD_PASSING = {"fleet_statistics": {"mean": 0.50, "sample_size": 10}}

_CRD_FAILING = {"fleet_statistics": {"mean": 0.10, "sample_size": 10}}


def _write_thresholds(tmp_path: Path) -> Path:
    p = tmp_path / "governance-thresholds.yml"
    p.write_text(yaml.dump(_GOOD_THRESHOLDS))
    return p


# ---------------------------------------------------------------------------
# 1–4: load_thresholds
# ---------------------------------------------------------------------------


class TestLoadThresholds:
    def test_load_thresholds_happy_path(self, tmp_path: Path) -> None:
        p = _write_thresholds(tmp_path)
        data = load_thresholds(p)
        assert data["encoding_coverage"]["min_principles_passing"] == 0.60

    def test_load_thresholds_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="thresholds file not found"):
            load_thresholds(tmp_path / "nonexistent.yml")

    def test_load_thresholds_malformed_yaml_raises(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.yml"
        p.write_text(": : : bad\n{{{")
        with pytest.raises(ValueError, match="malformed YAML"):
            load_thresholds(p)

    def test_load_thresholds_non_mapping_raises(self, tmp_path: Path) -> None:
        p = tmp_path / "list.yml"
        p.write_text("- item1\n- item2\n")
        with pytest.raises(ValueError, match="YAML mapping"):
            load_thresholds(p)


# ---------------------------------------------------------------------------
# 5–7: evaluate_encoding_coverage
# ---------------------------------------------------------------------------


class TestEvaluateEncodingCoverage:
    def test_evaluate_encoding_coverage_passes(self) -> None:
        passed, msg = evaluate_encoding_coverage(_ENCODING_OUTPUT_PASSING, 0.60)
        assert passed is True
        assert "3/3" in msg or "2/3" in msg or "passing" in msg.lower()

    def test_evaluate_encoding_coverage_fails_below_threshold(self) -> None:
        passed, msg = evaluate_encoding_coverage(_ENCODING_OUTPUT_FAILING, 0.60)
        assert passed is False

    def test_evaluate_encoding_coverage_zero_rows_fails(self) -> None:
        """Regression: no rows must fail, not silently pass (blocking comment 2990976477)."""
        passed, msg = evaluate_encoding_coverage("no table rows here", 0.60)
        assert passed is False
        assert "no encoding coverage rows" in msg.lower() or "cannot validate" in msg.lower()


# ---------------------------------------------------------------------------
# 8–9: evaluate_crd
# ---------------------------------------------------------------------------


class TestEvaluateCrd:
    def test_evaluate_crd_passes(self) -> None:
        passed, msg = evaluate_crd(_CRD_PASSING, 0.30)
        assert passed is True
        assert "0.5" in msg or "0.50" in msg

    def test_evaluate_crd_fails_below_threshold(self) -> None:
        passed, _ = evaluate_crd(_CRD_FAILING, 0.30)
        assert passed is False


# ---------------------------------------------------------------------------
# 10–13: main()
# ---------------------------------------------------------------------------


class TestMain:
    def _write_inputs(self, tmp_path: Path, enc_text: str, crd_data: dict) -> tuple[Path, Path, Path]:
        t = _write_thresholds(tmp_path)
        enc = tmp_path / "enc.txt"
        enc.write_text(enc_text)
        crd = tmp_path / "crd.json"
        crd.write_text(json.dumps(crd_data))
        return t, enc, crd

    def test_main_all_pass_exit_0(self, tmp_path: Path) -> None:
        t, enc, crd = self._write_inputs(tmp_path, _ENCODING_OUTPUT_PASSING, _CRD_PASSING)
        rc = main(
            [
                "--encoding-output",
                str(enc),
                "--crd-json",
                str(crd),
                "--thresholds",
                str(t),
            ]
        )
        assert rc == 0

    def test_main_threshold_breach_exit_1(self, tmp_path: Path) -> None:
        t, enc, crd = self._write_inputs(tmp_path, _ENCODING_OUTPUT_FAILING, _CRD_FAILING)
        rc = main(
            [
                "--encoding-output",
                str(enc),
                "--crd-json",
                str(crd),
                "--thresholds",
                str(t),
            ]
        )
        assert rc == 1

    def test_main_missing_input_file_exit_2(self, tmp_path: Path) -> None:
        t = _write_thresholds(tmp_path)
        rc = main(
            [
                "--encoding-output",
                str(tmp_path / "missing.txt"),
                "--crd-json",
                str(tmp_path / "missing.json"),
                "--thresholds",
                str(t),
            ]
        )
        assert rc == 2

    def test_main_bad_thresholds_exit_2(self, tmp_path: Path) -> None:
        bad_t = tmp_path / "bad.yml"
        bad_t.write_text("- not a mapping\n")
        enc = tmp_path / "enc.txt"
        enc.write_text(_ENCODING_OUTPUT_PASSING)
        crd = tmp_path / "crd.json"
        crd.write_text(json.dumps(_CRD_PASSING))
        rc = main(
            [
                "--encoding-output",
                str(enc),
                "--crd-json",
                str(crd),
                "--thresholds",
                str(bad_t),
            ]
        )
        assert rc == 2

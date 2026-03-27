"""Tests for scripts/detect_orchestration_loop.py"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).parent.parent / "scripts" / "detect_orchestration_loop.py"
spec = importlib.util.spec_from_file_location("detect_orchestration_loop", _SCRIPT)
_mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(_mod)  # type: ignore[union-attr]
detect_loop = _mod.detect_loop
main = _mod.main


def _write_scratchpad(tmp_path: Path, headings: list[str]) -> Path:
    p = tmp_path / "2026-03-26.md"
    lines = []
    for h in headings:
        lines.append(f"## {h}\n\nSome content.\n\n")
    p.write_text("".join(lines), encoding="utf-8")
    return p


@pytest.mark.io
class TestDetectLoop:
    def test_no_loop_unique_headings(self, tmp_path: Path) -> None:
        p = _write_scratchpad(tmp_path, ["Phase 1", "Phase 2", "Phase 3", "Review"])
        result = detect_loop("Phase 1", str(p))
        assert result["loop_detected"] is False
        assert result["iteration_count"] == 1

    def test_loop_detected_three_repeats(self, tmp_path: Path) -> None:
        p = _write_scratchpad(
            tmp_path,
            ["Phase 3 Start", "Other", "Phase 3 Retry", "Unrelated", "Phase 3 Again"],
        )
        result = detect_loop("Phase 3", str(p))
        assert result["loop_detected"] is True
        assert result["iteration_count"] == 3

    def test_loop_detected_two_repeats(self, tmp_path: Path) -> None:
        p = _write_scratchpad(tmp_path, ["Phase 2 Run", "Other", "Phase 2 Retry"])
        result = detect_loop("Phase 2", str(p))
        assert result["loop_detected"] is True
        assert result["iteration_count"] == 2

    def test_file_not_found(self, tmp_path: Path) -> None:
        result = detect_loop("Phase X", str(tmp_path / "missing.md"))
        assert result["loop_detected"] is False
        assert result["iteration_count"] == 0
        assert result["error"] == "file not found"

    def test_empty_scratchpad_no_h2(self, tmp_path: Path) -> None:
        p = tmp_path / "empty.md"
        p.write_text("No headings here at all.\n", encoding="utf-8")
        result = detect_loop("Phase 1", str(p))
        assert result["loop_detected"] is False
        assert result["iteration_count"] == 0
        assert result["matched_sections"] == []

    def test_case_insensitive_match(self, tmp_path: Path) -> None:
        p = _write_scratchpad(tmp_path, ["PHASE 1 RUN", "phase 1 retry"])
        result = detect_loop("phase 1", str(p))
        assert result["loop_detected"] is True
        assert result["iteration_count"] == 2

    def test_only_recent_10_headings(self, tmp_path: Path) -> None:
        # Put 12 headings; first 2 match but are outside the 10-heading window
        headings = ["Phase X match", "Phase X again"] + [f"Other {i}" for i in range(10)]
        p = _write_scratchpad(tmp_path, headings)
        result = detect_loop("Phase X", str(p))
        assert result["loop_detected"] is False

    def test_matched_sections_populated(self, tmp_path: Path) -> None:
        p = _write_scratchpad(tmp_path, ["Alpha Run", "Alpha Retry", "Beta"])
        result = detect_loop("Alpha", str(p))
        assert len(result["matched_sections"]) == 2


class TestMain:
    def test_main_outputs_json(self, tmp_path: Path, capsys) -> None:
        p = _write_scratchpad(tmp_path, ["Phase 1", "Phase 1 Again"])
        rc = main(["--task", "Phase 1", "--scratchpad", str(p)])
        assert rc == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert "loop_detected" in data

    def test_main_missing_file_exits_0(self, tmp_path: Path, capsys) -> None:
        rc = main(["--task", "T", "--scratchpad", str(tmp_path / "nope.md")])
        assert rc == 0
        data = json.loads(capsys.readouterr().out)
        assert data["error"] == "file not found"

"""Tests for prune_scratchpad.py --snapshot and compare_context_snapshot.py"""

from __future__ import annotations

# Import compare_context_snapshot
import importlib.util as _ilu
import json
from pathlib import Path

import pytest

_CCS_PATH = Path(__file__).parent.parent / "scripts" / "compare_context_snapshot.py"
_ccs_spec = _ilu.spec_from_file_location("compare_context_snapshot", _CCS_PATH)
_ccs = _ilu.module_from_spec(_ccs_spec)  # type: ignore[arg-type]
_ccs_spec.loader.exec_module(_ccs)  # type: ignore[union-attr]
compare = _ccs.compare
main_compare = _ccs.main

# Import prune_scratchpad for _run_snapshot
_PS_PATH = Path(__file__).parent.parent / "scripts" / "prune_scratchpad.py"
_ps_spec = _ilu.spec_from_file_location("prune_scratchpad", _PS_PATH)
_ps = _ilu.module_from_spec(_ps_spec)  # type: ignore[arg-type]
_ps_spec.loader.exec_module(_ps)  # type: ignore[union-attr]
_run_snapshot = _ps._run_snapshot


def _make_scratchpad(tmp_path: Path, heading: str, params: list[str]) -> Path:
    p = tmp_path / "2026-03-26.md"
    lines = [f"## {heading}\n"]
    for param in params:
        lines.append(f"{param}\n")
    p.write_text("".join(lines), encoding="utf-8")
    return p


@pytest.mark.io
class TestRunSnapshot:
    def test_snapshot_created(self, tmp_path: Path) -> None:
        sp = _make_scratchpad(tmp_path, "Phase 3 Planning", ["Step A", "Step B", "Step C"])
        _run_snapshot(sp, "2026-03-26")
        snap = tmp_path / "2026-03-26-snapshot.yaml"
        assert snap.exists()

    def test_snapshot_schema(self, tmp_path: Path) -> None:
        sp = _make_scratchpad(tmp_path, "Phase 3 Planning", ["Step A", "Step B"])
        _run_snapshot(sp, "2026-03-26")
        snap = tmp_path / "2026-03-26-snapshot.yaml"
        content = snap.read_text(encoding="utf-8")
        assert "task_name: Phase 3 Planning" in content
        assert "timestamp:" in content
        assert "scratchpad_section: Phase 3 Planning" in content
        assert "task_parameters:" in content
        assert "- Step A" in content

    def test_snapshot_unknown_when_no_h2(self, tmp_path: Path) -> None:
        sp = tmp_path / "2026-03-26.md"
        sp.write_text("Just prose, no headings.\n", encoding="utf-8")
        _run_snapshot(sp, "2026-03-26")
        snap = tmp_path / "2026-03-26-snapshot.yaml"
        content = snap.read_text(encoding="utf-8")
        assert "task_name: unknown" in content

    def test_snapshot_skips_archived_sections(self, tmp_path: Path) -> None:
        sp = tmp_path / "2026-03-26.md"
        sp.write_text(
            "## Phase 1 Summary (archived 2026-03-25)\nOld content.\n\n## Phase 2 Active\nNew content.\n",
            encoding="utf-8",
        )
        _run_snapshot(sp, "2026-03-26")
        snap = tmp_path / "2026-03-26-snapshot.yaml"
        content = snap.read_text(encoding="utf-8")
        assert "Phase 2 Active" in content
        assert "Phase 1 Summary" not in content

    def test_snapshot_missing_file_returns_1(self, tmp_path: Path) -> None:
        result = _run_snapshot(tmp_path / "missing.md", "2026-03-26")
        assert result == 1


@pytest.mark.io
class TestCompareContextSnapshot:
    def _write_snap(self, tmp_path: Path, task_name: str, params: list[str]) -> Path:
        snap = tmp_path / "2026-03-26-snapshot.yaml"
        lines = [
            f"task_name: {task_name}",
            "timestamp: 2026-03-26T10:00:00",
            f"scratchpad_section: {task_name}",
            "task_parameters:",
        ]
        for p in params:
            lines.append(f"  - {p}")
        snap.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return snap

    def test_equivalent_same_task_and_params(self, tmp_path: Path) -> None:
        params = ["Step A", "Step B", "Step C", "Step D", "Step E"]
        snap = self._write_snap(tmp_path, "Phase 3", params)
        sp = _make_scratchpad(tmp_path, "Phase 3", params)
        result = compare(str(snap), str(sp))
        assert result["equivalent"] is True
        assert result["task_name"] == "Phase 3"
        assert result["match_ratio"] == 1.0

    def test_non_equivalent_different_task(self, tmp_path: Path) -> None:
        snap = self._write_snap(tmp_path, "Phase 3", ["Step A", "Step B"])
        sp = _make_scratchpad(tmp_path, "Phase 4", ["Step A", "Step B"])
        result = compare(str(snap), str(sp))
        assert result["equivalent"] is False

    def test_partial_match_below_threshold(self, tmp_path: Path) -> None:
        # 3/5 = 0.6, below 0.8
        snap = self._write_snap(tmp_path, "Phase 3", ["A", "B", "C", "D", "E"])
        sp = _make_scratchpad(tmp_path, "Phase 3", ["A", "B", "C", "X", "Y"])
        result = compare(str(snap), str(sp))
        assert result["equivalent"] is False
        assert result["match_ratio"] < 0.8

    def test_missing_snapshot_error(self, tmp_path: Path) -> None:
        result = compare(str(tmp_path / "nope.yaml"), None)
        assert result["equivalent"] is False
        assert result["error"] == "snapshot not found"
        assert result["match_ratio"] == 0.0

    def test_missing_scratchpad_returns_error(self, tmp_path: Path) -> None:
        snap = self._write_snap(tmp_path, "Phase 3", ["A"])
        result = compare(str(snap), str(tmp_path / "missing.md"))
        assert result["equivalent"] is False


class TestMainCompare:
    def test_main_outputs_json(self, tmp_path: Path, capsys) -> None:
        params = ["A", "B", "C", "D", "E"]
        snap = tmp_path / "snap.yaml"
        lines = [
            "task_name: Phase 3",
            "timestamp: 2026-03-26T10:00:00",
            "scratchpad_section: Phase 3",
            "task_parameters:",
        ]
        for p in params:
            lines.append(f"  - {p}")
        snap.write_text("\n".join(lines) + "\n", encoding="utf-8")

        sp = _make_scratchpad(tmp_path, "Phase 3", params)
        rc = main_compare(["--snapshot", str(snap), "--scratchpad", str(sp)])
        assert rc == 0
        data = json.loads(capsys.readouterr().out)
        assert "equivalent" in data

    def test_main_missing_snapshot_exits_0(self, tmp_path: Path, capsys) -> None:
        rc = main_compare(["--snapshot", str(tmp_path / "nope.yaml")])
        assert rc == 0
        data = json.loads(capsys.readouterr().out)
        assert data["error"] == "snapshot not found"

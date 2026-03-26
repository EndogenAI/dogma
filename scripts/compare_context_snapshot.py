"""compare_context_snapshot.py — Compare current scratchpad context against a saved snapshot.

Reads a YAML snapshot produced by `prune_scratchpad.py --snapshot` and compares it
against the current active scratchpad section. Useful for detecting whether the agent
has re-entered the same context after an error-recovery cycle.

Inputs: --snapshot <path-to-snapshot.yaml>, optional --scratchpad <path>
Outputs: JSON to stdout: {"equivalent": bool, "task_name": str, "match_ratio": float}
Exit codes: 0 always (non-blocking; use returned JSON to decide)
Usage:
    uv run python scripts/compare_context_snapshot.py \
        --snapshot .tmp/feat/2026-03-26-snapshot.yaml
    uv run python scripts/compare_context_snapshot.py \
        --snapshot .tmp/feat/2026-03-26-snapshot.yaml \
        --scratchpad .tmp/feat/2026-03-26.md
    uv run python scripts/compare_context_snapshot.py --help
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

_EQUIVALENCE_THRESHOLD = 0.8


def _git_branch_slug() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip().replace("/", "-")
    except Exception:
        pass
    return "default"


def _resolve_scratchpad() -> Path:
    today = date.today().isoformat()
    slug = _git_branch_slug()
    root = Path(__file__).parent.parent
    return root / ".tmp" / slug / f"{today}.md"


def _parse_snapshot(snapshot_path: Path) -> dict:
    """Manually parse the YAML snapshot (no yaml import required)."""
    lines = snapshot_path.read_text(encoding="utf-8").splitlines()
    task_name = ""
    task_parameters: list[str] = []
    in_params = False

    for line in lines:
        if line.startswith("task_name:"):
            task_name = line.split(":", 1)[1].strip()
        elif line.startswith("task_parameters:"):
            in_params = True
        elif in_params:
            stripped = line.strip()
            if stripped.startswith("- "):
                task_parameters.append(stripped[2:].strip())
            elif stripped and not stripped.startswith("#"):
                in_params = False

    return {"task_name": task_name, "task_parameters": task_parameters}


def _first_active_section(text: str) -> tuple[str, list[str]]:
    """Return (heading, first_5_lines) of first substantive non-archived H2 section.

    Skips well-known meta headings (Active Context, Session State, etc.) that
    appear at the top of pruned scratchpads but do not represent the active
    task/phase being compared.
    """
    _META_HEADINGS = frozenset(
        {
            "Active Context",
            "Session State",
            "Session Start",
            "Pre-Compact Checkpoint",
            "Orchestration Plan",
        }
    )

    lines = text.splitlines()
    in_section = False
    heading = ""
    section_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            candidate = stripped[3:].strip()
            if "archived" in candidate.lower() or candidate in _META_HEADINGS:
                in_section = False
                heading = ""
                section_lines = []
                continue
            heading = candidate
            section_lines = []
            in_section = True
            break

    if not in_section or not heading:
        return "", []

    # Collect up to 5 non-empty lines after the heading
    after_heading = False
    for line in lines:
        stripped = line.strip()
        if stripped == f"## {heading}":
            after_heading = True
            continue
        if after_heading:
            if stripped.startswith("## "):
                break
            if stripped:
                section_lines.append(stripped)
                if len(section_lines) >= 5:
                    break

    return heading, section_lines


def compare(snapshot_path: str, scratchpad_path: str | None) -> dict:
    snap_p = Path(snapshot_path)
    if not snap_p.exists():
        return {
            "equivalent": False,
            "task_name": "",
            "match_ratio": 0.0,
            "error": "snapshot not found",
        }

    snapshot = _parse_snapshot(snap_p)
    snap_task = snapshot["task_name"]
    snap_params = snapshot["task_parameters"]

    if scratchpad_path:
        current_path = Path(scratchpad_path)
    else:
        current_path = _resolve_scratchpad()

    if not current_path.exists():
        return {
            "equivalent": False,
            "task_name": snap_task,
            "match_ratio": 0.0,
            "error": "scratchpad not found",
        }

    text = current_path.read_text(encoding="utf-8")
    current_task, current_params = _first_active_section(text)

    if not current_task:
        return {"equivalent": False, "task_name": snap_task, "match_ratio": 0.0}

    # Task name check
    tasks_match = snap_task.lower() == current_task.lower()

    # Parameter similarity
    denominator = max(len(snap_params), len(current_params), 1)
    matched = sum(1 for p in snap_params if p in current_params)
    ratio = matched / denominator

    equivalent = tasks_match and ratio >= _EQUIVALENCE_THRESHOLD

    return {
        "equivalent": equivalent,
        "task_name": snap_task,
        "match_ratio": round(ratio, 4),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare current scratchpad context against a saved snapshot.")
    parser.add_argument("--snapshot", required=True, help="Path to the snapshot YAML file")
    parser.add_argument(
        "--scratchpad",
        default=None,
        help="Path to the scratchpad .md file (auto-resolved if not provided)",
    )
    args = parser.parse_args(argv)

    result = compare(args.snapshot, args.scratchpad)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())

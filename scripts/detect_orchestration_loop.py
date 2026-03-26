"""detect_orchestration_loop.py — Detect orchestration loops in the scratchpad.

Parses the scratchpad file and checks whether a given task name appears repeatedly
in recent H2 section headings, indicating the agent is re-executing a failed sequence.

Inputs: --task <task-name>, --scratchpad <path-to-scratchpad-md>
Outputs: JSON to stdout: {"loop_detected": bool, "task": str, "iteration_count": int,
         "matched_sections": [list-of-headings]}
Exit codes: 0 always (non-blocking; use returned JSON to decide)
Usage:
    uv run python scripts/detect_orchestration_loop.py --task "Phase 3" \
        --scratchpad .tmp/feat-q2-wave2-phase2/2026-03-26.md
    uv run python scripts/detect_orchestration_loop.py --help
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_LOOP_THRESHOLD = 2
_RECENT_WINDOW = 10


def _parse_h2_headings(text: str) -> list[str]:
    """Return all H2 section headings from scratchpad text."""
    headings = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            headings.append(stripped[3:].strip())
    return headings


def detect_loop(task: str, scratchpad_path: str) -> dict:
    path = Path(scratchpad_path)
    if not path.exists():
        return {
            "loop_detected": False,
            "task": task,
            "iteration_count": 0,
            "matched_sections": [],
            "error": "file not found",
        }

    text = path.read_text(encoding="utf-8")
    all_headings = _parse_h2_headings(text)
    recent = all_headings[-_RECENT_WINDOW:]

    task_lower = task.lower()
    matched = [h for h in recent if task_lower in h.lower()]
    count = len(matched)

    return {
        "loop_detected": count >= _LOOP_THRESHOLD,
        "task": task,
        "iteration_count": count,
        "matched_sections": matched,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Detect orchestration loops in the scratchpad.")
    parser.add_argument("--task", required=True, help="Task name to check for repetition")
    parser.add_argument("--scratchpad", required=True, help="Path to the scratchpad .md file")
    args = parser.parse_args(argv)

    result = detect_loop(args.task, args.scratchpad)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())

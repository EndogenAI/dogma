# `detect\_orchestration\_loop`

detect_orchestration_loop.py — Detect orchestration loops in the scratchpad.

Parses the scratchpad file and checks whether a given task name appears repeatedly
in recent H2 section headings, indicating the agent is re-executing a failed sequence.

Inputs: --task <task-name>, --scratchpad <path-to-scratchpad-md>
Outputs: JSON to stdout: {"loop_detected": bool, "task": str, "iteration_count": int,
         "matched_sections": [list-of-headings]}
Exit codes: 0 always (non-blocking; use returned JSON to decide)
Usage:
    uv run python scripts/detect_orchestration_loop.py --task "Phase 3"         --scratchpad .tmp/feat-q2-wave2-phase2/2026-03-26.md
    uv run python scripts/detect_orchestration_loop.py --help

## Usage

```bash
    uv run python scripts/detect_orchestration_loop.py --task "Phase 3"         --scratchpad .tmp/feat-q2-wave2-phase2/2026-03-26.md
    uv run python scripts/detect_orchestration_loop.py --help
```

<!-- hash:e544ae88fdbec25f -->

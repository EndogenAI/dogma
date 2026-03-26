# `compare\_context\_snapshot`

compare_context_snapshot.py — Compare current scratchpad context against a saved snapshot.

Reads a YAML snapshot produced by `prune_scratchpad.py --snapshot` and compares it
against the current active scratchpad section. Useful for detecting whether the agent
has re-entered the same context after an error-recovery cycle.

Inputs: --snapshot <path-to-snapshot.yaml>, optional --scratchpad <path>
Outputs: JSON to stdout: {"equivalent": bool, "task_name": str, "match_ratio": float}
Exit codes: 0 always (non-blocking; use returned JSON to decide)
Usage:
    uv run python scripts/compare_context_snapshot.py         --snapshot .tmp/feat/2026-03-26-snapshot.yaml
    uv run python scripts/compare_context_snapshot.py         --snapshot .tmp/feat/2026-03-26-snapshot.yaml         --scratchpad .tmp/feat/2026-03-26.md
    uv run python scripts/compare_context_snapshot.py --help

## Usage

```bash
    uv run python scripts/compare_context_snapshot.py         --snapshot .tmp/feat/2026-03-26-snapshot.yaml
    uv run python scripts/compare_context_snapshot.py         --snapshot .tmp/feat/2026-03-26-snapshot.yaml         --scratchpad .tmp/feat/2026-03-26.md
    uv run python scripts/compare_context_snapshot.py --help
```

<!-- hash:6534725569bdfcee -->

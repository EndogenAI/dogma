# `watch\_scratchpad`

watch_scratchpad.py — Auto-annotate scratchpad session files on change.

Purpose:
    Watches the .tmp/ directory for changes to *.md session files and immediately
    runs `prune_scratchpad.py --annotate` on the changed file. This keeps every H2
    heading annotated with its current line range [Lstart–Lend] at all times,
    enabling agents to reference sections by precise line numbers rather than by
    vague heading names.

    _index.md and any file whose name starts with '_' or '.' are excluded.

    A cooldown window (COOLDOWN_SECONDS) prevents the annotator's own file write
    from re-triggering an annotation loop.

Usage:
    uv run python scripts/watch_scratchpad.py
    uv run python scripts/watch_scratchpad.py --tmp-dir .tmp

    Start this as a background VS Code task at the beginning of each session.
    Stop with Ctrl-C.

Requirements:
    watchdog >= 4.0 — install with: uv sync

    If watchdog is not installed, install it:
        uv add --group dev watchdog

Exit codes:
    0 — clean exit (Ctrl-C or observer stopped)
    1 — watchdog not installed

## Usage

```bash
    uv run python scripts/watch_scratchpad.py
    uv run python scripts/watch_scratchpad.py --tmp-dir .tmp

    Start this as a background VS Code task at the beginning of each session.
    Stop with Ctrl-C.
```

<!-- hash:5832596046e6a8b1 -->

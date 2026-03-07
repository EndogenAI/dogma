"""
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
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import threading
import time
from pathlib import Path

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:
    print(
        "ERROR: watchdog is not installed.\nInstall it with: uv sync  (or: uv add --group dev watchdog)",
        file=sys.stderr,
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COOLDOWN_SECONDS = 2.0
"""Seconds to ignore further events on a file after we write to it ourselves."""

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
ANNOTATE_SCRIPT = SCRIPT_DIR / "prune_scratchpad.py"


# ---------------------------------------------------------------------------
# Event handler
# ---------------------------------------------------------------------------


class ScratchpadHandler(FileSystemEventHandler):
    """Watchdog event handler that runs the annotator on session file changes."""

    def __init__(self) -> None:
        super().__init__()
        self._recently_written: dict[str, float] = {}
        self._lock = threading.Lock()

    def _cooldown_ok(self, path: str) -> bool:
        """Return True if enough time has passed since we last wrote to this path."""
        with self._lock:
            last = self._recently_written.get(path, 0.0)
            return (time.monotonic() - last) > COOLDOWN_SECONDS

    def _record(self, path: str) -> None:
        """Record that we are about to write to this path."""
        with self._lock:
            self._recently_written[path] = time.monotonic()

    def _handle(self, src_path: str) -> None:
        p = Path(src_path)

        # Only process Markdown session files
        if p.suffix != ".md":
            return
        # Skip index files and hidden files
        if p.name.startswith("_") or p.name.startswith("."):
            return
        # Skip if the file has vanished
        if not p.exists():
            return
        # Suppress re-triggers from our own writes
        if not self._cooldown_ok(src_path):
            return

        self._record(src_path)

        try:
            rel = p.relative_to(REPO_ROOT)
        except ValueError:
            rel = p

        print(f"[watch_scratchpad] Changed: {rel} — annotating…", flush=True)

        result = subprocess.run(
            [sys.executable, str(ANNOTATE_SCRIPT), "--annotate", "--file", src_path],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(
                f"[watch_scratchpad] ERROR annotating {rel}:\n{result.stderr.strip()}",
                file=sys.stderr,
                flush=True,
            )
        else:
            msg = result.stdout.strip()
            if msg:
                print(f"[watch_scratchpad] {msg}", flush=True)

    def on_modified(self, event) -> None:  # type: ignore[override]
        if not event.is_directory:
            self._handle(event.src_path)

    def on_created(self, event) -> None:  # type: ignore[override]
        if not event.is_directory:
            self._handle(event.src_path)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Watch .tmp/ and auto-annotate scratchpad session files on change.")
    parser.add_argument(
        "--tmp-dir",
        default=str(REPO_ROOT / ".tmp"),
        help="Directory to watch (default: .tmp/ at repo root)",
    )
    args = parser.parse_args()

    tmp_dir = Path(args.tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    handler = ScratchpadHandler()
    observer = Observer()
    observer.schedule(handler, str(tmp_dir), recursive=True)
    observer.start()

    print(f"[watch_scratchpad] Watching {tmp_dir}/ (Ctrl-C to stop)", flush=True)

    try:
        while observer.is_alive():
            observer.join(timeout=1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
    return 0


if __name__ == "__main__":
    sys.exit(main())

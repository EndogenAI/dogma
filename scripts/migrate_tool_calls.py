"""scripts/migrate_tool_calls.py — Archive synthetic seed data before live capture.

Moves .cache/mcp-metrics/tool_calls.jsonl to tool_calls.synthetic.bak.jsonl
and creates an empty tool_calls.jsonl ready for live records.

Usage:
    uv run python scripts/migrate_tool_calls.py
    uv run python scripts/migrate_tool_calls.py --dry-run

Exit codes:
    0 — success or source not found (nothing to do)
    1 — backup already exists; remove it first to re-run
"""

import argparse
import pathlib
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without writing")
    args = parser.parse_args()

    cache_dir = pathlib.Path(".cache/mcp-metrics")
    src = cache_dir / "tool_calls.jsonl"
    dst = cache_dir / "tool_calls.synthetic.bak.jsonl"

    if not src.exists():
        print(f"Source not found: {src} — nothing to migrate.")
        return 0

    if dst.exists():
        print(f"Backup already exists: {dst} — skipping to avoid clobber.")
        print("To re-run, remove the backup file first.")
        return 1

    line_count = sum(1 for _ in src.open(encoding="utf-8"))

    if args.dry_run:
        print(f"[dry-run] Would move: {src} → {dst} ({line_count} records)")
        print(f"[dry-run] Would create empty: {src}")
        return 0

    src.rename(dst)
    src.touch()
    print(f"Archived {line_count} synthetic records to: {dst}")
    print(f"Created empty live baseline: {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

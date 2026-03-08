"""
wait_for_unblock.py — Poll a GitHub issue until status:blocked is removed.

Purpose:
    Polls a GitHub issue's labels at a configurable interval. When
    status:blocked is no longer present, exits 0 and writes a trigger file to
    .tmp/triggers/ so the event is discoverable by the next agent session even
    if no VS Code session was open at the time.

    Two integration patterns:

    Tier 1 — in-session blocking (requires VS Code session open):
        Run as a background terminal, then block with await_terminal:

            Terminal A (background):
                uv run python scripts/wait_for_unblock.py --issue 60

            Agent (in session):
                # Start background poll, then await on it
                # When it returns exit 0, auto-continue orchestration

    Tier 2 — cross-session trigger file:
        Run as a launchd or cron daemon. On exit 0 the script writes
        .tmp/triggers/<repo>-issue-<N>.unblocked. Any future session start
        can check for these files before building the orchestration plan:

            python scripts/wait_for_unblock.py --issue 60 --interval 300

        Session start check:
            ls .tmp/triggers/*.unblocked 2>/dev/null && cat the file

    Tier 3 (future): GitHub webhook → local pub/sub handler. The trigger file
        written here is the connection point — a webhook consumer would write
        the same file format, and session-start logic reads it identically.

Usage:
    uv run python scripts/wait_for_unblock.py --issue 60
    uv run python scripts/wait_for_unblock.py --issue 60 --interval 60 --timeout 3600
    uv run python scripts/wait_for_unblock.py --issue 60 --repo EndogenAI/Workflows
    uv run python scripts/wait_for_unblock.py --issue 60 --dry-run

Arguments:
    --issue N           GitHub issue number to monitor (required)
    --interval SECS     Poll interval in seconds (default: 300)
    --timeout SECS      Max total wait in seconds, 0 = infinite (default: 0)
    --repo OWNER/REPO   Repository slug (default: auto-detected from git remote)
    --trigger-dir PATH  Directory to write trigger files (default: .tmp/triggers)
    --blocked-label     Label indicating blocked state (default: status:blocked)
    --dry-run           Print resolved config and exit without polling

Exit codes:
    0  — issue is no longer blocked (status:blocked label absent)
    1  — timeout reached before unblock
    2  — error (invalid issue, gh CLI unavailable, bad repo, etc.)

Trigger file (written on exit 0):
    .tmp/triggers/<owner>-<repo>-issue-<N>.unblocked
    Contains: issue number, repo, title, url, unblocked_at (ISO 8601 UTC)
    Session-start check: ls .tmp/triggers/*.unblocked 2>/dev/null
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BLOCKED_LABEL_DEFAULT = "status:blocked"


# ---------------------------------------------------------------------------
# Pure helpers (no I/O — fully unit-testable)
# ---------------------------------------------------------------------------


def parse_repo_from_remote_url(url: str) -> str | None:
    """Extract owner/repo from a GitHub remote URL (HTTPS or SSH)."""
    url = url.strip()
    if "github.com/" in url:
        part = url.split("github.com/")[-1]
    elif "github.com:" in url:
        part = url.split("github.com:")[-1]
    else:
        return None
    return part.removesuffix(".git").strip("/") or None


def parse_labels(gh_json: str) -> list[str]:
    """Parse label names from `gh issue view --json labels` output."""
    data = json.loads(gh_json)
    return [lbl["name"] for lbl in data.get("labels", [])]


def parse_issue_meta(gh_json: str) -> dict:
    """Parse title and url from `gh issue view --json title,url` output."""
    return json.loads(gh_json)


def trigger_filename(repo: str, issue: int) -> str:
    """Return the trigger filename for a given repo and issue number."""
    safe = repo.replace("/", "-")
    return f"{safe}-issue-{issue}.unblocked"


def format_trigger_content(repo: str, issue: int, meta: dict) -> str:
    """Return the string content of a trigger file."""
    lines = [
        f"issue: {issue}",
        f"repo: {repo}",
        f"title: {meta.get('title', '')}",
        f"url: {meta.get('url', '')}",
        f"unblocked_at: {datetime.now(timezone.utc).isoformat()}",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# I/O helpers (subprocess + filesystem)
# ---------------------------------------------------------------------------


def get_repo_from_git() -> str | None:
    """Auto-detect owner/repo from the git remote.origin.url."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        return parse_repo_from_remote_url(result.stdout)
    except subprocess.CalledProcessError:
        return None


def fetch_labels(repo: str, issue: int, blocked_label: str) -> tuple[bool, list[str]]:
    """
    Call `gh issue view` and return (is_blocked, all_label_names).
    Raises RuntimeError on gh CLI failure.
    """
    result = subprocess.run(
        ["gh", "issue", "view", str(issue), "--repo", repo, "--json", "labels"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"gh exit {result.returncode}")
    labels = parse_labels(result.stdout)
    return blocked_label in labels, labels


def fetch_issue_meta(repo: str, issue: int) -> dict:
    """Return title + url dict for the issue. Returns partial dict on error."""
    result = subprocess.run(
        ["gh", "issue", "view", str(issue), "--repo", repo, "--json", "title,url"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {"title": f"issue #{issue}", "url": ""}
    return parse_issue_meta(result.stdout)


def write_trigger(trigger_dir: Path, repo: str, issue: int, meta: dict) -> Path:
    """Write the trigger file and return its path."""
    trigger_dir.mkdir(parents=True, exist_ok=True)
    path = trigger_dir / trigger_filename(repo, issue)
    path.write_text(format_trigger_content(repo, issue, meta), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Core poll loop
# ---------------------------------------------------------------------------


def poll(
    repo: str,
    issue: int,
    interval: int,
    timeout: int,
    trigger_dir: Path,
    blocked_label: str,
) -> int:
    """
    Poll until blocked_label is absent from issue labels.

    Returns:
        0 — unblocked
        1 — timeout
        2 — error
    """
    start = time.monotonic()
    attempt = 0

    while True:
        attempt += 1
        elapsed = time.monotonic() - start

        try:
            is_blocked, labels = fetch_labels(repo, issue, blocked_label)
        except RuntimeError as exc:
            print(f"[wait_for_unblock] ERROR fetching labels: {exc}", file=sys.stderr)
            return 2

        if not is_blocked:
            meta = fetch_issue_meta(repo, issue)
            print(
                f"[wait_for_unblock] ✅  Issue #{issue} unblocked after "
                f'{elapsed:.0f}s ({attempt} poll(s)).  "{meta.get("title", "")}"'
            )
            trigger_path = write_trigger(trigger_dir, repo, issue, meta)
            print(f"[wait_for_unblock] Trigger written: {trigger_path}")
            return 0

        # Check timeout *before* sleeping — so we don't overshoot
        if timeout > 0 and elapsed + interval > timeout:
            print(
                f"[wait_for_unblock] ⏱  Timeout after {elapsed:.0f}s — #{issue} still has {blocked_label!r}.",
                file=sys.stderr,
            )
            return 1

        print(
            f"[wait_for_unblock] 🔒  #{issue} still blocked "
            f"(poll {attempt}, elapsed {elapsed:.0f}s). "
            f"Next check in {interval}s…"
        )
        time.sleep(interval)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Poll a GitHub issue until status:blocked is removed.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--issue", type=int, required=True, help="Issue number to monitor")
    parser.add_argument("--interval", type=int, default=300, help="Poll interval in seconds (default: 300)")
    parser.add_argument("--timeout", type=int, default=0, help="Max total wait in seconds, 0=infinite (default: 0)")
    parser.add_argument("--repo", type=str, default=None, help="owner/repo (default: auto-detected from git remote)")
    parser.add_argument(
        "--trigger-dir",
        type=Path,
        default=Path(".tmp/triggers"),
        help="Trigger file directory (default: .tmp/triggers)",
    )
    parser.add_argument(
        "--blocked-label",
        type=str,
        default=BLOCKED_LABEL_DEFAULT,
        help=f"Label that signals blocked state (default: {BLOCKED_LABEL_DEFAULT})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print resolved config and exit")
    args = parser.parse_args(argv)

    repo = args.repo or get_repo_from_git()
    if not repo:
        print(
            "[wait_for_unblock] ERROR: could not detect repo from git remote. Use --repo owner/repo.",
            file=sys.stderr,
        )
        sys.exit(2)

    if args.dry_run:
        print("[wait_for_unblock] DRY RUN — no polling will occur")
        print(f"  repo:          {repo}")
        print(f"  issue:         #{args.issue}")
        print(f"  blocked-label: {args.blocked_label}")
        print(f"  interval:      {args.interval}s")
        print(f"  timeout:       {'infinite' if args.timeout == 0 else str(args.timeout) + 's'}")
        print(f"  trigger-dir:   {args.trigger_dir}")
        sys.exit(0)

    print(
        f"[wait_for_unblock] Watching {repo}#{args.issue} for removal of "
        f"{args.blocked_label!r} every {args.interval}s "
        f"({'no timeout' if args.timeout == 0 else 'timeout ' + str(args.timeout) + 's'})"
    )
    sys.exit(
        poll(
            repo=repo,
            issue=args.issue,
            interval=args.interval,
            timeout=args.timeout,
            trigger_dir=args.trigger_dir,
            blocked_label=args.blocked_label,
        )
    )


if __name__ == "__main__":
    main()

# `wait\_for\_unblock`

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
    uv run python scripts/wait_for_unblock.py --issue 60 --repo EndogenAI/dogma
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

## Usage

```bash
    uv run python scripts/wait_for_unblock.py --issue 60
    uv run python scripts/wait_for_unblock.py --issue 60 --interval 60 --timeout 3600
    uv run python scripts/wait_for_unblock.py --issue 60 --repo EndogenAI/dogma
    uv run python scripts/wait_for_unblock.py --issue 60 --dry-run
```

<!-- hash:7340330d8b58b32c -->

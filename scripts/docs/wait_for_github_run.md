# `wait\_for\_github\_run`

Wait for GitHub Actions run to complete and return exit code matching conclusion.

Polls GitHub Actions run status at regular intervals until completion or timeout.
Useful for CI workflows where the agent must wait for a build to finish before
proceeding (e.g., after pushing a commit, before merging a PR).

Usage:
    uv run python scripts/wait_for_github_run.py <run-id> [--timeout-secs 150] [--repo EndogenAI/dogma]

Arguments:
    run-id              GitHub Actions run ID (e.g., from `gh run list` output)
    --timeout-secs      Maximum wait time in seconds (default: 150 = 2.5 minutes)
    --repo              Repository in format owner/repo (default: EndogenAI/dogma)
    --interval-secs     Poll interval in seconds (default: 5)

Exit Codes:
    0                   Run completed with conclusion="success"
    1                   Run completed with conclusion="failure" or timeout reached
    2                   Run not found or invalid run ID

Examples:
    # Wait for most recent CI run on current branch
    uv run python scripts/wait_for_github_run.py $(gh run list --limit 1 -q '.[0].databaseId')

    # Wait for a specific run with 5-minute timeout
    uv run python scripts/wait_for_github_run.py 22890618155 --timeout-secs 300

Environment:
    Requires `gh` CLI with appropriate GitHub token in GITHUB_TOKEN or via `gh auth`.

## Usage

```bash
    uv run python scripts/wait_for_github_run.py <run-id> [--timeout-secs 150] [--repo EndogenAI/dogma]
```

<!-- hash:a62bb494cf3988dc -->

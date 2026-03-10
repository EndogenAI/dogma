"""scripts/pr_review_reply.py

Post replies to GitHub PR inline review comments and resolve review threads.

Purpose:
    Automates the post-review response loop: after fixing issues raised in a PR
    review, this script posts a reply on each inline comment (referencing the fix
    commit) and marks the thread as resolved. Eliminates the manual click-through
    on GitHub's UI.

    Supports three modes:
      - Single reply: --reply-to <comment-id> --body <text>
      - Single resolve: --resolve <thread-node-id>
      - Batch: --batch <json-file>  (reply + resolve in one pass)

Batch JSON format:
    A JSON array where each entry may have any combination of:
      {
        "reply_to": <int comment database ID>,   // post a reply
        "body":     <string>,                    // reply text (required with reply_to)
        "resolve":  <string thread node ID>      // resolve the thread
      }

    Entries without "reply_to" but with "resolve" will only resolve (no reply posted).
    Entries with "reply_to" but without "resolve" will only post a reply (no resolve).

Inputs:
    --pr <num>           PR number. Defaults to the active PR detected via `gh pr view`.
    --repo <owner/repo>  Repository. Defaults to current repo via `gh repo view`.
    --reply-to <id>      Single-reply mode: comment database ID to reply to.
    --body <text>        Reply body text (required with --reply-to).
    --resolve <id>       Single-resolve mode: GraphQL node ID of the thread to resolve.
    --batch <file>       Path to a JSON file containing an array of batch operations.

Outputs:
    stdout: confirmation lines for each action taken.
    stderr: warnings and errors.

Exit codes:
    0  All requested operations succeeded.
    1  One or more operations failed.

Usage examples:
    # Reply to a single comment
    uv run python scripts/pr_review_reply.py --pr 15 --reply-to 2899252947 --body "Fixed in abc1234."

    # Resolve a single thread
    uv run python scripts/pr_review_reply.py --pr 15 --resolve PRRT_kwDORfkAR85yvrwz

    # Batch from a JSON file (reply + resolve in one pass)
    uv run python scripts/pr_review_reply.py --pr 15 --batch .tmp/review-replies.json

    # Get comment IDs and thread node IDs for a PR (useful for building the batch file)
    # gh api repos/<owner>/<repo>/pulls/<num>/comments --jq '.[] | {id, path, line}'
    # gh api graphql -f query='{repository(owner:"o",name:"r"){
    #   pullRequest(number:N){reviewThreads(first:20){nodes{
    #     id isResolved comments(first:1){nodes{databaseId}}}}}}}'
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from capability_gate import requires_capability, set_agent_context

# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------


def gh(*args: str, input: str | None = None) -> tuple[int, str, str]:
    """Run a `gh` CLI command. Returns (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["gh", *args],
        input=input,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def detect_repo() -> str:
    """Return 'owner/repo' for the current directory via `gh repo view`."""
    code, out, err = gh("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")
    if code != 0:
        print(f"ERROR: could not detect repo: {err}", file=sys.stderr)
        sys.exit(1)
    return out


@requires_capability("github_api")
def post_reply(repo: str, pr: int, comment_id: int, body: str) -> bool:
    """Post a reply to an inline review comment. Returns True on success."""
    payload = json.dumps({"in_reply_to": comment_id, "body": body})
    code, out, err = gh(
        "api",
        f"repos/{repo}/pulls/{pr}/comments",
        "--input",
        "-",
        "--jq",
        ".id",
        input=payload,
    )
    if code == 0:
        print(f"  REPLIED  comment {comment_id} -> new comment id {out}")
        return True
    print(f"  ERROR    reply to {comment_id}: {err}", file=sys.stderr)
    return False


@requires_capability("github_api")
def resolve_thread(thread_node_id: str) -> bool:
    """Resolve a PR review thread by its GraphQL node ID. Returns True on success."""
    mutation = json.dumps(
        {
            "query": (
                "mutation($id: ID!) {  resolveReviewThread(input: {threadId: $id}) {    thread { isResolved }  }}"
            ),
            "variables": {"id": thread_node_id},
        }
    )
    code, out, err = gh(
        "api",
        "graphql",
        "--input",
        "-",
        "--jq",
        ".data.resolveReviewThread.thread.isResolved",
        input=mutation,
    )
    if code == 0 and out == "true":
        print(f"  RESOLVED {thread_node_id}")
        return True
    print(
        f"  ERROR    resolve {thread_node_id}: {err or out}",
        file=sys.stderr,
    )
    return False


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------


def run_batch(ops: list[dict], repo: str, pr: int) -> int:
    """Execute a list of batch operations. Returns number of failures."""
    failures = 0
    for i, op in enumerate(ops):
        reply_to = op.get("reply_to")
        body = op.get("body", "")
        resolve = op.get("resolve")

        if reply_to is not None:
            if not body:
                print(
                    f"  SKIP  entry {i}: 'reply_to' requires a non-empty 'body'",
                    file=sys.stderr,
                )
                failures += 1
                continue
            if not post_reply(repo, pr, int(reply_to), body):
                failures += 1

        if resolve:
            if not resolve_thread(resolve):
                failures += 1

        if reply_to is None and not resolve:
            print(
                f"  SKIP  entry {i}: no 'reply_to' or 'resolve' key found",
                file=sys.stderr,
            )

    return failures


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    # Set agent context (GitHub operations require github_api capability)
    set_agent_context("github")

    parser = argparse.ArgumentParser(
        description="Post replies to PR inline review comments and resolve threads.",
        epilog="Exit 0 = all operations succeeded. Exit 1 = one or more failures.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--pr",
        type=int,
        metavar="<num>",
        default=None,
        help="PR number. Defaults to active PR detected via `gh pr view`.",
    )
    parser.add_argument(
        "--repo",
        metavar="<owner/repo>",
        default=None,
        help="Repository in owner/repo format. Defaults to current repo.",
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--reply-to",
        type=int,
        metavar="<comment-id>",
        help="Comment database ID to reply to (single-reply mode).",
    )
    mode.add_argument(
        "--resolve",
        metavar="<thread-node-id>",
        help="GraphQL node ID of the review thread to resolve (single-resolve mode).",
    )
    mode.add_argument(
        "--batch",
        metavar="<json-file>",
        help="Path to a JSON file containing an array of reply/resolve operations.",
    )

    parser.add_argument(
        "--body",
        metavar="<text>",
        default=None,
        help="Reply body text. Required with --reply-to.",
    )

    args = parser.parse_args()

    # Resolve repo and PR
    repo = args.repo or detect_repo()
    pr = args.pr
    if pr is None:
        code, out, err = gh("pr", "view", "--json", "number", "--jq", ".number")
        if code != 0:
            print(f"ERROR: could not detect active PR: {err}", file=sys.stderr)
            sys.exit(1)
        pr = int(out)

    print(f"repo={repo}  pr={pr}\n")
    failures = 0

    if args.reply_to is not None:
        if not args.body:
            print("ERROR: --body is required with --reply-to.", file=sys.stderr)
            sys.exit(1)
        if not post_reply(repo, pr, args.reply_to, args.body):
            failures += 1

    elif args.resolve:
        if not resolve_thread(args.resolve):
            failures += 1

    else:  # --batch
        batch_path = Path(args.batch)
        if not batch_path.exists():
            print(f"ERROR: batch file not found: {batch_path}", file=sys.stderr)
            sys.exit(1)
        try:
            ops = json.loads(batch_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"ERROR: invalid JSON in {batch_path}: {exc}", file=sys.stderr)
            sys.exit(1)
        if not isinstance(ops, list):
            print("ERROR: batch JSON must be an array.", file=sys.stderr)
            sys.exit(1)
        failures = run_batch(ops, repo, pr)

    if failures:
        print(f"\n{failures} operation(s) failed.", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

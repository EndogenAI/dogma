# `pr\_review\_reply`

scripts/pr_review_reply.py

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

## Usage

```bash
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
```

<!-- hash:305f98eafecce684 -->

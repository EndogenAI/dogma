---
name: pr-review-reply
description: |
  Encodes the post-review response loop using scripts/pr_review_reply.py: reply to inline PR comments referencing the fix commit, then resolve threads. USE FOR: responding to GitHub PR review comments after fixing the raised issues; batch-reply-and-resolve in one pass; obtaining comment IDs and thread node IDs from the GitHub API. DO NOT USE FOR: authoring the initial PR description (use the GitHub agent); requesting a new review before replies are posted; re-opening resolved threads.
argument-hint: "PR number"
---

# PR Review Reply

This skill enacts the *Algorithms Before Tokens* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md): repetitive post-review response workflows are encoded as a script and executed deterministically, not performed manually through the UI with repeated token burn per comment. The post-review loop is governed by [`AGENTS.md`](../../../AGENTS.md) § Verify-After-Act for Remote Writes. When this skill and those documents conflict, the primary documents take precedence.

---

## 1. Three Modes

The script supports three modes of operation:

| Mode | When to use | Command |
|------|-------------|---------|
| Single reply | One comment to address | `--reply-to <id> --body <text>` |
| Single resolve | One thread to close without reply | `--resolve <thread-node-id>` |
| Batch (preferred) | Multiple comments or resolve-without-reply in one pass | `--batch <json-file>` |

**Always use batch mode when addressing more than one comment.** It is more reliable than sequential single calls and produces a single audit trail.

---

## 2. Single Reply

```bash
uv run python scripts/pr_review_reply.py --pr <num> --reply-to <comment-id> --body "Fixed in <sha>."
```

For multi-line reply bodies, use batch mode with a JSON file instead of `--body` — shell quoting and backtick interpolation cause `gh` to misbehave with multi-line text.

---

## 3. Single Resolve

```bash
uv run python scripts/pr_review_reply.py --pr <num> --resolve <thread-node-id>
```

This resolves the thread without posting a reply. Use only when the comment does not warrant a reply (e.g., a nit that was silently fixed).

---

## 4. Batch Mode (Preferred)

Write a JSON array to a temp file and pass it with `--batch`:

```bash
# Write the batch file (use a file tool — never heredoc)
# Example contents: .tmp/<branch>/review-replies.json

uv run python scripts/pr_review_reply.py --pr <num> --batch .tmp/<branch>/review-replies.json
```

**Batch JSON format** — each entry may contain any combination of `reply_to`, `body`, and `resolve`:

```json
[
  {
    "reply_to": 12345678,
    "body": "Fixed in abc1234 — moved validation to the call site.",
    "resolve": "PRRT_kwDORfkAR85yvrwz"
  },
  {
    "resolve": "PRRT_kwDORfkAR85yvrwz_another"
  },
  {
    "reply_to": 87654321,
    "body": "Agreed — renamed to match the convention."
  }
]
```

- Entry with both `reply_to` and `resolve`: posts the reply, then resolves the thread.
- Entry with only `resolve`: resolves the thread without posting a reply.
- Entry with only `reply_to`: posts a reply without resolving.

---

## 5. Get Comment IDs

To build the batch file, first retrieve comment database IDs:

```bash
gh api repos/<owner>/<repo>/pulls/<num>/comments \
  --jq '.[] | {id, path, line, body: .body[:80]}'
```

The `id` field is the integer database ID used for `reply_to`.

---

## 6. Get Thread Node IDs

Thread node IDs (for `resolve`) require the GraphQL API:

```bash
gh api graphql -f query='{
  repository(owner:"<owner>", name:"<repo>") {
    pullRequest(number: <num>) {
      reviewThreads(first: 20) {
        nodes {
          id
          isResolved
          comments(first: 1) {
            nodes { databaseId body }
          }
        }
      }
    }
  }
}'
```

The `id` field in each `reviewThreads.nodes` entry is the thread node ID (`PRRT_kwDO...`) used for `--resolve`.

---

## 7. Verify After Posting

After posting replies, verify the last reply was recorded correctly:

```bash
gh api repos/<owner>/<repo>/pulls/<num>/comments/<comment-id>/replies \
  --jq '.[-1].body[:80]'
```

Zero output or an error means the reply did not post. Re-run the batch entry for that comment.

---

## 8. Request Re-Review After All Replies

After all comments have been addressed and threads resolved:

```bash
gh pr review <num> --request-review @github-copilot
```

Do not request re-review until all threads are resolved — unresolved threads indicate outstanding feedback.

---

## Guardrails

- **Never pass multi-line reply bodies via `--body "..."`** on the command line — use `--batch` with a JSON file.
- **Never use heredoc writes to create the JSON batch file** — use `create_file` or `replace_string_in_file` tools.
- **Always verify after posting** — zero exit from the script is not confirmation that the reply posted successfully.
- Do not request re-review until all flagged threads are resolved.

# PR Review Response Workflow

**Governing Axiom**: [Algorithms Before Tokens](../../MANIFESTO.md#2-algorithms-before-tokens) — the post-review triage and response cycle is encoded as a deterministic workflow, not performed interactively per PR.

**Related Skills**:
- [pr-review-triage](../../.github/skills/pr-review-triage/SKILL.md) — classify and prioritise review comments
- [pr-review-reply](../../.github/skills/pr-review-reply/SKILL.md) — batch-post replies and resolve threads

**When to Use**: After any PR receives a review with actionable comments (blockers, suggestions, nits, questions).

---

## Overview

```
Receive Review → Triage Comments → Fix Issues → Build Batch Reply → Post Replies → Merge
```

**Key principle**: Never post replies one-by-one. Batch all responses into a single API call to minimize token churn and auditing overhead.

---

## Step 1: Read the Review

Fetch all comments (inline + top-level):

```bash
# Inline comments
gh api repos/EndogenAI/dogma/pulls/<PR_NUM>/comments \
  --jq '.[] | {id, path, line, body, author: .user.login}'

# Top-level review summary
gh pr view <PR_NUM> --json reviews \
  --jq '.reviews[] | {state, body, author: .author.login}'
```

**What to extract**:
- Comment ID or thread node ID
- File path (for inline comments)
- Full text of the comment
- Comment state (APPROVED, CHANGES_REQUESTED, COMMENTED)

---

## Step 2: Classify Each Comment

| Class | Signal | Action |
|-------|--------|--------|
| **Blocking** | `CHANGES_REQUESTED` state OR comment identifies correctness/security/contract violation | Must fix before merge |
| **Suggestion** | `COMMENTED` state + proposes improvement | Strongly recommended |
| **Nit** | Prefix "nit:" in body OR style/wording preference | Optional; acknowledge if fixing |
| **Question** | Ends with `?` OR asks for clarification | Reply required; code fix optional |

**Anti-pattern**: Treating nits and questions as blockers. They require acknowledgement (reply), not necessarily code changes.

---

## Step 3: Priority-Order Fixes

Fix in this sequence to unblock merge:

```
1. Blocking (all of them)
    ↓
2. Suggestions (high-impact ones)
    ↓
3. Nits (optional; skip if time-constrained)
    ↓
4. Questions (reply; no fix unless answer reveals a gap)
```

**Per-file batching**: Group related fixes by file to minimize commit churn. Example:

```
Commit 1: fix(scripts/validate_adr.py) — docstring + error handling (blocks 2 comments)
Commit 2: chore(docs/guides/…) — reword sections (suggestion + nit)
Commit 3: test(test_*.py) — add coverage (question answer)
```

---

## Step 4: Build Batch Reply File

After all fixes are committed, create a JSON batch file (never heredoc):

**Format**: `[{ reply_to, body, resolve }, ...]`

```bash
cat > /tmp/<PR>_reviews.json << 'BATCH_EOF'
[
  {
    "reply_to": 12345678,
    "body": "Fixed in abc1234 — added error handling for empty input.",
    "resolve": "PRRT_kwDO…"
  },
  {
    "reply_to": 87654321,
    "body": "Good point. Clarification: we use yaml.safe_load for security. See updated docstring."
  },
  {
    "resolve": "PRRT_kwDO…_nit"
  }
]
BATCH_EOF
```

Where:
- `reply_to` = comment ID (from Step 1)
- `body` = reply text (reference commit SHA if fixing code)
- `resolve` = thread node ID (for resolving; optional; use with or without reply)

---

## Step 5: Post Replies & Resolve

Use the [`pr-review-reply`](../../.github/skills/pr-review-reply/SKILL.md) skill in batch mode:

```bash
uv run python scripts/pr_review_reply.py \
  --pr <PR_NUM> \
  --batch /tmp/<PR>_reviews.json
```

**Validation (Tier 0)**:
```bash
test -s /tmp/<PR>_reviews.json && \
  file /tmp/<PR>_reviews.json | grep -q "UTF-8" && \
  echo "File valid"
```

**Verification (Tier 1)** — After posting, confirm all replies appeared:
```bash
gh pr view <PR_NUM> --json comments \
  --jq '.comments[-3:] | .[] | "ID: \(.id), Author: \(.author.login), Time: \(.createdAt[:10])"'
```

---

## Step 6: Request Re-Review (if needed)

After posting replies, if there were blocking changes, dismiss the old review and request a fresh one:

```bash
# Dismiss old review
gh api repos/EndogenAI/dogma/pulls/<PR_NUM>/reviews/<REVIEW_ID>/dismissals \
  -f message="Fixed in commits [list]. Ready for re-review."

# Request new review (optional; maintainer may auto-re-review)
# Note: There is no built-in gh pr request-review; use the GitHub UI or API
```

---

## Step 7: Wait & Merge

- Monitor CI: `gh run list --limit 3`
- Once CI passes and re-review approves: `gh pr merge <PR_NUM> --squash` or `--rebase`
- Confirm merge: `git log --oneline main -1` should show your squashed commit

---

## Orchestrator Workflow Integration

When the Orchestrator receives a PR that needs review replies:

1. **Set marker**: Write `## PR Review Response` to session scratchpad
2. **Fetch review**: Use Step 1 above to get all comments
3. **Triage**: Apply Step 2 (classify) and Step 3 (prioritise)
4. **Delegate fixes**: If fixes are non-trivial, delegate to specialist agent (e.g., Executive Scripter)
5. **Batch reply**: After all fixes committed, build JSON batch file (Step 4)
6. **Post replies**: Execute `pr_review_reply.py --batch` (Step 5)
7. **Log**: Update scratchpad with `## PR Review Response Output` and commit SHA list
8. **Wait for approval**: Monitor with `gh pr checks` and re-request review if needed
9. **Merge**: Once CI green + review APPROVED, merge

---

## Rate Limit Mitigation

Use intermittent sleeps between major API calls to avoid rate limiting:

```bash
# Fetch comments (sleep before to space from prior operations)
sleep 2 && gh api repos/EndogenAI/dogma/pulls/<NUM>/comments

# Post batch replies (sleep before batch to wait for API cooldown)
sleep 3 && uv run python scripts/pr_review_reply.py --pr <NUM> --batch /tmp/file.json

# Request re-review (sleep before)
sleep 2 && gh api repos/EndogenAI/dogma/pulls/<NUM>/reviews/<ID>/dismissals
```

---

## References

- [`pr-review-triage` SKILL](../../.github/skills/pr-review-triage/SKILL.md)
- [`pr-review-reply` SKILL](../../.github/skills/pr-review-reply/SKILL.md)
- [AGENTS.md § Verify-After-Act for Remote Writes](../../AGENTS.md#verify-after-act-for-remote-writes)
- [MANIFESTO.md § Algorithms Before Tokens](../../MANIFESTO.md#2-algorithms-before-tokens)

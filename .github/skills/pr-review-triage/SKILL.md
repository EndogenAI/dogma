---
name: pr-review-triage
description: |
  **Mandatory pre-merge gate.** Encodes the PR review triage workflow: retrieve all automated and
  human reviews (Copilot review is auto-triggered on PR open), classify actionable vs. advisory
  comments, prioritise by blocking/suggestion/nit, batch fixes by file, phase them efficiently,
  and use scripts/pr_review_reply.py to reply and resolve threads. A PR must NOT be merged or
  treated as ready to merge until this workflow is complete. USE FOR: reading a new PR review
  and deciding what to fix in which order; preparing a batch reply file after all fixes are
  committed; distinguishing nits to acknowledge from blockers that gate merge. DO NOT USE FOR:
  posting individual replies one-by-one (use pr-review-reply skill instead); authoring the
  initial PR description; re-requesting review before replies are posted.
x-governs:
  - review-response
  - pr-workflow
---

# PR Review Triage

This skill enacts the *Algorithms Before Tokens* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md):
the post-review triage and response workflow is encoded as a repeatable procedure, not re-derived
interactively on each PR. It is governed by [`AGENTS.md`](../../../AGENTS.md)
§ Verify-After-Act for Remote Writes and § Agent Communication. When this skill conflicts
with those documents, the primary documents take precedence.

---

## 1. Governing Constraint

**This skill is a mandatory pre-merge gate.** A PR must not be merged, suggested for merge, or treated as "ready to merge" until this triage workflow has been run and all Blocking comments are resolved. CI passing is a necessary but insufficient condition — reviews must be triaged independently.

**Trigger**: Copilot review is automatically triggered when a PR is opened and on every subsequent push. Do not assume the review is empty — always retrieve it.

Per [`AGENTS.md`](../../../AGENTS.md) § PR Review Triage Gate and § Verify-After-Act for Remote Writes:
- Every reply posted to a review comment is a remote write — Tier 0 validation applies before
  sending.
- Every thread resolved is irreversible — only resolve threads whose change is confirmed
  committed.
- After posting replies, verify with `gh issue view` or `gh pr view` before treating the
  task as complete.

---

## 2. Workflow Overview

```
Read review → Classify comments → Prioritise → Batch fixes by file → Commit fixes
→ Build batch reply file → Post replies and resolve threads → Verify
```

---

## 3. Steps

### Step 0 — Merge Authorization Pre-Check

Before beginning triage (and again before suggesting merge), run `check_merge_authorization.py` to get a structural snapshot of the PR's authorization state:

```bash
uv run python scripts/check_merge_authorization.py <pr_num> --dry-run
```

This prints a full check table (✅/❌) for all four authorization criteria without blocking. Use it to:
- Identify which checks are already passing (no need to re-verify manually)
- Confirm that CI is green, no `CHANGES_REQUESTED` is outstanding, and no non-nit threads are unresolved

After all triage steps complete (Steps 1–7), run without `--dry-run` to get the final authorization verdict:

```bash
uv run python scripts/check_merge_authorization.py <pr_num>
```

Write the result to the scratchpad under `## Merge Authorization — PR #NNN` with the 5-checkbox template from `AGENTS.md` § PR Review Triage Gate. **The final human-gate checkbox must be checked before suggesting merge to the user.**

**Anti-pattern**: Treating `MERGE AUTHORIZED — ...` output as permission to merge without the explicit user "go ahead". The script clears the technical gate; the human confirms the strategic intent.

---

### Step 1 — Read the Review

Retrieve all inline comments and their body text:

```bash
gh api repos/<owner>/<repo>/pulls/<num>/comments \
  --jq '.[] | {id, path, line, body}'
```

Also retrieve any top-level review summary body (separate from inline comments):

```bash
gh pr view <num> --json reviews --jq '.reviews[] | {state, body}'
```

### Step 2 — Classify Each Comment

Assign every comment to exactly one class:

| Class | Definition | Must-fix before merge? |
|-------|-----------|----------------------|
| **Blocking** | Review state is `CHANGES_REQUESTED`; comment identifies a correctness, security, or contract violation | Yes |
| **Suggestion** | Review state is `COMMENTED`; comment proposes an improvement but does not block | Recommended |
| **Nit** | Prefix "nit:" in body; minor style or wording preference | Optional |
| **Question** | Comment ends with `?`; reviewer is asking for clarification only | Reply required; fix optional |

**Anti-pattern**: treating every comment as blocking. Nits and questions do not require code
changes — they require acknowledgement. Conflating classes causes over-engineering and delays
merge.

**Canonical example**:

> Review contains 3 comments:
> - "This will throw a `KeyError` if the dict is empty." → **Blocking** (correctness)
> - "nit: rename `x` to `result` for clarity" → **Nit** (optional)
> - "Why not use `pathlib` here?" → **Question** (clarification)
>
> Fix the KeyError first. Acknowledge the nit in a reply. Answer the question. Merge.

### Step 3 — Prioritise Changes

Fix in this order:

1. **Blocking** — correctness, security, contract violations
2. **Suggestion** — improvements that are clearly better and low-risk
3. **Nit** — only if trivially fast; skip if time-constrained
4. **Question** — reply with clarification; no code change unless the answer reveals a gap

For each fix, commit separately with a descriptive message:

```bash
git add <file>
git commit -m "fix(<scope>): <what was fixed> (addresses PR review comment)"
```

### Step 4 — Batch Fixes by File

Group fixes that target the same file into a single commit. Do not create one commit per
comment — one commit per file (or per logical change spanning files).

**Canonical example**:

> 4 comments touch `scripts/validate_synthesis.py`, 2 touch `docs/research/foo.md`.
> → Commit 1: fix all 4 synthesis validator issues
> → Commit 2: update foo.md for the 2 doc comments
> → 2 commits total, not 6

**Anti-pattern**: one commit per review comment. This produces noisy history and makes
rollbacks difficult.

### Step 5 — Build the Batch Reply File

After all fixes are committed, build a JSON batch file for `scripts/pr_review_reply.py`.
Each entry maps a comment ID to a reply body referencing the fix commit.

Write the batch file using a file tool — **never a heredoc**:

```json
[
  {
    "reply_to": 12345678,
    "body": "Fixed in abc1234 — added a guard for the empty-dict case.",
    "resolve": "PRRT_kwDORfkAR85yvrwz"
  },
  {
    "reply_to": 87654321,
    "body": "Good call — renamed to `result` in the same commit.",
    "resolve": "PRRT_kwDORfkAR85yvrw6"
  },
  {
    "reply_to": 99887766,
    "body": "Using `urllib.request` here to keep the stdlib-only constraint — `pathlib` would not help with URL fetching.",
    "resolve": "PRRT_kwDORfkAR85yvrw7"
  }
]
```

For nits that were skipped: reply with an acknowledgement, do not resolve (leave the thread
open to signal it was seen but deferred):

```json
  {
    "reply_to": 55443322,
    "body": "Noted — deferring the rename for now to keep this PR focused."
  }
```

### Step 6 — Post Replies and Resolve Threads

Use `scripts/pr_review_reply.py` in batch mode. See the
[pr-review-reply skill](../pr-review-reply/SKILL.md) for full usage.

```bash
uv run python scripts/pr_review_reply.py --pr <num> --batch .tmp/<branch>/review-replies.json
```

### Step 7 — Verify

After posting:

```bash
gh pr view <num> --json reviewThreads --jq '.reviewThreads[] | {isResolved, comments: .comments.nodes[0].body[:60]}'
```

Confirm that all blocking and suggestion threads are resolved. Unresolved nit threads are
acceptable. **Zero error output is not confirmation of success** — always verify.

---

## 4. Tools

| Task | Tool / Command |
|------|---------------|
| Retrieve inline comment IDs | `gh api repos/<owner>/<repo>/pulls/<num>/comments` |
| Retrieve thread node IDs | `gh api graphql` — see [pr-review-reply skill](../pr-review-reply/SKILL.md) § Get Thread Node IDs |
| Post replies + resolve threads | `uv run python scripts/pr_review_reply.py --batch <file>` |
| Verify resolution state | `gh pr view <num> --json reviewThreads` |

---

## 5. Examples

### Full triage — 5-comment review

**Setup**: PR #42, 5 inline comments. Reviewer state: `CHANGES_REQUESTED`.

**Classification**:
1. Comment 111 — "exit code is wrong on missing file" → **Blocking**
2. Comment 222 — "consider using `subprocess.run` instead of `os.system`" → **Suggestion**
3. Comment 333 — "nit: trailing whitespace" → **Nit**
4. Comment 444 — "why not pass `--dry-run` here?" → **Question**
5. Comment 555 — "this function is doing too much — consider splitting" → **Suggestion**

**Fix order**:
1. Fix exit code (commit `fix(scripts): return exit 1 on missing file`)
2. Replace `os.system` + split function (commit `fix(scripts): use subprocess.run, extract validate_path()`)
3. Answer question in reply — no code change needed
4. Acknowledge nit — no fix

**Batch reply file**:
```json
[
  {"reply_to": 111, "body": "Fixed in abc1234 \u2014 now exits 1 with a clear message.", "resolve": "PRRT_xxx1"},
  {"reply_to": 222, "body": "Switched to subprocess.run in def2345.", "resolve": "PRRT_xxx2"},
  {"reply_to": 333, "body": "Cleaned up in def2345.", "resolve": "PRRT_xxx3"},
  {"reply_to": 444, "body": "--dry-run is already threaded through from the caller; no change needed."},
  {"reply_to": 555, "body": "Extracted validate_path() in def2345.", "resolve": "PRRT_xxx5"}
]
```

**Result**: 2 fix commits, 1 batch reply call, all blocking/suggestion threads resolved.

---

## 6. Guardrails

### ❌ DO NOT use `gh pr comment` for inline replies

When moving from Step 5 (build batch file) to Step 6 (post replies), **you must use `pr_review_reply.py --batch`**, not `gh pr comment`.

**Wrong**:
```bash
# Posts a top-level comment, orphans it from the review thread
gh pr comment 144 --body "Fixed in abc123"
```

**Correct**:
```bash
# Posts as a threaded reply to the specific comment
uv run python scripts/pr_review_reply.py --pr 144 --batch .tmp/replies.json
```

See [pr-review-reply skill](../pr-review-reply/SKILL.md) § Anti-Patterns for details on why tool substitution breaks scope.

### ❌ DO NOT tag Copilot in reply comments

```bash
# WRONG — creates unwanted secondary Copilot tasks
gh pr comment 144 --body "@github-copilot Fixed in abc123 by doing X"
```

Use `pr_review_reply.py` without tags. The fix commit SHA and explanation speak for themselves.

### ✅ Delegate inline reply posting to `pr_review_reply` skill

Step 6 of this workflow **requires** the [pr-review-reply skill](../pr-review-reply/SKILL.md). Do not attempt inline replies outside that skill's tools.

---
title: "Copilot PR Review Automation"
research_issue: "29"
status: Final
date: 2026-03-07
sources: []
---

# Copilot PR Review Automation

> **Status**: Final
> **Research Question**: Can we programmatically request a review from GitHub Copilot on a pull request, and if so, how?
> **Date**: 2026-03-07

---

## 1. Executive Summary

Copilot PR review cannot be triggered per-PR through any public API. Every mechanism tested against the live `EndogenAI/Workflows` repository — REST reviewer request, `gh` CLI, GraphQL `requestReviews`, and GraphQL node ID lookup — returns an error or a silent no-op. The root cause is that `copilot-pull-request-reviewer` is a GitHub App bot, not a collaborator User, and reviewer request APIs only accept collaborators.

The sole supported automation path is a **repository ruleset** ("Automatically request Copilot code review") accessible under Repository Settings → Rules. This feature is **gated behind GitHub Pro or a public repository**. `EndogenAI/Workflows` is private on a free plan, returning 403 for ruleset creation attempts.

The immediate operational recommendation is to treat the Copilot review re-request as a manual two-second UI click (Reviewers sidebar → ↻). If the repository is made public or the plan is upgraded, a one-time ruleset configuration script replaces the click permanently.

---

## 2. Hypothesis Validation

### H1 — REST API reviewer request works for bot accounts

**Verdict**: REFUTED — bots excluded from collaborator check

Live test on PR #28:

```bash
gh api repos/EndogenAI/Workflows/pulls/28/requested_reviewers \
  --method POST --field reviewers[]="copilot-pull-request-reviewer"
```

**Result**: HTTP 422 "Reviews may only be requested from collaborators." The API does not distinguish between "wrong reviewers" and "bot accounts" — both return the same error. The reviewer APIs are hardcoded to collaborator Users and Teams only.

### H2 — GraphQL `requestReviews` mutation accepts bot node IDs

**Verdict**: REFUTED — bot node type is incompatible

Bot identity confirmed from active PR review record on PR #28:
- Login: `copilot-pull-request-reviewer[bot]`
- Type: `Bot` (not `User`)
- Node ID: `BOT_kgDOCnlnWA`
- App slug: `copilot-pull-request-reviewer`

GraphQL test via `requestReviewsByLogin` (user login): HTTP 200, **silent no-op** — reviewer not added.  
GraphQL test via `requestReviews` with node ID `BOT_kgDOCnlnWA`: **GraphQL NOT_FOUND** — "Could not resolve to User node."

The mutation only resolves `User` nodes. `Bot` nodes are structurally incompatible.

### H3 — CODEOWNERS can list a bot as a required reviewer

**Verdict**: REFUTED — CODEOWNERS syntax does not support bot accounts

CODEOWNERS only accepts `@user` logins and `@org/team` slugs. Adding `@copilot-pull-request-reviewer` produces a validation error. No review is triggered. This path is a dead end.

### H4 — A GitHub Actions workflow step can trigger Copilot review

**Verdict**: REFUTED — no public step or event exists

No `actions/` step or marketplace action initiates Copilot PR review. Rulesets do not expose a webhook that a workflow can call. There is no `workflow_dispatch` or `pull_request` event handler that initiates a Copilot review over any public interface.

### H5 — Repository rulesets can automate Copilot review at policy layer

**Verdict**: CONFIRMED — but gated on plan tier

The GitHub docs confirm one sanctioned automation mechanism: **Repository Settings → Rules → Rulesets → "Automatically request Copilot code review"**. Options once enabled:
- **Review new pushes** — re-triggers Copilot review on every push (closes the re-request gap)
- **Review draft pull requests** — reviews drafts before human review

Ruleset creation via REST API (`POST /repos/{owner}/{repo}/rulesets`) is supported but requires GitHub Pro or a public repo. Live test on `EndogenAI/Workflows`: **HTTP 403** — "Upgrade to GitHub Pro or make this repository public to enable this feature."

---

## 3. Pattern Catalog — Copilot Review Approaches

### P1 — Manual re-request (current baseline)

Click ↻ next to Copilot in the PR Reviewers sidebar after each push. Two seconds. No scripting required. This is the appropriate posture until rulesets are unlocked.

**When to use**: All PRs on the current free / private plan.

### P2 — One-time ruleset configuration (unlocked path)

Requires GitHub Pro (~$4/month) or making the repo public. Once either condition is met, run once:

```bash
gh api --method POST repos/EndogenAI/Workflows/rulesets \
  --input .github/rulesets/auto-copilot-review.json
```

Where `.github/rulesets/auto-copilot-review.json` encodes:

```json
{
  "name": "auto-copilot-review",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [{ "type": "code_review", "parameters": { "require_code_owner_review": false, "required_approving_review_count": 0, "require_last_push_approval": false, "dismiss_stale_reviews_on_push": false, "automatic_copilot_code_review_enabled": true } }]
}
```

After this one-time setup, every push to a PR automatically triggers Copilot review — no per-PR script or UI click needed.

**When to use**: Once GitHub Pro is activated or repo is made public.

### P3 — What NOT to build

A `scripts/request_copilot_review.py` would be a dead-end script on the current plan — it has no working API to call. Once rulesets are unlocked, the correct implementation is the **one-time ruleset configuration** (P2), not a per-PR script. Per-PR scripting is the wrong abstraction for this feature.

---

## 4. Limitations and Trade-offs

| Limitation | Detail |
|------------|--------|
| Bot not a collaborator | `copilot-pull-request-reviewer` is excluded from reviewer APIs by type |
| No public API endpoint | No `requestCopilotReview` in REST or GraphQL schema |
| Rulesets gated on plan | Private free repo → 403; needs GitHub Pro or public repo |
| Re-request has no API | The UI "re-request review" button uses an internal flow; no public API equivalent |
| Copilot review is non-blocking | Copilot only posts `COMMENT` reviews; cannot be a required reviewer blocking merge |

---

## 5. Recommendations for `EndogenAI/Workflows`

1. **Immediate**: Accept manual review re-request as the workflow — document in `docs/guides/github-workflow.md` under PR review conventions.

2. **Near-term decision gate**: Decide whether to (a) upgrade to GitHub Pro or (b) make the repo public. Either unlocks full automation via ruleset. Given the repo contains docs/guides/agents with no secrets, making it public has low risk and no cost.

3. **Do not build** `scripts/request_copilot_review.py` until rulesets are unlocked — it cannot work with the current API.

4. **If/when rulesets unlock**: Create `.github/rulesets/auto-copilot-review.json` and update the GitHub agent workflow to run the one-time setup command.

---

## 6. Documentation Update — `docs/guides/github-workflow.md`

The following should be added to the PR review section of `docs/guides/github-workflow.md`:

### Requesting Copilot Review

Copilot code review is triggered manually via the GitHub PR UI:

1. Open the PR on GitHub.
2. In the **Reviewers** sidebar, click **Copilot**.
3. After each new push, re-request review by clicking the ↻ icon next to Copilot.

There is no `gh` CLI flag or REST/GraphQL API call that programmatically requests a Copilot review on a per-PR basis. The reviewer request APIs (`POST /pulls/{number}/requested_reviewers`) do not accept bot accounts. All forms of API-based automation — REST, GraphQL user login, GraphQL node ID — were live-tested against PR #28 and each returned an error (HTTP 422 or GraphQL NOT_FOUND). See `docs/research/copilot-pr-review-automation.md` for the full test record.

**Automation path (future)**: Enable repository rulesets under Settings → Rules once GitHub Pro or public visibility is available. Setting "Automatically request Copilot code review" + "Review new pushes" replaces the manual ↻ click. See P2 above.

### CI Gate Before Review Request

Before requesting or re-requesting a Copilot review, verify CI is green:

```bash
gh run list --limit 3
```

A failing CI run means the PR is not ready for review. Fix the CI failure first. Common CI failure modes on this repo: lychee non-200 link (add to `.lycheeignore`), ruff format (run `uv run ruff format scripts/ tests/`), validate_synthesis heading requirement.


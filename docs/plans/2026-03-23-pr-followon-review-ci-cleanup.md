---
title: "PR Follow-On Review and CI Cleanup"
status: Draft
branch: feat/recommendation-provenance-sprint
date: 2026-03-23
governing_axiom: "Documentation-First — primary source: docs/guides/workflows.md"
related_prs: [412]
---

# Workplan: PR Follow-On Review and CI Cleanup

**Branch**: `feat/recommendation-provenance-sprint`
**Date**: 2026-03-23
**Orchestrator**: Executive Orchestrator

---

## Objective

If `feat/recommendation-provenance-sprint` still differs from `main`, open a follow-on pull request for the post-merge work that accumulated after merged PR #412, wait for the automatic Copilot review to land, triage and reply to all review comments through the scripted review-response loop, seed a new workflow-codification issue from the live friction observed in this pass, and clear all remaining CI failures until the new PR is merge-ready. If no branch delta remains, skip the PR-dependent phases and limit the session to recording that state plus seeding the workflow-codification issue.

---

## Branch State

- PR #412 is already merged and must be treated as closed history, not the update target for this session.
- There is currently no open PR for `feat/recommendation-provenance-sprint`.
- A follow-on PR is required only if `main..HEAD` still contains branch-only commits at Phase 1 execution time; if the branch no longer differs from `main`, the session short-circuits to issue seeding and/or cleanup rather than opening a duplicate PR.
- Current local untracked artifacts (`apply_output.txt`, `audit_output*.txt`, `docs/sessions/...`) are not part of the follow-on PR unless explicitly added later.

---

## Phase Plan

### Phase 1 — Open Follow-On PR

**Agent**: GitHub
**Deliverables**:
- D1: Branch divergence from `main` verified and recorded
- D2: If branch-only commits still exist, new PR opened from `feat/recommendation-provenance-sprint` to `main`
- D3: If a new PR is opened, PR title/body clearly identify this as the post-#412 follow-on PR
- D4: If a new PR is opened, Copilot review requested or confirmed automatic review trigger state recorded
**Depends on**: Workplan Review APPROVED
**Gate**: `git log main..HEAD` confirms branch-only commits still exist, `gh pr list --state open --head feat/recommendation-provenance-sprint` confirms no duplicate open PR exists, and `gh pr view <new-pr>` confirms the new PR opened successfully
**Status**: ⬜ Not started

### Phase 2 — Wait and Capture Copilot Review

**Agent**: Executive Orchestrator
**Deliverables**:
- D1: 10-minute wait completed after PR open
- D2: Review snapshot captured: top-level Copilot review, inline comments, comment IDs, thread IDs
- D3: Decision recorded whether review arrived or whether one repoll is needed
**Depends on**: Phase 1 complete with new PR opened
**Gate**: Review artifacts for the new PR are captured or a timeout/no-review state is explicitly logged
**Status**: ⬜ Not started

### Phase 3 — Triage, Fix, Reply, Resolve

**Agent**: Executive Docs and/or Executive Scripter, routed by file ownership; GitHub for replies
**Deliverables**:
- D1: All actionable Copilot review comments classified and batched by file
- D2: Required fixes committed and pushed
- D3: `pr_review_reply.py` batch payload created and used to post replies / resolve actionable threads
- D4: Verification that actionable threads are resolved or explicitly deferred with rationale
**Depends on**: Phase 2 complete with review artifacts captured
**Gate**: `gh pr view <new-pr> --json reviewThreads` shows addressed actionable threads resolved; latest fix commits pushed
**Status**: ⬜ Not started

### Phase 4 — Seed Workflow Codification Issue

**Agent**: Executive PM, then GitHub
**Deliverables**:
- D1: New issue created to codify the open-PR -> wait -> inspect Copilot review -> triage/reply -> CI cleanup loop
- D2: Issue includes workflow/skill update scope and any automation/script follow-up discovered during this session
**Depends on**: Phase 3 complete, or Phase 1 complete with no follow-on PR needed
**Gate**: `gh issue view <new-issue>` confirms created issue with labels and deliverables
**Status**: ⬜ Not started

### Phase 5 — CI Failure Cleanup and PR Readiness

**Agent**: CI Monitor; Executive Docs / Executive Scripter / Executive Automator as needed; GitHub for push
**Deliverables**:
- D1: Current failing CI jobs triaged by failure type
- D2: Remaining CI failures fixed and pushed
- D3: Local validations run for the changed surface area
- D4: Latest PR checks green and PR ready for re-review or merge
**Depends on**: Phase 4 complete and follow-on PR exists
**Gate**: `gh run list` / PR checks show green for the latest push
**Status**: ⬜ Not started

---

## Acceptance Criteria

- [ ] Phase 1 records whether the branch still differs from `main`
- [ ] If branch-only commits remain, a new follow-on PR exists for the current branch and is not a duplicate of merged PR #412
- [ ] If a follow-on PR is opened, Copilot review output for the new PR is captured after a 10-minute wait window
- [ ] If a follow-on PR is opened, all actionable Copilot review comments are triaged, fixed or explicitly deferred, replied to, and resolved where appropriate
- [ ] A new issue exists to encode this PR-review response loop into workflows and skills
- [ ] If a follow-on PR is opened, remaining CI failures on that PR are fixed and the latest checks are green

---

## Notes

- Phase 2 is intentionally orchestration-only to preserve context and avoid delegating a passive wait.
- Phase 3 should use the existing scripted reply workflow in `scripts/pr_review_reply.py` and the guidance in `.github/skills/pr-review-triage/SKILL.md` and `.github/skills/pr-review-reply/SKILL.md`.
- Phase 5 should fix only failures that remain on the follow-on PR; do not widen scope to unrelated `main` branch failures.

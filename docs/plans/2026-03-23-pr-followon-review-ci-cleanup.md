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
**Status**: ✅ Complete — PR #431 opened; workplan committed in 31a59c0

### Phase 2 — Wait and Capture Copilot Review

**Agent**: Executive Orchestrator
**Deliverables**:
- D1: 10-minute wait completed after PR open
- D2: Review snapshot captured: top-level Copilot review, inline comments, comment IDs, thread IDs
- D3: Decision recorded whether review arrived or whether one repoll is needed
**Depends on**: Phase 1 complete with new PR opened
**Gate**: Review artifacts for the new PR are captured or a timeout/no-review state is explicitly logged
**Status**: ✅ Complete — Copilot review landed with 7 inline comments on PR #431

### Phase 3 — Triage, Fix, Reply, Resolve

**Agent**: Executive Docs and/or Executive Scripter, routed by file ownership; GitHub for replies
**Deliverables**:
- D1: All actionable Copilot review comments classified and batched by file
- D2: Required fixes committed and pushed
- D3: `pr_review_reply.py` batch payload created and used to post replies / resolve actionable threads
- D4: Verification that actionable threads are resolved or explicitly deferred with rationale
**Depends on**: Phase 2 complete with review artifacts captured
**Gate**: `gh pr view <new-pr> --json reviewThreads` shows addressed actionable threads resolved; latest fix commits pushed
**Status**: ✅ Complete — all 7 comments fixed (e11994c), replied, and resolved; CI green

### Phase 4 — Seed Workflow Codification Issue

**Agent**: Executive PM, then GitHub
**Deliverables**:
- D1: New issue created to codify the open-PR -> wait -> inspect Copilot review -> triage/reply -> CI cleanup loop
- D2: Issue includes workflow/skill update scope and any automation/script follow-up discovered during this session
**Depends on**: Phase 3 complete, or Phase 1 complete with no follow-on PR needed
**Gate**: `gh issue view <new-issue>` confirms created issue with labels and deliverables
**Status**: ✅ Complete — Issue #432 created

### Phase 5 — CI Failure Cleanup and PR Readiness

**Agent**: CI Monitor; Executive Docs / Executive Scripter / Executive Automator as needed; GitHub for push
**Deliverables**:
- D1: Current failing CI jobs triaged by failure type
- D2: Remaining CI failures fixed and pushed
- D3: Local validations run for the changed surface area
- D4: Latest PR checks green and PR ready for re-review or merge
**Depends on**: Phase 4 complete and follow-on PR exists
**Gate**: `gh run list` / PR checks show green for the latest push
**Status**: ✅ Complete — broken cache link fixed (807c3d3); CI green (run 23504949810)

---

### Phase 6 — Retrofit Patch Migration

**Agent**: Executive Scripter (apply patches + code change), then GitHub (commit)
**Deliverables**:
- D1: All 37 patches in `data/retrofit-patches/` applied — `uv run python scripts/apply_retrofit_patch.py` (without `--dry-run`) exits 0; subsequent `--dry-run` shows zero "would patch" lines
- D2: Default `--patch-dir` in `scripts/apply_retrofit_patch.py` updated from `"data" / "retrofit-patches"` to `".cache" / "retrofit-patches"`; CLI help text updated to match
- D3: All 37 `.yml` files moved from `data/retrofit-patches/` to `.cache/retrofit-patches/`
- D4: `.gitignore` confirmed to exclude `.cache/`; rule added if absent
- D5: Tests updated to reference new default path; `uv run pytest tests/ -x -m "not slow and not integration" -q` passes
- D6: `data/retrofit-patches/` removed from tracked files (`git ls-files data/retrofit-patches/` returns empty)
- D7: Changes committed — `chore(scripts): apply retrofit patches and move to .cache`
**Depends on**: Phase 5 complete
**Gate**: `git ls-files data/retrofit-patches/` empty; `.cache/retrofit-patches/*.yml | wc -l` = 37; `--dry-run` shows 0 pending; tests pass
**Status**: ⬜ Not started

---

### Phase 7 — Secondary Research Sprint Skill Authoring

**Agent**: Executive Docs
**Description**: Author the `secondary-research-sprint` skill **before** any research is executed. This is the Documentation-First gate for Phase 8.
**Deliverables**:
- D1: `.github/skills/secondary-research-sprint/SKILL.md` created with YAML frontmatter and all five numbered workflow steps:
  1. **Issue Enrichment** — fetch issue URL(s), update issue body to D4 template via `gh issue edit --body-file`
  2. **Corpus Check** — search `docs/research/` for related existing synthesis (Endogenous-First before scouting)
  3. **Scout** — web search + fetch/cache via `scripts/fetch_source.py`; check `.cache/sources/` first
  4. **Synthesize** — produce D4 `docs/research/<slug>.md` with all required headings
  5. **Review + Archive** — validate via `validate_synthesis.py`, commit, close issue
- D2: Skill cross-referenced in AGENTS.md `Agent Skills` section
- D3: `uv run python scripts/validate_agent_files.py --skills` passes
- D4: All internal links use `../../../` relative paths (no `/`-rooted paths)
**Depends on**: Phase 6 complete
**Gate**: Skill file exists; validator passes; AGENTS.md updated
**Status**: ⬜ Not started

---

### Phase 7 Review — Review Gate

**Agent**: Review
**Deliverables**: Verdict `APPROVED` or `REQUEST CHANGES` in scratchpad under `## Phase 7 Review Output`; if APPROVED, skill + AGENTS.md update committed and pushed
**Depends on**: Phase 7 complete
**Gate**: Verdict recorded; Phase 8 does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 8 — Issue #433: Secondary Research Sprint (First Live Test)

**Agent**: Executive Researcher (using `secondary-research-sprint` skill)
**Description**: Execute the new skill against Issue #433 ("Agentic Platform Engineering with GitHub Copilot") as its first live test case. Issue body currently contains only a title + URL.
**Deliverables**:
- D1: Issue #433 body updated via `gh issue edit 433 --body-file` to D4 template before scouting
- D2: Corpus check complete — `docs/research/` searched; findings in scratchpad
- D3: Target URL + additional sources fetched and cached in `.cache/sources/`
- D4: D4 synthesis at `docs/research/<slug>.md` with YAML frontmatter and all five required headings
- D5: `uv run python scripts/validate_synthesis.py docs/research/<slug>.md` exits 0
**Depends on**: Phase 7 Review APPROVED
**Gate**: Synthesis doc exists and validates; issue #433 body has `## Acceptance Criteria`; cache contains source(s)
**Status**: ⬜ Not started

---

### Phase 8 Review — Review Gate

**Agent**: Review
**Deliverables**: Verdict `APPROVED` or `REQUEST CHANGES` in scratchpad under `## Phase 8 Review Output`; if APPROVED, synthesis doc committed, `Closes #433` in commit body (not manual `gh issue close`), pushed
**Depends on**: Phase 8 complete
**Gate**: Verdict recorded; Phase 9 does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 9 — Research Issue Enrichment Automation

**Agent**: Executive Automator (script + workflow), Executive Scripter (tests)
**Description**: Recurring automation to detect un-enriched `type:research` issues and auto-apply the Issue Enrichment step.
**Deliverables**:
- D1: `scripts/enrich_research_issues.py` with: GitHub API query for open `type:research` issues, detection heuristic (body ≤ 300 chars **and** no `## Acceptance Criteria`), `--dry-run` / `--apply` flags (dry-run default), D4 template enrichment, docstring, exit codes 0/1/2
- D2: `tests/test_enrich_research_issues.py` covering: happy path, skip (already-enriched), dry-run produces zero writes, each exit-code path
- D3: `.github/workflows/enrich-research-issues.yml` scheduled weekly (Monday 09:00 UTC) + `workflow_dispatch`
- D4: `scripts/README.md` updated with script entry
- D5: `uv run pytest tests/test_enrich_research_issues.py -x -q` passes; ruff clean
**Depends on**: Phase 8 Review APPROVED
**Gate**: Script + tests + workflow exist; dry-run exits 0; README updated; ruff clean
**Status**: ⬜ Not started

---

### Phase 9 Review — Review Gate

**Agent**: Review
**Deliverables**: Verdict `APPROVED` or `REQUEST CHANGES` in scratchpad under `## Phase 9 Review Output`; if APPROVED, all automation artifacts committed and pushed; CI green
**Depends on**: Phase 9 complete
**Gate**: Verdict recorded; CI green after push
**Status**: ⬜ Not started

---

## Acceptance Criteria

- [ ] Phase 1 records whether the branch still differs from `main`
- [ ] If branch-only commits remain, a new follow-on PR exists for the current branch and is not a duplicate of merged PR #412
- [ ] If a follow-on PR is opened, Copilot review output for the new PR is captured after a 10-minute wait window
- [ ] If a follow-on PR is opened, all actionable Copilot review comments are triaged, fixed or explicitly deferred, replied to, and resolved where appropriate
- [ ] A new issue exists to encode this PR-review response loop into workflows and skills
- [ ] If a follow-on PR is opened, remaining CI failures on that PR are fixed and the latest checks are green
- [ ] All 37 retrofit patches applied; `data/retrofit-patches/` removed from tracked files; patches at `.cache/retrofit-patches/`; `apply_retrofit_patch.py` default updated; tests pass
- [ ] `.github/skills/secondary-research-sprint/SKILL.md` exists with all 5 workflow steps; validator passes; cross-referenced in AGENTS.md
- [ ] Phase 7 Review `APPROVED` recorded before Phase 8 began
- [ ] Issue #433 body updated to D4 template before scouting; synthesis committed; `validate_synthesis.py` passes; issue closed on merge
- [ ] Phase 8 Review `APPROVED` recorded before Phase 9 began
- [ ] `scripts/enrich_research_issues.py` exists with `--dry-run`/`--apply`, docstring, tests (all exit codes); workflow scheduled weekly + `workflow_dispatch`; README updated; ruff clean; CI green

---

## Notes

- Phase 2 is intentionally orchestration-only to preserve context and avoid delegating a passive wait.
- Phase 3 should use the existing scripted reply workflow in `scripts/pr_review_reply.py` and the guidance in `.github/skills/pr-review-triage/SKILL.md` and `.github/skills/pr-review-reply/SKILL.md`.
- Phase 5 should fix only failures that remain on the follow-on PR; do not widen scope to unrelated `main` branch failures.

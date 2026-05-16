# Workplan: Dogma Reveal Readiness

**Branch**: `feat/reveal-readiness-may18` (merges into `main`)
**Date**: 2026-05-15
**Orchestrator**: Executive Orchestrator

---

## Objective

Prepare the dogma repository for public reveal on May 18, 2026. This sprint addresses 17 readiness audit findings from the May 13 Scout review, covering README enhancements, Sprint 23 reference cleanup, telemetry data archival, community issue management, documentation audits, and cross-repo integration with AccessiTech blog and product page. Critical path: blog code block graphics (May 17) and product page cross-linking (May 18) must complete on time to support reveal coordination.

**Timeline**: May 15-18, 2026 (3-day sprint)
**Scope**: 11 issues (#63-#73 in consulting repo)
**Critical dependencies**: 
- #67 (blog graphics) gates May 18 blog publication
- #73 (product page links) gates May 18 reveal coordination

---

## Phase Plan

### Phase 0 — Branch Setup ⬜
**Agent**: Executive Scripter
**Deliverables**:
- Create `feat/reveal-readiness-may18` branch off dogma/main
- Commit: (already complete — branch created during planning)

**Depends on**: nothing
**CI**: N/A
**Status**: ✅ Complete

### Phase 0 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**: 
- Verdict: APPROVED or REQUEST CHANGES
- Output logged to scratchpad under `## Phase 0 Review Output`

**Depends on**: Phase 0 deliverables committed
**Status**: Not started

---

### Phase 1 — README Enhancements ⬜
**Agent**: Executive Docs
**Deliverables**:
- Add 30-second plain-English hook from May 18 blog to dogma/README.md (Closes #63)
- Add eAI logo placeholder (text-based badge, not PNG) to dogma/README.md (Closes #64)
- Add high-level roadmap callout (Q3 2026 1.0 stability goal, one paragraph) to dogma/README.md (Closes #68)
- Commit: `docs(readme): add plain-English hook, logo placeholder, and roadmap callout for May 18 reveal`

**Depends on**: Phase 0 Review APPROVED
**CI**: Tests (ruff, lychee), Auto-validate
**Status**: Not started

**Hook source**: AccessiTech blog `introducing-endogenai-dogmamcp.md` (consulting repo has the text)
**Logo approach**: Text-based badge (e.g., "EndogenAI | DogmaMCP") until user exports PNG asset post-reveal
**Roadmap content**: Draft "Q3 2026 → 1.0 stability; expanding toolkit coverage; contributor onboarding" (consult consulting repo for any existing roadmap docs first)

### Phase 1 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**: 
- Verdict: APPROVED or REQUEST CHANGES
- Output logged to scratchpad under `## Phase 1 Review Output`

**Depends on**: Phase 1 deliverables committed
**Status**: Not started

---

### Phase 2 — Cleanup, Maintenance & Research Prerequisites ⬜
**Agent**: Executive Scripter (cleanup, archive), Executive Docs (getting-started audit), Research Scout (best practices)
**Deliverables**:
- Remove all "Sprint 23" references from dogma repo (5+ files: mcp_server/README.md, docs/mcp/api-reference.md, docs/mcp/mcp-ecosystem-architecture.md, docs/governance/recommendations-schema.md, docs/research/webmcp-browser-integration.md) (Closes #65)
- Archive 800 synthetic seed records using `scripts/migrate_tool_calls.py --dry-run` then live execution (Closes #66)
- Quick audit of `docs/guides/getting-started.md` for first-adopter blockers (Closes #69)
- Research: Good-first-issue best practices for governance frameworks (Closes #72)
- Research findings → scratchpad under `## Phase 2 Output — Research Scout`
- Commit 1: `chore(cleanup): remove Sprint 23 internal references across 5+ files`
- Commit 2: `chore(telemetry): archive 800 synthetic seed records pre-reveal`
- Commit 3 (if changes needed): `docs(getting-started): address first-adopter blockers`

**Depends on**: Phase 1 Review APPROVED
**CI**: Tests, Auto-validate
**Status**: Not started

**Cleanup scope**: Comprehensive (user confirmed). Human review gate: agent proposes changes, user validates before commit.
**Archive validation**: Run `--dry-run` first; verify output before live execution.
**Getting-started audit**: Flag anything a first-time adopter would find blocking/confusing. Quick pass, not full rewrite.
**Research scope** (N-1 pattern): Findings inform Phase 3 (issue management). Scout should focus on: what makes a good first issue in governance/policy repos (not typical CRUD apps), OSS community best practices, CNCF/Linux Foundation patterns.

### Phase 2 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**: 
- Verdict: APPROVED or REQUEST CHANGES
- Output logged to scratchpad under `## Phase 2 Review Output`

**Depends on**: Phase 2 deliverables committed
**Status**: Not started

---

### Phase 3 — Community & Issue Management ⬜
**Agent**: Executive PM
**Deliverables**:
- Audit all 42 open dogma issues; produce YAML-formatted recommendations (close/keep/label) (Closes #70)
- User reviews YAML list → approves before any closes execute
- Apply approved closes/labels using `gh issue edit` batch operations
- Identify 3-5 "good-first-issue" candidates using Phase 2 research findings (Closes #71)
- Apply "good-first-issue" label to selected issues
- Commit: `chore(issues): triage 42 open issues and designate good-first-issue candidates`

**Depends on**: Phase 2 Review APPROVED, Phase 2 research findings
**CI**: N/A (GitHub operations)
**Status**: Not started

**Triage authority**: Option B (user confirmed) — agent proposes, user approves before execution.
**Good-first-issue criteria**: Informed by Phase 2 Research Scout findings. Likely candidates: docs-only, small script extensions, synthesis tasks < 1 day for newcomers.

### Phase 3 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**: 
- Verdict: APPROVED or REQUEST CHANGES
- Output logged to scratchpad under `## Phase 3 Review Output`

**Depends on**: Phase 3 deliverables committed
**Status**: Not started

---

### Phase 4 — Cross-Repo Integration (CRITICAL PATH) ⬜
**Agent**: AT - Frontend Developer (#67, #73), Comms Strategist (coordination)
**Deliverables**:
- AccessiTech: Replace/supplement blog code blocks with graphics + simplify for lay audience (Closes #67) ⚠️ May 17 HARD DEADLINE
- AccessiTech: Add blog links to eAI product page (EndogenAI.tsx edits) (Closes #73) ⚠️ May 18 HARD DEADLINE
- Commit (AccessiTech): `feat(blog): add graphics and simplify code blocks for lay audience comprehension`
- Commit (AccessiTech): `feat(product): add cross-links to EndogenAI blog posts`

**Depends on**: Phase 3 Review APPROVED
**CI**: AccessiTech test suite, build validation
**Status**: Not started

**CRITICAL NOTES**:
- #67 is May 17 requirement — user is actively working on graphics May 15-17
- #73 requires TypeScript edits (EndogenAI.tsx), estimated 1-2hrs
- Both issues gate May 18 public reveal timeline
- Coordinate with user on graphics completion status before committing
- Verify AccessiTech is on feature branch before any file writes (cross-repo branch enforcement)

### Phase 4 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**: 
- Verdict: APPROVED or REQUEST CHANGES
- Output logged to scratchpad under `## Phase 4 Review Output`

**Depends on**: Phase 4 deliverables committed
**Status**: Not started

---

### Phase 5 — Final Review & Session Close ⬜
**Agent**: Executive Orchestrator
**Deliverables**:
- Fleet integration check: `uv run python scripts/check_fleet_integration.py --dry-run` (no new agents/skills expected, but verify)
- Update all 11 issue bodies with completion checkboxes: `gh issue edit <num> --body-file <path>`
- Post progress comments on all 11 issues with commit SHAs and workplan reference
- Archive session: `uv run python scripts/prune_scratchpad.py --force`
- Write `## Session Summary` to scratchpad
- Push feat/reveal-readiness-may18 branch
- Open PR with all 11 `Closes #NN` lines in description

**Depends on**: Phase 4 Review APPROVED
**CI**: Full CI suite (tests, lychee, validate-synthesis, validate-agent-files)
**Status**: Not started

---

## Acceptance Criteria

- [ ] All 5 phases complete and committed
- [ ] All 11 issues (#63-#73) have completion checkboxes updated
- [ ] Progress comments posted on all 11 issues
- [ ] CI passing on feat/reveal-readiness-may18 branch
- [ ] PR opened with all `Closes #NN` lines
- [ ] May 17 deadline met: #67 (blog graphics) committed
- [ ] May 18 deadline met: #73 (product page links) committed
- [ ] User manually merges feat/reveal-readiness-may18 to dogma/main before May 18 reveal
- [ ] Session scratchpad archived and `## Session Summary` written

## PR Description Template

<!-- Copy to PR description when opening the PR -->

**Reveal Readiness Sprint — May 18, 2026**

This PR addresses all 17 readiness audit findings from the May 13 Scout review, preparing the dogma repository for public reveal on May 18, 2026.

**README Enhancements**:
- Add 30-second plain-English hook from reveal blog
- Add eAI logo placeholder (text badge)
- Add high-level roadmap callout (Q3 2026 1.0 stability goal)

**Cleanup & Maintenance**:
- Remove all Sprint 23 internal references (5+ files)
- Archive 800 synthetic telemetry seed records
- Audit getting-started.md for first-adopter blockers

**Community & Issue Management**:
- Triage 42 open issues (close stale, label actionable)
- Designate 3-5 "good-first-issue" candidates

**Cross-Repo Integration** (CRITICAL PATH):
- AccessiTech blog: Graphics + simplified code blocks for lay audience
- AccessiTech product page: Cross-links to EndogenAI blog posts

**Timeline**: May 15-18, 2026 (3-day sprint)
**Critical deadlines**: 
- May 17: Blog graphics (#67)
- May 18: Product page cross-linking (#73)

Closes #63, Closes #64, Closes #65, Closes #66, Closes #67, Closes #68, Closes #69, Closes #70, Closes #71, Closes #72, Closes #73

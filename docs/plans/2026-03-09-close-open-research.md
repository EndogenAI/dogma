# Workplan: Close Out Open Research Issues

**Date**: 2026-03-09
**Branch**: `research/current-open-research`
**Milestone**: Open Research Closure Sprint
**Governing axiom**: Endogenous-First — all research docs assessed before new work begins
**Primary endogenous source**: `docs/research/OPEN_RESEARCH.md` + GitHub issue list

---

## Objective

Close all currently open `type:research` GitHub issues by either:
1. Verifying that an existing **Final** research doc satisfies all gate deliverables and closing the issue
2. Escalating deferred/blocked issues with an explicit blocker comment
3. Completing the product-discovery draft (#45) sprint to Final status
4. Resolving the three OQ-10 follow-up questions (OQ-10-1, OQ-10-2, OQ-10-3) tracked in `OPEN_RESEARCH.md`
5. Relabelling #132 correctly (implementation not research)

---

## Context: Issue Audit Results

### Issues Where Research Doc is Already Final → Close After Verification

| Issue | Title | Research Doc | Status |
|-------|-------|-------------|--------|
| [#13](https://github.com/EndogenAI/Workflows/issues/13) | Episodic and Experiential Memory | `episodic-memory-agents.md` | Final |
| [#14](https://github.com/EndogenAI/Workflows/issues/14) | AIGNE AFS Context Governance Layer Evaluation | `aigne-afs-evaluation.md` | Final |
| [#72](https://github.com/EndogenAI/Workflows/issues/72) | Context-sensitive axiom amplification (OQ-VE-2) | `epigenetic-tagging.md` | Final |
| [#74](https://github.com/EndogenAI/Workflows/issues/74) | LLM behavioral testing for value fidelity (OQ-VE-4) | `llm-behavioral-testing.md` | Final |
| [#76](https://github.com/EndogenAI/Workflows/issues/76) | XML structuring in `handoffs.prompt` fields (OQ-12-4) | `xml-agent-instruction-format.md` §11 | Resolved per OPEN_RESEARCH.md 2026-03-09 |
| [#83](https://github.com/EndogenAI/Workflows/issues/83) | Encoding external product/client values | `external-value-architecture.md` | Final |
| [#131](https://github.com/EndogenAI/Workflows/issues/131) | Cognee Library Adoption | Blocked by #13 + local compute | Defer |

### Issues Requiring Active Work

| Issue | Title | Status | Effort |
|-------|-------|--------|--------|
| [#45](https://github.com/EndogenAI/Workflows/issues/45) | Research: Product Definition | `endogenai-product-discovery.md` draft — needs sprint | XL |
| [#132](https://github.com/EndogenAI/Workflows/issues/132) | Product User Research Infrastructure | Implementation (R1–R6), not research | Relabel → `type:chore` |

### OQ-10 Follow-Up Questions (Tracked in OPEN_RESEARCH.md, No Dedicated Issue)

| ID | Question |
|----|----------|
| OQ-10-1 | Compression ratio by task type — at what compression level does precision-critical context degrade? |
| OQ-10-2 | Minimal viable `.tmp/` scratchpad isolation without new infrastructure |
| OQ-10-3 | Evaluator-optimizer convergence criteria for synthesis tasks |

---

## Phase Plan

### Phase 1 — Issue Closure Sweep (Quick Wins)

**Agent**: Executive Orchestrator (direct action — git/gh operations only)
**Deliverables**:
- Issues #13, #14, #72, #74, #76, #83 closed via `gh issue close` with closing comment summarising the research deliverable reference
- Issue #131 commented as deferred (blocker: #13 closure + local compute baseline) — leave open
- `OPEN_RESEARCH.md` updated: move #13, #14, #72, #74, #76, #83 to Completed table; mark OQ-12-4 closed (already annotated as resolved, verify)
- Issue #132 relabelled to `type:chore`, `area:docs` — remove `type:research`

**Depends on**: Nothing — all research docs already Final
**Gate**: Phase 1 Review does not start until all closes are committed
**Status**: ✅ Complete (2026-03-10, commit 1e361a5)

**Checklist**:
- [ ] Verify each issue's gate deliverables against the research doc (spot-check 2–3 D-items per issue)
- [ ] Write closing comment body files in `/tmp/` for each issue (`--body-file`)
- [ ] `gh issue close` each of #13, #14, #72, #74, #76, #83
- [ ] Comment on #131 noting blocker
- [ ] `gh label` update #132 to type:chore
- [ ] Update `OPEN_RESEARCH.md` — move resolved items to Completed table
- [ ] `git add -A && git commit`

### Phase 1 Review — Review Gate

**Agent**: Review
**Deliverables**: `## Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 1 commits
**Gate**: Phase 2 does not start until APPROVED
**Status**: ⬜ Not started

---

### Phase 2 — OQ-10 Resolution Sprint

**Agent**: Executive Researcher → Research Scout fleet
**Deliverables**:
- `docs/research/OPEN_RESEARCH.md` OQ-10-1, OQ-10-2, OQ-10-3 each marked RESOLVED with a ≤ 200-word resolution summary
- Findings appended to `docs/research/agent-fleet-design-patterns.md` or a new `docs/research/agent-fleet-aq-followups.md` if scope warrants a separate doc
- Acceptance criteria: each OQ has a concrete answer, a source citation, and a stated recommendation

**Depends on**: Phase 1 APPROVED
**Gate**: Phase 2 Review does not start until research doc committed and OQ entries updated
**Status**: ⬜ Not started

**Per-OQ scope:**

#### OQ-10-1 — Compression ratio by task type
- Survey Anthropic token-budget guidance; check `docs/research/agent-fleet-design-patterns.md` for any prior data
- Produce a table of recommended compression ratios by task type (code synthesis, research, docs editing, scripting)
- Note: AGENTS.md already states ≤ 2,000 tokens at handoff; this refines that into per-type floors

#### OQ-10-2 — Minimal viable scratchpad isolation
- Review current section-scoped write convention in AGENTS.md
- Survey whether any existing script or VS Code task constrains agent write scope
- Produce: minimum enforcement mechanism recommendation (instruction-only vs. script guard vs. filename convention)

#### OQ-10-3 — Evaluator-optimizer convergence for synthesis
- Review `docs/research/llm-behavioral-testing.md` for any synthesis-specific stopping criteria
- Cross-reference Reviewer agent definition in `.github/agents/`
- Produce: 2–3 concrete stopping conditions for the Reviewer loop on synthesis documents

### Phase 2 Review — Review Gate

**Agent**: Review
**Deliverables**: `## Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 2 deliverables committed
**Gate**: Phase 3 does not start until APPROVED
**Status**: ⬜ Not started

---

### Phase 3 — Product Definition (#45) Sprint to Final

**Agent**: Executive Researcher (using existing `endogenai-product-discovery.md` draft as seed)
**Deliverables**:
- `docs/research/endogenai-product-discovery.md` status updated to `Final` (or flagged with explicit gap list if full Final is not achievable this sprint)
- All gate deliverables in issue #45 body checked off or explicitly deferred with rationale
- Issue #45 closed or commented with clear "what remains" if the epic scope exceeds this sprint

**Depends on**: Phase 2 APPROVED (OQ-10 context informs product definition research posture)
**Gate**: Phase 3 Review gate before any close

**Note on scope**: Issue #45 is `effort:xl` and `priority:critical`. The intent here is to advance the status of the product-discovery doc to Final and close the research sub-tasks. The downstream implementation work (Adopt wizard, Greenfield wizard per gate deliverables 4–9) should be split into separate `type:chore` or `type:feature` issues at close time.

**Status**: ⬜ Not started

### Phase 3 Review — Review Gate

**Agent**: Review
**Deliverables**: `## Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 3 deliverables committed
**Gate**: Phase 4 does not start until APPROVED
**Status**: ⬜ Not started

---

### Phase 4 — #132 Implementation Planning (Chore Relabel + Issue Breakdown)

**Agent**: Executive PM
**Deliverables**:
- Issue #132 relabelled `type:chore` (done in Phase 1) + body updated with 6 concrete child issues for R1–R6, or converted to a milestone/epic with sub-issues
- Each R1–R6 recommendation from `product-research-and-design.md` has a corresponding actionable issue with `type:chore` and appropriate priority

**Depends on**: Phase 3 APPROVED
**Gate**: Phase 4 Review before session close
**Status**: ⬜ Not started

### Phase 4 Review — Review Gate

**Agent**: Review
**Deliverables**: `## Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 4 deliverables committed
**Gate**: Session does not close until APPROVED
**Status**: ⬜ Not started

---

### Phase 5 — Session Close + OPEN_RESEARCH.md Final Update

**Agent**: Executive Orchestrator (direct)
**Deliverables**:
- `OPEN_RESEARCH.md` fully reflects current state: all resolved items in Completed table, remaining open items clearly marked with their status, OQ-10 resolutions annotated
- Session summary written to scratchpad
- `prune_scratchpad.py --force` run
- All changes pushed to `research/current-open-research` branch
- PR opened or existing PR updated

**Depends on**: Phase 4 APPROVED
**Status**: ⬜ Not started

---

## Acceptance Criteria

- [ ] All issues with a Final research doc are closed (#13, #14, #72, #74, #76, #83)
- [ ] Issue #131 has a blocker comment and is explicitly deferred
- [ ] Issue #132 is relabelled `type:chore` with child issues for R1–R6
- [ ] OQ-10-1, OQ-10-2, OQ-10-3 each have a written resolution in `OPEN_RESEARCH.md`
- [ ] `endogenai-product-discovery.md` is Final (or gap-listed with explicit follow-up issues)
- [ ] Issue #45 is closed or has a clear "what remains beyond research" issue list
- [ ] `OPEN_RESEARCH.md` Completed table reflects all newly closed issues
- [ ] All phase commits pushed to branch
- [ ] CI passes

---

## CI Checks Required

- Tests (fast subset: `uv run pytest tests/ -x -m "not slow and not integration" -q`)
- validate_synthesis on any modified research docs
- ruff check/format on any modified scripts

---

## Related Issues

#13, #14, #45, #72, #74, #76, #83, #131, #132

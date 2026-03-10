# Workplan: Programmatic Governors — Shifting Behavioral Constraints out of Tokens

**Branch**: `feat/programmatic-governors`
**Date**: 2026-03-10
**Orchestrator**: Executive Orchestrator
**Governing axiom**: Algorithms Before Tokens — programmatic enforcement supersedes token-level instructions

---

## Objective

Act on a session insight: behavioral guardrails encoded as text instructions (AGENTS.md, user memory) are unreliable against weight-level pretraining defaults. The heredoc failure mode — AI generating a known-broken pattern despite explicit text rules — is the canonical evidence. This workplan encodes that insight as: (1) a pre-commit runtime governor, (2) a research synthesis, and (3) seeded issues for deeper investigation and fleet-wide audit.

---

## Phase Plan

### Phase 1 — Pre-commit Governor Hook ✅

**Agent**: Direct (Orchestrator)
**Deliverables**:
- [x] Add `no-heredoc-writes` pygrep hook to `.pre-commit-config.yaml` blocking `cat >> file << 'EOF'` and `cat > file << 'EOF'` patterns in committed shell and Python files; excludes `validate_agent_files.py` and its tests
- [x] Verified clean against all `scripts/*.py` and `tests/*.py`
**Commit**: `8095621`
**Depends on**: nothing
**Gate**: Phase 1 Review does not start until hook is committed and verified
**Status**: ✅ Complete

---

### Phase 1 Review — Review Gate ✅

**Agent**: Review
**Deliverables**: `## Phase 1 Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 1 committed
**Gate**: Phase 2 does not start until APPROVED
**Status**: ✅ Complete — APPROVED

---

### Phase 2 — Session Synthesis Research Doc ✅

**Agent**: Executive Docs (delegated)
**Deliverables**:
- [x] `docs/research/programmatic-governors.md` — D4 synthesis; Status: Draft; `validate_synthesis.py` PASS
**Commit**: `48a9a95` (doc), `f49d3e0` (research_issue updated to #151)
**Depends on**: Phase 1 APPROVED
**Gate**: Phase 2 Review does not start until doc is committed
**Status**: ✅ Complete

---

### Phase 2 Review — Review Gate ✅

**Agent**: Review
**Deliverables**: `## Phase 2 Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 2 committed
**Gate**: Phase 3 does not start until APPROVED
**Status**: ✅ Complete — APPROVED

---

### Phase 3 — Seed GitHub Issues ✅

**Agent**: Direct (Orchestrator — gh CLI)
**Deliverables**:
- [x] Issue [#150](https://github.com/EndogenAI/Workflows/issues/150): Research — Shell PREEXEC hook as project-scoped command governor (`priority:medium`, `type:research`, milestone 9)
- [x] Issue [#151](https://github.com/EndogenAI/Workflows/issues/151): Deep Research — Strategies for shifting AI behavioral constraints from tokens to deterministic code (`priority:high`, `type:research`, milestone 9)
- [x] Issue [#152](https://github.com/EndogenAI/Workflows/issues/152): Chore — Audit fleet guardrails for programmatic enforcement opportunities (`priority:medium`, `type:chore`, `status:blocked`, milestone 9, blocked-by #151)
**Depends on**: Phase 2 APPROVED
**Gate**: Phase 4 does not start until issues are verified
**Status**: ✅ Complete

---

### Phase 4 — Research Sprint: #150 (Shell PREEXEC Governor) ✅

**Agent**: Executive Researcher → Research Scout → Research Synthesizer → Research Reviewer → Research Archivist
**Issue**: [#150](https://github.com/EndogenAI/Workflows/issues/150)
**Deliverables**:
- [x] `docs/research/shell-preexec-governor.md` — D4 synthesis; Status: Final
- [x] Answers all 5 research questions in #150:
  1. Can zsh `preexec` / bash `DEBUG` trap reliably intercept heredoc-containing commands?
  2. Failure modes (subshell escaping, piped commands, eval, process substitution)
  3. Delivery via `.envrc` (direnv) as project-scoped activation
  4. False-positive rate on legitimate shell operations
  5. Existing tooling already hooking this intercept point
- [x] Code examples for both zsh and bash variants
- [x] #150 closed
**Depends on**: Phase 3 complete
**Gate**: Phase 4 Review does not start until doc is committed and #150 closed
**Status**: ✅ Complete

---

### Phase 4 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 4 Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 4 deliverables committed
**Gate**: Phase 5 does not start until APPROVED
**Status**: ⬜ Not started

---

### Phase 5 — Deep Research Sprint: #151 (Shifting Constraints from Tokens) ⬜

**Agent**: Executive Researcher → Research Scout (broad) → Research Synthesizer → Research Reviewer → Research Archivist
**Issue**: [#151](https://github.com/EndogenAI/Workflows/issues/151)
**Deliverables**:
- [ ] `docs/research/shifting-constraints-from-tokens.md` — D4 synthesis; Status: Final
- [ ] Covers all 6 research questions in #151:
  1. Taxonomy of AI behavioral constraint classes — which are programmatically enforceable vs. token-dependent
  2. Enforcement stack map — intervention points between LLM tool call and execution
  3. Prior art survey: Constitutional AI, RLHF, tool-use guardrails, agent sandboxing
  4. Empirical evidence for token-level instruction degradation (attention dropout, context position effects)
  5. Cost-benefit per enforcement tier
  6. Governor design patterns (allowlist/blocklist, intercept/audit, hard/soft)
- [ ] Pattern Catalog with `**Canonical example**:` and `**Anti-pattern**:` blocks
- [ ] Recommendations that directly feed the fleet audit (#152)
- [ ] `programmatic-governors.md` Status updated from Draft → Final (or superseded note added)
- [ ] #151 closed
**Depends on**: Phase 4 APPROVED (findings from PREEXEC research feed the enforcement stack map)
**Gate**: Phase 5 Review does not start until doc is committed and #151 closed
**Status**: ⬜ Not started

---

### Phase 5 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 5 Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 5 deliverables committed
**Gate**: Phase 6 (fleet audit) unlocks after APPROVED — update #152 to remove `status:blocked`
**Status**: ⬜ Not started

---

## Acceptance Criteria

- [x] `.pre-commit-config.yaml` contains `no-heredoc-writes` hook, CI-verified
- [x] `docs/research/programmatic-governors.md` exists with valid D4 frontmatter and all required headings
- [x] 3 GitHub issues created with correct labels and milestone
- [x] Issue #152 has explicit blocked-by reference to #151 in its body
- [x] All Phase 1–3 changes committed and pushed to `feat/programmatic-governors`
- [x] `docs/research/shell-preexec-governor.md` — D4, Status: Final; #150 closed
- [ ] `docs/research/shifting-constraints-from-tokens.md` — D4, Status: Final; #151 closed
- [ ] #152 `status:blocked` label removed and fleet audit sprint can begin

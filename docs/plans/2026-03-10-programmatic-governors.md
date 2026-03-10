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

### Phase 4 Review — Review Gate ✅

**Agent**: Review
**Deliverables**: `## Phase 4 Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 4 deliverables committed
**Gate**: Phase 5 does not start until APPROVED
**Status**: ✅ Complete — APPROVED

---

### Phase 5 — Deep Research Sprint: #151 (Shifting Constraints from Tokens) ✅

**Agent**: Executive Researcher → Research Scout (broad) → Research Synthesizer → Research Reviewer → Research Archivist
**Issue**: [#151](https://github.com/EndogenAI/Workflows/issues/151)
**Deliverables**:
- [x] `docs/research/shifting-constraints-from-tokens.md` — D4 synthesis; Status: Final
- [x] Covers all 6 research questions in #151:
  1. Taxonomy of AI behavioral constraint classes — which are programmatically enforceable vs. token-dependent
  2. Enforcement stack map — intervention points between LLM tool call and execution
  3. Prior art survey: Constitutional AI, RLHF, tool-use guardrails, agent sandboxing
  4. Empirical evidence for token-level instruction degradation (attention dropout, context position effects)
  5. Cost-benefit per enforcement tier
  6. Governor design patterns (allowlist/blocklist, intercept/audit, hard/soft)
- [x] Pattern Catalog with `**Canonical example**:` and `**Anti-pattern**:` blocks (6 patterns, 5 anti-patterns documented)
- [x] Recommendations that directly feed the fleet audit (#152) — P0/P1/P2 guardrail priorities with effort estimates
- [x] `programmatic-governors.md` Status updated from Draft → Final with forward reference to deeper synthesis
- [x] #151 closed via commit message and gh issue close
**Depends on**: Phase 4 APPROVED (findings from PREEXEC research feed the enforcement stack map)
**Commits**: `1e59c2e` (initial), `844cdeb` (workplan), `7e4a2ce` (endogenous sources remediation — REQUIRED for Phase 5 Review APPROVED)
**Gate**: Phase 5 Review completed — APPROVED after remediation
**Status**: ✅ Complete

---

### Phase 5 Review — Review Gate ✅

**Agent**: Review → Research Archivist (remediation) → Review (re-check)
**Deliverables**: 
- [x] validate_synthesis.py: PASS on both `docs/research/shifting-constraints-from-tokens.md` and `docs/research/programmatic-governors.md`
- [x] All 6 research questions answered with evidence-grounded depth
- [x] Pattern Catalog includes 6 canonical patterns + 5 documented anti-patterns with code examples
- [x] Recommendations concrete and actionable for fleet audit (#152) with P0/P1/P2 priorities
- [x] Endogenous-First axiom compliance: MANIFESTO.md citations (§1, §2, §3) + AGENTS.md + Phase 2 synthesis + values-encoding.md
- [x] Commits: `1e59c2e` (initial) + `7e4a2ce` (endogenous sources remediation), both validated
- [x] #151 closed via `gh issue close 151 --comment "..."`
**Remediation note**: Initial Review returned REQUEST CHANGES (missing endogenous sources). Archivist added 4-citation Endogenous Sources subsection + body MANIFESTO.md citations. Re-review APPROVED.
**Depends on**: Phase 5 deliverables committed + remediation validated
**Gate**: Phase 6 (fleet audit #152) unlocks after successful remediation re-check
**Status**: ✅ Complete — APPROVED (after remediation cycle)

---

---

### Phase 9 — bash-preexec Decision (#161, effort:xs) ✅

**Agent**: Executive Docs
**Issue**: [#161](https://github.com/EndogenAI/Workflows/issues/161)
**Deliverables**:
- [x] `docs/decisions/ADR-007-bash-preexec.md` committed — status: Accepted; decision: adopt for API surface consistency, retain DEBUG trap + `kill -INT` for blocking
- [x] #161 closed
**Commit**: `d011958`
**Depends on**: Phase 7 APPROVED
**Gate**: Phase 9 Review does not start until ADR committed and #161 closed
**Status**: ✅ Complete

---

### Phase 9 Review — Review Gate ✅

**Agent**: Review
**Deliverables**: `## Phase 9 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 9 committed
**Gate**: Phase 10 does not start until APPROVED
**Status**: ✅ Complete — APPROVED

---

### Phase 10 — Governor B Implementation (#159, effort:m) ✅

**Agent**: Executive Scripter
**Issue**: [#159](https://github.com/EndogenAI/Workflows/issues/159)
**Deliverables**:
- [x] `.envrc` — `export PREEXEC_GOVERNOR_ENABLED=1` (single line)
- [x] `docs/guides/governor-setup.md` — developer one-time setup guide: zsh ZLE `accept-line` wrapper (broad pattern + allowlist), bash `DEBUG` trap + `kill -INT`, bash-preexec sourcing note (refs ADR-007), `direnv allow` activation step, acceptance test
- [x] #159 closed
**Commit**: `e7f8299`
**Depends on**: Phase 9 APPROVED
**Gate**: Phase 10 Review does not start until both files committed and #159 closed
**Status**: ✅ Complete

---

### Phase 10 Review — Review Gate ✅

**Agent**: Review
**Deliverables**: `## Phase 10 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 10 committed
**Gate**: Phase 11 does not start until APPROVED
**Status**: ✅ Complete — APPROVED

---

### Phase 11 — Documentation Finish (#160 + #162, effort:s + xs) ✅

**Agent**: Executive Docs (both sub-phases — different files, commit together)
**Issues**: [#160](https://github.com/EndogenAI/Workflows/issues/160), [#162](https://github.com/EndogenAI/Workflows/issues/162)
**Deliverables**:
- [x] `AGENTS.md` — new `## Programmatic Governors` section (between `## Security Guardrails` and `## Guardrails`): names Governor A (pre-commit pygrep), Governor B (runtime shell, `PREEXEC_GOVERNOR_ENABLED=1`), cites `docs/guides/governor-setup.md`; #160 closed
- [x] `env-validator.agent.md` — new checklist item: `PREEXEC_GOVERNOR_ENABLED` env-var check, ⚠️ warning only (not ❌ failure — CI runners are non-interactive), refs `docs/guides/governor-setup.md`; #162 closed
- [x] `uv run python scripts/validate_agent_files.py --all` passes (49/49)
**Commit**: `37ac9af` (docs); `0a7cb6f`, `5883573` (ruff fixes for pre-existing capability_gate.py / test_capability_gate.py lint errors)
**Depends on**: Phase 10 APPROVED
**Gate**: Phase 11 Review does not start until all committed, both issues closed, and validator passes
**Status**: ✅ Complete

---

### Phase 11 Review — Review Gate ✅

**Agent**: Review → push → CI
**Deliverables**: APPROVED; all changes pushed; CI green (`5883573` — Tests: success)
**Depends on**: Phase 11 committed
**Gate**: Session complete
**Status**: ✅ Complete — APPROVED — CI green

---

## Acceptance Criteria

- [x] `.pre-commit-config.yaml` contains `no-heredoc-writes` hook, CI-verified
- [x] `docs/research/programmatic-governors.md` exists with valid D4 frontmatter and all required headings
- [x] 3 GitHub issues created with correct labels and milestone
- [x] Issue #152 has explicit blocked-by reference to #151 in its body
- [x] All Phase 1–3 changes committed and pushed to `feat/programmatic-governors`
- [x] `docs/research/shell-preexec-governor.md` — D4, Status: Final; #150 closed
- [x] `docs/research/shifting-constraints-from-tokens.md` — D4, Status: Final; commit `1e59c2e` includes `closes #151`
- [x] #152 `status:blocked` label to be removed after Phase 5 Review gates (unblocks fleet audit sprint)
- [x] Phase 6 (Terminal File I/O Linting): T2 ruff rule + AGENTS.md documentation complete
- [x] Phase 7 (Runtime Capability Gates): T4 decorator pattern + audit logging complete
- [x] P0 action items #154, #155 closed

---

## P0 Phase Plan (Action Items from Phase 5 Research)

### Phase 6 — #154 (T2 Static Linting: ruff rule for terminal file I/O) ✅

**Agent**: Executive Scripter
**Deliverables**:
- [x] Add ruff rule to pyproject.toml flagging `run_in_terminal` with I/O redirection (>, >>, pipes)
- [x] Integrate rule into .pre-commit-config.yaml (`no-terminal-file-io-redirect` hook)
- [x] Run ruff check on scripts/ and tests/ — zero violations
- [x] Update AGENTS.md with terminal I/O enforcement documentation + Programmatic-First cites
- [x] #154 closed via commit reference
**Commits**: `298efc9` (rule), `78163e4` (AGENTS.md documentation)
**Gate**: Phase 6 Review — ✅ APPROVED

---

### Phase 6 Review — Review Gate ✅

**Verdict**: ✅ APPROVED
All D2 (static linting) and documentation criteria met. T1→T2 shift grounded in research. Programmatic-First principle properly cited.

---

### Phase 7 — #155 (T4 Runtime Gate: API capability access control) ✅

**Agent**: Executive Automator
**Deliverables**:
- [x] Design runtime capability gate decorator: @requires_capability("github_api")
- [x] Implement audit logging middleware for API access
- [x] Gate GitHub agent API calls; audit-log + reject other agents
- [x] Add comprehensive test suite with @pytest.mark.io markers
- [x] #155 closed via commit reference
**Commits**: `7a30bf1` (initial), `534f0de` (cites + markers), `bb36a3b` (final markers)
**Gate**: Phase 7 Review — ✅ APPROVED

---

### Phase 7 Review — Review Gate ✅

**Verdict**: ✅ APPROVED
All T4 (execution-time enforcement) and documentation criteria met. MANIFESTO.md §2 and Programmatic-First properly cited. Audit logging operational. Test suite complete with markers.

---

## P0 Consolidation ✅

All P0 action items complete and APPROVED:
- [x] Terminal file I/O: T1 text instruction → T2 static linting + pre-commit hook
- [x] API capability gating: T1 documented → T4 runtime decorator + audit logging
- [x] Both issues #154, #155 closed
- [x] All commits pushed to `feat/programmatic-governors`
- [x] Ready for P1 (medium-term) action items (#156, #157) or PR review

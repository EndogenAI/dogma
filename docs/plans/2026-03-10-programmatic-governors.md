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

### Phase 1 — Pre-commit Governor Hook ⬜

**Agent**: Direct (Orchestrator — small file edit)
**Deliverables**:
- [ ] Add `no-heredoc-writes` pygrep hook to `.pre-commit-config.yaml` blocking `cat >> file << 'EOF'` and `cat > file << 'EOF'` patterns in committed shell and Python files
- [ ] Verify `uv run pre-commit run --all-files` passes
**Depends on**: nothing
**Gate**: Phase 1 Review does not start until hook is committed and verified
**Status**: ⬜ Not started

---

### Phase 1 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 1 Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 1 committed
**Gate**: Phase 2 does not start until APPROVED
**Status**: ⬜ Not started

---

### Phase 2 — Session Synthesis Research Doc ⬜

**Agent**: Executive Docs (delegated)
**Deliverables**:
- [ ] `docs/research/programmatic-governors.md` — D4 synthesis on shifting AI behavioral constraints from tokens to deterministic governors; includes the pre-commit / PREEXEC / DEBUG-trap taxonomy; Status: Draft
**Depends on**: Phase 1 APPROVED
**Gate**: Phase 2 Review does not start until doc is committed
**Status**: ⬜ Not started

---

### Phase 2 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 2 Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 2 committed
**Gate**: Phase 3 does not start until APPROVED
**Status**: ⬜ Not started

---

### Phase 3 — Seed GitHub Issues ⬜

**Agent**: Direct (Orchestrator — gh CLI)
**Deliverables**:
- [ ] Issue A: Research — Shell PREEXEC hook as project-scoped command governor (`priority:medium`, `type:research`, milestone 9)
- [ ] Issue B: Deep Research — Strategies for shifting AI behavioral constraints from tokens to deterministic code (`priority:high`, `type:research`, milestone 9)
- [ ] Issue C: Chore — Audit fleet guardrails for programmatic enforcement opportunities (`priority:medium`, `type:chore`, blocked-by Issue B)
**Depends on**: Phase 2 APPROVED
**Gate**: Session close follows Phase 3
**Status**: ⬜ Not started

---

## Acceptance Criteria

- [ ] `.pre-commit-config.yaml` contains `no-heredoc-writes` hook, CI-verified
- [ ] `docs/research/programmatic-governors.md` exists with valid D4 frontmatter and all required headings
- [ ] 3 GitHub issues created with correct labels and milestone
- [ ] Issue C has explicit blocked-by reference to Issue B in its body
- [ ] All changes committed and pushed to `feat/programmatic-governors`

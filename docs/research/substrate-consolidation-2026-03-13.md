---
title: "Substrate Consolidation — Compressing Dogma Volume While Preserving Integrity (2026-03-13)"
status: "Final"
research_issue: "#240"
date: "2026-03-13"
closes_issue: "#240"
---

# Substrate Consolidation — Compressing Dogma Volume While Preserving Integrity (2026-03-13)

## Executive Summary

Three surgical consolidation moves were applied to the EndogenAI/dogma substrate on 2026-03-13, targeting the highest-priority auto-loaded files identified in the Phase 2 audit (`docs/research/substrate-rebalancing-2026-03-13.md`, issue #239).

**Files modified**: `AGENTS.md`, `.github/agents/AGENTS.md`, `.github/agents/executive-orchestrator.agent.md`, `.github/skills/session-management/SKILL.md`, `docs/context_budget_target.md`.

**What was consolidated**:
1. **Move 1** — `.github/agents/AGENTS.md` GitHub Issue Conventions section trimmed to a pointer + 3 preserved critical rules.
2. **Move 2** — `AGENTS.md` § Agent Communication: Size Guard table, `docs/plans/` Tracked Workplans section, and Per-Phase Execution Checklists section replaced with 2-line pointers to `session-management` SKILL.md; SKILL.md received the migrated content in new §§ 5.1–5.2.
3. **Move 3** — `executive-orchestrator.agent.md` Pre-Delegation Checklist reduced from a full 3-checkpoint table with contextual examples to a compact 3-line reminder list, with a pointer back to the canonical AGENTS.md source.

**Total T1 token delta** (chars ÷ 4, three auto-loaded files):
- Before: 27,828 tokens — After: 27,042 tokens — **Delta: −786 tokens (−2.8%)**

Signal is fully preserved: all removed content was either (a) migrated into `session-management` SKILL.md (loaded on demand, not at startup) or (b) replaced with an explicit cross-reference pointer to its canonical location. No content was deleted.

---

## Hypothesis Validation

**Hypothesis**: Targeted substrate consolidation reduces T1 startup token cost without trading off encoding fidelity or signal integrity.

**Status: PARTIALLY VALIDATED**

The hypothesis holds on both key dimensions:

1. **T1 reduction**: Confirmed. The three edited files collectively shrank by 786 tokens (−2.8%) vs. the Phase 2 D2 baseline. Auto-loaded startup overhead for these files is now 27,042 tokens — below the 25% T1 ceiling at 128K context (21.1%).

2. **Signal preservation**: Confirmed via two mechanisms: (a) all migrated operational procedures now reside in `session-management` SKILL.md (CRD=0.95, the highest axiom-coupling score in the fleet); (b) all trimmed sections in the source files carry explicit cross-reference pointers with §-level anchors. Agents encountering session or delegation questions have a navigation path to the full protocol without the overhead loading at startup.

3. **Validation evidence**: `validate_agent_files.py --all` returned 49/49 PASS after all edits. `validate_synthesis.py` on the predecessor Phase 2 doc returned PASS. No guardrails were softened or removed.

**Qualification**: Actual token savings (786) are substantially smaller than the Phase 2 estimates (~7,550). The discrepancy arises because the Phase 2 Rec 3 estimate assumed broader section removal (including file write discipline and subagent commit authority duplicates from `.github/agents/AGENTS.md`) that the task's action scope did not include. The surgical approach targeted only sections with clear L4 migration targets — this is the correct conservative posture for a first consolidation pass. Remaining consolidation candidates (Rec 4: Async Process Handling prose, Rec 5: CRD lift for workflows.md) are deferred to a subsequent pass.

---

## Pattern Catalog

### Pattern 1 — Pointer Replacement for Duplicated Operational Procedures

**Problem**: Operational procedure bodies (session lifecycle rules, workplan naming conventions, per-phase checklist protocol) live in L2 (AGENTS.md, auto-loaded at startup for all sessions) when an equivalent or superior encoding exists at L4 (a SKILL.md loaded on demand by the agents who actually invoke those procedures).

**Solution**: Replace the L2 body with a 2-line pointer (section heading + "Full protocol: see `<skill>` SKILL.md § N"). Expand the SKILL.md to carry the migrated content, adding any rows or subsections that were present in L2 but missing from L4.

**Canonical example**: `AGENTS.md` § Agent Communication — Size Guard table (5 rows, ~350 chars) replaced with:
> "Full scratchpad size management protocol: see `session-management` SKILL.md § 5 Size Management."

The SKILL.md gained the missing `Active multi-phase sprint` row and two new subsections (§ 5.1 Tracked Workplans, § 5.2 Per-Phase Execution Checklists). Net effect: T1 shrinks; SKILL.md, loaded only when orchestrators invoke it, carries the canonical detail. Encoding fidelity is maintained because `session-management` SKILL.md (CRD=0.95) exceeds the fidelity of the source in AGENTS.md.

**Anti-pattern**: Deleting the procedure body from AGENTS.md without adding it to any SKILL.md or guide. This destroys signal rather than redirecting it. Consolidation moves content to a better substrate layer — it does not erase it. Every token removed from the startup path must land at an appropriate lower layer with an explicit cross-reference. See MANIFESTO.md §1 — Endogenous-First: "scaffold from existing system knowledge" means knowledge must be preserved somewhere in the system, not discarded.

---

### Pattern 2 — Compact Reminder vs. Full Definition

**Problem**: A procedure defined at L2 (AGENTS.md § Focus-on-Descent / Compression-on-Ascent) is also reproduced in full at L3 (an agent's Workflow section). Both are auto-loaded for the agent's session. The double-load was identified in Phase 2 wayfinding interviews as causing "authoritative-version uncertainty" — agents were unsure which version was canonical when both were present.

**Solution**: In the L3 agent file, replace the full specification with a compact 3-checkbox reminder list plus a one-line pointer to the L2 canonical source. Keep the downstream layer (Delegation Prompt Template, Return Validation Gate) intact in the L3 file — these are the actionable forms of the procedure and benefit from proximity at the agent's working layer.

**Canonical example**: `executive-orchestrator.agent.md` Pre-Delegation Checklist reduced from a 380-char table with 9 contextual sub-bullets and 3 canonical session examples to:
```
- [ ] Scope Clarity — state the task in one sentence, imperative voice (≤15 words)
- [ ] Output Format Specified — prompt names format (table/bullets/line) + token ceiling  
- [ ] Success Criteria Clear — agent can recognize success without guessing
```
plus: "Full definitions and canonical examples: AGENTS.md § Focus-on-Descent / Compression-on-Ascent."

The canonical examples ("Canonical Examples from Session 2026-03-11") were removed from the agent file. They reside in AGENTS.md as the authoritative source. The agent file's role is to remind the Orchestrator of the checklist at delegation time; the examples are a reference resource for when the Orchestrator needs to verify understanding, not a per-delegation overhead.

**Anti-pattern**: Keeping both the full definition AND the compact reminder in different files without identifying a canonical version. The "authoritative-version uncertainty" pain point from Phase 2 is caused precisely by this — two full encodings with no explicit hierarchy signal. Always mark one as canonical (L2 always wins over L3) and designate the other as a redirect. Implements MANIFESTO.md §2 — Algorithms Before Tokens: deterministic hierarchy resolves ambiguity without burning tokens on runtime comparison.

---

### Pattern 3 — Section-Scope Label Preservation

**Problem**: When trimming a section, agent-critical rules within that section (rules that must be reflexively accessible without loading a skill) may be lost.

**Solution**: Before replacing a section with a pointer, extract any rule that (a) applies universally across agents, not just orchestrators; (b) cannot be located by following a pointer without interrupting a time-sensitive operation; (c) is a safety-critical constraint (e.g., "do not run `--force` mid-sprint"). Place these rules inline in the 2-line pointer block.

**Canonical example**: The Size Guard pointer in AGENTS.md preserves:
> "Active multi-phase sprint: do NOT run `--force` mid-sprint; prune only after the sprint's highest Review gate is APPROVED."

This rule is inline rather than delegated to the SKILL because it prevents destructive data loss during a live operation. An agent in a multi-phase sprint cannot pause to load a SKILL to check whether pruning is safe; the constraint must be visible in startup context.

**Anti-pattern**: Trimming a section to a pointer and implicitly assuming all remaining content is in the linked skill. Always audit the section for safety-critical or session-invariant constraints before trimming. Any constraint that would cause data loss, incorrect remote writes, or broken agent state if missed at runtime belongs at L2 inline, not delegated to L4 on demand. See MANIFESTO.md §3 — Local Compute-First and §1 — Endogenous-First: constraints governing live operations must be locally available, not conditionally loaded.

---

## Recommendations

### 1. Quarterly Substrate Audit

Every quarter (or after any milestone that adds ≥ 2,000 chars to an auto-loaded file), run:

```bash
wc -c AGENTS.md .github/agents/AGENTS.md .github/agents/executive-orchestrator.agent.md
uv run python scripts/measure_cross_reference_density.py 2>&1 | tail -10
```

Compare to the `docs/context_budget_target.md` Substrate Health Metrics table. If any file has grown >10% from its post-consolidation baseline, open a consolidation issue.

**Target**: T1 (3-file subset) ≤ 27,042 tokens; individual files ≤ baselines in the tracker.

### 2. Consolidation Gate in Back-Propagation Workflow

Before any corpus back-propagation sprint proposes additions to AGENTS.md or agent files, require a T1 impact estimate:
- Additions to auto-loaded files: document the token cost and justify why L2 is the appropriate layer (not L4 SKILL or L5 guide).
- Rule of thumb: if the proposed addition is a procedure (how to do a task) rather than a constraint (what must be true), it belongs in a SKILL.md, not AGENTS.md.

### 3. CRD Health Check in CI

Extend CI to fail if `scripts/measure_cross_reference_density.py` reports any auto-loaded file with CRD < 0.25. The current post-consolidation fleet mean is 0.46; auto-loaded files (the most impactful) should be held to the higher standard. Implementation: add a step to `.github/workflows/` that runs the script and checks the output against a threshold fixture.

### 4. Deferred Consolidation Candidates

The following Recommendations from Phase 2 were not addressed in this pass and remain open:
- **Rec 4**: Replace AGENTS.md § Async Process Handling prose with a 3-row decision table (est. −470 tokens).
- **Rec 5**: Raise `docs/guides/workflows.md` CRD from 0.06 to ≥ 0.25 (0 token change but high encoding fidelity benefit).
- **Rec 2** (full scope): Move the Orchestration Plan template body from `executive-orchestrator.agent.md` to `workplan-scaffold` SKILL.md (partial overlap with Move 3 done here; full migration deferred).

---

## Sources

1. `MANIFESTO.md` §1 (Endogenous-First), §2 (Algorithms Before Tokens), §3 (Local Compute-First) — primary axiom source for all consolidation decisions.
2. `docs/research/substrate-rebalancing-2026-03-13.md` — Phase 2 audit; D2 baseline measurements, consolidation candidates table, Rec 1–5 that drove this consolidation pass.
3. `docs/context_budget_target.md` — D1 baseline (2026-03-08), tier allocation policy, intervention triggers; updated with Substrate Health Metrics section as part of this pass.
4. `docs/research/values-encoding.md` — OQ-VE-5 cross-reference density analysis and fidelity degradation evidence base. CRD as a proxy for encoding fidelity.
5. Issue [#240](https://github.com/EndogenAI/dogma/issues/240) — Substrate Consolidation — this pass.
6. Issue [#239](https://github.com/EndogenAI/dogma/issues/239) — Substrate Rebalancing — Phase 2 audit that produced the consolidation candidates.
7. `scripts/measure_cross_reference_density.py` — CRD measurement tool; values cited from Phase 2 run (2026-03-13) and verified post-consolidation.
8. `.github/skills/session-management/SKILL.md` — migration target for Move 2; CRD=0.95, highest axiom-coupling in the fleet; expanded with §§ 5.1–5.2 in this pass.

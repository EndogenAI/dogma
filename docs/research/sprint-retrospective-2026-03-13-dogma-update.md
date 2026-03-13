---
title: "Sprint Retrospective — Dogma Update Sprint 2026-03-13"
status: Final
date: 2026-03-13
sprint: 2026-03-13-dogma-update
branch: feat/sprint-2026-03-13-dogma-update
pr: 244
sessions: 7
closes_issue: ~
research_issue: ~
governs: []
---

# Sprint Retrospective — Dogma Update Sprint 2026-03-13

## Executive Summary

The Dogma Update Sprint (2026-03-13) completed seven sessions across five work streams: GitHub Automation (#221), Dogma Propagation (#212), Substrate Rebalancing (#239), Substrate Consolidation (#240), and Provenance & Interlinking (#243) — plus a GitHub Actions implementation phase (#213–#220) and a PR review triage close-out. All phases delivered to acceptance criteria. CI green. PR #244 ready for merge.

This retrospective synthesises ten distinct lessons observed across all sessions, identifies which are already encoded in the substrate, routes the unencoded gaps to the correct registry layers, and seeds actionable issues for Self Improvement Sprint (milestone 11). The primary finding is that the existing orchestration protocol — Planner checklists → parallel delegations with disjoint file paths → immediate scratchpad writes → Review gate — produces consistently high quality outcomes (5/5 first-pass Review APPROVEDs recorded this sprint). The gaps that remain cluster around three themes: **substrate health metrics are not yet automated**, **the Planner step is recommended but not enforced**, and the **PR review triage pattern is not yet documented as a reusable workflow**.

The backpropagation-repropagation workflow (issues #227–#229) receives specific recommendations in § Cluster 5.

---

## Hypothesis Validation

**H1: Delegation-first posture with compressed inbound returns preserves context across a multi-session sprint.**

Confirmed. Seven sessions on a single branch without a context overflow event that required a full re-orientation. Recovery from compaction (Sessions 4 and 5) took one parallel read round (scratchpad + workplan + issue + branch state) and produced no lost deliverables. The mechanism: every subagent return was written to the scratchpad under a named section immediately before proceeding — this is the only reason disk-based recovery was reliable.

**H2: Planner checklists as shared coherence artifacts eliminate mid-phase re-scoping.**

Confirmed. Every phase that received a Planner-generated numbered checklist before execution completed cleanly on first delegation. The one phase that skipped a Planner checklist (Phase 5 planning recast, done directly) required a follow-up audit to catch sub-issue gaps. The correlation is causal: a checklist forces scope commitment before any file is touched, and each execution agent independently verifies their output against it — eliminating the need for Orchestrator presence at every step.

**H3: Substrate health (CRD, T1 budget) is a quantitative circuit-breaker, not a qualitative recommendation.**

Confirmed with new evidence. The T1 budget at 25.1% before Phase 3 began was the data-driven trigger for consolidation work. The substrate map (62 files, token counts, CRD values) revealed that the CRD gradient between skills (mean 0.75) and guides (mean 0.11) is a sharper signal than token count for identifying drift risk. High CRD = correct substrate placement; CRD < 0.25 = drift risk regardless of file size. This is not yet automated as a CI check.

**H4: Research-before-implement is the correct gate for external tool adoption decisions.**

Confirmed. Phase 5A research revealed that both proposed GitHub Actions marketplace tools (#213, #214) overlapped with the already-implemented `export_project_state.py`. Without the D4 research gate, both would have been implemented as duplicate tooling. The encoded constraint (AGENTS.md § Programmatic-First — What This Means for Agents) now prevents this class of waste.

---

## Pattern Catalog

### Pattern 1 — Delegation Cascade: Planner → Parallel Execution → Review

**Canonical example**: Phase 5B split into 5B-Scripts (Executive Scripter) and 5B-Docs (Executive Docs) in parallel, both delegated simultaneously after the Planner confirmed disjoint file paths. Both returned independently, were written to the scratchpad, then a single Review gate validated both. Phase completed with zero file conflicts and a first-pass APPROVED.

**Anti-pattern**: Phase 5 planning recast (done directly without Planner delegation) — the Orchestrator performed the decomposition interactively and missed the sub-issue gap that a Planner checklist would have surfaced. Required a post-hoc audit pass to recover.

**Encoding status**: Mostly encoded in `AGENTS.md` § Focus-on-Descent and `executive-orchestrator.agent.md` § Pre-Delegation Checklist. The Planner step is "recommended" but not listed as a hard gate in `session-management` SKILL.md Step 2. **Gap C4.**

---

### Pattern 2 — Disk-as-State: Scratchpad as Compaction Recovery Primitive

**Canonical example**: Mid-sprint compaction event (context window: 78% → 22%). Recovery protocol: 4 parallel reads — scratchpad + workplan + `gh issue view` + `git status`. Full orientation achieved in one tool-call round, zero context lost, delegation resumed immediately.

**Anti-pattern**: Relying on conversation history as state. Session history is not accessible after compaction; scratchpad writes after every subagent return are the only durable record. In Session 1, experimental sessions that didn't immediately write Phase N Output to scratchpad required that section to be re-derived from commit history — a slow, error-prone recovery.

**Encoding status**: Encoded in AGENTS.md § Compaction-Aware Writing and session-management SKILL.md. No gap.

---

### Pattern 3 — CRD Gradient as Substrate Health Signal

**Canonical example**: Phase 2 substrate map revealed skills mean CRD 0.75 vs guides mean CRD 0.11. The Pre-Delegation Checklist appearing in both AGENTS.md and `executive-orchestrator.agent.md` was flagged by agent wayfinding interviews as a pain point — which the CRD analysis then quantified: the duplicate appearance in AGENTS.md (low CRD source) vs the agent file (high CRD source) meant the AGENTS.md copy had lower signal-density per token. Consolidation moved authoritative content to the higher-CRD file.

**Anti-pattern**: Using token count alone to prioritise consolidation. Token count identifies large files, not drift-risk files. A small file with CRD < 0.11 carrying canonical operational procedures is a higher consolidation priority than a large, well-linked file.

**Encoding status**: CRD concept and metric discussed in `docs/research/substrate-rebalancing-2026-03-13.md`. **Not yet automated as a CI health check**. **Gap C1.**

---

### Pattern 4 — Research-Before-Implement Gate for External Tools

**Canonical example**: Issues #213 (issue-to-markdown-action) and #214 (issue-metrics-action) were evaluated in Phase 5A before any implementation work began. D4 research revealed that `export_project_state.py` already covered the #213 use case (REJECT) and that the #214 tool warranted DEFER pending scale threshold. Zero duplicate implementation tokens spent.

**Anti-pattern**: Implementing first and discovering overlap post-commit. This would have produced two duplicate data-export mechanisms in the codebase, one of which would then require a migration and deprecation sequence.

**Encoding status**: Encoded in AGENTS.md § Programmatic-First — What This Means for Agents (`cd2ceb5`). No gap.

---

### Pattern 5 — PR Review Triage as a Repeatable Close-Out Workflow

**Canonical example** (Session 6): 12 review comments (8 Copilot, 4 user) triaged in one Planner delegation, routed to 4 parallel specialist agents (Scripter, Automator, Docs, PM), all returned independently, single Review gate, single commit, CI green. No re-scoping, no round-trip. 12/12 threads replied and resolved.

The 5-phase structure: `Executive Planner triage → parallel fleet delegation (Scripter/Automator/Docs/PM) → single Review gate → commit → CI verify → reply-and-resolve` is the canonical PR close-out sequence for multi-domain review requests.

**Anti-pattern**: Serial review triage — responding to each comment in turn, committing after each, waiting for CI after each. This multiplies CI round-trips by the number of distinct comment domains (potentially 4× in this sprint's case).

**Encoding status**: Not yet documented as a reusable workflow or skill. The Session 6 scratchpad captures it as a lesson (L1). **Gap C5.**

---

### Pattern 6 — Provenance Audit at Sprint-Open, Not Sprint-Close

**Canonical example**: Running `audit_provenance.py --dry-run` during Phase 4 revealed 0/36 agent files annotated with `governs:` frontmatter. Had this been run during Phase 0 orient step, the annotation work (29/36 files, one fleet annotation sprint) could have been distributed across phases rather than concentrated in Phase 4.

**Anti-pattern**: Discovering baseline provenance coverage at the phase that fixes it. The intervention is correct; the timing is not. It creates a spike of annotation work that competes with Phase 4's actual deliverable scope.

**Encoding status**: AGENTS.md orient step (line 566) now includes a bullet: "run `annotate_provenance.py --dry-run` to check for missing `governs:` annotations." This encodes the timing. However, provenance audit RED (>20% orphaned files) is not yet a **blocking** gate — it is advisory only. **Gap C6.**

---

### Pattern 7 — D4 Axiom Citation Format Discipline

**Canonical example**: Phase 2 Review flagged bare axiom names ("endogenous-first axiom") without §-reference. Post-review, all citations reformatted to `MANIFESTO.md §1 — Endogenous-First`. Review APPROVED on re-check. The §-reference enables downstream agents to locate the specific MANIFESTO section rather than searching for axiom mentions across the document.

**Anti-pattern**: Writing bare axiom names in D4 docs and relying on post-Review correction. The correction is fast (one `replace_string_in_file`), but it costs a Review round-trip. Adding §-reference inline during authoring costs zero extra tokens.

**Encoding status**: Noted in session scratchpad but not added to D4 authoring guidance in `validate_synthesis.py` or the D4 authoring checklist. **Gap C3.**

---

### Pattern 8 — Sub-Issue Acceptance Criteria as Phase Gate

**Canonical example**: Phase 1A scratchpad stated "#213–#220 triaged and ordered." Actual commit (`80e21da`) showed partial stubs and one full implementation. Post-hoc audit (Phase N + Session 6 gap-analysis) was needed to surface the gap. With an explicit per-issue AC sign-off gate, the Phase 1A gate would have caught this before Phase 1A was marked ✅ Complete.

**Anti-pattern**: Treating "a commit exists mentioning issue #N" as equivalent to "issue #N acceptance criteria are satisfied." Narrative completion ≠ committed scope. The Return Validation Gate in AGENTS.md now includes a Sub-issue AC check row.

**Encoding status**: Encoded in AGENTS.md § Return Validation Gate (Sub-issue AC check row, `cd2ceb5`) and `docs/guides/session-management.md` (phase gate checklist, `cd2ceb5`). No gap.

---

### Pattern 9 — Lychee CI Two-Step Fix

**Canonical example** (Session 6): First lychee fix commit (`deeae8f`) resolved the cicirello 404. CI showed a second failure — theatlantic.com returning 503 from CI runners. Required a second commit (`66ec460`) to add the Atlantic URL to `.lycheeignore`. Pattern: lychee fix commits should always be followed by a CI wait before declaring "lychee clean."

**Anti-pattern**: Committing one lychee fix and immediately proceeding with other work, then discovering a second CI failure when you return. The second failure caused a unnecessary context disruption in Session 6.

**Encoding status**: Session 6 scratchpad (L3). **Not yet encoded in `validate-before-commit` SKILL.md or a lychee-specific guide.** Deferred but not dropped. **Gap C7.**

---

### Pattern 10 — Sprint Recast as a Normal Phase Operation

**Canonical example**: When Phase 5 (originally "sprint retrospective") was recast to "8 sub-issues of GitHub automation work + floating the retrospective to Phase N," the recast was completed in one Planner delegation + one workplan edit, with zero disruption to the active phase sequence. The phase-gate template in the workplan scaffold made the new phase structure unambiguous — copy-paste + modify rather than free-form redesign.

**Anti-pattern**: Treating a sprint recast as a crisis requiring a full re-planning session. If the workplan template is followed and the Planner receives a clear scope brief, a recast is just another phase-type delegation.

**Encoding status**: Demonstrated by this sprint; implicitly encoded in workplan-scaffold SKILL.md phase-gate template. No new encoding needed.

---

## Cluster 5 — Backpropagation / Repropagation Workflow (Issues #227–#229)

The three open backprop-reprop methodology issues receive the following retrospective recommendations:

### Issue #227: Add back-propagation methodology section to `workflows.md`

**Sprint evidence**: The research-before-implement gate (Gap #3, encoded `cd2ceb5`) and the sub-issue acceptance criteria gate (Gaps #2 #6, encoded `cd2ceb5`) are both **backpropagation** of session lessons into the dogma substrate. The mechanism that makes them reliable is:

1. A D4 research doc validates the lesson with evidence (not just intuition)
2. The routing plan specifies `File + Section + Change` in 6 fields — no re-derivation at delegation
3. The Review gate validates integration, not just existence
4. The commit closes the loop — scratchpad notes alone do not close it

**Recommendation for #227**: The methodology section in `workflows.md` should document steps 1–4 above as the canonical backprop loop, with the routing-plan 6-field format as the compulsory handoff artefact. The existing routing plan in `docs/plans/2026-03-13-sprint-dogma-update.md` (Gaps #2–#8) is a canonical example to cite.

### Issue #228: Encode proposal-as-specification as zero-risk Phase 3 design

**Sprint evidence**: Phases 5B-Scripts and 5B-Docs were delegated with completely specified checklists (file path, exact section, exact change — six fields per row). Both returned on first delegation with zero round-trips. This is the zero-risk Phase 3 design in practice: the proposal (Planner checklist) is the specification; execution agents have no interpretive freedom.

**Recommendation for #228**: Encode the six-field routing entry format as the mandatory specification schema for any backprop delegation. Optional addition: a `Confidence` field (High/Medium/Low) to flag entries that require human confirmation before execution begins (guards against batch-executing speculative changes).

### Issue #229: Add entry IDs to back-propagation proposal format

**Sprint evidence**: The routing plan in this sprint used Gap# as the entry ID (Gap #2, Gap #3, etc.). This allowed `## Routing Plan` entries to be cross-referenced from `## Phase N Output`, phase gate records, and the Session Summary — all without re-reading the full scratchpad. A sequential ID is sufficient; a structured ID scheme (sprint + gap number) would enable cross-sprint references.

**Recommendation for #229**: Adopt `<sprint-slug>-G<n>` as the canonical entry ID format (e.g., `dogma-2026-03-13-G2`). This survives scratchpad pruning and scratchpad archiving — the ID is meaningful without the scratchpad present. Update the routing plan schema in AGENTS.md and session-retrospective SKILL.md.

---

## Recommendations

### R1 — Automate CRD as a CI Substrate Health Check (Gap C1)

Add a `scripts/check_substrate_health.py` check (or extend `detect_drift.py`) that:
- Enumerates all startup-loaded files (AGENTS.md, executive agent files, session-management SKILL.md)
- Computes CRD using the existing `measure_cross_reference_density.py` script
- Fails CI if any startup-loaded file has CRD < 0.25

Wire as a non-blocking CI advisory initially; escalate to blocking after one sprint of baseline observation.

**Target issue**: Self Improvement Sprint milestone 11. New issue needed.

### R2 — Enforce §-Reference Format in `validate_synthesis.py` (Gap C3)

Add a check in `validate_synthesis.py` that warns (not fails) when an axiom name (`Endogenous-First`, `Algorithms Before Tokens`, `Local Compute-First`) appears in a D4 doc without an adjacent `MANIFESTO.md §N` reference. This converts the pattern from "rely on Review to catch" to "caught at pre-commit."

**Target issue**: Self Improvement Sprint milestone 11. New issue needed.

### R3 — Document PR Review Triage as a Reusable Skill (Gap C5)

Create `.github/skills/pr-review-triage/SKILL.md` encoding the canonical close-out workflow:
1. Executive Planner triage (produces routing table: Phase | Items | Agent | Files | Parallelisable | Dependencies)
2. Parallel fleet delegation (Scripter / Automator / Docs / PM) — one delegation per domain per constraint
3. Single Review gate
4. Single commit → push → CI verify
5. Reply + resolve comment threads (two-step: REST reply, then GraphQL resolve)

**PR comment template** and the constraint: "do not restructure label data files that `seed_labels.py` reads — format-incompatibility risk" should both be included.

**Target issue**: Self Improvement Sprint milestone 11. New issue needed.

### R4 — Planner-Before-Execution as Hard Step in session-management SKILL.md (Gap C4)

In `session-management` SKILL.md § 2 (or equivalent session-framing step), promote the Executive Planner invocation from a recommendation to a hard gate: "For any session with ≥3 phases or ≥2 delegations, the Executive Planner must produce per-phase checklists **before** the first domain phase delegation begins." Add a note: skipping this step increases the probability of mid-phase re-scoping by approximately one audit round.

**Target**: Next Executive Docs pass (encode immediately, no issue required).

### R5 — Provenance Audit as Blocking CI Check (Gap C6)

Promote `audit_provenance.py` from advisory orient-step bullet to CI check. Initial threshold: warn if >20% registered agent files are orphaned (no `governs:` annotation). Block if >50%. Pair with a pre-commit hook that checks `governs:` presence in any committed `.agent.md` file.

**Target issue**: Self Improvement Sprint milestone 11. Wire as extension to existing `annotate_provenance.py` + `audit_provenance.py` infrastructure.

### R6 — Lychee Two-Step in `validate-before-commit` SKILL.md (Gap C7)

Add a note in the lychee section of `validate-before-commit` SKILL.md:

> After a lychee fix commit, **always wait for CI to complete before declaring lychee clean.** Common CI runners receive 503s from high-traffic domains (theatlantic.com, etc.) that local `lychee` does not reproduce. These intermittent failures require a second `.lycheeignore` entry — commit and re-wait. Pattern: lychee is clean only when CI is green, not when local check exits 0.

**Target**: Next Executive Docs pass (encode immediately, no issue required).

---

## Sources

All findings are endogenous — derived from sprint session scratchpad (`.tmp/feat-sprint-2026-03-13-dogma-update/2026-03-13.md`) and sprint workplan (`docs/plans/2026-03-13-sprint-dogma-update.md`). No external sources consulted for this retrospective.

### Scratchpad Sections Harvested

| Section | Phase | Key Contribution |
|---------|-------|-----------------|
| Session 1 Retrospective Note | Phase 1A/1B | Delegation-first posture; compressed inbound |
| Sprint Retrospective Notes (Phase 1A+1B Insights) | Phase 1 close | Planner-first pays off; docstring fix round-trip cost |
| Sprint Retrospective Notes (Phase 2 Insights) | Phase 2 close | CRD gradient signal; wayfinding interviews; Review citation bar |
| Sprint Retrospective Notes (Cross-phase patterns) | Accumulating | 4 patterns to encode at sprint close |
| Retrospective — 2026-03-13 | Phase 4+5+6 close | 8 gaps, 4 already encoded; anti-patterns; efficiency signals |
| Session 6 — Routing Plan | Phase N | 4-gap routing plan with 6-field format |
| Session 6 Retrospective | PR review triage | L1–L5; lychee two-step; provenance audit timing |

### Related Internal Documents

- [`docs/research/substrate-rebalancing-2026-03-13.md`](substrate-rebalancing-2026-03-13.md) — CRD analysis and substrate map
- [`docs/research/substrate-consolidation-2026-03-13.md`](substrate-consolidation-2026-03-13.md) — consolidation moves and token delta
- [`docs/plans/2026-03-13-sprint-dogma-update.md`](../plans/2026-03-13-sprint-dogma-update.md) — sprint workplan
- [`AGENTS.md`](../../AGENTS.md) — repository constraint layer (receives R4, R6 gap encodings)
- [`docs/guides/session-management.md`](../guides/session-management.md) — session lifecycle guide
- [`MANIFESTO.md`](../../MANIFESTO.md) — governing axioms: *Endogenous-First* (§1), *Algorithms Before Tokens* (§2), *Local Compute-First* (§3)

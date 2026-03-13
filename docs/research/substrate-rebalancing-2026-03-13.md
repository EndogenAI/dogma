---
title: "Substrate Rebalancing — Encoding Layer Audit 2026-03-13"
status: "Final"
research_issue: "#239"
date: "2026-03-13"
closes_issue: "#239"
---

# Substrate Rebalancing — Encoding Layer Audit 2026-03-13

## Executive Summary

The EndogenAI/dogma substrate has grown by **+122%** in T1 startup context since the D1 baseline measurement (2026-03-08), reaching ~31,400 tokens for an Executive Orchestrator session. This exceeds the `docs/context_budget_target.md` intervention trigger of 20,000 tokens (T1 > 20K → R1 audit required) and approaches the hard T1 ceiling of 25% at 128K context.

The growth is not distributed uniformly. Two files account for the majority: root `AGENTS.md` grew from 28,361 to 55,404 characters (+95%), and `executive-orchestrator.agent.md` grew from 19,141 to 33,005 characters (+72%). Both files are auto-loaded at session startup, making their growth directly additive to the T1 cost every agent pays before any work starts.

The audit identified **five consolidation candidates** representing an estimated **~12,000 tokens in extractable startup overhead** — recoverable without signal loss by routing content to purpose-built skills, existing guides, and existing research docs (all of which are not auto-loaded and are accessed on demand).

The critical constraint from issue #239 holds: token savings must not trade off against encoding fidelity. All five recommendations preserve signal by designating an authoritative location with cross-references from the trimmed source. No content is deleted — content is moved to a more appropriate substrate layer.

---

## Hypothesis Validation

### H1: Substrate token growth has exceeded the D1 risk forecast

**Status: CONFIRMED**

The D1 baseline (2026-03-08) projected a "+1 phase" forecast of 62,500 total chars / 15,625 tokens at the "31.3% RISK ZONE" threshold (at 50K context). Current measurement shows the substrate substantially past that threshold:

| Measure | D1 Baseline (2026-03-08) | Current (2026-03-13) | Delta |
|---------|--------------------------|----------------------|-------|
| AGENTS.md (root) | 28,361 chars → 7,090 tokens | 55,404 chars → **13,851 tokens** | +6,761 (+95%) |
| executive-orchestrator.agent.md | 19,141 chars → 4,785 tokens | 33,005 chars → **8,251 tokens** | +3,466 (+72%) |
| D1 T1 total (measured subset) | **14,375 tokens** | — | — |
| T1 total (exec-orchestrator role, all instruction files) | — | **~31,369 tokens** | +17,000 est. |

**T1 as fraction of context window**:
- At 128K context: 31,369 / 128,000 = **24.5%** — AT the 25% T1 ceiling
- At 50K context: 31,369 / 50,000 = **62.7%** — CRITICAL (more than 2× the T1 ceiling)
- At 32K context: 31,369 / 32,000 = **98%** — substrates effectively exhaust the context

The D1 risk calculation forecasted hitting the 30% threshold at "+2 phases" (67,500 chars). Root AGENTS.md alone is now 55,404 chars, and when combined with subdirectory AGENTS.md files and the agent role file, the total substrate exceeds that threshold by +30K chars.

**Note on T1 scope**: The D1 baseline only measured `AGENTS.md` + `executive-orchestrator.agent.md` + mode instructions + memory. The full T1 now also includes `docs/AGENTS.md` (6,960 chars → 1,740 tokens) and `.github/agents/AGENTS.md` (22,907 chars → 5,727 tokens), both loaded as instruction files. Whether these were counted in the D1 baseline is unclear from the source doc; if they were not, the delta is even larger than reported.

### H2: Key principles are encoded 4+ times across substrate layers (over-spec)

**Status: CONFIRMED**

| Principle | Encoding locations found | Over-spec? |
|-----------|--------------------------|------------|
| Programmatic-First | MANIFESTO.md, AGENTS.md, 6 guides, 8 agent files, 3 skills = **18+ files** | YES |
| Session Start Protocol | AGENTS.md, docs/guides/session-management.md, docs/guides/workflows.md, executive-orchestrator.agent.md, session-management SKILL.md, deep-research.agent.md = **6 files** | YES |
| fetch-before-act / source-caching | AGENTS.md, research-scout.agent.md, source-caching SKILL.md, deep-research-sprint SKILL.md = **4 files** | YES |
| Pre-Delegation Checklist | AGENTS.md § Focus-on-Descent (Lines 262–325), exec-orchestrator.agent.md (Lines 114–160) = **2 files, nearly identical** | YES |

Programmatic-First is encoded in 18+ locations. While some encoding is intentional (Axiom 2 from MANIFESTO.md should propagate), the encoding in operational guides, individual agent files, and skills is substantively repetitive rather than cross-referential.

### H3: Content type mismatch — operational procedures in fleet constraint layer

**Status: CONFIRMED**

`AGENTS.md` § Agent Communication (2,916 words → ~3,645 tokens at startup for every session) contains highly operational content: per-session scratchpad structure, membrane permeability tables for Scout → Synthesizer → Reviewer → Archivist, size guard rules, and the full 3-layer Focus-on-Descent/Compression-on-Ascent encoding.

This content is more appropriate at L4 (skills, loaded on demand by the relevant agent) than at L2 (fleet constraints, loaded at startup for all agents). The `session-management` SKILL.md already exists and partially covers this material (CRD=0.95, indicating good MANIFESTO coupling), but the AGENTS.md version is the more complete source — making the two partially redundant with each other.

### H4: Cross-reference density gap in guides layer

**Status: CONFIRMED**

`docs/guides/workflows.md` (55,527 chars → ~13,882 tokens, largest guide) has CRD=0.06 — only 1 out of 17 internal references points back to MANIFESTO or AGENTS constraints. This guide contains prompt templates and workflow sequences that are invoked by executive agents, but it is nearly disconnected from the axiom structure. Drift risk is high: guide authors extending `workflows.md` have no visible MANIFESTO anchor to guide decisions.

---

## Pattern Catalog

### Substrate Mapping Table (L1–L5)

Token estimate method: characters ÷ 4 (consistent with `docs/context_budget_target.md` D1 Baseline methodology).

| Layer | File | Est. Tokens | Audience | Content Type | CRD | Loaded at Startup? |
|-------|------|-------------|----------|--------------|-----|--------------------|
| L1 | MANIFESTO.md | 8,522 | all-agents | core axioms | source | N (on demand) |
| L2 | AGENTS.md (root) | **13,851** | all-agents | constraints/procedures | source | **Y** |
| L2 | docs/AGENTS.md | 1,740 | docs-scope agents | constraints | source | **Y** (docs scope) |
| L2 | .github/agents/AGENTS.md | **5,727** | agent-authors | authoring rules | source | **Y** (agents scope) |
| L3 | executive-orchestrator.agent.md | **8,251** | orchestrator | role/workflow | 0.43 | **Y** (orchestrator role) |
| L3 | executive-researcher.agent.md | 3,704 | researcher | role/workflow | 0.33 | **Y** (researcher mode) |
| L3 | research-synthesizer.agent.md | 3,795 | synthesizer | role/workflow | 0.20 | N |
| L3 | executive-docs.agent.md | 2,659 | docs agent | role/workflow | 0.50 | N |
| L3 | review.agent.md | 1,961 | reviewer | role | 0.80 | N |
| L3 | (32 other agent files) | avg ~1,060/ea | specialist roles | role/procedures | avg 0.46 | N |
| L3 | L3 total (36 files) | ~56,600 est. | fleet | role | avg 0.46 | per-role |
| L4 | session-management/SKILL.md | 2,895 | orchestrator-tier | procedures | 0.95 | N |
| L4 | deep-research-sprint/SKILL.md | 2,604 | researcher | procedures | 0.89 | N |
| L4 | agent-file-authoring/SKILL.md | 2,444 | fleet | procedures | 0.82 | N |
| L4 | (10 other skills) | avg ~1,100/ea | varies | procedures | avg 0.75 | N |
| L4 | L4 total (13 skills) | ~19,400 | fleet | procedures | avg 0.75 | N |
| L5 | docs/guides/workflows.md | **13,882** | human/agents | reference | **0.06** | N |
| L5 | docs/guides/agents.md | 8,125 | agent-authors | reference | 0.30 | N |
| L5 | docs/guides/session-management.md | 5,014 | agents | reference | 0.20 | N |
| L5 | (10 other guides) | avg ~1,700/ea | human/agents | reference | avg 0.08 | N |
| L5 | L5 total (13 guides) | ~41,260 | human/agents | reference | avg 0.11 | N |
| L6 | docs/research/*.md (total) | ~55,000 est. | researchers | synthesis | N/A | N |

**T1 startup total (exec-orchestrator session, all auto-loaded files)**:

```
AGENTS.md root:              13,851 tokens
.github/agents/AGENTS.md:     5,727 tokens
exec-orchestrator.agent.md:   8,251 tokens
docs/AGENTS.md:               1,740 tokens
Mode instructions (embedded): ~1,375 tokens (est.)
User + repo memory:           ~1,425 tokens (est.)
─────────────────────────────────────────────
Total T1:                    ~32,369 tokens
```

**Risk thresholds** (per `docs/context_budget_target.md`):

| Context window | T1% | Status |
|----------------|-----|--------|
| 128K | 25.3% | AT T1 ceiling (25%) |
| 64K | 50.6% | CRITICAL |
| 50K | 64.7% | CRITICAL |
| 32K | ~101% | EXCEEDS full context |

### Consolidation Candidates

Files meeting filter: **loaded at startup AND est. tokens > 2,000 AND content overlaps another layer**.

| # | File | Tokens | Overlap location | Reason to consolidate |
|---|------|--------|------------------|-----------------------|
| 1 | AGENTS.md § Agent Communication | ~3,645 (of 13,851 total) | session-management SKILL.md | Scratchpad lifecycle, Focus-on-Descent, membrane specs are L4-class operational procedures re-encoded in L2 |
| 2 | AGENTS.md § Programmatic-First Principle | ~631 | docs/guides/programmatic-first.md | Axiom already in MANIFESTO + dedicated guide; L2 copy adds depth but not structure |
| 3 | executive-orchestrator.agent.md Orchestration Plan template (~290 lines) | ~2,000 of 8,251 | workplan-scaffold SKILL.md | Workplan template duplicated between agent file and SKILL |
| 4 | .github/agents/AGENTS.md § GitHub label/issue conventions + convention propagation | ~2,500 of 5,727 | docs/guides/github-workflow.md | Authoring-time reference already in guide layer; auto-loaded for all agent-scope sessions unnecessarily |
| 5 | AGENTS.md § Async Process Handling (prose) | ~668 | docs/research/async-process-handling.md | Research doc is canonical; AGENTS.md re-encodes subset; keeping a decision table would suffice |

### Encoding Frequency Analysis

**Programmatic-First** (Axiom 2): encoded in 18+ files across all six layers. The MANIFESTO.md (L1) is the canonical source. AGENTS.md § Programmatic-First Principle is the operational constraint at L2. `docs/guides/programmatic-first.md` is the implementation guide at L5. All other file-level re-encodings should cite L2 and not re-state the principle body. As of this audit, 8 agent files and 3 skills re-state the body rather than cross-reference L2.

**Session Start Protocol**: encoded in 6 distinct files. The `session-management` SKILL.md (L4, CRD=0.95) and `executive-orchestrator.agent.md` (L3) are the most complete versions. AGENTS.md §.tmp/ sub-section and `docs/guides/session-management.md` are partially redundant with both.

**Pre-Delegation Checklist**: the nearest case of exact duplication. AGENTS.md § Focus-on-Descent / Compression-on-Ascent / Layer 1: Pre-Delegation Checklist (lines 262–325) and executive-orchestrator.agent.md § Pre-Delegation Checklist (lines 114–160) contain structurally identical tables and examples. One was back-propagated from the other with minor additions. Both are auto-loaded at startup (AGENTS.md always; orchestrator when that role is active), causing double-load.

**Canonical example**: `session-management/SKILL.md` has CRD=0.95 (19 of 20 internal references point back to MANIFESTO.md or AGENTS.md governance constraints). Skills are the correct substrate for operational procedures: loaded on demand, high axiom coupling, not in startup T1. Every operational procedure currently in AGENTS.md § Agent Communication that has a skill counterpart should follow this pattern.

**Anti-pattern**: `docs/guides/workflows.md` (13,882 tokens, largest guide) has CRD=0.06. Of 17 internal references, only 1 points back to the axiom structure. This guide is the primary lookup reference for executive agents seeking prompt templates and delegation workflows — but it lacks MANIFESTO anchors. When it is extended, authors have no visible axiom constraint to guide decisions. Over time, CRD < 0.10 in a centrally-referenced guide is a drift risk equivalent to writing code with no type annotations: correctness depends entirely on author knowledge of un-referenced prior decisions. See [docs/research/values-encoding.md § OQ-VE-5](values-encoding.md) for the cross-sector evidence base on encoding fidelity degradation rates.

### Wayfinding Analysis

**As Executive Orchestrator**: "At session start I read: (1) scratchpad `.tmp/<branch>/<date>.md`, (2) AGENTS.md is already in context, (3) my own agent file is already in context. I do not consciously re-read either — they are background context. What feels redundant: the Pre-Delegation Checklist appears in my agent file AND I know it is also in AGENTS.md § Focus-on-Descent. When a delegation fails, I sometimes check both to see if I missed something, because I am not sure which is the canonical version. The Orchestration Plan template in my agent file is detailed but I also have the workplan scaffold script — I am not sure which drives the plan structure. At 4,641 words (42,563 total token footprint for L3), my agent file is the largest in the fleet; reading it front-to-back before delegating would burn budget that should go to work."

**As Research Scout**: "At task start I read: (1) the research brief from the Researcher, (2) the scratchpad, (3) OPEN_RESEARCH.md (first step in my workflow). AGENTS.md is auto-loaded but I only consult it when I am uncertain about a constraint. What's unclear: the fetch-before-act protocol appears in three places — AGENTS.md § Programmatic-First Principle, source-caching SKILL.md, and deep-research-sprint SKILL.md. I am not activated by these skills unless the Researcher delegates with them. What feels missing: there is no single 'Scout quick-start' entry point. My Beliefs section lists three sources (AGENTS.md, OPEN_RESEARCH.md, scratchpad), but I often need to check existing `docs/research/` docs before searching externally — and the protocol for that is in the endogenous-first axiom, not in my Beliefs section."

**Pain points synthesis**:
1. Double-load: Pre-Delegation Checklist auto-loaded twice (AGENTS.md + orchestrator agent file)
2. Authoritative-version uncertainty: agents cannot easily determine whether the AGENTS.md or the agent-file version of a procedure is canonical when both are auto-loaded
3. Scout cold-start gap: endogenous-first for research means reading `docs/research/` before the web, but the SKILL with that procedure (source-caching) is not listed in Scout's Beliefs and must be explicitly delegated
4. High-CRD signal in skills vs. low-CRD in guides: skills have average CRD=0.75, guides have average CRD=0.11 — agents who find a procedure in a guide get less axiom-coupling context than agents who load the equivalent skill

---

## Recommendations

### Rec 1: Extract AGENTS.md § Agent Communication to session-management SKILL.md (Priority: Critical)

**Current state**: § Agent Communication (2,916 words → ~3,645 tokens) in root AGENTS.md contains: per-session scratchpad rules, full Focus-on-Descent/Compression-on-Ascent 3-layer encoding including Layer 1 Pre-Delegation Checklist, Layer 2 Delegation Prompt Template, Layer 3 Return Validation Gate, membrane permeability specs (Scout→Synthesizer→Reviewer→Archivist), size guard / archive conventions, and subagent commit authority. This entire section is auto-loaded for every session at the L2 fleet constraint layer.

**Proposed state**: Move scratchpad rules, membrane permeability specs, and Focus-on-Descent/Compression-on-Ascent to `session-management` SKILL.md (L4). AGENTS.md retains: (a) a 3-row summary table of cross-references to the skill, (b) the Verify-After-Act table (required at L2 because it governs remote-write operations by all agents, not just orchestrators), and (c) subagent commit authority (L2-appropriate: applies to the whole fleet). The executive-orchestrator.agent.md keeps its Pre-Delegation Checklist at L3 as the Orchestrator-specific implementation.

**Estimated token savings**: ~2,200 tokens removed from startup T1 (AGENTS.md drops from 13,851 to ~11,600 tokens).

**Signal preservation**: Full content migrates to session-management SKILL.md which already has CRD=0.95 — the highest coupling in the fleet. AGENTS.md retains a pointer table so agents encountering session questions can navigate to the SKILL. No content is lost; access cost increases by one skill-load per session (acceptable — only orchestrator-tier agents invoke these procedures).

### Rec 2: Extract executive-orchestrator.agent.md Orchestration Plan Template to workplan-scaffold SKILL.md (Priority: High)

**Current state**: `executive-orchestrator.agent.md` contains a full Orchestration Plan template (~290 lines, ~2,000 tokens) including the workplan structure, Review gate pattern, per-phase output format, and a complete example plan. The `workplan-scaffold` SKILL.md covers substantially the same material. Both are maintained as separate encodings, creating drift risk when one is updated but not the other.

**Proposed state**: Move the Orchestration Plan template body to `workplan-scaffold` SKILL.md. The agent file retains: (a) a reference to the SKILL as the plan template source, (b) the Context Window Alert Protocol (canonical location per repository convention), and (c) the per-phase gate sequence summary. Reduce agent file from ~8,251 to ~6,200 estimated tokens.

**Estimated token savings**: ~2,050 tokens removed from orchestrator-role startup T1.

**Signal preservation**: workplan-scaffold SKILL.md becomes the canonical plan template. The agent file gains a `See: workplan-scaffold SKILL` citation. The review gate requirement ("every domain phase must be followed by a Review gate") must be explicitly included in both the SKILL and the agent file's summary — it is a fleet constraint that must be visible without loading the SKILL.

### Rec 3: Trim .github/agents/AGENTS.md GitHub Conventions to a Pointer Layer (Priority: High)

**Current state**: `.github/agents/AGENTS.md` (22,907 chars → 5,727 tokens, auto-loaded in agents scope) contains: convention propagation rule, GitHub label/issue conventions table, Projects v2 CLI prerequisites, subagent commit authority (duplicate of root AGENTS.md), and file write discipline (also in root AGENTS.md). The GitHub conventions section (~1,500 words) duplicates `docs/guides/github-workflow.md` with minor additions.

**Proposed state**: Reduce GitHub label/issue conventions to a 3-line pointer: "See `docs/guides/github-workflow.md` for full label namespace and PR workflow". Consolidate Projects v2 CLI into the guide. Remove subagent commit authority from this file (canonical version in root AGENTS.md L2). Unique agent-authoring constraints (agent file validation, fleet propagation rule) stay. Estimated reduction from 5,727 to ~2,400 tokens.

**Estimated token savings**: ~3,300 tokens removed from agents-scope instruction T1 load. Impact: significant for agent-authoring sessions (fleet development tasks).

**Signal preservation**: `docs/guides/github-workflow.md` receives the migrated content. The cross-reference from `.github/agents/AGENTS.md` makes navigation explicit. `gh` CLI quick-reference already lives in `docs/toolchain/gh.md`; pointer added there from the guide.

### Rec 4: Replace AGENTS.md § Async Process Handling Prose with Decision Table (Priority: Medium)

**Current state**: § Async Process Handling (534 words → ~668 tokens) in root AGENTS.md contains: narrative explanation of tool selection, timeout defaults table (10 rows), service readiness checks table (4 rows), retry/abort policy section. The canonical research synthesis lives at `docs/research/async-process-handling.md`.

**Proposed state**: Replace the narrative and timeout-defaults table with a 3-row Decision Table (the most-invoked patterns: `uv run`, `pytest`, and service startup) plus a cross-reference: "Full timeout reference: `docs/research/async-process-handling.md`". The service readiness table (4 rows) stays — it is used frequently enough to justify L2 placement. Reduce from ~668 to ~200 tokens in AGENTS.md.

**Estimated token savings**: ~470 tokens removed from startup T1.

**Signal preservation**: The research doc remains the canonical source. AGENTS.md retains the most-used patterns (the 80% case) inline. Full detail is one cross-reference away.

### Rec 5: Raise CRD of docs/guides/workflows.md from 0.06 to ≥ 0.25 (Priority: Medium)

**Current state**: `docs/guides/workflows.md` (55,527 chars → ~13,882 tokens, largest guide) has CRD=0.06 — only 1/17 references cite MANIFESTO or AGENTS. This guide contains prompt libraries and session patterns that agents consult when constructing delegations. Its axiom-disconnection means every section is drifting without a visible constraint anchor.

**Proposed state**: Add explicit axiom citations at the start of each major section (e.g., "Implements MANIFESTO.md Axiom 2 — Algorithms Before Tokens" before the Programmatic-First workflow section). Target: ≥ 0.25 CRD (≥ 4/17 references cite MANIFESTO or AGENTS). This guide is not auto-loaded so there are no token savings — the benefit is encoding fidelity: future authors extending the guide have visible axiom anchors for every section. Prevents the same drift documented in values-encoding.md § OQ-VE-5 for prompt-only constraint propagation.

**Estimated token savings**: 0 (guide not auto-loaded). Encoding fidelity gain: CRD increase from 0.06 → ≥ 0.25.

**Signal preservation**: axiom citations added, no content removed. Low risk.

---

## Sources

1. `docs/context_budget_target.md` — D1 baseline (2026-03-08) measurements, tier allocation policy, and intervention triggers. Primary reference for T1 token budget and growth forecasts.
2. `docs/research/values-encoding.md` — OQ-VE-5 cross-reference density analysis and empirical fidelity degradation rates across encoding layers.
3. `scripts/measure_cross_reference_density.py` — CRD values measured 2026-03-13. Fleet statistics: mean=0.458, median=0.50, stdev=0.292 across 62 files (36 agents + 13 skills + 13 guides).
4. `AGENTS.md` § Guiding Constraints and § Agent Communication — primary L2 fleet constraint document audited in this analysis.
5. `.github/agents/executive-orchestrator.agent.md` — primary L3 role file audited; largest agent file in fleet at 33,005 chars.
6. `docs/guides/workflows.md` — largest L5 guide; CRD=0.06 finding sourced from script run.
7. `docs/research/async-process-handling.md` — canonical L6 synthesis for async patterns; used as consolidation target for AGENTS.md § Async Process Handling.
8. Issue #239 — Substrate Rebalancing — Optimize Content Distribution for Agent Orientation (EndogenAI/dogma). Problem statement and acceptance criteria.
9. Issue #82 — Dogma neuroplasticity — T1 reduction via pruning (R2). Related intervention context.
10. Issue #79 — Skills as decision codifiers — T1 reduction via extraction (R1). Related extraction pattern.

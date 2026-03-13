# Workplan: Bubble Clusters as Substrate Mental Model — Milestone 7 Continuation

**Milestone**: [Value Encoding & Fidelity](https://github.com/EndogenAI/dogma/milestone/7)
**Date seeded**: 2026-03-09
**Status**: Active — open for pick-up
**Governing axiom**: Endogenous-First — read `docs/research/values-encoding.md` before acting on any phase
**Orchestrator**: Executive Orchestrator (any session picking up this milestone)

---

## Completed Issues (Closed — Do Not Re-Plan)

> The following issues were completed in prior sessions and have committed research docs or scripts.
> They are listed here for milestone completeness only. Do not create branches or PRs for these.

| Issue | Title | Artifact |
|-------|-------|---------|
| #85 | Context budget target | `docs/context_budget_target.md` |
| #84 | Doc interlinking / weave-links | `scripts/weave_links.py` |
| #80 | Queryable substrate | `scripts/query_docs.py` + `docs/research/queryable-substrate.md` |
| #78 | Provenance tracing | `scripts/audit_provenance.py` + `docs/research/provenance-tracing.md` |
| #75 | Handoff drift measurement | `docs/research/handoff-drift.md` |
| #73 | [4,1] encoding coverage audit | audit table in `docs/research/values-encoding.md` §6 |
| #71 | Drift detection scripts | `scripts/detect_drift.py` |
| #70 | 4-form encoding in MANIFESTO.md | committed MANIFESTO.md edits |
| #69 | Hermeneutics note | MANIFESTO.md "How to Read This Document" |
| #54 | Cross-reference density score | `scripts/audit_provenance.py` density metric |

---

## Objective

Execute the remaining open research issues in Milestone 7, anchored on the **bubble cluster substrate mental model** (#88). The bubble cluster model — where the system is a collection of discrete lower-dimensional bubbles (substrates) bounded by membranes that govern inter-substrate signal clarity — is a conceptual evolution of the "biological homology" framing in `docs/research/values-encoding.md`. Researching this model first (#88) unlocks the framing for all downstream encoding-extension and behavioral-testing work. Read `docs/research/values-encoding.md` in full before picking up any phase.

---

## Dependency Map

```
#88 (bubble clusters + neuroanatomy)  ──► #83 (external/client value architecture)
                                       └─► #72 (epigenetic tagging — AGENTS.md annotation)

#72 NOTE: already partially encoded in AGENTS.md §Context-Sensitive Amplification table;
          Phase B research = synthesis + formal doc, not implementation from scratch

#74 (LLM behavioral testing)          ──► soft dep on #13 (episodic memory infra)
                                           Constitutional AI scope can start independently

#76 (XML structuring in handoffs)     ──► standalone, no deps
#13 (episodic memory)                 ──► soft prereq for #74 (can run independently)
#14 (AIGNE AFS evaluation)            ──► standalone (informs #80 already done)
```

---

## Recommended Execution Order

---

### Phase A — Anchor: Bubble Clusters + Neuroanatomy ✅

**Issues**:

| Issue # | Title | Type | Effort |
|---------|-------|------|--------|
| #88 | Deep Dive Research - Bubble Clusters as Substrate Mental Model + Neuroanatomy | research | xl |

**Branch convention**: `research/bubble-clusters-phase-a-neuroanatomy`
**Agent**: Executive Researcher → Research Scout → Research Synthesizer → Research Reviewer → Research Archivist
**Depends on**: none — start here
**Gate deliverables**:
- [ ] `docs/research/bubble-clusters-substrate.md` committed with `Status: Final`
- [ ] Document covers: bubble/soap/bucket metaphor, neuroanatomical parallels (Allen Institute atlas), boundary membrane dynamics, echo chamber / socio-political dimension, mathematical bubble properties
- [ ] At least one `**Canonical example**:` and one `**Anti-pattern**:` in the Pattern Catalog section
- [ ] ≥ 2 explicit MANIFESTO.md axiom citations in the synthesis
- [ ] Issue #88 updated with comment linking to committed doc
- [ ] CI passes on PR

**Review gate**: Research Reviewer validates that the boundary-membrane framing is clearly distinguished from the existing biological-homology framing in `docs/research/values-encoding.md`, and that the Pattern Catalog contains concrete actionable implications for encoding methodology.

**Session notes (2026-03-09)**:
- Governing axiom confirmed: **Endogenous-First** — primary endogenous source: `docs/research/values-encoding.md`
- Bubble cluster model identified as conceptual evolution of §3 biological-homology framing in `values-encoding.md`
- Scout scaffolding sources: `values-encoding.md` §3 (Patterns 1–6, §H5), `docs/research/dogma-neuroplasticity.md`, `docs/research/skills-as-decision-logic.md`
- Phase A status updated: ⬜ → 🔄 → ✅ (complete — `docs/research/bubble-clusters-substrate.md` committed)
- Branch: `research/bubble-clusters-phase-a-neuroanatomy`

---

### Phase B — Encoding Extensions ✅

**Issues**:

| Issue # | Title | Type | Effort |
|---------|-------|------|--------|
| #83 | Research: encoding external product and client values — layered value architecture for adoptions | research | xl |
| #72 | Research: context-sensitive axiom amplification — epigenetic tagging for task-type routing | research | m |

**Branch convention**: `research/encoding-extensions-phase-b`
**Agent**: Executive Researcher → Research Scout (per issue) → Research Synthesizer → Research Reviewer → Research Archivist; Executive Docs for #72 (partial implementation already in AGENTS.md)
**Depends on**: Phase A complete (bubble cluster framing informs layered value architecture)
**Sequencing note**: #83 and #72 can be researched in parallel on separate branches; merge order does not matter

**Gate deliverables**:
- [ ] `docs/research/external-value-architecture.md` committed with `Status: Final` (issue #83)
- [ ] `docs/research/epigenetic-tagging.md` committed with `Status: Final` (issue #72)
- [ ] #72 doc explicitly cross-references the existing AGENTS.md § Context-Sensitive Amplification table as the implementation artifact; research frames the theoretical basis
- [ ] Issues #83 and #72 each updated with comment linking to their committed docs
- [ ] CI passes on both PRs

**Review gate**: Research Reviewer confirms #83 synthesis addresses both inbound adoption (external product values) and outbound encoding (client-facing substrate layers). Reviewer confirms #72 synthesis validates or extends the existing AGENTS.md table rather than duplicating it.

---

### Phase C — LLM Behavioral Testing ✅

**Issues**:

| Issue # | Title | Type | Effort |
|---------|-------|------|--------|
| #74 | Research: LLM behavioral testing for value fidelity (Constitutional AI self-critique as post-session hook) | research | l |

**Branch convention**: `research/llm-behavioral-testing-phase-c`
**Agent**: Executive Researcher → Research Scout → Research Synthesizer → Research Reviewer → Research Archivist
**Depends on**: Phase A (bubble cluster framing clarifies what "value fidelity" means at substrate boundaries); #13 is a soft prerequisite for the full test infrastructure section — if #13 is unresolved, scope to Constitutional AI self-critique only and note the dependency gap explicitly in the doc
**Gate deliverables**:
- [x] `docs/research/llm-behavioral-testing.md` committed with `Status: Final`
- [x] Document covers: Constitutional AI self-critique as post-session hook, value-fidelity test taxonomy, property-based testing patterns for agent outputs
- [x] If #13 (episodic memory) is still open, doc contains explicit "Dependency Gap" section noting what would unlock the full test framework
- [x] Issue #74 updated with comment linking to committed doc
- [x] CI passes on PR

**Review gate**: Research Reviewer confirms the post-session hook design is concrete enough to be implemented as a script (not just theory), and that the test taxonomy maps to specific MANIFESTO.md axioms.

---

### Phase D — Low-Effort / Loose Ends ✅

**Issues**:

| Issue # | Title | Type | Effort |
|---------|-------|------|--------|
| #76 | Research: XML structuring in handoffs.prompt fields for complex orchestration instructions | research | xs |
| #13 | [Research] Episodic and Experiential Memory for Agent Sessions | research | l |
| #14 | [Research] AIGNE AFS Context Governance Layer Evaluation | research | l |

**Branch convention**: `research/loose-ends-phase-d` (or one branch per issue for xs/l split)
**Agent**: Executive Researcher for #76 (xs — may delegate directly to Research Synthesizer); Research Scout → Synthesizer → Reviewer → Archivist for #13 and #14
**Depends on**: none — all three are standalone; #13 should be completed before requesting #74 full test-framework expansion
**Sequencing note**: #76 is xs effort and can be completed in a single sitting; #13 and #14 are l effort and may need separate branches

**Gate deliverables**:
- [x] OQ-12-4 resolution appended to `docs/research/xml-agent-instruction-format.md` Section 11 (issue #76)
- [x] `docs/research/episodic-memory-agents.md` committed with `Status: Final` (issue #13)
- [x] `docs/research/aigne-afs-evaluation.md` committed with `Status: Final` (issue #14)
- [x] All three issues updated with comments linking to their committed docs
- [x] CI passes

**Review gate**: Research Reviewer confirms #14 AIGNE AFS evaluation includes a concrete recommendation (adopt / monitor / skip) with explicit rationale tied to Local Compute-First axiom.

---

## Deferred / Dependent Issues

| Issue # | Title | Status | Demarcation |
|---------|-------|--------|-------------|
| ~~#82~~ | Research: dogma neuroplasticity | Research doc already exists | `docs/research/dogma-neuroplasticity.md` — issue #82 needs closure |
| ~~#81~~ | Research: deterministic agent components | Research doc already exists | `docs/research/deterministic-agent-components.md` — issue #81 needs closure |
| ~~#79~~ | Research: skills as decision codifiers | Research doc already exists | `docs/research/skills-as-decision-logic.md` — issue #79 needs closure |

---

## Acceptance Criteria (Milestone Close)

- [x] Phase A complete: `docs/research/bubble-clusters-substrate.md` committed, issue #88 closed
- [x] Phase B complete: `docs/research/external-value-architecture.md` and `docs/research/epigenetic-tagging.md` committed, issues #83 and #72 closed
- [x] Phase C complete: `docs/research/llm-behavioral-testing.md` committed, issue #74 closed
- [x] Phase D complete: all three research docs committed, issues #76, #13, #14 closed
- [x] Deferred issues closed: #82, #81, #79 closed with reference to their existing research docs
- [x] Executive Docs notified if any findings require updates to `AGENTS.md`, `MANIFESTO.md`, or guides
- [x] `docs/research/values-encoding.md` updated with a forward-reference to `docs/research/bubble-clusters-substrate.md` once Phase A is committed

---

## Session Start Checklist

Any future session picking up a phase must complete these steps before acting:

1. Read `docs/research/values-encoding.md` — the primary endogenous source for this milestone
2. Read this workplan (`docs/plans/2026-03-09-bubble-substrate-model.md`) and note which phase is active (⬜ = not started, 🔄 = in progress, ✅ = complete)
3. Check branch status: `git log --oneline -5` and `git branch`
4. Read today's scratchpad: `cat .tmp/main/$(date +%Y-%m-%d).md`
5. State the governing axiom: "Endogenous-First — scaffold from existing research docs before reaching for external sources"
6. Run `uv run python scripts/prune_scratchpad.py --init` if today's scratchpad does not exist

---

## Appendix: Untracked Recommendations from docs/research

**Scanning all `docs/research/**.md` files for recommendations and actionable items not currently tracked by any GitHub issue (open or closed).**

This appendix identifies research recommendations that are either:
- Not yet scoped to a GitHub issue
- Scoped to a related but broader issue where the specific recommendation is not independently captured
- Documentation edits or design guidance not yet formalized as an issue

### Untracked Recommendations (Priority Order)

#### 1. **validate_session.py — LLM Behavioral Testing Framework (Tier 1 Structural Audit)** 
- **Source**: [docs/research/llm-behavioral-testing.md](../research/llm-behavioral-testing.md#l205) (R1)
- **Scope**: Implement 7-check Tier 1 post-commit script for session scratchpad audits (non-blocking)
- **Acceptance criteria**: `σuv run python scripts/validate_session.py <scratchpad>` returns structured audit output; ≥80% test coverage
- **Related issue**: #74 (LLM behavioral testing) exists but focuses on Constitutional AI evaluation, not `validate_session.py` implementation spec
- **Status**: Not independently scoped

#### 2. **Tier 2 Behavioral Testing — Drift Detection (Deferred)**
- **Source**: [docs/research/llm-behavioral-testing.md](../research/llm-behavioral-testing.md#l205) (R3)
- **Scope**: Defer Tier 2 `validate_session.py --tier2` implementation until (a) local model stack confirmed, (b) issue #13 (episodic memory) resolved
- **Rationale**: Premature Tier 2 without local compute = external API call (violates Local Compute-First); single-session drift detection is weak without episodic memory baseline
- **Status**: Dependency condition not independently logged

#### 3. **Value Fidelity Test Taxonomy for AGENTS.md**
- **Source**: [docs/research/llm-behavioral-testing.md](../research/llm-behavioral-testing.md#l238) (R2)
- **Scope**: Add test taxonomy table to `AGENTS.md §Validate & Gate` as reference for Review agent and human reviewers
- **Rationale**: Operationalizes "value fidelity" — makes assertions explicit and testable
- **Status**: No issue

#### 4. **Membrane Permeability Specifications in AGENTS.md**
- **Source**: [docs/research/bubble-clusters-substrate.md](../research/bubble-clusters-substrate.md#l220) (B1 / R1)
- **Scope**: Add named "Boundary Specification" for each major research fleet handoff (Scout→Synthesizer, Synthesizer→Reviewer, Reviewer→Archivist)
- **Details**: Each spec lists permitted-signal list (preserve verbatim), compression-allowed list, and surface-tension budget (max token count)
- **Rationale**: Closes 100% canonical-example loss documented in B8 Degradation Table (values-encoding.md)
- **Status**: No issue

#### 5. **AI-as-Pressurizing-Medium Framing in Session Start Ritual**
- **Source**: [docs/research/bubble-clusters-substrate.md](../research/bubble-clusters-substrate.md#l281) (R5)
- **Scope**: Add one-sentence note to session-start encoding checkpoint: *"The agent fleet is the pressurizing medium — it gives each substrate coherent form but does not own the membrane or the bucket."*
- **Effort**: XS (documentation edit)
- **Status**: No issue

#### 6. **Evolutionary Pressure Test for Fleet Agent Audit**
- **Source**: [docs/research/bubble-clusters-substrate.md](../research/bubble-clusters-substrate.md#l260) (B3 / R3)
- **Scope**: Apply evolutionary pressure test to every `.github/agents/` file during fleet audit; agents lacking stability-tier and mutation-rate rationale must be merged or justified in `## Beliefs`
- **Rationale**: Prevents spurious agent boundary proliferation (equivalent of unnecessary cortical area demarcations)
- **Status**: No issue (design gate for fleet audit phase, not independent deliverable)

#### 7. **Operationalize generate_agent_manifest.py Connectivity Atlas**
- **Source**: [docs/research/bubble-clusters-substrate.md](../research/bubble-clusters-substrate.md#l247) (B2 / R2)
- **Scope**: (1) Document command and output format in `scripts/README.md`; (2) add manifest validation step to CI on PRs touching `.github/agents/`; (3) define threshold policy (e.g., density < 1 = PR warning) in `AGENTS.md`
- **Rationale**: Provides computable substrate health metric; closes `values-encoding.md §4 R6`; aligns with Algorithms Before Tokens (algorithmic audit replaces manual inspection)
- **Status**: No issue

#### 8. **BM25 Retrieval Tool Completion (scripts/query_docs.py)**
- **Source**: [docs/research/queryable-substrate.md](../research/queryable-substrate.md#l199) (R1–R3)
- **Scope**: Extend existing `scripts/query_docs.py` to include `toolchain` and `skills` scopes; add tests covering happy path, empty-scope error, and score-threshold logic (≥80% coverage)
- **Acceptance criteria**: `uv run python scripts/query_docs.py "programmatic-first" --scope agents --top-n 3` returns three highest-scoring paragraphs within 500 ms; tests pass
- **Related issue**: #80 (Queryable substrate) is CLOSED and `query_docs.py` exists; completion of scopes and test coverage not independently scoped
- **Status**: Partial artifact exists; refinement not tracked

#### 9. **Cross-Reference Link Registry & Automated Weaving Completion**
- **Source**: [docs/research/doc-interweb.md](../research/doc-interweb.md#l229) (R1–R2)
- **Scope**: (1) Create `data/link_registry.yml` with seed concepts; (2) implement `scripts/weave_links.py` with `--dry-run`, idempotency guard, `--scope` filter
- **Constraints**: No self-referential injection; validated as per Programmatic-First
- **Related issue**: #84 (Doc interlinking) is CLOSED and `weave_links.py` exists; YAML registry and scope filtering not confirmed as complete
- **Status**: Partial artifact exists; completion specifics not tracked

#### 10. **Propose_dogma_edit.py — Programmatic Back-Propagation Enforcer**
- **Source**: [docs/research/dogma-neuroplasticity.md](../research/dogma-neuroplasticity.md#l150) (R1)
- **Scope**: Implement script that enforces back-propagation evidence thresholds (3 sessions for T1/T2, 2 for T3) and generates ADR-style proposals automatically
- **Inputs**: `--input <scratchpad>`, `--tier T1|T2|T3`, `--affected-axiom <str>`, `--proposed-delta <str|->`, `--output <path>`
- **Spec**: Loads tier metadata, validates coherence, exit code 1 if T1 and coherence fails
- **Related issue**: #82 (dogma-neuroplasticity research) is CLOSED; implementation spec not independently scoped
- **Status**: No issue

#### 11. **Skill File Validation (validate_skill_files.py)**
- **Source**: [docs/research/agent-skills-integration.md](../research/agent-skills-integration.md#l255) (R7)
- **Scope**: Extend or create `validate_skill_files.py` covering frontmatter schema, name format, directory-name match, cross-reference density, minimum body length; add to CI lint job
- **Status**: No issue

#### 12. **Six Agent Skills — Tier 1 Implementation** (3 skills)
- **Source**: [docs/research/agent-skills-integration.md](../research/agent-skills-integration.md#l224) (R1–R3)
- **Tier 1 skills** (high-value duplicates):
  - `session-management`: scratchpad convention, session-start checkpoint, close protocol
  - `deep-research-sprint`: Scout→Synthesizer→Reviewer→Archivist sequence, D4 doc requirements
  - `conventional-commit`: Conventional Commits format, this repo's conventions
- **Rationale**: Reduce token duplication; each skill saves ~500 tokens per session
- **Related issue**: #62 (Implement Remaining Agent Skills) is CLOSED; verify all 6 Tier 1 + Tier 2 skills completed
- **Status**: Issue closed; implementation completeness not verified

#### 13. **Extended Agent Documentation Standard** (per-role documentation)
- **Source**: [docs/research/agent-taxonomy.md](../research/agent-taxonomy.md) (implied) + docs
- **Scope**: Create per-role documentation beyond `.agent.md` — canonical decision trees, tool matrices, worked examples in `docs/agents/[role-name]/`
- **Status**: Issue #65 (feat(docs): Extended agent documentation standard) is OPEN

#### 14. **Adopt Wizard Integration with client-values.yml**
- **Source**: [docs/research/external-value-architecture.md](../research/external-value-architecture.md#l172) (E1)
- **Scope**: Adopt wizard (`scripts/adopt_wizard.py`, issue #56) must generate `client-values.yml` stub pre-populated with `conflict_resolution` field and explanatory comment
- **Rationale**: Makes Deployment Layer constraint encoding explicit; prevents Core Layer override risk
- **Related issue**: #56 (feat: implement Adopt onboarding wizard) exists; specific `client-values.yml` seeding requirement is not independently scoped
- **Status**: Depends on #56; seeding requirement not captured

#### 15. **Add Deployment Layer Reading to Session Start Ritual**
- **Source**: [docs/research/external-value-architecture.md](../research/external-value-architecture.md#l177) (E2)
- **Scope**: Add conditional step to `AGENTS.md §Session Start Ritual`: If `client-values.yml` exists, read it after `AGENTS.md` and note constraints in `## Session Start`
- **Effort**: One bullet point in AGENTS.md
- **Status**: No issue

#### 16. **Extend validate_agent_files.py for Core Layer Impermeability Check**
- **Source**: [docs/research/external-value-architecture.md](../research/external-value-architecture.md#l186) (E3)
- **Scope**: Flag agent files citing `client-values.yml` as higher-priority than `MANIFESTO.md`/`AGENTS.md` (Supremacy Rule violation)
- **Rationale**: Algorithms Before Tokens — enforcement must be programmatic, not convention-based
- **Status**: No issue

#### 17. **Phase 1 AFS Integration — Index Session to AFS on Session Close**
- **Source**: [docs/research/aigne-afs-evaluation.md](../research/aigne-afs-evaluation.md#l203) (R4)
- **Scope**: Extend `prune_scratchpad.py --force` with `--index-afs` flag calling `scripts/index_session_to_afs.py`
- **Adoption gate**: Deferred until local embedding stack confirmed (Local Compute-First)
- **Related issue**: #14 (AIGNE AFS Context Governance) is OPEN; adoption gating conditions not independently scoped
- **Status**: Phase gate condition not captured as separate issue

#### 18. **SQLite-only Pattern A1 for AFS — FTS5 Keyword Index (Phase 1)**
- **Source**: [docs/research/aigne-afs-evaluation.md](../research/aigne-afs-evaluation.md#l191) (R2)
- **Scope**: Start with SQLite FTS5 keyword index before vector embeddings; respects Algorithms Before Tokens
- **Status**: Dependent on #14; specific pattern not independently logged

#### 19. **Session History Table in Scratchpad Template**
- **Source**: [docs/research/episodic-memory-agents.md](../research/episodic-memory-agents.md#l162) (M1)
- **Scope**: Add `## Session History` table to scratchpad template in `docs/guides/session-management.md`
- **Effort**: XS (editorial update, zero dependencies)
- **Rationale**: Zero-infrastructure episodic memory layer for multi-session tracking
- **Status**: No issue

#### 20. **Cognee Library Adoption (After Local Compute Baseline)**
- **Source**: [docs/research/episodic-memory-agents.md](../research/episodic-memory-agents.md#l173) (R3)
- **Scope**: When local compute baseline is confirmed, Cognee is the preferred library (native Ollama support, graph-based, local-first design)
- **Related issue**: #13 (Episodic and Experiential Memory) is OPEN; library selection criteria not independently surfaced
- **Status**: Recommendation deferred pending #13 + local compute setup completion

#### 21. **Product User Research Infrastructure (Six Recommendations)**
- **Source**: [docs/research/product-research-and-design.md](../research/product-research-and-design.md#l116) (R1–R6)
- **Scope**: 
  - R1: Add JTBD job statement to each `scripts/README.md` entry
  - R2: Add legibility & idempotency checklist to `CONTRIBUTING.md`
  - R3: Create pinned GitHub Discussion: "Friction & Feature Requests"
  - R4: Adopt README-driven development for new tools (convention)
  - R5: Implement prompt archaeology as post-sprint ritual (scan sessions for patterns → encode into `.agent.md` examples)
  - R6: Quarterly "voice of the user" synthesis run (Scout session → `docs/research/` summary)
- **Related issue**: #45 (Research: Product Definition) is OPEN but broader in scope; specific research infrastructure recommendations not independently captured
- **Status**: Framework recommendations exist; no dedicated issue for infrastructure setup

#### 22. **Documentation Site Improvements (Six Recommendations)**
- **Source**: [docs/research/oss-documentation-best-practices.md](../research/oss-documentation-best-practices.md#l220) (R1–R6)
- **Scope**:
  - R1: Create `CHANGELOG.md` (immediate, 10 min)
  - R2: Add CI badge + TOC to `README.md` (immediate, 20 min)
  - R3: Add dev environment setup to `CONTRIBUTING.md` (immediate, 15 min)
  - R4: Add MkDocs Material docsite (1–2 hours)
  - R5: Add link-checker (lychee) to CI (30 min)
  - R6: Run `validate_synthesis.py` in CI (15 min)
- **Related issues**: #25 (GitHub PM Setup) is CLOSED; individual doc improvements not independently tracked; #27 (CI/DX Hygiene) is CLOSED but may not cover all six
- **Status**: Specific improvements not individually scoped

#### 23. **Commit .vscode/mcp.json & Design Endogenic MCP Server**
- **Source**: [docs/research/local-mcp-frameworks.md](../research/local-mcp-frameworks.md#l215) (recommendations 1–2)
- **Scope**: 
  - Commit `.vscode/mcp.json` with GitHub MCP + endogenic filesystem server as default
  - Design `scripts/mcp_server.py` wrapping key project scripts as tools (delegate to Executive Scripter for spec)
- **Related issue**: #6 (Locally distributed MCP frameworks) is CLOSED; integration specifics not independently logged
- **Status**: No issue

#### 24. **BDI Framework for Agent File Sections**
- **Source**: [docs/research/methodology-review.md](../research/methodology-review.md#l143) (D2)
- **Scope**: Rename `.agent.md` sections to Beliefs / Desired outcomes / Intentions (BDI cognitive architecture framing)
- **Effort**: Zero implementation cost; significant clarity gain
- **Status**: No issue (design guidance)

#### 25. **Add Session History Forward Reference to values-encoding.md**
- **Source**: [docs/research/bubble-clusters-substrate.md](../research/bubble-clusters-substrate.md#l268) (R4)
- **Scope**: Add one-line forward reference from `docs/research/values-encoding.md` Related section: `[bubble-clusters-substrate.md](bubble-clusters-substrate.md) (bubble-cluster topology — additive model)`
- **Effort**: XS (documentation edit)
- **Status**: No issue

#### 26. **Canonical H-LAM/T Distinction in Docs (Substance vs. Substrate)**
- **Source**: [docs/research/sprint-C-h3-augmentive.md](../research/sprint-C-h3-augmentive.md#l163)
- **Scope**: 
  - Draft substrate-creation distinction in `docs/guides/mental-models.md` using Engelbart H-LAM/T framework
  - Audit session outputs for substrate ratio (commits to docs/, scripts/, .github/agents/)
  - Add Engelbart citation to MANIFESTO.md augmentation axiom
- **Rationale**: Grounds augmentation axiom in historical tradition; clarifies substance vs. substrate distinction
- **Status**: No issue

#### 27. **Deterministic Components: YAML FSM Specifications & Validators**
- **Source**: [docs/research/deterministic-agent-components.md](../research/deterministic-agent-components.md#l129)
- **Scope**:
  - R1: Create `data/delegation-gate.yml` (machine-readable routing table)
  - R2: Implement `scripts/validate_delegation_routing.py` (check routing declarations against canonical schema)
  - R3: Implement `scripts/validate_session_state.py` (FSM validator reading `data/phase-gate-fsm.yml`)
  - R4: Extract pre-review sweep to `scripts/pre_review_sweep.py` (testable, extensible)
  - Bonus: Annotate orchestrator steps with D/LLM tags
- **Rationale**: Operationalizes deterministic decision flows; replaces implicit agent judgment with explicit routing logic
- **Status**: `data/` files exist (phase-gate-fsm.yml confirmed in workspace); validators not scoped as separate issue

#### 28. **Extend GitHub Project Management — Rulesets, Discussions, Auto-Labeling**
- **Source**: [docs/research/github-project-management.md](../research/github-project-management.md#l319)
- **Scope**:
  - R1: Seed label taxonomy via `scripts/seed_labels.py` reading `data/labels.yml` (immediate, 30 min)
  - R2: Create GitHub Project with Priority field + Board view (15 min)
  - R3: Migrate issue templates to YAML forms (45 min)
  - R4: Add `area:` auto-label workflow via `.github/labeler.yml` (20 min)
  - R5: Add stale bot (15 min)
  - R6: Document `gh auth refresh -s project` in `CONTRIBUTING.md` (5 min)
- **Related issue**: #25 (GitHub PM Setup) is CLOSED; detailed sequencing and specific recommendations not independently surfaced
- **Status**: Framework exists (#25); individual automation tasks not granularly tracked

#### 29. **Commit discipline: Inline D/LLM annotations for agent orchestration**
- **Source**: [docs/research/deterministic-agent-components.md](../research/deterministic-agent-components.md#l148)
- **Scope**: Annotate orchestrator steps with `<!-- D -->` (deterministic) or `<!-- L -->` (LLM-required) comments; makes the 63/37 split visible and auditable
- **Effort**: Editorial annotation
- **Status**: No issue

---

### Summary Table

| Count | Category | Notes |
|-------|----------|-------|
| **29** | Total untracked recommendations extracted | — |
| **8** | Have related but broader GitHub issues | Specifics not independently scoped (#45, #56, #62, #65, #74, #80, #82, #84) |
| **21** | No GitHub issue exists | — |
| **5** | Documentation edits only (XS effort) | Can be batched into single PR |
| **4** | Deferred by dependency gate | Depend on #13, #14, local compute setup, or prior phase completion |
| **3** | Already partially complete | Artifact exists; refinement/scope extension not tracked  |

---

### Recommended Next Steps

**✅ COMPLETED (2026-03-09)**:
- Issue seeding delegation to Executive PM: All 29 research recommendations extracted and scoped as issues #112–#140 in "Action Items from Research" milestone
- Step 2: Create issue for validate_session.py implementation spec (recommendation #1) → **#112** ✅
- Step 3: Create issue for BM25 scope completion (recommendation #8) → **#119** ✅

**REMAINING ACTION ITEMS**:

1. **Batch process XS documentation edits** (5 issues: #116, #126, #130, #135, #136, #140)
   - Scope: AI-pressurizing-medium framing, deployment-layer reading, session history forward reference, session history table addition, BDI framework, D/LLM annotations
   - Effort: Single PR, ~30 min total
   - Issues: #116, #126, #130, #135, #136, #140

2. **Schedule quarterly user research synthesis** (recommendation #21 / R6)
   - Lightweight process gate for "voice of the user" synthesis
   - Related issue: #132

3. **Verify #62 (Agent Skills) completion**
   - Confirm all 6 Tier 1 + Tier 2 skills are committed, tested, and integrated
   - Related issue: #123

4. **Defer external API vectorization**
   - All embedding/AFS work blocked on local compute baseline confirmation
   - Related issues: #128, #129, #131, #17 (gating condition: local compute foundation)


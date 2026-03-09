# Workplan: Value Encoding & Fidelity Research Agenda

**Milestone**: [Value Encoding & Fidelity](https://github.com/EndogenAI/Workflows/milestone/7)
**Date seeded**: 2026-03-08
**Status**: Active — open for pick-up
**Governing axiom**: Endogenous-First — every session must read `docs/research/values-encoding.md` before acting
**Orchestrator**: Executive Orchestrator (any session picking up this milestone)

---

## Objective

Execute the full Value Encoding & Fidelity milestone: deepen the endogenic substrate's ability to preserve value signal across all layers of the inheritance chain (MANIFESTO.md → AGENTS.md → agent files → session behavior), make enforcement programmatic, make the substrate queryable and self-referential, and establish a governed process for the dogma to evolve through neuroplasticity.

**Primary research document**: [`docs/research/values-encoding.md`](../research/values-encoding.md) — Final synthesis that generated all issues in this milestone. Read it in full before picking up any issue.

---

## Dependency Map

```
#73 ([4,1] audit)           ──► #70 (4-form encoding MANIFESTO)
#69 (hermeneutics note)     ──► standalone, no deps — start here
#85 (context budget)        ──► coordinates and prioritises interventions below:
    ├─► #80 (queryable docs)
    ├─► #79 (skills-as-decision)
    ├─► #81 (deterministic components)
    └─► #82 (neuroplasticity)
#54 (cross-ref density)     ──► #78 (provenance tracing)
#71 (drift detection)       ──► #78 (provenance tracing)
#75 (handoff drift)         ──► #85 (context budget signal)
#72 (epigenetic tagging)    ──► #79 (skills-as-decision)
#83 (external values)       ──► deferred until #69 + #70 complete
#84 (doc interweb)          ──► staged: #54 first, then #84
#74 (LLM behavioral test)   ──► deferred until local compute (#13 prereq)
#76 (XML handoffs)          ──► standalone, low priority
#13 (episodic memory)       ──► prerequisite for #74
#14 (AIGNE AFS)             ──► informs #80 and #85
```

---

## Recommended Execution Order

Phases are ordered by impact-to-cost ratio and dependency satisfaction. Each phase should run as its own branch + PR.

---

### Phase 1 — Quick Wins (no external dependencies)

**Issues**: #69, #73
**Branch convention**: `feat/value-encoding-phase-1-quick-wins`
**Agent**: Executive Docs (#69), Explore subagent for audit work (#73)
**Status**: ✅ Complete — PR #86 (pending merge to main)

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #69 | Add hermeneutics note to MANIFESTO.md | docs | xs |
| #73 | [4,1] encoding coverage audit | chore | xs |

**Gate deliverables**:
- [x] `MANIFESTO.md` updated with "How to Read This Document" note (exact text in issue body) *(done ce8ee48 / PR #53 — pre-existing)*
- [x] `AGENTS.md` cross-reference updated to cite the hermeneutics note *(done PR #86)*
- [x] Audit table committed to `docs/research/values-encoding.md` §6 appendix *(done PR #86)*
- [x] Priority-ordered gap list ready to drive Phase 3 *(done PR #86)*
- [x] CI passes; changes committed and PR opened *(PR #86 — all CI green)*

**Review gate**: Review agent validates MANIFESTO.md edit against existing axiom structure — no contradictions, no axiom reordering.

---

### Phase 2 — Context Budget (the meta-issue)

**Issue**: #85
**Branch convention**: `research/context-window-budget`
**Agent**: Executive Researcher → Research Scout
**Status**: ✅ Complete — branch `research/context-window-budget`

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #85 | Context window budget — balance dogma volume against adherence degradation | research | m |

This phase is the **measurement baseline** for the entire milestone. Its findings determine which of the four intervention categories (compression / retrieval / extraction / pruning) to prioritise in later phases. Run this before committing to heavy implementation work.

**Gate deliverables**:
- [x] Baseline measurement: instruction context fraction in a sample Executive Orchestrator session *(D1: ~14,375 tokens fixed load; INCONCLUSIVE — scale-dependent at 32K–200K context)*
- [x] Degradation threshold identified *(D2: CONFIRMED — adherence degrades when instruction fraction ≤15–20% of total in-context tokens)*
- [x] Ranked intervention recommendations with cost/impact *(D3: R1 Extraction > R2 Pruning > R3 RAG > R4 Compression)*
- [x] `docs/research/context-budget-balance.md` committed (Final status) — commit `8447fc4`
- [x] `docs/context_budget_target.md` policy draft — commit `aa940b2`

**Review gate**: Research Reviewer validates synthesis quality per D4 standard.

### Phase 2 Detailed Checklist

**Issue**: #85 | **Branch**: `research/context-window-budget` (off `feat/value-encoding-fidelity`)

---

#### Step 1 — Branch Setup
**Owner: Executive Orchestrator**

- [x] Ensure `feat/value-encoding-fidelity` is up to date: `git fetch origin && git checkout feat/value-encoding-fidelity && git pull`
- [x] Create branch: `git checkout -b research/context-window-budget`
- [x] Push branch: `git push -u origin research/context-window-budget`
- [x] Verify: `git branch -vv` confirms tracking remote

---

#### Step 2 — Pre-Flight Source Cache Warm
**Owner: Executive Orchestrator**

- [x] Warm cache: `uv run python scripts/fetch_all_sources.py`
- [x] Check priority URLs before fetching (re-fetching cached sources wastes tokens):

| URL to survey | Topic |
|---|---|
| Anthropic prompt caching docs | Instruction caching strategies |
| LangChain context management guide | Retrieval-augmented governance |
| `tiktoken` library docs (OpenAI/PyPI) | Token measurement methodology |
| Lilian Weng "Prompt Engineering" (lilianweng.github.io) | Instruction compression patterns |
| `docs/research/values-encoding.md` (endogenous) | Pattern 7, R2 — retrieval-augmented governance |

- [x] Read `.cache/sources/` listing post-warm: confirm ≥ 3 relevant sources cached before Scout begins

---

#### Step 3 — Scratchpad Init
**Owner: Executive Orchestrator**

- [x] Run: `uv run python scripts/prune_scratchpad.py --init`
- [x] Confirm active scratchpad at `.tmp/research-context-window-budget/2026-03-08.md`
- [x] Write `## Session Start` with governing axiom (Endogenous-First) and primary endogenous source (`docs/research/values-encoding.md`)

---

#### Step 4 — Research Delegation Brief to Executive Researcher
**Owner: Executive Orchestrator (hands off to Executive Researcher)**

Delegate with this scope:

> **Research question**: How do we prevent instruction volume from saturating the session context window while preserving full fidelity of encoded values?
>
> **Hypotheses to validate** (structured verdict blocks required):
> - Q1: Instruction context fraction in a typical Executive Orchestrator session exceeds 30% of usable context
> - Q2: Adherence measurably degrades above a measurable instruction-to-task ratio
> - Q3: Retrieval-augmented governance (Pattern 7 from `values-encoding.md`) yields the best cost/impact ratio among: compression / retrieval / extraction / pruning
>
> **Cross-references required** (read before writing):
> - `docs/research/values-encoding.md` §3 Pattern 7 and §4 R2
> - Issues #14 (AIGNE AFS), #13 (episodic memory), #75 (handoff drift), #80 (queryable docs), #79 (skills-as-decision), #82 (neuroplasticity)
>
> **Exclusions**: Do not modify MANIFESTO.md, AGENTS.md, or any agent file. Research-read and synthesis-write only.

---

#### Step 5 — Research Scout Survey
**Owner: Research Scout (under Executive Researcher)**

- [x] Survey the pre-warmed cache and fetch any missing priority sources
- [x] Measure token counts for instruction layers using tiktoken methodology:
  - `AGENTS.md` alone
  - Executive Orchestrator system prompt (estimated)
  - Full session context at a typical mid-session state
- [x] Return compressed handoff (≤ 2,000 tokens) to scratchpad under `## Scout Output`

---

#### Step 6 — Synthesizer Produces D4 Document
**Owner: Research Synthesizer**

**Target file**: `docs/research/context-budget-balance.md`

**Required D4 frontmatter**:
```yaml
---
title: "Context Window Budget — Research Synthesis"
status: Draft
---
```

**Required section outline**:
```
# Context Window Budget — Research Synthesis
## 1. Executive Summary
## 2. Hypothesis Validation
  ### Q1 — Instruction Fraction Baseline   (Verdict: CONFIRMED/REFUTED/INCONCLUSIVE/DEFERRED)
  ### Q2 — Adherence Degradation Threshold (Verdict: …)
  ### Q3 — Intervention Cost/Impact Ranking (Verdict: …)
## 3. Pattern Catalog   (≥ 3 patterns; each: Name, Evidence, Endogenous applicability)
## 4. Recommendations  (Ranked R1–R4; each: Action, Cost, Impact, Depends-on issue)
## 5. Sources
```

**Cross-reference requirement**: ≥ 1 explicit reference to `../../MANIFESTO.md` or `../../AGENTS.md` before closing `## 4. Recommendations`.

---

#### Step 7 — Policy Document Draft
**Owner: Research Synthesizer (same pass as D4 doc)**

**Target file**: `docs/context_budget_target.md`

**Required schema**: status header, Tiers table (T1 Instruction / T2 Session / T3 Output / T4 Reserve with budget ceilings derived from D1 baseline), Intervention Triggers table, Derivation section referencing synthesis, Related Issues list (#85, #80, #13).

---

#### Step 8 — Reviewer Validation Gate
**Owner: Research Reviewer**

- [x] Run: `uv run python scripts/validate_synthesis.py docs/research/context-budget-balance.md` (must exit 0)
- [x] YAML frontmatter has `title` and `status`; all five required headings present in order
- [x] ≥ 3 hypothesis verdicts recorded; ≥ 1 MANIFESTO/AGENTS cross-reference
- [x] Update `status: Draft` → `status: Final` after checklist passes
- [x] Record Reviewer verdict in scratchpad under `## Reviewer Verdict`

---

#### Step 9 — Commit Sequence
**Owner: Research Archivist**

```bash
git add docs/research/context-budget-balance.md docs/research/sources/
git commit -m "docs(research): add context-budget-balance synthesis — status: Final

Closes #85. D4 synthesis: D1 baseline, D2 threshold, D3 ranked interventions.
Refs #14, #13, #75, #80, #79, #82"

git add docs/context_budget_target.md
git commit -m "docs: add context_budget_target.md policy draft"

git push origin research/context-window-budget
```

---

#### Step 10 — Workplan Update & Issue Close
**Owner: Research Archivist**

- [x] Mark Phase 2 gate deliverables `[x]` in this workplan
- [x] Write close comment to temp file and post: `gh issue comment 85 --body-file /tmp/issue-85-close.md`
- [x] Close: `gh issue close 85` then verify: `gh issue view 85`

---

#### Acceptance Criteria Summary

| Deliverable | Path | Status check |
|---|---|---|
| D1 baseline | §2 Q1 in synthesis | Reviewer verdict |
| D2 threshold | §2 Q2 in synthesis | Reviewer verdict |
| D3 recommendations | §4 in synthesis | `validate_synthesis.py` exit 0 |
| D4 synthesis doc | `docs/research/context-budget-balance.md` | `status: Final` in frontmatter |
| D5 policy draft | `docs/context_budget_target.md` | Committed on branch |
| CI | branch CI | `gh run list --limit 3` all green before PR |

---

### Phase 3 Handoff Prompt

Use this prompt to start the Phase 3 session in a new context window:

```
@Executive Orchestrator Please continue the Value Encoding & Fidelity milestone — Phase 3.

- **Workplan**: `docs/plans/2026-03-08-value-encoding-fidelity.md`
- **Scratchpad**: `.tmp/feat-value-encoding-fidelity/<YYYY-MM-DD>.md` (today's date)
- **Governing axiom**: Endogenous-First
- **Milestone**: https://github.com/EndogenAI/Workflows/milestone/7

Before acting:
1. Run `uv run python scripts/prune_scratchpad.py --init` and read the scratchpad `## Session Summary`
2. Confirm PR #86 is merged to `feat/value-encoding-fidelity`: `gh pr view 86 --json state,baseRefName` → `MERGED → feat/value-encoding-fidelity`
3. Create branch off `feat/value-encoding-fidelity` (NOT main — PR #86 targets the milestone integration branch):
   `git checkout feat/value-encoding-fidelity && git pull && git checkout -b feat/value-encoding-phase-3-four-forms`
4. Read the Phase 3 section of this workplan (issue #70 — Encode Four Forms)
5. Read `docs/research/values-encoding.md` §6 in full — the audit gap list is the inventory for Phase 3
6. Write `## Session Start` citing Endogenous-First and this workplan as the primary endogenous source
7. Delegate a detailed Phase 3 checklist to Executive Planner; review and update it as needed, then append to the workplan under `### Phase 3`
8. Then delegate Phase 3 execution to Executive Docs

Last committed: `a2a445f` (research/context-window-budget — Phase 2 sprint + session retrospective)
Active phase: Phase 3 — Encode the Four Forms (issue #70)
Key input: values-encoding.md §6 — Endogenous-First F2 (canonical example) is highest-priority gap; EF-F4 and LCF-F4 are ⚠️ (behavioural, not CI-enforced)
Note: Phase 3 is COMPLETE as of 2026-03-08 — this prompt is preserved as historical record. See Phase 3 status in the workplan body.
```

---

### Phase 3 — Encode the Four Forms

**Issue**: #70
**Branch convention**: `feat/value-encoding-phase-3-four-forms`
**Agent**: Executive Docs
**Depends on**: Phase 1 (#73 audit output as the gap inventory)
**Status**: ✅ Complete — commit `399741f`, Review APPROVED, PR pending
**Checklist**: ✅ Delegated to Executive Planner — commit `a6f6786`

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #70 | Encode each core axiom in 4 forms (principle + example + anti-pattern + gate) | docs | s |

**Gate deliverables**:
- [x] MANIFESTO.md updated: canonical examples (form 2) for all three axioms + Programmatic-First, Documentation-First, Minimal Posture, Compress Context, Isolate Invocations, Validate & Gate
- [x] MANIFESTO.md updated: LCF-F4 reframed as intentional-design gate (not a gap)
- [x] Changes informed by #73 audit gap list (no redundant additions) — verified by Review agent
- [x] CI passes — 296 tests, ruff clean — commit `399741f`

**Review gate**: ✅ APPROVED 2026-03-08

### Phase 3 Detailed Checklist

**Issue**: #70 | **Branch**: `feat/value-encoding-phase-3-four-forms` | **Agent**: Executive Docs

---

#### Group A — Setup

- [x] **1. Branch guard**: Confirm PR #86 is merged to `feat/value-encoding-fidelity` (`gh pr view 86 --json state,baseRefName -q '"\(.state) → \(.baseRefName)"'` → `MERGED → feat/value-encoding-fidelity`); ✅ confirmed 2026-03-08T22:35:08Z.
- [x] **2. Branch creation**: `git checkout feat/value-encoding-fidelity && git pull && git checkout -b feat/value-encoding-phase-3-four-forms` — ✅ done 2026-03-08. Note: PR #86 merged to `feat/value-encoding-fidelity` (milestone integration branch), not to `main`. Phase 3 branch correctly based off this branch.
- [x] **3. Pre-read sources** (read before touching any file):
  - `docs/research/values-encoding.md` §6 gap list — the complete audit inventory
  - `MANIFESTO.md` lines 82–102 (EF section), lines 124–162 (LCF section), lines 165–250 (Guiding Principles)
  - This workplan Phase 3 gate deliverables as the completion criterion

---

#### Group B — Core Axiom Edits

- [x] **4. EF-F2 — Endogenous-First canonical example** *(HIGHEST PRIORITY)*: Insert a `**Canonical example**:` block immediately before the `**Programmatic gate**:` line in the Endogenous-First section. Content must show a concrete before/after contrast: session A opens by reading `AGENTS.md` + the active scratchpad before delegating (endogenous-first posture); session B drops straight into Copilot Chat and re-invents conventions already encoded (vibe-coding posture). Verification: `grep -n "Canonical example" MANIFESTO.md` shows a new match in the EF block (line ~101).

- [x] **5. LCF-F4 — Formalise human-judgment gate as intentional design**: In the Local Compute-First `**Programmatic gate**:` block, replace the sentence `No hard CI gate exists for this axiom — it requires human judgment at code review and conversation review; the gate is the Augmentive Partnership itself.` with a positive statement that makes the human-judgment gate an **explicit architectural decision**, not a gap acknowledgment. Pattern: `The absence of a CI gate is intentional — cloud-model usage detection requires semantic context that no static linter can evaluate; the gate is the Augmentive Partnership review step, a deliberate design choice consistent with ADR-002 (kanban, human judgment at each phase boundary) and recorded as such.` Verification: the word "gap" or "no hard CI gate" does not appear in the LCF block.

---

#### Group C — Guiding Principles Additions (in priority order)

- [x] **6. Programmatic-First F2 + F3**: Append a `**Canonical example**:` block and an `**Anti-pattern**:` block after the existing principle prose and before the next section heading.
  - F2: A commit history where the same data-extraction task (e.g., extracting citation metadata) was run interactively twice, then encoded as `scripts/format_citations.py` on the third occurrence — cite this script as the repo's canonical instance.
  - F3: Running `gh issue list` manually in each session to check open issues instead of encoding that check into a script — the information is re-discovered at token cost every time.

- [x] **7. Documentation-First F2 + F3**: Append `**Canonical example**:` and `**Anti-pattern**:` blocks after the existing principle prose.
  - F2: Adding `scripts/fetch_source.py` to `scripts/` with a module-level docstring, an entry in `scripts/README.md`, and a `tests/test_fetch_source.py` file — the triple completion signal; all three must land in the same commit.
  - F3: Merging a working script with no docstring and no `scripts/README.md` entry — the knowledge it encodes is invisible to the next agent or human; the substrate did not grow.

- [x] **8. Minimal Posture F2 + F3**: Append `**Canonical example**:` and `**Anti-pattern**:` blocks after the existing principle prose (before `### Testing-First`).
  - F2: `scripts/prune_scratchpad.py --init` — does one thing (init the daily scratchpad file), returns one value (the file path), loads nothing it does not need.
  - F3: An agent file that pre-loads all 42 sibling agents' instruction bodies into its system prompt "just in case" one is relevant — N×context overhead for 0 marginal value per invocation.

---

#### Group D — Label Renames (mechanical)

- [x] **9. Convert three `**Empirical basis**:` labels to `**Canonical example**:`**: In the Guiding Principles section, find and replace the `**Empirical basis**:` label (bold prefix only, not the content) in each of the three affected principles:
  - `Compress Context, Not Content`
  - `Isolate Invocations, Parallelize Safely`
  - `Validate & Gate, Always`
  Verification: `grep -n "Empirical basis" MANIFESTO.md` returns zero matches.

---

#### Group E — Validation & Close

- [x] **10. Redundancy check**: Re-read `docs/research/values-encoding.md` §6 gap list. Confirm every addition corresponds to a listed gap — no new blocks were added beyond what the audit specified.

- [x] **11. Pre-commit validation**:
  ```bash
  uv run ruff check scripts/ tests/
  uv run ruff format --check scripts/ tests/
  uv run pytest tests/ -x -m "not slow and not integration" -q
  ```
  All three must exit 0. `MANIFESTO.md` has no test coverage — no pytest change expected.

- [x] **12. Commit + push**: Single atomic commit — `docs(manifesto): encode four forms for all axioms and guiding principles (#70)`. Body summarises each of the 6 edit groups (A–D).

- [x] **13. PR + CI**: `gh pr create --title "docs(manifesto): encode four forms for all axioms and guiding principles" --body-file <tmp>` (write body to temp file). Wait for CI green: `gh run list --limit 3`. Fix any lint failures before requesting review. Verify: `gh pr view` shows CI status passing.

---

### Phase 3 Acceptance Criteria (self-check before marking complete)

| Check | Verification command / observable |
|-------|----------------------------------|
| EF has all 4 forms | `grep -A2 "Endogenous-First" MANIFESTO.md` shows principle, canonical example (new), 2× anti-patterns, gate |
| ABT has all 4 forms | Already complete (PR #86) — confirm no regression |
| LCF-F4 reframed | Sentence `No hard CI gate` absent from LCF block |
| PF has F2 + F3 | `grep -A5 "Programmatic-First" MANIFESTO.md` shows canonical example + anti-pattern |
| DF has F2 + F3 | Same pattern for `Documentation-First` |
| MP has F2 + F3 | Same pattern for `Minimal Posture` |
| Empirical basis removed | `grep -c "Empirical basis" MANIFESTO.md` = 0 |
| CI green | `gh run list --limit 1 --json conclusion -q '.[0].conclusion'` = `success` |

---

### Phase 3 → 4 Handoff Prompt

Use this prompt to start the Phase 4 session in a new context window:

```
@Executive Orchestrator Please continue the Value Encoding & Fidelity milestone — Phase 4.

- **Branch**: feat/value-encoding-fidelity (create feat/value-encoding-phase-4-programmatic off this)
- **Workplan**: docs/plans/2026-03-08-value-encoding-fidelity.md
- **Scratchpad**: .tmp/feat-value-encoding-fidelity/<YYYY-MM-DD>.md
- **Governing axiom**: Endogenous-First

Before acting:
1. Run `uv run python scripts/prune_scratchpad.py --init` and read today's scratchpad
2. Run `git checkout feat/value-encoding-fidelity && git pull` to confirm Phase 3 (PR #89) is merged
3. Run `git log --oneline -5` and `git status`
4. Read the Phase 4 section of this workplan (issues #54, #71, #78)
5. Read docs/research/values-encoding.md for programmatic fidelity context
6. Write `## Session Start` citing governing axiom and this workplan as primary endogenous source
7. Delegate a detailed Phase 4 checklist to Executive Planner; append under `### Phase 4`
8. Then delegate Phase 4 execution to Executive Scripter (leads) and Research Scout (#78)

Active phase: Phase 4 — Programmatic Fidelity Infrastructure (issues #54, #71, #78)
Issue order: #54 first (density score), then #71 (drift detection), then #78 (provenance tracing)
Depends on: Phase 3 (PR #89) merged to feat/value-encoding-fidelity
```

---

### Phase 4 — Programmatic Fidelity Infrastructure

**Issues**: #54, #78, #71
**Branch convention**: `feat/value-encoding-phase-4-programmatic`
**Agent**: Executive Scripter (leads), Research Scout (for #78 survey)
**Status**: 🔄 In progress — 2026-03-08
**Checklist**: ✅ Delegated to Executive Planner — see `### Phase 4 Detailed Checklist` below

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #54 | `generate_agent_manifest.py` cross-reference density score | feature | s |
| #71 | Semantic drift detection for agent files | research | m |
| #78 | Programmatic value signal provenance — `audit_provenance.py` | research | l |

#54 first (density count), then #71 (drift detection), then #78 (provenance tracing that builds on both).

**Gate deliverables**:
- [ ] `generate_agent_manifest.py` emits per-agent cross-reference density score and fleet average
- [ ] `scripts/detect_drift.py` (or `validate_agent_files.py --semantic`) prototype with per-agent drift score
- [ ] `scripts/audit_provenance.py` prototype with per-file provenance report
- [ ] Tests for all new scripts (≥80% coverage each)
- [ ] CI integration decision documented for each script

**Review gate**: Review agent validates new scripts don't introduce security issues (SSRF, injection) and follow AGENTS.md programmatic-first conventions.

---

### Phase 4 Detailed Checklist

**Issues**: #54 → #71 → #78 | **Branch**: `feat/value-encoding-phase-4-programmatic`
**Execution order**: Sequential — #54 completes before #71 begins; #78 requires both #54 and #71 outputs.

---

#### Group A — Setup
**Owner: Executive Orchestrator**

- [x] **1. Branch guard**: PR #89 confirmed MERGED to `feat/value-encoding-fidelity` — done 2026-03-08
- [x] **2. Branch creation**: `git checkout -b feat/value-encoding-phase-4-programmatic` off `origin/feat/value-encoding-fidelity` — done 2026-03-08
- [x] **3. Push tracking**: `git push -u origin feat/value-encoding-phase-4-programmatic` — done 2026-03-08
- [ ] **4. Pre-read endogenous sources** (read before touching any file):
  - `docs/research/values-encoding.md` §4 R3 (programmatic enforcement), §6 gap list
  - `scripts/generate_agent_manifest.py` lines 1–537 (full read — understand `process_agent_file()`, `build_manifest()`, `format_markdown()`, `main()`)
  - `tests/test_remaining_scripts.py` — locate `TestGenerateAgentManifest` class (4 placeholder stubs)
- [x] **5. Scratchpad check**: Session Start written 2026-03-08 with governing axiom (Endogenous-First) and this workplan as primary endogenous source.

---

#### Group B — Issue #54: Cross-Reference Density Score
**Owner: Executive Scripter**

**B1 — Implement density counting in `generate_agent_manifest.py`**

- [ ] **6. Read `process_agent_file()`** fully to understand dict keys currently returned (`name`, `description`, `tools`, `posture`, `capabilities`, `handoffs`, `file`).
- [ ] **7. Add `count_cross_ref_density(content: str) -> int` helper function** before `process_agent_file()`. Rules:
  - Count unique lines containing any of: `MANIFESTO.md`, `AGENTS.md`, `docs/guides/`
  - Return integer count (distinct lines — not total occurrences)
  - Include module docstring update: add `cross_ref_density` to Outputs description.
- [ ] **8. Wire density into `process_agent_file()`**: add `cross_ref_density` key to the returned dict.
- [ ] **9. Add fleet-wide average to `build_manifest()`**: compute `avg_cross_ref_density`; store on manifest dict (guard against empty list).
- [ ] **10. Add density warning in `build_manifest()`**: for agents where `cross_ref_density < 1`, emit `logging.warning()` with agent name. Not a raised exception — warning only.
- [ ] **11. Expose in `format_markdown()`**: append a `## Cross-Reference Density` section; table `Agent | cross_ref_density`; fleet average line below.
- [ ] **12. Expose in JSON output**: confirm `cross_ref_density` per-agent and `avg_cross_ref_density` at manifest root.

**B2 — Update `TestGenerateAgentManifest` in `tests/test_remaining_scripts.py`**

- [ ] **13. Read existing test class** (4 stubs; all `assert True`) to locate line numbers before editing.
- [ ] **14. Replace stub `test_reads_all_agent_files`**: verify JSON output contains ≥1 agent entry. `@pytest.mark.io`
- [ ] **15. Replace stub `test_outputs_json_manifest`**: assert `cross_ref_density` per-agent and `avg_cross_ref_density` at root. `@pytest.mark.io`
- [ ] **16. Replace stub `test_outputs_markdown_manifest`**: assert `## Cross-Reference Density` heading + `|` table row present. `@pytest.mark.io`
- [ ] **17. Replace stub `test_includes_agent_metadata`**: assert `name`, `description`, `cross_ref_density` keys per agent. `@pytest.mark.io`
- [ ] **18. Add `test_count_cross_ref_density_unit`**: unit tests: empty → 0; one `MANIFESTO.md` ref → 1; `MANIFESTO.md` + `AGENTS.md` → 2; same ref repeated → still 1 per line; `docs/guides/` → 1. No I/O markers.
- [ ] **19. Add `test_low_density_warning_emitted`**: fake agent with `cross_ref_density=0`; call `build_manifest()` + assert WARNING log message emitted with agent name.

**B3 — Fleet Manifest Regeneration + PR Note**

- [ ] **20. Run coverage**: `uv run pytest tests/test_remaining_scripts.py::TestGenerateAgentManifest --cov=scripts/generate_agent_manifest -q` — must reach ≥80%.
- [ ] **21. Regenerate manifest**: verify exact flags via `--help`, then `uv run python scripts/generate_agent_manifest.py --output .github/agents/manifest.json`.
- [ ] **22. Note low-density agents**: copy WARNING lines to `/tmp/phase4-pr-body.md` under `## Density Warnings`.

---

#### Group C — Issue #71: Semantic Drift Detection
**Owner: Research Scout (survey D1) → Executive Scripter (implementation D2–D4)**

**C1 — Survey Phase (Research Scout)**

- [ ] **23. Check source cache**: `uv run python scripts/fetch_source.py <sbert_url> --check` before fetching.
- [ ] **24. Survey watermark-phrase approach**: identify 3–5 canonical watermark phrases from `docs/research/values-encoding.md` §3; estimate false-negative rate.
- [ ] **25. Survey embedding-similarity approach**: `sentence-transformers` (PyPI network requirement?) vs `nomic-embed-text` via Ollama (local-compute compliant); estimate cost/latency.
- [ ] **26. Write D1 verdict** to scratchpad `## Scout Output #71` (≤500 tokens): recommended approach + threshold + implementation notes.

**C2 — Implementation (Executive Scripter)**

- [ ] **27. Read D1 verdict** from scratchpad before writing any code.
- [ ] **28. Create `scripts/detect_drift.py`** with module docstring (purpose, inputs, outputs, usage).
- [ ] **29. Implement per-agent drift score** per D1 verdict approach.
- [ ] **30. Fleet-wide report** JSON: `{ "agents": [...], "fleet_avg", "below_threshold": [...] }`.
- [ ] **31. `--fail-below <float>` flag**: exit 1 if any agent below threshold; exit 0 otherwise.
- [ ] **32. Write `tests/test_detect_drift.py`** (5+ tests): happy path, zero drift, exit-1, exit-0, JSON schema. `@pytest.mark.io` for file tests; `@pytest.mark.integration` for embedding tests.
- [ ] **33. Coverage**: `uv run pytest tests/test_detect_drift.py --cov=scripts/detect_drift -q` — ≥80%.
- [ ] **34. D4 CI decision**: write 2-sentence CI recommendation to `/tmp/phase4-drift-ci-decision.md` (warning-only until threshold calibrated).

**C3 — Research Document**

- [ ] **35. Append findings to `docs/research/values-encoding.md`** (new `## Value Drift Detection` section) OR create standalone `docs/research/value-drift-detection.md` with full D4 frontmatter + required headings.
- [ ] **36. Validate**: `uv run python scripts/validate_synthesis.py docs/research/value-drift-detection.md` → exit 0 (if standalone).

---

#### Group D — Issue #78: Programmatic Value Provenance
**Owner: Executive Scripter (builds on #54 and #71)**

**Prerequisites**:
- [ ] **37. Verify Group B gate**: `python -c "import json; m=json.load(open('.github/agents/manifest.json')); assert 'avg_cross_ref_density' in m"`
- [ ] **38. Verify Group C gate**: `uv run python scripts/detect_drift.py --help` → exit 0.

**D1 — Annotation Format**

- [ ] **39. Evaluate annotation formats**: inline HTML `<!-- axiom: ... -->` vs YAML frontmatter `governs:` vs external JSON manifest. Constraint: parseable by ≤50-line Python, no external deps. Write recommendation to scratchpad `## Scripter Output #78`.

**D2 — `scripts/audit_provenance.py` Implementation**

- [ ] **40. Create `scripts/audit_provenance.py`** with module docstring.
- [ ] **41. Implement axiom extraction** per chosen format: extract `(axiom_name, source_ref)` per instruction block.
- [ ] **42. Citation plausibility check**: load `MANIFESTO.md`, confirm cited axiom appears as H2/H3. Flag missing as `unverifiable`.
- [ ] **43. Orphan detection**: instructions with no annotation → `orphaned` count.
- [ ] **44. JSON output schema**: `{ "files": [...], "fleet_citation_coverage_pct", "total_unverifiable" }`.

**D3 — Tests**

- [ ] **45. Write `tests/test_audit_provenance.py`** (5 tests): happy path, orphaned detection, unverifiable citation, JSON schema, exit codes. `@pytest.mark.io` for file tests.
- [ ] **46. Coverage**: `uv run pytest tests/test_audit_provenance.py --cov=scripts/audit_provenance -q` — ≥80%.

**D4 — Research Document**

- [ ] **47. Create `docs/research/value-provenance.md`** with D4 frontmatter + required headings (Executive Summary, Hypothesis Validation, Pattern Catalog, Recommendations, Sources).
- [ ] **48. Validate**: `uv run python scripts/validate_synthesis.py docs/research/value-provenance.md` → exit 0.

---

#### Group E — Validation & Close
**Owner: Executive Scripter → Executive Orchestrator**

- [ ] **49. Pre-commit validation**: `ruff check scripts/ tests/ && ruff format --check scripts/ tests/ && pytest tests/ -x -m "not slow and not integration" -q` — all exit 0.
- [ ] **50. Smoke test**: `uv run python scripts/generate_agent_manifest.py --help && uv run python scripts/detect_drift.py --help && uv run python scripts/audit_provenance.py --help` — each exits 0.
- [ ] **51. Coverage summary**: all three new/updated modules ≥80%.
- [ ] **52. Workplan update**: mark Phase 4 gate deliverables `[x]`.
- [ ] **53. Issue close comments** (write to temp files; use `--body-file`):
  - `gh issue comment 54 --body-file /tmp/issue-54-close.md && gh issue close 54`
  - `gh issue comment 71 --body-file /tmp/issue-71-close.md && gh issue close 71`
  - `gh issue comment 78 --body-file /tmp/issue-78-close.md && gh issue close 78`

---

### Phase 4 Acceptance Criteria Summary

| Deliverable | Path | Verification |
|---|---|---|
| Density scoring | `scripts/generate_agent_manifest.py` | `grep "cross_ref_density"` ≥3 matches |
| Tests for density | `tests/test_remaining_scripts.py::TestGenerateAgentManifest` | 6 real tests; coverage ≥80% |
| Manifest regenerated | `.github/agents/manifest.json` | `avg_cross_ref_density` key in JSON |
| detect_drift.py | `scripts/detect_drift.py` | `--help` exits 0 |
| Drift tests | `tests/test_detect_drift.py` | coverage ≥80% |
| Drift research doc | `docs/research/value-drift-detection.md` or `values-encoding.md` update | `validate_synthesis.py` exits 0 |
| audit_provenance.py | `scripts/audit_provenance.py` | `--help` exits 0 |
| Provenance tests | `tests/test_audit_provenance.py` | coverage ≥80% |
| Provenance research | `docs/research/value-provenance.md` | `validate_synthesis.py` exits 0; `status: Final` |
| Pre-commit | n/a | ruff + pytest all green |
| CI green | branch | `gh run list --limit 3` all `success` |

---

**Issues**: #80, #84
**Branch convention**: `research/queryable-substrate`
**Agent**: Executive Researcher (#80 survey + design), Executive Scripter (#80 and #84 implementation)
**Informed by**: Phase 2 (#85) findings on compression/retrieval tradeoff
**Status**: ⬜ Not started
**Checklist**: Delegate detailed per-phase execution checklist to Executive Planner before beginning execution (per AGENTS.md § Per-Phase Execution Checklists).

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #80 | Queryable documentation substrate | research | l |
| #84 | Programmatic doc interlinking — citation interweb | research | m |

**Gate deliverables**:
- [ ] `scripts/query_docs.py` CLI tool (BM25 baseline) implemented and tested
- [ ] `data/link_registry.yml` schema and initial population
- [ ] `scripts/weave_links.py` prototype with dry-run mode
- [ ] `docs/research/queryable-substrate.md` committed (Final)
- [ ] `docs/research/doc-interweb.md` committed (Final)

**Review gate**: Research Reviewer validates both synthesis docs.

---

### Phase 6 — Skills as Decision Codifiers

**Issues**: #79, #81, #72
**Branch convention**: `research/skills-decision-logic`
**Agent**: Executive Fleet (#79 audit + skill authoring), Executive Researcher (#81 survey)
**Informed by**: Phase 2 (#85) findings on extraction intervention
**Status**: ⬜ Not started
**Checklist**: Delegate detailed per-phase execution checklist to Executive Planner before beginning execution (per AGENTS.md § Per-Phase Execution Checklists).

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #79 | Skills as decision codifiers — delegation routing and phase-gate extraction | research | m |
| #81 | Deterministic agent components — FSMs and pre-LLM architectures | research | l |
| #72 | Context-sensitive axiom amplification — epigenetic tagging | research | m |

**Gate deliverables**:
- [ ] Audit of decision patterns appearing in ≥2 agent bodies; token savings estimate
- [ ] `delegation-routing` SKILL.md prototype
- [ ] `phase-gate-sequence` SKILL.md prototype
- [ ] FSM state specification for the orchestration phase-gate loop
- [ ] Epigenetic tagging recommendation (metadata / AGENTS.md selector / script)
- [ ] `docs/research/skills-as-decision-logic.md` + `docs/research/deterministic-agent-components.md` committed

**Review gate**: Executive Fleet Review validates new skills against `agent-file-authoring` SKILL.md and `validate_agent_files.py`.

---

### Phase 7 — Neuroplasticity & Back-Propagation

**Issues**: #82, #75
**Branch convention**: `research/dogma-neuroplasticity`
**Agent**: Executive Researcher → Research Scout → Synthesizer → Archivist
**Informed by**: Phase 6 (what's extractable), Phase 4 (drift measurement provides signal source)
**Status**: ⬜ Not started
**Checklist**: Delegate detailed per-phase execution checklist to Executive Planner before beginning execution (per AGENTS.md § Per-Phase Execution Checklists).

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #82 | Dogma neuroplasticity — back-propagation protocol | research | m |
| #75 | Empirical value drift at handoff boundaries | research | m |

**Gate deliverables**:
- [ ] Back-propagation protocol: evidence threshold, proposal format, coherence check, ADR template
- [ ] Stability tier model for substrate (Axioms / Principles / Operational Constraints)
- [ ] `scripts/propose_dogma_edit.py` specification
- [ ] Per-boundary degradation analysis from #75 (Scout → Synthesizer → Archive)
- [ ] `docs/research/dogma-neuroplasticity.md` + OQ-VE-5 appended to `values-encoding.md`

**Review gate**: Executive Docs reviews protocol for consistency with existing ADR process in `docs/decisions/`.

---

### Phase 8 — External Value Encoding (Deferred)

**Issue**: #83
**Branch convention**: `research/external-value-encoding`
**Agent**: Executive Researcher
**Depends on**: Phase 1 (#69 complete) and Phase 3 (#70 complete — the core layer must be solid before client-layer additions can be designed coherently); Adopt wizard (#56) design stable
**Status**: ⬜ Not started — deferred
**Checklist**: Delegate detailed per-phase execution checklist to Executive Planner before beginning execution (per AGENTS.md § Per-Phase Execution Checklists).

| Issue | Title | Effort |
|-------|-------|--------|
| #83 | Encoding external product and client values — layered value architecture | xl |

**Note**: This phase is intentionally last. The layered value architecture requires the core encoding layer to be stable and well-specified before client-layer additions can be designed coherently. Confirm framing assumption in issue body before starting.

**Review gate**: Review agent validates that the external-value layering design does not contradict existing core axioms in MANIFESTO.md and does not introduce unresolved conflicts with Phase 3's four-form encoding.

---

### Deferred / Dependent Issues

| Issue | Title | Deferred until |
|-------|-------|----------------|
| #74 | LLM behavioral testing for value fidelity | Local compute resolved (#13 prerequisite) |
| #76 | XML structuring in `handoffs.prompt` fields | Low priority; pick up opportunistically |
| #13 | Episodic/experiential memory | Local compute baseline (#1 in OPEN_RESEARCH.md) |
| #14 | AIGNE AFS context governance | Local compute baseline; informs #80 and #85 |

---

## Acceptance Criteria (Milestone Close)

- [ ] All non-deferred issues closed with committed deliverables
- [ ] `docs/research/values-encoding.md` §5 Open Questions all marked RESOLVED with resolution citations
- [ ] `MANIFESTO.md` updated with hermeneutics note and 4-form axiom encoding
- [ ] `scripts/detect_drift.py` (or equivalent) in CI
- [ ] `scripts/query_docs.py` functional and documented
- [ ] `delegation-routing` and `phase-gate-sequence` skills committed to `.github/skills/`
- [ ] Back-propagation protocol documented in `docs/research/dogma-neuroplasticity.md`
- [ ] `docs/research/context-budget-balance.md` committed

---

## Session-Start Checklist

Every session picking up a phase in this milestone must complete this before acting:

1. Read `docs/research/values-encoding.md` in full (or the relevant section if resuming)  
2. Read this workplan and note which phase is active  
3. Check the branch for in-progress commits: `git log --oneline -5`  
4. Read today's scratchpad: `cat .tmp/<branch>/<date>.md`  
5. State the governing axiom for today's work (Endogenous-First unless a specific phase changes it)  
6. Run `uv run python scripts/prune_scratchpad.py --init` to initialise the scratchpad  

## Session-Close Checklist

Every session working on a phase in this milestone must complete these steps before closing:

1. Write `## Session Summary` to the active scratchpad (`.tmp/<branch>/<date>.md`)
2. Post a progress comment on every GitHub issue actively worked: `gh issue comment <num> --body-file /tmp/progress.md`
3. Update issue body checkboxes for completed deliverables: `gh issue edit <num> --body-file /tmp/updated-body.md`
4. Confirm all commits pushed: `git log --oneline -3` + `git status`
5. Run `uv run python scripts/prune_scratchpad.py --force` to archive the session
6. If novel patterns, efficiency gains, or techniques emerged: run `@session-retrospective What lessons did we learn this session?` before closing

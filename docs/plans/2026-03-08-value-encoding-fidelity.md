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
**Status**: ✅ Complete — PR #90 open 2026-03-08 (targeting `feat/value-encoding-fidelity`)
**Commits**: `b73466a` (checklist), `90203a0` (#54), `faadae1` (#71), `ab7ff2d` (#78)
**Checklist**: ✅ Delegated to Executive Planner — see `### Phase 4 Detailed Checklist` below

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #54 | `generate_agent_manifest.py` cross-reference density score | feature | s |
| #71 | Semantic drift detection for agent files | research | m |
| #78 | Programmatic value signal provenance — `audit_provenance.py` | research | l |

#54 first (density count), then #71 (drift detection), then #78 (provenance tracing that builds on both).

**Gate deliverables**:
- [x] `generate_agent_manifest.py` emits per-agent cross-reference density score and fleet average
- [x] `scripts/detect_drift.py` (or `validate_agent_files.py --semantic`) prototype with per-agent drift score
- [x] `scripts/audit_provenance.py` prototype with per-file provenance report
- [x] Tests for all new scripts (≥80% coverage each)
- [x] CI integration decision documented for each script

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
- [x] **4. Pre-read endogenous sources** (read before touching any file):
  - `docs/research/values-encoding.md` §4 R3 (programmatic enforcement), §6 gap list
  - `scripts/generate_agent_manifest.py` lines 1–537 (full read — understand `process_agent_file()`, `build_manifest()`, `format_markdown()`, `main()`)
  - `tests/test_remaining_scripts.py` — locate `TestGenerateAgentManifest` class (4 placeholder stubs)
- [x] **5. Scratchpad check**: Session Start written 2026-03-08 with governing axiom (Endogenous-First) and this workplan as primary endogenous source.

---

#### Group B — Issue #54: Cross-Reference Density Score
**Owner: Executive Scripter**

**B1 — Implement density counting in `generate_agent_manifest.py`**

- [x] **6. Read `process_agent_file()`** fully to understand dict keys currently returned (`name`, `description`, `tools`, `posture`, `capabilities`, `handoffs`, `file`).
- [x] **7. Add `count_cross_ref_density(content: str) -> int` helper function** before `process_agent_file()`. Rules:
  - Count unique lines containing any of: `MANIFESTO.md`, `AGENTS.md`, `docs/guides/`
  - Return integer count (distinct lines — not total occurrences)
  - Include module docstring update: add `cross_ref_density` to Outputs description.
- [x] **8. Wire density into `process_agent_file()`**: add `cross_ref_density` key to the returned dict.
- [x] **9. Add fleet-wide average to `build_manifest()`**: compute `avg_cross_ref_density`; store on manifest dict (guard against empty list).
- [x] **10. Add density warning in `build_manifest()`**: for agents where `cross_ref_density < 1`, emit `logging.warning()` with agent name. Not a raised exception — warning only.
- [x] **11. Expose in `format_markdown()`**: append a `## Cross-Reference Density` section; table `Agent | cross_ref_density`; fleet average line below.
- [x] **12. Expose in JSON output**: confirm `cross_ref_density` per-agent and `avg_cross_ref_density` at manifest root.

**B2 — Update `TestGenerateAgentManifest` in `tests/test_remaining_scripts.py`**

- [x] **13. Read existing test class** (4 stubs; all `assert True`) to locate line numbers before editing.
- [x] **14. Replace stub `test_reads_all_agent_files`**: verify JSON output contains ≥1 agent entry. `@pytest.mark.io`
- [x] **15. Replace stub `test_outputs_json_manifest`**: assert `cross_ref_density` per-agent and `avg_cross_ref_density` at root. `@pytest.mark.io`
- [x] **16. Replace stub `test_outputs_markdown_manifest`**: assert `## Cross-Reference Density` heading + `|` table row present. `@pytest.mark.io`
- [x] **17. Replace stub `test_includes_agent_metadata`**: assert `name`, `description`, `cross_ref_density` keys per agent. `@pytest.mark.io`
- [x] **18. Add `test_count_cross_ref_density_unit`**: unit tests: empty → 0; one `MANIFESTO.md` ref → 1; `MANIFESTO.md` + `AGENTS.md` → 2; same ref repeated → still 1 per line; `docs/guides/` → 1. No I/O markers.
- [x] **19. Add `test_low_density_warning_emitted`**: fake agent with `cross_ref_density=0`; call `build_manifest()` + assert WARNING log message emitted with agent name.

**B3 — Fleet Manifest Regeneration + PR Note**

- [x] **20. Run coverage**: `uv run pytest tests/test_remaining_scripts.py::TestGenerateAgentManifest --cov=scripts/generate_agent_manifest -q` — must reach ≥80%.
- [x] **21. Regenerate manifest**: verify exact flags via `--help`, then `uv run python scripts/generate_agent_manifest.py --output .github/agents/manifest.json`.
- [x] **22. Note low-density agents**: copy WARNING lines to `/tmp/phase4-pr-body.md` under `## Density Warnings`.

---

#### Group C — Issue #71: Semantic Drift Detection
**Owner: Research Scout (survey D1) → Executive Scripter (implementation D2–D4)**

**C1 — Survey Phase (Research Scout)**

- [x] **23. Check source cache**: `uv run python scripts/fetch_source.py <sbert_url> --check` before fetching.
- [x] **24. Survey watermark-phrase approach**: identify 3–5 canonical watermark phrases from `docs/research/values-encoding.md` §3; estimate false-negative rate.
- [x] **25. Survey embedding-similarity approach**: `sentence-transformers` (PyPI network requirement?) vs `nomic-embed-text` via Ollama (local-compute compliant); estimate cost/latency.
- [x] **26. Write D1 verdict** to scratchpad `## Scout Output #71` (≤500 tokens): recommended approach + threshold + implementation notes.

**C2 — Implementation (Executive Scripter)**

- [x] **27. Read D1 verdict** from scratchpad before writing any code.
- [x] **28. Create `scripts/detect_drift.py`** with module docstring (purpose, inputs, outputs, usage).
- [x] **29. Implement per-agent drift score** per D1 verdict approach.
- [x] **30. Fleet-wide report** JSON: `{ "agents": [...], "fleet_avg", "below_threshold": [...] }`.
- [x] **31. `--fail-below <float>` flag**: exit 1 if any agent below threshold; exit 0 otherwise.
- [x] **32. Write `tests/test_detect_drift.py`** (5+ tests): happy path, zero drift, exit-1, exit-0, JSON schema. `@pytest.mark.io` for file tests; `@pytest.mark.integration` for embedding tests.
- [x] **33. Coverage**: `uv run pytest tests/test_detect_drift.py --cov=scripts/detect_drift -q` — ≥80%.
- [x] **34. D4 CI decision**: write 2-sentence CI recommendation to `/tmp/phase4-drift-ci-decision.md` (warning-only until threshold calibrated).

**C3 — Research Document**

- [x] **35. Append findings to `docs/research/values-encoding.md`** (new `## Value Drift Detection` section) OR create standalone `docs/research/value-drift-detection.md` with full D4 frontmatter + required headings.
- [x] **36. Validate**: `uv run python scripts/validate_synthesis.py docs/research/value-drift-detection.md` → exit 0 (if standalone).

---

#### Group D — Issue #78: Programmatic Value Provenance
**Owner: Executive Scripter (builds on #54 and #71)**

**Prerequisites**:
- [x] **37. Verify Group B gate**: `python -c "import json; m=json.load(open('.github/agents/manifest.json')); assert 'avg_cross_ref_density' in m"`
- [x] **38. Verify Group C gate**: `uv run python scripts/detect_drift.py --help` → exit 0.

**D1 — Annotation Format**

- [x] **39. Evaluate annotation formats**: inline HTML `<!-- axiom: ... -->` vs YAML frontmatter `governs:` vs external JSON manifest. Constraint: parseable by ≤50-line Python, no external deps. Write recommendation to scratchpad `## Scripter Output #78`.

**D2 — `scripts/audit_provenance.py` Implementation**

- [x] **40. Create `scripts/audit_provenance.py`** with module docstring.
- [x] **41. Implement axiom extraction** per chosen format: extract `(axiom_name, source_ref)` per instruction block.
- [x] **42. Citation plausibility check**: load `MANIFESTO.md`, confirm cited axiom appears as H2/H3. Flag missing as `unverifiable`.
- [x] **43. Orphan detection**: instructions with no annotation → `orphaned` count.
- [x] **44. JSON output schema**: `{ "files": [...], "fleet_citation_coverage_pct", "total_unverifiable" }`.

**D3 — Tests**

- [x] **45. Write `tests/test_audit_provenance.py`** (5 tests): happy path, orphaned detection, unverifiable citation, JSON schema, exit codes. `@pytest.mark.io` for file tests.
- [x] **46. Coverage**: `uv run pytest tests/test_audit_provenance.py --cov=scripts/audit_provenance -q` — ≥80%.

**D4 — Research Document**

- [x] **47. Create `docs/research/value-provenance.md`** with D4 frontmatter + required headings (Executive Summary, Hypothesis Validation, Pattern Catalog, Recommendations, Sources).
- [x] **48. Validate**: `uv run python scripts/validate_synthesis.py docs/research/value-provenance.md` → exit 0.

---

#### Group E — Validation & Close
**Owner: Executive Scripter → Executive Orchestrator**

- [x] **49. Pre-commit validation**: `ruff check scripts/ tests/ && ruff format --check scripts/ tests/ && pytest tests/ -x -m "not slow and not integration" -q` — all exit 0.
- [x] **50. Smoke test**: `uv run python scripts/generate_agent_manifest.py --help && uv run python scripts/detect_drift.py --help && uv run python scripts/audit_provenance.py --help` — each exits 0.
- [x] **51. Coverage summary**: all three new/updated modules ≥80%.
- [x] **52. Workplan update**: mark Phase 4 gate deliverables `[x]`.
- [x] **53. Issue close comments** (write to temp files; use `--body-file`):
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

### Phase 5 — Queryable Documentation Substrate

**Issues**: #80, #84
**Branch convention**: `research/queryable-substrate`
**Agent**: Executive Researcher (#80 survey + design), Executive Scripter (#80 and #84 implementation)
**Informed by**: Phase 2 (#85) findings on compression/retrieval tradeoff
**Status**: ✅ Complete — PR #91 merged 2026-03-08 into `feat/value-encoding-fidelity` (27a0eb7); issues #80, #84 closed
**Checklist**: ✅ Delegated to Executive Planner — see `### Phase 5 Detailed Checklist` below

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #80 | Queryable documentation substrate | research | l |
| #84 | Programmatic doc interlinking — citation interweb | research | m |

**Gate deliverables**:
- [x] `scripts/query_docs.py` CLI tool (BM25 baseline) implemented and tested
- [x] `data/link_registry.yml` schema and initial population
- [x] `scripts/weave_links.py` prototype with dry-run mode
- [x] `docs/research/queryable-substrate.md` committed (Final)
- [x] `docs/research/doc-interweb.md` committed (Final)

**Review gate**: Research Reviewer validates both synthesis docs.

---

### Phase 5 Detailed Checklist

**Issues**: #80 → #84 | **Branch**: `research/queryable-substrate`
**Execution order**: A → B → C → D → E → F (D may begin after B completes, parallel to C)

---

#### Group A — Setup
**Owner: Executive Orchestrator** | No prerequisites

- [x] **A1.** Confirm Phase 4 gate: `git log --oneline -5` on `feat/value-encoding-fidelity`; verify `audit_provenance.py` and `generate_agent_manifest.py` density scoring commits are present before any work begins.
- [x] **A2.** Create branch: `git checkout feat/value-encoding-fidelity && git pull && git checkout -b research/queryable-substrate && git push -u origin research/queryable-substrate`. Verify: `git branch --show-current` → `research/queryable-substrate`.
- [x] **A3.** Pre-read endogenous sources: `docs/research/values-encoding.md` §4 R1 (bulk-load problem), `scripts/audit_provenance.py` (corpus structure), `AGENTS.md` §"Algorithms Before Tokens". Write `## Session Start` in scratchpad citing "Endogenous-First" and this workplan.

---

#### Group B — Issue #80 Research Survey
**Owner: Research Scout → Research Synthesizer** | Prerequisite: A3

- [x] **B4.** Source cache check: for planned BM25 URLs, run `uv run python scripts/fetch_source.py <url> --check` before fetching. Skip any already cached in `.cache/sources/`.
- [x] **B5.** Scout: survey BM25 algorithm (TF-IDF weighting, k1/b parameters) from cached sources. Confirm: no external API or embeddings needed — local-compute compliant.
- [x] **B6.** Scout: evaluate `rank_bm25` (PyPI). Record: pure-Python status, license (Apache-2.0), offline-operability, latest version. Compare against hand-rolled stdlib implementation (lines-of-code, test overhead).
- [x] **B7.** Scout: survey Markdown paragraph chunking strategies — blank-line delimiter, heading boundary, fixed token window. Identify which preserves context without splitting code fences. Record recommendation (≤75 words).
- [x] **B8.** Scout: enumerate doc corpus scope. Run `find docs/ -name '*.md' | wc -l` and `find . -name '*.agent.md' | wc -l`. Record file counts and total line count to inform chunking design.
- [x] **B9.** Scout: design `SCOPE_PATHS` mapping: `manifesto → [MANIFESTO.md]`, `agents → [AGENTS.md, .github/agents/*.agent.md]`, `guides → [docs/guides/*.md]`, `research → [docs/research/*.md]`, `all → union`. Verify mapping covers all endogenous sources.
- [x] **B10.** Synthesizer: draft `docs/research/queryable-substrate.md` — D4 frontmatter (`title`, `status: Final`); sections: Executive Summary, Hypothesis Validation, Pattern Catalog, Recommendations, Sources; ≥1 cite to `MANIFESTO.md` §"Algorithms Before Tokens".
- [x] **B11.** Synthesizer: validate: `uv run python scripts/validate_synthesis.py docs/research/queryable-substrate.md` → exit 0.
- [x] **B12.** Commit: `git add docs/research/queryable-substrate.md && git commit -m "docs(research): queryable substrate synthesis [#80]"`. Verify: `git log --oneline -1`.

---

#### Group C — Issue #80 Implementation
**Owner: Executive Scripter** | Prerequisite: B12

- [x] **C13.** Add `rank_bm25` to `pyproject.toml` `[project.dependencies]`. Run `uv sync`. Verify: `uv run python -c "import rank_bm25; print('ok')"` exits 0.
- [x] **C14.** Create `scripts/query_docs.py` with module docstring: purpose, inputs (`query`, `--scope`, `--top-n`, `--output`), outputs (ranked snippets with file + line range), usage example.
- [x] **C15.** Implement `SCOPE_PATHS: dict[str, list[str]]` constant using glob patterns from B9 design. `all` is the union of all four scopes.
- [x] **C16.** Implement `chunk_markdown(text: str, filepath: str) -> list[dict]` — split on blank-line boundaries; each chunk: `{text, file, start_line, end_line}`; skip chunks ≤ 3 non-whitespace words; treat triple-backtick fences as single atomic chunks.
- [x] **C17.** Implement `build_corpus(scope: str, repo_root: Path) -> list[dict]` — resolve `SCOPE_PATHS[scope]` globs, read each file, call `chunk_markdown()`. Silently skip missing files. Raise `KeyError` for unknown scope.
- [x] **C18.** Implement `run_query(query: str, corpus: list[dict], top_n: int) -> list[dict]` — tokenize chunks, instantiate `BM25Okapi`, score query, return top-N chunks descending by score. Return `[]` for empty corpus.
- [x] **C19.** Implement `format_output(results: list[dict], mode: str) -> str` — `text`: file:start–end header per result; `json`: `json.dumps(results, indent=2)`.
- [x] **C20.** Implement `main()` with `argparse`: `query` (positional), `--scope` (choices: `manifesto agents guides research all`, default `all`), `--top-n` (int, default 5), `--output` (choices: `text json`, default `text`).
- [x] **C21.** Smoke test: `uv run python scripts/query_docs.py "endogenous first" --scope manifesto --output text`. Expect ≥1 result with file + line range printed.
- [x] **C22.** Create `tests/test_query_docs.py` with module docstring. Test functions import module directly (not subprocess) except where `@pytest.mark.io` is warranted.
- [x] **C23.** `chunk_markdown` unit tests: empty string → `[]`; two paragraphs → 2 chunks with correct line numbers; ≤3-word paragraph excluded; code fence block → single chunk.
- [x] **C24.** `build_corpus` + `run_query` tests: unknown scope → `KeyError`; synthetic 10-chunk corpus with query term in 3 → top-N returned descending; empty corpus → `[]`.
- [x] **C25.** `format_output` + CLI tests: text mode contains `file:` header; JSON mode parses as valid list; `@pytest.mark.io` CLI test with `--scope manifesto` non-empty; `@pytest.mark.io` `--output json` parseable.
- [x] **C26.** Coverage gate: `uv run pytest tests/test_query_docs.py --cov=scripts/query_docs --cov-report=term-missing -q` ≥ 80%. Fix gaps, then: `git add scripts/query_docs.py tests/test_query_docs.py && git commit -m "feat(scripts): BM25 query_docs CLI + tests [#80]"`.

---

#### Group D — Issue #84 Research Survey
**Owner: Research Scout → Research Synthesizer** | Prerequisite: A3 (parallel-eligible with C13–C26)

- [x] **D27.** Source cache check: for planned linking/interweb strategy URLs, run `uv run python scripts/fetch_source.py <url> --check` before fetching.
- [x] **D28.** Scout: read `scripts/audit_provenance.py` fully. Identify: what concept mentions and cross-references it already detects. Document reuse opportunities for `weave_links.py`.
- [x] **D29.** Scout: survey bidirectional linking strategies for Markdown corpora — inline `[term](canonical.md)` injection, footnote-style refs, YAML-registry-driven weaving. Evaluate idempotency guarantees for each.
- [x] **D30.** Scout: design `link_registry.yml` schema: `{concept: str, canonical_source: str, applications: [str], aliases: [str]}`. Verify schema handles multi-word concepts and path-relative sources. Propose 3–5 seed entries from existing concepts (Endogenous-First, Algorithms Before Tokens, programmatic-first).
- [x] **D31.** Scout: define idempotency contract for `weave_links.py` — if inline link already present for a concept, skip it (no double-wrapping). Specify regex or marker strategy for detecting existing links.
- [x] **D32.** Scout: scope `--scope <path>` design — accepts a file path or directory; defaults to `docs/` if omitted; `--dry-run` prints diffs without writing.
- [x] **D33.** Synthesizer: draft `docs/research/doc-interweb.md` — D4 frontmatter (`title`, `status: Final`); sections: Executive Summary, Hypothesis Validation, Pattern Catalog, Recommendations, Sources; ≥1 cite to `AGENTS.md` §"Documentation-First".
- [x] **D34.** Synthesizer: validate: `uv run python scripts/validate_synthesis.py docs/research/doc-interweb.md` → exit 0.
- [x] **D35.** Commit: `git add docs/research/doc-interweb.md && git commit -m "docs(research): doc interweb synthesis [#84]"`. Verify: `git log --oneline -1`.

---

#### Group E — Issue #84 Implementation
**Owner: Executive Scripter** | Prerequisite: D35 and C26

- [x] **E36.** Create `data/link_registry.yml` with schema from D30 design. Populate ≥5 seed entries: `Endogenous-First`, `Algorithms Before Tokens`, `programmatic-first`, `Local Compute-First`, `cross-reference density`. Each entry must have `canonical_source` as a repo-relative path.
- [x] **E37.** Create `scripts/weave_links.py` with module docstring: purpose, inputs (`--scope`, `--dry-run`, `--registry`), outputs (modified files or dry-run diff), idempotency guarantee, usage example.
- [x] **E38.** Implement `load_registry(path: Path) -> list[dict]` — reads `data/link_registry.yml`; validates each entry has `concept`, `canonical_source`, `aliases` (may be empty).
- [x] **E39.** Implement `find_mentions(text: str, entry: dict) -> list[tuple[int, str]]` — returns `(line_number, matched_term)` for each unlinked occurrence of `concept` or any alias. Skip lines already containing a Markdown link to `canonical_source`.
- [x] **E40.** Implement `inject_link(text: str, entry: dict, dry_run: bool) -> tuple[str, list[str]]` — wraps first unlinked occurrence per paragraph; returns `(modified_text, list_of_diff_lines)`. Idempotent: second call on already-modified text produces zero diff.
- [x] **E41.** Implement `weave_file(filepath: Path, registry: list[dict], dry_run: bool) -> int` — applies `inject_link` for each registry entry; writes file only if `not dry_run` and changes exist; returns count of injections made.
- [x] **E42.** Implement `main()` with `argparse`: `--scope` (path, default `docs/`), `--dry-run` (flag), `--registry` (path, default `data/link_registry.yml`), `--top-n` injections per file (int, default unlimited). Print summary: `N injections in M files`.
- [x] **E43.** Idempotency smoke test: `uv run python scripts/weave_links.py --scope docs/guides/ --dry-run` (no writes). Run twice; assert second invocation reports same diffs. Verify: output non-empty and no crash.
- [x] **E44.** Create `tests/test_weave_links.py` with module docstring. Import functions directly.
- [x] **E45.** `find_mentions` + `inject_link` unit tests: unlinked term → detected; already-linked term → skipped; alias match → detected; inject twice → idempotent (zero second diff); `dry_run=True` → text unchanged.
- [x] **E46.** `load_registry` + `weave_file` tests: missing required field → `KeyError`; valid registry entry → correct injection count; `@pytest.mark.io` real file round-trip with `dry_run=True` leaves file unchanged.
- [x] **E47.** Coverage gate: `uv run pytest tests/test_weave_links.py --cov=scripts/weave_links --cov-report=term-missing -q` ≥ 80%. Fix gaps, then: `git add data/link_registry.yml scripts/weave_links.py tests/test_weave_links.py && git commit -m "feat(scripts): weave_links.py + link_registry + tests [#84]"`.

---

#### Group F — Validation & Close
**Owner: Executive Scripter + Orchestrator** | Prerequisite: C26 and E47

- [x] **F48.** Lint + format: `uv run ruff check scripts/query_docs.py scripts/weave_links.py tests/test_query_docs.py tests/test_weave_links.py && uv run ruff format --check scripts/ tests/`. Fix all violations before proceeding.
- [x] **F49.** Full test suite (fast subset): `uv run pytest tests/ -x -m "not slow and not integration" -q`. All tests pass; no regressions in pre-existing tests. Fix any failures.
- [x] **F50.** Synthesis validation: `uv run python scripts/validate_synthesis.py docs/research/queryable-substrate.md && uv run python scripts/validate_synthesis.py docs/research/doc-interweb.md`. Both exit 0.
- [x] **F51.** Gate deliverable confirm: verify all five Phase 5 gate items in the workplan are checkable — `scripts/query_docs.py` present, `data/link_registry.yml` present, `scripts/weave_links.py` present, both research docs committed with `status: Final`. Check workplan checkboxes.
- [x] **F52.** Push and open PR: `git push && gh pr create --base feat/value-encoding-fidelity --title "feat(phase-5): queryable substrate + doc interweb [#80, #84]" --body-file <temp-body-file>`. Verify: `gh pr view --json title,state`; post progress comment on issues #80 and #84 via `gh issue comment <num> --body-file <path>`.
- [x] **F53.** Post-PR CI checks: monitor `gh run list --limit 3` for this branch; all must be `success`. Address any failures immediately.
- [x] **F54.** Tag @AccessiT3ch for review on the PR once CI is green. Coordinate with reviewer for timely review and address feedback with the review PR Review skill.

---

### Phase 5 Acceptance Criteria Summary

| Deliverable | Path | Verification |
|---|---|---|
| BM25 query CLI | `scripts/query_docs.py` | `--help` exits 0; `--scope manifesto` returns ≥1 result |
| Query tests | `tests/test_query_docs.py` | coverage ≥80% |
| `rank_bm25` dep | `pyproject.toml` | `uv run python -c "import rank_bm25"` exits 0 |
| Link registry | `data/link_registry.yml` | ≥5 seed entries; schema-valid |
| Weave links CLI | `scripts/weave_links.py` | `--dry-run` exits 0; idempotent on second run |
| Weave tests | `tests/test_weave_links.py` | coverage ≥80% |
| Queryable substrate doc | `docs/research/queryable-substrate.md` | `validate_synthesis.py` exits 0; `status: Final` |
| Doc interweb doc | `docs/research/doc-interweb.md` | `validate_synthesis.py` exits 0; `status: Final` |
| Pre-commit | n/a | ruff + pytest all green |
| CI green | branch | `gh run list --limit 3` all `success` |

---

### Phase 6 — Skills as Decision Logic & Deterministic Components

**Issues**: #79, #81, #72
**Branch convention**: `research/skills-decision-logic`
**Agent**: Executive Fleet (#79 audit + skill authoring), Executive Researcher (#81 survey)
**Informed by**: Phase 2 (#85) findings on extraction intervention
**Status**: ✅ Complete — PR #92 merged into `feat/value-encoding-fidelity` 2026-03-09T23:44:27Z (commits fd20524 + 201b4be)
**Checklist**: ✅ Delegated to Executive Planner — see session scratchpad `.tmp/feat-value-encoding-fidelity/2026-03-09.md`

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #79 | Skills as decision codifiers — delegation routing and phase-gate extraction | research | m |
| #81 | Deterministic agent components — FSMs and pre-LLM architectures | research | l |
| #72 | Context-sensitive axiom amplification — epigenetic tagging | research | m |

**Gate deliverables**:
- [x] Audit of decision patterns appearing in ≥2 agent bodies; token savings estimate (~748 tokens/session)
- [x] `delegation-routing` SKILL.md prototype
- [x] `phase-gate-sequence` SKILL.md prototype
- [x] FSM state specification for the orchestration phase-gate loop (`data/phase-gate-fsm.yml`)
- [x] Epigenetic tagging recommendation (AGENTS.md lookup table adopted; script deferred)
- [x] `docs/research/skills-as-decision-logic.md` + `docs/research/deterministic-agent-components.md` committed

**Review gate**: ✅ APPROVED — Review agent verified all 10 checks; `validate_agent_files.py --all` 45/45 PASS.

---

### Phase α — Wire `detect_drift.py` into CI

**Issue**: #107
**Branch convention**: `feat/value-encoding-fidelity` (no new branch needed — single-file CI edit)
**Agent**: Executive Automator (CI step authoring) → Review → GitHub
**Depends on**: Phase 4 (`detect_drift.py` implemented and tested)
**Status**: ✅ Complete — commit ae5bfef pushed 2026-03-09
**Checklist**: Single-phase; no Executive Planner delegation required.

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #107 | Wire `detect_drift.py` into CI lint job for value-alignment enforcement | chore | s |

**Gate deliverables**:
- [x] `detect_drift.py` step added to `.github/workflows/tests.yml` lint job
- [x] Fleet baseline `fleet_avg` score recorded on issue #107 (0.1435 avg; 35/36 agents below 0.5)
- [x] `--fail-below` threshold set to a calibrated value (0.5, not `0.0`)
- [ ] CI passes with new step in place (⏳ next session: verify via `gh run list --limit 3`)
- [x] Acceptance criterion ticked: `scripts/detect_drift.py` (or equivalent) in CI

**Review gate**: ✅ APPROVED — Review agent verified all 6 checks (YAML syntax, integration, script path, threshold rationale, CI matrix impact, error clarity).

---

### Phase 7 — Neuroplasticity & Back-Propagation

**Issues**: #82, #75
**Branch convention**: `research/dogma-neuroplasticity`
**Agent**: Executive Researcher → Research Scout → Synthesizer → Archivist
**Informed by**: Phase 6 (what's extractable), Phase 4 (drift measurement provides signal source)
**Status**: 🔄 In progress — checklist delegated; branch setup next
**Checklist**: ✅ Delegated to Executive Planner — see `### Phase 7 Detailed Checklist` below

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #82 | Dogma neuroplasticity — back-propagation protocol | research | m |
| #75 | Empirical value drift at handoff boundaries | research | m |

**Gate deliverables**:
- [ ] Back-propagation protocol: evidence threshold, proposal format, coherence check, ADR template
- [ ] Stability tier model for substrate (Axioms / Principles / Operational Constraints)
- [ ] `scripts/propose_dogma_edit.py` implementation + tests ≥80%
- [ ] Per-boundary degradation analysis from #75 (Scout → Synthesizer → Archive)
- [ ] `docs/research/dogma-neuroplasticity.md` committed (Final)
- [ ] OQ-VE-5 appended to `docs/research/values-encoding.md`

**Review gate**: Executive Docs reviews protocol for consistency with existing ADR process in `docs/decisions/`.

---

### Phase 7 Detailed Checklist

**Issues**: #82 → #75 | **Branch**: `research/dogma-neuroplasticity`
**Execution order**: A → B and C (parallel-eligible after A3) → D → E → F

---

#### Group A — Setup
**Owner: Executive Orchestrator** | No prerequisites

- [ ] **A1.** Confirm Phase 6 gate: `git log --oneline -10` on `feat/value-encoding-fidelity`; verify Phase 6 skills-decision-logic merge commit and Phase α detect_drift CI commit are present. Abort if missing — merge predecessor PRs first.
- [ ] **A2.** Create branch: `git checkout feat/value-encoding-fidelity && git pull && git checkout -b research/dogma-neuroplasticity && git push -u origin research/dogma-neuroplasticity`. Verify: `git branch --show-current` → `research/dogma-neuroplasticity`.
- [ ] **A3.** Pre-read endogenous sources: `docs/research/values-encoding.md` §5 item 5 (OQ-VE-5); `docs/decisions/ADR-001` through `ADR-006` for template structure; `AGENTS.md` §"Focus-on-Descent / Compression-on-Ascent"; skim `scripts/audit_provenance.py` and `scripts/detect_drift.py` for reuse surface. Write `## Session Start` in scratchpad citing "Endogenous-First" and this workplan.

---

#### Group B — Issue #75 Empirical Audit
**Owner: Research Scout → Research Synthesizer** | Prerequisite: A3 (parallel-eligible with C)

- [ ] **B4.** Identify audit corpus: run `git log --oneline --all | grep -E 'research/queryable|research/skills'` to confirm merged source branches. Select 2–3 sessions from `.tmp/feat-value-encoding-fidelity/2026-03-08.md` + `2026-03-09.md`; locate their archived research doc counterparts (`docs/research/queryable-substrate.md`, `docs/research/skills-as-decision-logic.md`). Record each as a `(Scout section, Synthesizer section, Archive doc)` trio in scratchpad.
- [ ] **B5.** Element type 1 — Axiom citation density: for each session trio, count MANIFESTO.md back-references per stage. Run `uv run python scripts/audit_provenance.py` to score the archived doc; manually count in Scout and Synthesizer scratchpad sections. Record `{scout_count, synth_count, archive_count}` per session.
- [ ] **B6.** Element type 4 — Watermark phrase survival: run `uv run python scripts/detect_drift.py --path <archived_doc> --threshold 0.0` for each archived doc. Scan Scout and Synthesizer sections for the same six `WATERMARK_PHRASES` constants (`Endogenous-First`, `Algorithms Before Tokens`, `Local Compute-First`, `encode-before-act`, `morphogenetic seed`, `programmatic-first`). Record survival rate per boundary.
- [ ] **B7.** Element types 2 & 3 — Canonical example + anti-pattern preservation: grep each Scout, Synthesizer, and Archive stage for `\*\*Canonical example\*\*:` and `\*\*Anti-pattern\*\*:` patterns. Record count present at each stage per session.
- [ ] **B8.** Synthesizer: compile degradation summary table — rows: four element types (axiom density, canonical examples, anti-patterns, watermark phrases); columns: Scout→Synth loss %, Synth→Archive loss % — averaged across the 2–3 sessions. Identify the element type with highest total loss.
- [ ] **B9.** Synthesizer: draft proposed additive amendments to `AGENTS.md` §"Focus-on-Descent / Compression-on-Ascent" based on B8 findings — concrete additions only (e.g., "Retain axiom-citation count"; "Preserve ≥2 watermark phrases in Synthesizer return"). ≤3 bullet additions; no rewrites.
- [ ] **B10.** Synthesizer: write OQ-VE-5 resolution section text to scratchpad under `## B10 — OQ-VE-5 Draft` — heading `**5. Value drift in multi-agent handoffs** *(RESOLVED — <date>)*`, B8 degradation table, resolution statement citing B9 AGENTS.md amendments, `**Closes**: issue #75`. ≤500 words.
- [ ] **B11.** Review gate: Orchestrator reviews B10 draft. Confirm: degradation table spans ≥2 sessions and 4 element types; AGENTS.md amendment text is additive-only; OQ-VE-5 marked RESOLVED with date. Record `## B11 — Review: Approved` in scratchpad before C-group merge.

---

#### Group C — Issue #82 Research Survey
**Owner: Research Scout → Research Synthesizer** | Prerequisite: A3 (parallel-eligible with B)

- [ ] **C12.** Source cache check: for planned survey URLs (Constitutional AI RLAIF, Argyris double-loop learning, living specification methodologies, SemVer for prose), run `uv run python scripts/fetch_source.py <url> --check` before fetching. Skip already-cached URLs in `.cache/sources/`.
- [ ] **C13.** Scout: survey Constitutional AI RLAIF feedback loop and Argyris single/double-loop learning. Extract: signal aggregation threshold patterns, feedback cycle duration, and conflict resolution when new signal contradicts existing rule. Map to substrate: single-loop = AGENTS.md edit; double-loop = MANIFESTO.md edit. Record ≤150 words in scratchpad.
- [ ] **C14.** Scout: survey living specification methodologies and semantic versioning for prose. Identify empirical mutation-rate differences between stable policy layers vs. volatile operational layers. Record ≤75 words.
- [ ] **C15.** Scout: design evidence threshold — draft 3-tier threshold: T3 Operational Constraints (2 independent session signals); T2 Guiding Principles (3 signals + scratchpad retrospective); T1 Axioms (3 signals + formal ADR in `docs/decisions/`). Justify in scratchpad.
- [ ] **C16.** Scout: design stability tier model — T1 Axioms (`MANIFESTO.md` §axioms; very stable), T2 Guiding Principles (`MANIFESTO.md` non-axiom sections + `AGENTS.md` §1; moderately stable), T3 Operational Constraints (`AGENTS.md` operational sections; rapidly evolving). Record tier boundaries and mutation-rate rationale.
- [ ] **C17.** Scout: draft ADR-style template for dogma edits — headings: Date, Tier, Current Text, Proposed Text (unified-diff format), Evidence (session file citations + timestamps), Coherence Check (inheritance chain cross-references), Status (Proposed | Accepted | Rejected). Compare against ADR-006 structure confirmed in A3.
- [ ] **C18.** Synthesizer: draft `docs/research/dogma-neuroplasticity.md` — D4 frontmatter (`title: "Dogma Neuroplasticity & Back-Propagation Protocol"`, `status: Final`); required headings: Executive Summary, Hypothesis Validation, Pattern Catalog (stability tier model + back-propagation protocol + ADR template), Recommendations (`propose_dogma_edit.py` spec), Sources; ≥2 cites to `MANIFESTO.md` axioms.
- [ ] **C19.** Validate: `uv run python scripts/validate_synthesis.py docs/research/dogma-neuroplasticity.md` → exit 0. Fix any missing heading or frontmatter issues before proceeding.
- [ ] **C20.** Commit: `git add docs/research/dogma-neuroplasticity.md && git commit -m "docs(research): dogma neuroplasticity synthesis [#82]"`. Verify: `git log --oneline -1`.

---

#### Group D — Script Implementation (#82 gate deliverable D4)
**Owner: Executive Scripter** | Prerequisite: C20 committed

- [ ] **D21.** Before writing any code, read `scripts/audit_provenance.py` `extract_manifesto_axioms()` and `scripts/detect_drift.py` `WATERMARK_PHRASES` fully. Document reuse plan: import `WATERMARK_PHRASES` directly from `detect_drift`; import `extract_manifesto_axioms` from `audit_provenance`. No reimplementation.
- [ ] **D22.** Create `scripts/propose_dogma_edit.py` with module docstring: purpose, inputs (`--input <session-file>`, `--tier T1|T2|T3`, `--affected-axiom <str>`, `--proposed-delta <str or - for stdin>`, `--output <path>`), outputs (ADR-style Markdown proposal), usage example.
- [ ] **D23.** Implement `load_stability_tiers() -> dict[str, dict]` — hard-coded tier metadata (name, session_threshold, requires_adr) matching the C16 design and `dogma-neuroplasticity.md` §Pattern Catalog verbatim.
- [ ] **D24.** Implement `extract_evidence(session_text: str) -> list[str]` — import `WATERMARK_PHRASES` from `detect_drift`; return lines in `session_text` containing any watermark phrase. Return `[]` for empty input.
- [ ] **D25.** Implement `check_coherence(tier: str, proposed_delta: str, tiers: dict) -> dict` — returns `{"passes": bool, "session_threshold": int, "inheriting_layers": list[str]}`. Flag `passes: False` if proposed_delta removes any `WATERMARK_PHRASES` entry; T1 edits always require `requires_adr: True`.
- [ ] **D26.** Implement `generate_proposal(...) -> str` — returns Markdown using the C17 ADR-style template: Date (today), Tier, Current Text (placeholder `<replace>`), Proposed Text (unified-diff input), Evidence (extract_evidence lines), Coherence Check (check_coherence result summary), Status: Proposed.
- [ ] **D27.** Implement `main(argv: list[str] | None = None) -> int` with `argparse`. `--proposed-delta -` reads from stdin. Writes proposal to `--output` path or stdout. Returns 0 on success; 1 if `coherence["passes"] is False` and tier is T1.
- [ ] **D28.** Smoke test: `uv run python scripts/propose_dogma_edit.py --input .tmp/feat-value-encoding-fidelity/2026-03-09.md --tier T3 --affected-axiom "Focus-on-Descent" --proposed-delta "+" --output /tmp/smoke-proposal.md`. Verify: file created; contains `## Coherence Check`; exit 0.
- [ ] **D29.** Create `tests/test_propose_dogma_edit.py` with module docstring. Import all functions directly. Test: `load_stability_tiers()` returns all 3 tiers with T1 threshold > T3; `extract_evidence()` returns ≥1 line for watermark-containing text; `check_coherence()` T3 proposal removing watermark phrase → `passes: False`; valid T3 proposal → `passes: True`; `generate_proposal()` output contains all 7 ADR headings and `Status: Proposed`.
- [ ] **D30.** CLI tests (`@pytest.mark.io`): missing `--input` → non-zero exit; valid invocation → output file created; output file is valid Markdown with ≥6 `##` headings.
- [ ] **D31.** Coverage gate: `uv run pytest tests/test_propose_dogma_edit.py --cov=scripts/propose_dogma_edit --cov-report=term-missing -q` ≥ 80%. Fix gaps. Commit: `git add scripts/propose_dogma_edit.py tests/test_propose_dogma_edit.py && git commit -m "feat(scripts): propose_dogma_edit.py + tests ≥80% [#82]"`. Verify: `git log --oneline -1`.

---

#### Group E — AGENTS.md Amendments + OQ-VE-5 Resolution
**Owner: Executive Docs** | Prerequisite: D31 committed + B11 approved

- [ ] **E32.** Apply AGENTS.md amendments from B9 under `### Focus-on-Descent / Compression-on-Ascent` using `replace_string_in_file` (never heredoc). Verify: `grep -A 15 "Focus-on-Descent" AGENTS.md` shows new bullet(s); no existing bullet text deleted.
- [ ] **E33.** Append OQ-VE-5 resolution text from `## B10 — OQ-VE-5 Draft` into `docs/research/values-encoding.md` §5 using `replace_string_in_file` anchored at the existing item 5 heading. Verify: `grep -n "RESOLVED" docs/research/values-encoding.md` → ≥1 match.
- [ ] **E34.** Validate: `uv run python scripts/validate_synthesis.py docs/research/values-encoding.md` → exit 0. Then `uv run python scripts/validate_agent_files.py --all` → all PASS. Fix any regressions immediately.
- [ ] **E35.** Commit: `git add AGENTS.md docs/research/values-encoding.md && git commit -m "docs(agents,research): focus-on-descent amendments + OQ-VE-5 resolution [#75, #82]"`. Verify: `git log --oneline -1`.
- [ ] **E36.** Review gate: call Review agent on E35 diff. Confirm: AGENTS.md edit is additive-only (no deletions); OQ-VE-5 section appended without overwriting items 1–4; both validation scripts exit 0. Record `## E36 — Review: Approved` in scratchpad.

---

#### Group F — Validation & Close
**Owner: Executive Orchestrator** | Prerequisite: E36 approved

- [ ] **F37.** Lint + format: `uv run ruff check scripts/propose_dogma_edit.py tests/test_propose_dogma_edit.py && uv run ruff format --check scripts/ tests/`. Fix all violations before proceeding.
- [ ] **F38.** Full test suite (fast subset): `uv run pytest tests/ -x -m "not slow and not integration" -q`. Zero regressions in pre-existing tests. Fix any failures.
- [ ] **F39.** Gate deliverable confirm — verify all 6 Phase 7 items are checkable: (1) back-propagation protocol in `dogma-neuroplasticity.md` §Recommendations; (2) stability tier model in §Pattern Catalog; (3) `scripts/propose_dogma_edit.py` present + tests ≥80%; (4) B8 degradation table in scratchpad + OQ-VE-5 section; (5) `dogma-neuroplasticity.md` `status: Final`; (6) `grep "RESOLVED" docs/research/values-encoding.md` → match. Check all workplan gate item boxes.
- [ ] **F40.** Update issue bodies: write updated checkbox bodies to temp files; `gh issue edit 82 --body-file <path>` and `gh issue edit 75 --body-file <path>`. Verify: `gh issue view 82 --json body -q '.body' | grep -E '\[x\]|\[ \]'`.
- [ ] **F41.** Push and open PR: `git push && gh pr create --base feat/value-encoding-fidelity --title "feat(phase-7): dogma neuroplasticity + back-propagation [#82, #75]" --body-file <temp-body-file>`. Verify: `gh pr view --json title,state`.
- [ ] **F42.** Post progress comments: `gh issue comment 82 --body-file <path>` and `gh issue comment 75 --body-file <path>`. Verify: `gh issue view 82 --json comments -q '.comments[-1].body[:80]'`.
- [ ] **F43.** Monitor CI: `gh run list --limit 3` — all must be `success` before requesting review. Fix failures immediately. If session produced novel patterns (stability tier model, back-propagation evidence threshold), run `@session-retrospective What lessons did we learn this session?` before closing.

---

### Phase 7 Acceptance Criteria Summary

| Deliverable | Path | Verification |
|---|---|---|
| Dogma neuroplasticity synthesis | `docs/research/dogma-neuroplasticity.md` | `validate_synthesis.py` exits 0; `status: Final` |
| Back-propagation protocol | `dogma-neuroplasticity.md` §Recommendations | Evidence threshold, proposal format, coherence check, ADR template all present |
| Stability tier model | `dogma-neuroplasticity.md` §Pattern Catalog | T1/T2/T3 tiers with session thresholds defined |
| `propose_dogma_edit.py` | `scripts/propose_dogma_edit.py` | Smoke test exits 0; output contains `## Coherence Check` |
| Script tests | `tests/test_propose_dogma_edit.py` | `--cov=scripts/propose_dogma_edit` ≥ 80% |
| Degradation analysis | Scratchpad B8 + OQ-VE-5 section | Table spans 4 element types × 2 boundaries |
| OQ-VE-5 resolution | `docs/research/values-encoding.md` §5 | `grep "RESOLVED" docs/research/values-encoding.md` → ≥1 match |
| AGENTS.md amendments | `AGENTS.md` §Focus-on-Descent | `validate_agent_files.py --all` all PASS; edit is additive-only |
| Pre-commit | n/a | ruff + pytest fast-subset all green |
| CI green | branch | `gh run list --limit 3` all `success` |

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
- [x] `MANIFESTO.md` updated with hermeneutics note and 4-form axiom encoding
- [x] `scripts/detect_drift.py` (or equivalent) in CI (Phase α complete; commit ae5bfef)
- [x] `scripts/query_docs.py` functional and documented
- [x] `delegation-routing` and `phase-gate-sequence` skills committed to `.github/skills/`
- [ ] Back-propagation protocol documented in `docs/research/dogma-neuroplasticity.md`
- [x] `docs/research/context-budget-balance.md` committed

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

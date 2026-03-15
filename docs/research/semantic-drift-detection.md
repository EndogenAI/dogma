---
title: Semantic Drift Detection — Closing the T1–T2 Enforcement Gap
status: Draft
research_issue: 197
date: 2026-03-15
---

# Semantic Drift Detection — Closing the T1–T2 Enforcement Gap

## Executive Summary

The EndogenAI governance substrate is enforced across six tiers (T0 — schema; T1 — CI; T2 — static analysis; T3 — pre-commit; T4 — interactive shell governor; T5 — prose). Two prior audits (`enforcement-tier-mapping.md`, `values-enforcement-tier-mapping.md`) establish the coverage baseline: **19 behavioral constraints and 4 values constraints** are enforced at T1–T4; **77 constraints (69% of the 112 inventoried)** remain at T5, prose-only.

The hardened T3+ enforcement core covers **structural** compliance — required headings in D4 documents, required frontmatter fields, required sections in agent files, ruff code style, no-heredoc-writes. What it does not cover is **semantic** compliance: whether the content within those required sections upholds the MANIFESTO.md axiom values, not just the structural skeleton. `scripts/detect_drift.py` exists as an initial semantic check, but its approach — watermark phrase matching against six canonical strings — is a T3-equivalent surface measurement, not a deep semantic comparison.

This draft maps the current T3+ structural coverage precisely, identifies the semantic detection gap at T1–T2, and documents two research paths — **embedding-similarity scoring** and **watermark calibration** — as candidate approaches for closing the gap.

**Governing axiom**: `MANIFESTO.md §2. Algorithms Before Tokens` — encoding drift detection as a deterministic algorithm (T1–T3) is more reliable than relying on human reviewers to notice value erosion in session prompts. `MANIFESTO.md §1. Endogenous-First` — the current `detect_drift.py` methodology and the audit baselines are evaluated before proposing new approaches.

---

## Hypothesis Validation

### H1 — Current T3+ Enforcement Covers Structure, Not Semantics

**Verdict: CONFIRMED by `values-enforcement-tier-mapping.md` audit**

The `values-enforcement-tier-mapping.md` §H1 table states: of 44 values-specific constraints, 40 are T5 (prose-only) and only 4 are T1/T3. The four enforced values constraints are:

| Constraint | Tier | Mechanism |
|------------|------|-----------|
| ≥1 cross-reference per agent file | T3 | `validate_agent_files.py` |
| D4 frontmatter (`title`, `status`) present | T1+T3 | `validate_synthesis.py`, pre-commit |
| D4 required headings present | T1+T3 | `validate_synthesis.py`, CI |
| D4 minimum line count | T1+T3 | `validate_synthesis.py` |

All four are structural. None check whether the content under those headings faithfully encodes foundational axioms. A D4 document that has an `## Executive Summary` heading filled with text that contradicts MANIFESTO.md Axiom 1 passes all current validators.

`scripts/detect_drift.py` extends this to **six watermark phrases**: "Endogenous-First", "Algorithms Before Tokens", "Local Compute-First", "encode-before-act", "morphogenetic seed", "programmatic-first". Detection method: text substring presence (case-sensitive). This is T3-level enforcement added on top of the structural baseline — a necessary but insufficient gate. A file can include all six phrases as an empty acknowledgment without any operational adherence to the underlying values. Substring presence is a proxy for value alignment, not a measurement of it.

**T1–T2 semantic gap**: No current mechanism measures whether the *meaning* of an agent file's instructions is consistent with the *meaning* of MANIFESTO.md axioms. The gap between structural passes + watermark hits and genuine value alignment is the semantic drift detection gap.

### H2 — Watermark Phrase Calibration Can Close Part of the Gap

**Verdict: PLAUSIBLE — requires empirical threshold calibration**

`values-enforcement-tier-mapping.md` §H2 identifies "Watermark phrase integrity check absent" as a T3 (XS effort) gap: adding a check in `validate_synthesis.py` that requires at least one watermark phrase per D4 document. This is partially implemented in `detect_drift.py` (fleet-level scoring with a --threshold flag) but not applied at T1 in CI for synthesis documents.

**Proposed extension**: The detect_drift score (fraction of watermark phrases present) can be interpreted probabilistically. Calibration experiment (open research question): for known-drifted agent files (identified by human review) vs. known-coherent files, measure the distribution of `drift_score`. If the score distributions are separable, a threshold can be derived. `values-enforcement-tier-mapping.md` §H2 suggests the optimal CI threshold may be higher than the current --threshold default of 0.33.

**Limitation**: Watermark phrase matching has false-negative brittleness — it misses semantic equivalents ("draw from internal sources first" ≡ "Endogenous-First" in meaning but not in string). The calibration experiment must also measure false-negative rate by sampling files with high semantic alignment but low phrase density.

### H3 — Embedding Similarity Is the Candidate T2 Mechanism

**Verdict: OPEN RESEARCH PATH — not yet validated in this codebase**

The deeper semantic drift detection mechanism — checking whether the operational meaning of an agent file's instructions is semantically close to the operational meaning of MANIFESTO.md axiom sections — requires vector-space comparison. The approach:

1. **Embed axiom sections**: Compute dense vector representations of MANIFESTO.md §1 (Endogenous-First), §2 (Algorithms Before Tokens), §3 (Local Compute-First).
2. **Embed agent file sections**: Compute dense vector representations of each agent file's instruction/action sections.
3. **Compute cosine similarity**: Each agent section vs. its most relevant axiom. Low similarity (< threshold) signals semantic drift.
4. **Gate at T2 or T1**: Run as a CI check; annotate per-file similarity scores in the drift report.

**Prior art from `values-encoding.md`**: Pattern H3 (Programmatic Encoding is Immune to Semantic Drift) establishes that scripts and CI gates are the strongest defense against drift. The embedding similarity approach would operate at T2 — more semantic than string matching, deterministic once the embedding model is pinned, and runnable locally (`Local Compute-First` — `MANIFESTO.md §3`).

**Open questions**:
- Which embedding model? For local execution, `sentence-transformers/all-MiniLM-L6-v2` (384-dim, ~23MB) is a strong candidate.
- What similarity threshold discriminates drift? Needs calibration against the human-reviewed corpus.
- How to handle multi-axiom files? Take max-similarity, min-similarity, or mean?
- Should T2 be blocking (fail CI) or advisory (annotate, warn)?

### H4 — `validate_agent_files.py` Covers Structure; `detect_drift.py` Covers Surface; Neither Covers Semantic Depth

**Verdict: CONFIRMED by source code review**

`scripts/detect_drift.py` score logic: for each agent file, count which of the 6 `WATERMARK_PHRASES` appear in the file text; compute `drift_score = count / 6`. This is a presence-based fraction, not a semantic similarity measure. It cannot distinguish:
- A file that mentions "Endogenous-First" in a disclaimer vs. one whose instructions are structurally grounded in it
- A file that paraphrases all three axioms accurately but uses zero exact phrases (score = 0.0 → flagged as drifted)
- A file that cites all six phrases in a comment block but whose instructions systematically violate them (score = 1.0 → not flagged)

`validate_agent_files.py` checks: YAML frontmatter required fields; required section headings; minimum cross-reference count; no heredoc patterns. No content-level check.

The coverage map:

| Check type | Tool | Tier | Semantic depth |
|-------------|------|------|----------------|
| Structural headings | `validate_synthesis.py` | T1+T3 | None |
| Frontmatter fields | `validate_synthesis.py` | T1+T3 | None |
| Section presence (agent files) | `validate_agent_files.py` | T1+T3 | None |
| Watermark phrase presence | `detect_drift.py` | T3 (advisory) | Shallow — string match |
| Semantic alignment to axioms | *Not implemented* | **Gap** | **Deep — required** |

---

## Pattern Catalog

### Pattern SD1 — Three-Layer Detection Stack

The semantic integrity of a governance document should be checked at three independent layers, each catching a distinct failure mode:

| Layer | Check | Tool | Tier | Failure mode caught |
|-------|-------|------|------|---------------------|
| Structural | Required headings, frontmatter | `validate_synthesis.py` | T1+T3 | Missing skeleton |
| Superficial semantic | Watermark phrase presence | `detect_drift.py` | T3 | Complete axiom absence |
| Deep semantic | Embedding cosine similarity | *planned* | T2 (proposed) | Semantic misalignment despite structural/superficial pass |

**Canonical example**: The existing D4 research corpus (`docs/research/*.md`, `status: Final`) illustrates a document set that passes all three layers: required headings present; multiple MANIFESTO.md axiom phrases cited; content demonstrably grounded in Endogenous-First methodology (extensive internal citation, no external scaffolding without prior internal check). These documents define the positive reference distribution for any calibration of embedding similarity thresholds.

**Anti-pattern**: An agent file that contains the heading `## Workflow & Intentions` (structural pass ✅), cites "Endogenous-First" once in an opening sentence (watermark pass ✅), but whose instruction body consists exclusively of web-search steps, external API calls, and no reference to any internal endogenous source — passes all current T1–T3 checks while violating the Endogenous-First axiom in its operational meaning. This is the canonical semantic drift false-negative. Embedding similarity would flag it: the instruction body would cluster with the "fetch and summarize external content" semantic space, not with the MANIFESTO.md Endogenous-First axiom section.

### Pattern SD2 — Drift Score Calibration Protocol

Before any embedding similarity threshold can be deployed at T1/T2, a calibration corpus must be assembled and scored:

1. **Positive set** (N ≥ 10): Agent files rated "well-aligned" by two independent human reviewers. These define the upper similarity distribution.
2. **Negative set** (N ≥ 5): Agent files flagged in prior sessions as drifted (identified via scratchpad retrospective blocks or Review agent rejection comments). These define the lower similarity distribution.
3. **Threshold selection**: Choose the cosine similarity threshold $\theta$ that maximizes F1 on the calibration corpus. Accept false-positive rate ≤ 10% (tolerable false alarms) and false-negative rate ≤ 5% (near-zero missed drift).
4. **Stability check**: Re-run the calibration monthly. Drift in the threshold value itself signals that the fleet is evolving semantically — an expected, healthy signal.

### Pattern SD3 — Watermark Phrase Extension

Current `WATERMARK_PHRASES` in `detect_drift.py` covers three axioms and three implementation concepts (6 phrases). Proposed additions to improve recall:

| Phrase | Axiom covered | Rationale |
|--------|---------------|-----------|
| "endogenous source" | Endogenous-First | Common paraphrase; currently missed |
| "token burn" | Algorithms Before Tokens | Standard reduction vocabulary |
| "local model" | Local Compute-First | Concrete implementation phrase |
| "pre-commit" | Algorithms Before Tokens | Programmatic enforcement signal |
| "inheritance chain" | Endogenous-First | Structural cascade concept |

Adding these 5 phrases raises the detectable surface without requiring embedding infrastructure. This is an XS-effort T3 improvement achievable before the embedding approach is validated.

---

## Recommendations

1. **R1 — Raise `detect_drift.py` into CI as a non-blocking T1 job** (scripting sprint): Add `detect_drift.py --format summary --fail-below 0.2` as a CI step in `tests.yml`. The 0.2 threshold (1.2/6 phrases) is a minimal floor that catches completely axiom-free files without over-flagging specialized scripts. Raises `detect_drift.py` from T3 advisory to T1 enforcement.

2. **R2 — Extend `WATERMARK_PHRASES`** (Pattern SD3, XS effort): Add 5 phrases to `detect_drift.py` constants. Requires updating `tests/test_detect_drift.py` to cover new phrases.

3. **R3 — D4 watermark validation in `validate_synthesis.py`** (T3 enforcement, XS effort): Add assertion: each D4 document must contain at least one of {"Endogenous-First", "Algorithms Before Tokens", "Local Compute-First"} in the document body. Already identified in `values-enforcement-tier-mapping.md` §H2 as feasible and prioritized.

4. **R4 — Embedding similarity proof-of-concept** (research sprint, M effort): Implement `scripts/measure_semantic_drift.py` using a local embedding model (sentence-transformers). Compute similarity scores for all current `.agent.md` files vs. MANIFESTO.md §1–§3. Produce distribution report. No CI integration in first pass — observation only. This fulfills the calibration corpus requirement in Pattern SD2.

5. **R5 — Calibration corpus** (Phase 2 prerequisite for R4): Identify positive and negative reference sets from the current fleet and recent Review agent outputs. Document the sets in `docs/research/semantic-drift-detection.md` (this file) before running the similarity experiment.

---

## Sources

- [`docs/research/methodology/values-encoding.md`](methodology/values-encoding.md) — H3 (Programmatic Encoding), B8 Degradation Table, Pattern 2 (structural encoding), baseline values fidelity research
- [`docs/research/methodology/enforcement-tier-mapping.md`](methodology/enforcement-tier-mapping.md) — 68 behavioral constraints, T0–T5 tier distribution, T5 gap inventory
- [`docs/research/methodology/values-enforcement-tier-mapping.md`](methodology/values-enforcement-tier-mapping.md) — 112 constraints (44 values-specific), 91% T5 ratio for values constraints, Watermark phrase gap item
- [`docs/research/methodology/values-substrate-relationship.md`](methodology/values-substrate-relationship.md) — orthogonality of vertical (encoding) and horizontal (topological) models; joint failure mode taxonomy
- [`scripts/detect_drift.py`](../../scripts/detect_drift.py) — current watermark phrase detection implementation; `WATERMARK_PHRASES` constants; `drift_score` computation
- [`scripts/validate_agent_files.py`](../../scripts/validate_agent_files.py) — structural checks for `.agent.md` files; section presence, frontmatter, cross-reference count
- [`MANIFESTO.md`](../../MANIFESTO.md) — Axiom 1: Endogenous-First (§1); Axiom 2: Algorithms Before Tokens (§2); Axiom 3: Local Compute-First (§3)
- [`AGENTS.md`](../../AGENTS.md) — T1–T5 enforcement tier definitions; Value Fidelity Test Taxonomy table

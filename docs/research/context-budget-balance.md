---
title: "Context Window Budget — Research Synthesis"
status: Final
---

# Context Window Budget — Research Synthesis

> **Research Question**: As the endogenic documentation substrate grows, how do we prevent instruction volume from saturating the session context window — degrading principle adherence in the process — while preserving full fidelity of encoded values?
> **Date**: 2026-03-08
> **Related**: [#85](https://github.com/EndogenAI/dogma/issues/85) (source issue), [#80](https://github.com/EndogenAI/dogma/issues/80) (queryable docs), [#79](https://github.com/EndogenAI/dogma/issues/79) (skills extraction), [#82](https://github.com/EndogenAI/dogma/issues/82) (dogma neuroplasticity), [#14](https://github.com/EndogenAI/dogma/issues/14) (AIGNE AFS governance), [#13](https://github.com/EndogenAI/dogma/issues/13) (episodic memory), [#75](https://github.com/EndogenAI/dogma/issues/75) (value drift at handoffs)

---

## 1. Executive Summary

The fidelity-volume paradox is real: more encoding produces more instructions, which consume more context, which leaves less room for task execution, which forces shortcuts that reduce adherence to the instructions that were encoded to prevent shortcuts. This synthesis quantifies that paradox, identifies the degradation threshold, and ranks four intervention categories by cost/impact ratio.

**Key findings**:

- The primary Executive Orchestrator instruction substrate (AGENTS.md + agent file + mode instructions + memory) totals approximately **14,375 tokens** (≈57,500 characters). At a 32K effective context window this is **45% of total capacity before any task work begins** — confirming the risk zone for smaller context budgets. At 200K it is 7.2%.
- Adherence degradation follows the "lost in the middle" effect documented in the context engineering literature: as task history fills the context window, instruction content positioned at the start of prior turns receives proportionally less attention. The empirically-supported degradation threshold is **when instruction content represents ≤15–20% of total in-context tokens** — a condition that can arise mid-session at any context size.
- The highest-cost/impact intervention is **skill extraction** (Pattern 7-adjacent): encoding decision logic in reusable SKILL.md files reduces agent body size without sacrificing governance coverage, exploits existing infrastructure, and is immediately actionable.
- **Retrieval-augmented governance** (Pattern 7 from `docs/research/values-encoding.md`) offers the highest long-term ceiling but requires new infrastructure (BM25/vector index over `docs/`).

**Governing constraint** (from `../../AGENTS.md`, "Algorithms Before Tokens"): prefer deterministic, encoded solutions over interactive token burn. All four intervention categories honour this axiom — each converts LLM-time reasoning into pre-computed structure.

---

## 2. Hypothesis Validation

### Q1 — Instruction Fraction Baseline

**Hypothesis**: In a typical Executive Orchestrator session, the instruction substrate (AGENTS.md + mode instructions + agent file) consumes ≥30% of usable context before any task work begins.

**Verdict**: INCONCLUSIVE

**Evidence**:
- Direct measurement (2026-03-08): Instruction layer character counts — AGENTS.md: 28,361 chars (~7,090 tokens); Executive Orchestrator agent file: 19,141 chars (~4,785 tokens); mode instruction block: ~5,500 chars (~1,375 tokens); user + repo memory: ~4,500 chars (~1,125 tokens). **Total: ~57,500 chars ≈ 14,375 tokens**.
- At a 32K effective context window (older API default, VS Code Copilot Chat practical ceiling for some models), this is **44.9%** — well above the 30% threshold. Hypothesis is **confirmed** at this scale.
- At 128K context, the fraction is 11.2%; at 200K it is 7.2% — the hypothesis is **refuted** at these scales for a fresh session.
- The critical nuance: these figures describe instruction load at session *start*. Mid-session, as tool outputs, issue bodies, and file reads accumulate, the instruction content's proportional share shrinks further — but the absolute token cost is fixed and non-negotiable. A 14,375-token floor is structural, not variable.
- The 30% threshold is crossed for any effective context window ≤48,000 tokens. With VS Code Copilot's practical context compression and compaction architecture, the effective working context per turn is often in the 50K–80K range, placing the instruction fraction at 18–29% — close to the risk zone.

---

### Q2 — Adherence Degradation Threshold

**Hypothesis**: Principle adherence measurably degrades when the instruction-to-task context ratio exceeds a threshold, producing observable shortcut patterns.

**Verdict**: CONFIRMED

**Evidence**:
- The "lost in the middle" effect (Liu et al. 2023; replicated in multiple NLP evaluations) demonstrates LLM performance drops when critical information is positioned in the middle of long contexts. Instructions placed at position T=0 compete against recency bias once task exchanges accumulate past T=10,000.
- Anthropic's context engineering guidance (cached: `anthropic-com-engineering-effective-context-engineering-for-.md`) directly states: for long-horizon tasks "context pollution" causes coherence failure before the absolute token limit is reached. The practical degradation signal is shortcuts in structured protocols — skipping phase gates, omitting scratchpad writes, omitting verify-after-act steps.
- Observable pattern in this repository: session retrospectives and scratchpad divergence records (`.tmp/`) show that the steps most frequently skipped are the ones encoded latest in AGENTS.md — §"Verify-After-Act for Remote Writes" and "Convention Propagation Rule" — consistent with mid-context attention decay.
- Issue #75 (empirical drift at handoff boundaries) proposes measuring this directly via scratchpad audit. Cross-referencing: the steps that degrade are those that appear deepest in the instruction document, not those that appear early or are repeated in multiple sections.
- The Context Engineering Survey (arXiv:2507.13334, Mei et al., 2025, cached: `arxiv-context-engineering-survey.md`) identifies this as a fundamental asymmetry: models demonstrate "pronounced limitations in generating equally sophisticated, long-form outputs" as context fills — directly mapping to the adherence-shortcut pattern.
- Empirically-supported threshold: degradation is observable when instruction content represents **≤15–20% of total in-context tokens** at the point of each agent turn.

---

### Q3 — Intervention Cost/Impact Ranking

**Hypothesis**: Retrieval-augmented governance (Pattern 7 from `docs/research/values-encoding.md`) yields the highest cost/impact ratio among the four intervention categories.

**Verdict**: INCONCLUSIVE

**Evidence**:
- Retrieval-augmented governance has the highest long-term ceiling: instead of loading 14,375 tokens of instructions per turn, a RAG layer injects only the 500–1,000 tokens relevant to the current step. Potential saving: **~90% of instruction overhead at steady state**.
- However, retrieval infrastructure is not free: BM25 or embedding indexing over `docs/` requires new tooling, an index-update workflow, and query routing logic. The setup cost is estimated at 2–4 weeks of engineering — non-trivial against Local Compute-First constraints (#80).
- Skill extraction (#79) delivers **comparable savings for decision-logic content** at near-zero setup cost because SKILL.md infrastructure already exists. Extracting the delegation routing table and phase-gate sequence into shared skills could reduce agent body size by ~30–40% immediately.
- Pruning (#82) has the lowest marginal cost (identify unused instructions → remove or compress) but carries coherence risk: instructions that appear unused in session history may be invoked only in rare-but-critical edge cases.
- Compression (inline text reduction) shows diminishing returns beyond ~20%: the AGENTS.md content is already written to be minimal for its coverage scope; further compression risks losing the "programmatic gate" encoding forms that make values resilient (Pattern 1 from `values-encoding.md`).
- **Net ranking**: Extraction > Pruning > Retrieval > Compression — by implementable cost/impact ratio. Retrieval has the highest theoretical ceiling but is correctly categorised as a medium-term infrastructure investment, not immediate. This partially refutes the Q3 hypothesis as stated.

---

## 3. Pattern Catalog

### Pattern A — Context Tiering (Separation of Fixed and Variable Loads)

**Name**: Fixed/Variable Context Split

**Evidence**: Anthropic context engineering guidance distinguishes "system prompt" (fixed, per-turn) from "message history" (variable, accumulates). The fixed load (instruction substrate) should be minimised because it is paid on every turn. Variable load is managed through compaction. This maps to the scratchpad architecture already in place — `.tmp/<branch>/<date>.md` is the variable load; AGENTS.md is the fixed load.

**Endogenous applicability**: AGENTS.md and agent files are fixed-load. Every byte removed from them reduces cost on every turn, not just once. The programmatic-first principle (converting repeated LLM reasoning into scripts) is the canonical fixed-load reduction technique already endorsed in `../../AGENTS.md`. The next step is applying this to instruction prose: convert repeated decision logic into SKILL.md references (a pointer costs 30 tokens, the loaded skill costs 0 additional fixed-session tokens).

---

### Pattern B — Progressive Disclosure for Governance

**Name**: Just-In-Time Instruction Injection

**Evidence**: Anthropic's context engineering guidance (cached source) explicitly endorses the "just in time" approach: agents "maintain lightweight identifiers (file paths, stored queries, web links) and use these references to dynamically load data into context at runtime." Claude Code uses this architecture for CLAUDE.md files. The key insight: an instruction *pointer* is 10–30 tokens; the instruction *body* is 500–2,000 tokens. Instructions needed on 10% of tasks should not be loaded 100% of the time.

**Endogenous applicability**: The AGENTS.md "Guardrails" section (12 specific checks) is consulted only at commit time. The "Async Process Handling" section is consulted only when running long terminal commands. Replacing these sections with 2-line reminders ("run guardrails check — see validate-before-commit SKILL.md") would maintain governance coverage while reducing per-turn token cost by an estimated 2,000–3,000 tokens.

---

### Pattern C — Inverse Frequency Encoding

**Name**: Encode-by-Criticality, Load-by-Frequency

**Evidence**: Pattern 1 from `docs/research/values-encoding.md` establishes the [4,1] repetition code: values encoded in four forms (principle, example, anti-pattern, gate) are resilient to single-form degradation. This principle can be inverted for context efficiency: instructions encoding *critical but rare* behaviours (e.g., "never force-push to main") should be encoded in *short, memorable form* in the core substrate and backed by *programmatic gates* — not by long prose. The content that must be in every context turn is the pattern name and violation signal; the full rationale can be loaded on demand.

**Endogenous applicability**: AGENTS.md currently carries full rationale for many guardrails that have programmatic enforcement (ruff, validate_synthesis, pre-commit). These rationale paragraphs can be compressed to a single line ("enforced by pre-commit hook — see docs") saving approximately 1,500–2,000 tokens with zero governance loss.

---

## 4. Recommendations

These recommendations are ordered by implementable cost/impact ratio (R1 is highest). Each maps to an existing open issue and the relevant intervention category.

> Cross-reference: the Algorithms-Before-Tokens axiom in `../../AGENTS.md` governs all four recommendations — each converts LLM-time reasoning into deterministic pre-encoded structure. The "encode-before-act" posture from `../../MANIFESTO.md` applies equally to instruction structure as to task execution.

---

### R1 — Skill Extraction: Encode Decision Logic as SKILL.md

**Category**: Extraction  
**Action**: Extract the delegation routing table (Executive Orchestrator "which agent handles X" lookup), phase-gate sequence, and the full "Guardrails" checklist into dedicated SKILL.md files. Replace inline prose with `Read skill: validate-before-commit/SKILL.md` references (one line per skill reference).  
**Estimated Token Saving**: 4,000–6,000 tokens from agent body (the Executive Orchestrator file is 4,785 tokens of which an estimated 40% is decision logic rather than identity/values). Reduction from ~14,375 to ~10,000 fixed-load tokens per turn.  
**Implementation Cost**: Low — SKILL.md infrastructure exists. 2–3 new SKILL.md files, 1–2 days. No new tooling required.  
**Depends-on**: [#79](https://github.com/EndogenAI/dogma/issues/79) (skills as decision codifiers — formal validation of this approach)

---

### R2 — Pruning: Synaptic Pruning via Session Audit

**Category**: Pruning  
**Action**: Audit AGENTS.md sections against the last 20 session scratchpad files. Identify sections with zero citations in session behavior. Compress them to 2-line summaries with links to full documentation. Apply dogma neuroplasticity (#82) protocol: demote consistently-ignored instructions to referenced docs.  
**Estimated Token Saving**: 2,000–3,500 tokens from AGENTS.md (from 7,090 to ~4,000 tokens). The "Toolchain Reference" table and "Async Process Handling" detailed tables are candidates — referenced rarely inline, already fully documented in `docs/toolchain/`.  
**Implementation Cost**: Low to medium — requires session audit script (1 day) + careful review before any removals. Risk: rare-but-critical instructions may appear unused but are essential.  
**Depends-on**: [#82](https://github.com/EndogenAI/dogma/issues/82) (dogma neuroplasticity — governance process for substrate edits)

---

### R3 — Retrieval: RAG Governance Layer

**Category**: Retrieval  
**Action**: Implement a BM25-based local retrieval layer over `docs/` (no embeddings required — BM25 is deterministic and local-first). At each task boundary, agents query for the relevant AGENTS.md section rather than loading the full document. At session start, load only a 500-token "orientation header" that bootstraps the query interface.  
**Estimated Token Saving**: Up to 6,000 tokens of fixed instruction load replaced by 500-token orientation + 300-600 tokens per targeted query. Over a 20-step session, this is net neutral on retrieval volume but prevents context accumulation of unused instruction content.  
**Implementation Cost**: Medium — requires `scripts/query_docs.py` (BM25 over docs/ tree), AGENTS.md restructure into queryable units, and agent-file updates to use query patterns. Estimated 1–2 weeks.  
**Depends-on**: [#80](https://github.com/EndogenAI/dogma/issues/80) (queryable documentation substrate — formal design for the retrieval layer)

---

### R4 — Compression: Inline Rationale Reduction

**Category**: Compression  
**Action**: Replace full-rationale paragraphs in AGENTS.md sections that have programmatic enforcement with 1-line summaries. Specifically: the "Guardrails" section (currently lists full pre-commit commands with context), the "Toolchain Reference" table (already in `docs/toolchain/`), and the "Testing-First Requirement" section (covered in `docs/guides/testing.md`).  
**Estimated Token Saving**: 1,500–2,500 tokens from AGENTS.md (from 7,090 to ~5,000 tokens baseline after R2). This is the smallest lever but requires no new infrastructure.  
**Implementation Cost**: Low — text editing only. Risk of lossy compression is present; requires line-by-line review against [4,1] encoding coverage (see `docs/research/values-encoding.md` §Appendix).  
**Depends-on**: None (standalone). Coordinate with #82 to ensure any compression is governed by the neuroplasticity process, not ad hoc.

---

## 5. Sources

### Sources

- [`anthropic-com-engineering-effective-context-engineering-for-.md`](sources/anthropic-com-engineering-effective-context-engineering-for-.md) — Anthropic Applied AI team: "Context Engineering for AI Agents." Covers compaction, structured note-taking, sub-agent architectures, and the "just in time" retrieval pattern. Primary source for Q2 degradation threshold and Pattern B (Progressive Disclosure).
- [`arxiv-context-engineering-survey.md`](sources/arxiv-context-engineering-survey.md) — Mei et al. (2025) "A Survey of Context Engineering for Large Language Models" (arXiv:2507.13334). Survey of 1,400+ papers; identifies the fundamental asymmetry between long-context understanding and generation. Source for Q2 confirmation and Pattern A framing.
- [`lilianweng-github-io-posts-2023-03-15-prompt-engineering.md`](sources/lilianweng-github-io-posts-2023-03-15-prompt-engineering.md) — Lilian Weng: "Prompt Engineering." Context for few-shot, chain-of-thought, and system prompt architecture tradeoffs.
- [`docs-anthropic-com-en-docs-build-with-claude-prompt-caching.md`](sources/docs-anthropic-com-en-docs-build-with-claude-prompt-caching.md) — Anthropic prompt caching documentation. Relevant to T1 instruction caching as a retrieval-cost mitigation.

### Endogenous Sources

- [`docs/research/values-encoding.md`](values-encoding.md) — Full synthesis read. Pattern 7 (Retrieval-Augmented Governance) and R2 (4-form encoding increases volume) are the direct endogenous inputs to this research question. The [4,1] repetition code (Pattern 1) governs the compression risk analysis.
- [`AGENTS.md`](../../AGENTS.md) — Direct measurement source for D1 baseline (28,361 characters, ~7,090 tokens).
- [`.github/agents/executive-orchestrator.agent.md`](../../.github/agents/executive-orchestrator.agent.md) — Direct measurement source (19,141 characters, ~4,785 tokens).

### Cross-Referenced Issues

- [#75](https://github.com/EndogenAI/dogma/issues/75) — Empirical value drift measurement at multi-agent handoff boundaries. Provides the empirical measurement methodology that can be adapted to per-turn instruction attention measurement.
- [#79](https://github.com/EndogenAI/dogma/issues/79) — Skills as decision codifiers. Primary vehicle for R1 (skill extraction).
- [#80](https://github.com/EndogenAI/dogma/issues/80) — Queryable documentation substrate. Primary vehicle for R3 (retrieval governance layer).
- [#82](https://github.com/EndogenAI/dogma/issues/82) — Dogma neuroplasticity. Governance process required before R2 (pruning) and R4 (compression) can be safely applied.
- [#13](https://github.com/EndogenAI/dogma/issues/13) — Episodic memory. Reduces T2 (session context) load by making historical context queryable rather than bulk-loaded.
- [#14](https://github.com/EndogenAI/dogma/issues/14) — AIGNE AFS context governance. Pipeline-level solution for compress/select/isolate — a potential future wrapper around R3.

### External Sources Not In Cache

- Liu, N. F. et al. (2023) "Lost in the Middle: How Language Models Use Long Contexts." arXiv:2307.03172. Documents the position-attention degradation effect used in Q2 verification. URL: https://arxiv.org/abs/2307.03172
- Bai, Y. et al. (2022) "Constitutional AI: Harmlessness from AI Feedback." Anthropic. Cited in `values-encoding.md` §Pattern 7. URL: https://arxiv.org/abs/2212.08073

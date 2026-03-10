---
title: "Epigenetic Tagging — Context-Sensitive Axiom Amplification"
status: "Final"
---

# Epigenetic Tagging — Context-Sensitive Axiom Amplification

> **Status**: Final
> **Research Question**: How should the endogenic system amplify different axioms for different task contexts — and what is the minimal viable mechanism to implement this without new infrastructure?
> **Date**: 2026-03-09
> **Issue**: [#72](https://github.com/EndogenAI/Workflows/issues/72)
> **Related**: [`docs/research/values-encoding.md`](values-encoding.md) §5 OQ-VE-2 (source of the regulatory-region gap); [`docs/research/bubble-clusters-substrate.md`](bubble-clusters-substrate.md) (boundary-membrane model — epigenetic tagging is boundary-permeability calibration)

---

## 1. Executive Summary

Every cell in a human body carries the same genome. Yet a liver cell expresses different genes than a neuron. The difference is not in the DNA — it is in the **regulatory regions**: promoters, enhancers, and epigenetic marks (methylation, histone acetylation) that determine which genes are amplified in which cellular context.

`docs/research/values-encoding.md` §H5 identified the same gap in the endogenic substrate: the current system treats all three axioms as equally active in all contexts. A session doing deep research should amplify Endogenous-First; a session committing should amplify Documentation-First; a session writing scripts should amplify Algorithms Before Tokens. Without context-sensitive regulation, the axioms are stated but not calibrated to the task at hand.

**This research resolves OQ-VE-2 from `values-encoding.md` §5** — see the resolution note already appended to that document. The Phase 1 mechanism has been **implemented**: an AGENTS.md lookup table (§Context-Sensitive Amplification) maps task-type keyword groups to the axiom that should be amplified, and agents consult it during the encoding checkpoint at session start.

This document provides the **theoretical foundation** and **mechanism comparison** that justify the implemented approach, and frames the deferred Phase 2 script implementation as future work.

**Mechanism compared:**

| Mechanism | Complexity | Drift risk | Alignment with existing tooling | Recommendation |
|-----------|-----------|-----------|--------------------------------|---------------|
| YAML frontmatter `amplify:` per agent file | Low per file | High (dispersed updates) | Requires VS Code mode instruction support | Not recommended for Phase 1 |
| AGENTS.md lookup table *(implemented)* | Very low | Low (centralized, single-edit propagation) | Works today — agents read AGENTS.md at session start | **Adopted** |
| `scripts/amplify_context.py` *(deferred)* | Medium | Very low (programmatic enforcement) | Requires new script + CI integration | Deferred to Phase 2 |

**Key finding**: The AGENTS.md lookup table is the correct Phase 1 mechanism because it requires no new tooling and propagates immediately to all agents via the session-start ritual. The Phase 2 script will complete the programmatic governance layer by prepending the relevant axiom block from `MANIFESTO.md` verbatim to each session scratchpad — closing the gap between human-directed amplification and automated enforcement.

**Hypotheses validated:**

- **H1** — Biological epigenetic mechanisms (methylation, histone modification) provide a precise and instructive analog for context-sensitive axiom amplification in instructional substrates.
- **H2** — Constitutional AI per-task constitution variants (Bai et al. 2022) confirm this pattern is practiced in deployed AI systems.
- **H3** — A centralized lookup table (AGENTS.md) is the minimum-viable implementation with the lowest drift risk for Phase 1.
- **H4** — The YAML frontmatter approach carries high dispersal risk and is not recommended for primary mechanisms affecting all agents.

---

## 2. Hypothesis Validation

### H1 — Biological Epigenetics Is a Precise Analog

**Verdict: CONFIRMED**

**Biological mechanism**: DNA methylation (adding a methyl group to cytosine residues) silences gene expression in contexts where the gene should not be active. Histone acetylation has the opposite effect: it relaxes chromatin structure, making genes more accessible to transcription machinery — effectively amplifying expression. Neither mechanism changes the DNA sequence; both regulate which sequences are expressed in which cell type.

**Instructional analog**:
- **Methylation (silencing)**: The agent's context window naturally silences less-relevant axioms by not explicitly invoking them. A commit session does not need to re-read the entire Endogenous-First protocol before pushing — the session-start ritual having already happened is the equivalent of permanent epigenetic marking.
- **Histone acetylation (amplification)**: The lookup table adds an explicit amplification mark at session start: "for this task type, this axiom is the most relevant — name it in your encoding checkpoint." The mark is not permanent (it applies to this session's context window) and does not change the axiom — it makes it more accessible to the agent's working context.

**Waddington's epigenetic landscape**: Waddington (1957) described development as a ball rolling down a landscape of valleys — the valleys represent stable cell types, the ridges represent differentiation choices. Context-sensitive amplification creates an epigenetic landscape for agent task types: the agent rolls into the most appropriate axiom-emphasis valley based on its task context at session start. The "landscape" is the AGENTS.md lookup table; the "rolling" is the session-start encoding checkpoint.

**Connection to MANIFESTO.md — Axiom: Endogenous-First (§1)**: The lookup table is itself an endogenous source — it is read at session start as part of the AGENTS.md read. The amplified axiom is then stated explicitly in `## Session Start`. This is the Endogenous-First axiom applied recursively: the system reads its own regulatory instructions before acting.

---

### H2 — Constitutional AI Per-Task Variants Confirm the Pattern

**Verdict: CONFIRMED** (Bai et al. 2022; Anthropic deployment practice)

Constitutional AI applies the same base model to different contexts by prepending different constitutional principles. A "helpful assistant" deployment emphasizes user instruction-following; a "safe research tool" deployment emphasizes harm avoidance above helpfulness. The constitution changes; the underlying model does not.

The endogenic analog: the foundational axioms in `MANIFESTO.md` are the "base model" — they never change per task. The lookup table is the "per-task constitution": a context-sensitive weighting that prepends the most relevant axiom emphasis to the session start ritual. The distinction between axiom (immutable) and amplification signal (context-variable) mirrors the Constitutional AI distinction between the base model (stable) and the constitution (task-deployable).

**Pattern 7 connection** (`values-encoding.md` §3): Constitutional AI's retrieve-then-apply architecture is also the model for the Phase 2 script — rather than the agent memorizing which axiom to amplify, the `amplify_context.py` script retrieves the relevant axiom block from `MANIFESTO.md` verbatim and prepends it to the scratchpad. This prevents lossy re-encoding (the agent paraphrasing the axiom from memory) and enforces the Endogenous-First read order programmatically.

---

### H3 — AGENTS.md Lookup Table Is Optimal for Phase 1

**Verdict: CONFIRMED**

Three properties make the centralized lookup table the correct Phase 1 implementation:

1. **Single-edit propagation**: A change to the AGENTS.md table propagates immediately to all agents without requiring edits to individual agent files. Compare to the YAML frontmatter approach, where every agent file requires a separate `amplify:` field update — N agent files = N potential drift points.

2. **No new tooling**: All agents already read `AGENTS.md` at session start. The lookup table is a zero-infrastructure addition to an already-read document. The YAML frontmatter approach requires VS Code mode instruction parsing; the script approach requires a new script and CI integration. Both have higher adoption friction.

3. **Human-legible governance**: The AGENTS.md lookup table is human-readable and editable through normal PR review. Any change to which axiom is amplified for which task type is visible in the diff and subject to standard review. This aligns with the Documentation-First and Validate & Gate principles.

---

### H4 — YAML Frontmatter Approach Has High Drift Risk

**Verdict: CONFIRMED — not recommended**

Dispersed implementation across N agent files creates N independent drift vectors. If the amplification rules change (e.g., a new task type is added), every agent file requires a separate PR. In practice, the update will be made to some files but not others, creating inconsistent amplification behavior. The lookup table approach eliminates this by concentrating the rule to one location.

**Canonical example**: When the `agent / skill / authoring / fleet` task type row was added to the AGENTS.md lookup table, every agent in the fleet immediately benefited. Under the YAML frontmatter approach, only agent files explicitly updated with `amplify: endogenous-first+minimal-posture` would have received the new rule — all others would have continued with stale amplification behavior.

**Anti-pattern**: An agent file with a hardcoded `amplify: endogenous-first` frontmatter field that was correct when written but not updated when the amplification rules evolved. The hardcoded field silently produces incorrect amplification for the agent's current task type, with no visible signal to the reviewer that the amplification is stale.

---

## 3. Pattern Catalog

### Pattern F1 — Centralized Epigenetic Register (AGENTS.md Lookup Table)

**Source fields**: Epigenetics (Waddington 1957, methylation mechanisms), Constitutional AI (per-task constitution), software pattern (centralized config over distributed config)

**Pattern**: Encode all context-sensitive amplification rules as a single, centralized lookup table in the shared constraint document (AGENTS.md). The table is the epigenetic register: it maps task-type contexts to the axiom amplification signal. All agents consult it uniformly at session start; no agent file carries its own amplification metadata.

**Current implementation** (AGENTS.md §Context-Sensitive Amplification — Phase 1):

| Primary task type keyword | Amplify principle | Expression hint |
|---|---|---|
| research / survey / scout / synthesize | **Endogenous-First** | Read prior docs and cached sources before reaching outward |
| commit / push / review / merge / PR | **Documentation-First** | Every changed workflow/agent/script must have accompanying docs |
| script / automate / encode / CI | **Programmatic-First** | If done twice interactively → encode as script before third time |
| agent / skill / authoring / fleet | **Endogenous-First** + **Minimal Posture** | Read existing fleet before spawning; carry only required tools |
| local / inference / model / cost | **Local Compute-First** | Prefer local model invocation; document when external API is required |

**Canonical example**: A session beginning with the task "synthesize findings from Phase 5 and Phase 6B" matches the `research / survey / scout / synthesize` row. The encoding checkpoint writes: *"Governing axiom: Endogenous-First — primary endogenous source: `docs/research/values-encoding.md`."* The amplification causes the agent to read existing research docs before considering any external fetch — exactly the behavior the Endogenous-First axiom requires, now explicitly surfaced rather than merely implied.

**Anti-pattern**: An agent writing a session-start encoding checkpoint without consulting the lookup table. The result is a generic "I am Endogenous-First" statement regardless of task type — correct for research tasks, but insufficiently specific for commit tasks (where Documentation-First should be amplified) or scripting tasks (Algorithms Before Tokens). Generic statements carry lower signal than task-specific amplification; they are axiom-naming without axiom-application.

**Actionable implication**: The lookup table is the current implementation. Future sessions that identify missing task-type rows should propose additions via the standard T3 dogma edit path (two-session signal → AGENTS.md PR, no formal ADR required per `dogma-neuroplasticity.md` Pattern C1).

---

### Pattern F2 — Phase 2: Retrieval-Augmented Amplification Script

**Source fields**: `values-encoding.md` §3 Pattern 7 (Retrieval-Augmented Governance), Constitutional AI retrieval architecture

**Pattern**: A `scripts/amplify_context.py` script that, given a task type or keyword, retrieves the relevant axiom block from `MANIFESTO.md` verbatim and prepends it to the session scratchpad. This upgrades from human-directed amplification (Phase 1: the agent is told which axiom applies) to automated amplification (Phase 2: the relevant axiom text is injected directly, preventing paraphrase from memory).

**Phase 2 design** (deferred pending two-session validation of Phase 1 lookup table):

```python
# scripts/amplify_context.py (Phase 2 — not yet implemented)
# Usage: uv run python scripts/amplify_context.py --task-type "research" --scratchpad .tmp/branch/date.md
#
# 1. Read the lookup table from AGENTS.md §Context-Sensitive Amplification
# 2. Match task_type to the nearest keyword row
# 3. Retrieve the corresponding axiom section from MANIFESTO.md verbatim (not paraphrased)
# 4. Prepend the axiom block to the scratchpad as a ## Axiom Amplification header
# Tests: ≥80% coverage required (per issue #72 D4 gate deliverable)
```

**Deferred rationale**: The lookup table must be validated across at least two full sessions before scripting the automation. Premature scripting of an unvalidated mechanism bakes in errors that are harder to correct at the code layer than at the AGENTS.md text layer. This follows the Programmatic-First principle (MANIFESTO.md — Guiding Principle): *if done twice interactively → encode as script before the third time*.

---

## 4. Recommendations

Ordered by impact-to-cost:

### R1 — Validate Phase 1 Lookup Table Across Two Additional Sessions (Pattern F1)

**Target**: All sessions; AGENTS.md lookup table
**Action**: Before implementing Phase 2, validate the Phase 1 lookup table in at least two more session types beyond research tasks. Specifically: one commit session (Documentation-First amplification) and one scripting session (Algorithms Before Tokens amplification). Log the amplification signal in `## Session Start` and note in `## Session Summary` whether the amplification was correctly matched.
**Rationale**: The T3 dogma edit threshold (two independent session signals) applies to the lookup table entries themselves. Validation data also informs Phase 2 script design.

### R2 — Implement amplify_context.py (Pattern F2) Following Phase 1 Validation

**Target**: `scripts/amplify_context.py` (new)
**Action**: After two sessions validate the lookup table, implement the Phase 2 retrieval script. The script reads the AGENTS.md lookup table, matches the task-type argument, retrieves the axiom block from `MANIFESTO.md` verbatim, and prepends it to the scratchpad. Tests must achieve ≥80% coverage (issue #72 D4 gate).
**Rationale**: Closes the programmatic-governance gap. Human-directed amplification (Phase 1) is vulnerable to the session-start checkpoint being skipped; script-directed amplification (Phase 2) is not.

### R3 — Document Task-Type Coverage Gaps in AGENTS.md Lookup Table

**Target**: `AGENTS.md` §Context-Sensitive Amplification
**Action**: After each session where no lookup table row matches cleanly, log the unmatched task type as a candidate row addition. When two sessions identify the same gap, add the row via the T3 dogma edit path.
**Rationale**: The lookup table's coverage is currently calibrated to five task types. Systematically extending it as new task types emerge follows the dogma neuroplasticity protocol (Pattern C2 from `dogma-neuroplasticity.md`).

---

## Sources

**Endogenous (primary)**:
- `docs/research/values-encoding.md` — §H5 (regulatory regions gap), §5 OQ-VE-2 (original question), §3 Pattern 5 (programmatic governance as epigenetic layer), §3 Pattern 7 (retrieval-augmented governance)
- `docs/research/bubble-clusters-substrate.md` — Pattern B1 (calibrated membrane permeability — epigenetic tagging as boundary-permeability calibration), Pattern B3 (evolutionary pressure test for differentiation rationale)
- `docs/research/dogma-neuroplasticity.md` — Pattern C1 (stability tier model — T3 lookup table update path), Pattern C2 (back-propagation protocol)
- `MANIFESTO.md` — Axiom: Endogenous-First (§1); Guiding Principle: Programmatic-First; Guiding Principle: Algorithms Before Tokens (§2)
- `AGENTS.md` — §Context-Sensitive Amplification (Phase 1 implementation)

**External (supporting)**:
- C.H. Waddington (1957) — *The Strategy of the Genes* — epigenetic landscape model, histone modification as expression regulation
- Holliday & Pugh (1975) — DNA methylation as heritable epigenetic mark — silencing mechanism analog
- Bai et al. (2022) — "Constitutional AI: Harmlessness from AI Feedback" — per-task constitution as context-sensitive amplification in deployed AI systems

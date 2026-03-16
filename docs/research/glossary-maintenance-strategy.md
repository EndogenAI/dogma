---
title: "Glossary Maintenance Strategy — Keeping a Living Vocabulary Synchronised Across Human Contributors and AI Agents"
status: Final
research_sprint: "Sprint 12 — Intelligence & Architecture"
wave: 4
closes_issue: 267
governs: []
---

# Glossary Maintenance Strategy — Keeping a Living Vocabulary Synchronised Across Human Contributors and AI Agents

> **Status**: Final
> **Research Question**: What is the optimal strategy for maintaining a living glossary that remains synchronised across human contributors and AI agents, without becoming stale or causing definition drift?
> **Date**: 2026-03-15
> **Related**: [`docs/research/substrate-atlas.md`](substrate-atlas.md) · [`docs/research/reading-level-assessment-framework.md`](reading-level-assessment-framework.md) · [`docs/research/platform-agnosticism.md`](platform-agnosticism.md) · [`docs/glossary.md`](../glossary.md) · [`AGENTS.md` §Documentation Standards](../../AGENTS.md#documentation-standards) · [Issue #267](https://github.com/EndogenAI/dogma/issues/267)

---

## 1. Executive Summary

The optimal glossary maintenance strategy for a dual-audience repository (human contributors + LLM agents) is **single-source canonical authority** — one file (`docs/glossary.md`) with programmatic validation hooks that detect term presence violations and definition drift across the corpus. The key research findings challenge the default assumption that a richer, more comprehensive glossary is better: for LLM agents, a concise, structurally regular glossary with consistent definition format outperforms a comprehensive but irregularly structured one.

The existing `docs/glossary.md` in this repository is a strong foundation — 1,123 lines, 11 semantic sections, consistent `**Term**` bold-term format, citation references to authoritative sources. The gap is not the glossary's quality; it is the absence of programmatic validation that would detect when new terms introduced in AGENTS.md or research docs are not reflected in the glossary, and when existing definitions drift from their usage in the corpus.

Key findings:

1. **H1 confirmed: single canonical glossary reduces definition divergence vs. inline per-doc definitions.** When a term is defined in multiple places (inline in AGENTS.md, inline in research docs, and in the glossary), the three definitions diverge over time through independent editorial updates. A single canonical source with inline cross-references (not inline definitions) eliminates the divergence surface.

2. **H2 confirmed with implementation specifics: programmatic validation hooks improve maintenance fidelity.** Two distinct hooks are needed: (a) term-presence detection — scan governance docs for bold terms and check that each term appears in the glossary; (b) definition-drift detection — compare the glossary definition of a term against its usage context in AGENTS.md sections to flag divergence. Both are scriptable with `re` and Markdown AST parsing.

3. **The dual-audience constraint requires a glossary format that serves both readers**: human contributors scan for conceptual orientation (narrative context, cross-references, examples); LLM agents parse for constraint application (exact definition, authoritative source, canonical usage). The current `docs/glossary.md` structure — bold term + colon + definition sentence + citation — satisfies both.

4. **Endogenous-First** (MANIFESTO.md §1): `docs/glossary.md` already exists with 11 semantic sections covering Core Axioms, Agent Fleet Concepts, Substrates, and Anti-patterns. The maintenance strategy extends this existing asset; it does not propose replacing or restructuring it.

---

## 2. Hypothesis Validation

### H1 — A single canonical glossary file reduces definition divergence vs. inline per-doc definitions

**Verdict**: CONFIRMED

**Evidence**:

**The divergence mechanism**: Inline definitions accumulate through the normal process of doc authoring — a contributor adds a parenthetical definition to clarify a term in context, and that definition becomes a second authoritative source. Over multiple contributors and sprints, the inline definition evolves independently from the canonical glossary entry. Example: "encoding drift" is defined in AGENTS.md §Value Fidelity Test Taxonomy implicitly ("signal loss at every layer") and in the glossary explicitly. If a sprint edits the glossary definition without updating the AGENTS.md implicitly-defined usage, divergence accumulates.

**Cross-reference to platform-agnosticism evidence**: [`docs/research/platform-agnosticism.md`](platform-agnosticism.md) §2 identifies multi-contributor, multi-tool contexts as the primary driver of uncontrolled register and vocabulary variance. A glossary without enforcement is a statement of intent, not a constraint. The enforcement mechanism (validation hooks) is what converts a glossary from advisory to authoritative.

**Single-source pattern in software engineering**: The DRY principle (Don't Repeat Yourself) applied to documentation: a definition exists in exactly one place; all other occurrences are cross-references. Cross-references resolve to the authoritative definition at read time (following the link) rather than embedding a potentially stale copy. This is the correct architectural choice for a corpus that is read by LLM agents that follow links rather than inferring context from proximity.

**Endogenous evidence**: The current `docs/glossary.md` already enforces single-source for 40+ terms. The gap is the enforcement mechanism — new terms introduced in research docs or AGENTS.md sections do not automatically trigger a pull-request check that validates glossary inclusion.

### H2 — Programmatic validation hooks improve maintenance fidelity

**Verdict**: CONFIRMED — two distinct hooks identified with implementation paths

**Evidence**:

**Hook 1 — Term Presence Detection**: Scan all governance docs for bolded terms matching `\*\*[A-Z][a-zA-Z -]+\*\*` (capitalized bold terms). Check each unique term against the glossary index. Terms absent from the glossary are candidates for addition. This is analogous to a "missing import" compiler warning: a term used but not declared in the glossary creates a soft dependency on context inference. Implementation: extend `scripts/check_substrate_health.py` or create `scripts/check_glossary_coverage.py` — a 30-line script using `re` and `pathlib`.

**Hook 2 — Definition Drift Detection**: For each term defined in the glossary, extract the first sentence of its definition. Search for the same term in AGENTS.md and research docs. If a document contains a parenthetical definition of the term that diverges from the first sentence of the glossary entry (Levenshtein distance > 0.4 normalised), flag as definition drift. Implementation requires `difflib.SequenceMatcher` (standard library) — no additional dependencies. This implements the **Algorithms Before Tokens** principle (MANIFESTO.md §2): drift detection is a deterministic string comparison, not an LLM-assessed quality judgment.

**Calibration requirement**: Hook 2 requires calibrating the divergence threshold against the current corpus. Many inline usages are intentionally abbreviated (glossary entries are comprehensive; inline usage is a usage, not a definition). The hook should detect divergence in the *semantic claim*, not stylistic abbreviation. An initial threshold of Levenshtein distance > 0.4 on the first sentence may require adjustment after false-positive analysis.

---

## 3. Pattern Catalog

### P1 — Canonical Link-Out instead of Inline Definition

**Description**: When a term requires a definition in-context, provide a Markdown cross-reference to the glossary entry (`[term](../glossary.md#term)`) rather than an inline definition. The cross-reference resolves to the authoritative definition; the inline note remains context-specific and does not create a competing definition. This eliminates the divergence surface while preserving in-context navigability.

**Canonical example**: AGENTS.md §Agent-Role Terminology section uses bold terms with one-line explanations: "**Character**: A specialized agent with narrow domain scope…" followed by "**Role**: A broader functional agent classification…". These are concise contextual usages, not full definitions. The correct approach is to link each bold term to its `docs/glossary.md` entry at first occurrence in each section, so the reader can navigate to the full canonical definition without the section needing to maintain a competing copy. The **Endogenous-First** axiom (MANIFESTO.md §1) applies: the glossary already has the definitions; the sections need only link, not copy.

**Anti-pattern**: Defining a term in full inside a SKILL.md or `.agent.md` body — for example, "**Encoding inheritance chain** (MANIFESTO.md → AGENTS.md → role files → SKILL.md files → session behaviour): the cascade of encoding layers through which values flow". This 20-word inline definition will diverge from the glossary entry the next time either is edited independently. The inline form should be replaced with a one-line contextual summary plus a link to the glossary entry at `../glossary.md` (relative from `docs/research/`).

---

### P2 — Semantic Section Groups for LLM Navigation

**Description**: Organise the glossary into named semantic sections (as `docs/glossary.md` currently does: Core Axioms, Methodology Concepts, Agent Fleet Concepts, etc.) rather than a flat alphabetical list. Semantic grouping provides LLM agents with a navigation index — an agent researching "encoding" concepts can load the Methodology Concepts section rather than a full 1,100-line alphabetical document. Flat alphabetical indexes are optimized for human lookup speed; semantic groups are optimised for LLM context-window efficiency. Cross-reference: [`docs/research/substrate-atlas.md`](substrate-atlas.md) defines substrates by category, not alphabetically, for the same reason.

**Canonical example**: `docs/glossary.md`'s current 11 sections (Core Axioms through Anti-patterns) map directly to the conceptual domains an LLM agent needs when interpreting governance constraints. An agent processing an AGENTS.md constraint touching "encoding drift" can navigate to §Methodology Concepts and load only that section (≈ 150 lines) rather than the full 1,100-line document. The section anchor links in the Contents table at the top of `docs/glossary.md` enable this targeted navigation — they are used by LLM agents, not only humans.

**Anti-pattern**: A single flat alphabetical glossary without section grouping. For human lookup, alphabetical order is slightly faster. For LLM consumption (where the agent needs all definitions in a conceptual domain to build a coherent context frame), a flat alphabetical list wastes context window budget loading unrelated terms between the target entries. A 1,100-line alphabetical glossary may need to be fully loaded; an 11-section semantic glossary allows loading 1–2 relevant sections (150–300 lines) to cover any single conceptual domain.

---

### P3 — Programmatic Glossary Coverage Gate in CI

**Description**: Add a CI check that scans the corpus for bold-capitalised terms (potential glossary candidates) and verifies each appears in `docs/glossary.md`. New terms introduced by a PR that are not in the glossary generate a WARN (not a FAIL, during the calibration period). After calibration, promote to FAIL. This is the enforcement mechanism that converts the glossary from advisory to authoritative — without it, the single-source strategy relies entirely on author discipline.

**Canonical example**: `validate_synthesis.py` already enforces the presence of `**Canonical example**:` and `**Anti-pattern**:` labels in Pattern Catalog sections. The glossary coverage gate follows the same enforcement pattern: a regular-expression scan for structural markers (bold terms) in governance docs, validated against an authoritative index (the glossary). Both enforce the "declare what you use" contract — synthesis docs declare structural patterns; governance docs declare vocabulary. The **Algorithms Before Tokens** principle (MANIFESTO.md §2): term presence is a deterministic static check, not a human readability assessment.

**Anti-pattern**: Relying on PR review comments to catch missing glossary entries. Human reviewers miss new terms at high PR volume; they also lack a systematic way to check whether a bold term already has a glossary entry without manually scrolling through 1,100 lines. A CI gate that outputs "5 bold terms not in glossary: [list]" provides precise, actionable feedback in < 5 seconds. The reviewer's cognitive budget is preserved for substantive review; mechanical checks are delegated to the automation layer.

---

## 4. Recommendations

1. **Maintain `docs/glossary.md` as the single canonical vocabulary source.** Do not add full term definitions inline in AGENTS.md, SKILL.md, or research docs — use cross-reference links to the glossary instead. Contextual summaries (one clause) plus links are acceptable.

2. **Commission `scripts/check_glossary_coverage.py`** to scan governance docs for bold-capitalised terms and report coverage gaps. Integrate with `scripts/check_substrate_health.py` for unified substrate health reporting.

3. **Add a definition drift check** using `difflib.SequenceMatcher` comparing first definition sentences in the glossary against parenthetical definitions in AGENTS.md and research docs. Run as an advisory WARN in CI initially.

4. **Preserve the current 11-section semantic structure** of `docs/glossary.md` — it is well-designed for dual-audience navigation. Do not flatten to alphabetical order. Add new terms to the appropriate existing section; create a new section only when ≥ 5 related terms exist that do not fit any existing section.

5. **Document the link-out pattern** (P1) in `docs/guides/agents.md` authoring guidance: "When introducing a technical term from `docs/glossary.md`, link to the glossary entry at first occurrence rather than defining inline."

6. **Treat the glossary as a substrate validation artefact**, not just reference documentation. Its coverage directly determines how precisely LLM agents can resolve term references without resorting to contextual inference — a measurable encoding fidelity metric.

---

## 5. Project Relevance

`docs/glossary.md` is one of the most structurally mature artefacts in the repository — 1,123 lines, organised semantic sections, citation discipline. This research's contribution is to position it as an active enforcement layer, not passive reference material. The shift from reference to enforcement is the same transition that `validate_synthesis.py` made for synthesis documents: a manually-maintained format constraint became a CI-enforced structural contract.

The dual-audience constraint is particularly acute for vocabulary documents: human contributors read the glossary for conceptual orientation, often scanning multiple sections to build a mental model. LLM agents read the glossary for definition resolution, typically looking up a single term to resolve an ambiguous constraint. The semantic section structure (§P2) serves both modes simultaneously — humans browse sections; agents navigate to a specific section via anchor link.

The **Endogenous-First** axiom (MANIFESTO.md §1) drives the core recommendation: do not create a new vocabulary management system when `docs/glossary.md` is already a well-structured 11-section reference. The gap is tooling (coverage validation script) and convention (link-out instead of inline definition). Both are low-effort, high-leverage additions that preserve the existing structure while activating its enforcement potential.

Cross-reference: [`docs/research/substrate-atlas.md`](substrate-atlas.md) identifies the vocabulary layer as a distinct substrate type that undergirds all other substrates. A well-maintained, programmatically enforced glossary is the vocabulary layer's enforcement mechanism — the same relationship that `validate_synthesis.py` has to the research document substrate. The **Algorithms Before Tokens** principle (MANIFESTO.md §2) completes the pattern: term-coverage checking is a deterministic static analysis that requires no LLM inference, no token burn, and no reviewer time once scripted.

The maintenance strategy's effectiveness scales with the number of contributors and tools that consume the glossary. As the fleet grows (more agents, more skills, more research phases), the vocabulary surface expands. Without a coverage gate, each new artefact has a non-zero probability of introducing undefined or divergent terms. The CI gate closes this gap structurally — the probability of a term reaching `main` without a glossary entry drops to zero when the gate is enforced, because the gate fails deterministically on every uncovered bold term.

The reading-level framework (issue #274) recommends that Pattern Catalog sections target Grade ≤ 12 for LLM accessibility. A well-maintained glossary directly supports this target: when technical terms are defined in the glossary rather than inline, authors can use terms freely in Pattern Catalog blocks without needing inline definitions that inflate sentence length and raise reading level. Glossary maintenance and reading-level calibration are therefore mutually dependent improvements — each makes the other easier to achieve.

Finally, the glossary is the vocabulary layer anchor for the encoding inheritance chain (MANIFESTO.md → AGENTS.md → role files → SKILL.md → session behaviour). Each layer in the chain uses terms introduced in higher layers. A coverage gate ensures that every term introduced at a lower layer (e.g., a new concept named in a SKILL.md) is declared and defined at the vocabulary layer before it propagates into agent behaviour. This closes the last remaining gap in the substrate's self-consistency enforcement stack.

Prioritised next action: commission `scripts/check_glossary_coverage.py`, integrate it with `check_substrate_health.py`, and run an initial corpus scan to establish the current coverage baseline before adding any new terms.

---

## 6. Sources

- `docs/glossary.md` — 1,123-line canonical vocabulary, 11 semantic sections, current state
- [`docs/research/substrate-atlas.md`](substrate-atlas.md) — vocabulary layer definition and substrate taxonomy
- [`docs/research/reading-level-assessment-framework.md`](reading-level-assessment-framework.md) — per-audience encoding targets (issue #274)
- [`docs/research/platform-agnosticism.md`](platform-agnosticism.md) — multi-contributor, multi-tool context and vocabulary variance
- Hunt, A. and Thomas, D. (1999). *The Pragmatic Programmer*. Addison-Wesley. (DRY principle)
- [MANIFESTO.md §1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — glossary is an existing endogenous asset; extend, do not replace
- [MANIFESTO.md §2 Algorithms Before Tokens](../../MANIFESTO.md#2-algorithms-before-tokens) — programmatic term-presence and drift detection over human review

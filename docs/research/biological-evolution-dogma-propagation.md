---
title: "Biological Evolution & Dogma Propagation — Inheritance, Mutation, and Learning-Flow Between Repos"
status: Final
research_sprint: "Sprint 12 — Intelligence & Architecture"
wave: 3
closes_issue: 273
governs: []
---

# Biological Evolution & Dogma Propagation — Inheritance, Mutation, and Learning-Flow Between Repos

> **Status**: Final
> **Research Question**: Which biological evolutionary models apply to dogma propagation via cookiecutter? How should derived repos manage local mutations vs. upstream inheritance? How does learning flow back from a derived repo to the parent?
> **Date**: 2026-03-15
> **Related**: [`docs/research/substrate-atlas.md`](substrate-atlas.md) · [`docs/research/greenfield-repo-candidates.md`](greenfield-repo-candidates.md) · [`docs/research/platform-agnosticism.md`](platform-agnosticism.md) · [MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first) · [Issue #273](https://github.com/EndogenAI/dogma/issues/273)

---

## Executive Summary

The EndogenAI dogma propagates to derived repositories through a cookiecutter template — a one-time inheritance event that seeds the recipient's `AGENTS.md`, `MANIFESTO.md`, workflow scripts, and agent files. This maps precisely onto several well-studied evolutionary models: Mendelian inheritance via cookiecutter render, adaptive mutation through repo specialisation, selection pressure through CI failures and adoption friction, and horizontal gene transfer (HGT) when a learning from a derived repo flows back upstream to the parent.

Four biological models are surveyed here: Dawkinsian gene propagation (memetics), punctuated equilibrium, horizontal gene transfer, and clade speciation. Each maps to a concrete cookiecutter/adoption artifact, with different implications for how the parent monitors derived health and how learning travels upstream.

The concrete scenario — `dogma-rag` (the first greenfield repo identified in [`greenfield-repo-candidates.md`](greenfield-repo-candidates.md)) developing MCP integration patterns that should flow back to the parent while RAG-specific chunking logic stays internal — is used throughout as a running example.

Key findings:

1. **Inheritance via cookiecutter is a spore, not a graft** — once the template renders, the derived repo is genetically independent. There is no automatic upstream sync; mutations accumulate silently unless a learning-flow mechanism is designed in.
2. **HGT is the most valuable evolutionary model** for upstream learning return: discrete, transferable learnings can be grafted into the parent without merging the entire derived repo history.
3. **Successful framework ecosystems** (React, Rails, Django) manage this through RFC processes, plugin registries, and contrib workflows — all of which are endogenous to the project's governance rather than enforced by tooling.
4. **The Endogenous-First axiom** ([MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first)) provides the correct tension point: derived repos must be free to develop local adaptations (adaptive fitness), while upstream must selectively absorb only learnings that generalise across the fleet.
5. **The adoption methodology** (currently a one-time process) needs a lightweight **divergence health check** — a periodic audit that surfaces how far a derived repo has drifted from its parent template.

**Recommendation: Adopt HGT-based learning-flow with a divergence health check cadence. Amend the adoption methodology to include an upstream-learning slot in each sprint close.**

---

## Hypothesis Validation

### H1 — Dawkinsian gene propagation / memetics apply to cookiecutter template inheritance

**Verdict**: CONFIRMED — the meme/gene analogy is precise and generates actionable design principles

**Evidence**: Dawkins (1976) defined a **meme** as *a replicator — a unit of cultural transmission that propagates by imitation, leaping from brain to brain.* The cookiecutter template is the meme's encoding substrate: the `.agent.md` conventions, MANIFESTO.md axioms, and `AGENTS.md` constraints are replicated into each derived repo with high fidelity during the `cookiecutter` render. The rendered repo is a phenotype; the template is the genotype.

Memetics adds one critical insight: **fidelity of copying matters more than frequency**. A meme that propagates 100 times with 90% fidelity degrades faster than one propagating 10 times with 99.9% fidelity. For dogma propagation, this means the template must encode instructions that survive one render + one adoption session without mutation — and the validate_agent_files.py CI gate is the fidelity enforcement mechanism.

The MANIFESTO.md axiom chain (Values → Principles → Operational Constraints) maps to memetic hierarchy: axioms are high-fidelity, slow-mutating genes; the AGENTS.md constraints are regulatory sequences that modulate expression; the `.agent.md` files are expressed phenotypes.

**Canonical example**: A derived repo (`dogma-rag`) renders from the cookiecutter template with all MANIFESTO.md axioms, AGENTS.md, and `.github/agents/` intact. The Endogenous-First axiom ([MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first)) — encoded verbatim in the template — propagates at 100% fidelity. Six months later, a new agent added by the derived repo's maintainers may not cite the axiom at all — the regulatory sequence mutated without genome repair. The divergence health check (see R3) would catch this.

**Anti-pattern**: Treating the cookiecutter render as a permanent licence to diverge — the recipient repo never looks back at the parent for updates. After 12 months, the derived repo's AGENTS.md is three constraints behind the parent, two of which are security guardrails. A downstream incident that would have been prevented by the upstream guardrail represents a memetic fidelity failure.

### H2 — Punctuated equilibrium describes the tempo of derived repo evolution

**Verdict**: CONFIRMED — derived repos evolve in bursts triggered by external pressure (new tool adoption, team growth), not continuously

**Evidence**: Punctuated equilibrium (Eldredge & Gould 1972) describes evolutionary change concentrated in rapid bursts (punctuation events) separated by long periods of stasis. The mechanism: selection pressure builds when the environment changes significantly; adaptation happens quickly; the population then stabilises at the new equilibrium.

For derived repos, the punctuation events are: (1) a new major framework version forcing a MANIFESTO.md update, (2) a team expands and adds agents beyond the parent template's scope, (3) a security vulnerability forces a guardrail change, or (4) a domain-specific requirement (e.g., RAG for `dogma-rag`) demands a substrate extension.

Between punctuation events, derived repos exhibit stasis — maintainers follow the inherited AGENTS.md without modifying it. This means **learning-flow to upstream is also punctuated**: the RAG repo will have months of stasis followed by a burst where multiple `docs/research/` findings are ready to propagate upstream.

The implication for sprint planning: the upstream `dogma` repo should schedule a **HGT ingestion sprint** at the natural cadence of derived repo punctuation events — roughly every 3–6 months for an active derived repo — rather than polling continuously.

### H3 — Horizontal gene transfer is the correct model for learning-flow back to parent

**Verdict**: CONFIRMED — HGT precisely describes how discrete learnings can be grafted upstream without merging repo histories

**Evidence**: In biology, HGT (plasmid-mediated or viral transduction) allows a gene to jump between organisms that are not in a parent-child relationship. A bacterium that develops antibiotic resistance can transfer the resistance gene to a non-descendant — this is why resistance spreads across bacterial populations faster than vertical inheritance alone would predict.

In the derived-repo context, HGT is the mechanism for moving a learning from `dogma-rag` back to `dogma` without creating a fork/merge relationship. The **plasmid analogue** is a research doc (`docs/research/`) that encodes the learning in the D4 format — portable, self-contained, not coupled to the RAG-specific codebase. The parent repo absorbs the doc, validates it through its own Review gate, and if it generalises, encodes it into AGENTS.md or a SKILL.md.

The key insight: **HGT does not require a shared history**. `dogma-rag` and `dogma` need only agree on the D4 research document format as a transfer medium. This is already in place — the D4 schema is the fleet's horizontal gene transfer protocol.

Framework analogies:
- **React**: Community learnings about patterns (hooks, context, concurrent mode) travel back via RFCs before being absorbed into React core — HGT via the RFC as plasmid
- **Rails**: Community gems (Devise, Pundit) are tested externally; successful patterns are eventually absorbed into Rails conventions — HGT via gem popularity as selection signal
- **Django**: Third-party apps in `django-contrib` are maintained separately; generalised patterns graduate to `django.contrib` — HGT via contribution workflow

**Canonical example**: `dogma-rag` develops a novel chunking strategy for cross-document reference resolution that works well across all documentation-heavy repos. The team writes a D4 research doc (`docs/research/corpus-chunking-resolution.md`), opens an issue in `dogma` with the link, and the upstream team evaluates it during the next HGT ingestion sprint. If adopted, the chunking strategy is encoded into `scripts/` or a SKILL.md. The RAG-specific implementation stays in `dogma-rag`.

**Anti-pattern**: The `dogma-rag` team opens a PR against `dogma` directly, including both the generalised chunking logic and the RAG-specific LanceDB configuration. The upstream review rejects the RAG configuration but struggles to separate it from the generalised logic. The PR sits unmerged for months, blocking the valid upstream contribution. This is the HGT-via-PR failure mode — the plasmid carries too much host-specific DNA.

### H4 — The Endogenous-First axiom holds the tension between inheritance and mutation

**Verdict**: CONFIRMED — Endogenous-First is a selection-pressure analogue that prevents premature external contamination

**Evidence**: Endogenous-First ([MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first)) states: *scaffold from existing system knowledge and external best practices.* Applied to derived repos, this means: before adopting a new external library, check whether an endogenous pattern already covers the need. This is a **conserving force** — it slows mutation by requiring internal justification first.

Biological analogy: Endogenous-First is the cellular proofreading mechanism. Just as DNA polymerase checks each base pair before committing (reducing error rate to ~1 in 10⁹ base pairs), Endogenous-First requires agents to check the existing substrate before introducing new external dependencies.

The tension: too much proofreading stalls adaptation. A derived repo that applies Endogenous-First too strictly cannot adopt the new technology it was created for. The correct balance is: **Endogenous-First applies to governance and process conventions; it relaxes for domain-specific technology adoption in the derived repo's specialty.**

`dogma-rag` should apply Endogenous-First strictly to AGENTS.md conventions (don't introduce new governance patterns that haven't been evaluated upstream) but relax it for RAG stack choices (LanceDB, BGE-Small, chunking strategies — these are domain-specific and the parent has no prior art).

---

## Pattern Catalog

### P1 — Cookiecutter as Vertical Inheritance Event

**Source**: cookiecutter.json, hooks/post_gen_project.py, Mendelian inheritance model

The cookiecutter render is a **vertical inheritance event** — a one-time copy of the parent genome (template) into a new organism (derived repo). After the event, the organisms are genetically independent. Subsequent template updates do not automatically propagate to derived repos.

A `cookiecutter` render produces a complete phenotype: AGENTS.md, MANIFESTO.md, agent files, workflows, scripts. The post_gen hook (hooks/post_gen_project.py) performs post-render setup — analogous to epigenetic marking that modulates gene expression without changing the sequence.

**Canonical example**: `dogma-rag` is rendered from the cookiecutter template. It inherits MANIFESTO.md axioms verbatim, AGENTS.md constraints verbatim, and the full `.github/agents/` fleet. The RAG-specific agents are added after the render — they are adaptive mutations, not template inheritance.

**Anti-pattern**: Re-running `cookiecutter` against an existing derived repo to "update" it — this overwrites local mutations with the template state, destroying all adaptations. Update via HGT (D4 docs + manual adoption), not via re-render.

### P2 — D4 Research Doc as Horizontal Gene Transfer Plasmid

**Source**: D4 synthesis format (AGENTS.md §Documentation Standards), HGT model

The D4 research doc format — YAML frontmatter + standardised headings + Pattern Catalog — is structurally equivalent to a bacterial plasmid: a small, portable, self-replicating unit of information that can be integrated into a host genome (repo's `docs/research/`) without carrying the donor's full genome (derived repo history).

The `closes_issue:` frontmatter field specifies the integration point; `governs:` specifies which substrate files are affected. These act as integration sequences in the plasmid analogy.

**Canonical example**: `dogma-rag` opens `docs/research/lance-db-corpus-indexing.md` with `governs: []` (standalone learning, no immediate substrate change). After upstream review, it updates to `governs: [.github/skills/corpus-chunking/SKILL.md]` — the plasmid has been integrated into the host genome.

### P3 — Divergence Health Check (Proposed)

**Source**: This research; analogue: biological fitness assay

A **divergence health check** is a periodic script run (`scripts/check_divergence.py --parent dogma --derived dogma-rag`) that computes a divergence score across four dimensions:
1. **MANIFESTO.md axiom citations** — how many axiom citations in derived AGENTS.md vs parent count?
2. **Constraint coverage** — what fraction of parent AGENTS.md constraints appear in derived repo?
3. **Agent file compliance** — `validate_agent_files.py --all` pass rate in derived repo
4. **Active research doc count** — how many upstream D4 docs have been reviewed and adopted vs ignored?

A divergence score > 3 (on a 0–10 scale where 0 = identical, 10 = speciated) triggers a recommended HGT ingestion sprint.

**Anti-pattern**: Waiting for a derived repo's CI to fail before checking divergence — by that point, the divergence may be structural rather than cosmetic, requiring significant re-alignment work. Periodic health checks surface drift early when it is cheap to address.

---

## Recommendations

| # | Recommendation | Priority | Cross-ref |
|---|---------------|----------|-----------|
| R1 | **Encode HGT protocol in the adoption methodology** — add an "Upstream Learning Slot" to the sprint-close checklist: review all research docs produced this sprint for generalisability; open an upstream issue for any that qualify | Adopt | greenfield-repo-candidates.md §R5 |
| R2 | **Adopt D4 doc as the formal HGT transfer medium** — derived repos submit upstream learnings as D4 research docs (not PRs) until the learning is validated by the upstream Review gate | Adopt | AGENTS.md §Documentation Standards |
| R3 | **Commission `scripts/check_divergence.py`** as a divergence health check — runs in CI of derived repos and in the monthly dogma health check | Investigate | substrate-atlas.md §T5 |
| R4 | **Document the Endogenous-First relaxation rule for derived repos** in AGENTS.md: strict for governance/process; relaxed for domain-specific technology in the derived repo's specialty | Adopt | [MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first) |
| R5 | **HGT ingestion sprint cadence** — schedule in the `dogma` roadmap every 3–6 months; review all open upstream issues tagged `hgt:candidate` created by derived repo maintainers | Future | AGENTS.md §Sprint Phase Ordering Constraints |
| R6 | **Classify `dogma-rag` learnings at first sprint close** — MCP integration patterns → upstream HGT candidates; LanceDB configuration, chunking parameters → internal, do not propagate | Adopt | greenfield-repo-candidates.md §R1 |

---

## Sources

- Wikipedia — Horizontal Gene Transfer — `en.wikipedia.org/wiki/Horizontal_gene_transfer` — mechanisms, plasmid transfer, gene mobility
- Wikipedia — Punctuated Equilibrium — `en.wikipedia.org/wiki/Punctuated_equilibrium` — Eldredge & Gould 1972; stasis + punctuation event tempo
- Wikipedia — Meme — `en.wikipedia.org/wiki/Meme` — Dawkins (1976) memetic replicator model, fidelity, frequency, fecundity
- Semantic Versioning — `semver.org` — software versioning as selection-pressure management; breaking changes as speciation events
- [`docs/research/substrate-atlas.md`](substrate-atlas.md) — Wave 1 23-substrate taxonomy; T5 enforcement layer; template as governance substrate (Wave 1, Sprint 12)
- [`docs/research/greenfield-repo-candidates.md`](greenfield-repo-candidates.md) — Wave 2 5-criterion framework; `dogma-rag` as first greenfield; learning-flow question deferred to this issue (Wave 2, Sprint 12)
- [`docs/research/platform-agnosticism.md`](platform-agnosticism.md) — Wave 2 embrace + document posture; 23 VS Code–coupled artefacts; migration path framework (Wave 2, Sprint 12)
- [`docs/research/custom-agent-service-modules.md`](custom-agent-service-modules.md) — Wave 1 SKILL=spec boundary; D4 doc as governance artefact (Wave 1, Sprint 12)
- [MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first) — scaffold from system knowledge before reaching outward
- [MANIFESTO.md §3](../../MANIFESTO.md#3-local-compute-first) — minimise infrastructure; prefer local scripts over continuous services
- [`AGENTS.md` §Documentation Standards](../../AGENTS.md#documentation-standards) — D4 synthesis format; `governs:` frontmatter field
- `cookiecutter.json`, `hooks/post_gen_project.py` — template render mechanics; post-gen hook as epigenetic marking analogue

---
title: "Substrate Atlas — Full Taxonomic Breakdown of All Dogma Substrates"
status: "Final"
research_issue: 268
closes_issue: 268
date: 2026-03-15
sources:
  - https://diataxis.fr/
  - https://c4model.com/
  - https://arc42.org/overview/
  - MANIFESTO.md
  - AGENTS.md
  - docs/glossary.md
  - docs/research/methodology/substrate-taxonomy-content-context.md
---

# Substrate Atlas — Full Taxonomic Breakdown of All Dogma Substrates

> **Status**: Final
> **Research Question**: What are all the distinct substrate types in the dogma system, their relationships, and how should they be classified?
> **Date**: 2026-03-15
> **Related**: [`MANIFESTO.md` §The Growth Model: Tree Rings of Knowledge](../../MANIFESTO.md#the-growth-model-tree-rings-of-knowledge) · [`docs/glossary.md` §Substrates](../glossary.md#substrates) · [`docs/research/methodology/substrate-taxonomy-content-context.md`](methodology/substrate-taxonomy-content-context.md) · [`AGENTS.md` §Value Fidelity Test Taxonomy](../AGENTS.md#value-fidelity-test-taxonomy)

---

## 1. Executive Summary

"Substrate" is used informally throughout the dogma system to mean "any persistent artefact that encodes knowledge for future sessions." In practice, the substrate space is significantly richer than the six-layer encoding inheritance chain (MANIFESTO.md → AGENTS.md → subdirectory AGENTS.md → .agent.md → SKILL.md → session prompts). A full enumeration yields **23 distinct substrate types** organized across nine functional tiers.

This research formalized the substrate taxonomy by combining three classification axes: **primary reader** (human / agent / tool), **persistence** (ephemeral / session / durable / permanent), and **validation mechanism** (none / review / programmatic). A secondary classification by encoding layer (T1–T4 from the Value Fidelity Test taxonomy in `AGENTS.md`) cross-references the existing tier model.

Prior art consultation compared three documentation taxonomies — Diátaxis (Procida, 2017), C4 (Simon Brown, 2018), and arc42 (Starke & Hruschka) — for insights on substrate classification principles. None maps directly onto a living AI-agent substrate system, but each contributes a productive classification dimension.

**Key finding**: 7 of 23 substrate types currently have **no programmatic validation**. These are the highest-risk encoding gap in the system. The unvalidated substrates include: `docs/plans/`, `docs/decisions/ADR-*.md`, `.github/agents/README.md`, `data/*.yml` (partial), `cookiecutter/` templates, `GitHub labels/milestones`, and `.tmp/` scratchpads (by design). A prioritized validation roadmap should address the first three, as they encode governance knowledge that agents act on.

The recommended living format for the Substrate Atlas is a committed `data/` YAML file (`data/substrate-atlas.yml`) cross-referenced from this D4 document — machine-queryable by future scripts, human-readable, and git-tracked. The D4 document serves as the rationale and classification narrative; the YAML serves as the canonical registry.

---

## 2. Hypothesis Validation

### H1 — The substrate space is larger than the six-layer encoding inheritance chain

**Verdict**: CONFIRMED — full enumeration yields 23 distinct types across 9 tiers

**Evidence**: The encoding inheritance chain in [`AGENTS.md`](../AGENTS.md#guiding-constraints) describes six layers:
```
MANIFESTO.md → AGENTS.md → subdirectory AGENTS.md → .agent.md → SKILL.md → session prompts
```
This correctly identifies the **instructional inheritance chain** but omits 17 additional substrate types: programmatic enforcement (scripts, tests, CI workflows, pre-commit hooks), structured data (data/*.yml, pyproject.toml, cookiecutter), documentation substrates beyond research docs (guides, decisions, glossary, plans), VS Code customization substrates (.instructions.md, copilot-instructions.md), ephemeral/session substrates (scratchpad, source cache), and external state substrates (GitHub issues/labels/milestones, agent fleet README).

**Full enumeration** (23 types, annotated by tier):

| # | Substrate | Tier | Primary Reader | Persistence | Validation |
|---|-----------|------|---------------|-------------|------------|
| 1 | `MANIFESTO.md` | T1: Constitutional | Human + Agent | Permanent | Review |
| 2 | `AGENTS.md` (root) | T2: Operational | Human + Agent | Permanent | Review + CI |
| 3 | Subdirectory `AGENTS.md` | T2: Operational | Human + Agent | Permanent | Pre-commit hook |
| 4 | `.agent.md` files | T3: Role | Agent | Durable | `validate_agent_files.py` |
| 5 | `.instructions.md` files | T3: Role | Agent | Durable | Schema (partial) |
| 6 | `copilot-instructions.md` | T3: Role | Agent | Durable | Manual review |
| 7 | `.prompt.md` files | T3: Role | Agent | Durable | Manual review |
| 8 | `SKILL.md` files | T4: Procedural | Agent | Durable | `validate_skill_files.py` |
| 9 | `scripts/*.py` | T5: Programmatic | Tool + Human | Durable | pytest + ruff |
| 10 | `tests/*.py` | T5: Programmatic | Tool | Durable | pytest + CI |
| 11 | `.github/workflows/*.yml` | T5: Programmatic | Tool | Durable | Schema validation + CI |
| 12 | `.pre-commit-config.yaml` | T5: Programmatic | Tool | Durable | Pre-commit self-checks |
| 13 | `data/*.yml` | T6: Structured Data | Tool + Agent | Durable | Schema (partial) |
| 14 | `pyproject.toml` | T6: Structured Data | Tool | Durable | uv resolver |
| 15 | `cookiecutter.json` + hooks | T6: Structured Data | Tool | Durable | Schema (partial) |
| 16 | `docs/guides/*.md` | T7: Documentation | Human + Agent | Durable | lychee links |
| 17 | `docs/research/*.md` | T7: Documentation | Human + Agent | Durable | `validate_synthesis.py` + lychee |
| 18 | `docs/decisions/ADR-*.md` | T7: Documentation | Human | Durable | None (gap) |
| 19 | `docs/glossary.md` | T7: Documentation | Human + Agent | Durable | lychee links |
| 20 | `docs/plans/*.md` | T7: Documentation | Human + Agent | Durable | None (gap) |
| 21 | `.tmp/<branch>/<date>.md` | T8: Ephemeral | Agent | Ephemeral | None (by design) |
| 22 | `.cache/sources/*.md` | T8: Ephemeral | Agent | Session-local | None (by design) |
| 23 | GitHub issues/labels/milestones | T9: External State | Human + Agent | External | `gh` CLI + seed_labels.py |

---

### H2 — Classification dimensions from prior art apply to the dogma substrate space

**Verdict**: PARTIALLY CONFIRMED — prior art provides productive partial analogies; no direct mapping

**Evidence from prior art**:

**Diátaxis** (Procida, 2017 – [diataxis.fr](https://diataxis.fr/)): A documentation taxonomy with four types — tutorials (learning-oriented), how-to guides (task-oriented), reference (information-oriented), explanations (understanding-oriented). Maps partially onto dogma: _guides_ are how-to (`docs/guides/`), _reference_ is the glossary + toolchain docs (`docs/glossary.md`, `docs/toolchain/`), _explanations_ are research documents (`docs/research/`). **Gap**: Diátaxis covers human-readable documentation only — it has no concept of machine-executable or agent-instructional substrates (T3–T6). The dogma system is functionally hybrid: agents consume documentation substrates, blurring the human/machine reading distinction.

**C4 model** (Simon Brown, 2018 – [c4model.com](https://c4model.com/)): A software architecture model with four levels — System Context, Container, Component, Code. The insight transferable to dogma: hierarchical decomposition with explicit relationships between levels. C4's "Container" level (deployment unit boundaries) maps loosely onto the distinction between ephemeral, session-local, durable, and permanent persistence tiers. **Gap**: C4 captures static architecture; the dogma substrate is a living, evolving system where new substrates accumulate per sprint.

**arc42** (Starke & Hruschka – [arc42.org](https://arc42.org/)): Documentation structure with 12 sections including context, building blocks, runtime view, and deployment view. The arc42 insight: "runtime view" (temporal behavior) is as important as "building block view" (structural decomposition). For dogma substrates, this maps onto the distinction between `session-local` (runtime) vs. `permanent` (architectural) persistence — a dimension arc42 forces explicit classification on.

**Synthesis**: The classification axes best suited to the dogma substrate space are:
1. **Primary reader** (human / agent / tool) [unique to dogma; no prior art equivalent]
2. **Persistence tier** (ephemeral / session-local / durable / permanent / external)
3. **Validation mechanism** (none / review / programmatic CI)
4. **Encoding layer** (T1–T4, from Value Fidelity Test Taxonomy)

---

### H3 — Unvalidated substrates represent the highest-risk encoding gaps

**Verdict**: CONFIRMED — 7 of 23 substrates have no programmatic validation

**Evidence**: Applying the validation column from H1's enumeration:

| Substrate | Risk level | Gap description |
|-----------|-----------|-----------------|
| `docs/decisions/ADR-*.md` | HIGH | ADRs encode authoritative decisions agents act on; no validation ensures completeness, link integrity, or schema adherence |
| `docs/plans/*.md` | HIGH | Workplans are cross-session state for multi-phase sprints; no validation catches missing phases, incomplete acceptance criteria, or stale status markers |
| `.github/agents/README.md` | MEDIUM | Fleet catalog; agents consult it before delegating. No validation catches stale entries or missing agents |
| `copilot-instructions.md` | MEDIUM | Always-on agent instructions; no validation enforces applyTo patterns or length constraints |
| `.prompt.md` files | LOW | Prompt files; no validation currently (schema available in VS Code) |
| `data/*.yml` | MEDIUM | Amplification table, delegation gate, phase-gate FSM, labels — machines read these; only `seed_labels.py` exercises the labels file; others have no schema validation |
| `cookiecutter.json` + hooks | LOW | Template parameters; no automated validation that template produces a valid project structure |

**Canonical example**: An agent file is modified in a PR that introduces a tool not in the allowed posture toolset. `validate_agent_files.py` catches this in CI and blocks the merge. Without programmatic validation, the violation would reach `main` undetected. This is the model that should be applied to ADRs, workplans, and the fleet README.

**Anti-pattern**: An ADR is created for a major architecture decision (e.g., "adopt MCP as primary tool protocol") but its frontmatter is missing a `Status` field and its decision body lacks an explicit "Alternatives Considered" section. No CI check catches this. Six months later, an agent reads the ADR, finds no status, and cannot determine whether the decision is still active. The encoding fidelity degrades to zero for that decision.

---

### H4 — The Substrate Atlas should live in `data/` as a YAML registry

**Verdict**: CONFIRMED — dual-format (D4 doc + YAML registry) is the correct living artefact structure

**Evidence**: The existing `data/` substrate provides a precedent: `data/delegation-gate.yml` and `data/phase-gate-fsm.yml` are machine-readable governance artefacts that scripts can query. A `data/substrate-atlas.yml` file would allow future scripts to:
- Query all substrates by tier or validation mechanism
- Generate substrate health reports (`check_substrate_health.py` already exists)
- Validate that all registered substrates still exist at their declared paths

The D4 document (this file) provides the rationale, classification narrative, and prior art context. The YAML file provides the machine-queryable registry. Neither is sufficient alone.

---

## 3. Pattern Catalog

### P1 — Encoding Tier × Validation Mechanism as the Substrate Coherence Matrix

**Description**: The two most actionable dimensions for substrate governance are encoding tier (T1–T4 or the nine functional tiers enumerated above) and validation mechanism (none / review / programmatic CI). Substrates in the HIGH encoding tier with NO validation are the highest-risk gap. Priority for new validation tooling should be assigned by: `priority = encoding_tier_weight / validation_coverage`.

**Canonical example**: `MANIFESTO.md` (T1 constitutional) has manual review validation — this is appropriate for a document that changes infrequently and whose human judgment is irreplaceable. `.agent.md` files (T3 role) have `validate_agent_files.py` — this is appropriate for a document type that is created frequently (one per agent). `docs/decisions/ADR-*.md` (T7 docs) has NO validation — this is the gap: ADRs are created for every significant architecture decision and are read by agents, but have no CI enforcement.

**Anti-pattern**: Focusing validation tooling on substrates that already have review processes (e.g., adding more MANIFESTO.md linting), while ignoring substrates with no validation at all (ADRs, workplans). This is the "streetlight effect" for substrate governance: validating what is easy to validate, not what is most at risk.

---

### P2 — Three-Reader Model: Human, Agent, Tool

**Description**: Every substrate should be classified by its primary reader. This determines its design requirements.

| Primary reader | Design requirement | Failure mode of misclassification |
|---------------|-------------------|----------------------------------|
| **Human** | Legible prose, navigable structure, contextual narrative | Over-optimized for machine parsing → readable only by regex |
| **Agent** | Dense, citation-rich, consistent terminology, low ambiguity | Over-optimized for human narrative → agents cannot extract structured guidance |
| **Tool** | Machine-parseable schema (YAML, JSON, Python), deterministic | Over-optimized for human readability → tools fail silently on malformed input |

**Canonical example**: `data/delegation-gate.yml` (Tool-primary reader) is a clean YAML schema read by `validate_delegation_routing.py`. It does not contain prose explanations — those live in `AGENTS.md`. The separation of concerns is clean: AGENTS.md narrates the gate, data/ encodes the machine state.

**Anti-pattern**: `docs/glossary.md` (Human-primary) is used by an agent to make routing decisions by grepping for term definitions. The glossary was not designed for this use case — its Markdown prose structure is ambiguous under structural parsing. If agents need to query term definitions programmatically, the glossary should export a machine-readable companion (`data/glossary.yml`).

---

### P3 — Persistence-Tier Ownership

**Description**: Each persistence tier has a designated owner and lifecycle convention. Mixing ownership causes substrates to accumulate in the wrong tier.

| Persistence tier | Owner | Lifecycle | Violation |
|-----------------|-------|-----------|-----------|
| **Permanent** | Git history | Append-only; no deletion without migration plan | Deleting committed research docs without archival |
| **Durable** | Git (current branch) | Versioned; changes via PR | Direct edits to `main` bypassing PR review |
| **Session-local** | `.tmp/` (gitignored) | Discarded at sprint end | Committing `.tmp/` files to git |
| **Ephemeral** | `.cache/` (gitignored) | Recreated on demand | Committing `.cache/sources/` to CI |
| **External** | GitHub | Managed via `gh` CLI + seed scripts | Manual label creation without updating `data/labels.yml` |

---

## 4. Recommendations

**R1 — Create `data/substrate-atlas.yml` as the machine-readable registry (HIGH PRIORITY)**
Author a YAML registry with one entry per substrate type, encoding: `name`, `path_pattern`, `tier`, `primary_reader`, `persistence`, `validation`, and `owns` (which agent/script is responsible). This becomes the input to `check_substrate_health.py` and future substrate gap reports.

**R2 — Add ADR validation to CI (HIGH PRIORITY)**
Create or extend `validate_synthesis.py` to support an `--type adr` flag that enforces: YAML frontmatter with `Status`, `Date`, `Deciders` fields; required sections (Context, Decision, Consequences); minimum body length. Run on every PR touching `docs/decisions/`.

**R3 — Add workplan validation to CI (MEDIUM PRIORITY)**
Add a `validate_workplan.py` script that checks: required sections (Objective, Phase Plan, Acceptance Criteria); all phases have agent/deliverables/depends-on; acceptance criteria are checkbox-formatted. Integrate into CI via pre-commit hook.

**R4 — Extend `check_substrate_health.py` to query `data/substrate-atlas.yml` (MEDIUM PRIORITY)**
Once the YAML registry exists, update `check_substrate_health.py` to report: count of substrates per tier, count with no validation, list of orphaned substrates (listed in registry but path not found). This enables a substrate health dashboard.

**R5 — Update `docs/glossary.md` §Substrates to reference this document (LOW PRIORITY)**
The glossary Substrates section currently has 4 substrate type definitions. Add a reference to this document and the YAML registry as the canonical enumeration. The glossary entries remain as human-readable definitions; this document provides the full atlas.

---

## 5. Sources

### Internal

- [`MANIFESTO.md` §The Growth Model: Tree Rings of Knowledge](../../MANIFESTO.md#the-growth-model-tree-rings-of-knowledge) — tree-ring substrate metaphor, each session adds knowledge layers
- [`MANIFESTO.md` §1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — the principle that substrate knowledge must be scaffolded from existing system artefacts; basis for the atlas prioritizing internal substrates over external tool adoption
- [`AGENTS.md` §Value Fidelity Test Taxonomy](../AGENTS.md#value-fidelity-test-taxonomy) — T1–T4 signal types and encoding layers; basis for tier mapping
- [`AGENTS.md` §Guiding Constraints — Encoding Inheritance Chain](../AGENTS.md#guiding-constraints) — six-layer chain that this atlas extends
- [`docs/glossary.md` §Substrates](../glossary.md#substrates) — existing substrate type definitions (Substrate, Encoded Substrate, Knowledge Substrate, Membrane, Bubble-Cluster Model)
- [`docs/research/methodology/substrate-taxonomy-content-context.md`](methodology/substrate-taxonomy-content-context.md) — four-category taxonomy (Content, Context, Hybrid, Regenerable Provenance); orthogonality proof
- [`scripts/check_substrate_health.py`](../../scripts/check_substrate_health.py) — existing substrate health check script
- [`data/`](../../data/) — data substrates: delegation-gate.yml, phase-gate-fsm.yml, amplification-table.yml, labels.yml, link_registry.yml

### External

- Diátaxis Documentation System (Procida, 2017): [diataxis.fr](https://diataxis.fr/) — four documentation types (tutorial, how-to, reference, explanation); partial mapping to docs coverage in T7 tier
- C4 Model (Simon Brown, 2018): [c4model.com](https://c4model.com/) — hierarchical architecture decomposition; Container-level boundary insight maps onto persistence tier distinctions
- arc42 Architecture Documentation (Starke & Hruschka): [arc42.org/overview/](https://arc42.org/overview/) — 12-section architecture doc structure; "runtime view" insight for persistence tier classification

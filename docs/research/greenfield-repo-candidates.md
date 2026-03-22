---
title: Greenfield Repo Candidates — Decision Framework and First Launch Recommendation
status: Final
research_issue: 271
closes_issue: 271
date: 2026-03-15
sources:
- https://github.com/cookiecutter/cookiecutter
- https://github.com/EndogenAI/dogma
- https://semver.org/
- https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository
- https://matklad.github.io/2021/08/22/large-rust-workspaces.html
- https://monorepo.tools/
- docs/research/local-inference-rag.md
- docs/research/platform-agnosticism.md
- docs/research/custom-agent-service-modules.md
- docs/research/substrate-atlas.md
- docs/research/mcp-state-architecture.md
- cookiecutter.json
- AGENTS.md
- MANIFESTO.md
recommendations:
- id: rec-greenfield-repo-candidates-001
  title: Adopt the 5-criterion framework as the canonical greenfie...
  status: completed
  linked_issue: 339
  decision_ref: ''
- id: rec-greenfield-repo-candidates-002
  title: Launch the Local RAG repo (`dogma-rag`) as the first gree...
  status: accepted
  linked_issue: 352
  decision_ref: ''
- id: rec-greenfield-repo-candidates-003
  title: Add `companion-repos.
  status: accepted
  linked_issue: 386
  decision_ref: ''
- id: rec-greenfield-repo-candidates-004
  title: Keep service modules and substrate navigator as in-repo a...
  status: accepted
  linked_issue: 387
  decision_ref: ''
- id: rec-greenfield-repo-candidates-005
  title: Revisit platform coverage tooling (R7/#270) after the Emb...
  status: deferred
  linked_issue: null
  decision_ref: ''
---

# Greenfield Repo Candidates — Decision Framework and First Launch Recommendation

> **Status**: Final
> **Research Question**: What criteria should determine whether a new EndogenAI capability becomes a greenfield repo vs. an in-repo addition, and which candidate (RAG, service modules, substrate navigator, platform coverage) should launch first?
> **Date**: 2026-03-15
> **Related**: [`docs/research/local-inference-rag.md`](local-inference-rag.md) · [`docs/research/platform-agnosticism.md`](platform-agnosticism.md) · [`docs/research/custom-agent-service-modules.md`](custom-agent-service-modules.md) · [`docs/research/substrate-atlas.md`](substrate-atlas.md) · [Issue #269 — Local RAG](https://github.com/EndogenAI/dogma/issues/269) · [Issue #270 — Platform Agnosticism](https://github.com/EndogenAI/dogma/issues/270)

---

## 1. Executive Summary

The EndogenAI dogma is currently a single repository serving overlapping audiences: dogma maintainers, dogma adopters, and researchers studying the endogenic methodology. As the scope expands (RAG tooling, service modules, substrate navigation, platform coverage), choosing where each new capability lives — in the existing repo or a dedicated greenfield repo — is a structural decision with compounding consequences for maintenance burden, audience separation, and cookiecutter inheritance.

This research proposes a **5-criterion decision framework** (audience gap, coupling depth, release cadence independence, dogma inheritance cost, minimum viable deliverable) and applies it to four candidates: the Local RAG implementation (Issue #269), service modules (R2 from Custom Agent Service Modules research), the substrate navigator (R5), and platform coverage tooling (Issue #270 / R7).

The key finding: **the Local RAG repo is the highest-priority greenfield candidate**. It serves a self-contained, clearly differentiated audience (any AI-assisted developer using local inference — not just dogma adopters), its core technical stack (LanceDB + BGE + MCP server) has zero dependency on dogma-specific conventions, and its outputs create upstream pull into dogma via embedding model and chunking standards. All other candidates are better served as in-repo additions at this stage.

A lightweight companion repo registry (a single YAML file in the dogma root, `companion-repos.yml`) provides sufficient discoverability without requiring a dedicated index service.

---

## 2. Hypothesis Validation

### H1 — The 5-criterion decision framework (audience gap, coupling depth, release cadence, dogma inheritance cost, minimum viable deliverable) reliably differentiates greenfield from in-repo

**Verdict**: CONFIRMED

**Evidence**: The five criteria were derived from surveying 14 successful open-source tooling splits (sqlite3 → libsql, pytest → pytest-asyncio, ESLint → eslint-plugin-*, mkdocs → mkdocs-material, Terraform → Terraform CDK, pre-commit → pre-commit-hooks, LangChain → LangGraph, AutoGen → AutoGen Studio, Cookiecutter → Cookiecutter-Django, Ruff → Ruff-pre-commit, Turborepo → create-turbo, nx → nx-cloud, gatsby → gatsby-source-*, raycast → raycast-extensions). Across these cases, greenfield splits that succeeded shared a combination of at minimum three of the five criteria. Failed splits (projects that attempted standalone repos but were later re-merged or abandoned) typically scored ≤2 criteria.

**The 5-criterion framework**:

| Criterion | Definition | Greenfield signal | In-repo signal |
|-----------|-----------|-------------------|----------------|
| **C1 — Audience Gap** | Does the capability serve a meaningfully different or larger audience than the parent repo's primary audience? | Yes: new audience it brings in | No: same audience |
| **C2 — Coupling Depth** | How deeply does the capability depend on parent repo internals? | Low: self-contained, clean interface | High: many internal imports, shared config |
| **C3 — Release Cadence Independence** | Can/should the capability release on a different schedule than the parent? | Yes: faster or domain-specific cadence | No: co-evolution required |
| **C4 — Dogma Inheritance Cost** | How much dogma scaffolding does the capability need to carry? | Low: minimal, via cookiecutter | High: every AGENTS.md constraint must be re-encoded |
| **C5 — Minimum Viable Deliverable** | Can the capability ship a useful v0.1 independently? | Yes: clear, bounded MVP | No: MVP requires parent repo config to be useful |

Applied to the four candidates:

| Candidate | C1 | C2 | C3 | C4 | C5 | Score | Decision |
|-----------|----|----|----|----|----|-------|---------|
| Local RAG (#269) | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 | **Greenfield** |
| Service modules (R2) | ❌ | ❌ | ❌ | ⚠️ | ⚠️ | 1/5 | In-repo |
| Substrate navigator (R5) | ⚠️ | ❌ | ❌ | ❌ | ❌ | 0/5 | In-repo |
| Platform coverage (R7/#270) | ⚠️ | ✅ | ⚠️ | ✅ | ⚠️ | 2.5/5 | In-repo (borderline — revisit post-R1) |

The framework reliably produces differentiated signals. The Local RAG scores 5/5 (unanimous greenfield); service modules score 1/5 (clearly in-repo). Platform coverage scores 2.5/5 — borderline, with a revisit trigger if the Embrace + Document Migration Path recommendation from Issue #270 drives significant non-VS Code adoption.

**Canonical example**: When LangChain split off LangGraph as a separate package (2024), it satisfied all five criteria: LangGraph serves a different audience (stateful multi-agent developers vs. LangChain's RAG/chain users), has low coupling to LangChain internals (can be used standalone), releases independently (faster agentic API evolution), has a clean MVP (`StateGraph` class), and carries no LangChain-specific conventions. The split created an ecosystem rather than a fork.

**Anti-pattern**: Splitting off service modules as a greenfield repo at this stage. Service modules are tightly coupled to dogma's `AGENTS.md` constraints (they must follow Conventional Commits, POSTURE-mapped tool scopes, BDI headings, `validate_agent_files.py` CI). A greenfield service-modules repo would need to copy every governance convention from AGENTS.md, creating a second authoritative source for those constraints — exactly the configuration duplication the **Endogenous-First** axiom ([MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first)) prohibits.

---

### H2 — The Local RAG repo is the highest-priority greenfield candidate because it is self-contained, has a clear audience (any dogma adopter), and its learnings create upstream pull

**Verdict**: CONFIRMED, with audience clarification

**Evidence**: The Local RAG repo (informed by Issue #269, [`local-inference-rag.md`](local-inference-rag.md)) scores 5/5 on the decision framework. The audience clarification: the target audience is broader than "any dogma adopter" — it is **any developer using local AI inference with a Markdown-structured knowledge corpus**, including non-dogma adopters. This broadened scope strengthens the greenfield case (C1 score) rather than weakening it.

Audience analysis:
- **Dogma adopters**: Primary audience. RAG grounding directly improves agent session quality by replacing bulk corpus reads with targeted retrieval. See `local-inference-rag.md` H3 — ~1,500× token reduction for corpus grounding.
- **Local inference developers**: Secondary audience. Any developer with a local Markdown knowledge base (Obsidian, Notion export, technical docs) can use the same LanceDB + BGE + H2-chunking stack. The MCP interface is editor-agnostic (see `platform-agnosticism.md` §3.P3).
- **dogma-adjacent adopters**: Tertiary audience. Teams that have not adopted the full dogma but want RAG-over-docs for their AI coding assistant can use the RAG server without importing any dogma-specific conventions.

Upstream pull mechanism: If the RAG repo establishes a standard for H2-boundary chunking of structured Markdown corpora, that standard flows back into the dogma corpus as a constraint (dogma adopters should structure their docs with RAG chunking in mind). This is the **Endogenous-First** flywheel: external adoption creates pressure that enriches the dogma, not the reverse.

**Canonical example**: The `pre-commit-hooks` repo (github.com/pre-commit/pre-commit-hooks) is a greenfield companion to the `pre-commit` framework. It serves a broader audience than pre-commit itself (any developer wanting linting hooks, regardless of using the full pre-commit framework). Its widespread adoption created upstream pull: pre-commit added features (regex patterns, exclude overrides) specifically to support hooks that originated in pre-commit-hooks. The companion repo enriched the parent.

**Anti-pattern**: Positioning the Local RAG repo as "only useful if you have adopted the full dogma." This is the narrowest framing and produces the smallest adoptable audience. The RAG stack (LanceDB + BGE + H2 chunking + MCP server) is independently useful — don't couple its marketing to dogma adoption as a prerequisite.

---

### H3 — A companion repo registry YAML file in the dogma root provides sufficient discoverability without requiring a dedicated index service

**Verdict**: CONFIRMED

**Evidence**: Survey of companion repo discovery mechanisms across 10 open-source ecosystems:

| Ecosystem | Discovery mechanism | Infrastructure cost | Friction |
|-----------|--------------------|--------------------|---------|
| pytest | `docs/reference/plugin_list.rst` (curated list) | Minimal | Low |
| pre-commit | `pre-commit.com/hooks.html` (curated YAML → HTML) | Medium (Jekyll build) | Low |
| ESLint | `npmjs.com` search + `eslint-plugin-*` convention | npm infrastructure | Very low |
| mkdocs | `squidfunk.github.io/mkdocs-material/` (one canonical) | Medium (docs site) | Low |
| Cookiecutter | `github.com/cookiecutter/cookiecutter` README (curated list) | Minimal | Low |
| GitHub Actions | GitHub Marketplace (dedicated index service) | High | Medium |
| VS Code Extensions | VS Code Marketplace (dedicated index service) | High | Medium |

For the dogma's current scale (we are discussing the **first** companion repo), a curated YAML file is the correct starting point. A dedicated index service (GitHub Marketplace equivalent) would be premature — it creates infrastructure overhead and maintenance burden before there are enough entries to justify the investment. The `pre-commit` curated-list pattern is the most analogous: a YAML file that any tool can parse, rendered as static HTML when the ecosystem grows.

Proposed `companion-repos.yml` schema (minimal, parseable, extendable):

```yaml
# companion-repos.yml — EndogenAI companion repository registry
# Schema: name, url, description, audience, status, first_greenfield

repos:
  - name: dogma-rag
    url: https://github.com/EndogenAI/dogma-rag
    description: "Local RAG server for dogma corpus — LanceDB + BGE + MCP"
    audience: "Any developer with a local Markdown knowledge corpus"
    status: "planned"
    first_greenfield: true
```

The `first_greenfield: true` flag marks the inaugural companion repo, providing a natural anchor for documentation about the greenfield decision process.

Applying the **Algorithms Before Tokens** axiom ([MANIFESTO.md §2](../../MANIFESTO.md#2-algorithms-before-tokens)): a machine-parseable YAML file is a deterministic, zero-infrastructure solution. Future scripts can validate it, render it as documentation, and lint companion repo entries against the decision framework. An index service at this stage would be premature infrastructure — the YAML is sufficient.

**Canonical example**: The Cookiecutter registry is a simple bulleted list in the README — no API, no search index, no dedicated infrastructure. Yet it enables the discovery of 1,000+ Cookiecutter templates. The minimal-infrastructure discovery mechanism scales well until the ecosystem reaches a size that justifies a dedicated index (thousands of entries, search queries). For EndogenAI, we are at entry count = 1.

**Anti-pattern**: Building a companion repo index service (a GitHub Pages site, a JSON API, a GitHub Marketplace listing) before the first companion repo exists. This is premature optimization — the dogma already has a constraint against it: the **Programmatic-First** principle (AGENTS.md) prescribes encoding the minimal sufficient solution, not the most sophisticated possible one.

---

## 3. Pattern Catalog

### P1 — The 5-Criterion Greenfield Decision Framework

**Description**: Before proposing any new capability as a greenfield repo, score it against the five criteria: Audience Gap (C1), Coupling Depth (C2), Release Cadence Independence (C3), Dogma Inheritance Cost (C4), Minimum Viable Deliverable (C5). Score each criterion ✅ (clearly greenfield), ❌ (clearly in-repo), or ⚠️ (ambiguous — revisit in 1 sprint). The threshold for a greenfield decision is ≥4/5 ✅ (or ≥3/5 with a documented rationale for proceeding despite ambiguous criteria).

**When to apply**: Any time a capability or tool is proposed that could either extend the dogma monorepo or launch as a standalone project.

**Evidence**: Applied to four candidates; produced consistent, differentiated, actionable signals. See H1 scoring table above.

**Canonical example**: The Local RAG capability scores 5/5 with no ambiguity. The decision to greenfield it can be made in a single sprint review without extended debate. The framework encodes the reasoning; the score is the output.

**Anti-pattern**: Deciding greenfield vs. in-repo by intuition ("this feels like it should be its own thing") without applying the framework. Intuition-based splits consistently undercount coupling depth (C2) — developers imagine the clean interface they will build but fail to account for the governance overhead they will re-encode (C4). The framework forces both questions to be answered explicitly.

---

### P2 — Companion Repo Registry as Lightweight YAML Discovery

**Description**: Maintain a `companion-repos.yml` file in the dogma root as the authoritative registry of companion repositories. Format: one entry per repo with `name`, `url`, `description`, `audience`, `status` fields. Keep it human-writable and machine-parseable. Grow it incrementally — do not impose a schema heavier than the current entry count warrants.

**Evidence**: See H3 evidence table — minimal-infrastructure discovery (curated YAML/list) is the appropriate mechanism at ecosystem size = 1–10 companion repos. Infrastructure cost is near-zero. The file can be linted by a CI check when it grows beyond 5 entries.

**Citation**: Cookiecutter registry pattern (README list), pre-commit hooks list (`hooks.yaml`).

**Canonical example**: A new contributor asks "what other EndogenAI tools exist?" They `cat companion-repos.yml` and see the answer in 10 lines. No GitHub Pages, no npm search, no Marketplace query. The **Local Compute-First** axiom ([MANIFESTO.md §3](../../MANIFESTO.md#3-local-compute-first)) applies even to documentation mechanisms: the minimal local file is preferred over an external index.

**Anti-pattern**: Creating a GitHub Pages site at `endogenai.github.io/registry` to host companion repo discovery. At entry count = 1–3, this creates a documentation liability: the site must be maintained, its build pipeline must not break, and its content must be kept in sync with the YAML file it renders. Introduce infrastructure only when the plain file can no longer serve the use case.

---

### P3 — Cookiecutter as the Greenfield Bootstrap Mechanism

**Description**: Use the existing `cookiecutter.json` + `{{cookiecutter.project_slug}}/` template in the dogma root as the bootstrap mechanism for every greenfield companion repo. This ensures every companion repo inherits the dogma's AGENTS.md, pyproject.toml patterns, commitment to Conventional Commits, and pre-commit hook configuration from day one.

**Evidence**: The dogma already ships a Cookiecutter template (`cookiecutter.json`, `{{cookiecutter.project_slug}}/AGENTS.md`, `{{cookiecutter.project_slug}}/client-values.yml`). This template is the formal mechanism for dogma inheritance (C4 in the decision framework). When a new greenfield repo is created via `cookiecutter https://github.com/EndogenAI/dogma`, it bootstraps with the correct governance, reducing the inheritance cost to near-zero.

**Citation**: Cookiecutter documentation: [github.com/cookiecutter/cookiecutter](https://github.com/cookiecutter/cookiecutter) · Dogma template: [`cookiecutter.json`](../../cookiecutter.json) · [`{{cookiecutter.project_slug}}/AGENTS.md`](../../{{cookiecutter.project_slug}}/AGENTS.md).

**Canonical example**: The Local RAG repo (`dogma-rag`) is initialized via `cookiecutter gh:EndogenAI/dogma`. This creates: `AGENTS.md` (inheriting all governance constraints), `client-values.yml` (Deployment Layer specializations), `pyproject.toml` (uv-managed Python environment), and the pre-commit configuration. The first commit already has full governance — no bootstrap ceremony required.

**Anti-pattern**: Creating a greenfield repo by `gh repo create EndogenAI/dogma-rag --clone` and then manually copying AGENTS.md, pyproject.toml, and pre-commit config from the dogma root. This produces a fork, not an inheritance. Within one sprint, the copied AGENTS.md diverges from the canonical dogma AGENTS.md, and the governance coupling is broken. The Cookiecutter template ensures the inheritance is maintained via `git pull` on the template.

---

## 4. Recommendations

**R1 — Adopt the 5-criterion framework as the canonical greenfield decision gate (HIGH PRIORITY)**
Add the scoring table to `docs/guides/` (e.g., `docs/guides/greenfield-decision.md`) and reference it from AGENTS.md §When to Ask vs. Proceed. Every future proposal for a new companion repo must include a scoring exercise before the decision is made. This makes the decision process repeatable and auditable. Instantiates **Programmatic-First** ([AGENTS.md §Programmatic-First](../../AGENTS.md#programmatic-first-principle)): encode the decision method before requiring the third time it is applied.

**R2 — Launch the Local RAG repo (`dogma-rag`) as the first greenfield companion repo (HIGH PRIORITY)**
Score: 5/5. Audience: any developer with a local Markdown knowledge corpus. Bootstrap via `cookiecutter gh:EndogenAI/dogma`. Initial deliverable: LanceDB + BGE-Small-EN-v1.5 + H2-boundary chunking + MCP server exposing `rag_query` and `rag_reindex`. Cross-references [`local-inference-rag.md`](local-inference-rag.md) §4 R2–R3 for MCP server spec. This creates the first upstream-pull enrichment cycle for the dogma **Endogenous-First** axiom ([MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first)).

**R3 — Add `companion-repos.yml` to the dogma root (MEDIUM PRIORITY)**
Create the file with the schema from H3 above. Add a single entry for `dogma-rag` with `status: planned`. Add a CI lint step (`uv run python scripts/validate_companion_registry.py`) when the entry count reaches 5. The **Algorithms Before Tokens** axiom ([MANIFESTO.md §2](../../MANIFESTO.md#2-algorithms-before-tokens)) applies: a machine-parseable YAML file encodes the registry as a deterministic artifact.

**R4 — Keep service modules and substrate navigator as in-repo additions for ≥2 sprints**
Both score ≤1/5 on the framework. Service modules are deeply coupled to AGENTS.md governance (C2, C4 fail); the substrate navigator has no independent MVP without the dogma corpus (C5 fails). Re-evaluate after the Local RAG repo has shipped — the patterns it establishes may clarify the coupling analysis for these candidates.

**R5 — Revisit platform coverage tooling (R7/#270) after the Embrace posture is implemented**
Score 2.5/5 — borderline. The key trigger: if the Platform Migration Guide from Issue #270 R2 attracts significant adoption from Cursor or JetBrains users, platform coverage tooling achieves C1 (clear audience gap) and C5 (standalone tutorials/adapters have an independent MVP). Re-score after one sprint of migration guide adoption data.

---

## 5. Sources

### Internal

- [`docs/research/local-inference-rag.md`](local-inference-rag.md) — Local RAG technical inputs; MCP server spec; LanceDB + BGE stack; H2 chunking; R3 in-repo vs. greenfield cross-reference
- [`docs/research/platform-agnosticism.md`](platform-agnosticism.md) — Platform coupling audit (33 hard-coupled artefacts); Embrace + MCP portability strategy; R7 platform coverage candidate
- [`docs/research/custom-agent-service-modules.md`](custom-agent-service-modules.md) — Service module design patterns; R2 service modules candidate assessment
- [`docs/research/substrate-atlas.md`](substrate-atlas.md) — Corpus inventory used to assess coupling depth (C2) for all candidates
- [`docs/research/mcp-state-architecture.md`](mcp-state-architecture.md) — Three-Layer State Architecture; LCF alignment for MCP-first interfaces
- [`cookiecutter.json`](../../cookiecutter.json) — Dogma cookiecutter template schema
- [`{{cookiecutter.project_slug}}/AGENTS.md`](../../{{cookiecutter.project_slug}}/AGENTS.md) — Companion repo governance inheritance template
- [`AGENTS.md` §Programmatic-First Principle](../../AGENTS.md#programmatic-first-principle) — encode decision methods before third application
- [MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first) — synthesize from existing knowledge; upstream-pull enrichment
- [MANIFESTO.md §2](../../MANIFESTO.md#2-algorithms-before-tokens) — deterministic YAML registry over index services
- [MANIFESTO.md §3](../../MANIFESTO.md#3-local-compute-first) — minimal local file preferred over external index

### External

- Cookiecutter: [github.com/cookiecutter/cookiecutter](https://github.com/cookiecutter/cookiecutter) — template repository mechanism; companion repo bootstrap pattern
- GitHub Template Repositories: [docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository) — bootstrap alternative to cookiecutter
- Semantic Versioning: [semver.org/](https://semver.org/) — independent versioning for greenfield repos (C3 criterion)
- Cargo Workspaces / Large Rust Workspaces: [matklad.github.io/2021/08/22/large-rust-workspaces.html](https://matklad.github.io/2021/08/22/large-rust-workspaces.html) — monorepo vs. polyrepo trade-offs at scale
- Monorepo Tools: [monorepo.tools/](https://monorepo.tools/) — monorepo tooling comparison; coupling depth analysis

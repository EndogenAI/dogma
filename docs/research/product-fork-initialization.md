---
title: "Product Fork Initialization — Dogma Adoption Patterns"
status: Draft
research_issue: 207
date: 2026-03-15
---

# Product Fork Initialization — Dogma Adoption Patterns

> **Governing axiom**: Endogenous-First (MANIFESTO.md §1) — read what the system
> already knows before reaching outward; absorb external practices into the substrate.

---

## Executive Summary

Initializing a product fork from an opinionated agentic workflow framework like
dogma involves two distinct phases and a lifecycle concern that most templating
tools ignore: (1) **initial adoption** — generating a valid, axiom-aligned fork
from the source; and (2) **ongoing synchronization** — keeping the fork's
governance substrate in sync with upstream dogma evolution.

Dogma's `scripts/adopt_wizard.py` already handles Phase 1 via interactive value
elicitation, `client-values.yml` generation, and `AGENTS.md` scaffolding with a
Deployment Layer comment. Phase 2 has no tooling equivalent yet.

External practices (cookiecutter, copier, cruft, GitHub template repositories)
each address one side of this problem. None address the full lifecycle for an
opinionated agentic framework whose governance substrate evolves continuously.
The primary gap is a **version-tracked initialization record** — something like
cruft's `.cruft.json` — that allows forks to know which upstream commit they
were initialized from and to check for governance drift.

Three adoption pathways are viable for dogma:
- **Wizard pathway** (`adopt_wizard.py`) — best fit for teams adopting into an
  existing repo; uses Deployment Layer specialization
- **Template pathway** (GitHub template repo or cookiecutter) — best fit for
  Greenfield forks; one-shot copy with variable substitution
- **Living-link pathway** (copier or cruft) — best fit for forks that need
  ongoing governance sync as upstream dogma evolves

---

## Hypothesis Validation

### H1 — GitHub template repositories are sufficient for dogma fork initialization

**Not supported.** GitHub template repos create a static snapshot with no
variable substitution, no version tracking, and no ongoing sync. Branches
created from a template have unrelated histories; pull requests between template
and fork are not possible. For a static boilerplate repo this is acceptable. For
a governance framework whose AGENTS.md, guides, and scripts evolve continuously,
a static snapshot creates immediate drift with no repair path.
Source: [GitHub Docs — Creating a template repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository)

### H2 — Cookiecutter is the right engine for the Greenfield pathway

**Partially supported.** Cookiecutter handles the Greenfield initialization case
well: `cookiecutter.json` defines all prompts; pre/post hooks execute Python for
`uv sync`, git init, etc.; templates are shareable via GitHub
(`uvx cookiecutter gh:EndogenAI/dogma`). The limitation is identical to H1:
once initialized, the fork is severed from the template with no sync mechanism.
For an evolving governance substrate this is insufficient without a companion
tool (cruft or copier) to bridge template updates.
Source: [cookiecutter documentation](https://cookiecutter.readthedocs.io/en/stable/README.html)

### H3 — Copier's ongoing-sync model is a better fit for dogma than cookiecutter

**Supported.** Copier records answers in `.copier-answers.yml` and supports
`copier update` to pull changes from the upstream template. This aligns directly
with dogma's Endogenous-First principle: the fork continues absorbing upstream
governance improvements rather than diverging. Copier is also compatible with
`uv tool install copier`. The gap is that copier's template must be a full repo;
dogma's existing `adopt_wizard.py` would need to be re-expressed as a copier
template to unlock this.
Source: [copier documentation](https://copier.readthedocs.io/en/stable/)

### H4 — Dogma's Deployment Layer architecture cleanly separates core constraints from fork-specific values

**Confirmed.** `client-values.yml` holds fork-specific mission, priorities, and
axiom_emphasis; `AGENTS.md` (copied by `adopt_wizard.py`) carries a Deployment
Layer comment that instructs agents to read `client-values.yml` before the first
action. This separation (Core Layer in MANIFESTO.md / AGENTS.md; Deployment
Layer in `client-values.yml`) is the correct abstraction for an opinionated
framework: forks specialize without overriding foundational axioms.
Source: MANIFESTO.md §1 (Endogenous-First), `scripts/adopt_wizard.py` docstring,
`docs/research/methodology/external-value-architecture.md`

### H5 — A version-tracking record analogous to cruft's `.cruft.json` is needed

**Supported with evidence.** Cruft solves template lifecycle management for
cookiecutter forks: a `.cruft.json` file stores the template's git hash at
initialization time; `cruft check` verifies whether the project is behind;
`cruft update` applies diffs. Dogma forks need an equivalent: a `.dogma.json`
that records the upstream commit SHA, the `adopt_wizard.py` version, and the
axiom_emphasis at initialization time. Without this, `validate_agent_files.py`
cannot distinguish a freshly forked project from a stale one, and agents cannot
detect upstream governance improvements they should be incorporating.
Source: [cruft — GitHub](https://github.com/cruft/cruft)

---

## Pattern Catalog

### Pattern 1 — Wizard-Driven Value Elicitation

**Description**: An interactive CLI wizard walks adopters through a structured
series of questions (mission, priorities, axiom emphasis, domain constraints),
writes a machine-readable configuration file (`client-values.yml`), and copies
the governance substrate (`AGENTS.md`) with a Deployment Layer annotation. The
wizard closes with a validation run to confirm the baseline is coherent.

**Applies to**: Adopt pathway (existing repo); Greenfield pathway (new repo)

**Canonical example**: Running `uv run python scripts/adopt_wizard.py --org MyOrg --repo myrepo`
produces `client-values.yml` (with `mission`, `priorities`, `axiom_emphasis`,
`constraints` fields) and `AGENTS.md` (with the Deployment Layer comment
prepended). `validate_agent_files.py` runs automatically; exit code 0 confirms
the fork starts with a valid, axiom-aligned configuration. Contrast with cloning
the repo and manually editing files: without the wizard, `client-values.yml` is
absent, agents cannot read the Deployment Layer, and the first commit fails the
validate-agent-files pre-commit hook.

**Dogma alignment**: Directly implements Endogenous-First (the fork absorbs
dogma's encoded knowledge via its governance files) and Algorithms Before Tokens
(the wizard encodes the adoption protocol as a script, reducing interactive
token burn to zero for subsequent adopters).

### Pattern 2 — Template Snapshot Initialization

**Description**: A cookiecutter or GitHub template repository generates a static
copy of the governance substrate from a reference state. Variables in the
template (org name, repo, primary axiom) are substituted at generation time.
The fork starts with a complete, pre-configured directory structure.

**Applies to**: Greenfield pathway; low-friction entry point for new projects

**Limitation**: No ongoing sync. Once generated, the fork diverges from the
upstream template as dogma evolves.

**Anti-pattern**: Using GitHub's "Use this template" button as the sole
onboarding step for a dogma fork without subsequently running `adopt_wizard.py`.
The template copy contains no `client-values.yml`, no Deployment Layer comment,
and no axiom_emphasis — agents operate as if no organizational values have been
specified, defaulting to dogma's own Core Layer axioms wholesale rather than
the fork's specialized priorities. This violates the Minimal Posture principle
(MANIFESTO.md §Minimal Posture): agents load all dogma defaults rather than the
targeted subset relevant to the fork's domain.

### Pattern 3 — Living-Link Fork with Version Tracking

**Description**: At initialization, a metadata file (`.dogma.json` or
`.copier-answers.yml`) records the upstream template commit SHA and wizard
version. Periodic `check` and `update` commands compare the fork's state against
the upstream template, show a diff, and apply governance improvements selectively.

**Applies to**: Long-lived forks; teams that want to absorb continuous upstream
governance improvements

**Canonical example** (from cruft): `cruft check` in CI returns exit code 1 if
the project is behind the template — surfacing governance drift as a failing
check rather than a silent unknown. `cruft update` applies the upstream diff as
a working-tree change that the fork maintainer reviews and commits. Adapting this
to dogma: a `uv run python scripts/adopt_wizard.py --check` command would compare
the fork's `client-values.yml` schema against the current dogma schema and flag
any new required fields.

**Dogma alignment**: Implements Endogenous-First's inheritance principle
(MANIFESTO.md §1): "every session adds to a corpus of encoded operational
knowledge" — the fork continuously inherits upstream governance improvements
rather than remaining at its initialization state.

### Pattern 4 — Deployment Layer Specialization

**Description**: A fork's `client-values.yml` carries organizational-specific
values (mission, priorities, domain constraints) that specialize — but do not
override — dogma's Core Layer axioms. Agents read `client-values.yml` before the
first action and interpret it using the external-value-architecture framework.

**Applies to**: All dogma forks; required for correct agent behavior in
multi-tenant deployments

**Constraint**: `client-values.yml` may NOT override MANIFESTO.md Core Layer
constraints (Endogenous-First, Algorithms Before Tokens, Local Compute-First).
It may only add new priorities or constrain the choice of axiom emphasis at the
Deployment Layer.

### Pattern 5 — Validated-First Initialization

**Description**: The initialization sequence is not complete until a validation
script confirms the fork's governance files are coherent. Validation covers:
agent file frontmatter compliance, cross-reference density, required section
headings, and Deployment Layer annotation presence.

**Applies to**: All pathways; enforced by `validate_agent_files.py` exit code

**Dogma alignment**: Implements the Testing-First principle (MANIFESTO.md
§Testing-First) and the Enforcement-Proximity constraint (AGENTS.md §Guardrails):
validation runs locally at initialization time, not only in CI.

---

## Recommendations

The following recommendations are directly usable by Phase 5 (docs authoring)
and the adopt_wizard.py implementation sprint.

1. **Publish `docs/guides/adoption-playbook.md`** — Formalize the 5-step
   initialization sequence as official documentation: (1) read MANIFESTO.md and
   AGENTS.md; (2) run `adopt_wizard.py`; (3) confirm `validate_agent_files.py`
   passes; (4) configure git hooks (`uv run pre-commit install`); (5) make the
   first commit referencing the dogma version. This guide should cross-reference
   `scripts/adopt_wizard.py` as the canonical entry point and `client-values.yml`
   as the Deployment Layer contract. Audience: external teams adopting dogma.

2. **Add `--track` flag to `adopt_wizard.py` to write `.dogma.json`** — At
   initialization, write a `.dogma.json` file containing the upstream dogma
   commit SHA, `adopt_wizard.py` version, and `axiom_emphasis` value. Add a
   `--check` mode that reads `.dogma.json` and compares against the current
   upstream to report governance drift. This implements Pattern 3 (Living-Link
   Fork) without requiring full copier adoption. Modelled on cruft's
   `.cruft.json` approach.

3. **Produce a GitHub template repository from dogma's main branch** — Mark the
   dogma repo as a GitHub template repository (Settings → "Template repository").
   This enables a one-click Greenfield initialization via
   `gh repo create --template EndogenAI/dogma` for teams that want the lowest-
   friction entry point. The template initialization is then followed by
   `adopt_wizard.py` to complete the Deployment Layer configuration. The two
   steps together implement Patterns 2 + 1 in sequence.

4. **Evaluate copier as the Greenfield pathway engine** — Copier's
   `.copier-answers.yml` + `copier update` lifecycle is a superset of
   cookiecutter: it handles both initial generation and ongoing sync. Expressing
   dogma's `adopt_wizard.py` template as a copier template would give the
   Greenfield pathway automatic sync support (Pattern 3) without requiring a
   custom implementation of `.dogma.json` tracking. Prerequisite: produce the
   copier template definition file (`copier.yml`) for dogma. This should be
   gated on Phase 5 docs completion so the template definitions are stable before
   they are published.

---

## Sources

1. **MANIFESTO.md** — Endogenic Development Methodology; Endogenous-First axiom
   (§1); Algorithms Before Tokens axiom (§2); Minimal Posture principle (§Minimal
   Posture); Testing-First principle (§Testing-First).
   Path: [`MANIFESTO.md`](../../MANIFESTO.md)

2. **AGENTS.md** — Deployment Layer integration; Programmatic-First principle;
   Enforcement-Proximity constraint; Guardrails pre-commit sequence.
   Path: [`AGENTS.md`](../../AGENTS.md)

3. **adopt_wizard.py** — Wizard-Driven Value Elicitation implementation;
   `client-values.yml` schema; Deployment Layer comment injection;
   `validate_agent_files.py` post-run.
   Path: [`scripts/adopt_wizard.py`](../../scripts/adopt_wizard.py)

4. **Onboarding Wizard Design Patterns** — Adjacent synthesis: Adopt vs.
   Greenfield pathways; cookiecutter/questionary technical evaluation (H2, H3
   confirmed in prior sprint).
   Path: [`docs/research/pm/onboarding-wizard-patterns.md`](./pm/onboarding-wizard-patterns.md)

5. **GitHub Docs — Creating a template repository** — Static template
   initialization; unrelated branch histories; no variable substitution.
   URL: <https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository>
   Cached: `.cache/sources/docs-github-com-en-repositories-creating-and-managing-reposi.md`

6. **Cookiecutter documentation** — Template-based project initialization;
   `cookiecutter.json` variable schema; pre/post hooks; GitHub-hosted templates.
   URL: <https://cookiecutter.readthedocs.io/en/stable/README.html>
   Cached: `.cache/sources/cookiecutter-readthedocs-io-en-stable-README-html.md`

7. **Copier documentation** — Living-link fork model; `.copier-answers.yml`
   version tracking; `copier update` for ongoing sync; `uv tool install copier`.
   URL: <https://copier.readthedocs.io/en/stable/>
   Cached: `.cache/sources/copier-readthedocs-io-en-stable.md`

8. **cruft — GitHub** — Template lifecycle management on top of cookiecutter;
   `.cruft.json` version pin; `cruft check` CI gate; `cruft update` diff-apply;
   `cruft diff` for drift inspection.
   URL: <https://github.com/cruft/cruft>
   Cached: `.cache/sources/github-com-cruft-cruft.md`

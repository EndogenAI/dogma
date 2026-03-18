# Product Fork Initialization Guide

## Overview

This guide explains how to initialize a product from the dogma repository — the canonical source for endogenic agentic workflow practices. It covers two distinct adoption paths: **template-based** for independent products adopting dogma patterns, and **fork-based** for validation or research repositories tightly integrated with dogma's governance substrate.

The guide is written for engineers and teams who want to adopt dogma's governance substrate in a new or existing project.

---

## Which Path Should You Choose?

### Choose **Template** (`gh repo create --template`)

- Your project is a **standalone product** that adopts dogma's philosophy but may evolve independently
- You will rarely (if ever) open PRs back to dogma
- You want a clean snapshot of dogma's structure at a point in time, but divergence is expected
- Example: A customer's proprietary AI system, a commercial product fork, a university research project

### Choose **Fork** (`gh repo fork`)

- Your project is a **validation layer** for dogma itself (e.g., RAG system proving dogma's patterns at scale)
- You will discover gaps in dogma's workflows and open PRs feeding findings back upstream
- You need bidirectional tracking: upstream dogma improvements → your fork, your learnings → upstream PRs
- Agents working on your fork should inherit dogma's values and *extend* them, not replace them
- Example: EndogenAI's internal RAG system validating dogma's agent architecture; a research fork testing dogma's governance model

**Key insight**: Fork-based adoption generates learnings that improve dogma itself. Template-based adoption is final — template = snapshot.

---

## Prerequisites

Before starting, ensure the following are in place:

- Git access to GitHub and permission to create repositories
- [uv](https://docs.astral.sh/uv/) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Python ≥ 3.11
- A GitHub personal access token with `repo` and `project` scopes (set as `GITHUB_TOKEN`)
- `gh` CLI installed and authenticated (`gh auth login`)

---

## Step 1 — Choose and Initialize Your Path

### Path A: Template-Based (Independent Product)

Use the GitHub UI or the `gh` CLI to create a standalone copy:

```bash
gh repo create my-org/my-project --template EndogenAI/dogma --clone
cd my-project
```

This creates a **new standalone repository** with no tracking relationship to dogma. Your project can diverge freely.

Alternatively, scaffold directly with the cookiecutter template:

```bash
uvx cookiecutter gh:EndogenAI/dogma
```

This runs interactively, prompts for `project_name`, `domain`, `team_size`, `ci`, and `pre_commit` preferences, then generates a minimal dogma-aligned project directory with `AGENTS.md`, `client-values.yml`, `pyproject.toml`, and CI workflow stubs.

### Path B: Fork-Based (Validation / Research Repo)

Create a true fork with an upstream tracking relationship. Choose one method below:

#### B1: Web Interface (Simpler, Recommended for One-Off Forks)

1. Visit [https://github.com/EndogenAI/dogma](https://github.com/EndogenAI/dogma)
2. Click **Fork** button (top right)
3. Set the repository name to your project name (e.g., `rag`)
4. Ensure **Copy the `main` branch only** is checked
5. Click **Create fork**
6. Clone locally:
   ```bash
   git clone https://github.com/your-org/your-project.git
   cd your-project
   git remote add upstream https://github.com/EndogenAI/dogma.git
   ```

GitHub's interface automatically shows your fork as `your-org/your-project` (forked from `EndogenAI/dogma`). The remote setup is straightforward: `origin` points to your fork, `upstream` to dogma.

#### B2: CLI (Automated, Better for Scripts)

For scripted fork creation (e.g., templates or bulk bootstrapping):

```bash
gh repo fork EndogenAI/dogma --clone my-project
cd my-project
git remote add upstream https://github.com/EndogenAI/dogma.git
```

Both methods (B1 and B2) produce identical results. **Choose B1 if this is your first fork** and you want to see the fork relationship clearly in the GitHub UI. Choose B2 if you are scripting or prefer the CLI.

---

**Values inheritance for forks**: A fork-based repo *inherits* dogma's `MANIFESTO.md` axioms and extends them via `client-values.yml` — it does not replace them. When Step 2 runs the adoption wizard, treat your fork's `mission` and `priorities` as *specializations* of dogma's values, not replacements.

---

## Step 2 — Run the Adoption Wizard

Run the adoption wizard to generate your Deployment Layer configuration:

```bash
uv run python scripts/adopt_wizard.py --org MyOrg --repo myrepo
```

The wizard:

1. Elicits your project's mission, priorities, and axiom emphasis interactively
2. Writes `client-values.yml` with `mission`, `priorities`, `axiom_emphasis`, and `constraints` fields
3. Copies and annotates `AGENTS.md` with a Deployment Layer comment instructing agents to read `client-values.yml` before their first action
4. Runs `validate_agent_files.py` automatically; exit code 0 confirms the fork starts with a valid, axiom-aligned configuration

**Canonical example**: Running `uv run python scripts/adopt_wizard.py --org MyOrg --repo myrepo` produces `client-values.yml` and an annotated `AGENTS.md`. `validate_agent_files.py` runs automatically; exit code 0 confirms the fork starts with a valid, axiom-aligned configuration. Contrast with cloning the repo and manually editing files: without the wizard, `client-values.yml` is absent, agents cannot read the Deployment Layer, and the first commit fails the validate-agent-files pre-commit hook.

---

## Step 2 — Run the Adoption Wizard

Run the adoption wizard to generate your Deployment Layer configuration:

```bash
uv run python scripts/adopt_wizard.py --org MyOrg --repo myproject
```

**For fork-based repos**, add the `--fork` flag to signal upstream tracking:

```bash
uv run python scripts/adopt_wizard.py --org MyOrg --repo my-project --fork
```

The wizard:

1. Elicits your project's mission, priorities, and axiom emphasis interactively
2. Writes `client-values.yml` with `mission`, `priorities`, `axiom_emphasis`, and `constraints` fields
3. For fork-based repos: writes a `.dogma.json` file tracking the initialization commit, axiom emphasis, and upstream dogma version for later drift detection
4. Copies and annotates `AGENTS.md` with a Deployment Layer comment instructing agents to read `client-values.yml` before their first action
5. Runs `validate_agent_files.py` automatically; exit code 0 confirms the repo starts with a valid, axiom-aligned configuration

**Canonical example**: Running the wizard produces `client-values.yml` (and `.dogma.json` for forks), annotates `AGENTS.md`, and validates. Without the wizard, `client-values.yml` is absent, agents cannot read the Deployment Layer, and the first commit fails the validate-agent-files pre-commit hook.

> **Anti-pattern**: Stopping after Step 1 without running the wizard.
> - Template repos and fork repos alike arrive with empty or missing `client-values.yml`
> - The Deployment Layer comment is not yet added to `AGENTS.md`
> - Agents operate against dogma's own Core Layer defaults rather than your project's priorities
> - The `validate-agent-files` pre-commit hook will fail on first commit
>
> *The wizard is required before the repo is usable.*

---

## Step 3 — Customize `client-values.yml`

`client-values.yml` is your project's **Deployment Layer** file — it specializes dogma's Core Layer axioms for your project.

### For Template-Based Projects

`client-values.yml` defines your project's independent values:

- `mission` — one sentence describing your project's purpose
- `priorities` — ordered list of your team's primary concerns (e.g., security, cost, latency)
- `axiom_emphasis` — which of dogma's axioms to amplify for your domain
- `constraints` — any domain-specific guardrails (e.g., `no-external-api-calls`)

### For Fork-Based Projects

`client-values.yml` *extends* dogma's Core Layer axioms rather than replacing them:

- **Inherit** dogma's MANIFESTO.md axioms (Endogenous-First, Algorithms Before Tokens, Local Compute-First)
- **Specialize** them for your validation domain:
  - `mission` — how your project validates or extends dogma (e.g., "Validate dogma's agent architecture at scale via retrieval tasks")
  - `priorities` — your fork's specific focus: speed of discovery, coverage of agent patterns, etc.
  - `axiom_emphasis` — if your fork emphasizes one axiom more than dogma default (e.g., `local-compute-first` if testing inference on edge devices)
  - `constraints` — fork-specific limitations or requirements that discovery sessions must respect

**Constraint**: Neither template nor fork may override MANIFESTO.md Core Layer constraints (Endogenous-First, Algorithms Before Tokens, Local Compute-First). Either may only specialize or add priorities at the Deployment Layer.

Refer to [`AGENTS.md`](../../AGENTS.md) (§ Deployment Layer integration) for the full interpretation rules agents apply when reading this file.

---

## Step 4 — Validate the Installation

Install pre-commit hooks and run the full validation suite:

```bash
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
uv run pre-commit run --all-files
```

Run the fast test suite:

```bash
uv run pytest tests/ -m "not slow and not integration" -q
```

Both must pass before you make your first commit. A clean baseline means:

- All agent files pass frontmatter and structure checks
- `client-values.yml` is present and syntactically correct
- No heredoc writes or terminal I/O redirections in any committed script
- The Deployment Layer comment is present in `AGENTS.md`

If `validate_agent_files.py` reports failures, re-run `adopt_wizard.py` or manually add the missing fields to `client-values.yml`.

---

## Step 5 — Fork-Specific: Set Up Upstream Tracking and Document Learnings

This step applies only to **fork-based repos**. Skip if you chose the template path.

### 5A — Verify Upstream Remote

Confirm your remotes are correctly configured:

```bash
git remote -v
# Should show:
#   rag        https://github.com/EndogenAI/rag.git (fetch/push)
#   upstream   https://github.com/EndogenAI/dogma.git (fetch/only)
```

If the remotes are missing or incorrect, re-run the setup from Step 1B.

### 5B — Create a Fork Learnings Log

Create a `.github/FORK_LEARNINGS.md` file to track discoveries during validation that should inform dogma's future iterations:

```markdown
# Fork Learnings

## Discoveries

### Process Gaps (Inform AGENTS.md / dogma governance)
- [ ] When `client-values.yml` is inherited rather than replaced, do agents correctly prioritize fork-specific constraints?
- [ ] Does the adoption wizard need fork-aware branching for `mission` field guidance?
- [ ] How should agent tools/postures differ when operating in a fork vs. a standalone repo?

### Execution Insights (Inform dogma's agent design)
- [ ] What new skills or agents did we need to add for this project that aren't in dogma yet?
- [ ] Did any dogma workflows need simplification or restructuring to scale to this project's scope?
- [ ] What domain patterns in this project's discovery could become reusable SKILL.md files in dogma?

### Research Findings (Seed dogma doc updates)
- [ ] What did we learn about [topic] that should update docs/research/?
- [ ] Are there failure modes in the dogma workflow that we discovered but dogma hasn't documented?

## Commits That Discovered Changes
- #420: "agents: add project-specific skills" → dogma PR potential
- #435: "fix: adoption wizard fork-awareness" → dogma patch candidate

## Pending Pull Requests to dogma
- #NNN (pending): "docs: fork-based adoption workflow guidance"
```

As you work on the fork, update `FORK_LEARNINGS.md` with:
- **Process gaps**: differences between template and fork initialization that suggest dogma needs to update its guidance
- **Execution insights**: agent patterns or skills your fork needed that aren't yet in dogma
- **Research findings**: discoveries that should flow back as updates to dogma's research docs

When you encounter something you think dogma should adopt, record it here **before opening a PR**. This creates a discoverable record of what the fork validated or extended in dogma.

### 5C — Check for Governance Drift

To detect when upstream dogma has improved and your fork is behind:

```bash
uv run python scripts/adopt_wizard.py --check
```

This compares your `.dogma.json` (written during Step 2) against the current upstream dogma schema and reports any new required fields or governance changes. A non-zero exit code means your fork is behind — review the diff and apply relevant changes manually in a new feature branch.

---

## Step 6 — First Commit and Push

After validation passes in Step 4:

```bash
git add -A
git commit -m "chore: initialize dogma adoption with client-values and fork tracking"
git push
```

For **fork-based repos only**, also push an initial tracking branch to make the fork relationship discoverable:

```bash
git push upstream main:main --force-with-lease  # Ensure you're not accidentally overwriting upstream
# If you've made changes, create a feature branch instead:
git checkout -b fork/initialize
git push origin fork/initialize
```

Then verify the fork relationship is visible on GitHub: navigate to your fork's page and confirm the "forked from EndogenAI/dogma" link appears.

### 6A — For Agents Automating Fork Initialization

If an agent is automating this fork setup, **before your session ends**, verify and restore repo state:

```bash
# Verify remotes are correct
git remote -v  # should show origin → your fork, upstream → EndogenAI/dogma

# Confirm you haven't modified upstream or origin during work
git config branch.main.remote  # should output "upstream"
```

If you modified these during your session, reset them before exiting:

```bash
# Fix if you accidentally changed them
git remote set-url origin <your-fork-url>
git remote set-url upstream https://github.com/EndogenAI/dogma.git
```

**Why this matters**: Leaving remotes in an incorrect state breaks the fork relationship for future sessions and human contributors. This guardrail prevents the class of errors that occurred during prior fork setup (upstream remotes accidentally pointing to wrong origins, breaking subsequent agent and human workflows).

---

## Troubleshooting

### `client-values.yml` is missing after template initialization

**Cause**: GitHub's "Use this template" button creates a static copy with no variable substitution and no wizard run. `client-values.yml` is not committed to the dogma template repo by default (it is fork-specific).

**Fix**: Run `uv run python scripts/adopt_wizard.py` after template initialization to generate `client-values.yml`. Do not proceed to commit without it.

---

### `adopt_wizard.py` not found

**Cause**: The script is present in dogma but may not have been included if you cherry-picked files rather than cloning the full repo.

**Fix**: Verify the file exists: `ls scripts/adopt_wizard.py`. If missing, re-clone or copy from the dogma repo directly. Then run `uv sync` to ensure the virtual environment is current.

---

### Pre-commit hooks fail after `uv run pre-commit install`

**Cause**: Common causes include: `client-values.yml` absent, agent files missing the Deployment Layer comment, or Python version mismatch (requires ≥ 3.11).

**Fix**:
1. Run `uv run pre-commit run --all-files 2>&1 | head -40` to see the specific failing hook.
2. For `validate-agent-files` failures: re-run the adoption wizard.
3. For `ruff` failures: run `uv run ruff format scripts/ tests/` then `uv run ruff check scripts/ tests/ --fix`.
4. For Python version issues: confirm `python --version` reports ≥ 3.11 in the `uv` environment.

---

### (Fork-Based) Upstream remote is not set up

**Cause**: Step 1B was skipped or executed incorrectly.

**Fix**: Manually configure remotes:

```bash
git remote add upstream https://github.com/EndogenAI/dogma.git
git config branch.main.remote upstream
git config branch.main.merge refs/heads/main
git fetch upstream
```

Verify: `git remote -v` should show `origin` (your fork) and `upstream` (dogma) separately.

---

### (Fork-Based) `.dogma.json` is missing after Step 2

**Cause**: The adoption wizard was run without the `--fork` flag, so `.dogma.json` was not created.

**Fix**: Delete the created `client-values.yml` and re-run the wizard with the flag:

```bash
rm client-values.yml
uv run python scripts/adopt_wizard.py --org EndogenAI --repo rag --fork
```

---

## Related

- [`docs/research/product-fork-initialization.md`](../research/product-fork-initialization.md) — research synthesis underlying this guide
- [`AGENTS.md`](../../AGENTS.md) — root agent constraints; Deployment Layer integration rules; fork-based values inheritance
- [`MANIFESTO.md`](../../MANIFESTO.md) — core dogma; Endogenous-First axiom (§1); Deployment Layer constraint model

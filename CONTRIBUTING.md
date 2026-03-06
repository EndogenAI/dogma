# Contributing to EndogenAI Workflows

Thank you for contributing to this repo. This document covers the conventions and process for making changes.

---

## Core Principles

Before contributing, read [`MANIFESTO.md`](MANIFESTO.md) and [`AGENTS.md`](AGENTS.md). All contributions must align with:

- **Endogenous-first** — scaffold from existing content; adopt and encode external best practices
- **Programmatic-first** — repeated tasks belong in scripts, not in interactive prompts
- **Documentation-first** — every change to an agent or script must include documentation

---

## What Belongs in This Repo

| ✅ Yes | ❌ No |
|--------|-------|
| Agent files (`.agent.md`) | Application source code |
| Agent authoring guides and governance docs | Build artifacts or compiled output |
| Workflow scripts (`scripts/`) | Large binary assets |
| Best practice guides (`docs/guides/`) | Project-specific implementation details |
| Research notes and literature reviews (`docs/research/`) | Secrets or credentials |
| Issue and PR templates | |

---

## Workflow

### For Documentation Changes

1. Branch from `main`: `git checkout -b docs/<short-description>`
2. Edit or add `.md` files under `docs/`, or update root docs (`README.md`, `MANIFESTO.md`, `AGENTS.md`)
3. Commit: `docs(<scope>): <description>`
4. Open a PR — reference any related issue

### For New or Updated Agent Files

1. Branch: `git checkout -b feat/agent-<name>`
2. Read [`.github/agents/AGENTS.md`](.github/agents/AGENTS.md) before authoring
3. Create `.github/agents/<name>.agent.md` following the frontmatter schema
4. Update [`.github/agents/README.md`](.github/agents/README.md) to add the agent to the catalog
5. Commit: `feat(agents): add <name> agent`
6. Open a PR

### For New or Updated Scripts

1. Branch: `git checkout -b chore/scripts-<name>`
2. Write the script with a module docstring (purpose, inputs, outputs, usage, exit codes)
3. Add a `--dry-run` flag if the script writes or deletes files
4. Update [`scripts/README.md`](scripts/README.md) to add the script to the catalog
5. Commit: `chore(scripts): add <name> script`
6. Open a PR

---

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

| Type | Scope examples | When to use |
|------|---------------|-------------|
| `feat` | `agents`, `docs` | New agent, new guide |
| `fix` | `agents`, `scripts` | Correction to existing content |
| `docs` | `manifesto`, `readme`, `guides` | Documentation only |
| `chore` | `scripts`, `templates` | Tooling, scripts, templates |
| `refactor` | `agents`, `docs` | Restructuring without content change |

---

## Pull Request Template

All PRs use the template in [`.github/pull_request_template.md`](.github/pull_request_template.md).

**Before opening a PR, verify:**
- [ ] Content aligns with [`MANIFESTO.md`](MANIFESTO.md) principles
- [ ] Agent files follow the frontmatter schema in [`.github/agents/AGENTS.md`](.github/agents/AGENTS.md)
- [ ] New scripts have a docstring and are listed in [`scripts/README.md`](scripts/README.md)
- [ ] New docs are linked from the relevant index or guide
- [ ] No secrets, credentials, or personal data included

---

## Proposing New Research Topics

Open a GitHub Issue using the **Research** template. Good research topics include:
- External tools or frameworks to evaluate for adoption
- Methodologies from other fields (neuroscience, cognitive science, software engineering) to synthesize
- Open questions about the endogenic methodology itself

---

## Questions?

Open an issue or start a discussion. This repo is meant to grow — contributions that improve the methodology, extend the agent fleet, or add useful scripts are all welcome.

# Getting Started (🚧 Work in Progress - WIP)

This guide walks you through adopting the DogmaMCP governance framework for your own project. Choose your path below.

---

## Path 1: New Project Using Dogma Template

**Best for**: Starting a new project from scratch with governance built-in.

### Quick Setup (5 minutes)

```bash
# Option A: Use Cookiecutter (recommended)
uvx cookiecutter gh:EndogenAI/dogma

# Option B: Use adopt_wizard script
uv run python scripts/adopt_wizard.py \
  --org your-github-org \
  --repo your-project-name \
  --output-dir ./your-project-name

cd your-project-name
uv sync
```

### Step-by-Step: Cookiecutter Flow

**1. Generate Project from Template**

```bash
uvx cookiecutter gh:EndogenAI/dogma
```

Answer the prompts:
- `project_name`: Human-readable name (e.g., "My Governance Project")
- `project_slug`: Python/filesystem name (e.g., "my-governance-project")
- `org_name`: Your GitHub organization
- `repo_name`: Repository name (usually same as `project_slug`)
- `description`: One-line project description
- `python_version`: Target Python version (default: 3.11)

**2. Navigate to Your Project**

```bash
cd your-project-name
```

**3. Install Dependencies**

```bash
uv sync
```

Expected output:
```
Resolved 24 packages in 1.23s
Prepared virtual environment in 0.05s
Installed 24 packages in 0.15s
```

**4. Verify Setup with Tests**

```bash
uv run pytest
```

Expected output:
```
collected 42 items
tests/ ............ [ 100%]
====== 42 passed in 1.23s ======
```

### Post-Setup Customization Checklist

After running cookiecutter, review and customize these files:

| File | Task | Notes |
|------|------|-------|
| `MANIFESTO.md` | Review core values for your project; customize if needed | Do not remove core axioms (Endogenous-First, Algorithms-Before-Tokens, Local-Compute-First) |
| `AGENTS.md` | Inherit from dogma AGENTS.md; add org-specific constraints | See CONTRIBUTING.md for agent authoring conventions |
| `client-values.yml` | Set Deployment Layer values for your organization | Replace all placeholders (`YOUR_ORG`, `YOUR_EMAIL`, etc.) |
| `README.md` | Update hero, description, and Getting Started section | Keep link to dogma upstream |
| `CONTRIBUTING.md` | Tailor contributor guidelines to your team | Include your org's security and review practices |
| `docs/guides/` | Add org-specific workflow guides as needed | Reference AGENTS.md and MANIFESTO.md constraints |
| `.github/workflows/` | Verify CI workflows are enabled in your fork | Run `git push` to trigger first CI run |

**Verification**: Run `uv run python scripts/validate_agent_files.py AGENTS.md` — should exit 0.

---

## Path 2: Adopting Dogma in an Existing Project

**Best for**: Adding governance framework to an existing repository.

### Quick Setup (10 minutes)

```bash
# Clone dogma
git clone https://github.com/EndogenAI/dogma.git
cd dogma

# Run adopt_wizard to scaffold governance files
uv run python scripts/adopt_wizard.py \
  --org your-github-org \
  --repo your-existing-repo \
  --output-dir ../your-existing-repo-governance \
  --dry-run

# Review the output, then run without --dry-run
uv run python scripts/adopt_wizard.py \
  --org your-github-org \
  --repo your-existing-repo \
  --output-dir ../your-existing-repo-governance

# Copy generated files to your project
cp -r ../your-existing-repo-governance/* ../your-existing-repo/
cd ../your-existing-repo
```

### Step-by-Step: Adoption Flow

**1. Scaffold Governance Artefacts**

```bash
uv run python scripts/adopt_wizard.py \
  --org my-org \
  --repo my-project \
  --output-dir /tmp/my-project-governance \
  --dry-run
```

**Expected outputs** (in dry-run mode, listed but not written):
- `AGENTS.md` — Governance skeleton inheriting Core Layer constraints
- `client-values.yml` — Deployment Layer values for your org/repo
- `pyproject.toml` — Minimal project config with linting/testing setup
- `README.md` — Onboarding stub

**2. Review Generated Files**

```bash
cat /tmp/my-project-governance/AGENTS.md | head -30
cat /tmp/my-project-governance/client-values.yml
```

If the output looks correct, proceed to Step 3.

**3. Write Generated Files (Remove --dry-run)**

```bash
uv run python scripts/adopt_wizard.py \
  --org my-org \
  --repo my-project \
  --output-dir /tmp/my-project-governance
```

**4. Copy to Your Project**

```bash
cp -r /tmp/my-project-governance/* /path/to/your-project/
cd /path/to/your-project
```

**5. Validate the Governance Files**

```bash
uv run python scripts/validate_agent_files.py AGENTS.md
```

Expected output:
```
✅ AGENTS.md: Valid — all required sections present, tool count within limits
```

**6. Merge with Existing Files**

**AGENTS.md**: If your project already has governance docs, merge this with your existing content. Dogma's AGENTS.md **must** inherit Core Layer constraints from `MANIFESTO.md`.

**client-values.yml**: This is **new**. Ensure all placeholder values are customized for your organization.

**pyproject.toml**: **Merge carefully** — do not overwrite your existing `dependencies` or `scripts`. Import dogma's `[tool.ruff]`, `[tool.pytest]`, and pre-commit hook configuration instead.

**7. Install & Test**

```bash
uv sync
uv run pytest
```

---

## Example Scenarios

### Scenario 1: Startup Building Product with Governance from Day 1

**Situation**: New startup, 3-person engineering team, building an AI-powered SaaS product. Need governance for agent fleet + LLM guardrails from the start.

**Action**:
```bash
uvx cookiecutter gh:EndogenAI/dogma
# Answer prompts → my-saas-product
cd my-saas-product
uv sync
```

**Customization** (1 hour):
1. Update `MANIFESTO.md` with startup values (e.g., "Transparency to stakeholders", "Cost-conscious compute")
2. Add team member names to `.github/agents/README.md` Active Maintainers section
3. Link `CONTRIBUTING.md` to your Slack #engineering channel
4. Create `docs/guides/code-review-checklist.md` specific to your SaaS requirements

**Result**: All 3 developers use the same governance framework. Agent behavior is consistent across sessions.

### Scenario 2: Established Project Adding Dogma

**Situation**: Established open-source project with 50+ contributors, scattered agent/LLM usage, no formal governance. Want to standardize.

**Action**:
```bash
# Clone dogma repo
git clone https://github.com/EndogenAI/dogma.git
cd dogma
uv sync

# Run adoption flow
uv run python scripts/adopt_wizard.py \
  --org my-oss-org \
  --repo established-project \
  --output-dir /tmp/oss-governance

# Review generated files carefully
cat /tmp/oss-governance/AGENTS.md
cat /tmp/oss-governance/client-values.yml

# Copy to your project
cp -r /tmp/oss-governance/* ~/code/established-project/

# Merge existing CONTRIBUTING.md with the new one
# (Adopt_wizard generates a stub; merge with your existing practices)
```

**Customization** (2–3 hours):
1. Merge governance with existing contributor guidelines
2. Identify existing "agent-like" processes (code review, CI/CD, DevOps automation) and encode as `.agent.md` files
3. Create 2–3 project-specific SKILL.md files for domain workflows
4. Brief team on new governance constraints via team chat or wiki

**Result**: Contributors follow standardized governance. Onboarding new developers is faster.

### Scenario 3: Individual Researcher Adopting Dogma for Research Notebooks

**Situation**: AI researcher running multi-agent research sessions (e.g., literature survey, synthesis, peer review), needs to track agent decisions and reasoning.

**Action**:
```bash
# Light setup — just adopt AGENTS.md and session scratchpad protocol
git clone https://github.com/EndogenAI/dogma.git
cd my-research-project
mkdir -p docs/guides

# Copy just the files you need
cp ../dogma/AGENTS.md ./
cp -r ../dogma/docs/guides/session-management.md ./docs/guides/
cp -r ../dogma/.github/skills/session-management/ ./.github/skills/

# Initialize session structure
uv run python scripts/prune_scratchpad.py --init
```

**Customization** (30 min):
1. Update AGENTS.md with your research workflow agents
2. Configure MCP tools you need (research-scout, query-docs, scaffold-workplan)
3. Create a `.github/agents/research-orchestrator.agent.md` for your specific research domain

**Result**: Every research session is tracked in a structured scratchpad. Decision rationale is encoded. Future sessions can reference prior findings.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `cookiecutter: command not found` | Use `uvx cookiecutter` (recommended) or install with `uv pip install cookiecutter` |
| `uv sync` fails with "Python 3.11+ required" | Install Python 3.11+ from python.org or via `brew install python@3.11` |
| Generated files have placeholder values remaining | Run `adopt_wizard.py` again with correct `--org` and `--repo` flags |
| `validate_agent_files.py` exits with errors | Check AGENTS.md for TODO comments; fill in required sections per AGENTS.md schema |
| Can't run pytest (import errors) | Run `uv sync` again; ensure virtual environment is activated |

---

## Next Steps

### After Initial Setup

1. **Read MANIFESTO.md** — Understand the three core axioms: Endogenous-First, Algorithms-Before-Tokens, Local-Compute-First
2. **Read AGENTS.md** — Review operational constraints for your project's agents
3. **Create your first agent** — Use `.github/agents/my-agent.agent.md` to define a custom agent for your workflow
4. **Scaffold a workplan** — Use `scripts/scaffold_workplan.py` for multi-phase sessions

### Resources

- [**CONTRIBUTING.md**](../../CONTRIBUTING.md) — Contributor setup, commit discipline
- [**docs/guides/**](../../docs/guides/) — Formalized workflows and methodology guides
- [**docs/research/**](../../docs/research/) — Deep syntheses on governance, AI ethics, and best practices
- [**MANIFESTO.md**](../../MANIFESTO.md) — Core values and axioms
- [**AGENTS.md**](../../AGENTS.md) — Operational constraints
- [**MCP Server Docs**](../../mcp_server/README.md) — Governance toolset reference

---

## Support

- **GitHub Discussions**: [Ask questions](https://github.com/EndogenAI/dogma/discussions)
- **Report Issues**: [Open an issue](https://github.com/EndogenAI/dogma/issues)
- **Email**: conduct@endogenai.com


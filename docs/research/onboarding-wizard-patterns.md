---
title: "Onboarding Wizard Design Patterns (Adopt + Greenfield)"
status: "Draft"
---

# Onboarding Wizard Design Patterns (Adopt + Greenfield)

> **Status**: Draft
> **Research Question**: What are the best-practice patterns for building onboarding CLI wizards that adopt a repository's conventions, agents, and dogma into an existing or greenfield project?
> **Date**: 2026-03-07
> **Related**: [GitHub Issue #45](https://github.com/EndogenAI/dogma/issues/45) · [GitHub Issue #5](https://github.com/EndogenAI/dogma/issues/5) · [GitHub Issue #6](https://github.com/EndogenAI/dogma/issues/6)

---

## 1. Executive Summary

Endogenic development requires a conversion pathway: a way for existing teams and projects to adopt the dogma, tooling, and agent fleet without manually copying files. Two pathways exist:

1. **Adopt** — inject endogenic conventions (AGENTS.md, agents, guides, scripts) into an existing repo with minimal disruption
2. **Greenfield** — scaffold a new repo from zero, walking the user through a structured product definition workflow (gated on #45 product discovery output)

The design space for CLI wizards is well-studied. The dominant patterns are:
- **Template rendering** (cookiecutter, copier): variable prompts + file template substitution
- **Interactive prompts** (questionary, inquirer.py): rich TUI question flows returning structured answers
- **Scaffold scripts** (create-react-app, degit, `gh repo create --template`): one-shot file copy from a reference tree
- **Post-install hooks**: scripts that run after file copy to configure git, install deps, etc.

For the endogenic use case, the **Adopt** pathway requires a selective "inject, don't overwrite" approach that is more surgical than cookiecutter's full-repo substitution. The recommended technical approach is a custom Python CLI using `questionary` for prompts, implemented as `scripts/adopt_wizard.py`, installable as a `uv tool`.

---

## 2. Hypothesis Validation

### H1 — A single CLI tool can handle both Adopt and Greenfield pathways

**Supported** with a branching entry point. Both pathways share the same question infrastructure (project name, language, team size, etc.) and diverge at the action step: Adopt injects files into `$PWD`; Greenfield creates a new directory from scratch. The shared code is valuable — don't build two separate tools.

### H2 — Cookiecutter is the right engine for the Greenfield pathway

**Partially supported**. Cookiecutter (24.7k GitHub stars, active maintenance, `uv tool install cookiecutter`) handles the Greenfield case well:
- `cookiecutter.json` defines all prompts
- Pre/post hooks execute arbitrary Python for git init, `uv sync`, etc.
- Templates are shareable via GitHub (e.g., `uvx cookiecutter gh:EndogenAI/dogma`)

**Limitation**: Cookiecutter is designed for new-repo creation from a reference template. It is not designed for injecting into an existing repo. Using cookiecutter for Adopt would overwrite files, which is unacceptable.

**Recommendation**: Use cookiecutter for Greenfield only. Write a custom `scripts/adopt_wizard.py` for Adopt.

### H3 — Questionary is the right library for interactive prompts

**Confirmed**. `questionary` (MIT license, Python 3.8+, `pip install questionary`) provides:
- `questionary.text()`, `questionary.confirm()`, `questionary.select()`, `questionary.checkbox()`
- Conditional branching via `when` parameter
- ANSI-colored output, spinner support
- Validates input before proceeding

Single-file usage pattern that fits the `scripts/` directory well. Compatible with `uv run`.

### H4 — GitHub template repos are insufficient for the Adopt pathway

**Confirmed**. `gh repo create --template <org/repo>` creates a new repository seeded from a template, but:
- Only works for greenfield repo creation (cannot inject into existing repos)
- File names and content are copied verbatim — no variable substitution unless combined with a post-create wizard
- Does not run any setup scripts

Template repos are useful as a distribution mechanism for the Greenfield pathway only. The Adopt pathway requires a script that inspects the target repo and makes selective changes.

### H5 — The Adopt pathway must handle three file conflict scenarios

**Confirmed** through analogy with similar tools (Prettier migration scripts, ESLint wizard, etc.). The three scenarios:
1. **File does not exist** → copy from endogenic template
2. **File exists and is identical** → skip (idempotent)
3. **File exists and differs** → show diff, prompt user for merge strategy (skip / overwrite / manual)

This conflict resolution flow is the core of the Adopt wizard's value. Without it, the wizard would destroy existing customization.

---

## 3. Pattern Catalog

### Pattern 1 — Questionary Prompt Flow (for Adopt wizard)

```python
# scripts/adopt_wizard.py excerpt
import questionary

# Conditional flow example
def gather_config() -> dict:
    """Interview the user to determine what to inject."""
    project_name = questionary.text("Project name?", default=Path.cwd().name).ask()
    
    components = questionary.checkbox(
        "Select components to adopt:",
        choices=[
            questionary.Choice("Agent fleet (.github/agents/)", checked=True),
            questionary.Choice("AGENTS.md (root + docs/)", checked=True),
            questionary.Choice("Scripts (scripts/)", checked=True),
            questionary.Choice("Docs guides (docs/guides/)", checked=False),
            questionary.Choice("GitHub Actions (CI)", checked=False),
            questionary.Choice("Pre-commit hooks", checked=False),
        ]
    ).ask()
    
    return {"project_name": project_name, "components": components}
```

### Pattern 2 — Selective File Injection with Conflict Detection

```python
def inject_file(source: Path, dest: Path, dry_run: bool = False) -> str:
    """Inject a file with conflict detection. Returns: 'created', 'skipped', 'conflict'."""
    if not dest.exists():
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        return "created"
    
    if source.read_text() == dest.read_text():
        return "skipped"
    
    # Conflict: show diff, prompt for resolution
    diff = unified_diff(
        dest.read_text().splitlines(),
        source.read_text().splitlines(),
        fromfile=f"existing: {dest}",
        tofile=f"endogenic: {source}"
    )
    print("\n".join(list(diff)[:30]))  # first 30 lines
    
    action = questionary.select(
        f"Conflict in {dest.name}:",
        choices=["Skip (keep existing)", "Overwrite with endogenic version", "Open in editor"]
    ).ask()
    
    if action == "Overwrite with endogenic version" and not dry_run:
        shutil.copy2(source, dest)
        return "overwritten"
    return "skipped"
```

### Pattern 3 — Cookiecutter Template Structure (for Greenfield)

The Greenfield pathway distributes as a cookiecutter template hosted in this repository (or a dedicated template repo):

```
cookiecutter-endogenic/
  cookiecutter.json          # prompt definitions
  {{cookiecutter.project_slug}}/
    AGENTS.md                # parameterized with project_name
    MANIFESTO.md             # verbatim copy
    pyproject.toml           # parameterized
    .github/
      agents/
        README.md
      workflows/
        tests.yml
    scripts/
      # all scripts copied verbatim
    docs/
      guides/
```

The `hooks/post_gen_project.py` script runs after template generation:
```python
# Initialize git, run uv sync, open in VS Code
import subprocess
subprocess.run(["git", "init"])
subprocess.run(["uv", "sync", "--extra", "dev"])
```

### Pattern 4 — `--dry-run` as Default Posture

Per `AGENTS.md` guardrails, all wizard operations that write files must support `--dry-run`:

```bash
# Preview what would be injected — no files written
uv run python scripts/adopt_wizard.py --dry-run

# Execute for real
uv run python scripts/adopt_wizard.py
```

The dry-run output shows a file operation table:
```
  ✓  .github/agents/AGENTS.md              would create
  ✓  scripts/prune_scratchpad.py            would create
  ⚠  AGENTS.md                             CONFLICT — would prompt
  –  docs/guides/local-compute.md          would skip (exists, identical)
```

### Pattern 5 — Distribution via `uv tool`

The wizard is installable as a tool (no project checkout required for Greenfield):

```bash
# Install once
uv tool install git+https://github.com/EndogenAI/dogma

# Run Greenfield from anywhere
endogenic-new my-project

# Run Adopt in an existing repo
cd existing-project
endogenic-adopt
```

Entry points configured in `pyproject.toml`:
```toml
[project.scripts]
endogenic-new = "scripts.adopt_wizard:greenfield_main"
endogenic-adopt = "scripts.adopt_wizard:adopt_main"
```

---

## 4. UX Spec — Adopt Pathway

**Entry**: `uv run python scripts/adopt_wizard.py` (or `endogenic-adopt` via uv tool)

**Question flow**:
1. **Confirm target** — "Adopt endogenic conventions into: `<cwd>`? (Y/n)"
2. **Component selection** — checkbox: agent fleet / AGENTS.md / scripts / guides / CI / pre-commit
3. **Dry-run preview** — show operation table; confirm to proceed
4. **Execute + summarize** — create/skip/overwrite each file; print summary

**Post-adoption actions** (prompt each):
- Run `uv sync --extra dev`? (if pyproject.toml modified)
- Install pre-commit hooks? (`pre-commit install`)
- Create initial scratchpad? (`uv run python scripts/prune_scratchpad.py --init`)
- Open README.md in editor?

**Exit codes**: 0 = success, 1 = user abort, 2 = conflict resolution incomplete

---

## 5. UX Spec — Greenfield Pathway

> **Note**: D3 (Greenfield UX spec) is gated on issue #45 product discovery conversation completing. This section is a placeholder outline pending that discussion.

**Entry**: `uvx cookiecutter gh:EndogenAI/dogma` or `endogenic-new <project-name>`

**Question flow** (draft — subject to revision after #45):
1. Project name and slug
2. Python version target
3. Include GitHub Actions CI? (Y/n)
4. Include pre-commit hooks? (Y/n)
5. Team size (solo / small / team) — influences session management config
6. Primary domain (research / product / automation / mixed)

**Post-generation**:
- `git init && git add -A && git commit -m "chore: initial endogenic scaffold"`
- `uv sync --extra dev`
- Print "Next steps" guide pointing to MANIFESTO.md and AGENTS.md

---

## 6. Technical Approach and Toolchain

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python | Consistent with repo toolchain (`uv`-first) |
| Interactive prompts | `questionary` | MIT, well-maintained, rich question types, conditional branching |
| Greenfield templating | `cookiecutter` 2.x | Industry standard, GitHub distribution, hooks support |
| Distribution | `uv tool` entry point | Zero-install for end users; consistent with toolchain |
| Testing | `pytest` + `tmp_path` | Standard; dry-run makes wizard fully testable without side effects |
| Entry point file | `scripts/adopt_wizard.py` | Consistent with existing `scripts/` pattern |

**Dependencies to add to `pyproject.toml`**:
```toml
[project.optional-dependencies]
wizard = ["questionary>=2.0", "cookiecutter>=2.5"]
```

---

## 7. Implementation Roadmap

This research feeds directly into the following implementation work (see D5 requirement from issue #47):

**Issue to create**: "feat: implement Adopt onboarding wizard (`scripts/adopt_wizard.py`)"
- Depends on: #47 (this research), #5 (local compute), #6 (MCP)
- Scope: `questionary` prompt flow, file injection with conflict detection, `--dry-run`
- Tests: pytest with `tmp_path` fixture; all code paths testable without side effects

**Issue to create**: "feat: implement Greenfield cookiecutter template"
- Depends on: #45 (product definition), #47-adopt (wizard patterns confirmed)
- Scope: cookiecutter template + post-gen hooks
- Gate: #45 product discovery conversation must complete first

---

## References

- [Questionary docs](https://questionary.readthedocs.io/en/stable/) — interactive CLI prompt library
- [Cookiecutter GitHub](https://github.com/cookiecutter/cookiecutter) — project template engine (24.7k stars)
- [copier](https://copier.readthedocs.io/) — alternative to cookiecutter with update support
- [GitHub template repos](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository) — limitations for Adopt use case
- [GitHub Issue #47](https://github.com/EndogenAI/dogma/issues/47) — tracking issue
- [GitHub Issue #45](https://github.com/EndogenAI/dogma/issues/45) — parent epic (product definition gates Greenfield spec)

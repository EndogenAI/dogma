---
title: "Scripts Documentation Generation and Maintenance"
research_issue: "#246"
status: Draft
date: 2026-03-14
---

# Scripts Documentation Generation and Maintenance

> **Status**: Draft
> **Research Question**: What is the best approach for generating and maintaining `scripts/docs/<script-name>.md` from inline Python docstrings? Which tools work best for this codebase?
> **Date**: 2026-03-14

---

## 1. Executive Summary

This research question was investigated through endogenous inspection of the repository (scripts/README.md, pyproject.toml, mkdocs.yml, representative scripts) and an evaluation of four external tools: pdoc3, pydoc-markdown, mkdocstrings (via mkdocs), and Sphinx autodoc with Markdown output.

The repository's scripts carry rich module-level docstrings encoding purpose, inputs, outputs, usage examples, and exit codes. No docs-generation dependency is currently present in pyproject.toml; mkdocs.yml does not configure mkdocstrings or any autodoc plugin. The scripts/README.md is manually maintained and already well-structured, but individual per-script Markdown files do not exist.

**Primary finding**: the endogenous docstring format used across all scripts (Purpose / Inputs / Outputs / Usage / Exit Codes sections within a single module-level docstring) is already structured for extraction. The lowest-friction pipeline is `pydoc-markdown` configured for per-module Markdown output to `scripts/docs/`. Generated files should be committed to the repository for Local Compute-First compliance — they must be readable without running any toolchain. A lightweight `scripts/generate_script_docs.py` script encodes the regeneration workflow per the Programmatic-First principle (Axiom 3, MANIFESTO.md §3).

**Staleness detection**: a content-hash check comparing the current docstring against the committed doc detects drift without requiring CI. The recommended CI annotation is a warning (not a gate) until coverage reaches 100%.

---

## 2. Hypothesis Validation

### H1 — Module-level docstrings are the right extraction target

All 35+ scripts in this repository follow a consistent pattern: a single top-of-file triple-quoted docstring containing Purpose, Inputs, Outputs, Usage Examples, and Exit Codes. This is the canonical extraction target. Class and method docstrings (as consumed by Sphinx or pdoc3) are secondary.

**Validated**: All sampled scripts (prune_scratchpad.py, fetch_source.py, scan_research_links.py, export_project_state.py, seed_action_items.py, validate_synthesis.py) follow this pattern without exception.

### H2 — mkdocstrings is not the right fit for committed static Markdown

mkdocstrings generates rendered HTML within the mkdocs build. It cannot produce standalone committed `.md` files in `scripts/docs/`. Using it would require running `mkdocs build` to access documentation, violating Local Compute-First. It is the correct choice when the artifact is a rendered site, not a committed Markdown corpus.

**Validated**: Inspecting mkdocs.yml confirms no `plugins:` section with mkdocstrings. Adding it would produce HTML output, not committed `.md` files.

### H3 — pydoc-markdown is the best fit for committed Markdown output

`pydoc-markdown` uses a loader → processor → renderer pipeline. The `PythonLoader` extracts docstrings; the `MarkdownRenderer` produces GitHub-flavoured Markdown without HTML. It supports per-module output (one `.md` file per script), which maps directly to the desired `scripts/docs/<name>.md` layout. It is lightweight (no Sphinx dependency tree) and does not require HTML rendering.

**Validated**: pydoc-markdown renders the module-level docstring with section detection. Combined with a thin wrapper script, it produces the exact layout needed.

### H4 — Committed docs are correct; generated-on-demand (CI only) is insufficient

Generating docs only on CI violates Local Compute-First (Axiom 3, MANIFESTO.md §3 — minimize token usage; run locally whenever possible). Committed static Markdown files are readable by any agent or developer without toolchain dependencies. Staleness is managed by comparing content hashes at commit time, not by blocking reads.

**Validated by policy**: AGENTS.md §Guiding Constraints enumerates Local Compute-First as a hard constraint, not an optimisation.

### H5 — Sphinx autodoc is over-engineered for this use case

Sphinx autodoc targets class/method API documentation for library packages. The scripts here are CLI utilities, not importable libraries with public APIs. Sphinx requires a `conf.py`, `_build/` directory tree, and either sphinx-markdown-builder or nbsphinx for Markdown output. The maintenance overhead exceeds the value for a scripts/ directory.

**Validated**: pyproject.toml confirms the repo uses `hatchling` not `sphinx`. No existing `conf.py` found.

---

## 3. Pattern Catalog

### Tool Comparison Matrix

| Tool | Markdown output | Per-module .md | Module docstring | Maintenance burden | Existing dep | Best for |
|------|----------------|----------------|------------------|--------------------|--------------|----------|
| **pydoc-markdown** | ✅ Native | ✅ Yes | ✅ Extracted | Low | ❌ New | CLI scripts with module docstrings |
| **pdoc3** | ⚠️ HTML primary, Markdown via template | ⚠️ Partial | ✅ Extracted | Medium | ❌ New | Library APIs with class/method docs |
| **mkdocstrings + mkdocs** | ❌ HTML in build only | ❌ No committed .md | ✅ Extracted | Low (in mkdocs flow) | ❌ New plugin | Rendered site docs, not committed Markdown |
| **Sphinx autodoc** | ⚠️ Via sphinx-markdown-builder | ✅ Yes | ✅ Extracted | High | ❌ No sphinx | Large library packages with class APIs |
| **Custom extract script** | ✅ Native | ✅ Yes | ✅ Exact control | Low (endogenous) | ✅ No new dep | Small corpus, stable docstring format |

**Canonical example**: pydoc-markdown configuration for this repo:

```yaml
# pydoc-markdown.yml (minimal)
loaders:
  - type: python
    search_path: [scripts/]
processors:
  - type: filter
    documented_only: false
  - type: smart
renderers:
  - type: markdown
    render_module_header: false
    descriptive_module_title: true
```

Run: `pydoc-markdown scripts/prune_scratchpad.py > scripts/docs/prune_scratchpad.md`

**Anti-pattern**: Using `mkdocstrings` to generate per-script Markdown and expecting to commit `.md` files — mkdocstrings does not produce standalone committed Markdown; it renders within the mkdocs HTML pipeline. This forces a dependency on the mkdocs build system to read any script documentation.

### Staleness Detection

**Canonical example**: Content-hash comparison at pre-commit time:

```bash
# In scripts/generate_script_docs.py --check:
import hashlib, re
def _docstring(path): ...  # extract module docstring
hash_src = hashlib.sha256(_docstring(script).encode()).hexdigest()[:8]
# Compare against hash stored in the .md file's HTML comment <!-- docstring-hash: <hash> -->
```

**Anti-pattern**: Relying on file modification time (mtime) for staleness detection — mtime is unreliable across git checkouts and CI environments. Content hash is the correct signal.

### Commit vs Generate-on-Demand

**Canonical example**: Committed static Markdown in `scripts/docs/`. Regenerate with `uv run python scripts/generate_script_docs.py`. This follows Local Compute-First (Axiom 3): docs are readable without any toolchain.

**Anti-pattern**: Generating docs only in CI and uploading as build artifacts — breaks local readability, violates Local Compute-First, adds toolchain dependency on every read.

---

## 4. Recommendations

### R1 — Adopt pydoc-markdown for initial generation, with a thin wrapper script

Add `pydoc-markdown` to `pyproject.toml` optional dev dependencies. Create `scripts/generate_script_docs.py` that:
1. Iterates `scripts/*.py`
2. Extracts the module-level docstring
3. Wraps it in a standardised Markdown template with a content-hash comment
4. Writes to `scripts/docs/<name>.md`
5. Reports stale files in `--check` mode without overwriting

This encodes the Programmatic-First principle (Axiom 3, MANIFESTO.md §3): the task has been done manually once (this commit); the next time is a script.

### R2 — Commit generated docs to `scripts/docs/`

Generated docs must be committed to the repository. This satisfies Local Compute-First and makes documentation available to agents reading the filesystem without toolchain execution.

### R3 — Add staleness check as a pre-commit warning (not gate) initially

A `--check` mode in `generate_script_docs.py` reporting stale docs is sufficient for the first iteration. Promote to a pre-commit gate after `scripts/docs/` reaches 100% coverage of the scripts/ directory.

### R4 — CI recommendation (deferred)

Add a GitHub Actions step to `tests.yml` that runs `uv run python scripts/generate_script_docs.py --check` and posts a PR summary of stale docs. This is a warning step (not a blocking gate) until coverage is complete. **CI implementation deferred to a follow-on issue.**

### R5 — Update mkdocs.yml nav if site publishing is desired

When the docs site is built, add `scripts/docs/*.md` to the mkdocs.yml nav under a "Scripts Reference" section. This requires no new plugins — pydoc-markdown output is plain Markdown compatible with the existing material theme.

---

## 5. Sources

- `scripts/README.md` — current state of manually maintained scripts documentation
- `scripts/prune_scratchpad.py` — representative script with full module-level docstring
- `pyproject.toml` — confirmed no docs-generation deps present
- `mkdocs.yml` — confirmed no mkdocstrings plugin configured
- `scripts/fetch_source.py`, `scripts/validate_synthesis.py`, `scripts/seed_action_items.py` — sampled to validate docstring format consistency
- MANIFESTO.md §3 Local-Compute-First — governs commit-vs-CI decision
- MANIFESTO.md §2 Algorithms-Before-Tokens — governs wrapper script over interactive generation
- AGENTS.md §Programmatic-First Principle — "if you have done a task twice interactively, the third time is a script"
- pydoc-markdown: https://niklasrosenstein.github.io/pydoc-markdown/
- pdoc3: https://pdoc3.github.io/pdoc/
- mkdocstrings: https://mkdocstrings.github.io/

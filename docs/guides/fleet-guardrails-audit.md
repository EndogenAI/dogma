---
governs: [endogenous-first, algorithms-before-tokens, programmatic-first, self-governance]
---

# Fleet Guardrails Audit — Programmatic Enforcement Gap Report

**Date**: 2026-03-14  
**Branch**: feat/sprint-production-hardening-adoption  
**Closes**: [#152](https://github.com/endogenai/workflows/issues/152)

This audit surveys every behavioural guardrail stated in [`AGENTS.md`](../../AGENTS.md)
and [`MANIFESTO.md`](../../MANIFESTO.md) and classifies each by its current enforcement
layer.  The goal is to surface which guardrails are text-only conventions that could be
shifted into deterministic, machine-checkable gates — following the
[`Programmatic-First`](../../MANIFESTO.md#programmatic-first) principle and the
[`Enforcement-Proximity`](../../AGENTS.md#guiding-constraints) constraint.

---

## Enforcement Layer Taxonomy

| Layer | Code | Description |
|-------|------|-------------|
| Verbal | T1 | Documented convention read by an agent before acting |
| Text-constraint | T2 | Decision gate in a text document (decision table, checklist) |
| Static linting | T3 | Pre-commit hook or CI step that checks committed code |
| Runtime gate | T4 | Shell governor or runtime wrapper that intercepts commands |

---

## Guardrail Inventory

| Guardrail | Source | Enforcement Layer | Status | Scripting Gap? |
|-----------|--------|-------------------|--------|----------------|
| Read AGENTS.md / MANIFESTO.md before acting | AGENTS.md §Guiding Constraints | T1 + T3 (`detect_drift.py` cross-ref density) | Partial | No — drift linter already covers cross-ref density |
| Check `scripts/` before performing a multi-step task interactively | AGENTS.md §Programmatic-First | T2 decision table | Unenforced | Yes — no gate verifies agents consulted the catalog |
| Local model preferred over cloud inference | MANIFESTO.md §3, AGENTS.md §Guiding Constraints | T1 + T2 (`local-compute.md` guide) | Partial | Yes — `check_model_usage.py` proposed but not implemented |
| Minimal posture — carry only required tools | MANIFESTO.md §Minimal Posture | T3 (`validate_agent_files.py` checks `tools:` field) | Partial | No — tools-field check in place; deeper semantic audit optional |
| No heredoc file writes (`cat >> file << 'EOF'`) | AGENTS.md §Programmatic Governors | T3 (`no-heredoc-writes` pygrep hook) + T4 (zsh governor) | **Enforced** | — |
| No terminal file I/O redirection (`> file`, `\| tee`) | AGENTS.md §Programmatic Governors | T3 (`no-terminal-file-io-redirect` pygrep hook) | **Enforced** | — |
| Lint & format (ruff) | AGENTS.md §Guardrails | T3 (pre-commit + CI `lint` job) | **Enforced** | — |
| Agent file structure (BDI headings, cross-ref density) | AGENTS.md §VS Code Taxonomy | T3 (`validate_agent_files.py`, CI) | **Enforced** | — |
| Skill file structure | AGENTS.md §Agent Skills | T3 (`validate_agent_files.py --skills`, CI) | **Enforced** | — |
| D4 research doc structure | AGENTS.md §Agent Communication | T3 (`validate_synthesis.py`, CI) | **Enforced** | — |
| Value-encoding drift in agent files | AGENTS.md §Value Fidelity Test Taxonomy | T3 (`detect_drift.py`, CI) | **Enforced** | — |
| Fast tests on push | AGENTS.md §Guardrails | T3 (pre-push hook `fast-tests`) | **Enforced** | — |
| Relative links in Markdown docs | AGENTS.md §Guardrails | T3 (`check_doc_links.py`, CI Lychee) | **Enforced** | — |
| CRD substrate health check | AGENTS.md §Guardrails | T3 (`check_substrate_health.py`, CI) | **Enforced** | — |
| Client-values.yml Core Layer Impermeability | AGENTS.md §Deployment Layer | T3 (`validate_agent_files.py` checks citation order) | **Enforced** | — |
| No `## Phase N Review Output` heading in agent files | AGENTS.md §Agent Communication | T3 (`validate_agent_files.py`) | **Enforced** | — |
| Conventional commit message format | AGENTS.md §Commit Discipline, CONTRIBUTING.md | T2 (CONTRIBUTING.md reference) | Unenforced | **Yes** — no `commit-msg` hook |
| Secrets hygiene — never echo `$GITHUB_TOKEN` | AGENTS.md §Security Guardrails | T1 verbal only | Unenforced | **Yes** — no `detect-secrets` or `gitleaks` pre-commit hook |
| No `git push --force` to `main` | AGENTS.md §Guardrails | T1 verbal only | Unenforced | Yes — branch protection rule (GitHub admin); out of local-hook scope |
| No `--no-verify` bypass | AGENTS.md §Guardrails | T1 verbal only | Unenforced | Yes — enforcement is a workflow/social convention; hard to hook locally |
| SSRF — only `https://` from trusted sources to fetch scripts | AGENTS.md §Security Guardrails | T1 verbal only | Unenforced | Yes — static analysis of URL construction in scripts |
| Prompt injection awareness for `.cache/` content | AGENTS.md §Security Guardrails | T1 verbal only | Unenforced | Partial — hard to automate without semantic analysis |
| Verify-after-act for remote writes | AGENTS.md §Agent Communication | T1 verbal only | Unenforced | Yes — shell wrapper could enforce read-back on `gh issue create` etc. |
| Pre-use validation (Tier 0) before `gh` commands | AGENTS.md §Agent Communication | T1 verbal only | Unenforced | Yes — `gh` wrapper script could enforce `test -s` before `--body-file` |
| Script documentation completeness (docstring + README entry) | AGENTS.md §Programmatic-First | T2 + `generate_script_docs.py --check` (not in pre-commit) | Partial | **Yes** — add `generate_script_docs.py --check` to pre-commit and CI |
| Pre-commit hooks installed per clone | AGENTS.md §Guardrails | T1 verbal (`uv run pre-commit install`) | Unenforced | **Yes** — extend `check_substrate_health.py` to verify hook installation |
| Testing-First — every new script has tests | AGENTS.md §Testing-First | T3 (pre-push `fast-tests`) | Partial | Yes — no gate that *new* `scripts/*.py` files have a matching `tests/test_*.py` |
| Subagent commit authority routed through GitHub Agent | AGENTS.md §Subagent Commit Authority | T1 verbal only | Unenforced | Yes — social/process convention; no local static check available |

---

## Top 5 Scripting Gaps

These are the five gaps where a concrete, implementable programmatic check would
provide the highest enforcement improvement per engineering effort, ranked by
impact × tractability.

### Gap 1 — Conventional Commit Format (no `commit-msg` hook)

**Problem**: AGENTS.md and CONTRIBUTING.md both mandate Conventional Commits
format (`type(scope): description`) but there is no `commit-msg` hook to
reject non-conforming messages.  Any commit without a passing message silently
enters git history.

**Implementation**:
Add the `conventional-pre-commit` hook (or equivalent) to `.pre-commit-config.yaml`:
```yaml
- repo: https://github.com/compilerla/conventional-pre-commit
  rev: v3.4.0
  hooks:
    - id: conventional-pre-commit
      stages: [commit-msg]
      args: [feat, fix, docs, chore, test, refactor, ci, perf, build]
```
Or write `scripts/check_commit_message.py` that validates `$1` (the commit-msg
temp file) against the Conventional Commits regex.  Exit 1 rejects the commit.

**Effort**: Small.  Pre-existing hook available; config change only.

---

### Gap 2 — Secrets Hygiene (no credential-detection hook)

**Problem**: AGENTS.md §Security Guardrails prohibits committing credentials,
but there is no `detect-secrets` or `gitleaks` hook to catch accidental
credential exposure before it enters the git object store.  Once pushed, a
secret is compromised regardless of a subsequent `git revert`.

**Implementation**:
```yaml
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.5.0
  hooks:
    - id: detect-secrets
      args: ['--baseline', '.secrets.baseline']
```
Run `uv run detect-secrets scan > .secrets.baseline` once to establish the
baseline, then add `.secrets.baseline` to the repo.  The hook diffs new commits
against the baseline and blocks anything new that looks like a secret.

**Effort**: Small–medium.  One-time baseline scan; ongoing pre-commit enforcement.

---

### Gap 3 — Script Documentation Completeness (`generate_script_docs.py --check` not gated)

**Problem**: `scripts/generate_script_docs.py --check` exists and verifies that
every `scripts/*.py` has a docstring and a `scripts/docs/<name>.md` entry.
However, it is not in `.pre-commit-config.yaml` or the CI `lint` job, so a new
script can be committed with no docstring and the gap is discovered only in
review.

**Implementation**:
1. Add to `.pre-commit-config.yaml`:
   ```yaml
   - id: check-script-docs
     name: Verify script docstrings and docs/ entries
     entry: python3 scripts/generate_script_docs.py --check
     language: system
     files: ^scripts/[^_].*\.py$
     pass_filenames: false
   ```
2. Add to `.github/workflows/tests.yml` `lint` job:
   ```yaml
   - name: Check script docs completeness
     run: uv run python scripts/generate_script_docs.py --check
   ```

**Effort**: Small.  Script already exists; config wiring only.

---

### Gap 4 — Cloud Model Usage Detection (`check_model_usage.py` not yet implemented)

**Problem**: MANIFESTO.md §3 (Local Compute-First) explicitly names
`scripts/check_model_usage.py` as a candidate WARN-only T0 gate for detecting
hardcoded cloud API identifiers (e.g., `openai` SDK imports, `gpt-4o` model
name strings, hardcoded `api.openai.com` URLs) in committed code.  The script
does not exist yet and so the principle has no F4 enforcement form.

**Implementation**:
Write `scripts/check_model_usage.py` with:
- Patterns: `import openai`, `from openai`, `anthropic.Anthropic`, cloud model
  name literals (`gpt-4o`, `claude-3-5-sonnet`), hardcoded API base URLs.
- Mode: WARN-only (exit 0) until issue #131 baseline produces calibration data.
- Flag `--fail` reserved for future FAIL-blocking upgrade.
- Add to pre-commit as a WARN hook (no `fail_fast: true`).

**Effort**: Medium.  New script plus tests required.

---

### Gap 5 — Pre-commit Hook Installation Verification

**Problem**: AGENTS.md mandates `uv run pre-commit install && uv run pre-commit
install --hook-type pre-push` per clone, but nothing detects a missing
installation.  An agent working in a fresh clone can commit without passing any
of the T3 gates that enforce AGENTS.md constraints.

**Implementation**:
Extend `scripts/check_substrate_health.py` to check whether
`.git/hooks/pre-commit` exists and is executable; emit a WARN if not.  This
surfaces the gap at the start of a session rather than after a policy-violating
commit.

```python
hook_path = Path(".git/hooks/pre-commit")
if not hook_path.is_file() or not os.access(hook_path, os.X_OK):
    results.append(HealthResult("pre-commit hooks", "WARN", "Not installed — run: uv run pre-commit install"))
```

**Effort**: Very small.  Extend existing script; already in CI.

---

## Summary Statistics

| Status | Count |
|--------|-------|
| Enforced (T3/T4) | 14 |
| Partial (T2 + incomplete T3) | 5 |
| Unenforced (T1/T2 only) | 9 |
| **Total guardrails audited** | **28** |

50% of guardrails have no programmatic enforcement.  The five gaps above
represent the highest-return targets for the next scripting sprint.

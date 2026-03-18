---
name: validate-before-commit
description: |
  Encodes the full pre-commit guardrail sequence from AGENTS.md as a reusable checklist for any agent before git commit or git push. USE FOR: running lint, format, tests, and compliance checks before every commit; determining which checks apply based on which file types changed; installing pre-commit hooks once per clone; verifying CI passes before requesting review. DO NOT USE FOR: test authoring decisions (use the testing guide); release pipeline logic (use the Release Manager agent).
argument-hint: "file type changed (scripts|agents|skills|research|all)"
---

# Validate Before Commit

This skill enacts the *Algorithms Before Tokens* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md): validation is encoded once as a deterministic gate and executed consistently, not re-checked interactively per session. The full guardrail sequence is governed by [`AGENTS.md`](../../../AGENTS.md) § Guardrails. When this skill and those documents conflict, the primary documents take precedence.

---

## 1. Decision Table — Which Checks Apply

Run the checks corresponding to which file types were changed:

| Files changed | Required checks |
|---------------|----------------|
| `scripts/` or `tests/` | Lint, format, fast tests |
| `.github/agents/*.agent.md` | Lint, format, fast tests, agent compliance, drift check |
| `.github/skills/*/SKILL.md` | Lint, format, fast tests, skills compliance |
| `docs/research/*.md` | Research doc compliance |
| Any of the above | All applicable checks in the rows above |
| None of the above (docs, plans, guides) | No code checks required |

> **Pre-commit hook coverage** — the hooks in `.pre-commit-config.yaml` run automatically on `git commit` (and `fast-tests` on `git push`) once installed with `uv run pre-commit install`. They cover every row in this table. If pre-commit is installed, manual checks are needed only for lychee dead links (network-only, no local equivalent).

When in doubt, run all checks. The full sequence takes under 60 seconds on a warm environment.

---

## 2. Full Check Sequence

### 2.1 Lint and Format

```bash
uv run ruff check scripts/ tests/
uv run ruff format --check scripts/ tests/
```

To auto-fix format violations (safe, no logic changes):

```bash
uv run ruff format scripts/ tests/
```

### 2.2 Fast Tests

```bash
uv run pytest tests/ -x -m "not slow and not integration" -q
```

The `-x` flag stops on the first failure. The marker filter skips network and slow tests — fast enough to run before every commit.

### 2.3 Agent File Compliance

Run this only when `.github/agents/*.agent.md` files were changed:

```bash
uv run python scripts/validate_agent_files.py --all
```

To check a single file:

```bash
uv run python scripts/validate_agent_files.py .github/agents/<file>.agent.md
```

### 2.4 Skills Compliance

Run this only when `.github/skills/` files were changed:

```bash
uv run python scripts/validate_agent_files.py --skills
```

### 2.5 Research Doc Compliance

Run this only when `docs/research/*.md` files were changed:

```bash
uv run python scripts/validate_synthesis.py docs/research/<changed-file>.md
```

### 2.6 Value-Encoding Drift Check

Run this when `.github/agents/*.agent.md` files were changed:

```bash
uv run python scripts/detect_drift.py --agents-dir .github/agents/ --format summary --fail-below 0.33
```

A drift score below 0.33 means the agent file lacks sufficient MANIFESTO.md axiom references. Fix by adding explicit citations to `Endogenous-First`, `Algorithms Before Tokens`, or `Local Compute-First` in the agent body.

### 2.7 Push-Stage: Full Fast Tests

The `fast-tests` hook is configured as a `push`-stage hook and runs automatically on `git push` once pre-commit is installed. To run manually before pushing:

```bash
uv run pytest tests/ -x -m "not slow and not integration" -q
```

---

## 3. Pre-Commit Hooks

Pre-commit hooks automate ruff, validate-synthesis, and validate-agent-files on every `git commit`; `fast-tests` runs on every `git push`. Install **both** once per clone:

```bash
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
```

After installation, hooks run automatically on `git commit`. You do not need to run the manual checks above for files covered by the hooks — but running them proactively surfaces issues earlier in the workflow.

**Never use `--no-verify`** to skip pre-commit hooks. Bypassing hooks is explicitly prohibited by [`AGENTS.md`](../../../AGENTS.md) § Guardrails.

---

## 4. CI Gate — Wait for Green Before Review

After every `git push`:

```bash
gh run list --limit 3
```

Wait for the latest run to show a green `✓` status before requesting or re-requesting Copilot review. A push with failing CI is a broken PR — fix the failures before doing anything else.

**Common CI failure modes**:

| Failure | Fix |
|---------|-----|
| `ruff format --check` fails (N files would be reformatted) | Run `uv run ruff format scripts/ tests/` then re-commit. **Root cause**: `pre-commit install` not run — the `ruff-format` hook auto-formats on commit once installed. |
| `ruff check` fails (N errors) | Run `uv run ruff check --fix scripts/ tests/` then review and re-commit. |
| `validate_synthesis` heading missing | Add the required heading to the research doc. |
| `validate_agent_files` cross-reference missing | Add a `../../MANIFESTO.md` or `../../AGENTS.md` link to the agent body. |
| `validate_agent_files --skills` fails | Run `uv run python scripts/validate_agent_files.py --skills` locally to see which SKILL.md is malformed. |
| `detect_drift` below threshold | Add explicit axiom citations to the flagged `.agent.md` file. |
| `lychee` dead link (TLS / 4xx) | Check if the URL is genuinely dead. If it's a transient TLS issue (e.g. `spec.modelcontextprotocol.io`), add to `.lycheeignore` with a dated comment. |

### Lychee (Dead Link Checks)

**Lychee two-step rule**: After any lychee fix commit, always wait for CI to complete before declaring lychee clean. CI runners receive intermittent 503s from high-traffic domains (e.g., theatlantic.com) that local `lychee` does not reproduce. These produce a second CI failure requiring a separate `.lycheeignore` entry and re-push. Lychee is clean only when CI is green, not when local check exits 0.

---

## 5. Commit Only After All Checks Pass — Orchestrator Terminal Operations

The **Orchestrator performs commits via direct terminal operations** after all checks pass. The full validation sequence in order:

```bash
# 1. Lint + format
uv run ruff check scripts/ tests/
uv run ruff format --check scripts/ tests/

# 2. Fast tests
uv run pytest tests/ -x -m "not slow and not integration" -q

# 3. Agent file compliance (if .github/agents/ changed)
uv run python scripts/validate_agent_files.py --all

# 4. Skills compliance (if .github/skills/ changed)
uv run python scripts/validate_agent_files.py --skills

# 5. Research doc compliance (if docs/research/ changed)
uv run python scripts/validate_synthesis.py docs/research/<changed-file>.md

# 6. Commit
git add <files>
git commit -m "<type>(<scope>): <description>"

# 7. Push and verify CI
git push
gh run list --limit 3
```

---

## Guardrails

- **Never commit with `--no-verify`** — pre-commit hooks are not optional.
- **Never push without waiting for CI** before requesting review.
- **Never skip the research doc validation step** when `docs/research/` files change.
- Do not interpret a zero exit from `git push` as CI passing — always check `gh run list`.

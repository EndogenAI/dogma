---
title: T4-Without-T1 Trap — Squash Merge Pattern
status: Active
---

# T4-Without-T1 Trap — Squash Merge Pattern

## Trap Definition

**T4-Without-T1** = implementing governors (pre-commit hooks, CI gates, rate-limit policies) without encoding the underlying principles (MANIFESTO.md axioms) into AGENTS.md or docs/guides/.

### The Problem

Governors are T4 (runtime / mechanical enforcement). They enforce constraints algorithmically — `no-heredoc-writes` pre-commit hook rejects files containing `cat >> file << 'EOF'`.

But governors are fragile if they exist in isolation:

1. **No _why_**: Future contributors see the gate fail, not why it matters
2. **Silent drift**: Team members disable (`git commit --no-verify`) because they don't understand the reasoning
3. **Governance debt**: Each governor requires maintenance (catching new patterns, edge cases)
4. **Organizational risk**: Governors at one institution may not transfer to another (T4 without T1 is not portable)

### The Solution: Squash Merge with Synchronous Governance Update

Whenever a PR introduces a new governor or modifies an existing one:

1. **Ensure MANIFESTO.md encoding** — if the governor enforces a principle from MANIFESTO.md, verify the principle is documented and cited
2. **Update AGENTS.md** — add a reference to the governor in the relevant constraint section (e.g., "Heredoc Prohibition" section for `no-heredoc-writes`)
3. **Update docs/guides/** — if the governor is complex or addresses a workflow gap, add a corresponding guide (e.g., `guides/governor-setup.md` for shell preexec)
4. **Commit message** — cite both the governor implementation AND the governance encoding (e.g., "fix(ci): add no-heredoc-writes pre-commit hook; docs(AGENTS): cite heredoc prohibition in File Writing Guardrails")

---

## Canonical Example: Heredoc Governor

### Bad PR (T4-without-T1)

PR adds `no-heredoc-writes` pre-commit hook without updating documentation:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: no-heredoc-writes
      name: Reject heredoc writes
      entry: grep ...
```

**Problem**: Months later, a team member disables the hook (`--no-verify`) because they don't know why it exists.

### Good PR (T4 with T1)

PR adds the same hook _plus_ governance updates:

1. **MANIFESTO.md** — already documents the principle (Algorithms-Before-Tokens) and cites endogenous best practices
2. **AGENTS.md** — adds to the File Writing Guardrails section:
   > **Heredoc Prohibition** — NEVER use heredocs (`<< 'EOF'`) for Markdown or code. Backticks, triple-backtick fences, and special characters silently corrupt content. Enforced by pre-commit hook `no-heredoc-writes` (Governor A). See [`guides/governor-setup.md`](guides/governor-setup.md) for full setup guide.

3. **docs/guides/governor-setup.md** — full setup guide with:
   > Why this matters: heredocs silently corrupt content containing backticks and fences. The tool layer (Governor A — pre-commit) prevents accidental commits. The interactive layer (Governor B — shell preexec) prevents command execution. Both layers encode the same principle: **structure file writes as deterministic operations, not streaming commands**.

4. **Commit message**:
   > fix(ci): add no-heredoc-writes pre-commit hook to reject unsafe file writes
   > 
   > Implements File Writing Guardrails (AGENTS.md § File Writing Guardrails).
   > Encodes Algorithms-Before-Tokens (MANIFESTO.md § 2): deterministic file tools
   > prevent silent corruption that interactive shell commands do not catch.
   > 
   > Enforced at two layers:
   > - Governor A (T3): pre-commit hook (on commit)
   > - Governor B (T4): shell preexec (interactive terminal)
   > 
   > See docs/guides/governor-setup.md for full setup and rationale.

---

## Governance Layer Mapping

| Layer | Artifact | Example | Governance Check |
|-------|----------|---------|------------------|
| **T1** (Principles) | MANIFESTO.md | Algorithms-Before-Tokens | Does it derive from core axiom? |
| **T2** (Constraints) | AGENTS.md | File Writing Guardrails | Does AGENTS.md cite the constraint? |
| **T3** (Static)  | .pre-commit-config.yaml | no-heredoc-writes | Does CI enforce it? |
| **T4** (Runtime) | Shell preexec / hook | Governor B | Does execution respect it? |

A complete governor implements all four layers (T1 → T2 → T3 → T4). Skipping T1 or T2 produces isolated T3/T4 enforcement that fails over time.

---

## Checklist for PR Review

Before merging any PR that introduces a new governor:

- [ ] MANIFESTO.md principle documented and cited (if applicable)
- [ ] AGENTS.md constraint section added or updated
- [ ] docs/guides/ entry created (for complex governors)
- [ ] Commit message cites both implementation _and_ principle
- [ ] Example provided showing what the governor prevents

**Review gate**: No PR introducing a new governor merges without a synchronous governance update.

---
governs: [endogenous-first, documentation-first, programmatic-first]
---

# HGT Ingestion Cadence

> Governing axiom: [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — learnings from derived repos must flow back to the dogma template to keep the template substrate coherent. See [AGENTS.md § Agent Communication → HGT Learning Slot](../../AGENTS.md#agent-communication).

HGT (Horizontal Gene Transfer) is the project's mechanism for back-propagating learnings from derived repos to the dogma template. At the close of every sprint, the Executive Orchestrator runs the HGT Learning Slot. This guide specifies the cadence, classification rules, and propagation steps.

---

## Cadence

**Once per sprint at close** — HGT is not a continuous process. It is a discrete sprint-close activity, scheduled as the final step before the session summary is written.

Do not defer HGT to the next sprint. Accumulated learnings that are not classified and propagated become stale; their context is lost as the codebase diverges.

---

## Task-Regime Annotation

Each accumulated learning from the sprint must be classified into one of two regimes:

| Regime | Definition | Action |
|--------|-----------|--------|
| **Upstream** | The learning improves the dogma template in a way that benefits all derived repos | Propagate back to dogma via PR |
| **Internal** | The learning is specific to this derived repo's context, clients, or constraints | Keep in derived repo only; do not propagate |

**Classification signal**: Ask — "Would this constraint or pattern improve any dogma-derived repo, regardless of its domain?" If yes → Upstream. If the learning depends on domain-specific context (client values, proprietary tooling, project-specific conventions) → Internal.

---

## Propagation Steps (Upstream Regime)

For each learning classified as Upstream:

1. **Open a branch** against the dogma template repository:
   ```bash
   git checkout -b chore/hgt-<sprint-slug>
   ```

2. **Commit the change** using a `chore(hgt):` Conventional Commits prefix:
   ```
   chore(hgt): propagate <learning description> from sprint <N>
   
   Source: .tmp/<branch-slug>/<YYYY-MM-DD>.md § <section>
   Derived repo: <repo name>
   ```

3. **Reference the source scratchpad** in the commit body — include the branch slug and section heading where the learning was recorded. This creates a traceable link from the dogma change back to the session where the learning was discovered.

4. **Open a PR** against dogma's `main` branch and request Review agent approval:
   ```bash
   gh pr create \
     --title "chore(hgt): propagate learnings from <repo> sprint <N>" \
     --body-file /tmp/hgt-pr-body.md \
     --label "type:chore,area:docs"
   ```

5. **Get Review agent APPROVED** before merging. The Review agent validates that:
   - The propagated content does not introduce domain-specific constraints
   - The change is consistent with MANIFESTO.md axioms
   - The commit message follows the `chore(hgt):` format and includes the source reference

---

## HGT Learning Slot Checklist (Sprint Close)

At sprint close, work through this checklist before writing the `## Session Summary`:

- [ ] List all learnings accumulated during the sprint (reference scratchpad sections)
- [ ] Classify each as Upstream or Internal
- [ ] For each Upstream learning: open a branch, commit, open PR, request Review
- [ ] For each Internal learning: record in the derived repo's `docs/guides/` or `AGENTS.md` if not already encoded
- [ ] Write the HGT summary in the session scratchpad under `## HGT Learning Slot`

---

## Governing References

- [AGENTS.md § Agent Communication → HGT Learning Slot](../../AGENTS.md#agent-communication) — the original HGT Learning Slot constraint this guide operationalizes
- [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — learnings from practice are endogenous knowledge; propagating them keeps the template substrate coherent
- [AGENTS.md § Commit Discipline](../../AGENTS.md#commit-discipline) — `chore(hgt):` commit type follows Conventional Commits format

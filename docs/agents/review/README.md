# Review Agent — Extended Documentation

This document provides the invocation guide, acceptance criteria format, and a worked example for the Review agent.

For BDI content (beliefs, workflow, guardrails), see [`.github/agents/review.agent.md`](../../../.github/agents/review.agent.md).

---

## 1. When to Invoke

Invoke the Review agent before **every commit** that involves:

- Any file in `docs/` (guides, research, agents)
- Any `.agent.md` or `SKILL.md` file
- Any script in `scripts/` (new or modified)
- Any change to `AGENTS.md`, `MANIFESTO.md`, or `CONTRIBUTING.md`

**Do not invoke for**:

- Scratch files, temp files, or `.tmp/` content (gitignored, never committed)
- Pure whitespace or formatting fixes where no logic changed
- Mechanical renames with no content modification (verify with `git diff --stat` first)

### Routing Rule

The Review agent is **always invoked by the Orchestrator**, not by specialist agents directly. The handoff sequence is:

```
Specialist agent (Docs/Scripter/Fleet) → Orchestrator (receives result) → Review → GitHub Agent (commit)
```

Specialist agents do not invoke Review directly. The Orchestrator is the review gatekeeper.

---

## 2. Acceptance Criteria Format

Every Review delegation must include **explicit, numbered, binary acceptance criteria**. Binary means each criterion is either PASS or FAIL — no hedging.

### Template

```
Validate [file(s)] against these N criteria:
1. [Criterion description — testable, binary]
2. [Criterion description — testable, binary]
...N

Return: APPROVED or REQUEST CHANGES — [criterion number: one-line reason], one line per failing criterion.
```

### Rules for Criteria

- **One assertion per criterion** — do not bundle two checks into one criterion number
- **Existence + integration** — pair existence checks ("does section X exist?") with integration checks ("does section X link to Y?")
- **Concrete, not generic** — "heading 'Guardrails' is present" not "document is well-structured"
- **Binary pass/fail** — not "consider whether" or "check if appropriate"

### Anti-Pattern

```
# BAD — generic, unbounded, produces low-signal review
"Review this document and flag any issues."
```

### Canonical Pattern

```
# GOOD — explicit criteria, binary result
Validate docs/guides/new-guide.md against 4 criteria:
1. File contains H2 headings: Overview, Workflow, and Guardrails
2. No guardrail from AGENTS.md has been removed or softened
3. All cross-references link to files that exist in the workspace
4. validate_synthesis.py exits 0 on this file

Return: APPROVED or REQUEST CHANGES — [N: reason], one line per failing criterion.
```

---

## 3. Worked Example — 7-Criterion Review Prompt

### Scenario

Executive Docs has written a new D4 research synthesis document. Orchestrator delegates to Review with 7 explicit criteria.

### Delegation Prompt

```
Validate docs/research/new-synthesis.md against these 7 criteria:

1. Structure: has a YAML frontmatter block with `title` and `status` fields?
2. Entry completeness: all required D4 H2 headings present (Executive Summary,
   Hypothesis Validation, Pattern Catalog, Recommendations, Sources)?
3. Pattern Catalog: at least one entry with **Canonical example**: labeled verbatim?
4. MANIFESTO alignment: at least 2 explicit citations to MANIFESTO.md axioms
   (by name + section reference, not paraphrase)?
5. Cross-reference validity: all `[text](path)` links target files that exist in
   the workspace?
6. Source existence: all URLs in the Sources section appear in
   `.cache/sources/manifest.json` or are accompanied by a retrieval date?
7. No guardrail removal: no constraint from AGENTS.md has been softened
   or omitted compared to prior version of this file?

Return: APPROVED or REQUEST CHANGES — [criterion number: one-line reason],
one line per failing criterion. Nothing else.
```

### Example Return — Approved

```
APPROVED
```

### Example Return — Request Changes

```
REQUEST CHANGES
3: Pattern Catalog has no **Canonical example**: labeled entry — all examples are inline prose
4: MANIFESTO axioms mentioned by name but section references (§N) are absent
```

### What the Orchestrator Does Next

- **APPROVED** → delegate to GitHub Agent to commit
- **REQUEST CHANGES** → return to Executive Docs with the specific failing criteria; do not re-delegate the full file, delegate only the fixes

---

## 4. Review Scope Discipline

The Review agent is **read-only** — it never edits files. If it identifies a fix, it describes the required change and returns; the originating agent applies the fix.

Criterion cardinality (number of explicit criteria) is the primary predictor of review completeness. A 7-criterion prompt reliably catches what a generic "validate this" prompt misses. For every new review delegation, write at least as many criteria as there are distinct quality dimensions in the target file.

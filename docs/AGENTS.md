# docs/AGENTS.md

> This file narrows the constraints in the root [`AGENTS.md`](../AGENTS.md) for documentation work.
> It does not contradict any root constraint — it only adds documentation-specific rules.

---

## Purpose

This file governs the creation, review, and maintenance of documentation in `docs/`.

---

## Documentation-First Requirement

Every agent action that changes a workflow, script, or agent file must produce a corresponding
documentation update. The sequence is:

1. Change made → commit
2. Documentation updated → commit
3. PR opened linking both commits

**Never merge a script or agent change without updating the relevant `docs/` files.**

---

## What Lives in `docs/`

| Path | Purpose |
|------|---------|
| `docs/guides/` | Step-by-step guides for working with agents, scripts, and workflows |
| `docs/protocols/` | Formal protocol specifications (session management, handoff graph, etc.) |
| `docs/research/` | Research notes, literature reviews, and synthesis documents |

---

## Writing Standards

- Use clear, concise Markdown
- Every guide should have a "Why" section explaining the motivation
- Code blocks must include the language identifier (` ```bash `, ` ```python `, etc.)
- Link to related docs, agents, and scripts by relative path
- Research docs should distinguish between "established fact", "working hypothesis", and "open question"

---

## Research Documents

Research documents in `docs/research/` follow this structure:

```markdown
# [Topic] — Research Notes

## Research Question
## Why This Matters
## Key Findings
## Open Questions
## Sources
## Actionable Recommendations
```

Research is the bridge between external knowledge and endogenous encoding. Every research
document should end with actionable recommendations — what should be adopted, scripted, or
documented as a result of the research.

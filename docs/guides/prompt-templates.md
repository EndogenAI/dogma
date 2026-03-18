---
title: Prompt Template Registry
status: Active
---

# Prompt Template Registry

Registry of battle-tested prompt templates; consult before prompting a new subagent.

## Phase Handoff Prompt

**Use case**: Delegate a multi-phase session to a subagent with full context preservation.

```
@<Agent> Please continue the session on branch [branch-slug].
Read the active scratchpad at .tmp/[branch-slug]/[YYYY-MM-DD].md before delegating anything —
specifically the ## Executive Handoff and ## Session Summary sections.
Focus for this session: [one sentence from the handoff's "Recommended Next Session" section].
Write ## Session Start with a one-paragraph orientation before proceeding.
```

**Expected output**: Single line confirming phase pickup + session summary.

---

## Deep Research Sprint

**Use case**: Coordinate full research pipeline (Scout → Synthesizer → Reviewer → Archivist).

```
Execute the research sprint for issue [#NNN]:
1. Scout: Fetch and distill sources from [list/manifest]
2. Synthesizer: Consolidate findings into D4 doc structure (title, status, Pattern Catalog, Recommendations)
3. Reviewer: Validate against checklist [link to checklist]
4. Archivist: Commit docs/research/[topic].md with [commit message]
Return: commit SHA + one-line summary of 3 key findings.
```

**Expected output**: Commit hash + bullets (findings).

---

## Delegation Prompt (Compressed)

**Use case**: Delegate a scoped task with explicit output format ceiling.

```
**Goal**: [one imperative sentence]
**Scope**: [file/section/exclusions]
**Tasks**: [numbered list, specific actions]
**Output format**: [format type]; ≤[token ceiling]
Return only: [X, Y, Z]
```

**Expected output**: Exactly as specified; no preamble.

---

## Review Gate

**Use case**: Validate a deliverable against explicit criteria.

```
Validate [deliverable] against these [N] criteria:
1. [criterion]: [binary check]
2. [criterion]: [binary check]
...
Return: APPROVED or REQUEST CHANGES — [criterion #: one-line reason]
```

**Expected output**: Single verdict line with rationale.

---

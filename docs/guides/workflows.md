# Agent Workflows

Formalized workflows for the EndogenAI project. Each workflow defines the sequence of agents,
gates that must pass before advancing, human review checkpoints, and GitHub issue conventions
for showing work permanently.

The overarching pattern at every level of every workflow is **expansion → contraction**:
expand broadly during discovery, then contract into precise, durable outputs. This maps
directly to design thinking methodology and is the endogenic approach to all knowledge work.

---

## Contents

- [Research Workflow](#research-workflow)
- [Documentation Workflow](#documentation-workflow)
- [Scripting Workflow](#scripting-workflow)
- [Gates Reference](#gates-reference)
- [GitHub Issue Conventions](#github-issue-conventions)
- [Human Review Checkpoints](#human-review-checkpoints)

---

## Research Workflow

The research workflow converts an open question into a committed synthesis document in
`docs/research/`. It is orchestrated by the **Executive Researcher** and proceeds through
four specialist sub-agents.

### Trigger

A GitHub issue tagged `research` exists, or the Executive Researcher identifies a knowledge
gap that requires structured investigation.

### Phases

```
Orient → Frame → Scout (expand) → Synthesize (contract) → Review → Archive → Notify
```

---

### Phase 1 — Orient

**Agent**: Executive Researcher  
**Gate before advancing**: session scratchpad initialized; `OPEN_RESEARCH.md` read; no duplicate issue exists

```bash
uv run python scripts/prune_scratchpad.py --init
```

Read:
- `.tmp/<branch>/<date>.md` — prior session context
- `docs/research/OPEN_RESEARCH.md` — existing research queue and gate deliverables
- Open GitHub issues tagged `research`

**Human checkpoint**: confirm the research question is correctly scoped before delegating.

---

### Phase 2 — Frame

**Agent**: Executive Researcher  
**Output**: written to session scratchpad `## Research Frame` section

Write a concise research frame:

```markdown
## Research Frame — <Topic>

**Question**: What are we trying to learn?
**Good answer looks like**: <description of satisfying answer>
**Gate deliverables**: D1, D2, D3 (from OPEN_RESEARCH.md)
**Scoping constraints**: <e.g., local compute only; no cloud services>
**Endogenous sources already read**: <list>
```

**Gate before advancing**: frame committed to scratchpad; deliverables identified.

---

### Phase 3 — Scout (Expansion)

**Agent**: Research Scout  
**Invocation prompt**: *"Please survey [topic] and catalogue all relevant sources, links, and raw findings into the active session scratchpad under '## Scout Output'. Do not synthesize — gather only. Seed references: [paste from OPEN_RESEARCH.md]"*

**What Scout does**:
1. Reads local sources first (endogenous-first).
2. Surveys external sources: fetches pages, reads abstracts, follows references up to 2 levels deep.
3. Catalogues findings in a structured table — no interpretation.

**Scout Output format**:

```markdown
## Scout Output — <Topic> — <Date>

### Sources Surveyed

| # | Title | URL | Relevance |
|---|-------|-----|-----------|

### Key Raw Findings
- ...

### Leads for Follow-Up
- [ ] URL or reference
```

**Gate before advancing**: at least 3–5 relevant sources catalogued; no synthesis present in Scout output; Scout has returned control to Executive Researcher via takeback handoff.

---

### Phase 4 — Synthesize (Contraction)

**Agent**: Research Synthesizer  
**Invocation prompt**: *"Raw sources have been catalogued in the session scratchpad under '## Scout Output'. Please synthesize into a structured research draft in docs/research/<slug>.md following the expansion→contraction pattern. Topic: [topic]. Gate deliverables: [D1, D2, D3]."*

**What Synthesizer does**:
1. Reads Scout output from scratchpad.
2. Drafts `docs/research/<slug>.md` following the standard structure (see `docs/AGENTS.md`).
3. Sets `Status: Draft — pending review`.
4. Returns control to Executive Researcher via takeback handoff.

**Gate before advancing**: draft exists at `docs/research/<slug>.md`; all gate deliverables from `OPEN_RESEARCH.md` are addressed or explicitly deferred to open questions; no raw Scout notes present in the draft.

---

### Phase 5 — Review

**Agent**: Research Reviewer  
**Invocation prompt**: *"A research synthesis draft is ready. Please validate it against the endogenic methodology standards and flag any gaps, unsupported claims, or contradictions. Draft: docs/research/<slug>.md. Gate deliverables: [D1, D2, D3]."*

**What Reviewer checks** (full checklist in `research-reviewer.agent.md`):
- Research question addressed
- Claims cited to sources
- Consistent with `MANIFESTO.md`
- Recommendations are concrete and actionable
- Document is free of raw Scout notes

**Gate before advancing**: Reviewer verdict is **Approved**. If verdict is **Revise**, cycle back to Phase 4. If **Reject**, cycle back to Phase 3.

**Human checkpoint**: Review the Reviewer's findings in the scratchpad before approving to archive.

---

### Phase 6 — Archive

**Agent**: Research Archivist  
**Invocation prompt**: *"Research has been reviewed and approved. Reviewer verdict is in the scratchpad under '## Reviewer Output'. Please finalise docs/research/<slug>.md (Status: Final), route through Review for the commit gate, then commit and push."*

**What Archivist does**:
1. Updates `Status` to `Final`.
2. Routes through **Review** agent for commit gate.
3. Commits: `docs(research): add final synthesis — <topic title>  Closes #<issue>`.
4. Returns control to Executive Researcher.

**Gate before advancing**: commit is pushed; GitHub issue is updated.

---

### Phase 7 — Notify

**Agent**: Executive Researcher → Executive Docs  
**Invocation prompt**: *"Research on [topic] is complete and committed. Please review whether any guides or top-level docs should be updated to reflect the findings."*

Update the GitHub issue with a comment linking to the committed document.
Close the issue or move to the next phase if follow-on work is needed.

---

## Documentation Workflow

Triggered when guides, AGENTS.md files, top-level docs, or MANIFESTO.md need to be updated.
Orchestrated by **Executive Docs**.

```
Orient → Audit → Draft → Validate against MANIFESTO.md → Review → Commit
```

### Key Gates

| Gate | Criteria |
|------|----------|
| Before drafting | Changed triggers identified; `MANIFESTO.md` read; session scratchpad checked |
| Before finalising | No guardrail or constraint silently removed; no new axiom added without grounding |
| Before committing | Routed through **Review** agent; **MANIFESTO.md** changes require explicit user instruction |

---

## Scripting Workflow

Triggered when a task has been done >2 times interactively.
Orchestrated by **Executive Scripter**.

```
Audit scripts/ → Identify gap → Write or extend → Dry-run → Update scripts/README.md → Review → Commit
```

See [`docs/guides/programmatic-first.md`](programmatic-first.md) for the full decision criteria
and [`scripts/README.md`](../../scripts/README.md) for script conventions.

---

## Gates Reference

A gate is a set of criteria that must be satisfied before an agent or human may advance to the
next phase of a workflow. Gates enforce the **contraction** side of expansion → contraction:
they prevent unfinished work from propagating forward.

### Gate Levels

| Level | Enforced by | Examples |
|-------|------------|---------|
| **Phase gate** | Agent checklist (self-enforced) | "Scout output present before synthesizing" |
| **Quality gate** | Review agent | "No unsupported claims; consistent with MANIFESTO.md" |
| **Commit gate** | Review + GitHub agents | "Reviewed and approved before any push" |
| **Human gate** | Explicit checkpoint in workflow | "Human confirms scope before Scout runs" |

### Research Workflow Gate Summary

| Phase | Gate criteria |
|-------|--------------|
| Frame | Research question written; deliverables identified; no duplicate issue |
| Scout | ≥3–5 sources; no synthesis; takeback handoff received |
| Synthesize | Draft exists; deliverables addressed or deferred; no raw notes |
| Review | Reviewer verdict = Approved |
| Archive | Commit pushed; GitHub issue updated |

### Documentation Workflow Gate Summary

| Phase | Gate criteria |
|-------|--------------|
| Draft | Triggers identified; MANIFESTO.md read |
| Finalise | No guardrails silently removed; new axioms grounded in MANIFESTO.md |
| Commit | Review agent approved; MANIFESTO.md changes have user instruction recorded |

---

## GitHub Issue Conventions

Agents use GitHub issues and comments as a **permanent record** — "showing their work" durably,
independent of session scratchpads which are ephemeral.

### Conventions

| Action | Convention |
|--------|-----------|
| Starting work | Comment on the issue: "Beginning Phase 1 — Orient. Branch: `feat/...`" |
| Phase transition | Comment: "Phase N complete. [Brief summary]. Proceeding to Phase N+1." |
| Human checkpoint | Comment: "Human review requested. [What to review + decision needed]." |
| Completing work | Comment with link to committed artifact. Close or move issue to next milestone. |

### Issue Fields for Research Issues

- **Title**: `[Research] <topic>`
- **Label**: `research`
- **Linked branch**: `feat/issue-<N>-<slug>`
- **Assignee**: agent or human responsible for the current phase

---

## Human Review Checkpoints

Explicit points where an agent must stop and wait for human input before continuing.

| Workflow | Checkpoint | What to review |
|----------|-----------|---------------|
| Research | After Frame phase | Is the research question correctly scoped? Are the gate deliverables right? |
| Research | After Review phase | Review the Reviewer's findings before approving archive |
| Research | Before MANIFESTO.md update | Explicit approval required for any MANIFESTO.md changes |
| Documentation | Any MANIFESTO.md edit | Must have explicit user instruction on record |
| Scripting | Before scripts that delete files | Confirm the `--dry-run` output looks correct |
| Any | Ambiguous or irreversible action | Stop and ask; do not proceed under assumption |

---

## Prompt Library

Standard invocation prompts for recurring handoffs. Copy-paste these when delegating to agents
in Copilot Chat or in handoff `prompt:` fields.

### Research Workflow Prompts

**Start a research session:**
```
@Executive Researcher Please begin a research session on [topic]. 
The research question is: [question]. 
Seed references from OPEN_RESEARCH.md: [paste relevant section].
```

**Delegate to Scout:**
```
Please survey [topic] and catalogue all relevant sources, links, and raw findings 
into the active session scratchpad under '## Scout Output'. Do not synthesize — 
gather only. Seed references: [URLs].
```

**Delegate to Synthesizer:**
```
Raw sources have been catalogued in the session scratchpad under '## Scout Output'. 
Please synthesize into a structured research draft in docs/research/<slug>.md 
following the expansion→contraction pattern. Gate deliverables: [D1, D2, D3].
```

**Delegate to Reviewer:**
```
A research synthesis draft is ready for review at docs/research/<slug>.md. 
Please validate against endogenic methodology standards and flag any gaps, 
unsupported claims, or contradictions. Gate deliverables: [D1, D2, D3].
```

**Delegate to Archivist:**
```
Research is reviewed and approved (verdict in scratchpad under '## Reviewer Output'). 
Please finalise docs/research/<slug>.md (Status: Final), route through Review for 
the commit gate, commit, and push. Closes #[issue-number].
```

### Scripting Workflow Prompts

**Spawn a new agent scaffold:**
```
@Executive Scripter Please run: 
uv run python scripts/scaffold_agent.py \
  --name "[Name]" \
  --description "[One-sentence description ≤ 200 chars]" \
  --posture [readonly|creator|full] \
  --area [area] \
  --dry-run
```

### General Prompts

**Commit approved changes:**
```
@GitHub Please commit the following approved changes to the current branch:
Files: [list]
Commit message: [type(scope): description]
[Closes #N if applicable]
```

**Request review:**
```
@Review Please review the changed files against AGENTS.md constraints 
before committing. Changed files: [list].
```

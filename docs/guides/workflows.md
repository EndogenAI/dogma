# Agent Workflows

Formalized workflows for the EndogenAI project. Each workflow defines the sequence of agents,
gates that must pass before advancing, human review checkpoints, and GitHub issue conventions
for showing work permanently.

The overarching pattern at every level of every workflow is **expansion → contraction**:
expand broadly during discovery, then contract into precise, durable outputs. This maps
directly to design thinking methodology and is the endogenic approach to all knowledge work.

---

## Contents

- [Handoff Architecture](#handoff-architecture)
- [Research Workflow](#research-workflow)
- [Documentation Workflow](#documentation-workflow)
- [Scripting Workflow](#scripting-workflow)
- [Multi-Workflow Orchestration](#multi-workflow-orchestration)
- [Fleet Management Workflow](#fleet-management-workflow)
- [Project Management Workflow](#project-management-workflow)
- [Gates Reference](#gates-reference)
- [GitHub Issue Conventions](#github-issue-conventions)
- [Human Review Checkpoints](#human-review-checkpoints)

---

## Handoff Architecture

Three interlocking patterns govern how agents hand off to each other. Together they produce
**value coherence** across the fleet — agents produce consistent, well-grounded outputs not
because they share a single rule, but because each layer encodes the same context and passes
it forward in denser form.

### 1. Evaluator-Optimizer Loop

Executive agents have handoff buttons that target **themselves** — one per phase boundary.
After a sub-agent completes its task and returns control, the executive triggers the evaluator-optimizer loop handoff to enter a deliberate review step before deciding the next delegation.

```
Human → Executive
           ↓ (delegate)
        Sub-agent A
           ↓ (takeback)
        Executive  ← evaluator-optimizer loop fires here: "✓ A done — review & decide"
           ↓ (delegate)
        Sub-agent B
           ↓ (takeback)
        Executive  ← evaluator-optimizer loop fires here: "✓ B done — review & decide"
           ↓
        Review → GitHub
```

**Why this matters**: the evaluator-optimizer loop pre-fills a prompt that orients the executive to
the just-completed output and the decision to be made. It enforces a review pause that prevents
sub-agent output from propagating unchecked into the next phase.

**Authoring rule**: every executive agent should have one evaluator-optimizer loop handoff per phase boundary,
labeled `✓ <Phase> done — review & decide`. The prompt should name where to find the output
and what the gate criteria are.

### 2. Prompt Enrichment Chain

Each delegation level enriches the prompt with progressively denser project context:

```
Human           sparse intent
    ↓
Executive       reads scratchpad + OPEN_RESEARCH.md + AGENTS.md
                → emits a richer, grounded, scoped prompt
    ↓
Sub-agent       reads specialist sources + executive prompt
                → emits a precisely targeted instruction
    ↓
Specialist      executes with full context
```

This is the endogenous-first principle in practice. Context already encoded in the repo
(guides, prior session scratchpad, AGENTS.md guardrails) is absorbed at each level and
re-emitted in the next delegation — so work at the leaves is grounded in the full project
knowledge base, not just the human's initial message.

**Implication for prompt authoring**: handoff `prompt:` fields should leave room for the
receiving agent to apply its own encoded knowledge. Specific enough to convey context;
general enough not to over-constrain.

### 3. Quasi-Encapsulated Sub-Fleets

Sub-agents default to **returning to their executive** (takeback), but may escalate directly
to another agent in exceptional cases — when the executive's context is insufficient or the
issue crosses fleet boundaries.

| Route | When to use |
|-------|-------------|
| `Sub-agent → Executive` | Default: always return for the review gate |
| `Sub-agent → Executive Docs` | Exceptional: output directly implies a doc change the executive can't handle |
| `Sub-agent → Review` | Exceptional: quality issue requiring an immediate gate before any further work |

**Anti-patterns**:
- **Full encapsulation** — sub-agents can never escalate: too rigid, breaks on edge cases.
- **Free-chaining** — sub-agents route freely to any next agent: loses executive oversight.

The hybrid model gives fleets quasi-autonomy while keeping the executive in oversight as the
default path.

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

**Three-pass model**:

```
Pass 1 — Per-source synthesis  (one Synthesizer invocation per source, parallelisable)
    ↓
Pass 2 — Link graph             (scripted: uv run python scripts/link_source_stubs.py)
    ↓
Pass 3 — Issue synthesis        (one Synthesizer invocation, cross-source conclusions only)
```

#### Pass 1 — Per-Source Synthesis

**One Synthesizer invocation per source.** Each invocation:
1. Receives a brief naming one source slug and the research question.
2. Reads the **entire** `.cache/sources/<slug>.md` (the full cached distillation — not a sample).
3. Writes a complete synthesis report to `docs/research/sources/<slug>.md`.

The output is a research-quality academic synthesis report, not a summary or an index card:
- `## Citation` — full bibliographic reference (APA or equivalent)
- `## Research Question Addressed` — how this source maps to EndogenAI's research questions
- `## Theoretical / Conceptual Framework` — paradigm or model the source uses (N/A if not applicable)
- `## Methodology and Evidence` — how evidence is structured (methodology, datasets, design, code); direct quotes
- `## Key Claims` — 10–20 bullets each grounded in a direct quote; dense sources warrant 20
- `## Critical Assessment` — evidence quality rating (`strong | moderate | weak | opinion | documentation`), limitations, adoption risks
- `## Connection to Other Sources` — relative links to other `docs/research/sources/` files with relationship notes
- `## Relevance to EndogenAI` — editorial Adopt / Adapt / Reject recommendation naming specific files

Because each invocation is isolated to one source, multiple Synthesizers can run in parallel — one per source — to eliminate context rot across a large source list.

**Pass 1 invocation prompt**:
*"You are doing a Pass 1 single-source synthesis. Source: [slug]. Cache path: .cache/sources/[slug].md. Research question: [question]. Read the full cache file and write a complete academic synthesis report to docs/research/sources/[slug].md following the 8-section format in docs/research/sources/README.md. Include an evidence quality rating in the frontmatter (evidence_quality field) and in ## Critical Assessment. Minimum 100 lines."*

#### Pass 2 — Link Graph (scripted)

After all Pass 1 invocations are complete, the Executive Researcher runs:

```bash
uv run python scripts/link_source_stubs.py
```

This scans issue synthesis files for relative links to source synthesis files and writes bidirectional `## Referenced By` entries. Never populate `## Referenced By` manually.

#### Pass 3 — Issue Synthesis

**One Synthesizer invocation.** It:
1. Reads all per-source synthesis documents (not the raw Scout notes — the source syntheses are the input).
2. Writes a contraction outline in the scratchpad (core finding, 2–3 cross-source takeaways, recommended path forward) before drafting.
3. Drafts `docs/research/<topic-slug>.md` with cross-source conclusions only — **no source content re-summarised inline**.
4. References source synthesis documents via relative links.
5. Sets `Status: Draft — pending review`.

**Pass 3 invocation prompt**:
*"You are doing a Pass 3 issue synthesis. Topic: [topic]. Source synthesis docs: [list of docs/research/sources/<slug>.md paths]. Gate deliverables: [D1, D2, D3]. Read all source synthesis documents, write a contraction outline in the scratchpad, then draft docs/research/[topic-slug].md."*

**Research Output Structure**:
```
docs/research/
  sources/
    <slug>.md          ← per-source synthesis (full analysis, isolated, committed)
  <topic-slug>.md      ← issue synthesis (cross-source conclusions only, committed)
  OPEN_RESEARCH.md     ← research queue
.cache/sources/
  manifest.json        ← fetch manifest (committed)
  <slug>.md            ← raw HTML→Markdown distillation (gitignored, regenerable)
```

**Gate before advancing**: all per-source synthesis docs exist and are complete (≥100 lines, all 8 sections present, evidence quality rating set, ≥10 key claims with quotes, relevance names specific EndogenAI files); linking script has run; issue synthesis draft exists; all gate deliverables addressed or explicitly deferred; no raw Scout notes in draft; issue synthesis references source synthesis docs via relative links.

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

## Multi-Workflow Orchestration

Triggered when a request spans two or more executive agents, or when phases have inter-agent
dependencies that need explicit sequencing. Orchestrated by **Executive Orchestrator**.

For complex sessions where the scope is unclear before execution, first invoke
**Executive Planner** to produce a structured plan, then hand it to Orchestrator.

```
Plan (Executive Planner) → Approve plan → Orchestrate phases (Executive Orchestrator)
  └── Phase 1: Delegate to domain executive → gate → Phase 2 → ... → Review → Commit → Summarise
```

### When to invoke

| Situation | Action |
|-----------|--------|
| Request touches ≥2 executive domains | Start with Executive Orchestrator |
| Request is ambiguous or scope is unclear | Start with Executive Planner, then Orchestrator |
| Single-domain work (e.g., pure research) | Go directly to the domain executive |

### Key Orchestration Rules

1. **Write a plan before delegating**: Orchestrator must produce `## Orchestration Plan` in the scratchpad before any phase delegation.
2. **One phase at a time**: phases are sequential unless explicitly marked parallelisable.
3. **Gate deliverables are concrete**: a gate deliverable is a committed file or a confirmed GitHub state — not "phase done".
4. **Close the loop**: every session ends with `## Session Summary` + `uv run python scripts/prune_scratchpad.py --force`.

### Gate Summary

| Gate | Criteria |
|------|----------|
| Before Phase 1 | Orchestration plan written; phases + gates documented |
| Between phases | Prior phase output confirmed committed; deliverables verified |
| Session close | All phases done; session summary written; scratchpad pruned |

---

## Fleet Management Workflow

Triggered when the agent fleet needs to be updated: new agents added, existing agents corrected,
or stale agents deprecated. Orchestrated by **Executive Fleet**.

```
Orient → Audit → Act (create | update | deprecate) → Update README → Review → Commit
```

### Triggers

- A gap in the fleet is identified during an active session.
- A new workflow requires a new specialist agent.
- An agent's guardrails, handoffs, or tool list are out of date.
- A previously useful agent is no longer in use.

### Key Rules

- **Always use `scaffold_agent.py`** for new agents — never author from scratch.
- **Always dry-run first**: `uv run python scripts/scaffold_agent.py ... --dry-run`.
- **No TODO placeholders** in a completed agent file.
- **Deprecate, don't delete**: move stale agents to `.github/agents/deprecated/`.
- **Update `README.md`** after every fleet change.

### Gate Summary

| Gate | Criteria |
|------|----------|
| Before creating | Posture decided; description ≤200 chars; `--dry-run` reviewed |
| Before committing | No TODO placeholders; tool list matches posture; handoff targets are real agents; README updated |
| Commit | Routed through Review agent; commit type `feat(agents):` |

---

## Project Management Workflow

Triggered periodically or when a release is approaching. Orchestrated by **Executive PM**.

```
Orient → Audit (issues, changelog, community health) → Triage → Update → Review → Commit
```

### Surfaces Maintained

| Surface | Tool | Cadence |
|---------|------|---------|
| Issue triage | `gh issue` | Per session |
| Milestone management | `gh milestone` | Per release |
| Changelog | `CHANGELOG.md` | Per merge to `main` |
| Community health files | `README.md`, `CONTRIBUTING.md`, etc. | Per quarter |
| Label taxonomy | `gh label` | As fleet evolves |
| Release notes | `gh release` | Per tag |

### Key Rules

- **Use Keep a Changelog format** for `CHANGELOG.md`.
- **Map Conventional Commits to sections**: `feat` → Added, `fix` → Fixed, `docs`/`chore` → Changed.
- **Label every open issue** — no label = invisible in triage.
- **Do not edit `MANIFESTO.md`** — that is Executive Docs territory.

### Gate Summary

| Gate | Criteria |
|------|----------|
| Before acting | Audit written to scratchpad; self-loop review done |
| Before committing | All community health files present; changelog covers all merged PRs; issues labelled |
| Commit | Routed through Review agent; commit type `chore(repo):` |

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

**Delegate to Synthesizer (Pass 1 — single source):**
```
You are doing a Pass 1 single-source synthesis.
Source: [slug]. Cache path: .cache/sources/[slug].md.
Research question: [question].
Read the full cache file and write a complete academic synthesis report to
docs/research/sources/[slug].md following the 8-section format.
Minimum 100 lines; include evidence_quality in frontmatter and ## Critical Assessment.
```

**Delegate to Synthesizer (Pass 3 — issue synthesis):**
```
You are doing a Pass 3 issue synthesis. Topic: [topic].
Source synthesis docs: [list of docs/research/sources/<slug>.md paths].
Gate deliverables: [D1, D2, D3].
Read all source synthesis documents, write a contraction outline in the scratchpad,
then draft docs/research/[topic-slug].md with cross-source conclusions only.
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

### Orchestration & Planning Prompts

**Start a multi-workflow session:**
```
@Executive Orchestrator Please coordinate the following session:
[describe the full scope]
Begin by writing an Orchestration Plan in the session scratchpad before delegating.
```

**Pre-plan a complex request:**
```
@Executive Planner Please decompose the following request into a structured plan
with phases, gates, agent assignments, and dependency ordering.
Do not begin executing — return the plan for approval.
Request: [describe]
```

### Fleet Management Prompts

**Audit the fleet:**
```
@Executive Fleet Please run a fleet compliance audit.
Check all .agent.md files against AGENTS.md standards and report findings
to the session scratchpad under '## Fleet Audit'. Do not apply fixes yet — 
audit first, then pause for review.
```

**Create a new agent:**
```
@Executive Fleet Please create a new agent:
Name: [Name]
Description: [One-sentence description ≤ 200 chars]
Posture: [readonly|creator|full]
Run scaffold_agent.py with --dry-run first, then create if approved.
Fill in all TODO sections before routing to Review.
```

### Project Management Prompts

**Run a PM health check:**
```
@Executive PM Please run a repository health audit.
Check: open issues without labels, milestone drift, changelog gaps,
and community health file completeness.
Write findings to the scratchpad under '## PM Audit' and pause for review.
```

**Update the changelog:**
```
@Executive PM Please update CHANGELOG.md with all merged PRs since the last entry.
Use Keep a Changelog format. Map conventional commit types to changelog sections.
Route changes through Review before committing.
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

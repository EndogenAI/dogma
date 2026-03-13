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
- [Issue Seeding Workflow](#issue-seeding-workflow)
- [Research Workflow](#research-workflow)
  - [CI Gates for Research Documents](#ci-gates-for-research-documents)
- [Implementation Workflow](#implementation-workflow)
- [Documentation Workflow](#documentation-workflow)
- [Scripting Workflow](#scripting-workflow)
- [Automation Workflow](#automation-workflow)
- [Multi-Workflow Orchestration](#multi-workflow-orchestration)
- [Fleet Management Workflow](#fleet-management-workflow)
- [Project Management Workflow](#project-management-workflow)
- [PR Review Response Workflow](#pr-review-response-workflow)
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

## Issue Seeding Workflow

Converts a newly-identified capability gap into a well-seeded GitHub research issue. This
is the step that *creates* the trigger for the Research Workflow — a seeded issue, not
an empty stub. It is fast (one session, no agent delegation), endogenous-first (workspace
state is checked before any external fetch), and produces a durable record that Scout,
Synthesizer, and Reviewer can work from without rediscovering context.

```
Identify gap → Check workspace → Pre-flight fetch → Frame issue → Create issue → Verify
```

### Trigger

An agent or human notices a missing primitive, capability, or encoded knowledge area.
Common signals:
- A task is performed repeatedly without a script, guide, or agent covering it
- A VS Code / GitHub Copilot capability exists in the ecosystem that the project doesn't use
- A research question arises mid-session that cannot be answered from `docs/research/`
- An external open standard or tool is adopted by the broader community but not encoded here

### Phase 1 — Check Workspace (Endogenous-First)

**Agent**: Any (Orchestrator, or directly in the active session)

Before fetching anything externally, confirm what is already encoded:

```bash
# Is there already an issue or research doc on this topic?
gh issue list --state all | grep -i "<keyword>"
find docs/research/ -name "*.md" | xargs grep -l "<keyword>" 2>/dev/null
# Is the capability already present in the workspace?
find . -name "SKILL.md" -o -name "*.agent.md" | xargs grep -l "<keyword>" 2>/dev/null
```

**Gate before advancing**: confirm no duplicate issue and no existing coverage in
`docs/research/` or the agent fleet. If coverage exists, skip to Issue Seeding or stop.

### Phase 2 — Pre-Flight Fetch

**Agent**: Active session (or Research Scout if topic is broad)

Fetch the minimal set of primary sources needed to write an informed issue body. Target:
- Official docs for the capability (e.g., VS Code docs page, open standard specification)
- A community or reference implementation (e.g., `github/awesome-copilot`, `anthropics/skills`)
- One overview or comparison resource

Use the source cache check first:

```bash
# Check if primary source is already cached
uv run python scripts/fetch_source.py <url> --check
```

**What to gather** (keep it light — you are seeding, not synthesizing):
- What the capability is and what problem it solves
- How it fits relative to existing project primitives
- An initial list of 3–7 research questions the full synthesis will need to answer
- 5–10 candidate use cases or adoption areas specific to this project
- A seed sources table (name + URL + type)

**Gate before advancing**: at least 2 primary sources read; seed sources table populated;
research questions drafted; no synthesis attempted yet.

### Phase 3 — Frame the Issue Body

Write the issue body as a Markdown file before creating the issue (never `--body "..."`
with multi-line content — always `--body-file <path>`):

```
.tmp/issue-<slug>-body.md
```

**Required sections**:

| Section | Purpose |
|---------|--------|
| `## Research Goal` | What gaps this issue closes; endogenic alignment statement |
| `## Background` | 3–5 paragraph summary from pre-flight fetch |
| `## Candidate Areas` | Prioritised table of adoption candidates (Tier 1 / Tier 2) |
| `## Key Research Questions` | Numbered list (Q1–Q7) of questions the synthesis must answer |
| `## Seed Sources` | Table of name + URL + type for all pre-flight sources |
| `## Proposed Deliverables` | Checkbox list of concrete output files (`- [ ] path`) |
| `## Labels` | Inline label list at the end of the body |

The issue body is the **scout brief + research frame in one document**. When the Research
Workflow begins, the Researcher reads it as the starting context — so it must be dense
enough to stand alone.

**Gate before advancing**: all 7 sections present; research questions are specific
(not generic); seed sources include at least the official docs URL; deliverables
are concrete file paths, not vague themes.

### Phase 4 — Create & Verify

```bash
gh issue create \
  --title "Research: <Short descriptive title>" \
  --body-file .tmp/issue-<slug>-body.md \
  --label "type:research" \
  --label "priority:<level>" \
  --label "area:<area>"

# Verify
gh issue view <N> --json number,title,labels -q '"#\(.number): \(.title)\nLabels: \([.labels[].name] | join(", "))"'
```

### Key Rules

- **Endogenous-first always**: workspace check precedes any external fetch.
- **Seed, don't synthesize**: the issue body captures what is known, not what is concluded.
  Synthesis happens later in the Research Workflow.
- **Dense enough to stand alone**: the Researcher and Scout reading this issue in a future
  session must not need to re-fetch the overview sources — the background section prevents that.
- **Research questions drive Scout scope**: poorly-framed Q items produce unfocused Scout output.
  Each Q should be answerable with a specific source type (paper / docs / code / community).
- **Deliverables are file paths**: `- [ ] docs/research/agent-skills-integration.md` not
  `- [ ] research this topic`.
- **Always `--body-file`**: never `--body "..."` with multi-line Markdown — shell quoting
  and backtick interpolation corrupt or hang.

### Gate Summary

| Gate | Criteria |
|------|----------|
| Before fetching | Workspace check done; no duplicate issue or research doc found |
| Before framing | ≥2 primary sources read; seed sources table populated; Qs drafted |
| Before creating | All 7 body sections present; deliverables are concrete file paths |
| After creating | Verified with `gh issue view #N`; labels confirmed |

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

#### Large-Corpus Sweep (when corpus > 20 documents)

When scouting a corpus of more than ~20 documents, insert a **sweep step** before full scouting to allocate Scout depth proportionally:

1. **Organizational Sweep** — delegate to Explore agent: produce a triage table with one row per document:
   - *Recency tier*: Old (> 6 months) / Mid / Recent (< 4 weeks)
   - *Relevance to each target* (H / M / L / None) + one-line rationale
   - *Already cited in target papers?* (Yes / Partial / No)
   - *Recommended scout depth*: Thorough / Skim / Skip

2. **Depth allocation rule**: Thorough = full read; Skim = headings + key findings only; Skip = no scouting. Prioritize: high relevance + not yet cited + older (less likely to have been backpropagated).

3. **Recency + citation signal**: Older documents are *more likely* to contain uncited findings — primary papers are authored early and updated sporadically. Combine recency tier with citation status (not just relevance) to identify the highest-value targets.

The sweep table is the Scout's guide. Commit it to `docs/plans/` before delegating Scout work so the depth allocations are reviewable.

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

### CI Gates for Research Documents

Every `docs/research/*.md` (except `OPEN_RESEARCH.md`) is validated in CI by the `lint:` job. Two failure modes to know before committing research docs:

#### 0. Post-Push CI Verification (all workflows)

**After every `git push` to a PR branch, CI status must be verified before requesting review.**

```bash
# Monitor CI for the current branch
gh run list --limit 3
```

CI jobs on this repo (`Tests` workflow):

| Job | What it checks |
|-----|----------------|
| `test` | pytest + coverage (fails if tests fail) |
| `lint` | ruff check, ruff format --check, validate_synthesis.py |
| `links` | lychee dead-link check (fails on non-200 responses) |
| `All tests passed` | Aggregate gate — blocks merge if any above fails |

**Do not re-request Copilot review if CI is red.** Fix CI first. See common failure modes below.

> **Common failure modes and fixes**:
> - Lychee non-200 response (e.g. HTTP 202 Accepted): add URL to `.lycheeignore` with reason
> - `ruff format` failure: `uv run ruff format scripts/ tests/` then re-commit
> - `validate_synthesis.py` failure: add `## 2. Hypothesis Validation` and `## 3. Pattern Catalog` headings to the failing research doc

#### 1. `validate_synthesis.py` — D4 required headings

The `validate_synthesis.py` script enforces that D4 issue synthesis documents contain these exact headings (or headings whose text contains these keywords):

- `## 2. Hypothesis Validation`
- `## 3. Pattern Catalog`

Documents missing these headings fail CI. When backfilling an older document:
- Add a genuine `## 2. Hypothesis Validation` section (H1/H2/H3 claims validated from sources).
- Prefix an existing relevant section: `## 3. Pattern Catalog — <Original Title>`.

#### 2. Lychee — broken links and missing source stubs

The `links:` job runs lychee against all committed Markdown. Two common failure modes:

**Dead external URLs**: External links that are legitimately 404 (link rot, restructured sites) should be added to `.lycheeignore` at the workspace root. Do *not* remove the URL from the research doc — it is part of the citation record. Document the reason inline in `.lycheeignore`.

**Missing source stubs**: If a synthesis doc references `./sources/<slug>.md`, that file must exist in `docs/research/sources/` (committed), *not* only in `.cache/sources/` (gitignored). Copy any referenced stubs from `.cache/sources/` to `docs/research/sources/` before committing the synthesis doc.

```bash
# Check which source stubs are referenced but missing from the committed docs:
grep -r "\./sources/" docs/research/*.md | grep -v "sources/" | cut -d: -f2 | sort -u
```

---

## Implementation Workflow

Triggered when a research synthesis document in `docs/research/` reaches **Status: Final**
and contains actionable R-items (R1–R6). Converts research into committed code, docs, or
configuration changes. Orchestrated by **Executive Orchestrator**.

```
Orient → Audit R-items → Create Issues → Sprint Plan → Execute by Domain → Review → Commit → Update Synthesis
```

### Trigger

A synthesis document in `docs/research/` has `status: Final` in its frontmatter and contains
at least one R-item (recommendation) not yet implemented. A GitHub issue or Executive Handoff
note identifies the synthesis as ready for implementation.

### Phase 1 — Orient

**Agent**: Executive Orchestrator  
**Action**: Read the synthesis document in full; extract all R-items; check for existing GitHub
issues that already track any R-item.

**Gate before advancing**: synthesis doc has `status: Final`; R-item list is written to
the session scratchpad.

### Phase 2 — Audit R-items

**Agent**: Executive Orchestrator  
**Action**: For each R-item:

1. Confirm it is grounded in synthesis evidence (not a general best practice added ad hoc).
2. Assign it to a domain executive: Docs, Scripter, Automator, Fleet, or PM.
3. Estimate effort (`effort:xs/s/m/l/xl`).
4. Identify blockers or dependencies on other R-items.

R-items without direct synthesis evidence are **deferred** — they do not enter the sprint.

**Gate before advancing**: every scoped R-item has a domain and effort label; deferred items
are noted with a reason.

### Phase 3 — Create GitHub Issues

**Agent**: Executive Orchestrator (direct)  
**Action**: Create one GitHub issue per scoped R-item (or per cluster of tightly related items):

- Title: `[area/type] Short description`
- Body: R-item description + synthesis doc path + evidence quote
- Labels: `type:feature` or `type:chore`, `area:`, `priority:`, `effort:`
- Milestone: assign to the relevant milestone

**Gate before advancing**: all scoped R-item issues created and confirmed (`gh issue list`).

### Phase 4 — Sprint Plan

**Agent**: Executive Orchestrator  
**Action**: Write `## Implementation Sprint Plan — <topic>` to the session scratchpad. Group
R-items by domain executive; identify an execution sequence (dependencies first).

**Gate before advancing**: sprint plan vetted; all domain executives identified; phases
ordered.

### Phase 5 — Execute by Domain

**Agent**: Domain executives (Docs, Scripter, Automator, Fleet, PM) — one at a time  
**Delegation prompt must include**: R-item list with numbers and descriptions; synthesis doc
path; GitHub issue numbers; any predecessor outputs.

Each domain phase runs sequentially unless the sprint plan explicitly marks phases as
parallelisable.

**Gate before advancing**: each domain phase's deliverables committed before the next domain
phase begins.

### Phase 6 — Review & Commit

**Agent**: Review → GitHub  
**Action**: Route all changed files through Review agent. Commit with
`type(scope): description, Closes #N`.

### Phase 7 — Update Synthesis Status

**Agent**: Executive Docs (or Orchestrator direct)  
**Action**: Update the synthesis document frontmatter:

```yaml
implementation_status: complete  # or: partial
implemented_in: feat/<branch-slug>
```

Add a `## Implementation Notes` section below the synthesis body listing which R-items were
implemented, which were deferred, and why.

### Key Rules

- Only R-items supported by synthesis evidence enter the sprint.
- R-items that contradict `MANIFESTO.md` require explicit user instruction before being
  implemented.
- The synthesis doc is the source of truth — do not add scope not present in the R-items
  without a new research cycle.
- Every implementation sprint leaves the synthesis doc in a better state than it found it
  (updated status, deferred items documented).

### Gate Summary

| Gate | Criteria |
|------|----------|
| Before auditing | Synthesis doc committed with `status: Final` |
| Before sprint plan | All R-items assessed; deferred items documented with reason |
| Before executing | Sprint plan in scratchpad; all GitHub issues created and labelled |
| Between domain phases | Prior phase committed and confirmed |
| Before updating synthesis | All R-items either implemented or explicitly deferred |
| After committing | Synthesis `implementation_status` updated; PR comment or issue closed |

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

## Automation Workflow

Triggered when a file watcher, pre-commit hook, CI task, or GitHub Actions workflow needs to
be created or updated. Orchestrated by **Executive Automator**.

```
Orient → Identify Trigger → Choose Surface → Design → Implement → Dry-run → Register → Review → Commit
```

### When to Invoke

| Situation | Action |
|-----------|--------|
| A manual check is run before every commit | Add as pre-commit hook |
| A validation could silently break without CI | Add as CI workflow |
| A script is run manually more than twice | Encode as pre-commit or CI task |
| An output needs to update whenever a file changes | Add as VS Code file-watcher task |
| A GitHub event should trigger automated actions | Add as GitHub Actions workflow |

### Surfaces Maintained

| Surface | Location | When it runs |
|---------|----------|--------------|
| Pre-commit hooks | `.pre-commit-config.yaml` | Every `git commit` |
| CI workflows | `.github/workflows/` | Push / PR events |
| VS Code tasks | `.vscode/tasks.json` | On demand or file watch |
| GitHub Actions | `.github/workflows/` | GitHub events |

### Key Rules

- **Dry-run before enabling**: scripts use `--dry-run`; pre-commit hooks test with
  `pre-commit run --hook-stage manual <hook-id>` before adding to `default_install_hook_types`.
- **No double-run anti-pattern**: CI must not repeat checks already enforced by pre-commit.
  If a check runs in pre-commit, CI only needs to verify the hook ran, not re-execute it.
- **Register new automation**: every new pre-commit hook or CI check must be documented in
  `scripts/README.md` or the relevant `.github/workflows/` file header.
- **VS Code tasks get tested**: new `.vscode/tasks.json` entries must be manually triggered
  and verified before committing.
- **Gate: local before CI**: all automation must pass locally before it is added to a CI
  workflow.

### Gate Summary

| Gate | Criteria |
|------|----------|
| Before implementing | Trigger identified; surface (pre-commit / CI / VS Code task) decided |
| Before enabling | Dry-run passed locally; no duplication with existing automation |
| Before committing | Routed through Review agent; documentation updated |

---

## Multi-Workflow Orchestration

Triggered when a request spans two or more executive agents, or when phases have inter-agent
dependencies that need explicit sequencing. Orchestrated by **Executive Orchestrator**.

For complex sessions where the scope is unclear before execution, first invoke
**Executive Planner** to produce a structured plan, then hand it to Orchestrator.

```
Plan (Executive Planner) → Approve plan → Orchestrate phases (Executive Orchestrator)
  └── Phase 1: delegate → Review gate → Phase 2: delegate → Review gate → ... → Commit → Summarise
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
3. **Review gate between every domain phase**: after each domain phase completes, invoke the Review agent. The next domain phase may not begin until Review returns APPROVED. Record the verdict in the scratchpad under `## Review Output`.
4. **Gate deliverables are concrete**: a gate deliverable is a committed file or a confirmed GitHub state — not "phase done".
5. **Close the loop**: every session ends with `## Session Summary` + `uv run python scripts/prune_scratchpad.py --force`.

### Gate Summary

| Gate | Criteria |
|------|----------|
| Before Phase 1 | Orchestration plan written; phases + gates documented |
| Between phases | Prior phase deliverables committed; Review agent invoked; APPROVED verdict logged to scratchpad under `## Review Output`; both required before next phase starts |
| Before final commit | Review APPROVED for all phases; GitHub agent handles commit/push |
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
| GitHub Project (Backlog) | `gh project` | Per session |
| Milestone management | `gh milestone` | Per release |
| Changelog | `CHANGELOG.md` | Per merge to `main` |
| Community health files | `README.md`, `CONTRIBUTING.md`, etc. | Per quarter |
| Label taxonomy | `uv run python scripts/seed_labels.py` | As taxonomy evolves |
| Release notes | `gh release` | Per tag |

### Key Rules

- **Use Keep a Changelog format** for `CHANGELOG.md`.
- **Map Conventional Commits to sections**: `feat` → Added, `fix` → Fixed, `docs`/`chore` → Changed.
- **Label every open issue** — no label = invisible in triage.
- **Do not edit `MANIFESTO.md`** — that is Executive Docs territory.

### Planning Model

This project uses **Kanban over Scrum**. Irregular contributor cadence — including ad-hoc agent sessions — is incompatible with fixed sprint cycles. Work items flow continuously through the board; no sprint planning ceremonies or retrospectives are required. A Scrumban hybrid (Kanban day-to-day, retrospective per release milestone) is appropriate if a regular versioned release cadence is adopted.

### Agent Fleet as Team Topology

The agent fleet maps onto Team Topologies' four-team-type framework:

| Team Topologies type | Role |
|---|---|
| Stream-aligned | Human maintainers — own the product and drive direction |
| Enabling | Executive agents (Researcher, Docs, Scripter) — task-scoped capability augmentation |
| Complicated Subsystem | Research Scout, Synthesizer, domain specialist agents — deep expertise, on-demand |
| Platform | GitHub agent, Review agent — consumed X-as-a-Service |

Default interaction mode: **X-as-a-Service** (consume agent output via defined handoff contracts). Switch to **Collaboration** only when discovering new capabilities on a first-run workflow.

Agents are runtime instances of function contracts, not standing team members. Define agent SLAs — e.g., "Research Scout returns ≤ 2,000 tokens within one session" — not sprint assignments.

### Three-Tier Planning Hierarchy

Three planning tiers are active in this repo, scoped to different time horizons:

| Tier | Artifact | Scope | State |
|------|----------|-------|-------|
| Tactical | `.tmp/<branch>/<date>.md` | Live session state | Ephemeral (gitignored) |
| Operational | `docs/plans/YYYY-MM-DD-<slug>.md` | Committed workplans | Durable per-session |
| Strategic | GitHub Milestones | Longer-horizon goals | Publicly visible |

Use the correct tier for each artifact. Do not commit session-scoped scratchpad content to `docs/plans/`; do not track strategic milestones in ephemeral scratchpads.

### Architecture Decision Records

ADRs live in `docs/decisions/` (directory to be created on first ADR). An ADR is warranted when a decision has non-obvious tradeoffs, is difficult to reverse, or would be confusing to a future agent or contributor without prior context.

First ADRs planned:
- Why `uv run` over `python` directly
- Why Kanban-not-Scrum
- Why the XML hybrid agent instruction format

Use the Nygard format (Title, Status, Context, Decision, Consequences), targeting ≤ 30 lines per record. Optimise for future agent readability — assume no session context.

### Gate Summary

| Gate | Criteria |
|------|----------|
| Before acting | Audit written to scratchpad; self-loop review done |
| Before committing | All community health files present; changelog covers all merged PRs; issues labelled |
| Commit | Routed through Review agent; commit type `chore(repo):` |

---

## PR Review Response Workflow

Triggered when a PR receives a review with requested changes or inline comments. Tool: `scripts/pr_review_reply.py`.

```
Triage → Fix → Reply → Resolve → Commit → Re-request review
```

### Steps

| Step | Action | Tool |
|------|--------|------|
| **Triage** | Read all review comments; classify as: Fix Now / Defer / Decline | `gh pr view --comments` |
| **Fix** | Address each "Fix Now" item; route changes through **Review** agent | File tools |
| **Reply** | Post a reply on each inline thread noting the fix commit SHA | `scripts/pr_review_reply.py` |
| **Resolve** | Mark each addressed thread as resolved | `scripts/pr_review_reply.py --resolve` |
| **Commit** | Route all fixes through **Review** then **GitHub** agents | Standard commit flow |
| **Re-request review** | Re-request from the original reviewer once CI is green | `gh pr review --request <reviewer>` |

### Rules

- **Fix before replying** — do not reply until the fix is committed.
- **One reply per thread** — reference the fix commit SHA.
- **Defer/Decline requires a comment** — record reasoning before resolving.
- **SHA pinning and non-blocking items** — resolve with "Deferred to issue #N"; open the tracking issue first.
- **CI must be green before re-requesting review.**

### Checkpoints

| Gate | Condition |
|------|-----------|
| Before replying | Fix is committed and pushed |
| Before resolving | Reply references commit SHA |
| Before re-requesting review | CI is green |

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
| **Commit gate** | Review agent + Orchestrator/Docs agents | "Reviewed and approved; Orchestrator or Docs executes `git` operations after Review passes" |
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

### Issue Seeding Prompts

**Seed a new research issue from an identified gap:**
```
I've identified a gap: [describe the missing capability or knowledge area].
Please run the Issue Seeding Workflow:
1. Check the workspace for any existing coverage (issues, research docs, agent files)
2. Fetch the primary sources (official docs, open standard, reference impl)
3. Frame the issue body with all 7 required sections
4. Create the issue with correct labels and verify it
Target labels: type:research, priority:[level], area:[area]
```

**Seed from a mid-session observation:**
```
We just identified a gap while working on [topic]. Before closing this session,
please do a quick Issue Seeding pass:
- Gap: [describe gap in one sentence]
- Likely primary sources: [URL or topic hint]
- Candidate label: type:research, area:[area]
Create a seeded research issue and return the issue number.
```

---

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

### Documentation Workflow Prompts

**Update an existing guide:**
```
@Executive Docs Please update [guide name] at docs/guides/[slug].md.
Changes needed: [describe changes].
Read MANIFESTO.md and the existing guide before drafting.
Route through Review before committing.
```

**Create a new guide from a synthesis doc:**
```
@Executive Docs Please create a new guide from the synthesis doc at docs/research/[slug].md.
Target path: docs/guides/[slug].md.
The guide should encode practical workflow steps, not research findings.
Route through Review before committing.
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

**Identify scripting gaps:**
```
@Executive Scripter Please audit scripts/ against tasks done interactively this session.
List any task that qualifies for scripting under the programmatic-first criteria.
Propose a script outline for the top candidate; pause for review before implementing.
```

### Implementation Workflow Prompts

**Start an implementation sprint:**
```
@Executive Orchestrator Please start an implementation sprint for [synthesis-topic].
Synthesis doc: docs/research/[slug].md.
R-items to implement: [R1, R2, R3 — or 'all scoped items'].
Begin by auditing R-items against synthesis evidence,
then write a Sprint Plan to the scratchpad before delegating to any domain executive.
```

**Delegate R-items to a domain executive:**
```
@[Executive Domain] Please implement the following R-items from docs/research/[slug].md:
[R-item list with numbers and descriptions]
GitHub issues: [#N, #M, ...]
Route all changes through Review before committing.
Closes: [issue numbers]
```

### Automation Workflow Prompts

**Design new automation:**
```
@Executive Automator Please design automation for: [describe task].
This task has been done [N] times interactively.
Surface options to consider: pre-commit hook / CI workflow / VS Code task.
Begin with dry-run only — do not enable until I approve the design.
```

**Add a CI check:**
```
@Executive Automator Please add a CI check for: [describe check].
Relevant script or command: [command].
It should run on: [push | PR | both].
Do not duplicate any existing check that already runs in pre-commit.
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

When the plan is approved, delegate a **per-phase execution checklist** to Executive Planner before Phase 1 begins. The checklist becomes the shared acceptance specification that every execution agent (Scout, Synthesizer, Reviewer, Archivist) verifies their output against — eliminating interpretive drift across handoffs without requiring the Orchestrator to re-explain scope at each delegation.

**Continue from a prior session (session handoff):**
```
@Executive Orchestrator Please continue the session on branch [branch-slug].
Read the active scratchpad at .tmp/[branch-slug]/[YYYY-MM-DD].md before delegating anything —
specifically the ## Executive Handoff and ## Session Summary sections.
Focus for this session: [one sentence from the handoff's "Recommended Next Session" section].
Write ## Session Start with a one-paragraph orientation before proceeding.
```

> **Encoding note**: This is the standard session continuation handoff prompt. Copy-paste it
> when re-opening work on an existing branch. Replace `[branch-slug]`, `[YYYY-MM-DD]`, and
> the focus sentence. See `docs/guides/session-management.md#starting-a-new-session` for the
> full protocol.

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

---
name: prompt-archaeology
description: |
  Defines the prompt archaeology ritual: systematically mining prior session scratchpads,
  commit messages, and issue comments to surface decision rationale, failed approaches, and
  discovered constraints that should be encoded into the substrate.
  USE FOR: post-sprint review of older session artifacts (.tmp/ scratchpads, docs/sessions/
  summaries, git log, issue comments); finding constraints discovered interactively that
  should become programmatic; recovering decision rationale never encoded in guides or skills.
  DO NOT USE FOR: same-session insight capture (use session-retrospective instead);
  mid-phase check-ins; tasks where no prior session artifacts exist for the branch.
argument-hint: "branch or sprint name to mine (e.g. feat/issue-146 or milestone-9)"
governs:
  - session-retrospective
  - session-management
closes_issue: "#146"
---

# Prompt Archaeology

## Governing Axiom

This skill enacts the *Endogenous-First* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md#1-endogenous-first):

> Session artifacts — scratchpads, commit messages, issue comments, session summaries — are endogenous knowledge. Mining them before reaching outward satisfies the axiom that existing system knowledge must be exhausted before generating new tokens.

It also enacts the *Programmatic-First* principle from [`AGENTS.md`](../../../AGENTS.md#programmatic-first-principle):

> Constraints discovered interactively more than twice must be encoded programmatically before the third time. Prompt archaeology is the mechanism that catches constraints that survived two sessions interactively but were never promoted to a script, guide, or skill.

**Implements**: Issue [#146 — Implement prompt archaeology as a post-sprint ritual](https://github.com/EndogenAI/dogma/issues/146)

**Governed by**:
- [`AGENTS.md`](../../../AGENTS.md) § Session-Start Encoding Checkpoint — archaeology findings feed the encoding checkpoint for the next sprint
- [`MANIFESTO.md`](../../../MANIFESTO.md) *Endogenous-First* axiom — session artifacts are the first-order endogenous source

**Companion skill**: [`session-retrospective`](../session-retrospective/SKILL.md) — retrospective harvests this session's lessons; archaeology mines older sessions. They feed each other: retrospective findings accumulate as future archaeology targets.

**Foundation documents**:
- [`docs/research/scratchpad-architecture-maturation.md`](../../../docs/research/infrastructure/scratchpad-architecture-maturation.md) — R1 recommendation: `docs/sessions/` curated archive (the primary persistent archaeology substrate)
- [`docs/guides/session-management.md`](../../../docs/guides/session-management.md) — session lifecycle this skill extends

---

## 2. What Is Prompt Archaeology

Prompt archaeology is the practice of **systematically reviewing prior session artifacts** to recover knowledge that was generated interactively but never encoded into the substrate.

Every agent session produces ephemeral artifacts — scratchpad entries, commit message bodies, issue comments, and improvised workarounds. Most are written under context-window pressure and forgotten. Prompt archaeology treats these artifacts as a corpus to mine.

**Three categories of recoverable knowledge:**

| Category | Definition | Encoding target |
|----------|-----------|-----------------|
| **Decision rationale** | Why a path was chosen or rejected — not what was done, but why | `AGENTS.md` § When to Ask vs. Proceed; guide appendices |
| **Patterns that worked or failed** | Delegation shapes, compression tricks, retry policies — positive and negative | `SKILL.md` files; `AGENTS.md` § canonical examples |
| **Interactive constraints** | Guards, checks, or workarounds performed twice interactively without encoding | Pre-commit hooks; scripts; `AGENTS.md` guardrails |

**Canonical example**: During sprint Milestone-9, the pattern "write body to temp file and use `--body-file`" was performed interactively in three sessions before it was encoded as an `AGENTS.md` guardrail. Archaeology on those three scratchpads would have caught it after the second session.

**Anti-pattern**: Running archaeology as a box-ticking exercise without gap-analysing against the existing substrate. Surface-level "we did X" summaries are not findings — the signal is "we did X because Y, and Y is not yet encoded anywhere."

---

## 3. When to Run

**Primary trigger — post-sprint (recommended):**

Run prompt archaeology after every milestone completion, before the next sprint's planning session. The correct ordering is:

```
Sprint close → session-retrospective (current session) → prompt archaeology (prior sessions) → next sprint planning
```

**Secondary trigger — familiar-problem signal:**

Run archaeology when you encounter a problem that feels familiar but no substrate guidance exists. The absence of a guide despite a sense of familiarity is evidence that prior sessions solved it interactively without encoding.

| Trigger | Signal |
|---------|--------|
| Milestone just completed | `git log --oneline` shows ≥3 documentation commits since last milestone |
| Familiar problem, no guide | You recall solving it before but cannot cite the source |
| Repeated workaround | You have manually applied the same fix in ≥2 sessions |
| New contributor onboarding | Prior session rationale should be findable without asking |

**Do NOT run** if:
- Context window is under pressure — note the gap in the scratchpad and schedule for next session.
- The branch has no prior session artifacts (first session on a new branch).
- You are mid-phase — wait for a phase boundary.

---

## 4. Artifacts to Mine

Mine these sources in priority order — highest-signal first:

### 4.1 Active Scratchpads (`.tmp/<branch-slug>/*.md`)

Gitignored; available only during the current session. Mine before the session closes or the window compacts.

```bash
ls .tmp/<branch-slug>/
cat .tmp/<branch-slug>/<date>.md | grep -A5 "## Session Summary\|## Retrospective\|## Executive Handoff"
```

Key sections to target: `## Session Summary`, `## Executive Handoff`, `## Retrospective — *`, `## Pre-Compact Checkpoint`.

### 4.2 Archived Session Summaries (`docs/sessions/`)

Committed to git per R1 of [`scratchpad-architecture-maturation.md`](../../../docs/research/infrastructure/scratchpad-architecture-maturation.md). Naming convention: `YYYY-MM-DD-<branch-slug>-summary.md`.

```bash
ls docs/sessions/
grep -l "<branch-slug>" docs/sessions/*.md | xargs grep "Open questions\|Key findings"
```

These are the highest-quality archaeology targets: curated, structured, and querable via `scripts/query_docs.py`.

### 4.3 Commit Messages (`git log`)

Commit message bodies (not just subject lines) often carry decision rationale written under time pressure and never promoted to a guide.

```bash
git --no-pager log --oneline --since="2 weeks ago"
git --no-pager log --format="%H %s%n%b" --since="2 weeks ago" | grep -v "^$"
```

Look for: `# Why:`, `Note:`, `Fixes`, `Workaround:`, rationale sentences in commit bodies.

### 4.4 Issue Comments (`gh issue view`)

Issue comments with `## Session Summary` or `## Phase N Complete` bodies often contain the richest decision rationale, written at phase close.

```bash
gh issue list --state all --limit 50 --json number,title | jq '.[] | "\(.number) \(.title)"'
gh issue view <number> --comments | grep -A20 "Session Summary\|Phase.*Complete\|Key finding"
```

Mine closed issues from the relevant milestone — their session-close comments are archaeology gold.

---

## 5. Procedure

### Step 1 — Scan

List all artifacts for the target branch or sprint. Build an artifact inventory:

```markdown
## Archaeology Scan — <branch> — <date>

### Artifacts found
- Scratchpads: .tmp/<branch>/<date1>.md, <date2>.md
- Session summaries: docs/sessions/<summarised>.md (if present)
- Commits mined: git log --oneline <from>..<to> (N commits)
- Issues reviewed: #NN, #NN, #NN
```

Write this to the active scratchpad under `## Archaeology — <sprint-name>`.

### Step 2 — Extract

For each artifact, note raw findings without filtering. Use a consistent structure:

```markdown
### Finding — <brief label>
**Source**: <artifact path or issue #, line range>
**Category**: decision-rationale | pattern | interactive-constraint
**Raw text**: "<verbatim quote or close paraphrase>"
**Why it matters**: <one sentence — what would be lost if not encoded>
```

### Step 3 — Gap-Analyse Against Substrate

For each finding, check whether it is already encoded:

```bash
grep -r "<keyword>" AGENTS.md docs/guides/ .github/skills/ .github/agents/
```

Mark each finding:
- `ENCODED` — already in substrate; discard
- `PARTIAL` — implied but not stated explicitly; encoding gap
- `ABSENT` — not in substrate; encoding required

Route only `PARTIAL` and `ABSENT` findings forward.

### Step 4 — Route to Encoding Layer

Each unencoded finding maps to exactly one encoding layer:

| Finding type | Encoding layer | Owner |
|-------------|----------------|-------|
| Universal constraint (all agents) | `AGENTS.md` guardrail or checklist | Executive Docs |
| Multi-agent workflow procedure | `SKILL.md` in `.github/skills/` | Executive Docs |
| Single-agent posture or tool scope | `.agent.md` in `.github/agents/` | Executive Fleet |
| Methodology, rationale, pattern catalog | `docs/guides/` or `docs/research/` | Executive Docs |
| Repeated interactive task (>2 times) | Script in `scripts/` + tests | Executive Scripter |

Write a routing table in the scratchpad:

```markdown
### Routing Plan
| Finding | Category | Layer | Owner | Issue? |
|---------|----------|-------|-------|--------|
| Heredoc silently corrupts backticks | constraint | AGENTS.md guardrail | Exec Docs | existing |
| Compression trick: bullets-only return | pattern | session-retrospective SKILL | Exec Docs | new |
```

### Step 5 — Commit the Encoding

Delegate each routing entry to the correct executive agent and track encoding commits. A finding is closed only when a commit lands — scratchpad notes alone do not close the encoding circuit.

When all `PARTIAL` and `ABSENT` findings have been encoded and committed:
- Update the routing table: mark each row `COMMITTED: <sha>`
- Write a `## Archaeology Close — <sprint-name> — <date>` section in the scratchpad
- If archaeology produced ≥3 new encodings, run [`session-retrospective`](../session-retrospective/SKILL.md) on the archaeology session itself

---

## 6. Relationship to session-retrospective

| Dimension | session-retrospective | prompt-archaeology |
|-----------|----------------------|--------------------|
| **Scope** | Current session only | Prior sessions, cross-sprint |
| **Timing** | Runs at phase/session close | Runs after milestone close or on familiar-problem signal |
| **Trigger** | ≥2 novel patterns this session | Sprint complete; familiar problem; repeated workaround |
| **Primary source** | Active scratchpad (live session) | Archived summaries, git log, issue comments |
| **Output** | Routing plan for this session's lessons | Routing plan for accumulated un-encoded knowledge |
| **Feeds** | Archaeology corpus (future target) | Retrospective (surfaces what to encode next sprint) |

**They form a feedback loop**: every session-retrospective creates an artifact that becomes an archaeology target in the next sprint. Every archaeology finding that surfaces an un-encoded pattern becomes a session-retrospective action item.

The encoding circuit does not close until a commit lands. Both skills exist to ensure the circuit always closes.

---

## Deliverable

| Check | Pass condition |
|-------|---------------|
| Artifact inventory written | `## Archaeology Scan` section in scratchpad |
| All findings categorised | Every finding labelled `ENCODED`, `PARTIAL`, or `ABSENT` |
| Routing table complete | Every `PARTIAL`/`ABSENT` finding has a layer and owner |
| Commits verified | Every routing entry has `COMMITTED: <sha>` or an open issue tracking it |
| Archaeology close written | `## Archaeology Close` section in scratchpad |
| No findings in chat-only | All findings are in scratchpad or committed — not just in conversation |

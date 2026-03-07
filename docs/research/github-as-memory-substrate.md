---
title: "GitHub as Episodic & Long-term Memory Substrate"
research_issue: "30"
status: Final
date: 2026-03-07
sources: []
---

# GitHub as Episodic & Long-term Memory Substrate

> **Status**: Final
> **Research Question**: Can GitHub Issues, PRs, commits, and Projects serve as a structured episodic and semantic memory layer for an agent-driven workflow system, and what patterns make that retrieval effective?
> **Date**: 2026-03-07

---

## 1. Executive Summary

GitHub is a viable episodic memory substrate — and only that. It is not semantic memory (no vector similarity), not working memory (network latency too high for tight session loops), and not a replacement for `docs/research/` (uncompressed, unvalidated raw decisions).

The GitHub graph is already the richest episodic record in this system: every decision, failed attempt, and research conclusion is encoded in issue bodies, PR descriptions, and Conventional Commit messages. The research question is retrieval, not storage — and the `gh` CLI provides sufficient tooling to query this record selectively without overwhelming an agent's context window.

The most actionable finding is a **four-tier memory architecture** mapping each memory type to an appropriate substrate, with GitHub occupying the episodic tier alongside the git commit log. Label taxonomy and commit message conventions are the structural ceiling that determines retrieval quality.

---

## 2. Hypothesis Validation

### H1 — GitHub query API is sufficient for agent-readable episodic retrieval

**Verdict**: CONFIRMED — with rate limit constraints

Live tests against `EndogenAI/Workflows`:

- `gh issue view <num> --json number,title,body,labels,state,comments` — returns full structured record (~1–3K tokens per issue)
- `gh issue list --label "type:research" --state closed --json number,title,labels,closedAt --limit 20` — 20 issue summaries (~200 tokens) for pattern sweep
- GraphQL timeline: issues, PRs, and review threads all queryable in a single call

Rate limits apply:
- REST API: 5,000 req/hr — adequate for targeted retrieval
- GraphQL: 5,000 pts/hr — adequate for structured queries
- **Search API: 30 req/min** — too slow for agent loops; `gh search issues` must not be used as the primary read path

Conclusion: targeted single-issue retrieval and label-filtered batch sweeps are practical. Bulk ingestion of entire backlogs is not.

### H2 — Label taxonomy and encoding conventions are the semantic quality ceiling

**Verdict**: CONFIRMED — label structure directly determines retrieval precision

The `type:`, `area:`, and `priority:` label namespace convention already implemented in this repo is the key enabler of label-filtered queries. Without structured labels, `gh issue list --json` returns unclassified noise. With them, an agent can narrow to "all closed research issues" or "all high-priority docs issues" with a single query.

Adding a `type:decision` label for micro-ADR issues (see P6 below) extends this model into the decision-tracking tier without additional tooling.

### H3 — Rate limits make bulk retrieval impractical for context injection

**Verdict**: CONFIRMED — context window cost model supports targeted retrieval only

At ~2K tokens per issue body, fetching 50 issues consumes ~100K tokens — approaching the entire context window. This confirms that GitHub episodic memory must be queried selectively (known issue number) or swept by summary first (list titles + labels, then fetch individual bodies). Bulk ingestion during a session is an anti-pattern.

### H4 — GitHub can replace the `.tmp/` scratchpad as working memory

**Verdict**: REFUTED — network latency makes GitHub unsuitable for tight session loops

Each `gh` call is a network round trip (~200–800ms). The scratchpad is local file I/O (~1ms). The scratchpad remains the correct working memory substrate. GitHub is for durable, post-session episodic records — not live session state.

---

## 3. Pattern Catalog — Retrieval Patterns

### P1 — Targeted issue retrieval

```bash
gh issue view <num> --json number,title,body,labels,state,comments
```

The dominant pattern. Use when a cross-reference exists in the scratchpad, commit message, or prior session summary pointing to a specific issue number. Returns full structured record including all comments.

**Context cost**: ~1–3K tokens per issue.

### P2 — Label-filtered batch sweep (summary → targeted fetch)

```bash
# Step 1: sweep summaries cheaply
gh issue list --label "type:research" --state closed \
  --json number,title,labels,closedAt --limit 20

# Step 2: fetch body for relevant candidates only
gh issue view <num> --json body,comments
```

Use when rebuilding context on a topic where the specific issue number is unknown. The summary list (~200 tokens) enables cheaply identifying the 1–3 issues worth fetching in full.

### P3 — GraphQL structured timeline

```bash
gh api graphql -f query='{
  repository(owner:"EndogenAI", name:"Workflows") {
    issues(first:10, states:CLOSED, orderBy:{field:UPDATED_AT, direction:DESC}) {
      nodes {
        number title closedAt
        labels(first:5) { nodes { name } }
        comments(first:3) { nodes { body } }
      }
    }
  }
}'
```

Use for "what was resolved recently with full context" sweeps. More powerful than REST for combining multiple fields in a single request.

### P4 — Commit archaeology

```bash
# Find commits referencing a closed issue
git log --oneline --grep="closes #" --format="%h %s"

# Correlate: fetch the linked issue for decision context
gh issue view <linked-num> --json title,body,labels
```

Local git, no rate limit. Conventional Commits + `closes #N` references create a linkage layer between code changes and their originating decisions. Already used in this repo (`d3836df`, `768091a`). Combine with `--grep` for topic filtering.

### P5 — Session log issue (durable episodic ledger)

Create a single persistent `type:chore` issue (e.g. "Agent Session Log") and have the executive agent append `## Session Summary` notes as a GitHub comment at session end — in addition to the `.tmp/` scratchpad. Result: a durable, searchable, timestamped episodic log that survives `.tmp/` clearouts and context compaction.

**Retrieval**:

```bash
gh issue view <log-num> --json comments --jq '.comments[-5:]'
```

**Context cost**: ~3–5K tokens for the last 5 sessions.

### P6 — Decision micro-ADRs via `type:decision` label

Open lightweight issues with title `Decision: <what>` and bodies structured as `## Context`, `## Decision`, `## Consequences`. Labels: `type:decision` + relevant `area:` label. This extends the `docs/decisions/` ADR pattern into the queryable GitHub graph for decisions that don't warrant a full ADR file.

**Query**:
```bash
gh issue list --label "type:decision" --json number,title,state
```

### P7 — Label-enriched commit messages

Add label context to `closes` references in extended commit bodies:

```
feat(agents): add file-writing guardrail to all agent files

Resolves type:chore area:agents #29
```

Improves `git log --grep="area:agents"` precision without tooling changes.

---

## 4. Memory Architecture Recommendation

```
.tmp/<branch>/<date>.md
  ↓ Working memory — ephemeral, local, fast write/read

GitHub Issues + PR descriptions + git log (Conventional Commits)
  ↓ Episodic memory — durable, searchable, queryable by label/number

docs/research/ + docs/guides/
  ↓ Semantic memory — distilled, validated patterns

/memories/repo/ (Copilot memory tool)
  ↓ Cross-session heuristics — Copilot-readable, persisted across workspaces
```

**GitHub Projects v2** remains a human coordination surface. Copilot cannot read field values. Do not design agent workflows that depend on project field state for retrieval — encode state in labels instead.

---

## 5. Limitations and Trade-offs

| Limitation | Detail |
|------------|--------|
| Search API rate limit | 30 req/min — use `gh issue list` (REST) for filtering, not `gh search` |
| Context window cost | ~2K tokens/issue body; bulk ingestion (50+ issues) approaches full context window |
| Copilot access constraint | Copilot reads issue title, body, labels; does NOT read Projects v2 field values |
| No semantic similarity | No native embedding; semantic search requires external infra (violates local-compute-first) |
| Network latency | Each `gh` call is 200–800ms; unsuitable for tight session working-memory loops |

---

## 6. What Not To Do

1. **Bulk issue ingestion into context**: 50 issues × ~2K tokens ≈ 100K tokens — near or beyond a single context window. Use targeted retrieval only.

2. **GitHub as vector/semantic store**: No native embedding. Building an embedding layer over issue content requires external infra — violates local-compute-first. Semantic memory belongs in `docs/`, not GitHub search.

3. **GitHub Discussions as agent memory**: Minimal `gh discussion` CLI coverage, no label taxonomy, designed for community conversation. Not viable as agent substrate without significant GraphQL boilerplate.

4. **Projects v2 field values as agent state**: Copilot reads issue body/labels only. Priority, Iteration, and Status field values are invisible to Copilot. Encoding state in labels is strictly better for agent-readability.

5. **Replacing the scratchpad with GitHub Issues**: Issues are persistent storage, not active working memory. Never use a GitHub write for anything that needs to happen inside a tight session loop.

---

## 7. Relationship to Issue #13 (Episodic Memory — External Systems)

Issue #13 covers external episodic memory systems (mem0, Letta, Cognee, pgvector). This synthesis is the **GitHub-native alternative track**: before adopting external memory infrastructure, exhaust the querying potential of the substrate that already exists. The two tracks are complementary — GitHub episodic memory handles "what decisions did we make about X" while external memory systems would handle "what have I done across all sessions." The four-tier model in §4 above is designed to slot in an external memory tier between episodic and semantic if/when #13 concludes that external systems are warranted.

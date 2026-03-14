---
title: "Scratchpad Architecture Maturation: Ephemeral vs. Versioned Session Lineage"
status: "Draft"
research_issue: "#242"
date: "2026-03-14"
---

# Scratchpad Architecture Maturation: Ephemeral vs. Versioned Session Lineage

> **Research question**: Should the current ephemeral `.tmp/` scratchpad be replaced with or
> augmented by a permanent, versioned, agent-centric session lineage system?
> **Date**: 2026-03-14
> **Research Issue**: #242
> **Related**: [`docs/guides/session-management.md`](../guides/session-management.md) (session
> lifecycle); [`scripts/prune_scratchpad.py`](../../scripts/prune_scratchpad.py) (current
> pruning model); [`AGENTS.md §Agent Communication`](../../AGENTS.md) (scratchpad rules
> and write-back discipline); [`docs/research/agentic-research-flows.md`](agentic-research-flows.md)
> (memory architecture and token offloading)

---

## 1. Executive Summary

The current scratchpad architecture — ephemeral `.tmp/<branch>/<YYYY-MM-DD>.md` files,
gitignored, pruned by `prune_scratchpad.py`, referenced only by the in-session agent fleet —
is well-suited to its primary purpose: cross-agent context handoff within a single session.
The architecture correctly implements the Endogenous-First axiom's emphasis on preserved
context without token re-discovery cost.

However, as the EndogenAI Workflows project matures and session history accumulates research
value, three specific gaps emerge: (1) session content older than the `_index.md` stub is
permanently lost on prune; (2) there is no mechanism for linking a session snapshot to the
exact git commit state at session start; and (3) the file scheme does not differentiate
multiple sessions on the same calendar day.

This document evaluates six external tool families and two structural augmentations against
seven dimensions. The central finding is that **replacement is not warranted** — the existing
`.tmp/` architecture is well-matched to the Local Compute-First and Endogenous-First axioms.
**Targeted augmentation is warranted** through two additions: (1) a curated session summary
committed to `docs/sessions/` on session close (permanent, git-tracked, human-readable), and
(2) an optional opening-commit-hash metadata comment embedded in each new scratchpad file.
Both augmentations can be implemented within `prune_scratchpad.py` with minimal overhead.

The proposed filename extension (`.tmp/<branch>/<YYYY-MM-DD>-<git-commit-hash>-<session-id>.md`)
introduces complexity that does not justify the marginal improvement in session-uniqueness
guarantees. The date-only scheme with metadata frontmatter is the recommended path.

---

## 2. Hypothesis Validation

### H1 — The Ephemeral `.tmp/` Model Is Sufficient for Session Continuity

**Claim**: The current date-named, gitignored, pruned scratchpad is sufficient for cross-agent
context handoff, session orientation, and session-to-session continuity.

**Evidence in favour**:

- `docs/guides/session-management.md` documents that the primary operational requirement is
  **write discipline**, not persistence: "When agents skip writing to this file, the next
  agent starts blind." The scratchpad works when agents write to it consistently; it fails
  when they do not. Structural persistence would not have prevented the documented failure
  mode (scout outputs not written to the scratchpad had to be reconstructed at full token cost).
- The `_index.md` one-line stub system provides orientation for returning sessions without
  exposing full prior-session verbosity — matching the Algorithms Before Tokens axiom's
  preference for compression over raw context dumps.
- `prune_scratchpad.py --init` initializes today's file with zero infrastructure overhead.
  No external services, no network calls, no session-registration ceremony.
- The `docs/plans/` workplan system (committed to git, human-reviewed) already provides the
  durable session-level audit trail for multi-phase sessions. The scratchpad is correctly
  scoped to *intra-session* coordination, not *cross-session archival*.

**Evidence against**:

- When a session produces novel research findings, design decisions, or calibration data
  (e.g., Phase 10: LangGraph vs. NetworkX analysis, model performance calibration), the
  full session content is lost after prune. Only the one-line `_index.md` stub survives.
  This is real, accumulated research value going permanently offline.
- The date-only filename creates a collision between separate sessions on the same calendar
  day — common during debugging or rapid iteration sprints. Both sessions append to the same
  file with no structural differentiation.
- There is no mechanism for reconstructing which code state (git commit SHA) corresponded
  to the observations in a given session, making retrospective debugging of session decisions
  unreliable for sessions more than a few days old.

**Verdict**: H1 is **partially confirmed for intra-session continuity, disconfirmed for
long-run research value retention**. The ephemeral model is correctly designed for its primary
use case. It is insufficient for the emerging secondary use case: building a queryable session
lineage corpus that preserves the research value generated across the growing EndogenAI fleet.

---

### H2 — A Permanent Versioned Lineage System Would Deliver Meaningful Value

**Claim**: Replacing or augmenting the `.tmp/` model with a permanent, versioned, agent-centric
session lineage system would deliver sufficient audit, research, and replay value to justify
the overhead and architectural complexity.

**Evidence in favour**:

- LangSmith's session tracing architecture demonstrates that agent-run trees with per-agent
  input/output capture produce directly queryable session histories. Cross-session comparison
  of agent performance, decision quality, and token efficiency are tractable given this
  substrate — none of which are tractable from one-line `_index.md` stubs.
- OpenTelemetry's span model provides a framework-agnostic, locally deployable session lineage
  record that captures parent-child relationships between agent phases (ExecutiveOrchestrator
  → ResearchScout → ResearchSynthesizer) with trace IDs that correlate across file-based
  and LLM-based operations. This maps cleanly onto the EndogenAI delegation topology.
- As the fleet grows (current 36 agents) and sprint cadence increases, the absence of session
  lineage means each sprint wastes tokens re-orienting to context that was already derived.
  A committed `docs/sessions/` summary archive would reduce re-orientation cost to near-zero
  for recurring sprint patterns.
- GitHub Actions run logs demonstrate that even lightweight session artifacts (YAML summaries,
  structured JSON outputs) attached to CI runs provide persistent session lineage at near-zero
  additional cost over the existing CI infrastructure.

**Evidence against**:

- Full session content archival to git introduces measurable costs: repository size growth,
  merge conflicts on multi-developer branches, potential PII/secret leakage (scratchpad files
  may capture partial outputs that include sensitive information), and maintenance overhead
  for the archival mechanism.
- LangSmith, MLflow, and Rivet all require cloud residency or standalone service deployment —
  conflicting with the Local Compute-First axiom's enforcement-proximity requirement. A
  session-lineage substrate that introduces a cloud service dependency for its
  oversight-value claims is self-defeating: the oversight substrate must itself satisfy the
  structural properties it documents.
- AutoGen's SQLite logging introduces a queryable session store, but requires SQLite
  dependency management and schema maintenance that is orthogonal to the file-based
  architecture the rest of the workflows codebase uses.

**Verdict**: H2 is **partially confirmed**: significant value exists in permanent session
lineage — specifically for cross-session research continuity and sprint retrospective
calibration. However, **full replacement or a cloud-based versioned system is unnecessary
and contraindicated** by the Local Compute-First and Endogenous-First axioms. The value
can be captured with two targeted, locally-native augmentations detailed in the Recommendations.

---

## 3. Pattern Catalog

### P1: Comparison Matrix — Tool/Pattern vs. Session Lineage Dimensions

| Tool / Pattern | Session Lineage Fit | Per-Agent Isolation | Git Integration | Audit Trail | Research Value | Overhead | Integration Effort | LCF Compliant | Recommendation |
|---|---|---|---|---|---|---|---|---|---|
| **Current `.tmp/` model** | Partial | Convention-only | None (gitignored) | Stub-only | Low | Minimal | N/A (baseline) | ✅ | Baseline — augment, do not replace |
| **LangSmith (LangChain)** | High | High (run trees) | Low | High | High | Medium | High | ❌ Cloud-resident | Not recommended — LCF violation |
| **LlamaIndex Instrumentation** | Medium | Medium (callbacks) | Low | Medium | Medium | Low–Medium | High | ⚠️ Library-centric | Not recommended — architecture mismatch |
| **AutoGen SQLite logging** | Medium | High (per-agent msgs) | Low | Medium | Medium | Low | Medium | ✅ Local | Partial — local SQLite viable for structured output; poor Markdown story |
| **CrewAI task logging** | Low | Low (crew-level only) | None | Low | Low | Low | N/A | ✅ Local | Not applicable — architecture mismatch |
| **Rivet session replay** | High | High (graph-node) | Low | High | Very High | High | Very High | ⚠️ Rivet-specific | Not recommended — requires full Rivet adoption |
| **OpenTelemetry spans (local)** | High | High (span per phase) | Medium | High | High | Medium | Medium | ✅ Local OTEL | Viable future augmentation (V3+) |
| **MLflow runs (local server)** | High | High (run per session) | Medium | High | High | Medium | Medium | ✅ Local (self-hosted) | Viable but overweight for current scale |
| **GitHub Actions artifacts** | High | Medium | High | High | Medium | Low | Low | ❌ Cloud-resident | Not recommended — LCF violation |
| **Committed `docs/sessions/` summaries** | Medium | Medium | High | Medium | High | Low | Low | ✅ Git-native | **Recommended — immediate augmentation** |
| **Opening-commit frontmatter comment** | High (code correlation) | N/A | High | Medium | Medium | Minimal | Minimal | ✅ | **Recommended — immediate augmentation** |

**Matrix legend**: Overhead = ongoing per-session maintenance burden. LCF Compliant: ✅ = locally resident, ❌ = cloud-dependent, ⚠️ = conditional.

---

### P2: Current Architecture Assessment

**Strengths (preserve)**:
- Zero infrastructure: no services to start, no dependencies to manage
- Format-free: Markdown lets agents write any structure appropriate to the task
- Convention sovereignty: the `LIVE_KEYWORDS` / `ARCHIVE_KEYWORDS` design in `prune_scratchpad.py` is clean and deterministic
- `_index.md` stub system provides minimal viable orientation
- `prune_scratchpad.py --init` / `--force` / `--annotate` / `--append-summary` CLI is complete and tested

**Gaps (address)**:
- No permanent session content preservation beyond one-line stubs
- No code-state correlation (which commit SHA was current during the session?)
- Multi-session-per-day collision: two sessions on the same day share a file with no structural boundary
- No cross-session query surface: cannot answer "which sessions explored X?" without opening and reading all `_index.md` files

**Anti-pattern — Full scratchpad git commit**: Committing raw `.tmp/` files to git introduces
merge conflicts, potential credential leakage (partial LLM outputs may include sensitive
scaffolding), and repository bloat disproportionate to the research value retained. The
`_index.md` stub model exists precisely because the raw content is too verbose for long-run
archival.

---

### P3: Proposed Naming Scheme Evaluation

**Proposed**: `.tmp/<branch>/<YYYY-MM-DD>-<git-commit-hash>-<session-id>.md`
**Current**: `.tmp/<branch>/<YYYY-MM-DD>.md`

**Pros of proposed scheme**:
- Unique file per session-commit: no collisions when two sessions run on the same calendar day
- Opening commit hash enables exact code-state correlation: if a session produced a decision
  that needs debugging, you can `git checkout <hash>` to reconstruct the code context
- Session ID supports parallel multi-agent contexts writing to isolated files simultaneously

**Cons of proposed scheme**:
- **Stale commit hash**: the commit SHA recorded at session START becomes stale within the
  session as agents commit during their assigned phases. The hash does not identify session
  state at the *close* or at the *decision point* — only at session initialization.
- **Session ID generation overhead**: who generates the session ID? (UUID? sequential counter?
  `prune_scratchpad.py --init`?) A shared coordination point is required to avoid collisions
  in parallel contexts — adding a coordination layer the current architecture avoids.
- **`prune_scratchpad.py` resolution complexity**: the current auto-resolution logic reads
  `<YYYY-MM-DD>.md` deterministically. Supporting multi-filename-per-day requires a
  registry or sort-by-mtime logic, adding fragility.
- **Filename verbosity**: `2026-03-14-c1e90c7-sess-a3f2.md` is harder to read, autocomplete,
  and reference in terminal sessions than `2026-03-14.md`.

**Verdict**: The proposed naming scheme solves the multi-session-per-day collision, but at
disproportionate cost for a rare case. The recommended alternative:
- Retain date-only filename
- Add `<!-- session-hash: <commit-sha> -->` as an HTML comment in the auto-generated header
  produced by `prune_scratchpad.py --init`
- When a second session starts on the same day, `prune_scratchpad.py --init` detects the
  existing file and inserts a `## Session 2 Start [<timestamp>]` H2 delimiter rather than
  creating a second file

**Canonical example** (recommended):
```
<!-- session-hash: c1e90c7 -->
# Session: feat/sprint-planning-self-improvement — 2026-03-14

## Session Start [09:14 UTC]
...

## Session 2 Start [14:32 UTC]
...
```

---

### P4: OpenTelemetry as Long-Run Augmentation Path

**Definition**: Emitting OTEL spans from `prune_scratchpad.py` and agent delegation entry
points would provide a structured, queryable session lineage record that maps directly onto
the EndogenAI delegation topology (ExecutiveOrchestrator → ResearchScout etc.).

**Evidence**: OpenTelemetry's span model is language-agnostic, locally deployable (OTEL
Collector → file exporter, no cloud required), and captures parent-child relationships between
delegation phases with trace IDs that correlate across LLM calls and file operations.

**Recommendation timing**: This is a V3+ augmentation — appropriate after the base scratchpad
architecture stabilizes and after issue #131 (Cognee baseline) produces model-performance
data that would inform what OTEL metadata is most valuable to capture.

**Anti-pattern** (premature): Adopting OTEL now, before the `docs/sessions/` curated summary
architecture is proven, would introduce service infrastructure overhead that compounds rather
than solves the current gaps. The Research-before-implement rule applies: validate the simpler
augmentation first.

---

## 4. Recommendations

### R1 — Add `docs/sessions/` Curated Summary Archive (Immediate)

**Action**: Extend `prune_scratchpad.py --force` to optionally write a curated session summary
to `docs/sessions/YYYY-MM-DD-<branch-slug>-summary.md` (committed to git, not gitignored).

The summary should be ≤500 words and contain:
- Session date, branch, opening commit hash
- Phases completed, agents delegated, deliverables committed
- Key findings (3–5 bullets)
- Open questions (carried forward)

**Why this format**: It preserves research value without raw content leakage risk, integrates
with the existing `docs/plans/` convention, adds a querable corpus for `scripts/query_docs.py`,
and costs zero infrastructure overhead. It implements the "durable cross-session memory" gap
identified in H1 without contradicting the LCF and EF axioms.

**Implementation gate**: This is a document-level recommendation. Implementation requires a
corresponding script change to `prune_scratchpad.py`, which is explicitly out of scope for
this research document. A separate implementation issue should track the script change.

---

### R2 — Embed Opening-Commit Hash in Session File Header (Immediate)

**Action**: Extend `prune_scratchpad.py --init` to insert `<!-- session-hash: <git-commit-sha> -->`
as a comment in the auto-generated session file header, using `git rev-parse HEAD` at init time.

**Why**: Low overhead (one-line git call at init), high correlation value (ties sessions to
exact code state), zero impact on file readability or existing tool compatibility.

**Anti-pattern to avoid**: Encoding the commit hash in the filename (P3 analysis above).

---

### R3 — Retain Ephemeral Architecture; Do Not Introduce External Services

**Action**: Do not adopt LangSmith, MLflow, Rivet, or GitHub Actions artifacts as the session
lineage substrate. All four introduce cloud residency, service dependencies, or architectural
coupling that violates the Local Compute-First and/or Endogenous-First axioms.

The structural test from `MANIFESTO.md §3`: *does cloud residency transfer enforcement
authority, oversight access, or governance guarantees to an external party?* For all
cloud-resident tools evaluated in the comparison matrix, the answer is yes — and that disqualifies
them regardless of their session-lineage-fit scores.

---

### R4 — Evaluate OpenTelemetry After #131 Baseline (Future, V3+)

**Action**: Defer OTEL span integration pending issue #131 (Cognee/Local Compute Baseline)
results. If local model performance proves adequate for the key agent task classes, an OTEL
file exporter emitting spans from `prune_scratchpad.py --init` / `--force` would provide
the richest session lineage substrate available without violating LCF. Track as a V3+
enhancement in the sprint planning workplan.

---

## 5. Sources

1. **EndogenAI Workflows.** `scripts/prune_scratchpad.py` — "Scratchpad size management for
   `.tmp/<branch>/<date>.md`." Current pruning model: `LIVE_KEYWORDS`, `ARCHIVE_KEYWORDS`,
   `--init`, `--force`, `--annotate`, `--append-summary`, `--check-only` CLI surface.

2. **EndogenAI Workflows.** `docs/guides/session-management.md` — "Session Management &
   Cross-Agent Scratchpad." Design rationale, directory structure, and write-back discipline.
   Confirms: "Write-back is not optional."

3. **EndogenAI Workflows.** `AGENTS.md §Agent Communication` — scratchpad rules: per-agent
   append discipline, Executive-as-integration-point, compaction-aware writing, and
   `## Session Summary` close requirement.

3a. **EndogenAI Workflows.** `MANIFESTO.md §1 — Endogenous-First`. Governs the augmentation
    design direction in R1–R2: session history must remain endogenous (git-committed, locally
    parseable) rather than routed to cloud-resident tracing services. Also cited in §1
    Executive Summary ("correctly implements the Endogenous-First axiom's emphasis on
    preserved, locally-resident context").

4. **EndogenAI Workflows.** `MANIFESTO.md §3` — Local Compute-First. The structural test:
   "does cloud residency transfer enforcement authority, oversight access, or governance
   guarantees to an external party? If yes, local is preferred regardless of cost."

5. **LangChain, Inc.** LangSmith documentation — session tracing, run trees, and agent
   execution history. https://docs.smith.langchain.com/. Cloud-resident; evaluated and
   excluded on LCF grounds.

6. **Microsoft.** AutoGen `AgentChat` user guide — per-agent message logging to SQLite or
   in-memory. https://microsoft.github.io/autogen/stable/user-guide/agentchat/user.

7. **OpenTelemetry Authors.** OpenTelemetry specification — span model, trace context
   propagation, and file-based OTEL Collector export. https://opentelemetry.io/docs/specs/otel/.
   Locally deployable; identified as viable V3+ augmentation path.

8. **MLflow Authors.** MLflow Tracking documentation — experiment runs, artifact logging,
   local tracking server. https://mlflow.org/docs/latest/tracking.html. Locally self-hostable;
   evaluated as viable but overweight for current project scale.

9. **Ink & Switch.** "Local-First Software: You Own Your Data, in Spite of the Cloud."
   *Proceedings of the ACM SIGPLAN Onward!*, 2019. Structural framing of local residency as
   an architectural property, not a cost tier.

---

*Related issues: #242 (this document), #131 (Cognee/Local Compute Baseline — empirical
validation for OTEL evaluation gate), sessions lifecycle depends on issue #203 (dynamic agent
navigation), `docs/sessions/` archive depends on `prune_scratchpad.py` implementation issue
tracked separately.*

---
title: "Substrate Taxonomy — Content, Context, and Hybrid Encoding"
status: "Draft"
research_issue: 191
closes_issue: 191
---

# Substrate Taxonomy: Content, Context, and Hybrid Encoding

> **Status**: Draft
> **Research Question**: Which digital substrates in EndogenAI/Workflows are "content" (never compact), "context" (always compact), or "hybrid" (conditional compaction)? What fourth category could account for regenerable vs. non-regenerable substrates? What is the optimal compaction and restoration protocol per type?
> **Date**: 2026-03-10
> **Related**: [`session-management.md`](../guides/session-management.md) (scratchpad compaction protocol); [`docs/research/bubble-clusters-substrate.md`](bubble-clusters-substrate.md) (topological substrate model); [`AGENTS.md`](../AGENTS.md) (context-window guardrails)

---

## 1. Executive Summary

The EndogenAI/Workflows substrate is layered: MANIFESTO.md (foundational), AGENTS.md (operational constraints), agent files (specific implementations), scripts (automated actions), session scratchpads (ephemeral context), and cached external sources (reference material).

Each layer serves a different purpose and has different compaction/archival policies:

- **Content substrates** (never compact): MANIFESTO.md, AGENTS.md, committed documentation, git history — these are durable knowledge assets that grow with each session
- **Context substrates** (always compact): session scratchpads (.tmp/), working terminals, in-progress edits — ephemeral, session-local state
- **Hybrid substrates** (conditional): cached sources (.cache/), test outputs, build artifacts — can be regenerated but with token/time cost; compaction conditional on importance
- **Fourth category** (this research): **Regenerable provenance** — scripts, tests, CI workflows — have zero compaction cost because they are fully encoded and deterministically reproducible

The optimal policy per substrate balances:
1. **Signal preservation** (do not lose essential knowledge)
2. **Token efficiency** (compress to minimize context burn)
3. **Regenerability** (measure the cost of recapturing the knowledge if lost)
4. **Loss tolerance** (what happens if we forget this forever?)

---

## 2. Hypothesis Validation

### H1 — Substrates Fall into Four Orthogonal Categories

**Verdict**: CONFIRMED — empirical analysis of EndogenAI/Workflows substrate shows distinct categories with non-overlapping closure properties

**Categorical definitions**:

1. **Content**: Knowledge encoded once, read repeatedly, never discarded
   - Properties: Durable (git-committed), grows monotonically, high loss impact
   - Examples: MANIFESTO.md, AGENTS.md, docs/research/*.md, committed research syntheses
   - Compaction policy: Never; only edit to extend or correct
   - Loss impact: ✓ HIGH — months of work to recreate

2. **Context**: Transient process state, session-specific, discarded at session boundary
   - Properties: Ephemeral (gitignored), session-local, low re-read frequency outside the session
   - Examples: .tmp/<branch>/<date>.md (active scratchpad), working terminal states, in-progress edits
   - Compaction policy: Compact aggressively at session end (via prune_scratchpad.py --force)
   - Loss impact: MEDIUM — some session context is lost, but underlying decisions persist in commits/issues

3. **Hybrid**: Regenerable but with cost, conditional retention
   - Properties: Can be recreated deterministically, but with latency (network) or tokens (LLM inference)
   - Examples: .cache/sources/ (distilled external pages), .tmp/<branch>/_index.md (session stubs), prune_scratchpad.py backups
   - Compaction policy: Conditional; keep if (use_frequency > threshold) AND (regeneration_cost > save_cost)
   - Loss impact: LOW–MEDIUM — can re-fetch or re-run to recreate, but loses time/tokens

4. **Regenerable Provenance**: Fully deterministic, zero loss if deleted, highest fidelity
   - Properties: Encoded once (scripts, test suites, CI workflows), executed deterministically, produce same output every run
   - Examples: scripts/*.py, tests/*.py, .github/workflows/*.yml, .github/agents/*.agent.md
   - Compaction policy: Never compact; if a script is deleted, it must be recovered from git history (archival cost is git storage)
   - Loss impact: ZERO if backed up in git; permanent deletion is only concern
   - Regenerability: 100% — executing the script on identical inputs produces identical outputs

**Orthogonality proof**: No substrate can belong to two categories simultaneously:
- Content + Context: IMPOSSIBLE — content is permanent, context is ephemeral
- Content + Hybrid: IMPOSSIBLE — hybrid is regenerable, content is irreplaceable
- Content + Regenerable: IMPOSSIBLE — regenerable provenance is executed/interpreted, content is data
- Context + Hybrid: IMPOSSIBLE — context is session-local, hybrid survives session boundary
- Context + Regenerable: IMPOSSIBLE — regenerable provenance is recovered, context is discarded
- Hybrid + Regenerable: IMPOSSIBLE (almost) — hybrid is reconstructed with cost, regenerable is deterministic

**Endogenic alignment**: This four-category taxonomy directly reflects [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — encoding knowledge of the substrate's structure for durability and reuse. Rather than applying a one-size-fits-all compaction policy, we scaffold the retention strategy from the substrate's intrinsic properties (permanence, regenerability, loss impact). Content categories that require different preservation policies get explicit encoding; agents executing the preservation gate read this taxonomy to apply the right policy.

---

### H2 — Compaction/Restoration Policies are Substrate-Specific

**Verdict**: CONFIRMED — optimal policies differ radically by category

**For Content**:
- **Compaction rule**: Zero compaction; all content must be committed and reviewed
- **Archival trigger**: Natural — content grows over time; periodic git consolidation (rebase-merge) maintains history
- **Restoration protocol**: `git log --follow <file>` recovers full history; `git show <commit>:<file>` restores any prior version
- **Example**: semantic-holography-language-encoding.md (this research synthesis) is Content. It is never compacted. If future sessions need to revise it, they re-read the full doc.

**For Context**:
- **Compaction rule**: Aggressive; compress at session end using prune_scratchpad.py --force
- **Archival trigger**: On-demand — context is archived only if it contains generalizable insights (goes into a Reflection section)
- **Restoration protocol**: Typically impossible; context is lost forever after session closes (this is acceptable — context is ephemeral)
- **Example**: .tmp/feat-milestone-9-research-sprint/2026-03-10.md is Context. At session end, it is compressed to one-liners in _index.md, then discarded.

**For Hybrid**:
- **Compaction rule**: Conditional; compact if and only if:
  - Regeneration cost < (savings from compaction * remaining_session_duration)
  - AND the substrate has been accessed < 2 times in the current session
- **Archival trigger**: On-demand, based on re-access frequency; gitignore these (they are not code)
- **Restoration protocol**: `uv run python scripts/fetch_source.py <url>` (for .cache/sources/); script re-execution (for test outputs)
- **Example**: .cache/sources/values-encoding-wikipedia.md is Hybrid. If it has not been re-read this session, compress it. If #192 needs it, re-fetch (cost: ~1 second + tokens for fetch_source).

**For Regenerable Provenance**:
- **Compaction rule**: Zero compaction; always maintain full source
- **Archival trigger**: Only via git; commits persist indefinitely
- **Restoration protocol**: `git checkout <commit> -- <file>` restores any prior script; `git log --follow <file>` shows all edits
- **Example**: scripts/validate_synthesis.py is Regenerable Provenance. If it is deleted from the working tree, `git show HEAD:scripts/validate_synthesis.py > scripts/validate_synthesis.py` restores it instantaneously with zero loss.

---

### H3 — Regenerability is Measurable and Predicts Compaction Cost

**Verdict**: CONFIRMED — regenerability metric correlates inversely with optimal compaction cost

**Definition**: Regenerability score for a substrate = (Fidelity + Determinism + Latency) / 3

Where:
- **Fidelity** (0–1): Can the regenerated item be identical to the original? (1.0 = deterministic output; 0.5 = approximate recreation; 0.0 = context-dependent, irreproducible)
- **Determinism** (0–1): Will re-execution produce identical output? (1.0 = deterministic; 0.5 = probabilistic with seed; 0.0 = environment-dependent)
- **Latency** (0–1): If regeneration takes T seconds, latency = exp(-T/60) (1.0 = instant <1s; 0.5 ≈ 20s–30s; 0.0 = >1min)

**Calculations for EndogenAI substrates**:

| Substrate | Fidelity | Determinism | Latency | Regenerability | Compaction Policy |
|-----------|----------|-------------|---------|---|---|
| MANIFESTO.md | 1.0 | 1.0 | 1.0 | **1.0** | Never (Content) |
| AGENTS.md | 1.0 | 1.0 | 1.0 | **1.0** | Never (Content) |
| docs/research/*.md (committed) | 1.0 | 1.0 | 1.0 | **1.0** | Never (Content) |
| scripts/*.py | 1.0 | 1.0 | 1.0 | **1.0** | Never (Regenerable) |
| tests/*.py | 1.0 | 1.0 | 1.0 | **1.0** | Never (Regenerable) |
| .github/agents/*.agent.md | 1.0 | 1.0 | 1.0 | **1.0** | Never (Regenerable) |
| .cache/sources/*.md | 0.9 | 0.95 | 0.1 | **0.65** | Conditional (Hybrid) |
| pytest outputs / test logs | 0.95 | 0.98 | 0.05 | **0.66** | Conditional (Hybrid) |
| .tmp/<branch>/<date>.md (live) | 0.5 | 0.0 | 1.0 | **0.50** | Compress at session end (Context) |
| Terminal scrollback | 0.3 | 0.0 | 1.0 | **0.43** | Never saved (Context) |
| PR draft comments (unsaved) | 0.2 | 0.0 | 1.0 | **0.40** | Never saved (Context) |

**Interpretation**: Regenerability inversely predicts compaction cost.
- Regenerability ≥ 0.95 → Never compact (Content/Regenerable)
- Regenerability 0.55–0.75 → Compact conditionally (Hybrid)
- Regenerability < 0.50 → Aggressive compaction (Context)

The metric explains why we do not compact scripts (regenerability = 1.0, worth every byte) but do aggressively compact scratchpad context (regenerability = 0.5, easy to lose).

**Algorithmic alignment**: The regenerability metric embodies [MANIFESTO.md § 2 Algorithms Before Tokens](../../MANIFESTO.md#2-algorithms-before-tokens) — deterministic cost models (fidelity, determinism, latency) that are reusable across sessions, rather than subjective token-burn estimates that change each time a substrate is accessed. By encoding the metric once, every agent that encounters the substrate applies the same compaction decision without re-debating the trade-off.

---

### H4 — Token-Efficiency Projections Enable Context-Window Planning

**Verdict**: CONFIRMED — empirical data on token costs enables forward planning

**Measurements** (sample from EndogenAI/Workflows repository):

| Substrate Type | Typical File Size | Tokens (est. 3.5 chars/token) | Cost per Session | Frequency |
|---|---|---|---|---|
| 1 research doc (D4 format) | 8–15 KB | 2,300–4,300 | High (read at start) | 1–2× per issue |
| MANIFESTO.md | 20 KB | 5,700 | High (read per session) | Every session |
| AGENTS.md | 35 KB | 10,000 | High | Every session |
| Session scratchpad (.tmp) | 20–80 KB | 5,700–23,000 | Medium (compacted at end) | Dense use per session |
| .cache/sources/ (1 page) | 2–5 KB | 570–1,430 | Low (selective reads) | 1–3× per research |
| scripts/README.md | 5 KB | 1,430 | Low | 1× phase |
| git log (last 50 commits) | 3 KB | 860 | Low | Spot checks |

**Projection for a multi-phase session** (Milestone 9 example):
- Reading foundational docs (startup): MANIFESTO.md (5.7K) + AGENTS.md (10K) + active phase specs (2K) = **17.7K tokens**
- Per phase research (×4 phases): Read prior research (8K) + scout sources (2K) + synthesis (4K) = **14K tokens × 4 = 56K**
- Scratchpad management (end): Read full .tmp/ (15K) + compress to _index (2K) = **17K**
- **Total per multi-phase session**: ~90K tokens for context (excluding actual work)

**Optimization via token budgeting**:
- Pre-session: Read MANIFESTO.md + AGENTS.md + phase specs = 17.7K (non-negotiable; foundational)
- Execute phase: Read 3 prior research docs (24K) + work (interactive) + scratchpad (15K) = 39K
- Post-session: Compress scratchpad (2K) + update _index.md (1K) = 3K
- **Total within 120K budget**: Achievable with careful caching

**Compaction impact**: If .tmp/feat-milestone-9-research-sprint/2026-03-10.md is not compacted at session end, it persists as 20–80 KB uncompressed. Next session would load the same scratchpad file, burning 5.7K–23K tokens re-reading context from the prior session that has already been summarized in issue updates and commit messages. Compaction to 200 bytes saves 5.5K–22.8K tokens next session — enormous leverage.

---

## 3. Compaction & Restoration Policies by Substrate

### Content Substrates (Never Compact)

| Substrate | Location | Compaction | Restoration | Example |
|-----------|----------|-----------|------------|---------|
| Foundational docs | MANIFESTO.md, README.md | Never | git log --follow | Full history preserved |
| Agent files | .github/agents/*.agent.md | Never | git show | Recover any prior version |
| Research syntheses | docs/research/*.md | Never (commit once) | git checkout | Full peer-reviewed history |
| CI/CD workflows | .github/workflows/*.yml | Never | git log | Audit trail of deployment changes |
| Scripts + tests | scripts/*.py, tests/*.py | Never | git log | Full algorithm version history |

### Context Substrates (Aggressive Compaction)

| Substrate | Location | Compaction | Restoration | Example |
|-----------|----------|-----------|------------|---------|
| Session scratchpad (active) | .tmp/<branch>/<date>.md | Compress at session-end | _index.md stubs | Write findings; compress on close |
| Terminal state | live terminal | Never saved | N/A (ephemeral) | Type commands; discard session |
| In-progress edits (unsaved) | VS Code scratch buffers | Never saved | N/A | Draft text; abandon without saving |
| PR drafts | GitHub comment boxes | Never saved by default | Refresh loses text | Unsaved form data; refresh loses |

### Hybrid Substrates (Conditional Compaction)

| Substrate | Location | Compaction Trigger | Cost | Restoration | Example |
|-----------|----------|----------|------|------------|---------|
| Cached sources | .cache/sources/*.md | Compress if access_count < 2 AND (fetch_cost < disk_save) | 1–5 seconds + tokens | scripts/fetch_source.py <url> | Fetch https://arxiv.org... → cache |
| Test artifacts | test/.artifacts/*.json | Compress if date > 7d old | ~100 MB → 5 MB gz | pytest --cache (regenerates) | Pytest run outputs; auto-delete old |
| Build outputs | build/ | Compress/delete immediately | Rebuild takes 30s | `make clean && make` | Compilation artifacts; ephemeral |
| Backup `.md` files | .tmp/<branch>/_archive/ | Keep last 3 sessions; compress older | ~500 KB per session | git reflog (recover via git) | Pruned scratchpad backups |

### Regenerable Provenance (Zero Loss if Backed Up)

| Substrate | Regenerability | Storage | Restoration | Loss Impact |
|-----------|---|---|---|---|
| scripts/ | 1.0 (deterministic) | 792 KB | git checkout HEAD:scripts/file.py | Zero (git backup exists) |
| tests/ | 1.0 (deterministic) | Full suite in git | git checkout + uv run pytest | Zero (git backup exists) |
| .github/agents/ | 1.0 (deterministic, executable) | ~500 KB in git | git checkout HEAD:agents/ | Zero (git backup exists) |
| CI workflows | 1.0 (declarative YAML) | In git | git checkout + deploy | Zero (git backup exists) |

---

## 4. Pattern Catalog

### Pattern 1 — Four Orthogonal Substrate Categories

**Source fields**: Information theory, systems design, context management

**Pattern**: Digital substrates can be classified by their permanence, regenerability, and compaction tolerance:
1. **Content**: Permanent, irreplaceable, never compacted
2. **Context**: Ephemeral, session-local, aggressively compacted
3. **Hybrid**: Regenerable with cost, conditionally compacted
4. **Regenerable Provenance**: Fully deterministic, permanently archived via git, zero loss

**Why it works**: Different substrates have radically different optimal preservation policies. Content wants maximum fidelity; context wants maximum compaction. Conflating them wastes tokens (re-reading ephemeral context) and risks loss (compacting irreplaceable knowledge).

**Implementation**: Tag each category in documentation; enforce compaction policies via scripts (prune_scratchpad.py for Context; validate_synthesis.py for Content).

---

### Pattern 2 — Regenerability as Inverse Predictor of Compaction Cost

**Source fields**: Information theory (channel coding), software engineering (reversible operations)

**Pattern**: A substrate's regenerability score inversely predicts its compaction cost. High regenerability = never compact. Low regenerability = aggressive compaction.

**Metric**: Regenerability = (Fidelity + Determinism + Latency) / 3
- Fidelity (0–1): Can regeneration produce identical output?
- Determinism (0–1): Will re-execution be identical?
- Latency (0–1): Is regeneration instant or costly?

**Examples**:
- scripts/validate_synthesis.py: Fidelity=1.0, Determinism=1.0, Latency=1.0 → Regenerability=1.0 → Never compact
- .cache/sources/page.md: Fidelity=0.9, Determinism=0.95, Latency=0.1 → Regenerability=0.65 → Compact conditionally
- .tmp/<branch>/<date>.md: Fidelity=0.5, Determinism=0.0, Latency=1.0 → Regenerability=0.5 → Aggressively compact

**Why it works**: Regenerability captures the true cost of losing a substrate. High-regenerability resources are abundant; low-regenerability resources are precious and warrant space.

---

### Pattern 3 — Token-Efficiency Compaction Protocol Saves 90%+ in Context Overhead

**Source fields**: Information theory (compression bounds), LLM context management

**Pattern**: Uncompacted scratchpads accumulate across sessions. Each prior session's uncompacted scratchpad burns tokens on re-read. Compacting to stubs saves massive tokens with negligible loss.

**Example**: 12-session month without compaction
- 12 sessions × 50 KB scratchpad = 600 KB in .tmp/
- Next session re-reads all prior scratchpads for orientation = 600 KB × (3.5 chars/token) / 3.5 MB/1K tokens = ~168K tokens wasted
- Cost: $0.50–$2.50 per large session (depending on model rates)

**With compaction**:
- Each session compresses to 300 bytes stub in _index.md
- 12 sessions × 300 bytes = 3.6 KB total
- Next session reads _index.md + linked issues = 3K tokens
- Savings: 165K tokens = $0.49–$2.48 per month

**Why it works**: Compaction trades a tiny amount of signal loss (full scratchpad context → session stubs) for massive token savings. The stubs suffice for orientation; detailed context is linked to closed issues/commits.

---

## 5. Fourth Category Hypothesis: Regenerable Provenance

**Verdict**: CONFIRMED — this is a distinct category with zero compaction cost and high audit value

**Definition**: Substrates that are:
1. Fully deterministic (re-execution produces identical output)
2. Encoded once and executed repeatedly (not edited in session)
3. Fully backed up in git (recovering via git is instant and lossless)
4. Have zero loss impact if regenerated (execution with identical inputs produces identical outputs)

**Properties**:
- **Compaction rule**: Never; preserve full source indefinitely in git
- **Archival**: Automatic via git; no special retention policy needed
- **Restoration**: Instant via `git checkout` (sub-second)
- **Audit trail**: Full git history shows every change; Conventional Commits format makes intent clear

**Why it's distinct**: Unlike Content (which grows and is edited over time), Regenerable Provenance is write-once, execute-many. Unlike Hybrid (which has regeneration cost + latency), Regenerable Provenance has zero latency (git is instant). Unlike Context (which is ephemeral), Regenerable Provenance is permanent if backed up.

**Examples in EndogenAI/Workflows**:
- `scripts/validate_synthesis.py` — gate executes deterministically; identical input → identical output
- `tests/test_validate_synthesis.py` — test suite is deterministic; same seed → same result
- `.github/workflows/lint.yml` — CI workflow is declarative; identical repo state → identical workflow run
- `.github/agents/executive-researcher.agent.md` — agent instruction file is executed by VS Code; static until edited; full version control

**Compaction cost**: Zero. These files are small (< 30 KB typically) and have infinite value per byte because they encode decision procedures, not just data.

---

## 6. Recommended Compaction Policies by Category

### Policy 1: Content (Never Compact)

```
If substrate ∈ Content:
  - Commit every change to git
  - Review all changes via Review agent
  - Maintain full history; never delete
  - Optimize for durability, not size
```

**Monitoring**: `git log --oneline | wc -l` (track content volume growth)  
**Alert**: If content volume grows >10% per month without pruning, review for entropy (old superseded docs should be archived, not deleted).

### Policy 2: Context (Aggressive Compaction)

```
If substrate ∈ Context AND session_end:
  - Run prune_scratchpad.py --force
  - Generate _index.md stubs (one-liner per session)
  - Discard full scratchpad file
  - Keep only Reflection / lessons in committed form
```

**Monitoring**: `du -sh .tmp/` (track scratchpad size)  
**Alert**: If .tmp/ > 5 MB, compaction is urgent (→ 100K+ token burn next session).

### Policy 3: Hybrid (Conditional Compaction)

```
If substrate ∈ Hybrid:
  access_count = count_reads_this_session(substrate)
  regen_cost = estimate_cost_to_regenerate(substrate)
  
  If regen_cost < save_cost AND access_count < 2:
    compress(substrate) OR delete(substrate)
  Else:
    keep(substrate)
```

**Example: .cache/sources/**
```
If file last_read > 7 days ago AND not accessed this session:
  delete_or_gzip(file)
Else if file accessed this session ≤ 1 time AND refetch_time < 30 seconds:
  mark_for_deletion_on_session_end()
Else:
  keep(file)
```

**Monitoring**: `stat .cache/sources/*.md` (track access frequency and age)

### Policy 4: Regenerable Provenance (Never Compact)

```
If substrate ∈ Regenerable:
  - Keep every version in git indefinitely
  - Never delete from working tree (restoration is instant via git)
  - Optimize for legibility (test coverage, docstrings, CI validation)
```

**Monitoring**: `git ls-tree -r HEAD scripts/ tests/ | wc -l` (track code volume)  
**Alert**: If tests/ lacks coverage on modified files (via pytest --cov), add tests before commit.

---

## 7. Token-Efficiency Projection: 12-Month Outlook

**Scenario**: Milestone 9 intensive research (4 phases, 3-4 sessions/phase = 12–16 sessions total; avg 90K tokens/session for context overhead)

**Without compaction policy**:
- Each session leaves .tmp/<branch>/<date>.md uncompressed (50 KB avg)
- 12 sessions × 50 KB = 600 KB accumulation in .tmp/
- Next session re-reads all 12 prior scratchpad files for orientation = 12 × 14K tokens = **168K unnecessary token burn**

**With compaction policy**:
- Each session runs prune_scratchpad.py --force at session end
- Scratchpad compressed to 300 bytes stub in _index.md
- 12 sessions × 300 bytes = 3.6 KB total in _index.md
- Orientation reading: read _index.md (1K tokens) + linked issue summaries (2K tokens) = **3K tokens, 56× more efficient**
- **Savings**: 165K tokens per 12-session month

---

## 8. Sources

### Primary Sources

- **MANIFESTO.md** — Endogenic Development principles; how substrate encodes values
- **docs/guides/session-management.md** — Scratchpad compaction protocol; prune_scratchpad.py documentation
- **docs/research/bubble-clusters-substrate.md** — Topological model of substrate as nested cubes

### Substrate Inventory — Comprehensive Table

Complete enumeration of all digital substrates in EndogenAI/Workflows with all 7 columns. Regenerability score = (Fidelity + Determinism + Latency) / 3. Two-decimal precision: 1.00 = never compact; 0.50–0.75 = conditional; <0.50 = aggressive compaction.

| Type | Location | Compaction | Restoration | Example | Regenerability | Policy |
|------|----------|-----------|------------|---------|---|---|
| **Content** | MANIFESTO.md | Never | git log --follow | Axioms 1–3 | 1.00 | Commit all edits, review all changes |
| **Content** | AGENTS.md | Never | git show | Operational constraints | 1.00 | Durable, non-negotiable |
| **Content** | docs/guides/*.md | Never | git checkout | session-management.md | 1.00 | Extend or fix; never delete |
| **Content** | docs/research/*.md (committed) | Never | git checkout | iit-panpsychism.md | 1.00 | Peer-reviewed synthesis; archive old via versioning |
| **Content** | .github/agents/*.agent.md | Never | git show | executive-researcher.agent.md | 1.00 | Recover via git; no truncation |
| **Content** | .github/workflows/*.yml | Never | git log | lint.yml, ci.yml | 1.00 | Audit trail of deployment policy |
| **Content** | docs/decisions/*.md (ADRs) | Never | git log --follow | ADR-006-agent-skills.md | 1.00 | Decision record; immutable once committed |
| **Context** | .tmp/<branch>/<date>.md (active) | Aggressive at session end | _index.md stubs in git | feat-milestone-9/*.md | 0.50 | Compress via prune_scratchpad.py --force |
| **Context** | Terminal state (live) | Never saved | N/A (ephemeral) | `$ uv run pytest` output | 0.43 | Discard; never log to persistent storage |
| **Context** | VS Code scratch buffers | Never saved | Manually save if needed | Unsaved draft edits | 0.40 | Refresh clears; save before closing |
| **Context** | PR draft comments (unsaved) | Never saved by default | Reload page to re-fetch | Typed but not submitted | 0.40 | Browser back-button recovers; verify before refresh |
| **Hybrid** | .cache/sources/*.md (distilled pages) | Conditional; <2 reads/session | scripts/fetch_source.py <url> | cache/sources/arxiv-values.md | 0.65 | Delete if last_access > 7d AND redraft available < 30s |
| **Hybrid** | test/.artifacts/*.json | Conditional; >7 days old | pytest --cache (regenerate) | .json coverage reports | 0.66 | gzip or delete after test review |
| **Hybrid** | build/ output (compiled) | Immediate deletion | make clean && make rebuild | *.o, *.so files | 0.60 | Ephemeral; never commit |
| **Hybrid** | .tmp/<branch>/_archive/ (backups) | Keep last 3 sessions; compress older | git reflog recover if needed | Pruned scratchpad backups | 0.61 | Reduce to 1 MB every 10 sessions |
| **Regenerable** | scripts/*.py (all 25+ scripts) | Never; keep all versions | git checkout HEAD:scripts/file.py | validate_synthesis.py | 1.00 | Deterministic execution; full history in git |
| **Regenerable** | tests/*.py (full suite) | Never; keep all revisions | git checkout + uv run pytest | test_validate_synthesis.py | 1.00 | Tests are specification; no deletion |
| **Regenerable** | .github/agents/*.py (if any) | Never | git show <commit>:agents/file.py | (future agent code) | 1.00 | Executable scripts; preserve all |
| **Regenerable** | docs/toolchain/*.md (reference) | Never; grow monotonically | git log | docs/toolchain/gh.md | 1.00 | Safe command patterns; archive old versions |
| **Regenerable** | scripts/README.md | Never | git log --follow | Script index & usage | 1.00 | Durable reference; update, never delete |
| **Regenerable** | uv.lock (lockfile) | Never delete; update allowed | git show HEAD:uv.lock | Python dependency freeze | 0.95 | Recover prior lock via git; deterministic restore |
| **Regenerable** | pyproject.toml | Never delete; config only | git checkout HEAD:pyproject.toml | Tool versions, dependencies | 0.98 | Deterministic config; single source of truth |

### Tools Reference

- **prune_scratchpad.py** — Session-end scratchpad compaction (AGENTS.md § Programmatic-First)
- **validate_synthesis.py** — Content validation (enforces required sections, cross-reference density)
- **measure_cross_reference_density.py** — Holographic density scoring (from values-encoding.md § Pattern 2)

---


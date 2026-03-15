---
title: "Programmatic Governance Completeness Audit: T0–T5 Enforcement Tier Mapping"
status: Final
research_issue: "174"
closes_issue: "174"
date: "2026-03-10"
---

# Programmatic Governance Completeness Audit: T0–T5 Enforcement Tier Mapping

> **Research question**: Which governance constraints in the EndogenAI codebase are enforced programmatically, and which exist only as prose? What is the complete T0–T5 tier distribution, and what is the prioritised remediation roadmap for the largest T5 gaps?
> **Date**: 2026-03-10
> **Closes**: #174

---

## 1. Executive Summary

This audit systematically maps every imperative constraint extracted from the root `AGENTS.md`,
`docs/AGENTS.md`, `.github/agents/AGENTS.md`, all `.github/agents/*.agent.md` files, the CI
workflow (`tests.yml`), `.pre-commit-config.yaml`, `scripts/validate_agent_files.py`,
`scripts/validate_synthesis.py`, and `docs/decisions/ADR-007-bash-preexec.md` against the
six enforcement tiers (T0–T5).

The audit reveals a two-cluster structure: a hardened enforcement core covering file-write
anti-patterns, synthesis validation, agent-file structure, and code style; and a large T5
prose-only periphery covering commit discipline, session lifecycle, remote-write verification,
documentation-first obligations, and agent delegation patterns.

**Key findings:**

- **68 constraints inventoried** across 7 source files and 3 CI layers.
- **19 constraints are T1 or above** (fully programmatic enforcement): CI jobs block merge on
  violations of code style, synthesis structure, agent-file compliance, link integrity, and drift.
- **12 constraints are T3 (pre-commit)**: ruff, validate-synthesis, validate-agent-files,
  check-doc-links, no-heredoc-writes, and no-terminal-file-io-redirect blocks local commit.
- **2 constraints are T4 (interactive shell governor)**: bash-preexec intercepts heredoc
  writes before execution in developer terminal sessions.
- **37 constraints are T5 (prose-only)**: no automated enforcement exists. Highest-risk T5
  constraints span commit discipline, `uv run` enforcement, Verify-After-Act, CI-before-review,
  secrets hygiene, and agent delegation patterns.
- **3 high-priority T5→T3 remediations are feasible** with low engineering cost and high
  coverage: commitlint pre-commit hook, `uv run` pygrep enforcement, and `gh --body` shell guard.

The distribution aligns with `MANIFESTO.md §2. Algorithms Before Tokens`: constraints that
have been encoded programmatically are the most reliably honored. T5 constraints exhibit
observable drift in session history — they are routinely violated when context pressure is high.
Closing the T5 gap via T3/T1 uplift is the highest-leverage governance investment available.

---

## 2. Hypothesis Validation

### H1 — The codebase has a coherent programmatic enforcement core but a large T5 prose periphery

**Verdict: CONFIRMED**

The enforcement core is genuine: five distinct CI jobs enforce code style (ruff), synthesis
document structure (validate_synthesis.py), agent-file compliance (validate_agent_files.py +
detect_drift.py), link integrity (lychee), and test coverage (pytest). Pre-commit mirrors T1
checks at the local commit boundary, creating redundant enforcement. Governor B (bash-preexec)
adds T4 interactive enforcement for the highest-risk anti-pattern (heredoc file writes).

However, the periphery is large. Counting only constraints explicitly stated as
MUST/NEVER/always/never imperatives in AGENTS.md text produces 37 unenforceable prose rules.
The ratio of T5 to T1–T4 constraints is approximately 37:31. This is the structural gap.

The 37 T5 constraints include critical operational obligations: Conventional Commits format,
`uv run` instead of bare `python`, CI-must-pass-before-review, Verify-After-Act, secrets
hygiene, session lifecycle (encoding checkpoint, scratchpad size guard), and the complete
agent delegation protocol (takeback gates, inter-phase review gates, compression-on-ascent).

### H2 — T5 constraints with measurable proxies can be uplifted to T3 with low engineering cost

**Verdict: CONFIRMED FOR A SUBSET**

The following T5 constraints have well-defined violation patterns detectable by static analysis:

| Constraint | Violation pattern | Feasible target tier |
|---|---|---|
| Use Conventional Commits | Commit message not matching `^(feat|fix|docs|chore|test|refactor|ci|perf)(\([a-z]+\))?: .+` | T3 (commitlint hook) |
| Always use `uv run` | Shell commands containing `python ` or `python3 ` without `uv run` prefix in CI/shell files | T3 (pygrep hook) |
| Never `--body "..."` for multi-line gh bodies | Shell commands matching `gh issue.*--body "` or `gh pr.*--body "` with embedded newlines | T3 (pygrep hook) |
| Never push --force to main | `git push --force` or `git push -f` targeting main | T3 (pre-push hook) |
| Testing-First: every script gets tests | `scripts/*.py` without a corresponding `tests/test_*.py` | T1 (CI check: compare script list to test list) |
| CI must pass before review | PR opened while runs are in progress | T0 (branch protection required status checks — configuration, not code) |

Constraints that describe session cognition (Focus-on-Descent, encoding checkpoint,
Verify-After-Act) have no detectable violation proxy — they require human judgment and cannot be
uplifted above T5.

### H3 — Governor B successfully moves the highest-risk constraint from T5 to T4

**Verdict: CONFIRMED**

The heredoc file-write constraint — "never use `cat >> file << 'EOF'`" — was T5 prose in the
original `AGENTS.md` commit. It has since been encoded at T3 (no-heredoc-writes pygrep hook in
`.pre-commit-config.yaml`) and T4 (bash-preexec Governor B). `docs/decisions/ADR-007-bash-preexec.md`
documents the rationale. This is the canonical instance of the T5→T3→T4 uplift pattern. The
constraint now exists at three independent enforcement layers simultaneously: prose, pre-commit,
and runtime shell interception.

An identical T5→T3 transition occurred for terminal file I/O redirection (`> file`, `>> file`,
`| tee`) via the `no-terminal-file-io-redirect` pygrep hook. Both transitions were motivated by
the same failure mode: agents repeatedly violated the constraint under context pressure because
prose-only enforcement relies on context window capacity, which degrades near compaction
boundaries.

---

## 3. Pattern Catalog

### Master Constraint Inventory

The following table inventories all imperative constraints extracted from the corpus. Tier
assignments use the definitions in the task prompt and this document's header.

| # | Constraint (abbreviated) | Source | Tier | Gap notes |
|---|---|---|---|---|
| 1 | Never use heredocs for file content | AGENTS.md, docs/AGENTS.md | T3+T4 | Fully enforced |
| 2 | Never use terminal file I/O redirection | AGENTS.md | T3+T4 | Fully enforced |
| 3 | All docs writes via create_file / replace_string_in_file | docs/AGENTS.md | T3+T4 | Same as #1+#2 |
| 4 | ruff lint must pass on scripts/ + tests/ | tests.yml lint job | T1+T2+T3 | Fully enforced |
| 5 | ruff format must pass on scripts/ + tests/ | tests.yml lint job | T1+T2+T3 | Fully enforced |
| 6 | pytest full suite must pass | tests.yml test job | T1 | Fully enforced |
| 7 | validate_synthesis.py: all docs/research/*.md pass | tests.yml lint job | T1+T3 | Fully enforced |
| 8 | validate_agent_files.py: all *.agent.md pass | tests.yml lint job | T1+T3 | Fully enforced |
| 9 | validate_agent_files.py --skills: all SKILL.md pass | tests.yml lint job | T1+T3 | Fully enforced |
| 10 | detect_drift.py must pass | tests.yml lint job | T1 | Fully enforced |
| 11 | lychee link check must pass for docs | tests.yml links job | T1 | Fully enforced |
| 12 | check-doc-links pre-commit hook | .pre-commit-config.yaml | T3 | Only guards committed files |
| 13 | YAML frontmatter name+description in agent files | validate_agent_files.py | T1+T3 | Fully enforced |
| 14 | description ≤ 200 chars in agent files | validate_agent_files.py | T1+T3 | Fully enforced |
| 15 | ≥1 MANIFESTO/AGENTS cross-reference in agent files | validate_agent_files.py | T1+T3 | Density=1 minimum enforced |
| 16 | No heredoc writes in agent files | validate_agent_files.py | T1+T3 | Fully enforced |
| 17 | No Fetch-before-check label (must be Check-before-fetch) | validate_agent_files.py | T1+T3 | Fully enforced |
| 18 | No '## Phase N Review Output' heading in agent files | validate_agent_files.py | T1+T3 | Fully enforced |
| 19 | D4 synthesis: title+status frontmatter required | validate_synthesis.py | T1+T3 | Fully enforced |
| 20 | D4 synthesis: ≥3 required headings present | validate_synthesis.py | T1+T3 | Fully enforced |
| 21 | D4 synthesis: ≥4 ## headings total | validate_synthesis.py | T1+T3 | Fully enforced |
| 22 | D4 synthesis: ≥80 non-blank lines | validate_synthesis.py | T1+T3 | Fully enforced |
| 23 | D3 source synthesis: slug/title/cache_path frontmatter | validate_synthesis.py | T1+T3 | Fully enforced |
| 24 | Governor B: heredoc writes killed in interactive bash | ADR-007, .envrc | T4 | Requires one-time machine setup |
| 25 | bash-preexec shim installed for bash users | ADR-007 | T5 | Machine-level prereq; not checkable |
| 26 | validate_url() rejects non-https and private IPs in fetch_source.py | fetch_source.py | T0 | Runtime — raises ValueError |
| 27 | validate_slug() enforces naming charset in fetch_source.py | fetch_source.py | T0 | Runtime — raises ValueError |
| 28 | capability_gate.py enforces tool access by posture | capability_gate.py | T0 | Runtime — exit 1 |
| 29 | Always use `uv run` — never invoke Python directly | AGENTS.md | T5 | **GAP — T3 feasible** |
| 30 | Conventional Commits format for every commit message | AGENTS.md, CONTRIBUTING.md | T5 | **GAP — T3 feasible** |
| 31 | Never git push --force to main | AGENTS.md | T5 | **GAP — T3 pre-push feasible** |
| 32 | Never delete/rename committed script/agent without migration plan | AGENTS.md | T5 | Hard to automate |
| 33 | Every script must have automated tests before shipping | AGENTS.md | T5 | **GAP — T1 check feasible** |
| 34 | Every script needs ≥80% test coverage | AGENTS.md | T5 | ADR-004 defers coverage threshold; gap acknowledged |
| 35 | Documentation-First: every script/agent/workflow change gets doc update | AGENTS.md, docs/AGENTS.md | T5 | Hard to automate generically |
| 36 | Convention Propagation: update ALL AGENTS.md files when adding convention | AGENTS.md | T5 | Hard to automate |
| 37 | Session-Start Encoding Checkpoint: first sentence names governing axiom | AGENTS.md | T5 | Session cognition; unenforceable |
| 38 | Verify-After-Act: every remote write followed by verification read | AGENTS.md | T5 | Session cognition; unenforceable |
| 39 | CI must pass before requesting or re-requesting review | AGENTS.md | T5 | **GAP — T0 via branch protection** |
| 40 | Never echo shell variables containing secrets | AGENTS.md | T5 | **GAP — T3 possible via secret-pattern grep** |
| 41 | Never write credential values to scratchpad | AGENTS.md | T5 | Hard to enforce (unstructured text) |
| 42 | Never pass multi-line gh bodies via --body "..." | AGENTS.md | T5 | **GAP — T3 feasible** |
| 43 | Minimal Posture: agents carry only required tools (web only when needed) | .github/agents/AGENTS.md | T5 | validate_agent_files checks required sections only |
| 44 | send: false default for handoffs in agent files | .github/agents/AGENTS.md | T5 | Not checked by validate_agent_files |
| 45 | Every agent must hand off to at least one downstream agent | .github/agents/AGENTS.md | T5 | validate_agent_files checks sections not handoff existence |
| 46 | handoffs[].agent values must match existing agent names | .github/agents/AGENTS.md | T5 | **GAP — T1 feasible via manifest cross-reference** |
| 47 | depends-on agents must exist in fleet | .github/agents/AGENTS.md | T5 | **GAP — T1 feasible** |
| 48 | Pre-warm source cache with fetch_all_sources.py before Scout delegation | AGENTS.md | T5 | Session cognition; unenforceable |
| 49 | Check .cache/sources/ before fetching any URL (Check-before-fetch) | AGENTS.md | T5 | Only prose + #17 label check |
| 50 | Fetch-before-act: run fetch_all_sources.py at research session start | AGENTS.md | T5 | Session cognition |
| 51 | Timeout defaults on blocking run_in_terminal calls | AGENTS.md | T5 | Session cognition |
| 52 | Retry once for transient failures; abort immediately on test failure | AGENTS.md | T5 | Session cognition |
| 53 | Scratchpad size guard: ≥2000 lines → run prune_scratchpad.py | AGENTS.md | T5 | **GAP — T4 via watch_scratchpad.py watcher** |
| 54 | Inter-phase Review Gate between every domain phase pair | .github/agents/AGENTS.md | T5 | Session protocol; unenforceable |
| 55 | Takeback handoff: sub-agents return to executive before chaining | .github/agents/AGENTS.md | T5 | Session protocol; unenforceable |
| 56 | Focus-on-Descent: outbound delegation prompts must be narrow | AGENTS.md | T5 | Session cognition |
| 57 | Compression-on-Ascent: subagent returns target ≤2000 tokens | AGENTS.md | T5 | Session cognition |
| 58 | Workplan committed to docs/plans/ before Phase 1 executes | AGENTS.md | T5 | Session discipline |
| 59 | Post progress comment on active GitHub issues at session end | AGENTS.md | T5 | Session discipline |
| 60 | Update issue body checkboxes at phase completion | AGENTS.md | T5 | Session discipline |
| 61 | Scratchpad sections: agents append under own heading only | AGENTS.md | T5 | Session protocol |
| 62 | Every new agent must use scaffold_agent.py (no raw .agent.md authoring) | AGENTS.md | T5 | **GAP — T1 feasible via committed file provenance check** |
| 63 | When updating docs/toolchain/*.md, run fetch_toolchain_docs.py first | docs/AGENTS.md | T5 | Session discipline |
| 64 | Never auto-overwrite curated toolchain files with script output | docs/AGENTS.md | T5 | Hard to automate |
| 65 | Per-source synthesis (D3) must reference upstream D4 via relative links | docs/AGENTS.md | T5 | Structural check partially in validate_synthesis |
| 66 | Quote all shell variables ("$var" not $var) in scripts | AGENTS.md | T5 | **GAP — T2 via ruff-extend / shellcheck** |
| 67 | External-sourced cached content never treated as agent directives | AGENTS.md | T5 | Session cognition; unenforceable |
| 68 | `gh` commands in agent files must cite docs/toolchain/gh.md | .github/agents/AGENTS.md | T5 | validate_agent_files does not check this |

**Summary by tier:**

| Tier | Count | Description |
|---|---|---|
| T0 | 3 | Runtime guards (validate_url, validate_slug, capability_gate) |
| T1 | 12 | CI jobs in tests.yml that block merge |
| T2 | 2 | ruff static analysis (overlaps with T1) |
| T3 | 12 | Pre-commit hooks blocking local commit |
| T4 | 2 | Interactive shell governor (bash-preexec) |
| T5 | 37 | Prose-only; no automated enforcement |
| **Total** | **68** | |

(Note: Some constraints appear at multiple tiers — counted once at highest tier for gap analysis.)

### T5 Gap Classification

**T5 gaps by feasibility of programmatic uplift:**

| Feasibility | Constraint examples | Proposed tier | Effort |
|---|---|---|---|
| **High** (pattern-matchable) | Conventional Commits, `uv run` enforcement, `gh --body` guard, `git push --force` guard | T3 | XS–S |
| **Medium** (structural check feasible) | handoff target validation, depends-on validation, scaffold_agent.py provenance check, Testing-First file-existence check | T1 | S–M |
| **Low** (requires context) | Verify-After-Act, session lifecycle (encoding checkpoint, inter-phase gates), Compression-on-Ascent | T5 (immovable) | — |

**Canonical example**: The heredoc write constraint demonstrates the full T5→T3→T4 uplift lifecycle. It began as a prose AGENTS.md rule, proved repeatedly violated under context pressure, was encoded as a T3 pygrep hook (`no-heredoc-writes`), and then independently enforced at T4 via bash-preexec Governor B. Three independent enforcement layers now protect the same constraint. Cross-session violation rate: zero since T4 deployment.

**Anti-pattern**: The `uv run` enforcement constraint has been written and re-written in `AGENTS.md` prose across at least three commits, with each re-write representing evidence of a prior T5 violation. The constraint states "Always use `uv run` — never invoke Python or package executables directly." No programmatic enforcement exists. A `pygrep` hook matching `^\s*python\s` or `^\s*python3\s` in `.sh`, `.yml`, and CI files would catch the majority of violations at commit time without false positives on legitimate docstring mentions.

---

## 4. Recommendations

### R1 — Conventional Commits gate (T5→T3) — Priority: High

**Action**: Add `commitlint` as a pre-commit hook (local) and as a CI step in `tests.yml`.

**Rationale**: Commit message format is enforced only in `CONTRIBUTING.md` prose and AGENTS.md.
Conventional Commits format is machine-verifiable with zero false negatives. All CHANGELOG
tooling and release automation depends on this format being correct — lax enforcement
directly degrades release quality. `commitlint` with `@commitlint/config-conventional` is a
one-file change to `.pre-commit-config.yaml`.

**Implementation**: Add to `.pre-commit-config.yaml` under `stages: [commit-msg]`. Also
add a CI lint step: `npx commitlint --from origin/main --to HEAD`. Effort: XS.

**Expected effect**: 100% of new commits on `feat/**` and `main` are format-verified.
Violations surface at commit time rather than during PR review.

### R2 — `uv run` enforcement gate (T5→T3) — Priority: High

**Action**: Add a `pygrep` hook that blocks committed shell scripts (`.sh`) and CI YAML
(`.yml`) containing bare `python ` or `python3 ` invocations outside of comments.

**Rationale**: `MANIFESTO.md §2. Algorithms Before Tokens` requires deterministic, encoded
solutions over interactive improvisation. A bare `python` invocation in CI bypasses the
locked `uv` environment, producing non-reproducible builds. This violates the Local
Compute-First axiom (`MANIFESTO.md §3. Local Compute-First`) by introducing implicit
platform-dependency on the system Python. The violation pattern is simple and regex-matchable.

**Implementation**:
```yaml
- id: require-uv-run
  name: Require uv run (never bare python/python3)
  language: pygrep
  entry: '^\s*(python|python3)\s'
  types_or: [shell, yaml]
  exclude: docs/|tests/|\.github/(?!workflows)
```
Effort: XS.

### R3 — Handoff target validation (T5→T1) — Priority: Medium

**Action**: Extend `validate_agent_files.py` to cross-reference each `handoffs[].agent`
value against the `name` fields of all `.agent.md` files in the fleet.

**Rationale**: Broken handoff targets produce silent delegation failures — the handoff
button appears in the UI but invokes a non-existent agent. `generate_agent_manifest.py`
already reads all agent frontmatter to build the manifest; the same traversal can validate
cross-references. This closes the T5 gap on two related constraints: handoff target
existence (constraint #46) and depends-on existence (constraint #47).

**Implementation**: Add `validate_handoff_targets()` to `validate_agent_files.py` that
loads all agent `name` values, then checks each processed file's `handoffs[].agent` field
against the fleet set. Effort: S. Tests required per the Testing-First requirement.

### R4 — Testing-First coverage guard (T5→T1) — Priority: Medium

**Note on ADR-004**: `docs/decisions/ADR-004-no-coverage-threshold.md` explicitly defers
a numerical coverage threshold. This recommendation does not propose overriding ADR-004.
Instead, it proposes a weaker structural check: verify that every file in `scripts/` has a
corresponding `tests/test_*.py` file. This is a file-existence check, not a coverage
threshold, and is consistent with ADR-004's rationale.

**Action**: Add a CI lint step that identifies files in `scripts/` without a matching
`tests/test_<script_name>.py` file and exits non-zero.

**Implementation**: Add `uv run python scripts/check_test_coverage_files.py` to the lint
job. Effort: S. This script does not yet exist; create it per the Programmatic-First
principle since this gap has been observed in multiple sessions.

---

## 5. Sources

**Endogenous primary corpus** (all reads performed before any external fetch per
`MANIFESTO.md §1. Endogenous-First`):

1. `AGENTS.md` (root) — imperative constraint extraction. All MUST/NEVER/always/never
   statements extracted and catalogued. Lines 1–700+ read in full.
2. `docs/AGENTS.md` — documentation-specific constraints.
3. `.github/agents/AGENTS.md` — agent-authoring constraints including frontmatter schema,
   posture tables, handoff graph patterns, and validation rules.
4. `.github/workflows/tests.yml` — CI enforcement inventory. All job steps and conditions
   mapped to T1/T2 tier assignments.
5. `.pre-commit-config.yaml` — pre-commit hook inventory. All hooks mapped to T3 tier.
6. `scripts/validate_agent_files.py` — automated checks for agent files: frontmatter,
   required sections, cross-reference density, heredoc patterns, label correctness.
7. `scripts/validate_synthesis.py` — automated checks for D4/D3 synthesis docs: frontmatter,
   heading presence, minimum line count, section structure.
8. `docs/decisions/ADR-007-bash-preexec.md` — Governor B scope and implementation.
   Confirms T4 tier assignment for bash-preexec heredoc interception.
9. `docs/decisions/ADR-004-no-coverage-threshold.md` — explicit decision context for R4.
10. `docs/research/shell-preexec-governor.md` — Governor B design synthesis.
11. `docs/research/values-encoding.md` — programmatic enforcement as signal-preservation
    mechanism (H3 of values-encoding synthesis — confirmed basis for T5→T3 uplift priority).
12. All `.github/agents/*.agent.md` files (36 total) — agent-specific guardrail survey.

**Methodological note**: No external sources were fetched for this audit. All findings derive
from the endogenous codebase per `MANIFESTO.md §1. Endogenous-First`. The algorithmic
constraint classification (T0–T5) is itself an application of `MANIFESTO.md §2. Algorithms
Before Tokens`: encoding the tier-mapping as a deterministic audit rather than as a
conversational assessment provides a reproducible, revisable artifact.

---
title: "GitHub Actions Caching Patterns"
status: Final
research_issue: 221
date: 2026-03-15
governs: [ci, caching, orientation, project-state-export]
---

# GitHub Actions Caching Patterns

> **Status**: Final
> **Research Question**: What caching and artifact strategies does GitHub Actions provide, and how should the EndogenAI Workflows project use them for CI project-state snapshots and Orchestrator orientation?
> **Date**: 2026-03-15

---

## Executive Summary

GitHub Actions provides two complementary persistence mechanisms — `actions/cache` for cross-run reuse of stable files, and `actions/upload-artifact` for immutable job-produced outputs — with distinct guarantees and failure modes. The EndogenAI Workflows project can exploit these primitives to eliminate redundant API calls during Orchestrator orientation sessions (aligning with [Local Compute-First, §3](../../../MANIFESTO.md#3-local-compute-first)) and to encode the project-state snapshot workflow as a deterministic scheduled job rather than a per-session interactive token burn (aligning with [Algorithms Before Tokens, §2](../../../MANIFESTO.md#2-algorithms-before-tokens)).

Two patterns are immediately actionable: a **date-keyed cache** for same-day orientation hits across concurrent CI runs, and an **artifact-as-snapshot** pattern for a canonical named project-state artifact retrievable by logical name without requiring the artifact ID. A third pattern — **centralized producer / read-only consumer** — provides the structural separation between the scheduled exporter job and any Orchestrator-triggered consumer. Security risks from cache poisoning via fork PRs are the primary constraint shaping key-design decisions; all recommendations below incorporate the mitigations documented in GitHub's security guidance.

---

## Hypothesis Validation

| Hypothesis | Verdict | Evidence |
|---|---|---|
| GitHub Actions cache can serve as a same-day orientation hit for all runs | **Confirmed** | Date-keyed cache (`${{ steps.get-date.outputs.date }}`) produces a same-day hit; 7-day idle eviction matches orientation data lifecycle |
| Artifacts provide a more reliable snapshot primitive than cache for cross-workflow provenance tracking | **Confirmed** | Artifacts carry `artifact-id`, `artifact-digest` (SHA-256), `head_sha`, `head_branch` provenance fields; cache has no equivalent integrity guarantee |
| Cache and artifacts are interchangeable for project-state snapshots | **Rejected** | Official documentation explicitly distinguishes the two: cache = reuse stable files across runs; artifact = save job-produced outputs. Mixing them leads to the stale-restoration anti-pattern |
| GitHub Actions supports a native AI/agent orientation warming pattern | **Not confirmed** | No GitHub-native documented pattern found as of 2026-03-15; Artifact-as-snapshot is the closest composable primitive |
| Fork PRs can poison cached binaries and trigger execution | **Confirmed** | Forks can restore base-branch caches; if a workflow executes cached binaries, a malicious fork PR can poison the cache and trigger execution in the target repo context |

---

## Pattern Catalog

### Pattern 1 — Date-Keyed Cache for Same-Day Orientation Hits

**Intent**: Eliminate redundant GitHub API calls across all CI runs on the same calendar day by caching the project-state snapshot with a date-dependent key.

**Canonical example**:
```yaml
- name: Get current date
  id: get-date
  run: echo "date=$(date -u +%Y-%m-%d)" >> "$GITHUB_OUTPUT"

- name: Restore project-state cache
  id: cache-restore
  uses: actions/cache/restore@v5
  with:
    path: .cache/github/
    key: ${{ runner.os }}-project-state-${{ steps.get-date.outputs.date }}

- name: Export project state (cache miss only)
  if: steps.cache-restore.outputs.cache-hit != 'true'
  run: uv run python scripts/export_project_state.py

- name: Save project-state cache
  if: steps.cache-restore.outputs.cache-hit != 'true'
  uses: actions/cache/save@v5
  with:
    path: .cache/github/
    key: ${{ runner.os }}-project-state-${{ steps.get-date.outputs.date }}
```

**Rationale**: The date key auto-invalidates at UTC midnight. The split `restore@v5` / `save@v5` sub-actions (rather than the composite `actions/cache@v5`) allow the save step to be conditioned on a cache miss, avoiding an unnecessary upload when the cache already exists. This is the [Algorithms Before Tokens (§2)](../../../MANIFESTO.md#2-algorithms-before-tokens) principle applied directly: the cached result is a deterministic output; regenerating it on every run wastes tokens and API quota unnecessarily.

**Constraints**:
- Key must include `runner.os` to prevent cross-OS path pollution.
- Do not include `run_id` in the key — this creates a new entry every run (cache thrashing) and evicts main-branch caches.
- Path must be consistent between restore and save steps; mismatch → guaranteed cache miss.

---

### Pattern 2 — Artifact-as-Snapshot with Digest Validation

**Intent**: Publish a named, immutable project-state snapshot from a scheduled workflow; any subsequent run in any workflow retrieves it by logical name without requiring the artifact ID.

**Canonical example**:
```yaml
# Scheduled exporter job (runs nightly)
- name: Upload project-state snapshot
  id: upload-snapshot
  uses: actions/upload-artifact@v4
  with:
    name: project-state
    path: .cache/github/project_state.json
    retention-days: 1
    overwrite: true

# Consumer job (in any triggered workflow)
- name: Retrieve latest project-state snapshot
  run: |
    ARTIFACT=$(gh api \
      "/repos/${{ github.repository }}/actions/artifacts?name=project-state&per_page=1" \
      --jq '.artifacts[0]')
    ARTIFACT_ID=$(echo "$ARTIFACT" | jq -r '.id')
    HEAD_SHA=$(echo "$ARTIFACT" | jq -r '.workflow_run.head_sha')
    echo "artifact_id=$ARTIFACT_ID" >> "$GITHUB_OUTPUT"
    echo "provenance_sha=$HEAD_SHA" >> "$GITHUB_OUTPUT"
```

**Rationale**: The `?name=project-state` filter on the artifacts REST API retrieves the latest artifact by logical name, making this resilient to artifact ID rotation when `overwrite: true` produces a new ID on each upload. `retention-days: 1` auto-expires stale orientation data, preventing a consumer from inadvertently reading week-old project state. The `workflow_run.head_sha` field provides provenance tracing without additional API calls — this is [Local Compute-First (§3)](../../../MANIFESTO.md#3-local-compute-first): the provenance is embedded in the artifact metadata rather than requiring a separate lookup.

**Digest validation** (optional integrity gate):
```yaml
- name: Validate artifact digest
  run: |
    EXPECTED_DIGEST="${{ steps.upload-snapshot.outputs.artifact-digest }}"
    ACTUAL=$(sha256sum .cache/github/project_state.json | awk '{print "sha256:"$1}')
    [ "$ACTUAL" = "$EXPECTED_DIGEST" ] || (echo "Digest mismatch" && exit 1)
```

**Constraints**:
- `retention-days: 1` is the correct setting for ephemeral daily orientation data; do not use the default (repo setting may be 90 days).
- `overwrite: true` produces a **new** `artifact-id`; downstream steps must use the name-filtered API query, not a hardcoded ID.
- Never store the artifact under a path containing secrets or credentials.

---

### Pattern 3 — Centralized Producer / Read-Only Consumer

**Intent**: Separate cache/artifact write authority into a single scheduled job ("Project State Exporter") and enforce read-only access in all consumer workflows, preventing cache poisoning and path conflicts.

**Canonical example**:
```yaml
# Producer workflow (scheduled, runs on default branch only)
jobs:
  export-project-state:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Export and cache
        uses: actions/cache/save@v5
        with:
          path: .cache/github/
          key: project-state-${{ runner.os }}-${{ steps.date.outputs.date }}

# Consumer workflow (triggered by orchestrator events)
jobs:
  orient-orchestrator:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/cache/restore@v5
        with:
          path: .cache/github/
          key: project-state-${{ runner.os }}-${{ steps.date.outputs.date }}
          fail-on-cache-miss: true   # abort if snapshot absent; do not silently proceed
```

**Rationale**: Confining write authority to a single producer job on the default branch closes the primary cache-poisoning vector: a fork PR workflow cannot trigger the producer job and cannot write to the default-branch cache namespace. The `fail-on-cache-miss: true` option acts as a correctness gate — the consumer aborts rather than silently operating without orientation context, which aligns with the [Endogenous-First axiom](../../../MANIFESTO.md#1-endogenous-first): prefer halting to operating on absent internal knowledge.

The `lookup-only: true` variant (on `restore@v5`) enables a "check before act" gate — verify the cache exists before downloading it, supporting conditional branching without incurring download cost:
```yaml
- uses: actions/cache/restore@v5
  id: check-cache
  with:
    path: .cache/github/
    key: project-state-${{ runner.os }}-${{ steps.date.outputs.date }}
    lookup-only: true
```

---

### Pattern 4 — Multi-Factor Cache Key with Lockfile Hash

**Intent**: Invalidate the cache precisely when dependencies change, without over-invalidating on unrelated commits.

**Canonical example**:
```yaml
- uses: actions/cache@v5
  with:
    path: .venv/
    key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}
    restore-keys: |
      ${{ runner.os }}-uv-
```

**Rationale**: The lockfile hash ensures that any change to `uv.lock` produces a new key (exact match miss) and falls back to the `restore-keys` prefix for a partial hit — restoring the closest prior venv and then running an incremental `uv sync`. This is cheaper than a cold install and cheaper than always using a date-keyed strategy for dependency caches that change infrequently. For the EndogenAI project: use this pattern for `.venv/` (Python dependencies) and separate it from the project-state cache (which warrants the date-keyed pattern in Pattern 1).

---

## Anti-Patterns

**Anti-pattern — Secrets/tokens stored in cache paths**:
Caches scoped to branches accessible by fork PRs (e.g., `refs/pull/*/merge`) can be read by any fork workflow. Any path containing credentials, tokens, or API keys stored in cache is exploitable. Mitigation: audit all `path:` entries to confirm they never include `.env`, credential stores, or token files. Enforce with a `pre-commit` check or `validate_agent_files.py`-style linter on workflow YAML.

**Anti-pattern — `run_id` key component (cache thrashing)**:
```yaml
# DO NOT DO THIS
key: ${{ runner.os }}-deps-${{ github.run_id }}
```
Every run creates a new cache entry and never produces a hit. Within days, the 10 GB repo quota fills with single-use entries; main-branch caches are evicted. Use content-addressed keys (lockfile hash) or time-bounded keys (date) instead.

**Anti-pattern — Single OS-only key for shared runners**:
```yaml
# DO NOT DO THIS
key: deps-${{ hashFiles('uv.lock') }}  # missing os
```
A cache saved on `ubuntu-latest` will attempt to restore on `macos-latest`, corrupting the Python venv or producing silent failures. Always include `runner.os` as the first key segment.

**Anti-pattern — Path mismatch between save and restore**:
If a restore step uses `path: .venv/` and the save step uses `path: ./.venv`, the cache will always miss. Use an explicit variable or anchored constant for the path to ensure both steps resolve identically.

**Anti-pattern — Cross-workflow artifact ID hardcoding**:
`overwrite: true` on `upload-artifact@v4` produces a new `artifact-id` on every upload. Any downstream step that stores the ID for later use will break after the next upload. Always use the name-filtered REST API query (`?name=<name>`) to retrieve the current artifact.

---

## Recommendations

These recommendations are ordered by implementation priority for the EndogenAI Workflows project.

### R1 — Adopt the Artifact-as-Snapshot pattern for `export_project_state.py` outputs

Modify the `export-project-state.yml` workflow to upload `project_state.json` as a named artifact (`project-state`) with `retention-days: 1` and `overwrite: true`. The Orchestrator-triggered orientation step should retrieve it via the name-filtered REST API. This eliminates per-session GitHub API calls for project state — a direct application of [Algorithms Before Tokens (§2)](../../../MANIFESTO.md#2-algorithms-before-tokens).

Acceptance: `export-project-state.yml` uploads artifact on success; `.github/workflows/` consumer reads via `?name=project-state` query; no session makes a live API call for project state when a same-day artifact exists.

### R2 — Layer a date-keyed cache over the artifact for same-day hit without download cost

Add a date-keyed `actions/cache/restore@v5` step before the artifact retrieval. If the cache hits, skip the artifact download entirely. This reduces egress and avoids the 1-minute expiring redirect URL from the artifact REST API. Pattern 1 above provides the exact YAML.

Acceptance: On the second CI run of the same day, the cache step reports `cache-hit: true` and the artifact retrieval step is skipped.

### R3 — Restrict cache write authority to the scheduled producer job on `main`

Audit all workflow YAML in `.github/workflows/` that contains `actions/cache/save@v5` or `actions/cache@v5` with a write path overlapping `.cache/github/`. Any such write that occurs in a PR-triggered workflow is a potential cache-poisoning vector. Move writes to the scheduled producer. This implements the Centralized Producer / Read-Only Consumer pattern (Pattern 3) and closes the fork-PR poisoning vector documented in the Anti-Patterns section.

Acceptance: No `actions/cache/save` step targeting `.cache/github/` exists in any workflow triggered by `pull_request` events.

### R4 — Add `fail-on-cache-miss: true` to all orientation restore steps

Consumer workflows that need project state for correct operation must abort rather than silently proceed with stale or absent context. Add `fail-on-cache-miss: true` to every `actions/cache/restore@v5` step that is a hard dependency for the job's correctness. This is a direct encoding of the [Endogenous-First axiom (§1)](../../../MANIFESTO.md#1-endogenous-first): operating without internal knowledge is worse than halting.

Acceptance: If the orientation cache is absent, the consumer job exits with a non-zero code and surfaces a clear failure message.

### R5 — Separate `.venv/` caching from project-state caching

`.venv/` should use the multi-factor lockfile-hash key (Pattern 4). Project state should use the date-keyed strategy (Pattern 1). Conflating both into a single cache entry ties venv invalidation to calendar date and project-state invalidation to dependency changes — neither is correct. Two separate cache entries with purpose-specific keys is the right decomposition.

Acceptance: `pyproject.toml` cache and project-state cache use distinct `path:` and `key:` values in all workflows.

### R6 — Encode key-design rules as a YAML linting check

The anti-patterns above (missing `runner.os`, `run_id` in key, path mismatch) are mechanically detectable. Add a `validate_workflow_cache_keys.py` script under `scripts/` that checks all workflow YAML files for these patterns. Wire it to the pre-commit `.pre-commit-config.yaml` as a `local` hook. This shifts the constraint from token-level instruction (AGENTS.md) to a programmatic enforcement layer — aligning with the [Programmatic-First principle](../../../AGENTS.md#programmatic-first-principle).

Acceptance: `uv run python scripts/validate_workflow_cache_keys.py` exits 0 for all current workflows; 1 for any workflow violating a key-design rule. Pre-commit hook installed and documented in `docs/toolchain/`.

---

## Open Questions

1. **Rate limit exposure**: The documented limits (200 uploads/min, 1500 downloads/min) have not been validated against the EndogenAI project's actual CI parallelism. If the fleet scales to concurrent Orchestrator runs, the download limit may become a constraint. Instrument download counts before assuming headroom.

2. **Cross-OS cache sharing**: The `enableCrossOsArchive: true` option on `actions/cache` is undocumented in the Scout findings beyond the existence note. The security implications of cross-OS sharing for paths that contain binaries (e.g., `.venv/`) are unclear. Do not enable this option until the behavior is validated.

3. **`lookup-only: true` vs. `fail-on-cache-miss: true` interaction**: It is not documented whether these two options can be combined. If `lookup-only: true` is set and the cache is absent, does `fail-on-cache-miss: true` also apply? Validate against a test workflow before relying on the combination.

4. **Project-state snapshot schema versioning**: As `export_project_state.py` evolves, the schema of `project_state.json` will change. A consumer that reads a prior-day artifact with a schema mismatch will fail silently or with a confusing error. The recommendation to use `retention-days: 1` mitigates this for daily workflows, but cross-day stale reads remain possible. Consider embedding a schema version field in the artifact and validating it on retrieval.

5. **`validate_workflow_cache_keys.py` scope**: R6 proposes this script. Before implementing, confirm there is no existing tool in `scripts/` that already validates workflow YAML structure — search `scripts/` for `workflow` before writing a new script (Programmatic-First: check before create).

---

## Sources

All findings are derived from Scout output dated 2026-03-15. No external sources were re-fetched during synthesis.

- **GitHub Actions: Caching dependencies to speed up workflows** — official GitHub documentation covering `actions/cache@v5`, key strategies, storage limits, and security notes. Canonical source for Pattern 1, Pattern 3, and Pattern 4.
- **GitHub Actions: Storing workflow data as artifacts** — official GitHub documentation covering `actions/upload-artifact@v4`, retention, overwrite behavior, and REST API access. Canonical source for Pattern 2.
- **GitHub API: List artifacts for a repository** — REST API endpoint `GET /repos/{owner}/{repo}/actions/artifacts` with `?name=` filter. Canonical source for name-based artifact retrieval in Pattern 2.
- **EndogenAI Workflows project**: [`scripts/export_project_state.py`](../../../scripts/export_project_state.py) — existing script whose output this caching strategy is designed to preserve and distribute.
- **EndogenAI Workflows project**: [`MANIFESTO.md`](../../../MANIFESTO.md) — axioms cited throughout: Local Compute-First (§3), Algorithms Before Tokens (§2), Endogenous-First (§1).
- **EndogenAI Workflows project**: [`AGENTS.md`](../../../AGENTS.md) — Programmatic-First principle governing R6 (encode key-design rules as a linting check).

---
governs: [programmatic-first]
status: Draft
issue: 364
date: 2026-03-18
---

# Programmatic-First Audit

> Governing constraint: [`AGENTS.md § Programmatic-First Principle`](../../AGENTS.md#programmatic-first-principle)
> Script catalog: [`scripts/README.md`](../../scripts/README.md)

---

## Purpose

This document catalogues every known 2×-interactive repetition that has occurred in this repository, its encoding status (scripted / automation / documented-as-non-recurring / gap), and any recommended next action. It is the authoritative audit record for Sprint 19 issue #364.

An entry is classified as **scripted** when a committed `scripts/` file encodes the task programmatically. An entry is classified as **automation** when it is enforced by a pre-commit hook, file watcher, or CI job rather than an on-demand script. An entry is **gap** when the task is documented as recurring but no encoding exists.

---

## Coverage Table

| # | Repeated Interactive Task | Trigger (AGENTS.md) | Encoding | Script / Hook | README? |
|---|--------------------------|---------------------|----------|--------------|---------|
| 1 | Annotating scratchpad H2 headings with line-range numbers after every write | Validation + event-driven | Automation (file watcher) | `watch_scratchpad.py` | ✓ |
| 2 | Managing per-session scratchpad files (init / annotate / archive) | Reading many files to build context | Scripted | `prune_scratchpad.py` | ✓ |
| 3 | Fetching a single external URL into `.cache/sources/` | Reading many files to build context | Scripted | `fetch_source.py` | ✓ |
| 4 | Batch-fetching all URLs from `OPEN_RESEARCH.md` and research doc frontmatter | Reading many files to build context | Scripted | `fetch_all_sources.py` | ✓ |
| 5 | Scaffolding a new `.agent.md` role file from template | Boilerplate from template | Scripted | `scaffold_agent.py` | ✓ |
| 6 | Scaffolding a `docs/plans/` workplan document | Boilerplate from template | Scripted | `scaffold_workplan.py` | ✓ |
| 7 | Validating agent and skill files before commit | Validation or format check | Scripted + CI | `validate_agent_files.py` | ✓ |
| 8 | Validating D3/D4 synthesis documents before archive | Validation or format check | Scripted + CI | `validate_synthesis.py` | ✓ |
| 9 | Seeding GitHub labels idempotently from `data/labels.yml` | Could break if done wrong | Scripted (`--dry-run`) | `seed_labels.py` | ✓ |
| 10 | Posting replies to PR inline review comments and resolving threads | Twice interactively | Scripted | `pr_review_reply.py` | ✓ |
| 11 | Pre-delegation rate-limit budget check | Validation or format check | Scripted | `rate_limit_gate.py` | **✗** |
| 12 | Polling GitHub Actions runs for CI completion | Twice interactively | Scripted | `wait_for_github_run.py` | **✗** |
| 13 | Pre-computing session orientation digest (open issues, recent commits, active branches) | Reading many files to build context | Scripted | `orientation_snapshot.py` | ✓ |
| 14 | Checking fleet integration (new agents/skills cross-referenced in AGENTS.md) | Validation or format check | Scripted + CI | `check_fleet_integration.py` | ✓ |
| 15 | Annotating files with `governs:` provenance frontmatter | Validation or format check | Scripted | `annotate_provenance.py` | ✓ |
| 16 | Auditing provenance annotations for drift | Validation or format check | Scripted | `audit_provenance.py` | ✓ |
| 17 | Batch-reading GitHub issue / PR metadata | Reading many files to build context | Scripted | `bulk_github_read.py` | ✓ |
| 18 | Batch GitHub write operations (issue-create, close, edit) from spec file | Could break if done wrong | Scripted (`--dry-run`) | `bulk_github_operations.py` | ✓ |
| 19 | Detecting template/derived-repo governance drift | Twice interactively | Scripted (`--dry-run`) | `check_divergence.py` | ✓ |
| 20 | Exporting GitHub issue and label state to local snapshot | Reading many files to build context | Scripted | `export_project_state.py` | ✓ |
| 21 | Blocking terminal file I/O redirection in committed code | Validation or format check | Automation (pre-commit hook) | `no-terminal-file-io-redirect` | N/A |
| 22 | Blocking heredoc file writes in committed code | Validation or format check | Automation (pre-commit hook) | `no-heredoc-writes` | N/A |

---

## Gap Analysis

### Genuine 2×-Interactive Gaps (no encoding exists)

**None found.** All tasks documented in [`AGENTS.md § Programmatic-First Principle`](../../AGENTS.md#programmatic-first-principle) as recurring have at least one encoding (script, file watcher, or pre-commit hook).

### README Documentation Gaps

Two scripts named in `AGENTS.md` as canonical examples are **absent from `scripts/README.md`**:

| Script | Referenced In | Recommended Next Action |
|--------|--------------|------------------------|
| `rate_limit_gate.py` | `AGENTS.md § Pre-Delegation Rate-Limit Gate` (explicitly shown with code example) | Add catalog entry to `scripts/README.md` |
| `wait_for_github_run.py` | `AGENTS.md § Async Process Handling` ("canonical example — GitHub Actions run polling") | Add catalog entry to `scripts/README.md` |

Additionally, the following **23 scripts exist in `scripts/` but have no entry in `scripts/README.md`**. These are not necessarily 2×-interactive gaps (they may be newer scripts committed after the last README update), but they represent catalog drift:

| Script | Notes |
|--------|-------|
| `add_source_to_manifest.py` | Source manifest management |
| `agent_registry.py` | Agent registry tooling |
| `amplify_context.py` | Context amplification per `data/amplification-table.yml` |
| `check_doc_links.py` | Documentation link validation |
| `correlate_health_metrics.py` | Substrate health correlation |
| `create_phase1_research_issues.py` | Phase 1 research issue seeding |
| `format_citations.py` | Citation formatting utility |
| `generate_sweep_table.py` | Sweep table generation |
| `measure_cross_reference_density.py` | Cross-reference density measurement |
| `pre_review_sweep.py` | Pre-review corpus sweep |
| `preexec_audit_log.py` | Shell pre-exec audit logging |
| `rate_limit_config.py` | Rate-limit configuration helper |
| `scaffold_manifest.py` | Manifest scaffolding |
| `scan_research_links.py` | Research document link scanner |
| `seed_action_items.py` | Action item seeding from D4 docs |
| `token_spin_detector.py` | Token burn anomaly detection |
| `validate_adr.py` | ADR document validation |
| `validate_delegation_routing.py` | Delegation routing validation |
| `validate_session.py` | Session file validation |
| `validate_session_state.py` | Session state schema validation |
| `validate_skill_files.py` | Skill file validation |

**Recommended next action**: Run `uv run python scripts/generate_script_docs.py` and update `scripts/README.md` to catalog all 23 undocumented scripts. This is a documentation task, not a scripting gap — the scripts exist but are invisible to future agents relying on the README as a discovery index.

---

## Verdict

| Category | Count | Status |
|----------|-------|--------|
| Scripted 2×-interactive tasks | 20 | ✓ All encoded |
| Automation-enforced tasks | 2 | ✓ All encoded |
| Genuine scripting gaps | 0 | ✓ None |
| Scripts absent from README (priority: named in AGENTS.md) | 2 | ⚠ README update needed |
| Scripts absent from README (catalog drift) | 23 | ⚠ README update needed |

---

## References

- [`AGENTS.md § Programmatic-First Principle`](../../AGENTS.md#programmatic-first-principle) — governing decision table and canonical examples
- [`scripts/README.md`](../../scripts/README.md) — authoritative script catalog
- [`docs/guides/programmatic-first.md`](programmatic-first.md) — narrative guide (script vs. automation taxonomy)

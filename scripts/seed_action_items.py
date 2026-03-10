#!/usr/bin/env python3
"""Seed 29 GitHub issues from research recommendations."""

# ruff: noqa: E501
import subprocess

issues = [
    {
        "title": "validate_session.py — LLM Behavioral Testing Framework",
        "labels": ["type:feature", "area:scripts", "priority:high"],
        "body": """Implement 7-check Tier 1 post-commit script for session scratchpad audits (non-blocking).

## Acceptance Criteria
- `uv run python scripts/validate_session.py <scratchpad>` returns structured audit output
- ≥80% test coverage

Related: #74 focuses on Constitutional AI evaluation, not this implementation spec.

**Source**: docs/research/llm-behavioral-testing.md (R1)""",
    },
    {
        "title": "Tier 2 Behavioral Testing — Drift Detection (Deferred)",
        "labels": ["type:feature", "priority:low"],
        "body": """Defer Tier 2 `validate_session.py --tier2` until (a) local model stack confirmed, (b) issue #13 resolved.

**Rationale**: Premature Tier 2 without local compute violates Local Compute-First; single-session drift detection is weak without episodic memory baseline.

**Blocked by**: #13 (episodic memory) + local compute baseline

**Source**: docs/research/llm-behavioral-testing.md""",
    },
    {
        "title": "Value Fidelity Test Taxonomy for AGENTS.md",
        "labels": ["type:docs", "priority:medium"],
        "body": """Add test taxonomy table to `AGENTS.md §Validate & Gate` as reference for Review agent and human reviewers.

Operationalizes 'value fidelity' — makes assertions explicit and testable.

**Source**: docs/research/llm-behavioral-testing.md (R2)""",
    },
    {
        "title": "Membrane Permeability Specifications in AGENTS.md",
        "labels": ["type:docs", "priority:high"],
        "body": """Add named 'Boundary Specification' for each major research fleet handoff:
- Scout→Synthesizer
- Synthesizer→Reviewer
- Reviewer→Archivist

Each spec lists:
- permitted-signal list (preserve verbatim)
- compression-allowed list
- surface-tension budget (max token count)

**Impact**: Closes 100% canonical-example loss documented in values-encoding.md.

**Source**: bubble-clusters-substrate.md (B1/R1)""",
    },
    {
        "title": "AI-as-Pressurizing-Medium Framing in Session Start Ritual",
        "labels": ["type:docs", "priority:low"],
        "body": """Add one-sentence note to session-start encoding checkpoint:

> "The agent fleet is the pressurizing medium — it gives each substrate coherent form but does not own the membrane or the bucket."

Effort: XS

**Source**: bubble-clusters-substrate.md (R5)""",
    },
    {
        "title": "Evolutionary Pressure Test for Fleet Agent Audit",
        "labels": ["type:docs", "priority:medium"],
        "body": """Apply evolutionary pressure test to every `.github/agents/` file during fleet audit; agents lacking stability-tier and mutation-rate rationale must be merged or justified in `## Beliefs`.

**Prevents**: Spurious agent boundary proliferation.

**Source**: bubble-clusters-substrate.md (B3/R3)""",
    },
    {
        "title": "Operationalize generate_agent_manifest.py Connectivity Atlas",
        "labels": ["type:feature", "area:scripts", "priority:high"],
        "body": """Operationalize the agent manifest tool:

1. Document command and output format in `scripts/README.md`
2. Add manifest validation step to CI on PRs touching `.github/agents/`
3. Define threshold policy in `AGENTS.md` (e.g., density < 1 = PR warning)

**Outcome**: Provides computable substrate health metric.

**Source**: bubble-clusters-substrate.md (B2/R2)""",
    },
    {
        "title": "BM25 Retrieval Tool Completion (scripts/query_docs.py)",
        "labels": ["type:feature", "area:scripts", "priority:medium"],
        "body": """Extend `scripts/query_docs.py` to include `toolchain` and `skills` scopes; add tests covering happy path, empty-scope error, and score-threshold logic (≥80% coverage).

## Acceptance Criteria
- `uv run python scripts/query_docs.py 'programmatic-first' --scope agents --top-n 3` returns three highest-scoring paragraphs within 500 ms
- Tests pass

**Related**: #80 (Queryable substrate — closed)

**Source**: queryable-substrate.md (R1–R3)""",
    },
    {
        "title": "Cross-Reference Link Registry & Automated Weaving Completion",
        "labels": ["type:feature", "area:scripts", "priority:medium"],
        "body": """Complete doc interlinking:

1. Create `data/link_registry.yml` with seed concepts
2. Ensure `scripts/weave_links.py` has `--dry-run`, idempotency guard, `--scope` filter

**Constraints**: No self-referential injection; validated per Programmatic-First.

**Related**: #84 (Doc interlinking — closed)

**Source**: doc-interweb.md (R1–R2)""",
    },
    {
        "title": "Propose_dogma_edit.py — Programmatic Back-Propagation Enforcer",
        "labels": ["type:feature", "area:scripts", "priority:high"],
        "body": """Implement script enforcing back-propagation evidence thresholds (3 sessions for T1/T2, 2 for T3) and generating ADR-style proposals automatically.

## Inputs
- `--input <scratchpad>`
- `--tier T1|T2|T3`
- `--affected-axiom <str>`
- `--proposed-delta <str|->`
- `--output <path>`

## Behavior
- Exit code 1 if T1 and coherence fails

**Related**: #82 (dogma-neuroplasticity research — closed)

**Source**: dogma-neuroplasticity.md (R1)""",
    },
    {
        "title": "Skill File Validation (validate_skill_files.py)",
        "labels": ["type:feature", "area:scripts", "priority:high"],
        "body": """Extend or create `validate_skill_files.py` covering:
- Frontmatter schema
- Name format
- Directory-name match
- Cross-reference density
- Minimum body length

Add to CI lint job.

**Source**: agent-skills-integration.md (R7)""",
    },
    {
        "title": "Verify Agent Skills Implementation Completeness",
        "labels": ["type:chore", "priority:medium"],
        "body": """Verify all 6 Tier 1 + Tier 2 agent skills from #62 are committed, tested, and integrated.

**Expected outcome**: Token duplication reduced (~500 tokens per session per skill).

**Tier 1 skills**:
- session-management
- deep-research-sprint
- conventional-commit

**Related**: #62 (Implement Remaining Agent Skills — closed)

**Source**: agent-skills-integration.md (R1–R3)""",
    },
    {
        "title": "Extended Agent Documentation Standard",
        "labels": ["type:docs", "priority:medium"],
        "body": """Create per-role documentation beyond `.agent.md` — canonical decision trees, tool matrices, worked examples in `docs/agents/[role-name]/`.

**Extends**: #65

**Blocked by**: #65 (Extended agent documentation standard — open)

**Source**: agent-taxonomy.md""",
    },
    {
        "title": "Adopt Wizard Integration with client-values.yml",
        "labels": ["type:feature", "area:scripts", "priority:medium"],
        "body": """Enhance #56: Adopt wizard (`scripts/adopt_wizard.py`) must generate `client-values.yml` stub pre-populated with `conflict_resolution` field and explanatory comment.

**Impact**: Makes Deployment Layer constraint encoding explicit; prevents Core Layer override risk.

**Blocked by**: #56 (feat: implement Adopt onboarding wizard — open)

**Source**: external-value-architecture.md (E1)""",
    },
    {
        "title": "Add Deployment Layer Reading to Session Start Ritual",
        "labels": ["type:docs", "priority:low"],
        "body": """Add conditional step to `AGENTS.md §Session Start Ritual`: If `client-values.yml` exists, read it after `AGENTS.md` and note constraints in `## Session Start`.

Effort: XS

**Source**: external-value-architecture.md (E2)""",
    },
    {
        "title": "Extend validate_agent_files.py for Core Layer Impermeability Check",
        "labels": ["type:feature", "area:scripts", "priority:medium"],
        "body": """Extend `validate_agent_files.py` to flag agent files citing `client-values.yml` as higher-priority than `MANIFESTO.md`/`AGENTS.md` (Supremacy Rule violation).

**Enforcement**: Programmatically per Algorithms Before Tokens.

**Source**: external-value-architecture.md (E3)""",
    },
    {
        "title": "Phase 1 AFS Integration — Index Session to AFS on Session Close",
        "labels": ["type:feature", "area:scripts", "priority:low"],
        "body": """Extend `prune_scratchpad.py --force` with `--index-afs` flag calling `scripts/index_session_to_afs.py`.

**Adoption gate**: Deferred until local embedding stack confirmed (Local Compute-First).

**Blocked by**: #14 (AIGNE AFS Context Governance — open) + local embedding stack

**Source**: aigne-afs-evaluation.md (R4)""",
    },
    {
        "title": "SQLite-only Pattern A1 for AFS — FTS5 Keyword Index",
        "labels": ["type:feature", "area:scripts", "priority:low"],
        "body": """Implement SQLite FTS5 keyword index for AFS before vector embeddings (respects Algorithms Before Tokens).

Phase 1 pattern for pattern-A1. Dependent on #14.

**Blocked by**: #14

**Source**: aigne-afs-evaluation.md (R2)""",
    },
    {
        "title": "Session History Table in Scratchpad Template",
        "labels": ["type:docs", "priority:medium"],
        "body": """Add `## Session History` table to scratchpad template in `docs/guides/session-management.md`.

**Outcome**: Provides zero-infrastructure episodic memory layer for multi-session tracking.

Effort: XS

**Source**: episodic-memory-agents.md (M1)""",
    },
    {
        "title": "Cognee Library Adoption (After Local Compute Baseline)",
        "labels": ["type:research", "priority:low"],
        "body": """When local compute baseline is confirmed, adopt Cognee as preferred library (native Ollama support, graph-based, local-first design).

**Status**: Recommendation deferred pending #13 + local compute setup.

**Blocked by**: #13 (Episodic and Experiential Memory — open) + local compute baseline

**Source**: episodic-memory-agents.md (R3)""",
    },
    {
        "title": "Product User Research Infrastructure",
        "labels": ["type:research", "priority:medium"],
        "body": """Implement user research infrastructure (6 recommendations from product-research-and-design.md):

**R1**: Add JTBD job statement to each `scripts/README.md` entry
**R2**: Add legibility & idempotency checklist to `CONTRIBUTING.md`
**R3**: Create pinned GitHub Discussion: 'Friction & Feature Requests'
**R4**: Adopt README-driven development for new tools (convention)
**R5**: Implement prompt archaeology as post-sprint ritual (scan sessions → encode `.agent.md` examples)
**R6**: Quarterly 'voice of the user' synthesis run (Scout session → `docs/research/` summary)

Framework recommendations exist; no dedicated issue for infrastructure setup.

**Related**: #45 (Research: Product Definition — open)

**Source**: product-research-and-design.md (R1–R6)""",
    },
    {
        "title": "Documentation Site Improvements",
        "labels": ["type:chore", "priority:high"],
        "body": """Batch documentation improvements (specific tasks from oss-documentation-best-practices.md):

**R1**: Create `CHANGELOG.md` (10 min) — DONE
**R2**: Add CI badge + TOC to `README.md` (20 min)
**R3**: Add dev environment setup to `CONTRIBUTING.md` (15 min)
**R4**: Add MkDocs Material docsite (1–2 hours)
**R5**: Add link-checker (lychee) to CI (30 min)
**R6**: Run `validate_synthesis.py` in CI (15 min)

#25, #27 closed but didn't granularly track these.

**Related**: #25 (GitHub PM Setup — closed), #27 (CI/DX Hygiene — closed)

**Source**: oss-documentation-best-practices.md (R1–R6)""",
    },
    {
        "title": "Commit .vscode/mcp.json & Design Endogenic MCP Server",
        "labels": ["type:feature", "area:scripts", "priority:medium"],
        "body": """Commit `.vscode/mcp.json` with GitHub MCP + endogenic filesystem server as default.

Design `scripts/mcp_server.py` wrapping key project scripts as tools (delegate to Executive Scripter for spec).

Integration specifics not independently logged.

**Related**: #6 (Locally distributed MCP frameworks — closed)

**Source**: local-mcp-frameworks.md (recommendations 1–2)""",
    },
    {
        "title": "BDI Framework for Agent File Sections",
        "labels": ["type:docs", "priority:low"],
        "body": """Rename `.agent.md` sections to Beliefs / Desired outcomes / Intentions (BDI cognitive architecture framing).

**Impact**: Zero implementation cost; significant clarity gain. Pure design guidance.

**Source**: methodology-review.md (D2)""",
    },
    {
        "title": "Add Session History Forward Reference to values-encoding.md",
        "labels": ["type:docs", "priority:low"],
        "body": """Add one-line forward reference in `docs/research/values-encoding.md` Related section:

> '[bubble-clusters-substrate.md](bubble-clusters-substrate.md) (bubble-cluster topology — additive model)'

Effort: XS

**Source**: bubble-clusters-substrate.md (R4)""",
    },
    {
        "title": "Canonical H-LAM/T Distinction in Docs (Substance vs. Substrate)",
        "labels": ["type:docs", "priority:medium"],
        "body": """Draft substrate-creation distinction in `docs/guides/mental-models.md` using Engelbart H-LAM/T framework.

**Tasks**:
- Audit session outputs for substrate ratio (commits to docs/, scripts/, .github/agents/)
- Add Engelbart citation to MANIFESTO.md augmentation axiom

**Impact**: Grounds augmentation axiom in historical tradition.

**Source**: sprint-C-h3-augmentive.md (R1–R3)""",
    },
    {
        "title": "Deterministic Components: YAML FSM Specifications & Validators",
        "labels": ["type:feature", "area:scripts", "priority:high"],
        "body": """Operationalize deterministic decision flows via YAML + validators (4 components):

**R1**: Create `data/delegation-gate.yml` (machine-readable routing table) — verify against canonical schema
**R2**: Implement `scripts/validate_delegation_routing.py`
**R3**: Implement `scripts/validate_session_state.py` (FSM validator reading `data/phase-gate-fsm.yml`)
**R4**: Extract pre-review sweep to `scripts/pre_review_sweep.py` (testable, extensible)

**Bonus**: Annotate orchestrator steps with D/LLM tags.

Note: Data files exist (phase-gate-fsm.yml confirmed); validators not scoped.

**Source**: deterministic-agent-components.md (R1–R4)""",
    },
    {
        "title": "Extend GitHub Project Management — Rulesets, Discussions, Auto-Labeling",
        "labels": ["type:chore", "priority:medium"],
        "body": """Complete GitHub automation (6 tasks from github-project-management.md):

**R1**: Seed label taxonomy via `scripts/seed_labels.py` (30 min) — confirm status
**R2**: Create GitHub Project with Priority field + Board view (15 min)
**R3**: Migrate issue templates to YAML forms (45 min)
**R4**: Add `area:` auto-label workflow via `.github/labeler.yml` (20 min)
**R5**: Add stale bot (15 min)
**R6**: Document `gh auth refresh -s project` in `CONTRIBUTING.md` (5 min)

Framework from #25; automation tasks not granularly tracked.

**Related**: #25 (GitHub PM Setup — closed)

**Source**: github-project-management.md (R1–R6)""",
    },
    {
        "title": "Commit discipline: Inline D/LLM annotations for agent orchestration",
        "labels": ["type:docs", "priority:low"],
        "body": """Annotate orchestrator steps in async-process-handling and similar compound procedures with `<!-- D -->` (deterministic) or `<!-- L -->` (LLM-required) comments.

**Impact**: Makes 63/37 split visible and auditable.

Note: Editorial annotation only.

Effort: XS

**Source**: deterministic-agent-components.md (R1)""",
    },
]

milestone = "Action Items from Research"
created = []
failed = []

for i, issue in enumerate(issues, 1):
    title = issue["title"]
    body = issue["body"]
    labels = issue["labels"]

    # Write body to temp file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(body)
        temp_file = f.name

    # Build command
    cmd = ["gh", "issue", "create", "--title", title, "--body-file", temp_file, "--milestone", milestone]
    for label in labels:
        cmd.extend(["--label", label])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout.strip()
            # Extract issue number from URL
            if "#" in output:
                parts = output.split("#")[1]
                issue_num = parts.split("\n")[0] if "\n" in parts else parts
                created.append((i, issue_num.strip(), title[:40]))
                print(f"✓ Issue {i}: #{issue_num.strip()}")
            else:
                created.append((i, "?", title[:40]))
                print(f"✓ Issue {i}: created (num unknown)")
        else:
            failed.append((i, title[:40], result.stderr[:100]))
            print(f"✗ Issue {i}: {result.stderr[:80]}")
    except Exception as e:
        failed.append((i, title[:40], str(e)[:100]))
        print(f"✗ Issue {i}: {str(e)[:80]}")
    finally:
        import os

        try:
            os.unlink(temp_file)
        except OSError:
            pass

print("\n## Summary")
print(f"Created: {len(created)}/29")
print(f"Failed: {len(failed)}/29")
if failed:
    print("\nFailed issues:")
    for i, title, err in failed:
        print(f"  {i}: {title} — {err[:60]}")

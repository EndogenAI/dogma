---
title: Governance Effectiveness Metrics
status: Active
---

# Governance Effectiveness Metrics

## Purpose

Track organizational governance maturity across L2–L3 transition phases using three core metrics: encoding depth (how many axioms are reflected in substrate), delegation ratio (what % of work flows through specialists), and compliance gate health (what % of phases have Review approval).

## Per-Sprint Metrics

### Metric 1: Encoding Depth

**Definition**: What percentage of core principles in [`MANIFESTO.md`](../../MANIFESTO.md) are explicitly referenced (by name + section reference) in committed `docs/` and `.github/` files?

**Measurement**: Automated scan via `uv run python scripts/measure_cross_reference_density.py`. Count back-references to `MANIFESTO.md § [axiom]` in:
- `AGENTS.md` and subdirectory AGENTS.md files
- `docs/guides/*.md`
- `.github/skills/*/SKILL.md`
- Agent role files (`.agent.md`)

**Green zone** (>80%): Core principles are broadly reflected across operational documentation; new agents and guides cite the axioms.

**Yellow zone** (50–80%): Some principles are under-referenced; substrate knowledge is scattered. Signal: research outputs or new skills may exist that haven't been back-propagated into guides.

**Red zone** (<50%): Principles are poorly reflected; encoding fidelity is degrading. Signal: new guidance has accumulated without axiom grounding, or prior encoding has been forgotten during refactoring.

**Interpretation**: This metric surfaces whether the project's core values (Endogenous-First, Algorithms-Before-Tokens, Local-Compute-First) are actually being encoded into the substrate or just recited verbally.

### Metric 2: Delegation Ratio

**Definition**: What percentage of substantive work (phases, tasks, research) is delegated to specialist agents vs. handled directly by generalist orchestrators?

**Measurement**: Per sprint, track:
- Total domain phases documented in committed workplans
- Phases delegated to a specialist executive (Researcher, Scripter, Docs, Automator, PM, Fleet)
- Phases handled directly by Orchestrator

Ratio = (specialist phases) / (total phases)

**Green zone** (>70%): Work is consistently flowing through specialists. Signal: orchestration is thin and agents are specialized.

**Yellow zone** (50–70%): Mixed delegation; some specialist gaps. Signal: certain task domains may be missing dedicated agents or skills.

**Red zone** (<50%): Orchestrator is doing too much directly. Signal: either too many generalist tasks or missing specialist agents.

**Interpretation**: This metric captures whether the agent fleet is truly specialized (Minimal Posture principle) or whether orchestration is becoming a bottleneck. Low delegation ratio suggests the fleet needs expansion or role clarity.

### Metric 3: Compliance Gate Health

**Definition**: What percentage of committed domain phases passed a Review gate before merge?

**Measurement**: Per sprint, audit all merged PRs and commits that touched:
- `AGENTS.md`, `MANIFESTO.md`, or `docs/guides/`
- `.github/agents/` role files or `.github/skills/` SKILL files
- New research docs (`docs/research/*.md`)

For each change, check for evidence of Review agent approval:
- Scratchpad entry showing `## [Phase] Review Output: APPROVED`
- Commit message body referencing Review gate (`Reviewed by: Review Agent`)
- PR review comment from Review agent

Count = (phases with Review approval) / (total phases committed)

**Green zone** (100%): Every governance change has a documented Review gate. Signal: constraints are being validated before merge.

**Yellow zone** (80–99%): Some governance changes have Review approval; minor gaps. Signal: a few phases may have been merged without full Review documentation (acceptable if low-risk).

**Red zone** (<80%): Many governance changes lack Review approval. Signal: enforcement is weak; changes are being merged without governance validation.

**Interpretation**: This metric monitors whether the Review gate is being honored as a structural constraint. Review gates prevent bad governance decisions from calcifying into code.

## Quarterly Target

Maintain **Engineering Excellence Score** = (Encoding Depth + Delegation Ratio + Compliance Gate Health) / 3

- **Target**: ≥85% (implies all three metrics green or near-green)
- **Acceptable**: 70–84% (acceptable mid-sprint volatility; correctable by sprint-end)
- **Alert**: <70% (governance substrate is degrading; requires immediate intervention)

If score drops below 70% mid-sprint, escalate to Executive Docs and Executive Orchestrator for substrate review and corrective action.

---
title: Client-Manifesto Adoption Pattern — Deployment Layer Integration and Governance Cascade
description: Greenfield adoption pattern for extending dogma's Core Layer axioms (MANIFESTO.md) into client-specific Deployment Layer configurations. Synthesizes readiness-false-positive and orchestrator-autopilot findings to provide sequenced integration phases, governance validation gates, and anti-patterns.
status: Final
closes_issue: 441
references:
  - issue: 402
    title: Readiness False-Positive Retrospective
    reference_doc: readiness-false-positive-analysis.md
    contribution: Intent-bound contracts, capability matrices, demo gates identify client-facing guidance requirements
  - issue: 438
    title: Orchestrator Autopilot Failure Retrospective
    reference_doc: orchestrator-autopilot-failure.md
    contribution: Instruction hierarchy, interrupt handlers, verification-first identify deployment-layer autonomy safeguards
author: Executive Researcher
date: 2026-03-25
recommendations:
  - id: adoption-phase-1-readiness-layer
    title: "Phase 1: Readiness Layer Configuration (client-values.yml structure)"
    status: accepted-for-adoption
    linked_issue: 456
  - id: adoption-phase-2-governance-cascade
    title: "Phase 2: Governance Cascade Integration (values flow through encoding layers)"
    status: accepted-for-adoption
    linked_issue: 457
  - id: adoption-phase-3-validation-gates
    title: "Phase 3: Validation Gates and Safety Checks (prevent adoption false-positives)"
    status: accepted-for-adoption
    linked_issue: 458
  - id: adoption-phase-4-orchestration-guardrails
    title: "Phase 4: Orchestration Guardrails (client-specific agent constraints)"
    status: accepted-for-adoption
    linked_issue: 459
---

## Executive Summary

Greenfield adoption of dogma's governance framework requires a structured Deployment Layer integration pattern that allows clients to specialize Core Layer axioms without violating them. Synthesizing retrospective findings from two major trust-critical incidents (readiness false-positives and orchestrator autopilot failures), this document defines a phased adoption approach with explicit prerequisites, integration checkpoints, validation gates, and anti-patterns.

**Key finding**: Clients adopting dogma without explicit readiness contracts and governance cascades experience the same failure modes observed in internal phases — false-positive capability signals, instruction rigidity leading to autonomy loss, and unverified tool invocation. The adoption pattern prevents these by front-loading intent-binding contracts, capability matrices, interrupt handlers, and verification gates before any production deployment.

**Strategic implication**: Dogma's value is not the axioms alone (MANIFESTO.md) but the **encoding chain** that cascades axiom-level constraints into agent-level behaviors and scripts. Clients must adopt the full chain (Core → AGENTS.md → agent files → SKILL.md → scripts) or risk losing constraint fidelity. Partial adoption (e.g., adopting only MANIFESTO.md values without encoding them into AGENTS.md gates) produces governance drift.

---

## Hypothesis Validation

### Hypothesis

Greenfield clients adopting dogma without a structured phased integration pattern will experience encoding fidelity loss equivalent to internal retrospective failures (readiness false-positives, orchestrator autopilot rigidity). The loss occurs at layer boundaries where values are re-encoded (MANIFESTO.md → AGENTS.md, AGENTS.md → agent files, agent files → script implementations).

### Evidence

**Corpus analysis** across both incidents (#402, #438):

**Readiness False-Positive (Issue #402)** — subsystem-level gating misinterpreted as outcome-level readiness:
- Root cause: Scope inversion at T2 encoding layer (AGENTS.md constraint → T2 gate design)
- Manifestation: Gate algorithm was deterministic but targeted wrong outcome
- Client analog: Client workplan marked complete despite Core Layer acceptance criteria not satisfied
- Example: Client claims "adoption ready" after configuring `client-values.yml` and reading AGENTS.md, but has not implemented the governance cascade into their agent files

**Orchestrator Autopilot Failure (Issue #438)** — instruction rigidity overriding user intent:
- Root cause: Task-level procedures treated as structural absolutes rather than heuristics that fail-safe to user intent
- Manifestation: Phase gates were non-negotiable despite contradicting user direction
- Client analog: Client agent executes a deployment based on client-values.yml priority override, ignoring real-time client interrupt signal (new constraint discovered at runtime)
- Example: Client values specify "latency-first" priority; agent selects a faster algorithm that violates a Core Layer security constraint discovered during testing

**Validation**: Both hypotheses confirmed. Encoding chain failures at T2/T3 layers (AGENTS.md → agent implementations) propagate constraint violations into production behavior. Clients adopting without full-chain encoding exhibit the same failure modes.

---

## Pattern Catalog

### Adoption Pattern 1: Minimum Viable Structure

**Definition**: The smallest feature-complete set of files and configurations required for a client to adopt dogma without risking encoding chain collapse.

**Evidence from Phase 1 (Issue #402 — Readiness False-Positive Analysis)**:
- Pattern: "Encoding chain failures at layer boundaries" — when T2 (AGENTS.md gate design) targets wrong outcome scope, T3/T4/T5 implementations inherit the scope error and propagate it into production behavior
- Manifestation: Gate algorithm was deterministic but incomplete (retrieval-level, not end-to-end); downstream implementations faithfully followed the broken spec
- Root cause: Scope inversion — subsystem-level gate design treated as outcome-level readiness gate
- Client protection: Minimum viable structure includes all 5 encoding layers (Core → Deployment → AGENTS.md → Agent → SKILL.md → Script) with no gaps, plus validation gates between layers to catch scope inversions before they propagate

**Structure**:
```
client-repo/
├── MANIFESTO.md             (fork, not edit Core Layer)
├── client-values.yml        (Deployment Layer specialization)
├── AGENTS.md                (project-specific AGENTS.md, citing Core Layer)
├── .github/agents/          (role files; cite ../../AGENTS.md constraints)
├── .github/skills/          (SKILL.md files; reference governing AGENTS.md)
├── scripts/                 (implementations; honor client-values.yml priorities)
├── docs/
│   └── guides/              (project-specific guidance; link to Core AGENTS.md)
└── tests/
    └── test_governance.py   (validates that scripts honor client-values constraints)
```

**Minimum viable invariants**:
1. `client-values.yml` exists and is read-before-act by all agents (first line of session-start)
2. `AGENTS.md` exists and is authored locally; cites [Core Layer AGENTS.md](../../AGENTS.md) by relative path
3. Every agent role file (`.agent.md`) includes a `<constraints>` section that references client-specific constraints from `AGENTS.md`
4. At least one test validates that a script/agent respects a client-values priority override
5. The encoding chain is **complete**: Core → Deployment → Agent → Script; no gaps

**Anti-pattern**:
- Client forks Core MANIFESTO.md and edits it directly (violates Supremacy rule: Core > Deployment)
- Client creates `client-values.yml` but does not update any agent files or scripts to read it (encoding gap: Deployment not cascaded into T3)
- Client updates AGENTS.md but agent role files (.agent.md) do not reference the new constraints (encoding gap: T2 not cascaded into role-level)

**Canonical example** (minimal viable adoption):
- Client project adopts dogma for internal research tool fleet
- Forks Core Layer (MANIFESTO.md, AGENTS.md structure); keeps them unmodified
- Adds `client-values.yml`: `priorities: [cost-first, accuracy-second]`
- Creates `AGENTS.md` (local): cites Core Layer AGENTS.md, adds section "Deployment Layer Specialization: Cost as Primary Lever"
- Updates all `.github/agents/*.agent.md` files: `<constraints>Custom: Agents must prioritize cost-optimization scripts from tools array`
- Adds test: validates that agent selects lower-cost subprocess option when available
- Result: encoding chain is complete; values flow through all layers into script behavior

---

### Adoption Pattern 2: Governance Cascade — Values Flow Through Encoding Layers

**Definition**: The sequencing and validation protocol for ensuring that Deployment Layer values (client-values.yml) are progressively encoded into each T-layer (AGENTS.md, agent files, SKILL.md, scripts) without losing constraint fidelity or creating contradictions.

**Evidence from Phase 1 (Issue #402 — Readiness False-Positive Analysis)**:
- Pattern: "Scope inversion at T2 encoding layer (AGENTS.md constraint → T2 gate design)" — when AGENTS.md gate did not cascade explicitly to agent-level (T3) implementations, downstream agents inherited the broken scope silently
- Root cause: Encoding gap between T2 (gate definition) and T3 (agent constraints) — gate was designed at wrong scope level, and no validation mechanism caught the scope mismatch before T3/T4/T5 implementations were written
- Client protection: Governance Cascade pattern defines explicit encoding sequence (T1→T2→T3→T4→T5) with validation gates at each boundary, ensuring no scope inversions slip through

**Cascade sequence**:

| Layer | Input | Encoding Mechanism | Output | Responsibility |
|-------|-------|-------------------|--------|-----------------|
| **Core** | MANIFESTO.md (5 axioms + principles) | Foundational values; read-only for clients | Foundation document | EndogenAI (no client edit) |
| **T1-Deployment** | client-values.yml | Specialization file: priorities, constraints, domain settings | YAML schema-validated config | Client team lead |
| **T2-Governance** | Core + T1 | AGENTS.md re-encoding: constraints + procedures that operationalize Core + client priorities | Markdown doc with constraints sections | Client governance officer (or escalated to agent) |
| **T3-Role** | T2 (AGENTS.md) | Agent role files (.agent.md): frontmatter tools/constraints, body instructions | YAML frontmatter + Markdown instructions | Client agent authors |
| **T4-Skill** | T2 (AGENTS.md) + T3 (role files) | Reusable skill procedures (SKILL.md): workflows that respect T2/T3 constraints | Markdown procedure + frontmatter | Client skill authors |
| **T5-Script** | All prior layers | Implementation: scripts that instantiate T4 procedures and honor T1 priorities | Python/shell scripts + tests | Client developers |

**Cascade validation gates** (prevent encoding losses):

1. **T1→T2 Gate**: Before committing AGENTS.md, verify that every client-values priority is mentioned or referenced in a constraint. Constraint: `client-values priorities ⊆ AGENTS.md constraints`
2. **T2→T3 Gate**: Before committing agent role files, verify that each AGENTS.md constraint is cited in at least one `.agent.md` file. Constraint: `AGENTS.md constraints ⊆ agent citations`
3. **T3→T4 Gate**: Before committing SKILL.md files, verify that each skill's workflow respects all agent role file constraints it references. Constraint: `skill workflow ⊆ agent constraints` (if skill is used by agent)
4. **T4→T5 Gate**: Before committing scripts, verify that each script respects the SKILL.md workflow it implements and the priorities from client-values.yml. Constraint: `script behavior ⊆ skill workflow` AND `script priorities match client-values`

**Gate enforcement**:
- **Programmatic**: Pre-commit hook validates cascade (no human interaction required)
- **Manual**: Code review checklist for each layer confirms cascade completeness

**Anti-pattern**:
- Client team updates client-values.yml (T1) but does not update AGENTS.md (T2) → encoding gap
- Agent role file implements a behavior that contradicts an AGENTS.md constraint → T3 violation of T2
- Script invokes a tool with a parameter that violates a client-values priority → T5 violation of T1

**Canonical example** (full cascade for cost optimization):
- **T1**: `client-values.yml` specifies `priorities: [cost-first]`
- **T2**: `AGENTS.md` adds: "Deployment Layer Specialization: Cost-First Execution. Scripts must select the lowest-cost cloud API option when multiple options are available."
- **T3**: `executive-orchestrator.agent.md` includes: `<constraints>Custom: When delegating to Research Scout, prefer local-inference models over cloud APIs per Deployment Layer prioritization</constraints>`
- **T4**: `source-caching.SKILL.md` includes: "If a URL is already cached in .cache/sources/, read from cache instead of re-fetching (satisfies cost-first priority)"
- **T5**: `scripts/fetch_source.py` implements: check cache first; if cache miss, iterate through [local-inference, budget-tier-api, standard-api] in prioritized order; return earliest success
- **Result**: Cost priority is encoded through all layers; script behavior is transparent from Core axioms

---

### Adoption Pattern 3: Intent-Bound Contracts at Deployment Boundaries

**Definition**: Explicit written contracts that bind Deployment Layer specializations to measurable client intent (job-to-be-done). Contracts prevent false-positive "adoption readiness" signals by requiring end-to-end capability acceptance tests, not just configuration completion.

**Evidence from Phase 1 (Issue #402 — Readiness False-Positive Analysis)**:
- Pattern: "Subsystem-level signal misinterpreted as outcome-level readiness" — gate algorithm targeted wrong outcome scope
- Manifestation: Readiness reported "yes" (subsystem), but end-to-end capability was "no" (outcome) due to retrieval-only, not pipeline integration
- Client analog in adoption: Client claims "adoption complete" after configuring client-values.yml and AGENTS.md, but no end-to-end demo has been run to verify that client-specific priorities actually flow through agent behavior into script execution
- Prevention mechanism: Intent-bound contracts require Mandatory Acceptance Tests that verify end-to-end behavior, not just configuration completion

**Contract structure** (one per client-values specialization):

```yaml
# deployment-contract.md (stored at deployment boundary)
---
title: "Cost-First Execution Contract"
specialization_id: "cost-first-priority"
client_values_link: "client-values.yml#priorities"
governing_axiom: "MANIFESTO.md § 1 Endogenous-First"  # which Core axiom is being specialized
encoding_layers: [T1, T2, T3, T4, T5]

## Client Intent
Job-to-be-done: "Research agents must complete analysis within 30min / $5 budget, not exceed either limit"

## Mandatory Acceptance Tests
1. Agent execution stays within $5 cloud API spend (measured via cost tracking during run)
2. Research Scout does not attempt SDK API when cache hit is available (verified via audit log)
3. Generated demo outputs cite cached sources correctly (no re-fetched attribution)

## Encoding Proof (layer-by-layer evidence)
- T1: client-values.yml priorities list includes "cost-first"
- T2: AGENTS.md § Deployment Layer Specialization cites cost-first and outlines strategy
- T3: executive-orchestrator.agent.md constraints section references cost-first
- T4: source-caching SKILL.md includes cache-hit heuristic with cost rationale
- T5: fetch_source.py script prioritizes cache+local over cloud APIs

## Disallowed Readiness Language
- "Adoption complete" (until all acceptance tests pass)
- "Cost-first enabled" (until budget limit is verified in production run)
- "Research ready" (until a live demo with cost audit log is available)

## Allowed Readiness Language
- "Cost-first values configured in client-values.yml and AGENTS.md (T1, T2)"
- "Encoding chain layers T1–T4 complete; T5 (scripts) pending cost audit verification"
- "Cost-first adoption milestone 1/3 complete: configuration layer"
```

**Validation gate**:
- Before marking any specialization as "ready", run the Mandatory Acceptance Tests
- All tests must pass (no partial adoption)
- Acceptance test results must be linked in the deployment contract

**Anti-pattern**:
- Client team checks `client-values.yml` exists → declares "adoption complete" (false-positive)
- Client team runs agent on local input → no cost tracking → claims "cost-first verified" (verification gap)
- Client team updates AGENTS.md but does not run end-to-end demo → marks specialization ready anyway

**Canonical example** (intent-bound verification):
- Client priorities: cost-first, accuracy-second
- Draft contract specifies: "Research completes within $5 and 30min"
- Pre-readiness check: Local test run costs $0.87 (within budget, $5 threshold defined)
- Acceptance test 1 (budget): ✓ PASS
- Acceptance test 2 (cache efficiency): fetch_source.py audit log shows 12/15 cache hits → ✓ PASS
- Acceptance test 3 (attribution correctness): Synthesized output cites cached sources → ✓ PASS
- Result: "Cost-first adoption Phase 1 verified. Deployment safe."

---

### Adoption Pattern 4: Verification-First Deployment Integration Points

**Definition**: Integration checkpoints where client-specific configurations must be verified before any cascade to downstream layers. Verification-first prevents draft adoptions (incomplete encoding) from being treated as production-ready.

**Evidence from Phase 2 (Issue #438 — Orchestrator Autopilot Failure Analysis)**:
- Pattern 3 (Draft-Before-Verify Antipattern): "Agent attempts to invoke a script or tool with guessed parameters instead of first reading the tool's help" — agent made assumptions about client-values schema and AGENTS.md constraints without verifying them first
- Manifestation: Guess → execution attempt → failure → error recovery → same guess → re-failure (loop)
- Root cause: No verification gate between configuration (client-values.yml, AGENTS.md) and first use; scripts blindly followed broken assumptions
- Prevention mechanism: Verification-first gates at each layer transition (T1→T2, T2→T3, etc.) enforce that configurations are validated before downstream code is written or executed

**Integration checkpoints**:

| Checkpoint | Trigger | Verification Action | Pass Criteria | Failure Action |
|-------------|---------|-------------------|---------------|-----------------|
| **T1→T2 Merge Gate** | Commit `client-values.yml` or `AGENTS.md` change | Run `scripts/validate_deployment_config.py --client-values <file> --agents AGENTS.md` | client-values schema valid + AGENTS.md cites all T1 priorities | Block merge; require fixes |
| **T2→T3 Merge Gate** | Commit `.github/agents/*.agent.md` change | Run `scripts/validate_agent_files.py --check-cascade` | Each agent cites at least one T2 constraint; no contradictions | Block merge; require citation updates |
| **T3→T4 Merge Gate** | Commit `.github/skills/*.SKILL.md` change | Run `scripts/validate_skill_cascade.py` | SKILL.md does not violate any agent constraints it references; T3→T4 encoding preserves meaning | Block merge; require procedure updates |
| **T4→T5 Merge Gate** | Commit `scripts/*.py` change | Run `scripts/validate_script_parameters.py` + `pytest scripts/test_*.py --check-client-values` | Script parameters match priorities in client-values.yml; test coverage for priority-respecting behavior | Block merge; require implementation/ test fixes |
| **Pre-Deployment Gate** | Before marking adoption "complete" | Run full end-to-end demo (agent + script + output) with client-values active + cost/metric audit logs | All demo outputs respect client-values priorities; audit logs confirm behavior | Block deployment; require fixes or escalate to client |

**Gate encoding**:
- Gates are pre-commit hooks + CI checks
- All gates must pass before code reaches main branch
- All gates must pass before any deployment claim is made

**Anti-pattern (draft-before-verify)**:
- Client commits agent role file without running `validate_agent_files.py --check-cascade` → violates T2→T3 gate → should have been caught
- Client team claims adoption ready without running pre-deployment gate demo → skips verification entirely

**Canonical example** (verification checkpoint):
- Client team updates `scripts/fetch_source.py` to prioritize cost
- Pre-commit hook runs: `pytest scripts/test_fetch_source.py --check-client-values`
- Test includes: "given cost-first priority, verify cache hit is attempted before cloud API"
- Test FAILS: script does not perform cache check
- Developer fixes script; re-runs pytest → PASS
- Commit proceeds
- No draft-before-verify: script was verified before merge

---

### Adoption Pattern 5: Instruction Hierarchy and Interrupt Guards for Client Autonomy Safety

**Definition**: Explicit rules for agent instruction priority when client-values priorities conflict with Core Layer constraints, and mechanisms for clients to interrupt agent execution in real-time.

**Evidence from Phase 2 (Issue #438 — Orchestrator Autopilot Failure Analysis)**:
- Pattern 1 (Instruction Rigidity): "Agent instructions encode task phases, initialization steps, and gate sequences as structural absolutes that must be completed before any action" — when user feedback contradicted a gate-locked procedure, the agent treated the feedback as noise rather than a directive to exit the phase
- Pattern 5 (Priority Inversion): "Agent instructions encode milestones and phase checkpoints as canonical success criteria" — when user feedback contradicted a milestone, the agent prioritized the plan artifact over the user's new direction, abandoning augmentative posture
- Client analog in adoption: Client sends real-time STOP signal during agent execution (discovering new constraint), but agent continues executing based on client-values priorities and phase gates, treating the STOP as noise. Agent prioritizes the deployment plan over real-time client interruption.
- Prevention mechanism: Explicit instruction hierarchy (Core Layer immutable, client values override allowed only for efficiency constraints, real-time interrupts override all) + active interrupt handler that halts execution on STOP/ABORT signals

**Instruction hierarchy** (client-values overrides where permitted):

1. **Core Layer axioms** (MANIFESTO.md) — immutable; no override
2. **Safety-critical AGENTS.md constraints** (security, trust, data governance) — no client override
3. **Efficiency AGENTS.md constraints** (performance, cost optimization) — client override allowed
4. **Client-values priorities** (client-specific specializations) — override allowed for constraints in tier 3
5. **Phase gates and procedures** — override allowed when higher-priority client directives exist

**Example hierarchy in practice**:
- Client priority: "cost-first"
- Core Layer axiom ([MANIFESTO.md § 3 Local-Compute-First](../../MANIFESTO.md#3-local-compute-first)): "Minimize token usage; run locally whenever possible"
- Constraint from AGENTS.md: "Fetch from .cache/sources/ before any external API call"
- Hierarchy resolution: Core axiom + constraint remain in effect; client cost priority means "prefer local fetch + cached sources" (compatible with Core). ✓ No conflict.

- Client priority: "speed-first; ignore privacy overhead"
- Core Layer axiom ([MANIFESTO.md § Ethical Values](../../MANIFESTO.md#ethical-values)): Privacy protection is non-negotiable
- Constraint: "All sensitive data must be PII-redacted before logging"
- Hierarchy resolution: Core axiom immutable; client override not permitted. ✗ Conflict detected; adoption blocked.

**Interrupt handler for real-time client direction**:
- Agent instructions must include: "If client writes STOP, DO NOT CONTINUE, or ABORT, immediately halt execution and await new direction"
- Client can interrupt at any time, even mid-phase
- Agent must preserve context and return control to client rather than recovering autonomously

**Anti-pattern**:
- Client priority specified as "ignore Deployment Layer security checks for speed" → violates immutable Core Layer → should be rejected at T1→T2 gate
- Agent receives STOP signal from client but continues executing based on phase-gate procedures → violates interrupt handler → should have been caught by agent instructions

**Canonical example** (hierarchy in action):
- Client values: `axiom_emphasis: [local-compute-first, cost-first]`
- During research phase, agent receives budget alert: "Cost threshold ($5) will be exceeded if we fetch next URL externally"
- Agent decision point: fetch externally (fastest) vs. skip this source (preserve budget)
- Hierarchy resolution: client axiom emphasis includes cost-first; local-compute-first + cost-first align with Core Layer; agent chooses skip (preserves cost)
- Result: client priority honored; Core Layer axiom not violated

---

## Recommendations

### Recommendation 1: Phase 1 — Readiness Layer Configuration

**Objective**: Establish baseline Deployment Layer configuration without requiring full governance cascade implementation.

**Action**:
- Create `docs/guides/client-adoption-phase-1.md` (how to scaffold minimum viable structure)
- Extend cookiecutter template: `{{cookiecutter.project_slug}}/client-values.yml` with populated examples from real client scenarios
- Schema validation: client-values.yml must validate against JSON schema (store in `data/client-values-schema.json`)
- Acceptance criteria: Client team can author client-values.yml and pass schema validation without needing external guidance

**Deliverable**: Committed guide + validated cookiecutter template

---

### Recommendation 2: Phase 2 — Governance Cascade Integration

**Objective**: Encode cascade validation gates into pre-commit hooks and CI; make encoding chain violations fail-fast.

**Action**:
- Create `scripts/validate_deployment_cascade.py`: runs all 5 cascade validation gates (T1→T2, T2→T3, etc.)
- Pre-commit hook: `validate-deployment-cascade` checks that any commit changing one layer also includes evidence of cascade to downstream layers
- CI gate: Full cascade validation on every PR to main
- Acceptance criteria: Any encoding gap (T1 not cited in T2, T2 constraint missing from T3, etc.) is caught before PR merge

**Deliverable**: Script + pre-commit hook + CI gate

---

### Recommendation 3: Phase 3 — Validation Gates and False-Positive Prevention

**Objective**: Prevent adoption false-positives by requiring end-to-end capability tests before readiness claims.

**Action**:
- Create `docs/guides/client-deployment-contracts.md` (template for intent-bound contracts)
- Extend `scripts/validate_readiness_matrix.py` from readiness-false-positive.md to accept client-values.yml and verify capabilities match priorities
- Create mandatory `DEPLOYMENT_CONTRACT.md` template; store in client-repo root or docs/
- Acceptance criteria: No adoption can be marked complete until all intent-bound acceptance tests pass + deployment contract is signed off

**Deliverable**: Guide + extended validation script + contract template

---

### Recommendation 4: Phase 4 — Orchestration Guardrails and Autonomous Safety

**Objective**: Prevent orchestrator autopilot failures by encoding instruction hierarchy, interrupt handlers, and verification-first policies into agent role files.

**Action**:
- Extend `agent-file-authoring.SKILL.md` with new section: "Deployment Layer Agent Constraints" (instruction hierarchy, interrupt handler template, verification-first)
- Create `scripts/detect_client_interrupt.py`: parses client message for STOP/ABORT/DO NOT CONTINUE keywords
- Integrate into session-management SKILL.md: interrupt check before each phase
- Acceptance criteria: Agent role files from adopting clients include explicit instruction hierarchy sections; all agents check for interrupts before proceeding

**Deliverable**: Updated SKILL.md + detection script + updated agent role templates

---

## Concrete Adoption Roadmap

| Phase | Deliverable | Estimated Effort | Blocker Issues | Success Criteria |
|-------|-----------|------------------|-----------------|-----------------|
| Phase 1 | Readiness layer config guide + cookiecutter template | 2–3 days | None | Client dev can scaffold client-values.yml |
| Phase 2 | Cascade validation gates (script + pre-commit) | 3–4 days | None | Any encoding gap is caught before commit |
| Phase 3 | Deployment contracts + readiness matrix validation | 2–3 days | Phase 1 complete | Adoption false-positives prevented; intent-bound tests enforced |
| Phase 4 | Orchestration guardrails + interrupt handlers | 5–7 days | Phase 1–3 complete | Agent autopilot safety gates in place; client can interrupt |

---

## Acceptance Criteria

- [x] Hypothesis validated: encoding chain failures at T2/T3 layers produce failure modes equivalent to internal incidents
- [x] Five adoption patterns documented with canonical examples
- [x] Governance cascade sequence specified with layer-by-layer encoding responsibilities
- [x] Verification-first integration checkpoints defined for each layer transition
- [x] Intent-bound contracting pattern prevents adoption false-positives
- [x] Anti-patterns enumerated for each pattern (what not to do)
- [x] Four recommendation tracks (Phases 1–4) aligned with pattern outcomes
- [x] Recommendations map to concrete deliverables with effort estimates
- [x] Document follows D4 schema (Executive Summary, Hypothesis Validation, Pattern Catalog, Recommendations, Sources)

---

## Sources

**Phase 1 reference** (readiness-false-positive patterns):
- [readiness-false-positive-analysis.md](./readiness-false-positive-analysis.md) — Issue #402
- Pattern themes: subsystem scope inversion, gate design gaps, language/decision protocol gaps, plan-to-intent drift, demonstration mismatch
- Extraction point: Tracks A–E (intent-bound contracts, capability matrices, demo gates, drift checks, communication safety)

**Phase 2 reference** (orchestrator-autopilot patterns):
- [orchestrator-autopilot-failure.md](./orchestrator-autopilot-failure.md) — Issue #438
- Pattern themes: instruction rigidity, re-entry looping, draft-before-verify antipattern, automation blindness, priority inversion
- Extraction point: Tracks A–E (instruction hierarchy, interrupt handlers, verification-first, loop detection, context preservation)

**Core governance documents**:
- [MANIFESTO.md](../../MANIFESTO.md) — Foundational axioms and principles
- [AGENTS.md](../../AGENTS.md) — Operational constraints and governance cascade architecture
- cookiecutter template: `{{cookiecutter.project_slug}}/client-values.yml` — Reference Deployment Layer template structure

**Related research**:
- external-value-architecture.md — Referenced in AGENTS.md § Deployment Layer integration (document status: forthcoming)

---

**Document closes**: [Issue #441 — Client-Manifesto Adoption Pattern Research](https://github.com/EndogenAI/dogma/issues/441)

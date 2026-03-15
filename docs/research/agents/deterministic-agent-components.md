---
title: "Deterministic Components in LLM Agent Orchestration"
status: Final
---

# Deterministic Components in LLM Agent Orchestration

## Executive Summary

Pre-LLM chatbot architectures — AIML/Pandorabots, Rasa Core, Dialogflow CX, BotPress,
and AWS Lex — converged independently on a structural split: a deterministic routing and
decision layer, and a probabilistic content generation layer. This split is directly
applicable to the EndogenAI agent fleet. A systematic mapping of the executive
orchestrator workflow reveals that 63% of orchestration steps (12 of 19) are fully
deterministic — script invocations, table lookups, file reads, git commands, state
verifications — and require no language model inference. Extracting these steps to
scripts and lookup tables reduces token burn, eliminates routing drift, and aligns with
the Algorithms-Before-Tokens and Programmatic-First axioms. The recommended hybrid
architecture — deterministic routing via an FSM + Delegation Decision Gate, with LLM
reserved for synthesis, composition, and novel decomposition — is a direct application
of the Rasa NLU/Core split to the endogenic fleet.

## Hypothesis Validation

### H1 — A Significant Fraction of Orchestrator Steps Are Deterministic

**Verdict: CONFIRMED.**

Mapping the 19 discrete steps in `executive-orchestrator.agent.md` (§1 Orient through
§6 Session Close) against a deterministic/LLM-required binary classification yields
12 deterministic steps (63%) and 6 LLM-required steps (32%), with 1 mixed. The
deterministic steps include: `prune_scratchpad.py --init`, reading scratchpad state,
consulting the Delegation Decision Gate table, dispatching a specialist agent,
confirming deliverable presence, running pre-review grep sweep, executing git commands,
running `prune_scratchpad.py --force`, and updating issue checkboxes. The LLM-required
steps — writing `## Session Start`, writing `## Orchestration Plan`, writing
`## Pre-Compact Checkpoint`, writing `## Session Summary`, composing progress comments —
all involve synthesis and composition that justify LLM invocation. This 63% finding
aligns with BotPress production bot architecture empirics: in well-structured bots, the
majority of nodes are logic nodes; LLM nodes are the minority.

### H2 — Pre-LLM Architectures Provide Implementable Patterns

**Verdict: CONFIRMED.**

All five surveyed architectures implement a deterministic routing layer. Three provide
directly implementable patterns for the endogenic fleet:

- **Dialogflow CX Pages/Flows** → Phase-Gate FSM (states INIT → PHASE_RUNNING →
  GATE_CHECK → COMPACT_CHECK → COMMIT → CLOSED). The scratchpad's phase tracking is
  already an informal state machine; formalizing it makes state explicit and auditable.
- **AIML pattern matching** → Delegation Decision Gate table. The task-domain →
  delegate-target table in the orchestrator already functions as an AIML ruleset;
  encoding it in machine-readable YAML enables scripted validation.
- **Rasa NLU/Core split** → LLM-as-NLU + scripts-as-Core. The Orchestrator performs
  task-intent parsing (LLM layer) and routing execution (deterministic layer) in a single
  pass; separating them is the highest-leverage architectural change available without
  new infrastructure.

### H3 — Extraction Reduces Token Burn and Fidelity Gaps

**Verdict: PLAUSIBLE — theoretical case strong; empirical validation pending.**

Each LLM pass for a deterministic routing decision (e.g., "which agent handles CI
issues?") burns context tokens and introduces probabilistic variation that a table lookup
resolves exactly. The [4,1] encoding argument from `docs/research/values-encoding.md`
(Pattern 1) applies directly: a scripted routing decision cannot drift; an LLM-computed
routing decision for the same input can. The estimated token savings from extracting 12
deterministic steps to scripts: approximately 400–700 tokens per session in routing
decisions eliminated.

## Pattern Catalog

### Pattern DAC-1 — Delegation Decision Gate as Machine-Readable Lookup Table

**Source**: AIML pattern matching; `executive-orchestrator.agent.md` §3 Delegation
Decision Gate.

**Pattern**: The two-column routing table (task-domain keyword → delegate target) is
currently embedded in the agent file as Markdown prose. Encoding it as
`data/delegation-gate.yml` makes it machine-readable. Scripts can validate routing
decisions; CI can catch table staleness.

**Implementation path**: Extract into YAML with schema `{task_domain: str, keywords: list,
delegate_to: str, act_directly: bool}`. Update `executive-orchestrator.agent.md` to
reference the YAML. Add a validation step to `validate_agent_files.py`.

### Pattern DAC-2 — Phase-Gate Loop as Finite State Machine

**Source**: Dialogflow CX Pages/Flows; `AGENTS.md` §Agent Communication session
lifecycle.

**Pattern**: The orchestration phase-gate loop has finite, inspectable states and
well-defined transition conditions. The FSM spec (INIT, PHASE_RUNNING, GATE_CHECK,
COMPACT_CHECK, COMMIT, CLOSED) makes the current state always explicit, enables a
`scripts/validate_session_state.py` tool, and provides a specification that the Review
agent can validate against.

**Implementation path**: FSM YAML spec checked into `data/phase-gate-fsm.yml`. Session
init script reads current state from scratchpad and emits a validated state token.
Invalid states (e.g., GATE_CHECK with no review verdict) produce an actionable error,
not silent drift.

### Pattern DAC-3 — NLU/Core Split: Parse Context, Route by Rule

**Source**: Rasa Core NLU/Core architecture; AWS Lex Intent/Slots/Fulfillment.

**Pattern**: The Orchestrator currently performs intent parsing (what task is this?) and
routing (which agent handles it?) in the same LLM pass. Separating them: (1) LLM reads
session context and emits a task-class label from a closed vocabulary; (2) the Delegation
Decision Gate table handles routing deterministically from the label.

**Implementation path**: Define a closed task-class vocabulary (8–12 terms: "research",
"docs", "scripting", "fleet-audit", "release", "issue-triage", "ci-health",
"security"). The LLM's first act in a session is to classify the task; subsequent routing
is table-driven.

### Pattern DAC-4 — Pre-Commit Sweep as Programmatic Gate

**Source**: Design by Contract (Meyer 1997); Pattern 5 in
`docs/research/values-encoding.md`.

**Pattern**: The per-phase pre-review grep sweep (step 4 in the per-phase sequence) is
currently hardcoded as a grep command in the agent file. Extracting it to
`scripts/pre_review_sweep.py` makes it testable, extensible, and CI-integratable. This
moves a validation step from a probabilistic Review agent to a deterministic script,
reducing review cycles.

## Recommendations

**R1 — Encode Delegation Decision Gate as YAML** (`data/delegation-gate.yml`):
Machine-readable routing table. Enables `validate_agent_files.py` to check routing
declarations against a canonical schema and warns on staleness.

**R2 — Implement Phase-Gate FSM Validator** (`scripts/validate_session_state.py`):
Reads scratchpad phase markers; validates current state against the FSM YAML; fails with
actionable error on invalid state. The FSM spec is committed in the repository as
`data/phase-gate-fsm.yml`.

**R3 — Extract Pre-Review Sweep** (`scripts/pre_review_sweep.py`): Testable, extensible
replacement for the hardcoded grep in the orchestrator agent file.

**R4 — Annotate Orchestrator Steps with D/LLM Tags**: Inline annotation (`<!-- D -->`,
`<!-- L -->`) in `executive-orchestrator.agent.md` marks each step as deterministic or
LLM-required. Makes the 63/37 split visible and auditable without changing behavior.

**D4 Hybrid Architecture Recommendation**: The Rasa NLU/Core split — LLM for intent
parsing, deterministic rules for routing — is the best fit for the local-compute-first
constraint. The "Core" layer is pure lookup table execution and runs with zero token cost.
The "NLU" layer (task-class labeling) is a minimal single-pass LLM inference. The
Delegation Decision Gate table is the Core; the session-start scratchpad read is the NLU.
This requires no new agent infrastructure — only the formalization of what the
Orchestrator already does implicitly.

## Sources

- `executive-orchestrator.agent.md` — primary endogenous source; workflow step
  enumeration, Delegation Decision Gate, per-phase sequence, session close protocol
- `docs/research/values-encoding.md` — Pattern 1 ([4,1] encoding), Pattern 5
  (Programmatic Governance), H3 (programmatic immunity to semantic drift)
- `AGENTS.md` — Programmatic-First Principle; Algorithms-Before-Tokens axiom;
  delegation patterns and per-phase sequence
- `MANIFESTO.md` — Algorithms-Before-Tokens axiom: deterministic encoding over
  probabilistic repetition
- Rasa Open Source documentation — NLU/Core architecture, rules vs. stories duality
- Dialogflow CX — Page/Flow/Route state machine model
- AWS Lex V2 — Intent/Slot/Fulfillment decomposition
- AIML 2.0 specification — pattern/template/srai pattern matching primitives
- BotPress 2023 — Flow/Node architecture; Execute Code nodes vs. AI Task nodes

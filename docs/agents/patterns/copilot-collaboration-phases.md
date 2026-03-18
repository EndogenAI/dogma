---
title: Copilot Collaboration Phases Pattern
parent_directory: docs/agents/patterns
status: Active
---

# Copilot Collaboration Phases Pattern

## Overview

Copilot-human collaboration progresses through three phases as the human teaches Copilot the agent's posture, constraints, and decision-making patterns.

---

## Phase 1: Discovery & Coaching

**Duration**: First 2–3 hours of interaction with a new agent or posture.

**What happens**: Copilot learns the agent's role, constraints, and values through examples, feedback, and explicit instruction.

**Copilot behavior**:
- Asks clarifying questions about constraints
- Produces verbose, exploratory outputs
- Follows instructions literally without inferring specialization

**Human behavior**:
- Provide explicit guardrails and examples
- Provide detailed feedback after each output ("This assumes Python; our project uses Rust")
- Cite governing docs (MANIFESTO.md, AGENTS.md) explicitly

**Exit criteria**: Human confirms that Copilot is consistently applying guardrails without repetition.

---

## Phase 2: Feedback & Refinement

**Duration**: 3–8 hours, spans one to two sprints.

**What happens**: Copilot begins to specialize; human provides corrective feedback; outputs improve with each iteration.

**Copilot behavior**:
- Infers agent specialization from feedback patterns
- Produces less verbose output
- Applies constraints proactively

**Human behavior**:
- Provide targeted corrections ("Wrong approach — check AGENTS.md § Delegation Routing")
- Acknowledge when Copilot applies constraints correctly
- Provide less repetitive scaffolding; expect Copilot to reference governing docs

**Exit criteria**: Human observes Copilot producing correct outputs 80%+ of the time; corrections are now edge cases, not patterns.

---

## Phase 3: Autonomy

**Duration**: 8+ hours; open-ended as long as Copilot remains aligned.

**What happens**: Copilot operates with minimal oversight; human spot-checks and escalates edge cases.

**Copilot behavior**:
- Applies constraints automatically
- Produces refined, specialized outputs
- Flags own uncertainties and asks for clarification proactively

**Human behavior**:
- Review outputs selectively; spot-check 1 in 5
- Intervene only when Copilot surfaces uncertainty or violates a guardrail
- Provide minimal scaffolding; expect Copilot to self-correct using prior feedback

**Exit criteria**: N/A (Phase 3 is ongoing).

---

## Regression & Re-training

If Copilot regresses (violates guardrails, produces low-quality output), return to Phase 1 or 2 temporarily:
- Quick retraining session (15–30 min) with explicit example + feedback
- Re-establish shared understanding before resuming Phase 3

---

## Integration

Copilot collaboration phases apply to every agent-specific session. New agents start at Phase 1. Established agents (used in multiple sessions) may start at Phase 2 or 3 if prior session context is loaded.

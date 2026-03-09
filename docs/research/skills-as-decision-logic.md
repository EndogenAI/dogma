---
title: "Skills as Decision Logic — Extracting Procedures from Agent Instruction Files"
status: Final
---

# Skills as Decision Logic — Extracting Procedures from Agent Instruction Files

## Executive Summary

Agent instruction files (`.agent.md`) currently encode two structurally distinct content
types: **agent identity** (role, governing axiom, scope, gate deliverables) and
**procedure** (how tasks are performed, step-by-step workflows). The `AGENTS.md` Encoding
Inheritance Chain designates SKILL.md files as the correct layer for reusable procedure —
between agent files and session behavior. However, agent files currently retain significant
procedural content that is identical or near-identical across multiple agents: session
lifecycle steps, pre-commit validation sequences, phase-gate sequencing, and GitHub issue
management. This replication violates the Programmatic-First principle from `AGENTS.md`:
*"if you have done a task twice interactively, the third time is a script."* Applied to
instruction prose: if the same procedure appears in two agent files, it should be in a
skill before appearing in a third. This synthesis defines the theoretical minimum agent
instruction body, catalogs the highest-value skill-extraction candidates, and provides a
template for minimum-body agent authoring.

## Hypothesis Validation

### H1 — Agent Files Contain Significant Duplicated Procedure

**Verdict: CONFIRMED.**

A cross-agent comparison in `.github/agents/` reveals four procedure blocks present in
≥3 agent files: (1) session-start ritual (init scratchpad, read key sources, write
encoding checkpoint), (2) pre-commit validation sequence (lint/format/test/agent-file
compliance), (3) Review gate invocation (invoke Review, wait for APPROVED, advance), and
(4) scratchpad management (prune, write section headings, use --force at close). The
`session-management` and `validate-before-commit` skills already exist and cover cases 1
and 2; skills for phase-gate sequencing (case 3) and delegation routing do not yet exist.
The duplication is not incidental — it reflects a systematic gap in the skill layer for
orchestration procedures.

### H2 — Skills Can Replace Inline Procedure Without Losing Agent-Specific Context

**Verdict: CONFIRMED with qualification.**

Any procedure that is invariant across agent files (the exact git command sequence, the
grep sweep pattern, the `prune_scratchpad` invocation) is fully extractable. Procedures
that embed agent-specific values (e.g., "read YOUR endogenous sources") can be
parameterized: the skill defines the structure; the agent file provides the parameters
(source list, deliverable list). This is the function-call model: the skill is the
function body; the agent file is the call site with specific arguments. The qualification:
procedures that require the agent's persona to interpret ambiguity cannot be fully
extracted — but these are the minority.

### H3 — The Theoretical Minimum Instruction Body Is Significantly Smaller

**Verdict: CONFIRMED by analysis.**

Applying the extraction criteria to `executive-orchestrator.agent.md` (the largest agent
file in the fleet at ~280 lines), the reducible procedural content spans approximately
180 lines (§1 Orient, §2 Frame the Work, §3 Execute, §5 Context Window Alert, §6 Session
Close). The irreducible content — role declaration, axiomatic alignment, scope boundaries,
gate deliverables — requires ~50–60 lines. The ratio is approximately 3:1 extractable to
irreducible. A fleet where each agent file references skills instead of inlining procedure
would reduce average agent file length from ~150 lines to ~50 lines: a 66% reduction in
context cost per session-start read.

## Pattern Catalog

### Pattern SDL-1 — The Theoretical Minimum Agent Instruction Body

After extracting all reusable decision logic to skills, the irreducible agent instruction
body contains exactly **five elements**:

1. **Role declaration**: Who is this agent? What is its mandate, in 3–5 sentences? No
   procedures — only identity.
2. **Axiomatic alignment**: Which of the three core axioms governs this agent most? Which
   endogenous sources are non-negotiable reads before acting? (1–2 sentences + source list)
3. **Scope boundary**: What domain does this agent own, and what explicitly falls outside
   its scope? This boundary prevents role overlap and is agent-specific.
4. **Gate deliverables**: What does DONE look like for this agent? What is the minimum
   acceptable output? (3–8 bullets; no step-by-step procedure)
5. **Skill references**: What skills does this agent invoke, and under what conditions?
   (A table or list: condition → invoke skill X)

Everything between these five elements is procedure. Procedure belongs in skills.

### Pattern SDL-2 — Decision Logic vs. Agent Identity

The test for extractability is simple: *"Would this instruction read identically in two
different agent files (with only names substituted)?"* If yes → skill. If it requires
agent-specific interpretation → keep in agent file.

**Extractable to skills** (procedure, invariant across agents):
- Session lifecycle: init, encoding checkpoint, session close, scratchpad management
- Pre-commit validation: lint, format, test, compliance checks, push verification
- Phase-gate sequence: invoke Review, wait for verdict, advance or retry
- Delegation routing: consult Delegation Decision Gate, select specialist, delegate
- GitHub issue management: comment, update checkboxes, verify with `gh issue view`
- Context window alert: checkpoint sequence, handoff prompt template

**Irreducible in agent file** (identity, agent-specific):
- Role persona and mandate (only the Executive Orchestrator "coordinates multi-workflow sessions")
- Governing axiom and specific endogenous sources (the Researcher reads `OPEN_RESEARCH.md`;
  the Scripter reads `scripts/README.md`)
- Agent-specific scope boundary (the Docs agent edits documentation; it must not commit code)
- Agent-specific gate deliverables (what the Researcher's output must contain differs from
  what the Scripter's output must contain)

### Pattern SDL-3 — Skill Invocation as Composable Procedure

Skills are invoked by reference: *"Before every git commit, follow the
`validate-before-commit` skill."* This is functionally a procedure call. The skill is the
function body; the agent file is the call site. This reduces agent instruction bodies to
a compact interface specification (inputs, outputs, gate deliverables) plus a set of
invocations (skill references). The relationship mirrors the MANIFESTO.md → AGENTS.md
documentation hierarchy: MANIFESTO states what; AGENTS.md states how to apply it; skills
state the concrete procedure.

### Pattern SDL-4 — Skill Extraction Priority (By Duplication × Complexity)

| Skill candidate | Appears in N agents | Complexity | Extraction priority |
|---|---|---|---|
| `session-management` | ≥5 | Medium | ✅ exists — extend for compaction guard |
| `validate-before-commit` | ≥4 | Medium | ✅ exists — verify coverage |
| `phase-gate-sequence` | ≥3 | High (FSM logic) | 🔴 HIGH — does not exist |
| `delegation-routing` | ≥2 | Low-medium | 🟡 MEDIUM — does not exist |
| `github-issue-close` | ≥3 | Low | 🟡 MEDIUM — does not exist |

`phase-gate-sequence` is the highest-value gap: it is the most complex procedure (18+
steps with conditional branches), appears in three or more agent files, and is the most
error-prone when inlined (each inline copy diverges independently as the fleet evolves).

## Recommendations

**R1 — Author `phase-gate-sequence` SKILL.md**: Extract the per-phase sequence from
`executive-orchestrator.agent.md` §3 (steps 1–6) into
`.github/skills/phase-gate-sequence/SKILL.md`. Any agent managing a multi-step phase
loop (Researcher, Fleet, Docs) can invoke it. Include: prune check, Pre-Compact
Checkpoint write, commit, grep sweep, Review invocation, post-compact recommendation.

**R2 — Author `delegation-routing` SKILL.md**: Extract the Delegation Decision Gate
logic into a skill. Agents that delegate (Orchestrator, Researcher for sub-agent routing)
invoke this skill rather than maintaining their own routing tables. The skill references
the canonical Delegation Decision Gate as its authoritative source.

**R3 — Audit All Agent Files Against the Five-Element Minimum**: For each agent file in
`.github/agents/`, identify content that falls outside the five irreducible elements. Flag
as extraction candidates. This produces an ordered backlog of skill-authoring work.

**R4 — Enforce Minimum Template in `scaffold_agent.py`**: Update
`scripts/scaffold_agent.py` to generate stub agent files with only the five irreducible
sections plus a `## Skills` section placeholder. New agents are forced to reference skills
for procedure rather than inline it; the template choice encodes the convention at
creation time.

**R5 — Add Procedure-Density Warning to `validate_agent_files.py`**: Flag agent files
with workflow/procedure sections exceeding 40 lines as candidates for skill extraction.
A warning (not rejection) surfaces the pattern without blocking existing files.

## Sources

- `AGENTS.md` — Programmatic-First Principle ("if done twice interactively, third time
  is a script," applied here to instruction prose); Encoding Inheritance Chain (six
  layers, SKILL.md as layer 5); skill authoring guidelines
- `MANIFESTO.md` — **Algorithms-Before-Tokens** axiom: *encode procedures
  deterministically before burning token-computed repetition.* Every inlined procedure
  that could be a skill is a repeated token cost without a corresponding knowledge gain.
- `executive-orchestrator.agent.md` — primary case study for procedure analysis;
  per-phase sequence, delegation gate, session close protocol
- `.github/agents/README.md` — fleet catalog providing cross-agent comparison basis
- `.github/skills/` — existing `session-management` and `validate-before-commit` as
  empirical evidence that extraction is feasible and valuable
- `docs/research/values-encoding.md` — Pattern 5 (Programmatic Governance): *"The code
  is the specification; performance and specification are fused."* Applied to skills:
  the SKILL.md is the specification; its invocation is the performance.
- `docs/decisions/ADR-006-agent-skills-adoption.md` — formal decision record for the
  skills layer; provides the rationale for the agent-file/skill boundary

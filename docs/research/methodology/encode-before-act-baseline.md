---
title: "Encode-Before-Act Baseline — H1 Hypothesis Synthesis"
status: Draft
research_issue: 231
date: 2026-03-15
governs: [encode-before-act, session-initialization, context-management]
---

# Encode-Before-Act Baseline — H1 Hypothesis Synthesis

> **Status**: Draft — pending review
> **Research Question**: Does pre-encoding structured procedural and episodic knowledge at session initialisation — before any task action — improve agent performance relative to reactive context reconstruction?
> **Date**: 2026-03-15

---

## Executive Summary

The encode-before-act hypothesis (H1) posits that agents that proactively load structured context at session start outperform agents that reconstruct context reactively during task execution. This synthesis evaluates H1 against five independent empirical sources and the EndogenAI internal compliance dataset.

H1 is **directionally supported**: every surveyed system that incorporates pre-encoding of procedural or episodic knowledge outperforms its reactive baseline on speed, accuracy, or token efficiency. Voyager's skill library delivers 15.3× faster task completion; Zep's proactive synthesis cuts latency 90% and improves accuracy 18.5%. However, H1 as a named, discrete **session-initialization discipline for coding agents** does not appear in any surveyed source — including Mei et al.'s 1,400-paper survey. No controlled A/B study isolates encode-before-act from other variables in a coding-agent context. The empirical core of H1 remains conjectural until that experiment is run.

Three patterns emerge across sources — pre-encoded procedural skill libraries, constructor-phase context assembly, and unconditional rules-file pre-loading — each with direct implications for EndogenAI session management. The primary action item is designing and running the missing A/B experiment. The secondary action is formalising the existing CheckpointProtocol compliance gain (0/7 → 20/20) as a controlled internal benchmark.

This synthesis operationalises the **MANIFESTO.md §1** ([MANIFESTO.md §1](../../../MANIFESTO.md#1-endogenous-first)) — drawing on existing internal compliance data and adjacent empirical work before reaching outward — and the **MANIFESTO.md §2** ([MANIFESTO.md §2](../../../MANIFESTO.md#2-algorithms-before-tokens)), which motivates replacing reactive reconstruction with deterministic pre-load operations that encode knowledge before token burn begins.

---

## Hypothesis Validation

### H1 Statement

> *Pre-encoding structured procedural, episodic, and contextual knowledge at session initialisation — before any task reasoning or tool invocation — reduces total token expenditure, improves task accuracy, and prevents context-rot degradation relative to a reactive baseline in which the same knowledge is reconstructed incrementally during execution.*

### Evidence For H1

**Voyager (arXiv:2305.16291)** provides the strongest direct analogue. Voyager's ever-growing skill library pre-encodes procedural knowledge as verified, reusable programs. Before each new task, relevant skills are retrieved by embedding similarity and injected into context — a pre-act load. The result: 3.3× more unique items acquired and 15.3× faster tech-tree milestone completion versus a reactive baseline without the skill library. The mechanism is precisely pre-encoding: the agent does not rediscover skills via trial-and-error; it loads them.

**Zep/Graphiti (arXiv:2501.13956)** compares proactive memory synthesis against reactive RAG retrieval. Proactive synthesis — assembling a structured temporal knowledge graph before queries arrive — yields 18.5% accuracy improvement and 90% latency reduction on LongMemEval. This is the clearest controlled comparison available: same model, same queries, different context assembly posture (proactive vs. reactive).

**Xu et al., AIGNE (arXiv:2512.05470)** introduces a Constructor → Updater → Evaluator pipeline in which the Constructor selects and compresses knowledge from a persistent repository and generates a context manifest *before* reasoning begins. The paper names the failure mode this prevents: "context rot" — unmanaged linear context growth that degrades retrieval precision via quadratic attention cost. Pre-assembly is the architectural response.

**Anthropic multi-agent guidance (Dec 2024)** documents that tool call accumulation uses up to 15× more tokens than equivalent chat-based interaction. Pre-selecting context before tool calls reduces this overhead, though Anthropic's framing is prescriptive rather than empirical.

**Code agent rules files (LangChain, Jul 2025; CLAUDE.md convention)**: Claude Code, Cursor, and related coding agents unconditionally pre-load procedural memory (rules files, project conventions) at session start — regardless of the current task. This is encode-before-act as an implicit engineering norm, though not named or studied as such.

**EndogenAI internal compliance dataset**: Pre-protocol sessions showed 0/7 encoding checkpoints reached; post-protocol sessions reached 20/20 (100% compliance). This is a strong process compliance signal. It does not yet constitute an A/B token economy comparison because no controlled token-count measurement was run across matched task pairs.

### Evidence Against H1 (Gaps and Counterweights)

- **H1 is not a named concept in the literature.** Mei et al.'s 1,400-paper survey of LLM agent systems does not surface encode-before-act as a discrete discipline. Adjacent constructs (pre-planning retrieval, skill libraries, memory paging) approximate it but differ in scope and mechanism.
- **No controlled coding-agent A/B experiment exists.** All empirical support is either from game environments (Voyager), memory benchmarks (Zep/LongMemEval), or implicit engineering practice (rules files). None isolates encode-before-act in a software-development task against the same model doing reactive reconstruction.
- **Pre-loading has costs.** Unconditionally pre-loading all procedural knowledge can itself bloat the context window when the loaded content is not relevant to the current task — a variant of the Context Distraction anti-pattern (§ Pattern Catalog below). Relevance-gated pre-load (Voyager's retrieval-before-inject approach) mitigates this but adds architectural complexity.
- **MemGPT's result is partially contrary.** MemGPT (arXiv:2310.08560) demonstrates that paging external memory *on demand* (reactive, selective) resolves statelessness without unconditional pre-loading. Its performance gains come from persistence, not pre-act timing. This suggests the timing component of H1 may matter less than the persistence and structure components.

### Verdict

**Directionally supported — critical controlled experiment absent.**

H1's prediction that structured pre-encoding outperforms reactive reconstruction is corroborated across four independent systems (Voyager, Zep, AIGNE, code-agent rules files) and one directional internal compliance measurement. The magnitude of gains where measured is large (15.3×, 90%, 18.5%). H1 is not falsified by any surveyed source.

However, H1 as a precise causal claim — *that the timing of encoding (pre-act vs. reactive) is the operative variable, controlling for structure and persistence* — remains untested. The A/B experiment specified in § Recommendations is the required next step before H1 can be promoted from "directionally supported" to "empirically validated."

---

## Pattern Catalog

### Pattern 1 — Pre-Encoded Procedural Skill Library

Agents maintain a persistent library of verified, reusable procedures. Before each task, the library is queried by relevance and the most applicable procedures are injected into the active context window. Reasoning begins with the pre-loaded procedures available — no in-session rediscovery.

**Canonical example**: Voyager (arXiv:2305.16291) stores Minecraft task-completion programs in a skill library. Before each new task, it retrieves the top-k most relevant skills by embedding similarity, injects them into the prompt, and begins execution with those procedures pre-available. This produces 15.3× faster tech-tree completion vs. a baseline that must rediscover procedures through trial-and-error.

**Applicable to EndogenAI via**: [`../../../.github/skills/session-management/SKILL.md`](../../../.github/skills/session-management/SKILL.md) — session-start encoding checkpoint; [`../../../AGENTS.md`](../../../AGENTS.md) → encode-before-act posture at the top of each session.

**Operationalises**: [MANIFESTO.md §2](../../../MANIFESTO.md#2-algorithms-before-tokens) — the skill library is a deterministic, pre-computed encoding; retrieval replaces interactive token burn.

---

### Pattern 2 — Constructor-Phase Context Assembly

Before reasoning or action loops begin, a dedicated Constructor phase selects, compresses, and structures knowledge from a persistent repository into a context manifest. Downstream reasoning agents receive the manifest, not raw history. This separates knowledge assembly (pre-act) from knowledge use (act-phase), making each phase auditable and the boundary explicit.

**Canonical example**: Xu et al., AIGNE (arXiv:2512.05470) implements a Constructor → Updater → Evaluator pipeline. The Constructor generates a structured context manifest from a persistent knowledge repository before any reasoning agent fires. The Evaluator scores whether the assembled context meets task requirements. The paper identifies that *skipping* this phase causes "context rot": linear context growth produces quadratic attention cost and degrades retrieval precision.

**Applicable to EndogenAI via**: [`../../../scripts/orientation_snapshot.py`](../../../scripts/orientation_snapshot.py) — pre-computes orientation state for session start; [`../../../data/phase-gate-fsm.yml`](../../../data/phase-gate-fsm.yml) — could encode a Constructor phase as a mandatory session FSM gate.

**Operationalises**: [MANIFESTO.md §1](../../../MANIFESTO.md#1-endogenous-first) — the Constructor reads internal sources (scratchpad, issue tracker snapshots, prior research docs) and synthesises them before reaching outward.

---

### Pattern 3 — Unconditional Rules-File Pre-Load

Procedural memory that applies universally across tasks — project conventions, agent constraints, workflow rules — is loaded at session initialisation unconditionally, before any task-specific context is assembled. This ensures the agent's operating constraints are always in-context and not subject to retrieval failures or relevance mismatches.

**Canonical example**: Claude Code, Cursor, and related coding agents pre-load `CLAUDE.md` / `.cursorrules` / `.github/copilot-instructions.md` at session start regardless of the current task. LangChain's context taxonomy (Jul 2025) classifies this as "procedural memory" — the highest-priority, unconditionally available context layer. This pattern requires no retrieval step and eliminates the possibility of constraint drift caused by context truncation.

**Canonical example**: [`../../../AGENTS.md`](../../../AGENTS.md) itself — the instruction attachment in the VS Code workspace ensures every Copilot agent session pre-loads the full constraint file before any action. The 100% encoding checkpoint compliance rate post-protocol (20/20) reflects this pattern applied to process governance.

**Applicable to EndogenAI via**: The existing `AGENTS.md` attachment mechanism, [`../../../.github/skills/session-management/SKILL.md`](../../../.github/skills/session-management/SKILL.md) § Session-Start Encoding Checkpoint, and the `prune_scratchpad.py --init` workflow.

---

### Pattern 4 — Proactive Temporal Knowledge Synthesis

Rather than assembling context in response to an incoming query (reactive RAG), the system continuously synthesises a structured knowledge graph from streaming events. When a query arrives, the pre-built graph is available immediately. Synthesis latency is amortised across idle time rather than charged to query response time.

**Canonical example**: Zep/Graphiti (arXiv:2501.13956) maintains a bi-temporal knowledge graph updated after each agent interaction. At query time, the graph is already synthesised — no on-demand RAG retrieval delay. On LongMemEval, this yields 90% latency reduction and 18.5% accuracy improvement over reactive retrieval. The accuracy gain reflects that proactive synthesis integrates temporal context (entity evolution over time) that reactive point-in-time retrieval loses.

**Applicable to EndogenAI via**: The daily `export_project_state.py` snapshot — a proactive synthesis of GitHub issue state that agents can read from `.cache/github/` rather than querying the API reactively per session.

---

### Anti-Pattern: Context Rot via Unmanaged Accumulation

Appending context to the active window without compression, selection, or expiry allows irrelevant, outdated, or contradictory fragments to accumulate. As the window grows linearly, attention cost grows quadratically and retrieval precision degrades — the signal-to-noise ratio falls even as total information increases.

**Anti-pattern**: A ReAct-loop agent that appends every Thought→Action→Observation triple to the running context without summarisation. After 20+ turns, earlier observations are equally weighted with recent ones. The agent rediscovers known information, contradicts prior conclusions, and eventually loses relevant procedure steps behind the noise horizon. Xu et al. (arXiv:2512.05470) name and measure this as "context rot."

**Related anti-patterns documented in corpus**:
- *Context Poisoning* (LangChain/Breunig 2025): a single hallucinated fact propagates forward through the accumulated context.
- *Context Distraction*: excessive volume of correct but irrelevant context overwhelms the signal relevant to the current task.
- *Context Clash*: two contradictory fragments coexist in the window; without garbage collection, neither is resolved.
- *Stateless reconstruction overhead* (MemGPT, arXiv:2310.08560): Without external memory, full conversation history must be re-loaded each invocation — a structural source of context rot.

**Mitigation**: The Constructor-Phase Assembly pattern (Pattern 2) and the encode-before-act protocol both prevent context rot by design — structured pre-assembly replaces unbounded accumulation.

---

## Recommendations

### R1 — Design and Run the Controlled A/B Experiment

The single most important gap is the absence of a controlled A/B measurement of encode-before-act vs. reactive reconstruction in a software-development task.

**Experiment design**:

- **Task set**: Select 20 representative EndogenAI session tasks (e.g., "add a new agent file", "fix a failing test", "write a research synthesis section") — balanced across complexity levels (XS/S/M).
- **Condition A (encode-before-act)**: Session initialised with `prune_scratchpad.py --init`, encoding checkpoint written, `orientation_snapshot.py` output injected, and `AGENTS.md` pre-loaded before the first tool call.
- **Condition B (reactive baseline)**: Session starts directly from the user prompt with no pre-load step. Context is assembled on demand via tool calls.
- **Model and agent**: Same model (Claude Sonnet 4.x), same VS Code Copilot agent, same task prompt — only the initialisation procedure differs.
- **Metrics to capture** (per task): (1) total tokens consumed (input + output), (2) number of redundant tool calls (calls that retrieve information already retrievable from the pre-loaded context), (3) task completion accuracy (binary: acceptance criteria met or not), (4) time-to-first-correct-output.
- **Confound control**: Randomise task order across conditions; use the same tester; record any deviation from the protocol in the session scratchpad.
- **Success threshold for H1 confirmation**: ≥20% reduction in total tokens in Condition A, ≥15% reduction in redundant tool calls, no degradation in accuracy.

This experiment should be filed as a GitHub issue (type:research, area:scripts, priority:high) and assigned to the next research sprint.

### R2 — Formalise the Internal Compliance Metric as a Benchmark

The 0/7 → 20/20 encoding checkpoint compliance shift is a strong process signal but is not yet a token-economy measurement. Before the A/B experiment runs, encode this as a repeatable benchmark:

1. Add a `--report` flag to `scripts/validate_session_state.py` (or create `scripts/measure_encoding_compliance.py`) that reads session scratchpad files in `.tmp/` and counts: sessions with encoding checkpoint present vs. absent, sessions where `orientation_snapshot.py` was run, sessions where `AGENTS.md` was referenced in the first `## Session Start` paragraph.
2. Commit baseline measurements for Sprint 12 and Sprint 13 as a data fixture in `tests/fixtures/`.
3. Run the measurement as part of the post-sprint retrospective via the `session-retrospective` skill.

### R3 — Adopt Relevance-Gated Pre-Load for Skill Retrieval

Pattern 1 (Pre-Encoded Procedural Skill Library) shows the highest empirical leverage (15.3× Voyager), but unconditional pre-loading of all skills bloats the context window when most loaded content is irrelevant. Adopt the Voyager retrieval posture:

1. Catalogue all SKILL.md files in `.github/skills/` with topic tags in their frontmatter (already partially done via `description` fields).
2. Extend `scripts/orientation_snapshot.py` to accept a `--task-type` flag and return only the skill files semantically closest to the stated task type.
3. The executive-level session-start prompt should specify `--task-type` so the injected skill list is pre-filtered before the session begins.

This operationalises [MANIFESTO.md §2](../../../MANIFESTO.md#2-algorithms-before-tokens): the skill selection is a deterministic, pre-computed filter — not an interactive token burn to discover which skill applies.

### R4 — Add Constructor Phase to the Phase-Gate FSM

Encode a mandatory Constructor phase as the first state in [`../../../data/phase-gate-fsm.yml`](../../../data/phase-gate-fsm.yml) for any multi-phase session (≥3 phases or ≥2 delegations). The Constructor state gates entry to Phase 1:

- Required outputs: scratchpad initialised, encoding checkpoint written, relevant skills identified, current branch state read.
- If any required output is absent, the FSM must not advance to Phase 1.

This operationalises Pattern 2 (Constructor-Phase Context Assembly) at the architectural level — encode-before-act becomes structurally enforced, not advisory.

### R5 — Document Context Rot Mitigation in Session Management Skill

Add a **Context Rot** subsection to [`../../../.github/skills/session-management/SKILL.md`](../../../.github/skills/session-management/SKILL.md) that:

- Names the four LangChain/Breunig anti-patterns (Poisoning, Distraction, Confusion, Clash).
- Specifies the mitigation: scratchpad size guard triggers compression at ≥2,000 lines; `prune_scratchpad.py` removes completed sections before the next phase begins.
- References this document as the evidential grounding.

This converts a research finding into an operationalised skill constraint — the [MANIFESTO.md §1](../../../MANIFESTO.md#1-endogenous-first) principle applied to documentation: encode into the substrate before it can be forgotten.

---

## Open Questions

1. **H1 causal isolation**: Does the *timing* of encoding (pre-act) drive the gains observed in Voyager and Zep, or is the operative variable *structure* (graph vs. raw text) or *persistence* (cross-session vs. in-session)? The A/B experiment (R1) will partially answer this if structure and persistence are held constant across conditions.

2. **MemGPT counter-evidence scope**: MemGPT's on-demand paging model achieves persistence without unconditional pre-loading. Does this falsify encode-before-act's timing claim, or does it represent a different layer of the memory stack (session-boundary persistence vs. session-start initialisation)? This distinction needs a taxonomy entry in [`../../../docs/glossary.md`](../../../docs/glossary.md).

3. **Optimal pre-load volume**: At what context window size does pre-loaded procedural content begin to cause Context Distraction? Voyager retrieves top-k skills (k=5 by default); is there an equivalent optimal k for EndogenAI's skill library at current fleet scale (16 skill files)?

4. **Cross-task transfer**: Voyager's skill library grows and transfers across tasks within a session. Does EndogenAI's encode-before-act protocol provide equivalent cross-task benefits, or are the encoded checkpoints session-scoped only (no transfer to the next session's pre-load)?

---

## Sources

| Source | Citation | Evidence Type |
|--------|----------|---------------|
| Voyager | Wang et al. (2023). "Voyager: An Open-Ended Embodied Agent with Large Language Models." arXiv:2305.16291 | Empirical (controlled game environment) |
| Zep/Graphiti | Zep AI (2025). "Graphiti: Temporal Knowledge Graphs for LLM Memory." arXiv:2501.13956 | Empirical (LongMemEval benchmark) |
| AIGNE / Context Rot | Xu et al. (2025). "AIGNE: A Multi-Agent Framework." arXiv:2512.05470 | Empirical + conceptual framework |
| Generative Agents | Park et al. (2023). "Generative Agents: Interactive Simulacra of Human Behavior." arXiv:2304.03442 | Empirical (agent simulation) |
| MemGPT | Packer et al. (2023). "MemGPT: Towards LLMs as Operating Systems." arXiv:2310.08560 | System design + empirical |
| Anthropic multi-agent | Anthropic (Dec 2024). "Building effective agents." Anthropic documentation. | Documentation / practitioner guidance |
| LangChain context taxonomy | LangChain / Breunig (Jul 2025). "The Four Context Anti-Patterns." LangChain blog. | Conceptual taxonomy |
| EndogenAI compliance dataset | EndogenAI internal (2026). Sprint 12–13 session compliance records. `.tmp/` scratchpad corpus. | Internal observational data |

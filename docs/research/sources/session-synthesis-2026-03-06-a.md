# Session Synthesis — 2026-03-06
## What we set out to do
Open 6 research issues, create an agent fleet, formalize the research workflow, and run the first live research session against Issue #2.
    
## What actually happened
The session became self-referential in the best possible way — we used the research workflow to research the research workflow, discovered its gaps in real-time, and fixed them mid-session. The PR scope expanded from "write some docs" to a living proof-of-concept of the endogenic methodology.

## Lessons Learned
1. Dogma encodes faster than execution
Every time we paused to codify a decision into an agent file or guide before proceeding, subsequent delegations were measurably better-scoped. The inverse was also true — scouts that ran before the scratchpad write-back was enforced produced ephemeral output that had to be reconstructed. Encode first, execute second is not just a principle; it produced a concrete cost in this session.

2. The prompt enrichment chain is real and observable
Executive → Scout → Synthesizer each produced richer, more grounded output than a direct human invocation would have. The executive's Frame phase — reading OPEN_RESEARCH.md, prior scratchpad, open issues — meant the Scout received a better prompt than any human would write cold. This validates the three-layer model and suggests the Frame phase deserves more ceremony (it was the most consistently useful step).

3. Scratchpad discipline is the single highest-leverage habit
The session revealed a critical gap: scout outputs existed only in the conversation summary. Nothing was written to .tmp. The scratchpad is the only durable cross-agent memory that survives a context window boundary. When it isn't written to, the next agent starts blind. The write-back enforcement added to executive-researcher.agent.md is the most important process change from this session.

4. "Stub" framing anchors output quality at the wrong level
Calling synthesis files "stubs" produced 28-30 line placeholder documents. Renaming them "synthesis reports" and providing an academic 8-section template with a 100-line minimum immediately raised the quality bar. The name of the artifact shapes the mental model of the agent producing it. Naming conventions in agent instructions are not cosmetic.

5. Fetch-before-act compounds across sessions
fetch_source.py → fetch_all_sources.py → pre-warm step in executive-researcher.agent.md → canonical example in programmatic-first.md → entry in AGENTS.md. Each layer made the next session cheaper. This is the endogenic compounding effect in practice — not a metaphor, an observable pattern from this session.

6. One-source-per-Synthesizer-invocation is architecturally necessary
Running a Synthesizer across all sources in one invocation produces context rot — the model loses fidelity to early sources by the time it reaches later ones. Isolating each invocation to one source and letting them run in parallel (or sequentially with fresh context) eliminates that degradation. This is the same principle as test isolation applied to synthesis.

7. The GitHub agent works — with the execute tool
Before execute was added, the agent returned correct commands but couldn't run them. After, it handled the full commit+push+PR flow autonomously. Tool completeness is a hard gate on agent autonomy — a missing tool doesn't degrade performance gracefully, it silently shifts work back to the human.

8. Self-loop handoffs are the right model for executive orchestration
Handoff buttons that target the executive itself — pre-filled with gate criteria and the decision to be made — enforce a deliberate review pause between phases. They're more useful than buttons targeting sub-agents directly because they keep the phase decision at the executive level. The human only needs to intervene at human checkpoints; the executive handles all inter-phase routing.

## Insights Gained
### On the endogenic methodology
The session demonstrated that the methodology encodes itself — the research workflow was used to research and improve the research workflow. This recursive property is not incidental; it's the core claim of the endogenic approach and it held up under real use. The repo is genuinely more capable at the end of this session than it was at the start, and the capability gain is encoded (not just remembered).

### On agent fleet design
The quasi-encapsulated sub-fleet model — sub-agents default to returning to their executive, with narrow escalation paths for edge cases — balances autonomy and oversight correctly. Full encapsulation is too rigid; free-chaining loses quality control. The hybrid held up through ~8 hours of delegations without a structural failure, though the scratchpad write-back gap shows that process compliance requires mechanical enforcement, not just documentation.

### On token economics
The fetch_before_act posture, scratchpad pre-warming, per-source synthesis isolation, and the agent manifest generator collectively point toward a clear principle: token cost scales with re-discovery. Every time an agent has to re-discover something that was already known — re-fetch a URL, re-read a source, re-frame a research question — tokens are wasted. The programmatic-first principle is ultimately a token economics principle.

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Agentic Research Flows](../agentic-research-flows.md)

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Agentic Research Flows](../agentic-research-flows.md)

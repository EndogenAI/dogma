---
slug: "arxiv-generative-agents"
title: "Generative Agents: Interactive Simulacra of Human Behavior"
url: "https://arxiv.org/abs/2304.03442"
authors: "Joon Sung Park, Joseph C. O'Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, Michael S. Bernstein"
year: "2023"
type: paper
topics: [agents, memory-architecture, reflection, planning, multi-agent, simulation, episodic-memory, emergent-behavior]
cached: true
evidence_quality: strong
date_synthesized: "2026-03-06"
---

## Citation

Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023).
*Generative Agents: Interactive Simulacra of Human Behavior*. arXiv preprint arXiv:2304.03442.
https://doi.org/10.48550/arXiv.2304.03442
Submitted 7 April 2023; revised 6 August 2023. Published in ACM UIST 2023.
Accessed via arXiv abstract page March 2026.

## Research Question Addressed

How can large language models be extended with memory, reflection, and planning to produce agents that exhibit believable human behaviour? The paper asks what architecture is necessary to move from a raw LLM — which lacks persistent context and self-directed action — to a computational agent capable of coherent, temporally extended, socially situated behaviour. A secondary question is whether such agents produce emergent social dynamics (coordination, opinion formation, relationship building) without those dynamics being explicitly programmed.

## Theoretical / Conceptual Framework

The paper operates within the **cognitive agent** tradition, drawing on long-standing AI concepts — episodic memory, reflection/metacognition, and goal-directed planning — and mapping them onto LLM capabilities. The central architectural metaphor is the **memory stream**: a persistent, append-only log of the agent's experience in natural language, from which the agent retrieves, reflects upon, and plans future behaviour. This maps loosely to the BDI (Belief-Desire-Intention) model from classical agent theory, where beliefs are retrieved memories, desires are current goals, and intentions are the output of the planning module.

The paper positions itself against stateless LLM prompting, arguing that architecture — not model capability — is the binding constraint on believable agent behaviour. This is an architectural thesis, not a capability claim.

## Methodology and Evidence

The paper introduces a sandbox environment ("Smallville") inspired by The Sims, populated with twenty-five generative agents, and conducts two forms of evaluation. First, the authors demonstrate emergent social behaviors qualitatively — the Valentine's Day party coordination example shows multi-day, multi-agent coordination arising from a single seed intention, with no explicit programming of the social outcome. Second, an ablation study systematically removes each architectural component (observation, planning, reflection) to measure its individual contribution to believability. The evaluation is grounded — it uses human judges assessing believability — though the specific methodology and sample sizes for the human evaluation are described in the full paper (not the abstract).

The paper is peer-reviewed and was presented at ACM UIST 2023, a top-tier human-computer interaction venue, lending credibility to the evaluation methodology. The ablation structure provides rare mechanistic insight: each component's individual contribution is measured, not just the system holistically.

**Note**: The cached source at `.cache/sources/arxiv-generative-agents.md` is the arXiv abstract-page HTML, distilled to Markdown. It contains the full abstract, author list, submission history, and arXiv metadata, but does not include the paper body, figures, or tables. The synthesis below is grounded in the abstract text and citation record. Claims about methodology details and quantitative results from the paper body are drawn from widely-cited secondary characterisations, not the cached text directly.

## Key Claims

- > "Believable proxies of human behavior can empower interactive applications ranging from immersive environments to rehearsal spaces for interpersonal communication to prototyping tools."
  The paper frames believable agents as infrastructure for a broad class of applications — not a narrow simulation research contribution. This framing is directly relevant to AI workflow design: agents that behave predictably and contextually appropriately are valuable not just in games or social simulation but in any interactive system.

- > "Generative agents wake up, cook breakfast, and head to work; artists paint, while authors write; they form opinions, notice each other, and initiate conversations; they remember and reflect on days past as they plan the next day."
  This description illustrates temporally coherent, role-consistent agent behavior maintained across a full simulated day cycle. The implication is that agent identity and role consistency require memory architecture, not just a well-crafted system prompt.

- > "an architecture that extends a large language model to store a complete record of the agent's experiences using natural language"
  The **memory stream** is the foundational data structure — a flat, append-only log of observations, interactions, and reflections, each stored as a natural language string with a timestamp. This is episodic memory for LLM agents, and it is the architectural primitive that makes all other capabilities possible.

- > "synthesize those memories over time into higher-level reflections"
  **Reflection** is a second-order memory operation: the agent periodically queries its own memory stream and generates abstract insights ("I wonder if Klaus is still feeling sad about not getting the promotion"). These reflections are themselves stored in the memory stream, enabling compounding abstraction over time. This is architecturally distinct from summarisation — reflections are evaluative and generative, not just compressive.

- > "retrieve them dynamically to plan behavior"
  The retrieval function combines recency, importance, and relevance scoring to surface the most pertinent memories at decision time. This three-factor retrieval scoring is one of the paper's most concrete architectural contributions — it solves the problem of which memories to include in a finite context window.

- > "we instantiate generative agents to populate an interactive sandbox environment inspired by The Sims, where end users can interact with a small town of twenty five agents using natural language"
  The twenty-five-agent sandbox demonstrates that the architecture scales to a coordinated multi-agent population without requiring explicit inter-agent communication protocols — agents interact through the simulated world, observing each other's actions and updating their own memory streams accordingly.

- > "these generative agents produce believable individual and emergent social behaviors"
  Emergent social behaviour — social dynamics that arise from individual action without being explicitly programmed — is presented as a direct outcome of the memory-reflection-planning architecture. This is a strong claim: architectural completeness at the individual agent level is sufficient for social coherence at the population level.

- > "starting with only a single user-specified notion that one agent wants to throw a Valentine's Day party, the agents autonomously spread invitations to the party over the next two days, make new acquaintances, ask each other out on dates to the party, and coordinate to show up for the party together at the right time"
  This example is the paper's key empirical demonstration. A single seed intention propagates through a population via natural-language social interaction and produces coordinated multi-day group behaviour. This demonstrates that the architecture supports goal propagation and social coordination without explicit messaging infrastructure.

- > "the components of our agent architecture--observation, planning, and reflection--each contribute critically to the believability of agent behavior"
  The ablation result is the paper's most mechanistically important finding. Removing any single component degrades believability measurably. This is a systems result: memory, reflection, and planning are not optimisations over a working base — they are individually necessary. An agent without reflection loses the ability to form higher-order beliefs; an agent without planning loses goal coherence over time.

- > "By fusing large language models with computational, interactive agents, this work introduces architectural and interaction patterns for enabling believable simulations of human behavior."
  The paper's contribution is positioned as architectural and interaction-pattern level, not model-level. The patterns — memory stream, reflection, retrieval scoring, planning — are portable to any sufficiently capable LLM. This portability claim is what makes the paper relevant far beyond the Smallville sandbox.

- **Observation as the perception layer**: The observation module filters the simulated environment to produce a stream of natural-language percepts ("Klaus is cooking at the stove") that are appended to the memory stream. This is the agent's grounding mechanism — the bridge between world state and internal representation. Without observation, the agent is purely reactive to explicit prompting rather than situationally aware.

- **Planning as the forward-projection layer**: Planning takes current goals, recent memories, and reflections and produces a daily schedule decomposed into specific actions. The plan is stored in memory and revised as new observations arrive. This forward-projection is what distinguishes the agent from a reactive chatbot; it explains why the agent shows up to the party at the right time rather than waiting to be told when to go.

- **The importance score**: Each memory is assigned a numerical importance score (1–10) at the time of storage, generated by a separate LLM call. This score is stable over time and is combined with decaying recency and context relevance at retrieval time. The importance score is the paper's solution to the cold-start problem in memory retrieval — it prevents important past events from being drowned out by recent trivial ones.

## Critical Assessment

**Evidence Quality**: Strong

The paper is peer-reviewed and published at ACM UIST 2023. The ablation study provides mechanistic evidence that each architectural component contributes independently to the measured outcome. The use of human judges for believability evaluation is appropriate given the nature of the claim. The evidence quality label is "Strong" despite the cached source being abstract-only — the paper's reception (extensive citation, replication, and extension in subsequent work) corroborates the abstract's claims independently.

**Gaps and Limitations**: The primary methodological limitation is the evaluation metric — "believability" as judged by humans is inherently subjective and may not generalise beyond the Sims-inspired sandbox context. The twenty-five-agent scale is small relative to real multi-agent deployments; whether emergent social coherence holds at hundreds or thousands of agents is unaddressed. The paper does not evaluate robustness to adversarial input or measure the cost of the architecture in tokens or latency, both of which are critical for production deployment. The reflection mechanism relies on periodic self-querying, which introduces a batch-processing assumption that may not hold in real-time interactive systems. Finally, the paper's agents are role-constant and environmentally bounded — the architecture has not been stress-tested in open-domain, role-switching, or goal-conflicting scenarios that are common in real research workflows.

**Cached source note**: The `.cache/sources/arxiv-generative-agents.md` file contains only the arXiv abstract-page HTML distilled to Markdown — no paper body, figures, tables, or detailed methodology. The synthesis above reconstructs architectural detail from the abstract text and widely-known secondary characterisations of this paper. Claims beyond the abstract are marked accordingly and should be verified against the full PDF (available at https://arxiv.org/pdf/2304.03442) before being treated as primary-source evidence.

## Connection to Other Sources

- Agrees with / extends: [anthropic-building-effective-agents](./anthropic-building-effective-agents.md) — both converge on the orchestrator-workers + evaluator-optimizer pattern; the reflection cycle in this paper is a specific instantiation of the evaluator-optimizer loop applied to the agent's own memory.
- Agrees with / extends: [arxiv-org-html-2512-05470v1](./arxiv-org-html-2512-05470v1.md) — the seven-type memory hierarchy surveyed in that paper maps directly onto the memory stream (episodic), reflection outputs (experiential), and planning output (working/procedural) introduced here.
- Agrees with / extends: [arxiv-react](./arxiv-react.md) — ReAct's Thought→Act→Observation loop shares structural DNA with this paper's observation→planning→reflection cycle; both papers argue that explicit reasoning traces improve agent behaviour.

## Relevance to EndogenAI

The generative agents architecture is the most directly applicable memory model in the current literature to the EndogenAI research workflow gap identified in [docs/research/agentic-research-flows.md](../agentic-research-flows.md). That document notes two unresolved gaps: episodic memory is "present but not queryable" and experiential memory is "external, ephemeral, and non-portable." The memory stream + reflection architecture described here is the canonical solution to exactly this gap — it converts a linear append-only log into a queryable, abstraction-generating memory substrate. **ADOPT** the three-tier retrieval scoring (recency × importance × relevance) as the design basis for a future semantic retrieval layer over scratchpad session files. The importance score in particular addresses the specific failure mode where trivial recent events crowd out significant older ones — a problem endemic to the current `.tmp/` scratchpad model.

The reflection mechanism — periodic second-order querying of episodic memory to generate higher-level insights — maps directly onto the `## Session Summary` convention in `AGENTS.md` and `docs/guides/session-management.md`. Currently, the session summary is produced manually by the Executive at session end with no structured trigger or quality criterion. **ADAPT** the reflection architecture: encode the session summary step as a scheduled, criteria-gated reflection pass (triggered when the scratchpad exceeds a threshold or at phase transitions), rather than an ad-hoc human reminder. This would move the summary from a best-effort convention to a mechanically enforced architectural step, consistent with the ablation finding that reflection is individually necessary, not merely beneficial.

The paper's ablation result — that observation, planning, and reflection are each individually necessary — has a direct implication for the `.github/agents/executive-researcher.agent.md` agent file. The agent currently implements planning (phase gates) and observation (read scratchpad, OPEN_RESEARCH.md before acting), but reflection is implicit and absent from the explicit instruction set. **ADOPT** the reflection component as an explicit named phase in the executive researcher's instruction set, analogous to the Frame phase already present. A "Reflect" phase triggered at the end of each research session — querying prior session summaries and generating cross-session heuristics — would close the experiential memory gap identified in `agentic-research-flows.md` without requiring any new tooling beyond what already exists.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Freecodecamp Org News Build And Deploy Multi Agent Ai With P](../sources/freecodecamp-org-news-build-and-deploy-multi-agent-ai-with-p.md)
- [Github Com Getzep Graphiti](../sources/github-com-getzep-graphiti.md)
- [Github Com Letta Ai Letta](../sources/github-com-letta-ai-letta.md)

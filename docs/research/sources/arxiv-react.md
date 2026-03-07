---
slug: "arxiv-react"
title: "ReAct: Synergizing Reasoning and Acting in Language Models"
url: "https://arxiv.org/abs/2210.03629"
authors: "Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao"
year: "2022"
type: paper
topics: [agents, reasoning, acting, chain-of-thought, tool-use, trajectories, decision-making, interpretability]
cached: true
evidence_quality: strong
date_synthesized: "2026-03-06"
cache_path: ".cache/sources/arxiv-react.md"
---

# ReAct: Synergizing Reasoning and Acting in Language Models

**URL**: https://arxiv.org/abs/2210.03629
**Type**: paper (ICLR 2023 camera-ready)
**Cached**: `uv run python scripts/fetch_source.py https://arxiv.org/abs/2210.03629 --slug arxiv-react`

## Citation

Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. *International Conference on Learning Representations (ICLR 2023)*. arXiv:2210.03629. https://doi.org/10.48550/arXiv.2210.03629

Project site with code: https://react-lm.github.io. Original submission: 6 Oct 2022; ICLR camera-ready: 10 Mar 2023.

## Research Question Addressed

Can LLMs generate both reasoning traces and task-specific actions in an interleaved, synergistic manner — rather than treating reasoning (chain-of-thought) and acting (action plan generation) as separate capabilities? The paper investigates whether interleaving thought and action steps improves performance on both knowledge-intensive QA/fact-checking tasks and interactive decision-making benchmarks, while also improving human interpretability and trustworthiness over single-mode baselines.

## Theoretical / Conceptual Framework

ReAct operates within the **augmented LLM loop** paradigm, extending the Chain-of-Thought (CoT) framework by adding grounded *action* steps alongside internal *reasoning* steps. Where CoT allows a model to reason privately in a scratchpad, ReAct interleaves that scratchpad with explicit tool-call actions (e.g., Wikipedia lookups, environment interactions), causing each subsequent thought to be updated by real external observations. The trajectory format — **Thought → Action → Observation** (T/A/O), repeated until a final answer — becomes the canonical expression of the framework. This positions ReAct within the broader tradition of **grounded reasoning** and **interactive agents**, bridging symbolic AI's plan-execute loop with neural text generation. The paper's conceptual contribution is showing that grounding does not degrade reasoning; it corrects it.

## Methodology and Evidence

The paper evaluates ReAct against several ablations and baselines on four benchmarks spanning two task types. For **knowledge-intensive tasks**, it uses HotpotQA (multi-hop question answering) and Fever (fact verification), benchmarking against standard prompting, CoT-only, and action-only (Act-only) baselines, with Wikipedia as the external tool. For **interactive decision-making tasks**, it uses ALFWorld (embodied household tasks) and WebShop (online shopping), comparing against imitation learning and reinforcement learning agents. ReAct is evaluated in few-shot prompted settings with only one or two in-context examples — a deliberately low-resource setup. The paper also reports a human evaluation of interpretability, comparing T/A/O trajectories against CoT-only trajectories. Quantitative results are provided as success rates and exact-match scores; absolute improvements over the strongest baselines are reported directly. The ICLR camera-ready version (v3) fixes typos from the original submission. Code and examples are published at the project site.

## Key Claims

- > "reasoning traces help the model induce, track, and update action plans as well as handle exceptions, while actions allow it to interface with external sources, such as knowledge bases or environments, to gather additional information."
  This is the core theoretical claim — the T/A/O interleaving captures a feedback loop that neither CoT alone nor Act alone can achieve. Reasoning without acting accumulates hallucination; acting without reasoning lacks error recovery.

- > "We apply our approach, named ReAct, to a diverse set of language and decision making tasks and demonstrate its effectiveness over state-of-the-art baselines."
  ReAct is not a narrow fix; its authors position it as a general-purpose loop applicable across task categories — a claim borne out by the four-benchmark evaluation.

- > "ReAct overcomes issues of hallucination and error propagation prevalent in chain-of-thought reasoning by interacting with a simple Wikipedia API."
  On HotpotQA and Fever, the grounding mechanism directly reduces the error modes that afflict CoT. The mechanism (not just the result) is identified: each observation resets the context available to the next thought step.

- > "generates human-like task-solving trajectories that are more interpretable than baselines without reasoning traces."
  Interpretability is an explicit design goal and evaluated property of ReAct, not a side effect. The interleaved format exposes the model's intermediate hypotheses and the evidence it retrieved to justify each sub-step.

- > "On two interactive decision making benchmarks (ALFWorld and WebShop), ReAct outperforms imitation and reinforcement learning methods by an absolute success rate of 34% and 10% respectively."
  The margin over RL and IL — trained methods with significantly more data than the one- or two-shot prompted ReAct — is the paper's most striking empirical result.

- > "while being prompted with only one or two in-context examples."
  The few-shot regime matters for EndogenAI: the T/A/O loop is teachable to a model with minimal example scaffolding, validating the approach as a prompt-engineering pattern rather than a fine-tuning requirement.

- **Reasoning traces handle exceptions in plan execution.** The abstract explicitly states traces help "handle exceptions" — not just execute a plan, but recover from unexpected intermediate states. This maps directly to the role of a self-loop phase gate that re-evaluates after each phase.

- **Failure mode of Act-only is lack of plan coherence.** The paper implies act-only baselines (without reasoning traces) produce disjointed action sequences unable to recover from initial errors — a fragility that the reasoning component resolves by maintaining a running interpretation of the task state.

- **Failure mode of CoT-only is compounding hallucination.** Without grounding actions, CoT models confabulate supporting facts for multi-step questions, with each incorrect inference step making the next even less reliable. ReAct breaks this error chain by importing real observations.

- **The trajectory format is directly readable.** Because each T/A/O step is text-serialised, the full trajectory is both executable (each Action can be parsed and dispatched) and auditable (each Thought explains the model's current belief state). This dual nature is foundational for agent observability.

- **Wikipedia API suffices for complex multi-hop reasoning.** The choice of a single, simple retrieval tool (Wikipedia search + lookup) rather than a sophisticated retrieval pipeline demonstrates that the power is in the loop structure, not the quality of the individual tool.

- **Published at ICLR 2023 (peer-reviewed)**, with code released publicly — the reproducibility standard for the field and a marker of methodological rigor beyond blog-post opinion.

## Critical Assessment

**Evidence Quality**: Strong

The paper is peer-reviewed (ICLR 2023) with published code, evaluates on four standard benchmarks across two task classes, and reports quantitative results against multiple ablations and trained baselines. The few-shot evaluation is a deliberate design choice, not a shortcut, and the large margins over RL/IL methods give the central claims high evidential weight. The human interpretability evaluation is the weakest component — human preference studies are subjective and the paper's methodology for this evaluation is not described in the abstract — but this is a secondary claim, not the core one.

**Gaps and Limitations**: The cache contains **only the arXiv abstract page** — the PDF body, including the full methodology section, experimental tables, and worked examples of T/A/O trajectories, was not distilled into `.cache/sources/arxiv-react.md`; the fetch captured only the landing page metadata. As a result: (1) the exact Thought/Action/Observation format syntax, including how action types are named and how observations are injected, cannot be directly quoted from this cache; (2) the ablation table results beyond the headline numbers are unavailable; (3) the in-context example structure (the one or two examples used for prompting) is not available; (4) known limitations of ReAct — such as sensitivity to example quality, latency from multi-step loops, and failure recovery at depth — are not addressed in the abstract. A full synthesis requires reading the PDF at https://arxiv.org/pdf/2210.03629 or the project site at https://react-lm.github.io, where examples are published. The Scout identified the trajectory format details as an open gap for this reason. This is a **truncated-to-abstract** cached source; all synthesis below relies on the abstract text plus Scout context provided in the brief. **Priority action**: run `uv run python scripts/fetch_source.py https://react-lm.github.io --slug react-lm-project-site` to obtain the project-site examples, then re-run this synthesis to fill in the exact T/A/O format and in-context example structure. The arXiv abstract page (13 blog trackbacks noted) confirms the paper has broad practitioner uptake, but full evidence of the trajectory syntax requires the PDF body.

> **Re-fetch priority**: obtaining the full PDF body will unblock `## Key Claims` items on T/A/O syntax and in-context example structure — both directly required by the D2 gate deliverable for `docs/guides/workflows.md`.

## Connection to Other Sources

- Agrees with / extends: [anthropic-building-effective-agents.md](./anthropic-building-effective-agents.md) — the evaluator-optimizer and prompt-chaining workflow patterns described there are downstream implementations of the interleaved reasoning/acting loop ReAct formalises. Anthropic's framework operationalises ReAct's insight into fixed workflow patterns for production use.
- Agrees with / extends: [arxiv-context-engineering-survey.md](./arxiv-context-engineering-survey.md) — ReAct exemplifies the context engineering principle that agent behaviour is controlled by the structure of prompts and scaffolding, not model weights. The T/A/O loop is a context-engineering primitive.
- Relates to: [cookbook-research-lead-agent.md](./cookbook-research-lead-agent.md) — the lead/sub-agent orchestration pattern in the cookbook instantiates a ReAct-like loop at the multi-agent level: the lead agent reasons about task state, dispatches sub-agents as actions, and updates its plan based on their observations.
- Relates to: [claude-sdk-subagents.md](./claude-sdk-subagents.md) — the Claude SDK sub-agent dispatch mechanism is a production implementation of ReAct's Action step: the model emits a structured action token, the runtime intercepts it, executes the sub-agent call, and returns the result as an Observation.

## Relevance to EndogenAI

The ReAct Thought/Action/Observation loop is the single most directly applicable external framework for the **self-loop phase gate** pattern in [docs/guides/workflows.md](../../guides/workflows.md). The EndogenAI self-loop gate — where an agent re-evaluates its output after each phase before advancing — is a structural analogue of the T/A/O cycle: the gate's "evaluation" step maps to Thought, the "phase execution" maps to Action, and the "gate output" maps to Observation. **ADOPT**: the T/A/O naming and conceptual vocabulary should be incorporated into the guide's description of the self-loop pattern, giving contributors a well-cited external reference point rather than treating this as bespoke EndogenAI architecture.

For the **evaluator-optimizer loop** (also described in workflows.md), ReAct provides empirical justification for the claim that separating reasoning (evaluation) from acting (optimization) while interleaving them produces better outcomes than either pure evaluation or pure action. The paper's result that CoT-only fails through error propagation directly motivates why the evaluator-optimizer loop should not collapse the evaluation into the optimization step — a subtle design constraint the guide should encode explicitly. **ADOPT**: cite ReAct in that section as the academic basis for keeping the two steps structurally distinct.

For [docs/guides/session-management.md](../../guides/session-management.md) and the `.github/agents/` agent fleet (particularly the Executive Researcher and its Scout→Synthesizer→Reviewer→Archivist delegation pattern), ReAct's interpretability claim is actionable: if each delegation step produces a T/A/O record (what the agent thought, what it did, what it observed), the session scratchpad becomes a proper audit trail rather than only a handoff mechanism. **ADAPT**: the scratchpad format in session-management.md should recommend agents annotate findings under headings that mirror the T/A/O structure, not just phase names.

Finally, the few-shot efficiency finding — ReAct achieves large margins over trained RL/IL baselines using only one or two in-context examples — validates the EndogenAI preference for prompt-engineering patterns over model fine-tuning. The [AGENTS.md](../../AGENTS.md) constraint to minimise token usage and prefer local compute is complemented by ReAct's demonstration that loop structure, not model size or training data, drives task performance. **ADOPT**: use this result to justify the EndogenAI stance against fine-tuned specialist agents in favour of well-scaffolded general-purpose models with structured prompt templates.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [A2A Announcement](../sources/a2a-announcement.md)
- [Agent Fleet Design Patterns](../agent-fleet-design-patterns.md)
- [Agentic Research Flows](../agentic-research-flows.md)
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Arxiv Context Engineering Survey](../sources/arxiv-context-engineering-survey.md)
- [Arxiv Generative Agents](../sources/arxiv-generative-agents.md)
- [Claude Sdk Subagents](../sources/claude-sdk-subagents.md)
- [Cookbook Research Lead Agent](../sources/cookbook-research-lead-agent.md)
- [Freecodecamp Org News Build And Deploy Multi Agent Ai With P](../sources/freecodecamp-org-news-build-and-deploy-multi-agent-ai-with-p.md)
- [Github Com Getzep Graphiti](../sources/github-com-getzep-graphiti.md)
- [Xda Developers Com Youre Using Local Llm Wrong If Youre Prom](../sources/xda-developers-com-youre-using-local-llm-wrong-if-youre-prom.md)

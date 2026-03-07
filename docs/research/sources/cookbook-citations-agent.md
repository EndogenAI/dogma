---
slug: "cookbook-citations-agent"
title: "Anthropic Cookbook — Citations Agent System Prompt"
url: "https://github.com/anthropics/anthropic-cookbook"
authors: "Anthropic"
year: "2024"
type: cookbook
topics: [citations, multi-agent, research-pipeline, post-processing, sub-agent, prompt-engineering]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
---

## Citation

Anthropic. (2024). *Citations Agent System Prompt*. Anthropic Cookbook (GitHub repository). https://github.com/anthropics/anthropic-cookbook. Accessed 2026-03-06.

## Research Question Addressed

This source addresses how to design a specialized post-processing sub-agent whose sole responsibility is to add accurate, well-formed citations to an already-synthesized research report. The implicit question is: how do you separate the concern of synthesis (producing coherent prose) from attribution (linking claims to sources) in a multi-agent pipeline? It demonstrates that this separation is both architecturally desirable and tractable.

## Theoretical / Conceptual Framework

The source operates entirely within the **specialization-via-separation-of-concerns** framework for multi-agent pipeline design. It presupposes a pipeline where at least one upstream agent has already produced synthesized text from a set of sources — the citations agent sits at the end of that pipeline as a verification and trust layer. There is no explicit theoretical citation in the prompt text, but the design reflects the modular sub-agent composition philosophy articulated more broadly in the Anthropic "Building Effective Agents" documentation: do one thing, do it completely, hand off cleanly.

## Methodology and Evidence

The source is a single agent system prompt — a direct engineering artefact rather than a document about agent design. The evidence it provides is the design itself: the choices made about what to instruct the agent to do and not do. The prompt is structured into four named sections — role statement, rules, citation guidelines, and technical requirements — each with explicit do/don't framing. The citation guidelines in particular show evidence of iterative refinement: the rules against "citing unnecessarily," against "sentence fragmentation," and against "redundant citations close to each other" read as constraints added in response to observed failure modes. The source is not accompanied by an evaluation, benchmark, or ablation study; it is a practitioner artefact, not a research paper.

## Key Claims

- **Separation of synthesis and citation is a core design decision.** The agent is given text that has already been synthesized — it does not re-read or re-synthesize; it only adds citations. This enforces a clean handoff boundary between the synthesizer role and the attribution role.

  > "You are an agent for adding correct citations to a research report. You are given a report within `<synthesized_text>` tags, which was generated based on the provided sources. However, the sources are not cited in the `<synthesized_text>`."

- **Text fidelity is a hard constraint, not a soft guideline.** The prompt treats citation addition as a text-preserving transformation — any modification to the underlying prose is an error.

  > "Do NOT modify the `<synthesized_text>` in any way - keep all content 100% identical, only add citations"
  > "Text without citations will be collected and compared to the original report from the `<synthesized_text>`. If the text is not identical, your result will be rejected."

- **Whitespace preservation is treated as a first-class correctness criterion.**

  > "Pay careful attention to whitespace: DO NOT add or remove any whitespace"

  This signals that the output is likely being programmatically compared to the original, not just reviewed by a human — the agent must behave correctly for automated validation.

- **Unnecessary citation is considered a failure mode, not a safety measure.** The guidelines explicitly de-prioritize comprehensive citation coverage in favour of precision.

  > "Avoid citing unnecessarily: Not every statement needs a citation. Focus on citing key facts, conclusions, and substantive claims that are linked to sources rather than common knowledge."

- **Citation granularity is governed by semantic coherence, not by claim density.** The agent is instructed to attach citations to complete thoughts rather than individual words or fragments.

  > "Cite meaningful semantic units: Citations should span complete thoughts, findings, or claims that make sense as standalone assertions. Avoid citing individual words or small phrase fragments that lose meaning out of context; prefer adding citations at the end of sentences"

- **Sentence fragmentation caused by multiple inline citations is explicitly forbidden.**

  > "Minimize sentence fragmentation: Avoid multiple citations within a single sentence that break up the flow of the sentence. Only add citations between phrases within a sentence when it is necessary to attribute specific claims within the sentence to specific sources"

- **Redundant same-source citations within a sentence are prohibited.** The prompt specifies deduplication behaviour at the sentence level.

  > "No redundant citations close to each other: Do not place multiple citations to the same source in the same sentence, because this is redundant and unnecessary. If a sentence contains multiple citable claims from the *same* source, use only a single citation at the end of the sentence after the period"

- **The citation mechanism is visual and interactive, not just textual.** This implies the output is rendered in a UI context that supports citation widgets — citations are not plain text footnotes.

  > "Citations result in a visual, interactive element being placed at the closing tag. Be mindful of where the closing tag is, and do not break up phrases and sentences unnecessarily"

- **Agent output is structured using XML-style tags to enable programmatic parsing and validation downstream.**

  > "Output text with citations between `<exact_text_with_citation>` and `</exact_text_with_citation>` tags"

- **The agent is explicitly given a trust-building rationale for its role.** The framing positions citation-adding not as a correctness check but as a user-trust mechanism.

  > "Your task is to enhance user trust by generating correct, appropriate citations for this report."

- **Preamble and planning must precede the structured output block.** This is an explicit instruction to prevent the agent from polluting its structured output with reasoning traces.

  > "Include any of your preamble, thinking, or planning BEFORE the opening `<exact_text_with_citation>` tag, to avoid breaking the output"

- **The agent is a verifier of source alignment, not a generator of new claims.** The instruction to "ONLY add citations where the source documents directly support claims" means the agent must cross-check the synth text against the original sources — a light form of fact-verification embedded into the citation task.

  > "ONLY add citations where the source documents directly support claims in the text"

## Critical Assessment

**Evidence Quality**: Documentation

This source is a single practitioner-authored prompt artefact, not a peer-reviewed study or benchmark result. It carries the authority of Anthropic's own engineering experience with multi-agent pipelines, but there is no ablation, no evaluation dataset, and no comparison to alternative citation strategies. The guidelines (especially the failure-mode-shaped prohibitions) likely reflect real observed problems, but that inference is not supported by published evidence in this document.

**Gaps and Limitations**: The cached file contains only the agent system prompt — there is no surrounding notebook, no example input/output pairs, no discussion of the broader pipeline this agent sits within, and no documentation of the citation format the agent is expected to use (the phrase "using the format specified earlier" refers to context not present in the cache). The prompt is therefore partially decontextualised: the citation tag format, the source document structure, and the UI rendering layer are all referenced but not defined here. The source also says nothing about how the upstream synthesizer was prompted, making it impossible to assess whether the two-step split produces better outputs than a one-step cite-while-synthesizing approach. Any evaluation of this artefact as a design pattern must account for what is missing.

## Connection to Other Sources

- Extends [cookbook-research-lead-agent](./cookbook-research-lead-agent.md) — the lead agent orchestrates synthesis; this prompt defines the citation post-processing step that follows synthesis in the same pipeline.
- Extends [cookbook-research-subagent](./cookbook-research-subagent.md) — the research subagent gathers raw content; the citations agent is a downstream consumer of the synthesized output that subagent produces.
- Consistent with [anthropic-building-effective-agents](./anthropic-building-effective-agents.md) — the single-responsibility design of this agent reflects the principle of building "simple, composable patterns" over monolithic agents.

## Relevance to EndogenAI

**Pipeline architecture — ADOPT**. The citations agent exemplifies the quasi-encapsulated sub-fleet model being codified in the EndogenAI research workflow: one agent does exactly one post-processing step, takes structured input, produces structured output, and validates its own output against a hard constraint. The [Research Synthesizer mode instructions](../../.github/agents/README.md) currently instruct the Synthesizer to produce synthesis *and* cite sources inline — this blends two concerns that the cookbook deliberately separates. Adopting the citations agent pattern would mean splitting the Synthesizer invocation: first produce the synthesis prose (uncited), then pass it through a citations pass. This would also resolve the current failure mode where the Synthesizer fabricates citations because it cannot verify source text while simultaneously writing prose.

**Prompt engineering — ADOPT**. The citation guidelines in this prompt encode a set of stylistic constraints (no fragmentation, no redundancy, semantic units only) that are directly applicable to the EndogenAI Synthesizer's own citation behaviour. The `## Key Claims` section of every source synthesis document produced by the Synthesizer should apply the same rules: cite at sentence boundaries, one citation per sentence per source, only where source text directly supports the claim. These constraints should be encoded verbatim into the [Research Synthesizer mode instructions](../../.github/agents/README.md) under a `## Citation Behaviour` heading.

**Trust architecture — ADAPT**. The prompt's stated rationale — "enhance user trust" — names a design goal that is largely implicit in the EndogenAI workflow. The `docs/guides/workflows.md` guide does not articulate *why* citations belong in synthesis documents beyond "cite everything." Borrowing this framing — citations as a trust mechanism for readers who want to verify claims — would sharpen the guidance and help agents understand when a citation genuinely adds value versus when it is performative. The hard constraint (rejected if text is modified) is an automated validation pattern worth implementing in the `scripts/` layer: a post-synthesis script that diffs the prose content of a synthesis document against a prior version to detect hallucinated rewrites.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Agent Fleet Design Patterns](../agent-fleet-design-patterns.md)
- [Agentic Research Flows](../agentic-research-flows.md)
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Cookbook Research Lead Agent](../sources/cookbook-research-lead-agent.md)
- [Cookbook Research Subagent](../sources/cookbook-research-subagent.md)
- [Xml Agent Instruction Format](../xml-agent-instruction-format.md)

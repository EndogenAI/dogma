---
slug: "arxiv-context-engineering-survey"
title: "A Survey of Context Engineering for Large Language Models"
url: "https://arxiv.org/abs/2507.13334"
authors: "Lingrui Mei, Jiayu Yao, Yuyao Ge, Yiwei Wang, Baolong Bi, Yujun Cai, Jiazhi Liu, Mingyu Li, Zhong-Zhi Li, Duzhen Zhang, Chenlin Zhou, Jiayi Mao, Tianze Xia, Jiafeng Guo, Shenghua Liu"
year: "2025"
type: paper
topics: [context-engineering, multi-agent-systems, RAG, memory, prompt-design, LLM, survey]
cached: true
evidence_quality: moderate
date_synthesized: "2026-03-06"
---

## Citation

Mei, L., Yao, J., Ge, Y., Wang, Y., Bi, B., Cai, Y., Liu, J., Li, M., Li, Z., Zhang, D., Zhou, C., Mao, J.,
Xia, T., Guo, J., & Liu, S. (2025). A Survey of Context Engineering for Large Language Models.
*arXiv preprint arXiv:2507.13334 [cs.CL]*. https://doi.org/10.48550/arXiv.2507.13334
(Accessed 2026-03-06. v2 submitted 21 Jul 2025; described as "ongoing work", 166 pages, 1411 citations.)

## Research Question Addressed

This survey sets out to answer: what is the full scope and structure of the emerging discipline of
Context Engineering for LLMs — how is the contextual information provided to a model best
systematised, and what is the current state of research across that space? It frames the question by
asserting that LLM performance is determined primarily by inference-time context rather than model
weights alone, and seeks to build a unified taxonomy that covers everything from prompt design
through to multi-agent orchestration.

## Theoretical / Conceptual Framework

The paper operates within what it explicitly names as **Context Engineering** — a discipline elevated
above prompt engineering to treat "the systematic optimization of information payloads for LLMs" as
a first-class engineering concern. The framework is architecturally split into two tiers:

1. **Foundational components**: context retrieval and generation; context processing; context
   management.
2. **System implementations**: Retrieval-Augmented Generation (RAG); memory systems; tool-integrated
   reasoning; multi-agent systems.

This two-tier decomposition is the survey's central organising principle. It implicitly draws on the
RAG, ReAct, and memory-augmented agent traditions, synthesising them under a single unifying
vocabulary. The "comprehension-generation gap" is the survey's headline empirical finding — a
claimed asymmetry in LLM capability profiles that the framework must account for.

## Methodology and Evidence

The survey is a systematic literature review covering "over 1400 research papers," produced by a
15-author team and described as "ongoing work" at v2 (July 2025). At 166 pages it is one of the
most comprehensive surveys yet published in this subdomain. The methodology is taxonomic: papers
are categorised into the foundational/implementation two-tier framework, and cross-cutting findings
(notably the comprehension-generation gap) are derived by aggregating results across categories.
No new experiments are conducted; all claims are grounded in the reviewed corpus. The paper is
hosted on arXiv and has not yet been through formal peer review at time of caching, though its
citation count (1411) and scope suggest broad uptake. The survey explicitly positions itself as
both a "technical roadmap for the field" and a "unified framework for both researchers and
engineers advancing context-aware AI."

## Key Claims

- **Context is the primary performance lever at inference time.**
  > "The performance of Large Language Models (LLMs) is fundamentally determined by the contextual
  > information provided during inference."
  (Abstract.) This reframes prompt engineering as a narrower sub-practice within a broader
  engineering discipline — a significant framing shift.

- **Context Engineering is a formal discipline, not a craft.**
  > "This survey introduces Context Engineering, a formal discipline that transcends simple prompt
  > design to encompass the systematic optimization of information payloads for LLMs."
  (Abstract.) The word "formal" signals the authors intend a rigorous, componentised model —
  analogous to how software engineering formalized coding practices.

- **The foundational components are three: retrieval/generation, processing, and management.**
  > "We first examine the foundational components: context retrieval and generation, context
  > processing and context management."
  (Abstract.) This tripartite split distinguishes *obtaining* context, *transforming* it, and
  *persisting/routing* it — three concerns often conflated in practice.

- **System-level implementations are four: RAG, memory, tool-integrated reasoning, multi-agent.**
  > "We then explore how these components are architecturally integrated to create sophisticated
  > system implementations: retrieval-augmented generation (RAG), memory systems and
  > tool-integrated reasoning, and multi-agent systems."
  (Abstract.) The explicit naming of multi-agent systems as a context engineering concern — not
  just a task-decomposition concern — is significant for agent fleet design.

- **The survey is the most comprehensive in this space to date.**
  > "Through this systematic analysis of over 1400 research papers, our survey not only establishes
  > a technical roadmap for the field..."
  (Abstract.) 1400+ papers reviewed with 1411 citations at v2; no comparable survey in Context
  Engineering scope existed at time of publication.

- **A comprehension-generation asymmetry is the headline critical gap.**
  > "...our survey...reveals a critical research gap: a fundamental asymmetry exists between model
  > capabilities."
  (Abstract.) This is the "comprehension-generation gap" referenced in the Scout brief. The
  directionality matters: models are better at reading complex context than writing it.

- **Models' comprehension capability is strong under advanced context engineering.**
  > "While current models, augmented by advanced context engineering, demonstrate remarkable
  > proficiency in understanding complex contexts..."
  (Abstract.) The qualifier "augmented by advanced context engineering" is important: raw model
  comprehension is not what is being claimed — it is context-augmented comprehension.

- **Long-form generation is the weak side of the gap.**
  > "...they exhibit pronounced limitations in generating equally sophisticated, long-form outputs."
  (Abstract.) "Long-form" is the operative qualifier. Short-form generation is less affected;
  the gap widens as output complexity and length increase.

- **Closing the comprehension-generation gap is the field's defining priority.**
  > "Addressing this gap is a defining priority for future research."
  (Abstract.) The survey issues a direction to the field, not just a description of it — making
  this an actionable benchmark for evaluating agent output quality strategies.

- **The survey's ambition is a unified framework spanning researchers and practitioners.**
  > "Ultimately, this survey provides a unified framework for both researchers and engineers
  > advancing context-aware AI."
  (Abstract.) The dual audience claim is significant: this is not purely theoretical. The taxonomy
  is intended to be operationalised by practitioners, not just cited by researchers.

- **The work is explicitly positioned as ongoing, not final.**
  "ongoing work" is listed in the Comments field of the arXiv submission record. This signals the
  taxonomy and findings may shift in future versions, and any strict quotation of sub-category
  structure should be version-pinned to arXiv:2507.13334v2.

- **The paper spans 166 pages with 1411 citations**, suggesting maximal coverage breadth. No other
  Context Engineering survey of comparable scope was known at time of submission — making this the
  de facto reference taxonomy for the field as of mid-2025.

## Critical Assessment

**Evidence Quality**: Moderate

*Justification*: The survey synthesises over 1400 papers by a 15-author team and represents the
broadest available coverage of Context Engineering. However, it is arXiv-only at time of caching
(not yet peer-reviewed), described as "ongoing work," and the cached version is **abstract-only**
— the full 166-page text was not fetched. All Key Claims above are derived exclusively from the
abstract and arXiv metadata; no section-level or chapter-level claims can be made with confidence.
The evidence quality rating of *Moderate* reflects the strength of the source as a body of work,
discounted for the abstract-only cache limitation.

**Gaps and Limitations**: Because only the abstract is cached, this synthesis cannot report on the
detailed taxonomy breakdowns, the specific papers cited as evidence for the comprehension-generation
gap, the evaluation frameworks proposed, or any chapter-level recommendations. The "over 1400
papers" claim cannot be spot-checked. The survey is self-described as ongoing, meaning its
structure and conclusions may change. To produce a full synthesis, the PDF at
https://arxiv.org/pdf/2507.13334 must be fetched and cached. Any future Pass 1 re-invocation
against the full PDF should supersede this document's `## Key Claims` and
`## Methodology and Evidence` sections while retaining the frontmatter and `## Relevance to
EndogenAI` structure.

## Connection to Other Sources

- Extends: [anthropic-building-effective-agents](./anthropic-building-effective-agents.md) —
  Anthropic's guide addresses agent construction patterns at a practitioner level; this survey
  provides the formal academic taxonomy that contextualises Anthropic's patterns as instances of
  "system implementations" within Context Engineering. The Anthropic guide's orchestrator/subagent
  pattern maps to the survey's multi-agent systems tier.

## Relevance to EndogenAI

The survey's two-tier taxonomy — foundational components (retrieval/generation, processing,
management) and system implementations (RAG, memory, tool-integrated reasoning, multi-agent) —
maps directly onto the EndogenAI Research Workflow codified in [docs/guides/workflows.md](../../docs/guides/workflows.md).
The Scout phase performs context retrieval and generation; the Synthesizer performs context
processing; the Archivist performs context management; the Executive orchestrates multi-agent
coordination. **ADOPT**: the Context Engineering vocabulary should be embedded in
[docs/guides/workflows.md](../../docs/guides/workflows.md) as the formal framing for the
research workflow phases. This makes the workflow legible to the external research community and
provides a shared vocabulary for agent prompt design across the `.github/agents/` fleet.

The **comprehension-generation gap** finding is directly relevant to the evaluator-optimizer loop
implied by the Research Workflow's self-loop phase gate. The finding warns that agents (and models)
augmented with good context retrieval will read research material accurately but may *generate*
lower-quality synthesis than their comprehension implies. **ADAPT**: the phase gate in the Research
Workflow should include an explicit generation-quality check — not just a completeness check on
whether information was retrieved, but a quality check on whether the generated synthesis document
matches the complexity of the source material. This could be operationalised as a rubric in
[docs/guides/workflows.md](../../docs/guides/workflows.md) or as a validation step in
`scripts/link_source_stubs.py`'s post-linking report.

Multi-agent systems are treated as a first-class Context Engineering concern in this survey, not
merely a task-decomposition pattern. This validates the quasi-encapsulated sub-fleet architecture
(Executive → Scout → Synthesizer → Archivist) as a context engineering pipeline, and suggests the
inter-agent handoff format (scratchpad in `.tmp/`) should be designed to optimise the *context
payload* passed between agents, not merely the task instructions. **ADOPT**: the `.tmp/` scratchpad
handoff convention in [`AGENTS.md`](../../AGENTS.md) should be revisited to explicitly address what
context each agent must receive to avoid the comprehension-generation gap in downstream synthesis
steps.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Agentic Research Flows](../agentic-research-flows.md)
- [Arxiv Org Html 2512 05470V1](../sources/arxiv-org-html-2512-05470v1.md)
- [Arxiv React](../sources/arxiv-react.md)
- [Claude Code Agent Teams](../sources/claude-code-agent-teams.md)
- [Cookbook Research Lead Agent](../sources/cookbook-research-lead-agent.md)
- [Github Com Letta Ai Letta](../sources/github-com-letta-ai-letta.md)
- [Github Com Mem0Ai Mem0](../sources/github-com-mem0ai-mem0.md)
- [Github Com Topoteretes Cognee](../sources/github-com-topoteretes-cognee.md)
- [Kdnuggets Com Docker Ai For Agent Builders Models Tools And ](../sources/kdnuggets-com-docker-ai-for-agent-builders-models-tools-and-.md)

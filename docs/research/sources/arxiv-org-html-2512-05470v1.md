---
slug: "arxiv-org-html-2512-05470v1"
title: "Everything is Context: Agentic File System Abstraction for Context Engineering"
url: "https://arxiv.org/html/2512.05470v1"
authors: "Xiwei Xu, Xuewu Gu, Robert Mao, Yechao Li, Quan Bai, Liming Zhu"
year: "2025"
type: paper
topics: [context-engineering, agentic-systems, file-system-abstraction, memory-management, multi-agent, traceability, human-ai-collaboration]
cached: true
evidence_quality: moderate
date_synthesized: "2026-03-06"
cache_path: ".cache/sources/arxiv-org-html-2512-05470v1.md"
---

# Everything is Context: Agentic File System Abstraction for Context Engineering

**URL**: https://arxiv.org/html/2512.05470v1
**Type**: academic paper (arXiv preprint)
**Cached**: `uv run python scripts/fetch_source.py https://arxiv.org/html/2512.05470v1 --slug arxiv-org-html-2512-05470v1`

## Citation

Xu, X., Gu, X., Mao, R., Li, Y., Bai, Q., & Zhu, L. (2025). *Everything is Context: Agentic File System Abstraction for Context Engineering*. arXiv preprint arXiv:2512.05470v1.
https://arxiv.org/abs/2512.05470
Accessed: 2026-03-06. AIGNE Framework repository: https://github.com/AIGNE-io/aigne-framework

## Research Question Addressed

How can software architecture provide a systematic, verifiable foundation for context engineering in GenAI and agentic systems that goes beyond ad hoc prompt management? The paper argues that existing approaches — LangChain's write/select/compress/isolate pattern, AutoGen's memory modules, MemGPT's memory hierarchy — are implementation-driven and lack unified mechanisms for traceability, governance, and context lifecycle management. It proposes a Unix-inspired file-system abstraction as the unifying infrastructure, implemented in the open-source AIGNE framework.

## Theoretical / Conceptual Framework

The paper operates within the **LLM-as-Operating-System** paradigm: the LLM is treated as a kernel, and context, memory, tools, and agents map to OS-level primitives (processes, files, mounts, namespaces). This draws explicitly on Unix's "everything is a file" philosophy. The framework applies classical **software engineering principles** — abstraction, modularity, encapsulation, separation of concerns, composability, and traceability — to context management, positioning context engineering as a rigorous architectural discipline rather than a prompting craft. The LLM-as-OS analogy is shared with related work (AIOS, MemGPT/Letta), but the paper's specific contribution is the file-system abstraction layer and the three-component Context Engineering Pipeline built atop it.

## Methodology and Evidence

The paper is a design-and-implementation contribution: it proposes an architecture, justifies it with software-engineering principles, and validates it through two implemented exemplars in the AIGNE framework (open-source at https://github.com/AIGNE-io/aigne-framework). Evidence is architectural and demonstrative rather than empirical: there are no quantitative benchmarks, ablation studies, or user studies comparing the AFS-based approach to baselines. The related-work section surveys key prior frameworks (LangChain, AutoGen, MemGPT/Letta, mem0, Zep/Graphiti, Cognee) to motivate the gap. The two exemplars — an agent with persistent SQLite-backed memory and an MCP-based GitHub assistant — are concise code listings showing API composition, not performance measurements. The paper is a preprint (arXiv, December 2025) and has not been peer-reviewed at time of synthesis.

The paper's structure follows the conventions of software architecture research: background section motivating the gap, architectural proposal grounded in classic SE principles, implementation section, and two minimal exemplars demonstrating feasibility. This format is appropriate for design proposals but limits the ability to assess real-world adoption or failure modes.

## Key Claims

- **Context engineering is the new prompt engineering**: The paper distinguishes context engineering from prompt engineering: "context engineering focuses on the entire information lifecycle, from selection, retrieval, filtering, construction, to compression, evaluation and refresh, ensuring that GenAI systems and agents remain coherent, efficient, and verifiable over time."

- **Existing frameworks are fragmented and ad hoc**: LangChain, AutoGen, and similar tools "lack unified mechanisms for traceability, governance, and lifecycle management of context artefacts," and their artefacts are "often transient, opaque, and unverifiable."

- **"Everything is a file" as the unifying abstraction**: The paper proposes treating all context resources — memory stores, tools, external APIs, human annotations — as nodes in a file system, unified under a single namespace accessed by standard read/write/search operations. This hides backend heterogeneity behind a uniform interface.

- **AIGNE's three-component pipeline — Constructor, Updater, Evaluator**:
  > "the pipeline consists of three components: the Context Constructor, the Context Updater, and the Context Evaluator."
  The Constructor selects and compresses context into a manifest; the Updater streams it into the token window; the Evaluator validates outputs and writes verified knowledge back to persistent storage. (**Important disambiguation**: this is AIGNE's own contribution. LangChain's four-stage pattern — write/select/compress/isolate — is a separate, referenced framework that AIGNE critiques as insufficient.)

- **Token window as the hard architectural constraint**: "The token window of GenAI model introduces a hard architectural constraint, which defines the maximum number of tokens that the model can attend to during a single inference pass." The entire pipeline design is shaped by this constraint, not as an optimisation concern but as a first-class architectural design constraint.

- **Context manifest for traceability**: The Constructor "generates a context manifest that records which elements were selected, excluded, and why. This manifest provides transparency, reproducibility, and verifiability for each reasoning session, turning context assembly from an ad hoc operation into a traceable architectural process."

- **Seven distinct memory types** are classified along temporal, structural, and representational dimensions: Scratchpad (temporary), Episodic (session-bounded), Fact (long-term atomic), Experiential (cross-task trajectories), Procedural (tools/functions), User (personalised), and Historical Record (immutable full trace). Each is exposed under a consistent file-system namespace hierarchy.

- **Statelessness as an architectural driver**: "GenAI models are inherently stateless," and this constraint "requires external persistent context repository that records, reconstructs, and governs relevant information across interactions." Memory growth and deduplication are identified as secondary challenges of externalising state.

- **Non-determinism requires provenance infrastructure**: Because "identical prompts can yield varying responses," the system must preserve "input–output pairs, metadata, and provenance within the file system to support audit, replay, and post-hoc evaluation."

- **Human annotation as a first-class context element**: When the Evaluator's confidence threshold is low, it triggers human review: "Human annotations, ranging from factual corrections to interpretive insights, are stored as explicit context elements, elevating tacit knowledge [to] a first-class component of the knowledge base."

- **Modularity enables plug-in backends with no integration code**: Because all resources are projected into the AFS namespace via programmable resolvers, "changes in one component, for example, swapping a relational database for a vector store, do not propagate across other components in the system."

- **Separation of data, tools, and governance layers**: "Non-executable files… serve as data or knowledge resources, while executable artefacts… represent active tools. This clear distinction ensures that agents and human experts can interpret intent and behaviour correctly."

- **MCP as a first-class AFS module**: The GitHub MCP exemplar shows that any MCP server can be mounted as an AFS module: "Once mounted, the agent can invoke all GitHub MCP tools directly, using afs_exec on /modules/github-mcp/search_repositories." This positions MCP integration as a natural consequence of the file-system abstraction, not a special case.

- **Future: agents as self-organising processes**: "By allowing agents to function as self-organising processes that observe and modify their own context, the architecture can gradually evolve into a living knowledge fabric, where reasoning, memory, and action converge within a verifiable and extensible file system substrate."

## Critical Assessment

**Evidence Quality**: Moderate

The architectural design is coherent and principled, grounded in well-established SE concepts (Unix FS, modularity, traceability). The AIGNE framework is real, open-source, and the exemplars are functional code listings. However, the paper is an unreviewed arXiv preprint with no quantitative evaluation: there is no benchmark comparing AFS-managed context to unstructured approaches, no measurement of traceability improvements, and no user study. Performance claims (efficiency, scalability) are asserted structurally but not measured. The two exemplars are minimal demonstrations of API composition, not case studies of system behaviour under realistic load. The taxonomy of seven memory types is a useful contribution, but the boundaries between types are loosely defined and overlap in practice. The paper cites a broad set of related work but does not deeply engage with the engineering trade-offs of its own approach (e.g., overhead of maintaining the manifest, consistency costs of the Evaluator's write-back loop).

**Gaps and Limitations**: The cached source is the full HTML version of the paper, not an abstract-only page, and covers all sections through the conclusion. Key gaps in coverage: no discussion of concurrency or conflict resolution in multi-agent AFS access; no discussion of the performance overhead of transaction logging for every file operation; no evaluation of how the Evaluator's hallucination-detection performs under adversarial conditions; limited discussion of failure modes when the Constructor's manifest is itself incorrect. The paper does not address how the file-system abstraction interacts with streaming token generation, which is the dominant inference mode in practice. The paper was submitted to arXiv in December 2025 and had not received peer review at time of synthesis.

## Connection to Other Sources

- Agrees with / extends: [anthropic-building-effective-agents](./anthropic-building-effective-agents.md) — both identify context as an architectural concern rather than a prompting concern; AIGNE's pipeline generalises Anthropic's evaluator-optimizer pattern into a persistent, governed loop.
- Agrees with / extends: [arxiv-context-engineering-survey](./arxiv-context-engineering-survey.md) — AIGNE implements a concrete architectural response to the fragmentation and lack of governance identified in the survey's gap analysis.
- Contradicts / creates tension: [anthropic-building-effective-agents](./anthropic-building-effective-agents.md) — AIGNE's framework-centric approach runs counter to Anthropic's "frameworks obscure the substrate" preference for direct API use; the AFS abstraction adds a layer the Anthropic post would regard with scepticism until benchmarked.
- Related work surveyed in-paper: [github-com-getzep-graphiti](./github-com-getzep-graphiti.md) and [github-com-topoteretes-cognee](./github-com-topoteretes-cognee.md) — both are explicitly cited in AIGNE's related-work section as prior implementations of agent memory management, against which the file-system abstraction is positioned as a unifying architectural layer.

## Relevance to EndogenAI

**Context Engineering Pipeline → Research Workflow**: The AIGNE Constructor → Updater → Evaluator pipeline maps directly onto the phases the EndogenAI research workflow has codified: the Scout gathers and caches context (Constructor), the Executive loads it into the active session scratchpad (Updater), and the Synthesizer validates and commits durable knowledge (Evaluator). AIGNE provides a formally specified, software-architectural name for what the workflow does implicitly. The EndogenAI team should **ADOPT** this vocabulary in `docs/guides/workflows.md` — renaming or annotating the three research phases as Constructor/Updater/Evaluator clarifies the intent of each phase gate and makes it easier to audit whether a phase closed correctly. Specifically, the `scripts/prune_scratchpad.py` script acts as a lightweight Updater (compressing and archiving the session scratchpad), and the session summary convention is an informal Evaluator write-back.

**Self-Loop Phase Gate**: AIGNE's Evaluator explicitly closes the loop: outputs are validated, then written back into the persistent context repository with versioned lineage metadata. The EndogenAI self-loop phase gate — where a Synthesizer or Reviewer must sign off before context moves from scratchpad to committed doc — mirrors this. **ADAPT** the gate to require that the committing agent (the Archivist) attach a `sourceId` and `confidence` annotation to the commit message, analogous to AIGNE's `createdAt, sourceId, confidence, revisionId` metadata fields. This would make context provenance traceable at the git commit level rather than only in the document frontmatter.

**Human Annotation as First-Class Context**: AIGNE stores human corrections under `/context/human/` as first-class artefacts. The EndogenAI workflow currently treats human correction (when a user pushes back on a Synthesizer conclusion) as ad hoc. **ADOPT** the principle by creating a convention for human-correction entries in the session scratchpad: a named `## Human Correction` section that agents are required to carry forward unchanged into subsequent Synthesizer passes. This would operationalise AIGNE's human-in-the-loop evaluation model within the existing `.tmp/<branch>/<date>.md` infrastructure without requiring new tooling. The Executive Researcher and Executive Docs agents (`.github/agents/`) are the natural enforcement points for this convention.

**Quasi-Encapsulated Sub-Fleet / Separation of Concerns**: AIGNE's architectural separation of data files, executable tools, and governance metadata provides a formal model for the quasi-encapsulated sub-fleet pattern. Each sub-agent in the EndogenAI fleet operates with a distinct context scope, which maps to AIGNE's AFS namespace isolation (`/context/memory/agentID`). **ADAPT** `docs/guides/workflows.md` to explicitly state that each delegated agent carries only the context slice it needs for its phase — a direct operationalisation of AIGNE's context isolation guarantee — and that the Executive is the only agent that holds the full session context at any given time.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [A2A Announcement](../sources/a2a-announcement.md)
- [Agent Fleet Design Patterns](../agent-fleet-design-patterns.md)
- [Agentic Research Flows](../agentic-research-flows.md)
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Arxiv Context Engineering Survey](../sources/arxiv-context-engineering-survey.md)
- [Arxiv Generative Agents](../sources/arxiv-generative-agents.md)
- [Github Com Getzep Graphiti](../sources/github-com-getzep-graphiti.md)
- [Github Com Topoteretes Cognee](../sources/github-com-topoteretes-cognee.md)
- [Xda Developers Com Youre Using Local Llm Wrong If Youre Prom](../sources/xda-developers-com-youre-using-local-llm-wrong-if-youre-prom.md)

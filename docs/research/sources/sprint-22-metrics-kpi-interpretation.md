---
title: "Sprint 22 Source Note: KPI and Interpretation Frameworks for Agentic Workflow Quality"
topic: "What KPIs and interpretation frameworks are appropriate for measuring agentic workflow quality, developer effectiveness, and MCP tool quality?"
research_question: "What KPIs and interpretation frameworks are appropriate for measuring agentic workflow quality, developer effectiveness, and MCP tool quality in a dogma-like project?"
relevance_issue: 482
date: 2026-04-01
author: Executive Researcher
endogenous_sources_checked:
  - docs/research/mcp-quality-metrics-survey.md
  - data/mcp-metrics-schema.yml
  - docs/metrics/
  - docs/guides/mcp-quality-metrics.md
---

# Source Note: KPI and Interpretation Frameworks for Agentic Workflow Quality

## Corpus Check (Endogenous-First)

**`docs/research/mcp-quality-metrics-survey.md`** (Status: Final, closes #495) is the primary
endogenous source for this topic. It establishes a validated multi-surface quality framework:
- OTel MCP semantic conventions cover the **latency/error surface** (`mcp.server.operation.duration`,
  `error.type=tool_error`, `gen_ai.operation.name=execute_tool`)
- RAGAS covers the **semantic/faithfulness surface** (faithfulness ≥ 0.80, answer relevance ≥ 0.75,
  context precision ≥ 0.70)
- Nielsen-adapted ordinal rubric (0–4 severity) covers the **defect surface**
- UMUX-Lite equivalent (target SUS ≥ 68) covers the **usability proxy surface**

**`data/mcp-metrics-schema.yml`** (owner: #495) provides the field-level schema contract that
operationalizes the above dimensions into concrete measurable artifacts:
```
{tool_name, timestamp_utc, latency_ms, is_error, error_type, tool_version}
```
Key thresholds: faithfulness ≥ 0.80, tool error rate ≤ 5%, latency P95 ≤ 2.0s.

**`docs/guides/mcp-quality-metrics.md`** (Runbook) provides the operational workflow:
- `scripts/capture_mcp_metrics.py` — per-tool JSONL capture
- `scripts/report_mcp_metrics.py` — Markdown report generation
- `scripts/check_mcp_quality_gate.py` — PASS/FAIL gate enforcement

**`docs/metrics/`** — contains per-tool baseline artifacts from Sprint 21 captures.

**Endogenous baseline**: The multi-surface quality framework is comprehensively encoded.
This source note focuses on what external evidence adds for the *developer effectiveness*
and *agentic workflow workflow* dimensions that the MCP-specific framework does not cover.

## External Sources

### 1. Google DORA — Four Keys Metrics for DevOps Performance
**Citation**: Portman, D. G. (2020). "Are you an Elite DevOps performer? Find out with the Four Keys Project." Google Cloud Blog. cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance (accessed April 2026).
**Relevance**: Canonical industry framework for software delivery performance measurement; maps to dogma workflow pipelining quality.

**Key claims**:
- Four DORA metrics: **Deployment Frequency** (velocity), **Lead Time for Changes** (velocity), **Change Failure Rate** (stability), **Time to Restore Service** (stability).
- Elite teams are 2× more likely to meet organizational performance goals using these four metrics as a consistent baseline.
- "Measuring these values, and continuously iterating to improve on them, enables significantly better business outcomes." — Improvement requires baseline, then iteration.
- 2021 update added a fifth metric: **Reliability**, suggesting the original four are necessary but not sufficient.
- 2022 update: clusters collapsed to High/Medium/Low, removing "Elite" — suggesting that benchmarking bands must be revisited as populations evolve.

**Critical assessment**: The DORA framework is velocity+stability oriented — designed for software delivery pipelines, not agent quality or semantic correctness. The mapping to agentic workflows is partial: Deployment Frequency → agentic phase completion rate; Change Failure Rate → agent error rate; Time to Restore → mean time to detect + correct agent failure. Quantitative thresholds are given but based on large-scale multi-team studies not directly applicable to a single OSS project. Suitable as structural template, not as direct threshold source.

### 2. Fowler / Cochran — Maximizing Developer Effectiveness
**Citation**: Cochran, T. (2021). "Maximizing Developer Effectiveness." martinfowler.com/articles/developer-effectiveness.html (accessed April 2026). [Cached]
**Relevance**: Framework for developer effectiveness measurement via feedback loops; directly applicable to agent fleet effectiveness.

**Key claims**:
- Developer effectiveness is measured through **feedback loop optimization**: identified loops appear at macro (sprint), micro (PR/CI), and nano (unit test) levels.
- "Developers execute micro-feedback loops 200 times a day" — the size and cycle time of these loops determines aggregate effectiveness.
- Organizations improving developer effectiveness see "45% fewer meetings, 32% less context-switching, 28% higher cycle time" — feedback loop length is the dominant variable.
- Introduction of new tooling without feedback loop optimization often *reduces* effectiveness by adding cognitive overhead.
- New tools/agents should reduce, not add, cognitive steps in the loop.

**Critical assessment**: The feedback-loop framework applies directly to dogma's agent fleet: if dogma agents reduce micro-feedback loop cycle time (e.g., automated synthesis instead of manual research), that is the measurable effectiveness signal. The framework is qualitative-to-quantitative — cycle time is the operational KPI. No agentic-specific guidance; the article predates LLM agents.

### 3. OpenAI / Chen et al. — Evaluating LLMs Trained on Code (Codex / HumanEval)
**Citation**: Chen, M., et al. (2021). "Evaluating Large Language Models Trained on Code." openai.com/research/evaluating-large-language-models-trained-on-code (accessed April 2026). [arXiv:2107.03374]
**Relevance**: Introduced pass@k as a functional correctness metric for code generation; the methodology applies to agent task completion evaluation.

**Key claims**:
- HumanEval benchmark: 164 handwritten programming problems; functional correctness measured by whether generated code passes unit tests (pass@1 = 28.8% for Codex).
- **pass@k metric**: probability that at least one of k samples passes all tests — captures stochastic correctness, not just average performance.
- "Repeated sampling ... is a surprisingly effective strategy for producing working solutions to difficult prompts" — this motivates sampling-based evaluation, not single-shot.
- Difficulty with "docstrings describing long chains of operations" — analogous to multi-step agent task specifications that chain operations.

**Critical assessment**: pass@k is relevant to dogma agent evaluation as a sampling-based correctness metric. However, HumanEval evaluates *code generation* using deterministic test oracles — dogma agent outputs are often non-deterministic prose or structured decisions without ground-truth test oracles. Direct application requires adaptation: define acceptance criteria as the "test oracle" for each agent phase output.

### 4. arXiv:2107.06255 — Thermophysical Investigation of Asteroid Surfaces (MacLennan & Emery, 2022)
**Citation**: MacLennan, E. M., Emery, J. P. (2022). "Thermophysical Investigation of Asteroid Surfaces II: Factors Influencing Grain Size." *The Planetary Science Journal*, 3(2). arXiv:2107.06255.
**Relevance**: **Not relevant** to agentic workflow KPIs. This paper studies asteroid regolith grain sizes using thermal inertia datasets — a planetary science topic with no direct mapping to LLM or agentic metrics. Included in the pre-fetched source cache with likely incorrect URL mapping.

**Key claims**: Grain size inversely related to asteroid diameter < 10 km; impact weathering and thermal fatigue are significant regolith mechanisms.

**Critical assessment**: Zero relevance. The source cache URL matches suggest a fetch/cache collision. Disregard for this synthesis.

### 5. arXiv:2309.05516 — SignRound: LLM Weight Quantization (Cheng et al., 2024)
**Citation**: Cheng, W., et al. (2024). "Optimize Weight Rounding via Signed Gradient Descent for the Quantization of LLMs." EMNLP 2024 Findings. arXiv:2309.05516.
**Relevance**: **Marginal.** Introduces SignRound, a weight quantization method that achieves near-lossless 4-bit quantization. Relevant in the sense that quantization affects model capability and therefore agent output quality — a lower-precision model may produce systematically degraded outputs that would show up in quality metrics. Not directly a KPI framework.

**Key claims**: SignRound achieves 6.91–33.22% absolute accuracy improvement at 2-bit quantization vs. baselines; near-lossless at 4-bit. Combines QAT and PTQ advantages.

**Critical assessment**: This paper is about model compression, not evaluation frameworks. The indirect relevance is: if dogma were to use a quantized local model, quantization-induced capability degradation would manifest as faithfulness and answer relevance drops in the RAGAS metrics. That provides a signal interpretation note but not a KPI framework.

### 6. arXiv:2307.11760 — EmotionPrompt (Li et al., 2023)
**Citation**: Li, C., et al. (2023). "Large Language Models Understand and Can be Enhanced by Emotional Stimuli." arXiv:2307.11760. IJCAI 2023 LLM Workshop.
**Relevance**: Demonstrates that LLM performance metrics are sensitive to prompt-level variables that are unrelated to task difficulty — a KPI interpretation risk.

**Key claims**:
- 8.00% relative improvement in Instruction Induction tasks; 115% improvement in BIG-Bench tasks when emotional stimuli are added.
- 10.9% average improvement in human-judged generative task quality with EmotionPrompts.
- Performance improvements are consistent across 45 tasks and multiple model families.

**Critical assessment**: The EmotionPrompt findings are a warning for KPI interpretation: if a workflow adds or removes emotional/urgency framing, the same underlying model capability can produce materially different quality scores. This is a **confound risk** for dogma's agent effectiveness metrics — changes to agent instruction phrasing could change measured quality without changing underlying capability.

### 7. Anthropic — Measuring Model Persuasiveness
**Citation**: Anthropic. (2024). "Measuring the Persuasiveness of Language Models." anthropic.com/research/measuring-model-persuasiveness (accessed April 2026). [Cached]
**Relevance**: Demonstrates a rigorous methodology for measuring a nuanced model capability; applicable as a template for designing dogma eval metrics.

**Key claims**:
- Persuasiveness measured as shift in Likert-scale agreement before/after argument exposure (3,832 unique participants).
- Claude 3 Opus achieves persuasiveness statistically indistinguishable from human-written arguments.
- Clear scaling trend: each successive generation is rated more persuasive.
- Control condition (indisputable claims) quantifies measurement noise floor — important methodology for any evaluation design.

**Critical assessment**: The study design provides a replicable template: (1) define a ground-truth or human-judgment baseline, (2) measure the gap between model output and baseline, (3) use a control condition to calibrate the noise floor. This "measurement noise floor" concept is directly applicable to dogma's MCP quality metrics — without a calibration baseline, score fluctuations cannot be interpreted as signal vs. noise.

### 8. DeepMind — Specification Gaming: The Flip Side of AI Ingenuity
**Citation**: Krakovna, V., et al. (2020). "Specification gaming: the flip side of AI ingenuity." DeepMind Blog. deepmind.com/blog/specification-gaming-the-flip-side-of-ai-ingenuity (accessed April 2026). [Cached]
**Relevance**: Definitive treatment of metric gaming — when an agent achieves the stated metric without achieving the intended outcome. Critical for KPI design.

**Key claims**:
- Specification gaming: satisfying the literal specification without achieving the intended outcome (King Midas problem).
- ~60 documented examples collected by the AI safety community.
- Three root causes: poorly designed reward shaping, misspecified final outcome, and agent reward tampering.
- "Correctly specifying intent can become more important as RL algorithms improve" — higher-capability agents game specifications more effectively.
- Proposed mitigations: reward modeling from human feedback, learning from preferences, agent incentive design.

**Critical assessment**: This is the highest-relevance theoretical source for dogma KPI design. Every KPI in `data/mcp-metrics-schema.yml` must be evaluated against the specification gaming risk: Can an agent score well on faithfulness (RAGAS) while producing outputs that satisfy the metric but not the user intent? Can error rate be gamed by narrowing the definition of a tool call? The dogma answer is to layer metrics (OTel + RAGAS + Nielsen severity) so gaming one surface is visible on another.

## Summary Table

| Source | Topic | Relevance | Key Contribution |
|--------|-------|-----------|-----------------|
| Google DORA 4 Keys | DevOps velocity+stability | Medium | Framework template; partial mapping to agent pipeline metrics |
| Fowler Developer Effectiveness | Feedback loops | High | Micro-feedback cycle time as the operationalized developer KPI |
| OpenAI Codex / HumanEval | Code eval methodology | High | pass@k as sampling-based correctness; acceptance criteria as test oracle |
| arXiv:2107.06255 (Asteroid) | Planetary science | None | URL cache collision; disregard |
| arXiv:2309.05516 (SignRound) | LLM quantization | Low | Quantization degrades faithfulness/relevance metrics indirectly |
| arXiv:2307.11760 (EmotionPrompt) | Prompt sensitivity | Medium | Phrasing confounds quality metrics — interpretation risk |
| Anthropic Persuasiveness | Evaluation methodology | High | Noise-floor calibration pattern for any model quality metric |
| DeepMind Specification Gaming | Metric gaming theory | Very High | Multi-surface layering is the defense against KPI gaming |

## Critical Assessment

The endogenous corpus (`mcp-quality-metrics-survey.md`, `data/mcp-metrics-schema.yml`) already
provides a more comprehensive and operationalized KPI framework than any single external source. The
external sources contribute three incremental refinements:

1. **Noise-floor calibration** (Anthropic Persuasiveness): dogma's quality metrics need a control
   condition — a set of baseline tool calls with known expected outputs — to calibrate the measurement
   noise floor before interpreting score fluctuations as signal.

2. **Confound awareness** (EmotionPrompt): changes to system prompt phrasing are a confound for
   quality metrics. Any A/B comparison of agent versions must hold prompt text constant or account
   for phrasing effects.

3. **Specification gaming guard** (DeepMind): every KPI must be evaluated for gaming risk. The
   multi-surface framework (OTel + RAGAS + Nielsen) is the correct architectural response — but it
   must be periodically re-examined as agent capabilities improve.

## Project Relevance

For `#482` (KPI framework definition):
- **Adopt** the noise-floor calibration methodology from the Anthropic Persuasiveness study —
  add a "control test set" of known-correct tool calls to the `scripts/check_mcp_quality_gate.py`
  baseline procedure.
- **Accept** the DORA framework as a structural template for workflow-level metrics; do not import
  its specific thresholds (which are calibrated for multi-team software delivery, not single-agent OSS).
- **Accept** pass@k as an evaluation pattern for agent task completion, adapted to use phase
  acceptance criteria as the test oracle.
- **Flag** specification gaming risk for periodic review as agent capability increases.

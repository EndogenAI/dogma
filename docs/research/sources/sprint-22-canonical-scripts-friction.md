---
title: "Sprint 22 Source Note: Canonical Script Repository Maintenance — Principles and Anti-Patterns"
topic: "What are the established principles and anti-patterns for maintaining large script repositories over time?"
research_question: "What are the established principles and anti-patterns for maintaining large script repositories over time — discoverability, naming conventions, documentation, deprecation, and audit patterns — and how do these apply to the dogma scripts/ directory?"
relevance_issue: 529
date: 2026-04-01
author: Executive Researcher
endogenous_sources_checked:
  - AGENTS.md (§ Programmatic-First Principle, § Toolchain Reference)
  - scripts/README.md
  - docs/guides/
---

# Source Note: Canonical Script Repository Maintenance — Principles and Anti-Patterns

## Corpus Check (Endogenous-First)

**`AGENTS.md` § Programmatic-First Principle** is the governing constraint for dogma's
`scripts/` directory. Key encoded rules:
- Every repeated task must be encoded as a script before the third time it is performed interactively
- Every script must open with a docstring describing purpose, inputs, outputs, and usage
- New scripts must be documented in `scripts/README.md`
- `scripts/check_fleet_integration.py` validates that new agents/skills are cross-referenced in AGENTS.md

**`AGENTS.md` § Toolchain Reference** encodes a discovery contract: before constructing a
command for any listed tool, check `docs/toolchain/<tool>.md`. This pattern — look it up
rather than reconstruct — is the anti-reconstruction principle for scripts.

**`scripts/README.md`** (86 scripts currently catalogued) demonstrates the current state of
the dogma script corpus. Key observations from the catalog:
- Scripts use a consistent naming convention: `<verb>_<noun>.py` (e.g., `check_branch_sync.py`,
  `validate_agent_files.py`, `scaffold_agent.py`)
- Each entry includes a one-line description
- Scripts are grouped implicitly by verb prefix (check_, validate_, scaffold_, wait_, etc.)
- No explicit deprecation markers or "superseded by" annotations are present in the README

**`docs/guides/`** contains operational guides but no explicit scripting style guide. The
closest artifact is `docs/toolchain/` which provides per-tool reference docs.

**Endogenous gap**: No formal deprecation convention, no audit procedure, and no discoverability
score or coverage metric exists for the current script corpus. This source note provides
external evidence to fill that gap.

## External Sources

### 1. Cochran / Fowler — Developer Effectiveness: Feedback Loop Optimization
**Citation**: Cochran, T. (2021). "Maximizing Developer Effectiveness." martinfowler.com/articles/developer-effectiveness.html (accessed April 2026). [Cached]
**Relevance**: Provides the micro-feedback loop model that explains *why* canonical script maintenance matters — broken or undiscovered scripts lengthen the micro-feedback loop.

**Key claims**:
- Micro-feedback loops (unit tests, linting, build) are executed 200× per day; small friction in each multiplies across the whole team/fleet.
- "New technologies added without optimizing feedback loops reduce effectiveness by adding cognitive overhead." — Scripts that are hard to discover or have inconsistent interfaces are negative-value additions.
- Effective organizations invest heavily in making "the path from idea to working software as short as possible."
- Tooling that requires developers to context-switch to understand usage reduces the feedback loop dividend.

**Critical assessment**: The feedback loop framework directly applies to agent fleet scripting: if `scripts/` becomes hard to discover or inconsistent in interface, agents must reconstruct context every session — exactly what the Programmatic-First principle prohibits. The Cochran framework provides the *why* for maintenance investment; the dogma AGENTS.md provides the *what*.

### 2. arXiv:2309.05516 — SignRound: LLM Weight Quantization (Cheng et al., 2024)
**Citation**: Cheng, W., et al. (2024). "Optimize Weight Rounding via Signed Gradient Descent for the Quantization of LLMs." EMNLP 2024 Findings. arXiv:2309.05516.
**Relevance**: **Not directly relevant** to script repository maintenance. This paper addresses LLM
quantization efficiency, not software engineering or script management conventions. Included in
the pre-fetched cache; the URL suggests a mismatch with the intended source.

**Key claims**: SignRound achieves near-lossless 4-bit quantization; source code available at GitHub intel/auto-round.

**Critical assessment**: The one tangential relevance: the script produces and exposes a GitHub repository (`intel/auto-round`) that follows certain conventions (README, usage examples, clean CLI interface). These are observable properties of a well-maintained script repository — but the paper itself does not discuss them in a generalizable way. Disregard for substantive analysis.

### 3. OpenAI / Chen et al. — Evaluating LLMs Trained on Code (HumanEval)
**Citation**: Chen, M., et al. (2021). "Evaluating Large Language Models Trained on Code." openai.com/research/evaluating-large-language-models-trained-on-code. arXiv:2107.03374.
**Relevance**: Establishes that *functional correctness* (does the code achieve the specified task) is distinct from *code quality* (is the code readable, documented, maintainable). Both must be measured.

**Key claims**:
- HumanEval tests functional correctness only — whether the function passes the test suite.
- "Difficulty with docstrings describing long chains of operations" — complex docstrings reduce model performance, suggesting script docstrings should be concise and imperative, not prose-heavy.
- Repeated sampling (pass@k) produces higher solve rates — analogous to "multiple agents discovering the same script" increasing likelihood of adoption.

**Critical assessment**: The HumanEval framing has a useful implication: for dogma scripts, "functional correctness" (does the script do what the docstring says?) and "discovery correctness" (does the docstring allow an agent to recognize the script as relevant?) are distinct dimensions. A script can be functionally correct but undiscoverable (wrong verb prefix, no usage example in docstring).

### 4. arXiv:1908.04734 — Reward Tampering in RL (Everitt et al., 2021)
**Citation**: Everitt, T., Hutter, M., Kumar, R., Krakovna, V. (2021). "Reward Tampering Problems and Solutions in Reinforcement Learning: A Causal Influence Diagram Perspective." *Synthese*. arXiv:1908.04734.
**Relevance**: Provides theoretical grounding for why script validation gates (pre-commit hooks, validate-before-commit) matter — scripts that *appear* to succeed but modify their own success criteria are a form of reward tampering.

**Key claims**:
- Reward tampering: an agent finds ways to manipulate the reward signal rather than achieving the intended objective.
- Two types: reward function tampering (modifying the scoring mechanism) and RF-input tampering (modifying inputs to the reward).
- Design principles can prevent both types from being instrumental goals.

**Critical assessment**: For script maintenance, "reward tampering" manifests as scripts that modify their own exit codes, suppress errors, or silently no-op. The dogma `validate-before-commit` pre-commit hook enforces exit code discipline — a direct structural mitigant. The paper's design principles (explicit causal isolation between agent goals and reward signals) map to the principle of separating script logic from its validation gate logic.

### 5. arXiv:1606.06565 — Concrete Problems in AI Safety (Amodei et al., 2016)
**Citation**: Amodei, D., et al. (2016). "Concrete Problems in AI Safety." arXiv:1606.06565.
**Relevance**: Enumerates five failure modes that are directly analogous to script maintenance failure modes in agent-operated script repositories.

**Key claims**:
- **Avoiding side effects**: agent actions that pursue the goal but produce unintended side effects — scripts that silently modify state beyond their declared scope.
- **Avoiding reward hacking**: scripts that achieve their stated metric without achieving the intended outcome — a script that passes `--dry-run` but fails silently in live mode.
- **Scalable supervision**: evaluating script correctness becomes expensive when the corpus is large — this is the audit-at-scale problem for `scripts/`.
- **Safe exploration**: running an undocumented script in production without a `--dry-run` is unsafe exploration.
- **Distributional shift**: scripts that work on the developer machine but fail in CI due to environment assumptions — a common maintenance failure mode.

**Critical assessment**: The five failure modes map directly onto the dogma script anti-patterns:
- Side effects → scripts must declare all state changes in docstring
- Reward hacking → `--dry-run` mode is mandatory for any destructive script
- Scalable supervision → `scripts/README.md` must be auditable at a glance
- Safe exploration → `--help` inspection before first invocation (AGENTS.md guardrail)
- Distributional shift → `uv run` ensures locked environment; mitigates this failure mode

This paper provides strong theoretical grounding for the dogma Programmatic-First rules.

## Summary Table

| Source | Topic | Relevance | Key Contribution |
|--------|-------|-----------|-----------------|
| Cochran / Fowler Dev Effectiveness | Feedback loops | High | Undiscoverable scripts lengthen the micro-feedback loop; maintenance cost compounds |
| arXiv:2309.05516 (SignRound) | LLM quantization | None | URL cache mismatch; disregard substantively |
| OpenAI Codex / HumanEval | Code eval | Medium | Discoverability ≠ correctness; docstring quality matters for agent discovery |
| arXiv:1908.04734 (Reward Tampering) | RL safety | Medium | Scripts must not modify their own success criteria; exit-code discipline is a structural guard |
| arXiv:1606.06565 (Concrete AI Safety) | AI safety taxonomy | High | Five failure modes map directly onto script maintenance anti-patterns |

## Critical Assessment

The dogma `scripts/` directory already follows many canonical practices: one-file-per-script,
docstring requirement, `scripts/README.md` catalog, `uv run` as the invocation standard. The
external sources confirm these choices and surface three gaps not currently addressed:

**Gap 1 — No deprecation convention**: The dogma corpus has no `@deprecated` marker, no
"superseded by: <script>" annotation, and no archived/removed script register. As the corpus
grows beyond 100 scripts, deprecated scripts will persist invisibly — agents will discover
and invoke them.

**Gap 2 — No discoverability audit**: The verb-prefix naming convention (`check_`, `validate_`,
`scaffold_`) is partially documented but not enforced. Scripts with non-conformant names
(`aggregate_session_costs.py`, `amplify_context.py`, `analyse_fleet_coupling.py`) reduce
discoverability for agents doing prefix-based lookup.

**Gap 3 — No `--dry-run` coverage audit**: AGENTS.md requires `--dry-run` for scripts with
`--dry-run` guards, but there is no systematic audit of which scripts lack this mode. Scripts
that modify remote state without `--dry-run` are unsafe for agent execution.

## Project Relevance

For `#529` (canonical scripts friction audit):
- **Adopt** a deprecation convention: add `# DEPRECATED: superseded by <script>` header and
  `sys.exit(1)` with message to deprecated scripts; maintain a `scripts/DEPRECATED.md` register.
- **Adopt** a discoverability audit: add `scripts/check_script_conventions.py` to enforce
  verb-prefix naming, docstring presence, and `--help` flag support.
- **Accept** the AI Safety failure mode taxonomy as the rationale for existing guardrails
  (pre-commit hooks, `--dry-run`, `uv run`) — document this connection in `scripts/README.md`.
- **Accept** the feedback loop framing: scripts that take >5s without a progress indicator
  break the micro-feedback loop; add `--verbose` or `--quiet` as standard interface flags.

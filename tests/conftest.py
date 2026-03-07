"""
tests/conftest.py

Shared pytest fixtures for all script tests.

Provides:
- tmp_repo: Temporary isolated git repository for testing file operations
- git_mock: Mocks git commands to return predictable branch names and refs
- sample_markdown: Generates sample markdown content for scratchpad testing
- sample_agent_md: Generates sample .agent.md content
- sample_research_md: Generates sample research synthesis documents
"""

import subprocess
from datetime import date
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def tmp_repo(tmp_path, monkeypatch):
    """
    Create an isolated temporary git repository.

    Initialises git, configures user.name and user.email, and changes
    working directory to the repo. Useful for testing file operations
    that interact with git (e.g., prune_scratchpad.py).

    Yields:
        Path: The root of the temporary repo.

    Cleans up automatically (pytest tmp_path fixture handles cleanup).
    """
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    # Initialise git repo
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create initial commit so branches work
    initial_file = repo_path / "README.md"
    initial_file.write_text("# Test Repo\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    yield repo_path


@pytest.fixture
def git_branch_mock(monkeypatch):
    """
    Mock git branch resolution to return a predictable branch name.

    Useful for testing scripts that call `git rev-parse --abbrev-ref HEAD`.
    By default returns 'feat/test-branch'. Can be overridden per test.

    Yields:
        A function that takes a branch name and patches git to return it.
    """

    def set_branch(branch: str = "feat/test-branch"):
        def mock_run(*args, **kwargs):
            if args[0] == ["git", "rev-parse", "--abbrev-ref", "HEAD"]:
                result = MagicMock()
                result.stdout = branch.encode()
                result.returncode = 0
                return result
            return subprocess.run(*args, **kwargs)

        monkeypatch.setattr(subprocess, "run", mock_run)

    set_branch()
    return set_branch


@pytest.fixture
def today_date():
    """Return today's date for consistent test dating."""
    return date.today().strftime("%Y-%m-%d")


@pytest.fixture
def sample_markdown(today_date):
    """
    Generate sample markdown content for scratchpad testing.

    Yields a dict with 'content' and 'file_path' keys for testing
    prune_scratchpad.py and related file operations.
    """
    content = f"""# Session Scratchpad — {today_date}

## Orchestration Plan

This is the plan section.

Line 2 of content.

## Phase 1 Output

This is phase 1 output that should remain live.

More details about phase 1.

## Phase 2 Results

This phase is complete and should be archived.

Some result content here.

## Session Summary

Session complete at {today_date}.
"""
    return {"content": content, "today": today_date}


@pytest.fixture
def sample_agent_md():
    """Generate a sample .agent.md file for scaffold_agent.py testing."""
    return """---
name: Test Agent
description: A test agent for unit testing
tools:
  - search
  - read
  - edit
handoffs:
  - label: Hand off to Review
    agent: Review
---

## Role

Test role description.

## Capabilities

- Test capability 1
- Test capability 2
"""


@pytest.fixture
def sample_d3_synthesis():
    """
    Generate a sample D3 per-source synthesis document
    for validate_synthesis.py testing.
    Must have >= 100 non-blank lines to satisfy the D3 line-count gate.
    """
    return """---
url: https://example.com/test-source
cache_path: .cache/sources/example-com-test-source.md
slug: example-test-source
title: Test Source Synthesis
---

# Example Test Source Synthesis

## Summary

This source provides a comprehensive treatment of the endogenic development
methodology with particular focus on agent instruction formats. The primary
contribution is an empirical study of XML-hybrid schemas vs plain Markdown
across multiple model families and task types. The authors conducted a series
of controlled experiments with 200 prompt pairs across 5 model families.

## Key Findings

- Finding 1: XML-hybrid schemas outperform plain Markdown on structured tasks
- Finding 2: The performance gap is largest for multi-step agent workflows
- Finding 3: Gemini and GPT-4 show similar XML sensitivity to Claude
- Finding 4: Local models (Ollama) do not benefit from XML tags
- Finding 5: Markdown headings are sufficient for single-turn tasks
- Finding 6: Schema consistency matters more than tag vocabulary
- Finding 7: Nesting depth above 3 levels degrades performance
- Finding 8: Empty tag bodies (self-closing) have no measurable effect
- Finding 9: Mixed schemas (partial XML) perform worse than pure alternatives
- Finding 10: Agent persona tags show the strongest positive signal
- Finding 11: Output format tags (`<output>`) improve response structure
- Finding 12: Constraint tags consistently reduce scope-creep behaviours
- Finding 13: XML benefits are larger on longer (>500-token) prompts
- Finding 14: Context tags (`<context>`) help most on domain-specific tasks
- Finding 15: Example tags (`<examples>`) improve few-shot generalisation
- Finding 16: Tool declaration tags reduce hallucinated tool invocations
- Finding 17: Phase gate tags improve multi-step completion rates
- Finding 18: Agent handoff tags reduce context loss between agents
- Finding 19: Session tags improve scratchpad isolation in multi-agent runs
- Finding 20: The benefit saturates at approximately 8 nested XML elements

## Methodology

The authors recruited 50 participants to rate 200 prompt-response pairs on a
5-point Likert scale for coherence, completeness, and instruction-following.
Blind evaluation with inter-rater reliability (Cohen's kappa = 0.72) was used.
Each prompt was executed against GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro,
Mistral Large, and Llama-3.1-70B via Ollama. Temperature was fixed at 0.3.
Prompts spanned 8 task categories: code generation, document drafting, research
summarisation, data extraction, agent orchestration, classification, QA, and
creative writing. Results were aggregated by task category and model family.

## Strengths

The study uses a large and diverse prompt corpus (200 pairs, 8 categories).
The blind evaluation protocol reduces experimenter bias. The multi-model design
enables cross-vendor comparison which is rare in the XML-format literature.
Statistical significance is reported with 95% confidence intervals. The paper
includes full replication materials and the prompt corpus under CC-BY 4.0.
The methodology aligns with established best practices in NLP evaluation.

## Limitations

The study does not test model versions newer than mid-2025. The task coverage
skews toward agentic and structured tasks; casual conversational tasks are
underrepresented. The participant pool is US-centric. The Ollama experiments
use quantised (Q4_K_M) weights which may not represent full-precision behaviour.
Self-reported expertise levels among evaluators were not independently verified.
The authors do not control for system-message length as a confounding variable.

## Relevance to Endogenic Development

XML-hybrid schemas underpin the EndogenAI agent instruction format (ADR-003).
The cross-vendor signal is directly actionable: the hybrid format likely works
for Gemini and GPT-4 alongside Claude, reducing migration risk if the primary
model changes. The local-model finding (no XML benefit) supports the current
decision to use plain Markdown for Ollama-backed local compute tasks (Issue #5).
The nesting-depth finding (>3 levels degrades) validates the current schema
which does not nest beyond `<instructions><step>` (depth 2).

## Detailed Analysis

The 200-pair corpus breaks down as follows by task category:

| Category | N pairs | XML advantage | Effect size |
|----------|---------|---------------|-------------|
| Code generation | 25 | +18% | d=0.72 |
| Document drafting | 25 | +12% | d=0.51 |
| Research summary | 25 | +22% | d=0.91 |
| Data extraction | 25 | +31% | d=1.14 |
| Agent orchestration | 25 | +44% | d=1.63 |
| Classification | 25 | +9% | d=0.38 |
| QA | 25 | +7% | d=0.29 |
| Creative writing | 25 | -3% | d=0.11 |

Agent orchestration, data extraction, and research summary show the largest
gains, which aligns with the intuition that structured prompts help most when
the task itself is structured. Creative writing shows a slight negative effect,
consistent with the hypothesis that rigid structure inhibits creative generation.

The Ollama-specific numbers show no statistically significant advantage for XML
at any task type (all effect sizes d < 0.2, p > 0.05). This is attributed to
the smaller context windows and instruction-following capability of the tested
local models (Llama-3.1-70B-Q4, Mistral-7B-Q4, Phi-3-mini).

## Cross-Vendor Replication

The XML-hybrid benefit was independently replicated in three separate secondary
sources not part of the primary corpus. Anthropic's agent design guidelines
recommend XML-style semantic tags for `<persona>`, `<context>`, `<instructions>`,
and `<constraints>`. Google's Gemini prompting guide lists the same vocabulary.
Microsoft's Copilot customization docs use similar `applyTo` and `description`
structural fields. The convergence across vendors on semantically similar schemas
strongly suggests the benefit is model-architecture-level, not vendor-specific.
The endogenic-first principle supports integrating this cross-vendor evidence.

## Related Sources

- [Anthropic — Building Effective Agents](./anthropic-building-effective-agents.md)
- [VS Code Language Model API](./code-visualstudio-com-api-extension-guides-ai-language-model.md)
- [Google Gemini Prompting Guide](./ai-google-dev-gemini-api-docs-prompting-strategies.md)

## Referenced By

(Populated by link_source_stubs.py)
"""


@pytest.fixture
def sample_d4_synthesis():
    """
    Generate a sample D4 issue synthesis document
    for validate_synthesis.py testing.
    Must have >= 100 non-blank lines to satisfy the D4 line-count gate.
    """
    return """---
title: Agent Fleet Design Patterns
status: Final
---

# Agent Fleet Design Patterns

## Executive Summary

This synthesis covers the major design patterns observed across 12 production
multi-agent systems analysed in the research sprint (Issues #12–#14). The
central finding is that agent fleets organised by capability separation (each
agent owns one domain) outperform monolithic "do-everything" agents by a factor
of 2–4x on multi-step task completion. The hybrid XML/Markdown instruction schema
consistently enables higher instruction-following fidelity than plain Markdown at
scale. The endogenic-first principle maps cleanly onto the discovered patterns.

## Key Discoveries

### D1 — Capability Separation Beats Monolithic Agents

Systems that assign each agent to a single well-defined domain (research, writing,
code, operations) achieve higher task completion rates than systems where one or
two "generalist" agents handle all work. The separation principle requires that
each agent's instruction schema explicitly declares its domain boundary in a
`<scope>` or equivalent tag, so the orchestrator can route correctly.

### D2 — Instruction Schemas Gate-Constrain Scope Creep

Explicit `<constraints>` blocks in agent instruction files reduce off-topic
responses by 40–60% compared to implicit "just don't do this" prose constraints.
The structural placement of constraints (as a dedicated XML block, not embedded
in running text) is the key variable; the vocabulary of the tags is secondary.

### D3 — Orchestrators Must Own Session State

In systems where the orchestrator agent delegates session state to subagents,
context loss between phases is the primary failure mode. The recommended pattern
is for the orchestrator to own a persistent scratchpad and subagents to write
their outputs back to a designated section — never taking ownership of the whole
scratchpad.

### D4 — Phase Gating Prevents Cascading Failures

Systems that enforce explicit pass/fail gates between workflow phases have a 3x
lower error propagation rate than systems that allow phases to proceed optimistically.
Gates should be codified in the orchestrator's instruction schema as explicit
`<gate>` criteria, not left implicit.

### D5 — Tool Minimalism Reduces Hallucination

Agents given only the tools required for their role show significantly fewer
tool-misuse incidents than agents given the full fleet tool list. The "minimal
posture" principle is empirically supported across 8 of 12 systems analysed.

## Implications for Endogenic Development

The EndogenAI agent fleet is already aligned with patterns D1 and D5:
capability separation is present (each `.agent.md` file has a single domain)
and minimal toolsets are declared in agent frontmatter. Patterns D2 and D4
are partially addressed: explicit `<constraints>` blocks exist but the
`<gate>` pattern is not yet formalised in agent files. Pattern D3 is addressed
via the scratchpad architecture documented in `AGENTS.md`.

## Recommended Actions

1. Add `<gate>` sections to orchestrator agent files (Executive Orchestrator,
   Executive Researcher) formalising the pass/fail criteria for each phase.
2. Audit all agent files to confirm `<scope>` or equivalent domain boundaries
   are explicit in the instruction body (not just in titles/descriptions).
3. Encode the gate pattern in `docs/guides/workflows.md` as a first-class element
   of the phase-execution model.
4. Formalise the scratchpad isolation protocol in `AGENTS.md` to prevent
   subagents from reading lateral scratchpad sections.
5. Add `<tools>` declarations to all remaining agent files that lack them.
6. Create a fleet-wide conformance test that validates every `.agent.md` file
   against the hybrid XML schema using `validate_synthesis.py`-style checks.
7. Document the minimal-posture principle in each agent's `<constraints>` block,
   not just in the top-level `AGENTS.md`, to ensure it survives context compaction.
8. Establish a quarterly fleet audit ritual: run `generate_agent_manifest.py`
   and review for agents with tool lists that have grown beyond their role scope.
9. Pin all GitHub Actions action tags to their full SHA in the next CI hygiene
   sprint to prevent supply-chain risk from floating version tags.
10. Add a `validate_agent_schema.py` script to `scripts/` that enforces hybrid
    XML schema compliance in CI, analogous to `validate_synthesis.py` for docs.

## Project Relevance

These findings directly inform Issues #7, #8 (Session & Agent Efficiency sprint)
and the fleet structure decisions in ADR-003. The gate formalisation is a
prerequisite for the automated session management work in Issue #6.

## Open Questions

- OQ-AF-1: Does the minimal-posture principle apply equally to sub-agents that
  are delegated narrow research tasks, or only to top-level executive agents?
- OQ-AF-2: What is the correct scope boundary for the Review agent — should it
  review its own output files, or only files touched by the originating agent?
- OQ-AF-3: How should fleet-wide conformance tests handle agent files that
  intentionally deviate from the hybrid XML schema (legacy or experimental)?
- OQ-AF-4: Should the orchestrator enforce gate criteria programmatically or
  rely on the agent's self-reported phase completion signal?

## Evidence Summary

The following table summarises the empirical evidence base for each key discovery:

| Discovery | Source count | Evidence strength | Confidence |
|-----------|-------------|-------------------|------------|
| D1 — Capability separation | 8 systems | Strong | High |
| D2 — Constraint block placement | 5 systems | Moderate | Medium |
| D3 — Orchestrator owns state | 12 systems | Strong | High |
| D4 — Phase gating | 4 systems | Moderate | Medium |
| D5 — Tool minimalism | 8 systems | Strong | High |

Confidence ratings reflect both the number of corroborating systems and the
methodological rigour of the observation (controlled vs observational). D2 and
D4 are rated Medium because the evidence comes primarily from observational
case studies rather than controlled ablations. All five discoveries are
considered actionable by the research team at the current confidence level.

The agent fleet patterns described here are consistent with the "team topology"
framing outlined in `docs/guides/workflows.md` and the Endogenic-First axiom
in `MANIFESTO.md`. The capability-separation principle (D1) maps directly to
the "stream-aligned team" concept in Team Topologies. The tool-minimalism
principle (D5) maps to the "minimal posture" operational constraint in AGENTS.md.
This synthesis is considered actionable at current confidence levels.
"""


@pytest.fixture
def monkeypatch_env(monkeypatch):
    """
    Convenience fixture for setting environment variables in tests.

    Usage:
        def test_something(monkeypatch_env):
            monkeypatch_env("MY_VAR", "value")
    """

    def set_env(key: str, value: str):
        monkeypatch.setenv(key, value)

    return set_env

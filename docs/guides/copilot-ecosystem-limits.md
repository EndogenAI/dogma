---
title: Copilot Ecosystem Limitations
status: Active
---

# Copilot Ecosystem Limitations

## What Copilot Can't Do

### 1. Single-Turn Context Window Ceiling
Claude Code operates within token budgets per turn (≈120K tokens). Complex projects exceed this. Copilot cannot automatically fetch multi-file context or rank files by relevance — you must manage context explicitly or trigger manual context gathering via tool invocations.

### 2. Reasoning Depth Plateau
Copilot reasoning (o1 model extension) has diminishing returns beyond 3–4 inter-dependent steps within a single turn. Multi-phase reasoning across multiple turns requires explicit handoff and state preservation.

### 3. No Native Tool Discovery
Copilot sees only the tools you expose to it (via extension APIs or MCP). It cannot discover available commands, scripts, or external tools unless they are surfaced as semantic interfaces (MCP resources, agent SKILLS, or hardcoded prompts).

### 4. Lateral Context Dependency Gaps
When Copilot delegates to a subagent, it cannot automatically pass full session context to the delegate. The parent must explicitly stage context (via scratchpad, session memory, or handoff prompts).

## Workflow Strategies

### Phase-Based Context Bundling
Break work into phases; each phase has explicit context inputs written to the scratchpad before delegation. Copilot reads `.tmp/<branch>/YYYY-MM-DD.md` at phase boundaries to recover context from prior phases.

### Tool Staging for Relevance
Before asking Copilot to read a large file, use `file_search` with specific patterns (e.g., `scripts/*.py`) to surface only relevant files. Explicit staging reduces token waste on irrelevant context.

---

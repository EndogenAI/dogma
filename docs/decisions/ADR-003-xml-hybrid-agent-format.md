# ADR-003: XML-Hybrid Format for Agent Instruction Files

**Date**: 2026-03-07
**Status**: Proposed
**Deciders**: EndogenAI core team

---

## Context

`.agent.md` files currently use Markdown headings (`## Workflow`, `## Guardrails`) to structure agent instruction bodies. Research from [`docs/research/xml-agent-instruction-format.md`](../research/xml-agent-instruction-format.md) found that:

- Anthropic's production cookbook agents use XML-tagged section boundaries (`<research_process>`, `<delegation_instructions>`) rather than Markdown headings
- XML tags are machine-unambiguous and appear in Claude's training data as instruction delimiters
- Migration requires a script (`scripts/migrate_agent_xml.py` exists) and fleet-wide consistency

## Decision

**Proposed: Adopt XML-hybrid format** — XML tags for section delimiters within the instruction body, YAML frontmatter preserved as-is. The hybrid approach retains human readability while improving instruction-following fidelity.

**This decision is Proposed, not Accepted** pending:
- OQ-12-1: Confirmation that the VS Code LM API layer passes XML through unmodified
- OQ-12-2: Empirical ablation test (XML vs. Markdown instruction-following fidelity)
- OQ-12-3: Degradation behavior on non-Claude models

## Consequences if Accepted

- All 15+ agent files must be migrated via `scripts/migrate_agent_xml.py`
- `scaffold_agent.py` updated to emit XML-format stubs
- `docs/guides/agents.md` and `.github/agents/AGENTS.md` updated with XML format documentation
- Validation script added to CI

## References

- [`docs/research/xml-agent-instruction-format.md`](../research/xml-agent-instruction-format.md)
- `scripts/migrate_agent_xml.py`
- Issue #12 Follow-Up Open Questions in `docs/research/OPEN_RESEARCH.md`

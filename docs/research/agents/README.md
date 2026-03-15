# Research: Agent Fleet & Navigation

Research and synthesis documents covering agent identity, fleet design patterns, skill integration, agentic research flows, and memory architectures.

## Scope

- **Agent taxonomy & roles**: Character vs. Role definitions, fleet catalog, executive tiers
- **Fleet design patterns**: Orchestration, handoff topology, delegation gates
- **Skills integration**: SKILL.md authoring, decision logic, cross-agent procedures
- **Memory & navigation**: Episodic memory, dynamic navigation, context anchors
- **AFS / MCP integration**: Agent-facing systems, local MCP frameworks

## Key Documents

| File | Description |
|------|-------------|
| `agent-taxonomy.md` | Canonical Character vs. Role definitions; fleet tier model |
| `agent-fleet-design-patterns.md` | Orchestration and handoff design patterns |
| `agent-skills-integration.md` | SKILL.md authoring decisions; cross-agent skill reuse |
| `agentic-research-flows.md` | Research fleet pipeline (Scout → Synthesizer → Reviewer) |
| `dynamic-agent-navigation.md` | Low-token navigation strategies for agent context descent |
| `episodic-memory-agents.md` | Episodic memory architectures for long-running agents |
| `fleet-emergence-operationalization.md` | Fleet-level emergence patterns and coordination |
| `deterministic-agent-components.md` | Deterministic vs. probabilistic component classification |
| `skills-as-decision-logic.md` | Skills as decision gates; when to use SKILL.md vs. agent body |
| `aigne-afs-evaluation.md` | AFS evaluation framework for agent capability gates |
| `context-amplification-calibration.md` | Context budget tuning per agent tier |
| `context-budget-balance.md` | Context window budget management patterns |
| `local-mcp-frameworks.md` | Local MCP topology and deployment patterns |

## Agent Search Tips

```
grep_search "taxonomy|fleet|handoff" --includePattern "docs/research/agents/**"
```

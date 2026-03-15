# Research: LLM Models & Inference

Research and synthesis documents covering LLM model selection, local inference, tiering strategies, and behavioral testing.

## Scope

- **Model selection**: Capability × cost × latency tiering
- **Local inference**: Ollama, LM Studio, llama.cpp deployment patterns
- **Behavioral testing**: LLM behavioral testing frameworks and quality metrics
- **Local Compute-First integration**: Local inference as a structural LCF enabler

## Key Documents

| File | Description |
|------|-------------|
| `llm-tier-strategy.md` | Model tier decision table: capability × cost × latency |
| `local-copilot-models.md` | Local Copilot model deployment and VS Code integration |
| `llm-behavioral-testing.md` | LLM behavioral testing frameworks and evaluation patterns |

## Agent Search Tips

```
grep_search "Ollama|LM Studio|local.*model" --includePattern "docs/research/models/**"
grep_search "tier|latency|cost.*model" --includePattern "docs/research/models/**"
```

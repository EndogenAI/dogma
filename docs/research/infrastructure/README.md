# Research: Infrastructure & Engineering

Research and synthesis documents covering security, async process handling, scripting patterns, substrate mechanics, CI, and programmatic enforcement governors.

## Scope

- **Security**: SSRF, prompt injection, secrets hygiene, threat modelling
- **Async & process handling**: Terminal timeout patterns, polling, service readiness
- **Scripting & automation**: Script generation, documentation automation, pre-commit hooks
- **Substrate mechanics**: Scratchpad architecture, queryable substrate, consolidation
- **CI / GitHub Actions**: Issue/metrics actions, Copilot PR automation
- **LCF enforcement**: Programmatic governors, oversight infrastructure

## Key Documents

| File | Description |
|------|-------------|
| `security-threat-model.md` | SSRF, prompt injection, and secrets hygiene threat model |
| `async-process-handling.md` | Terminal timeout patterns, polling algorithms, service readiness |
| `programmatic-governors.md` | T3/T4 governor design: pre-commit hooks, shell preexec |
| `shell-preexec-governor.md` | Shell preexec governor implementation and adoption (ADR-007) |
| `lcf-programmatic-enforcement.md` | Local Compute-First programmatic enforcement patterns |
| `lcf-oversight-infrastructure.md` | LCF oversight infrastructure: monitoring, alerting, guarding |
| `scratchpad-architecture-maturation.md` | Scratchpad architecture evolution and segmentation |
| `queryable-substrate.md` | Queryable substrate design for agent context retrieval |
| `github-as-memory-substrate.md` | GitHub Issues/PRs as persistent agent memory substrate |
| `substrate-consolidation-2026-03-13.md` | Substrate consolidation sprint retrospective |
| `substrate-rebalancing-2026-03-13.md` | Substrate rebalancing and normalization decisions |
| `session-checkpoint-and-safeguard-patterns.md` | Session checkpoint patterns and safeguards |
| `dev-workflow-automations.md` | Developer workflow automations and pre-commit patterns |
| `testing-tools-and-frameworks.md` | Testing tools, frameworks, and pytest conventions |
| `scripts-documentation-generation.md` | Script-level documentation generation patterns |
| `action-item-extraction.md` | Action item extraction from research documents |
| `issue-metrics-action.md` | GitHub Actions: issue metrics collection workflow |
| `issue-to-markdown-action.md` | GitHub Actions: issue-to-Markdown export workflow |
| `copilot-pr-review-automation.md` | Copilot PR review automation patterns |
| `local-mcp-frameworks.md` | Local MCP framework topologies (see also: agents/) |
| `doc-interweb.md` | Documentation interweb / weave-links architecture |

## Agent Search Tips

```
grep_search "SSRF|injection|security" --includePattern "docs/research/infrastructure/**"
grep_search "timeout|poll|async" --includePattern "docs/research/infrastructure/**"
grep_search "pre-commit|T3|T4|governor" --includePattern "docs/research/infrastructure/**"
```

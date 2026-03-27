# `scaffold\_agent`

scripts/scaffold_agent.py

Scaffold a new VS Code Copilot .agent.md file from a minimal template.

Purpose:
    Generate a well-formed .agent.md stub in .github/agents/ with correct
    frontmatter, body structure, and placeholder sections ready to be filled in.
    Enforces the naming conventions and frontmatter schema defined in
    .github/agents/AGENTS.md.

Inputs:
    --name         Display name for the agent, e.g. "Research Foo"  (required)
    --description  One-line summary ≤ 200 characters               (required)
    --posture      readonly | creator | full                        (default: creator)
    --area         Area prefix for fleet sub-agents, e.g. "research"
                   If omitted, the agent is treated as a standalone workflow agent.
    --dry-run      Print the generated file without writing it

Outputs:
    .github/agents/<slugified-name>.agent.md

Usage examples:
    uv run python scripts/scaffold_agent.py         --name "Research Foo"         --description "Surveys sources on foo topics and catalogues findings."         --posture creator         --area research

    uv run python scripts/scaffold_agent.py         --name "Research Foo"         --description "Surveys sources on foo topics and catalogues findings."         --dry-run

Exit codes:
    0  Success
    1  Validation error (name conflict, description too long, missing required arg)

## Usage

```bash
    uv run python scripts/scaffold_agent.py         --name "Research Foo"         --description "Surveys sources on foo topics and catalogues findings."         --posture creator         --area research

    uv run python scripts/scaffold_agent.py         --name "Research Foo"         --description "Surveys sources on foo topics and catalogues findings."         --dry-run
```

<!-- hash:42ca53304de186e6 -->

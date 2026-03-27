# `validate\_agent\_files`

scripts/validate_agent_files.py

Programmatic encoding-fidelity gate for agent files — equivalent to
validate_synthesis.py but for `.agent.md` files in `.github/agents/`.

Purpose:
    Enforce a minimum structural bar on agent files to prevent encoding drift
    in the MANIFESTO → AGENTS.md → agent files → session prompts chain.

Checks:
    1. Valid YAML frontmatter with required fields: ``name``, ``description``.
    2. Required section headings present (fuzzy keyword matching):
       - Beliefs & Context section (confirms the agent reads before acting)
       - Workflow & Intentions section (Workflow, Checklist, Conventions, or equivalent)
    - Desired Outcomes & Acceptance section (Desired Outcomes, Acceptance, or Completion Criteria)
    3. At least one back-reference to MANIFESTO.md or AGENTS.md (cross-reference
       density ≥ 1).  Low density signals likely encoding drift.
    4. No heredoc-based file writes (``cat >> ... << 'EOF'`` patterns), which
       silently corrupt Markdown content containing backticks.
    5. No ``Fetch-before-check`` guardrail label (correct label is
       ``Check-before-fetch`` — check cache first, then fetch only if absent).
    6. No ``## Phase N Review Output`` heading (use ``## Review Output``
       as defined in ``review.agent.md``).
    7. Core Layer Impermeability: if ``client-values.yml`` is cited in Beliefs & Context,
       it must not appear before or instead of ``MANIFESTO.md`` or ``AGENTS.md``
       (Deployment Layer values are subordinate to Core Layer axioms).

Inputs:
    [file ...]    One or more .agent.md files to validate.  (positional, optional)
    --all         Scan every *.agent.md in .github/agents/ AND every SKILL.md
                  in .github/skills/*/SKILL.md.
    --skills      Scan every SKILL.md in .github/skills/*/SKILL.md.
    --strict      Reserved for future use — currently a no-op flag.

Outputs:
    stdout:  Human-readable pass/fail summary with specific gap list per file.
    stderr:  Nothing (all output goes to stdout for easy capture).

Exit codes:
    0  All checks passed.
    1  One or more checks failed — specific gap(s) reported to stdout.

Usage examples:
    # Validate a single agent file
    uv run python scripts/validate_agent_files.py .github/agents/executive-orchestrator.agent.md

    # Validate all agent files in .github/agents/
    uv run python scripts/validate_agent_files.py --all

    # Validate all SKILL.md files in .github/skills/
    uv run python scripts/validate_agent_files.py --skills

    # Integrate into CI (non-zero exit blocks the job)
    for f in .github/agents/*.agent.md; do
        uv run python scripts/validate_agent_files.py "$f"
    done

## Usage

```bash
    # Validate a single agent file
    uv run python scripts/validate_agent_files.py .github/agents/executive-orchestrator.agent.md

    # Validate all agent files in .github/agents/
    uv run python scripts/validate_agent_files.py --all

    # Validate all SKILL.md files in .github/skills/
    uv run python scripts/validate_agent_files.py --skills

    # Integrate into CI (non-zero exit blocks the job)
    for f in .github/agents/*.agent.md; do
        uv run python scripts/validate_agent_files.py "$f"
    done
```

<!-- hash:a5a5c885e387c651 -->

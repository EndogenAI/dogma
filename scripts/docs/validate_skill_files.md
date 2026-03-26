# `validate\_skill\_files`

scripts/validate_skill_files.py

Programmatic encoding-fidelity gate for skill files — equivalent to
validate_agent_files.py but for `.github/skills/*/SKILL.md` files.

Purpose:
    Enforce a minimum structural bar on skill files to prevent encoding drift
    in the MANIFESTO → AGENTS.md → skill files → session procedures chain.

Checks (5-point gate):
    1. Valid YAML frontmatter with required fields: ``name``, ``description``.
    2. Required section headings present (fuzzy keyword matching):
       - Governing Axiom section (documents which axiom/principle governs the skill)
       - Workflow section (Workflow, Procedure, Steps, or equivalent)
       - Output section (documents what the skill produces)
    3. At least one back-reference to MANIFESTO.md or AGENTS.md (cross-reference
       density ≥ 1). Low density signals likely encoding drift.
    4. No heredoc-based file writes (``cat >> ... << 'EOF'`` patterns), which
       silently corrupt Markdown content containing backticks.
    5. Inverse scope checks: file explicitly states what the skill does NOT
       handle (negation statements for scope boundaries). Typically uses "DO NOT",
       "AVOID", "NOT FOR" patterns in the frontmatter description or a dedicated section.

Inputs:
    [file ...]    One or more .md files to validate (positional, optional).
    --all         Scan every SKILL.md in .github/skills/*/SKILL.md.
    --check       If provided, exit cleanly with exit code 0 even if checks fail.
                  Useful for pre-flight validation without blocking. Default: fail on errors.

Outputs:
    stdout:  Human-readable pass/fail summary with specific gap list per file.

Exit codes:
    0  All checks passed.
    1  One or more checks failed — specific gap(s) reported to stdout.

Usage examples:
    # Validate a single skill file
    uv run python scripts/validate_skill_files.py .github/skills/delegation-routing/SKILL.md

    # Validate all skill files
    uv run python scripts/validate_skill_files.py --all

    # Check-only mode (do not block CI)
    uv run python scripts/validate_skill_files.py --check --all

## Usage

```bash
    # Validate a single skill file
    uv run python scripts/validate_skill_files.py .github/skills/delegation-routing/SKILL.md

    # Validate all skill files
    uv run python scripts/validate_skill_files.py --all

    # Check-only mode (do not block CI)
    uv run python scripts/validate_skill_files.py --check --all
```

<!-- hash:155250bd5e7ff5b5 -->

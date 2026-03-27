# `adopt\_wizard`

scripts/adopt_wizard.py

Dogma framework onboarding wizard for new adopting organisations.

Purpose:
    Automates Steps 2–5 from docs/guides/adoption-playbook.md. Prompts for
    organisation mission, priorities, and constraints; generates client-values.yml
    and scaffolds AGENTS.md with a Deployment Layer integration note; then runs
    validate_agent_files.py to confirm the setup is valid.

Inputs:
    --org TEXT             Organisation name (required)
    --repo TEXT            Repository name (required)
    --non-interactive      Skip interactive prompts; use built-in defaults
    --load-values PATH     Load an existing client-values.yml as prompt defaults
    --output-dir PATH      Directory to write files into (default: current directory)

Outputs:
    <output-dir>/client-values.yml   Deployment Layer values for the adopter
    <output-dir>/AGENTS.md           Root constraint file with Deployment Layer note

Usage:
    uv run python scripts/adopt_wizard.py --org AccessiTech --repo platform
    uv run python scripts/adopt_wizard.py --org MyOrg --repo myrepo --non-interactive
    uv run python scripts/adopt_wizard.py --org MyOrg --repo myrepo \
        --load-values existing-client-values.yml

Exit codes:
    0   Adoption complete and validation passed
    1   Missing required flags, validation failed, or I/O error

## Usage

```bash
    uv run python scripts/adopt_wizard.py --org AccessiTech --repo platform
    uv run python scripts/adopt_wizard.py --org MyOrg --repo myrepo --non-interactive
    uv run python scripts/adopt_wizard.py --org MyOrg --repo myrepo \
        --load-values existing-client-values.yml
```

<!-- hash:62e2e3c340ad15fb -->

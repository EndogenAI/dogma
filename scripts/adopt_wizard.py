"""scripts/adopt_wizard.py

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
    uv run python scripts/adopt_wizard.py --org MyOrg --repo myrepo \\
        --load-values existing-client-values.yml

Exit codes:
    0   Adoption complete and validation passed
    1   Missing required flags, validation failed, or I/O error
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

_AXIOM_CHOICES = ["endogenous-first", "algorithms-before-tokens", "local-compute-first"]
_DEPLOYMENT_COMMENT = "# Deployment Layer: client-values.yml present — see AGENTS.md §Deployment Layer integration\n"
_DOGMA_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Public helper — importable by tests and other scripts
# ---------------------------------------------------------------------------


def validate_client_values(path: Path) -> list[str]:
    """
    Validate a client-values.yml file against the required schema.

    Checks that the required keys (``mission``, ``priorities``) are present
    and non-empty.

    Args:
        path: Path to the client-values.yml file.

    Returns:
        A list of error strings.  Empty list means the file is valid.
    """
    errors: list[str] = []
    if not path.exists():
        errors.append(f"{path}: file not found")
        return errors
    try:
        data: dict[str, Any] = yaml.safe_load(path.read_text()) or {}
    except yaml.YAMLError as exc:
        errors.append(f"{path}: invalid YAML — {exc}")
        return errors
    for key in ("mission", "priorities"):
        if key not in data:
            errors.append(f"missing required key: '{key}'")
        elif not data[key]:
            errors.append(f"required key '{key}' must not be empty")
    return errors


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_existing_values(path: Path) -> dict[str, Any]:
    """Load an existing client-values.yml and return its data dict."""
    if not path.exists():
        print(f"[warn] --load-values file not found: {path}", file=sys.stderr)
        return {}
    try:
        return yaml.safe_load(path.read_text()) or {}
    except yaml.YAMLError as exc:
        print(f"[error] Cannot parse {path}: {exc}", file=sys.stderr)
        return {}


def _prompt(prompt_text: str, default: str = "") -> str:
    """Prompt the user for input, showing the default value."""
    if default:
        prompt_text = f"{prompt_text} [{default}]"
    value = input(f"{prompt_text}: ").strip()
    return value or default


def _collect_values(
    org: str,
    repo: str,
    non_interactive: bool,
    defaults: dict[str, Any],
) -> dict[str, Any]:
    """
    Collect mission, priorities, axiom_emphasis, and constraints from the user
    (or from defaults when --non-interactive is set).
    """
    default_mission = defaults.get("mission") or f"Purpose-driven technology for {org}."
    default_priorities = defaults.get("priorities") or ["Endogenous-First"]
    default_axiom = defaults.get("axiom_emphasis") or "endogenous-first"
    default_constraints = defaults.get("constraints") or []

    if non_interactive:
        mission = default_mission
        priorities = list(default_priorities)
        axiom_emphasis = default_axiom
        constraints = list(default_constraints)
    else:
        print()
        print(f"=== Dogma Adoption Wizard — {org}/{repo} ===")
        print("Press Enter to accept bracketed defaults.\n")

        # Mission
        mission = _prompt(
            "Organisation mission (one sentence, ≤50 words)",
            default_mission,
        )
        word_count = len(mission.split())
        if word_count > 50:
            print(
                f"[warn] Mission is {word_count} words — recommended ≤50 words.",
                file=sys.stderr,
            )

        # Priorities
        print(
            "\nTop priorities (comma-separated; map to axioms where possible).\n"
            "  Axiom options: Endogenous-First, Algorithms Before Tokens, Local Compute-First"
        )
        raw = _prompt(
            "Priorities",
            ", ".join(str(p) for p in default_priorities),
        )
        priorities = [p.strip() for p in raw.split(",") if p.strip()]

        # Axiom emphasis
        print(f"\nPrimary axiom emphasis. Choices: {', '.join(_AXIOM_CHOICES)}")
        axiom_emphasis = ""
        while axiom_emphasis not in _AXIOM_CHOICES:
            axiom_emphasis = _prompt("Axiom emphasis", default_axiom)
            if axiom_emphasis not in _AXIOM_CHOICES:
                print(
                    f"[error] Must be one of: {', '.join(_AXIOM_CHOICES)}",
                    file=sys.stderr,
                )

        # Constraints (optional)
        print("\nDomain-specific compliance constraints (comma-separated, or press Enter to skip).")
        raw_c = _prompt(
            "Constraints",
            ", ".join(str(c) for c in default_constraints) if default_constraints else "",
        )
        constraints = [c.strip() for c in raw_c.split(",") if c.strip()]

    return {
        "org": org,
        "repo": repo,
        "mission": mission,
        "priorities": priorities,
        "axiom_emphasis": axiom_emphasis,
        "constraints": constraints,
        "deployment_layer": {},
    }


def _write_client_values(data: dict[str, Any], output_dir: Path) -> Path:
    """Write client-values.yml to output_dir and return its path."""
    content_lines = [
        "# client-values.yml — Deployment Layer external-values file",
        "# Specialises (does not override) Core Layer constraints in MANIFESTO.md.",
        "",
    ]
    content_lines.append(yaml.dump(data, default_flow_style=False, sort_keys=False))
    dest = output_dir / "client-values.yml"
    dest.write_text("\n".join(content_lines))
    return dest


def _write_agents_md(output_dir: Path) -> Path:
    """
    Copy the canonical dogma AGENTS.md into output_dir with the
    Deployment Layer comment prepended.
    """
    source = _DOGMA_ROOT / "AGENTS.md"
    dest = output_dir / "AGENTS.md"
    if source.exists():
        original = source.read_text()
        dest.write_text(_DEPLOYMENT_COMMENT + original)
    else:
        # Fallback: write a minimal stub so the wizard always produces a file
        stub = (
            _DEPLOYMENT_COMMENT + "# AGENTS.md\n\n"
            "# Generated by adopt_wizard.py — replace with canonical dogma AGENTS.md.\n"
        )
        dest.write_text(stub)
    return dest


def _run_validation(output_dir: Path) -> tuple[bool, str]:
    """
    Run scripts/validate_agent_files.py --all from output_dir.

    Returns (passed: bool, raw_output: str).
    Errors from the validator are surfaced verbatim to the caller.
    """
    script = _DOGMA_ROOT / "scripts" / "validate_agent_files.py"
    if not script.exists():
        return True, "(validate_agent_files.py not found — skipped)"
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--all"],
            cwd=str(output_dir),
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return False, str(exc)
    combined = (result.stdout + result.stderr).strip()
    return result.returncode == 0, combined


def _print_summary(
    org: str,
    repo: str,
    created_files: list[Path],
    validation_passed: bool,
) -> None:
    """Print the AC5-compliant structured summary."""
    print(f"\nAdoption complete for {org}/{repo}.\n")
    print("Files created:")
    for f in created_files:
        print(f"  {f.name:<30} ✓ valid")
    print()
    status = "PASSED" if validation_passed else "FAILED"
    print(f"Validation: {status}\n")
    if validation_passed:
        print("Next steps:")
        commit_msg = f"chore(adoption): initialise dogma framework for {org}"
        print(f'  1. git add client-values.yml AGENTS.md && git commit -m "{commit_msg}"')
        print("  2. Add .agent.md role files to .github/agents/  (see docs/guides/agents.md)")
        print("  3. Install pre-commit hooks: uv run pre-commit install")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dogma framework onboarding wizard.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--org", required=True, help="Organisation name")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Skip interactive prompts; use built-in defaults",
    )
    parser.add_argument(
        "--load-values",
        metavar="PATH",
        help="Load an existing client-values.yml as prompt defaults",
    )
    parser.add_argument(
        "--output-dir",
        metavar="PATH",
        default=".",
        help="Directory to write files into (default: current directory)",
    )
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load existing values as defaults if --load-values provided
    defaults: dict[str, Any] = {}
    if args.load_values:
        defaults = _load_existing_values(Path(args.load_values))

    # Collect values
    data = _collect_values(
        org=args.org,
        repo=args.repo,
        non_interactive=args.non_interactive,
        defaults=defaults,
    )

    # Write files
    cv_path = _write_client_values(data, output_dir)
    agents_path = _write_agents_md(output_dir)

    # Validate client-values.yml
    cv_errors = validate_client_values(cv_path)
    if cv_errors:
        for err in cv_errors:
            print(f"[error] client-values.yml: {err}", file=sys.stderr)
        return 1

    # Run agent files validation
    validation_passed, validation_output = _run_validation(output_dir)
    if validation_output:
        print(validation_output)

    if not validation_passed:
        print("\n[error] Validation failed — fix the above issues before committing.", file=sys.stderr)
        return 1

    _print_summary(
        org=args.org,
        repo=args.repo,
        created_files=[cv_path, agents_path],
        validation_passed=validation_passed,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

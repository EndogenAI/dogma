"""
post_gen_project.py — Cookiecutter post-generation hook for dogma-based repos.

Purpose:
    Runs after cookiecutter renders the template into the new project directory.
    Initializes a git repo and prints next-steps guidance.

Inputs:
    None — cookiecutter invokes this automatically after rendering.

Outputs:
    - A git repository initialized in the new project directory (cwd at hook time).
    - Next-steps instructions printed to stdout.

Usage example:
    Invoked automatically by cookiecutter. Not intended for direct execution.

Exit codes:
    0 — success
    1 — git init failed
"""

import subprocess
import sys


def main() -> None:
    print(
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "  Dogma template scaffolded — next steps\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "\n"
        "  1. Review and complete client-values.yml (Deployment Layer)\n"
        "  2. Follow the full initialization guide:\n"
        "     https://github.com/EndogenAI/dogma/blob/main/docs/guides/product-fork-initialization.md\n"
        "  3. Install dependencies and pre-commit hooks:\n"
        "     uv sync && uv run pre-commit install\n"
        "  4. Run the adoption wizard for a fully guided setup:\n"
        "     uvx --from endogenai-workflows adopt_wizard --org <YourOrg> --repo <your-repo>\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )

    result = subprocess.run(["git", "init"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: git init failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    print("✓ Dogma template scaffolded. Run: uv sync && uv run pre-commit install")


if __name__ == "__main__":
    main()

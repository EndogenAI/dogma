"""scripts/check_branch_counter.py — Pre-push gate: warn if BRANCH_COUNTER != 0.

Reads mcp_server/_version.py via AST (no import side-effects) and exits with
status 1 if BRANCH_COUNTER is non-zero, indicating the branch-specific counter
was not reset before pushing.

Usage (direct):
    python3 scripts/check_branch_counter.py

Used by pre-commit hook `check-branch-counter` (stage: pre-push).

Exit codes:
    0 — BRANCH_COUNTER == 0 (safe to merge)
    1 — BRANCH_COUNTER != 0 (reset before merging to main)
    2 — _version.py not found or parse error
"""

import ast
import pathlib
import sys


def main() -> int:
    version_path = pathlib.Path("mcp_server/_version.py")
    if not version_path.exists():
        print(f"check_branch_counter: {version_path} not found — skipping check.", file=sys.stderr)
        return 0

    try:
        tree = ast.parse(version_path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        print(f"check_branch_counter: parse error in {version_path}: {exc}", file=sys.stderr)
        return 2

    branch_counter: int | None = None
    for node in ast.walk(tree):
        # Handle both plain assignment (x = 0) and annotated assignment (x: int = 0)
        if isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.target.id == "BRANCH_COUNTER"
                and node.value is not None
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, int)
            ):
                branch_counter = node.value.value
                break
        elif isinstance(node, ast.Assign):
            if (
                len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "BRANCH_COUNTER"
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, int)
            ):
                branch_counter = node.value.value
                break

    if branch_counter is None:
        print(
            "check_branch_counter: BRANCH_COUNTER not found in mcp_server/_version.py",
            file=sys.stderr,
        )
        return 2

    if branch_counter != 0:
        print(
            f"check_branch_counter: BRANCH_COUNTER={branch_counter} — reset to 0 before merging to main.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
test_cookiecutter_template.py — Tests for the dogma cookiecutter template.

Validates template structure, file existence, and content without executing cookiecutter.
"""

import ast
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
TEMPLATE_ROOT = REPO_ROOT / "{{cookiecutter.project_slug}}"
HOOKS_DIR = REPO_ROOT / "hooks"
COOKIECUTTER_JSON = REPO_ROOT / "cookiecutter.json"

REQUIRED_TEMPLATE_FILES = [
    "AGENTS.md",
    "client-values.yml",
    "pyproject.toml",
    "README.md",
    ".github/workflows/ci.yml",
    ".pre-commit-config.yaml",
]

REQUIRED_COOKIECUTTER_KEYS = [
    "project_name",
    "project_slug",
    "python_version",
    "domain",
    "ci",
]


def test_cookiecutter_json_is_valid_and_contains_required_keys():
    """cookiecutter.json must be valid JSON and contain all required keys."""
    assert COOKIECUTTER_JSON.exists(), "cookiecutter.json not found at repo root"
    content = COOKIECUTTER_JSON.read_text(encoding="utf-8")
    data = json.loads(content)  # raises json.JSONDecodeError if invalid
    for key in REQUIRED_COOKIECUTTER_KEYS:
        assert key in data, f"cookiecutter.json missing required key: {key!r}"


def test_all_template_files_exist():
    """Every expected file must exist under {{cookiecutter.project_slug}}/."""
    assert TEMPLATE_ROOT.is_dir(), f"Template directory not found: {TEMPLATE_ROOT}"
    for rel_path in REQUIRED_TEMPLATE_FILES:
        full_path = TEMPLATE_ROOT / rel_path
        assert full_path.exists(), f"Missing template file: {{cookiecutter.project_slug}}/{rel_path}"


def test_post_gen_hook_is_valid_python():
    """hooks/post_gen_project.py must be parseable as valid Python."""
    hook = HOOKS_DIR / "post_gen_project.py"
    assert hook.exists(), "hooks/post_gen_project.py not found"
    source = hook.read_text(encoding="utf-8")
    # ast.parse raises SyntaxError on invalid Python
    ast.parse(source)


def test_client_values_yml_contains_project_name_placeholder():
    """client-values.yml must reference the cookiecutter project_name variable."""
    client_values = TEMPLATE_ROOT / "client-values.yml"
    assert client_values.exists(), "client-values.yml not found in template dir"
    content = client_values.read_text(encoding="utf-8")
    # Must contain the cookiecutter variable reference for project_name
    assert re.search(
        r"cookiecutter\.project_name|project_name.*cookiecutter",
        content,
    ), "client-values.yml does not reference {{ cookiecutter.project_name }}"

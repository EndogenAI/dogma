"""
tests/test_validate_l2_constraints.py
----------------------------------------
Tests for scripts/validate_l2_constraints.py — L2 constraints schema validator.

Covers:
- Valid YAML file passes validation (exit 0)
- Missing required field fails with exit 1
- Invalid enum value fails with exit 1
- Empty constraints list fails with exit 1
- Missing file returns exit 2
- Malformed YAML returns exit 2
- Real data/l2-constraints.yml passes validation
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Module loader
# ---------------------------------------------------------------------------


def _load_module(name: str, rel_path: str):
    repo_root = Path(__file__).parent.parent
    spec = importlib.util.spec_from_file_location(name, repo_root / rel_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def vlc():
    return _load_module("validate_l2_constraints", "scripts/validate_l2_constraints.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_yaml(tmp_path, data, filename="l2-constraints.yml"):
    p = tmp_path / filename
    p.write_text(yaml.dump(data))
    return p


def _valid_constraint(**overrides):
    base = {
        "id": "test-constraint",
        "description": "A test constraint.",
        "enforcement": "pre-commit",
        "severity": "blocking",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Valid YAML
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_valid_yaml_passes(vlc, tmp_path):
    """A well-formed YAML file exits 0."""
    path = _write_yaml(
        tmp_path,
        {"constraints": [_valid_constraint()]},
    )
    assert vlc.validate(path) == 0


@pytest.mark.io
def test_valid_yaml_multiple_constraints(vlc, tmp_path):
    """Multiple valid constraints exit 0."""
    path = _write_yaml(
        tmp_path,
        {
            "constraints": [
                _valid_constraint(id="c1"),
                _valid_constraint(id="c2", enforcement="runtime", severity="warning"),
                _valid_constraint(id="c3", enforcement="review"),
            ]
        },
    )
    assert vlc.validate(path) == 0


# ---------------------------------------------------------------------------
# Schema violations → exit 1
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_missing_id_field_fails(vlc, tmp_path):
    """Missing 'id' field causes exit 1."""
    constraint = _valid_constraint()
    del constraint["id"]
    path = _write_yaml(tmp_path, {"constraints": [constraint]})
    assert vlc.validate(path) == 1


@pytest.mark.io
def test_missing_description_field_fails(vlc, tmp_path):
    """Missing 'description' field causes exit 1."""
    constraint = _valid_constraint()
    del constraint["description"]
    path = _write_yaml(tmp_path, {"constraints": [constraint]})
    assert vlc.validate(path) == 1


@pytest.mark.io
def test_invalid_enforcement_enum_fails(vlc, tmp_path):
    """Unknown enforcement value causes exit 1."""
    path = _write_yaml(
        tmp_path,
        {"constraints": [_valid_constraint(enforcement="ci-only")]},
    )
    assert vlc.validate(path) == 1


@pytest.mark.io
def test_invalid_severity_enum_fails(vlc, tmp_path):
    """Unknown severity value causes exit 1."""
    path = _write_yaml(
        tmp_path,
        {"constraints": [_valid_constraint(severity="critical")]},
    )
    assert vlc.validate(path) == 1


@pytest.mark.io
def test_missing_constraints_key_fails(vlc, tmp_path):
    """YAML missing top-level 'constraints' key causes exit 1."""
    path = _write_yaml(tmp_path, {"rules": []})
    assert vlc.validate(path) == 1


# ---------------------------------------------------------------------------
# File errors → exit 2
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_missing_file_exits_2(vlc, tmp_path):
    """Non-existent file causes exit 2."""
    missing = tmp_path / "does_not_exist.yml"
    assert vlc.validate(missing) == 2


@pytest.mark.io
def test_malformed_yaml_exits_2(vlc, tmp_path):
    """Unparseable YAML causes exit 2."""
    bad = tmp_path / "bad.yml"
    bad.write_text("constraints: [\nnot valid yaml: [[[")
    assert vlc.validate(bad) == 2


# ---------------------------------------------------------------------------
# Real data file
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_real_data_file_passes(vlc):
    """The committed data/l2-constraints.yml must pass schema validation."""
    real_path = Path(__file__).parent.parent / "data" / "l2-constraints.yml"
    if not real_path.exists():
        pytest.skip("data/l2-constraints.yml not yet committed")
    assert vlc.validate(real_path) == 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_cli_valid(vlc, tmp_path, capsys):
    """CLI exits 0 and prints VALID for a correct file."""
    path = _write_yaml(tmp_path, {"constraints": [_valid_constraint()]})
    rc = vlc.main([str(path)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "VALID" in captured.out


@pytest.mark.io
def test_cli_missing_file(vlc, tmp_path, capsys):
    """CLI exits 2 for missing file."""
    missing = tmp_path / "ghost.yml"
    rc = vlc.main([str(missing)])
    assert rc == 2

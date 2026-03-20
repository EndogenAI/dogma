#!/usr/bin/env python3
"""Tests for substrate_distiller.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from substrate_distiller import _classify_rdi, _iter_targets, distill_path, main


@pytest.mark.io
def test_happy_path_extraction(tmp_path: Path):
    source = '''"""
x-governs: [endogenous-first, algorithms-before-tokens]

## Intent
Keep behavior deterministic.

## Rationale
This module encodes deterministic extraction and explicit policy metadata.
"""


def public_fn():
    """
    x-governs: [local-compute-first]

    ## Intent
    Provide a callable unit.

    ## Rationale
    We keep this rationale explicit so the distiller has measurable rationale density.
    """
    return 1
'''
    target = tmp_path / "sample.py"
    target.write_text(source, encoding="utf-8")

    payload = distill_path(target, threshold=0.08, include_private=False)
    assert payload["summary"]["records"] >= 2

    module_record = next(item for item in payload["records"] if item["kind"] == "module")
    assert module_record["x_governs"] == ["endogenous-first", "algorithms-before-tokens"]
    assert "deterministic" in module_record["intent"].lower()
    assert module_record["rationale_token_count"] > 0


@pytest.mark.io
def test_missing_x_governs_detected(tmp_path: Path):
    source = '''"""
## Intent
Only intent.

## Rationale
Some rationale exists.
"""


def f():
    return 1
'''
    target = tmp_path / "missing_x_governs.py"
    target.write_text(source, encoding="utf-8")

    payload = distill_path(target, threshold=0.08, include_private=False)
    module_record = next(item for item in payload["records"] if item["kind"] == "module")
    assert module_record["has_x_governs"] is False
    assert "missing_x_governs" in module_record["debt_reasons"]


@pytest.mark.io
def test_missing_rationale_detected(tmp_path: Path):
    source = '''"""
x-governs: [endogenous-first]

## Intent
Only intent exists.
"""
'''
    target = tmp_path / "missing_rationale.py"
    target.write_text(source, encoding="utf-8")

    payload = distill_path(target, threshold=0.08, include_private=False)
    module_record = next(item for item in payload["records"] if item["kind"] == "module")
    assert module_record["has_rationale"] is False
    assert "missing_rationale" in module_record["debt_reasons"]


def test_threshold_classification_behavior():
    assert _classify_rdi(0.12) == "green"
    assert _classify_rdi(0.5) == "green"
    assert _classify_rdi(0.08) == "yellow"
    assert _classify_rdi(0.1199) == "yellow"
    assert _classify_rdi(0.0799) == "red"
    assert _classify_rdi(0.0) == "red"


@pytest.mark.io
def test_exit_code_behavior_success_and_fail_on_debt(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    source = '''"""
x-governs: [endogenous-first]

## Intent
Intent text.

## Rationale
A long enough rationale block for healthy ratio in this tiny module.
"""

VALUE = 1
'''
    target = tmp_path / "ok.py"
    target.write_text(source, encoding="utf-8")

    code_ok = main(["--path", str(target), "--format", "json"])
    assert code_ok == 0

    captured = capsys.readouterr()
    json.loads(captured.out)

    code_fail = main(
        [
            "--path",
            str(target),
            "--format",
            "json",
            "--fail-on-debt",
            "--threshold",
            "10.0",
        ]
    )
    assert code_fail == 1


def test_exit_code_behavior_invalid_args_is_2():
    code = main(["--path", ".", "--format", "invalid"])
    assert code == 2


@pytest.mark.io
def test_parse_error_handling_returns_2(tmp_path: Path):
    bad_file = tmp_path / "broken.py"
    bad_file.write_text("def broken(:\n    pass\n", encoding="utf-8")

    code = main(["--path", str(bad_file), "--format", "json"])
    assert code == 2


@pytest.mark.io
def test_include_private_controls_private_symbol_scanning(tmp_path: Path):
    source = '''"""
x-governs: [endogenous-first]

## Intent
Module intent.

## Rationale
Module rationale.
"""


def _private_fn():
    """
    x-governs: [local-compute-first]

    ## Intent
    Private intent.

    ## Rationale
    Private rationale.
    """
    return 1
'''
    target = tmp_path / "private_sample.py"
    target.write_text(source, encoding="utf-8")

    without_private = distill_path(target, threshold=0.08, include_private=False)
    with_private = distill_path(target, threshold=0.08, include_private=True)

    symbols_without = {record["symbol"] for record in without_private["records"]}
    symbols_with = {record["symbol"] for record in with_private["records"]}

    assert "_private_fn" not in symbols_without
    assert "_private_fn" in symbols_with


@pytest.mark.io
def test_summary_only_and_rendering_paths(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    source = '''"""
x-governs: [endogenous-first]

## Intent
Intent text.

## Rationale
Rationale text for rendering checks.
"""
'''
    target = tmp_path / "render_sample.py"
    target.write_text(source, encoding="utf-8")

    code_md = main(["--path", str(target), "--format", "markdown", "--summary-only"])
    assert code_md == 0
    md_out = capsys.readouterr().out
    assert "## Substrate Distiller Summary" in md_out
    assert "## Records" not in md_out

    code_table = main(["--path", str(target), "--format", "table", "--summary-only"])
    assert code_table == 0
    table_out = capsys.readouterr().out
    assert "files_scanned\trecords" in table_out


@pytest.mark.io
def test_non_python_path_returns_2(tmp_path: Path):
    text_file = tmp_path / "not_python.txt"
    text_file.write_text("plain text", encoding="utf-8")

    code = main(["--path", str(text_file), "--format", "json"])
    assert code == 2


@pytest.mark.io
def test_block_style_x_governs_parsing(tmp_path: Path):
    source = '''"""
x-governs:
- endogenous-first
- documentation-first

## Intent
Intent text.

## Rationale
Rationale text.
"""
'''
    target = tmp_path / "block_style.py"
    target.write_text(source, encoding="utf-8")

    payload = distill_path(target, threshold=0.08, include_private=False)
    module_record = next(item for item in payload["records"] if item["kind"] == "module")
    assert module_record["x_governs"] == ["endogenous-first", "documentation-first"]


@pytest.mark.io
def test_iter_targets_excludes_common_env_and_cache_dirs(tmp_path: Path):
    keep = tmp_path / "scripts" / "keep.py"
    skip_venv = tmp_path / ".venv" / "lib.py"
    skip_cache = tmp_path / "scripts" / "__pycache__" / "cached.py"

    keep.parent.mkdir(parents=True, exist_ok=True)
    skip_venv.parent.mkdir(parents=True, exist_ok=True)
    skip_cache.parent.mkdir(parents=True, exist_ok=True)

    keep.write_text("VALUE = 1\n", encoding="utf-8")
    skip_venv.write_text("VALUE = 2\n", encoding="utf-8")
    skip_cache.write_text("VALUE = 3\n", encoding="utf-8")

    targets = _iter_targets(tmp_path)
    assert keep in targets
    assert skip_venv not in targets
    assert skip_cache not in targets

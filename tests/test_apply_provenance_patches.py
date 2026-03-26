"""Tests for scripts/apply_provenance_patches.py."""

from __future__ import annotations

import inspect
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import scripts.apply_provenance_patches as app

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_patch(patch_dir: Path, name: str, data: dict) -> Path:
    """Write *data* as a YAML patch file in *patch_dir*; return its path."""
    p = patch_dir / f"{name}.yml"
    p.write_text(yaml.dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return p


def _write_doc(path: Path, frontmatter: dict, body: str = "## Body\n") -> None:
    """Write a research doc with YAML frontmatter at *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fm_text = yaml.dump(frontmatter, sort_keys=False, allow_unicode=True)
    path.write_text(f"---\n{fm_text}---\n{body}", encoding="utf-8")


# ---------------------------------------------------------------------------
# _rel
# ---------------------------------------------------------------------------


def test_rel_returns_relative_path_not_absolute() -> None:
    root = Path("/some/repo/root")
    path = root / "docs" / "research" / "foo.md"
    result = app._rel(path, root)
    assert result == "docs/research/foo.md"
    assert not result.startswith("/")


# ---------------------------------------------------------------------------
# apply_patches: status filter
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_apply_patches_skips_patch_with_non_matching_status(tmp_path: Path) -> None:
    patch_dir = tmp_path / "patches"
    patch_dir.mkdir()
    doc_path = tmp_path / "doc.md"
    _write_doc(doc_path, {"title": "Test", "status": "Final"})
    _write_patch(
        patch_dir,
        "p1",
        {
            "doc": str(doc_path),
            "status": "pending",
            "recommendations": [{"id": "r1", "title": "Rec"}],
        },
    )
    _, results = app.apply_patches(patch_dir=patch_dir, status_filter="approved-for-adoption")
    assert len(results) == 1
    assert results[0]["status"] == "SKIPPED"


# ---------------------------------------------------------------------------
# apply_patches: dry_run
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_apply_patches_dry_run_returns_would_apply_and_does_not_modify_file(tmp_path: Path) -> None:
    patch_dir = tmp_path / "patches"
    patch_dir.mkdir()
    doc_path = tmp_path / "doc.md"
    _write_doc(doc_path, {"title": "Test", "status": "Final"})
    original_content = doc_path.read_text(encoding="utf-8")

    _write_patch(
        patch_dir,
        "p1",
        {
            "doc": str(doc_path),
            "status": "approved-for-adoption",
            "recommendations": [{"id": "r1", "title": "Rec"}],
        },
    )
    _, results = app.apply_patches(
        patch_dir=patch_dir,
        status_filter="approved-for-adoption",
        dry_run=True,
    )
    assert len(results) == 1
    assert results[0]["status"] == "WOULD_APPLY"
    assert doc_path.read_text(encoding="utf-8") == original_content


# ---------------------------------------------------------------------------
# apply_patches: missing doc
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_apply_patches_missing_doc_returns_error(tmp_path: Path) -> None:
    patch_dir = tmp_path / "patches"
    patch_dir.mkdir()
    _write_patch(
        patch_dir,
        "p1",
        {
            "doc": str(tmp_path / "nonexistent.md"),
            "status": "approved-for-adoption",
            "recommendations": [{"id": "r1", "title": "Rec"}],
        },
    )
    exit_code, results = app.apply_patches(patch_dir=patch_dir, status_filter="approved-for-adoption")
    assert exit_code == 1
    assert results[0]["status"] == "ERROR"


# ---------------------------------------------------------------------------
# apply_patches: malformed YAML patch
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_apply_patches_malformed_yaml_patch_returns_error(tmp_path: Path) -> None:
    patch_dir = tmp_path / "patches"
    patch_dir.mkdir()
    # Write a YAML file that is syntactically invalid (unclosed flow sequence)
    (patch_dir / "bad.yml").write_text("key: [\nno closing bracket\n", encoding="utf-8")
    exit_code, results = app.apply_patches(patch_dir=patch_dir, status_filter=None)
    assert exit_code == 1
    assert any(r["status"] == "ERROR" for r in results)


# ---------------------------------------------------------------------------
# apply_patches: empty recommendations
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_apply_patches_empty_recommendations_returns_skipped(tmp_path: Path) -> None:
    patch_dir = tmp_path / "patches"
    patch_dir.mkdir()
    doc_path = tmp_path / "doc.md"
    _write_doc(doc_path, {"title": "Test", "status": "Final"})
    _write_patch(
        patch_dir,
        "p1",
        {
            "doc": str(doc_path),
            "status": "approved-for-adoption",
            "recommendations": [],
        },
    )
    _, results = app.apply_patches(patch_dir=patch_dir, status_filter="approved-for-adoption")
    assert results[0]["status"] == "SKIPPED"


# ---------------------------------------------------------------------------
# apply_patches: happy path
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_apply_patches_happy_path_applies_and_updates_file(tmp_path: Path) -> None:
    patch_dir = tmp_path / "patches"
    patch_dir.mkdir()
    doc_path = tmp_path / "doc.md"
    _write_doc(doc_path, {"title": "Original", "status": "Final", "recommendations": []})
    _write_patch(
        patch_dir,
        "p1",
        {
            "doc": str(doc_path),
            "status": "approved-for-adoption",
            "recommendations": [{"id": "r1", "title": "New Rec"}],
        },
    )
    exit_code, results = app.apply_patches(patch_dir=patch_dir, status_filter="approved-for-adoption")
    assert exit_code == 0
    assert results[0]["status"] == "APPLIED"
    updated = doc_path.read_text(encoding="utf-8")
    assert "r1" in updated


# ---------------------------------------------------------------------------
# CLI: --status-filter default
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_cli_status_filter_default_is_approved_for_adoption() -> None:
    """--status-filter help text exposes 'approved-for-adoption' as default."""
    script_path = Path(__file__).parent.parent / "scripts" / "apply_provenance_patches.py"
    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        capture_output=True,
        text=True,
    )
    assert "approved-for-adoption" in result.stdout


# ---------------------------------------------------------------------------
# _rel: relative path in repo context
# ---------------------------------------------------------------------------


def test_rel_result_has_no_absolute_path_for_path_inside_repo() -> None:
    """_rel returns a repo-relative string (no leading /) for paths inside repo root."""
    repo_root = app._repo_root()
    path = repo_root / "docs" / "research" / "example.md"
    result = app._rel(path, repo_root)
    assert not result.startswith("/")
    assert "Users" not in result
    assert result == "docs/research/example.md"


# ---------------------------------------------------------------------------
# source inspection: default is not None
# ---------------------------------------------------------------------------


def test_main_argparse_default_for_status_filter_is_not_none() -> None:
    """Verify main()'s argparse definition uses 'approved-for-adoption', not None."""
    source = inspect.getsource(app.main)
    assert 'default="approved-for-adoption"' in source or "default='approved-for-adoption'" in source

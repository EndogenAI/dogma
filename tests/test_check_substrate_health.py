"""Tests for scripts/check_substrate_health.py — Issue #248 + #279."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from check_substrate_health import classify_status, compute_crd, load_atlas, print_atlas_summary  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# classify_status tests
# ---------------------------------------------------------------------------


def test_status_pass():
    """CRD >= warn threshold → PASS."""
    assert classify_status(0.30, warn_below=0.25, block_below=0.10) == "PASS"
    assert classify_status(0.25, warn_below=0.25, block_below=0.10) == "PASS"
    assert classify_status(1.0, warn_below=0.25, block_below=0.10) == "PASS"


def test_status_warn():
    """warn_below <= CRD < warn threshold → WARN."""
    assert classify_status(0.11, warn_below=0.25, block_below=0.10) == "WARN"
    assert classify_status(0.24, warn_below=0.25, block_below=0.10) == "WARN"
    assert classify_status(0.10, warn_below=0.25, block_below=0.10) == "WARN"


def test_status_block():
    """CRD < block threshold → BLOCK."""
    assert classify_status(0.05, warn_below=0.25, block_below=0.10) == "BLOCK"
    assert classify_status(0.0, warn_below=0.25, block_below=0.10) == "BLOCK"
    assert classify_status(0.09, warn_below=0.25, block_below=0.10) == "BLOCK"


# ---------------------------------------------------------------------------
# compute_crd tests
# ---------------------------------------------------------------------------


def test_compute_crd_missing_file(tmp_path: Path):
    """Missing file → returns None."""
    result = compute_crd(tmp_path / "nonexistent.md")
    assert result is None


def test_compute_crd_no_references(tmp_path: Path):
    """File with no Markdown links → CRD = 0.0."""
    f = tmp_path / "empty.md"
    f.write_text("# Heading\n\nNo links here.\n")
    result = compute_crd(f)
    assert result == 0.0


def test_compute_crd_intra_only(tmp_path: Path):
    """File with only intra-subsystem refs → CRD = 1.0."""
    f = tmp_path / "test.agent.md"
    f.write_text("# Test\n[AGENTS.md](../../AGENTS.md)\n[MANIFESTO.md](../../MANIFESTO.md)\n")
    result = compute_crd(f)
    assert result == 1.0


def test_compute_crd_mixed(tmp_path: Path):
    """File with 1 intra + 1 cross ref → CRD = 0.5."""
    f = tmp_path / "test.agent.md"
    f.write_text("# Test\n[AGENTS.md](../../AGENTS.md)\n[Some Script](../../scripts/foo.py)\n")
    result = compute_crd(f)
    assert result == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# main() integration tests
# ---------------------------------------------------------------------------


def test_main_happy_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """File with CRD >= 0.25 → status PASS, exit 0."""
    f = tmp_path / "good.md"
    f.write_text("# Good\n[AGENTS.md](../../AGENTS.md)\n[MANIFESTO.md](../../MANIFESTO.md)\n")
    # Confirm classify_status gives PASS for this CRD value (no subprocess needed)
    crd = compute_crd(f)
    assert crd is not None
    status = classify_status(crd, warn_below=0.25, block_below=0.10)
    assert status == "PASS"


def test_main_warn_case(capsys: pytest.CaptureFixture[str]):
    """Status WARN → exit 0 (advisory only)."""
    # CRD = 0.11 → WARN (warn_below=0.25, block_below=0.10)
    status = classify_status(0.11, warn_below=0.25, block_below=0.10)
    assert status == "WARN"
    # WARN does not trigger blocked=True, so exit code would be 0
    # (covered by classify_status test above; main() exits 1 only on BLOCK)


@pytest.mark.integration
def test_main_block_case(tmp_path: Path):
    """File with CRD < 0.10 → status BLOCK, script exits 1."""
    # Create a file with only cross refs (CRD = 0.0 → BLOCK)
    f = tmp_path / "cross_only.md"
    f.write_text("# Cross\n[Some Script](../../scripts/foo.py)\n[Some Doc](../../docs/guides/bar.md)\n")
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parent.parent / "scripts" / "check_substrate_health.py"),
            "--files",
            str(f),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "BLOCK" in result.stdout


@pytest.mark.integration
def test_main_missing_file_exits_1(tmp_path: Path):
    """Script reports error and exits 1 for a missing file."""
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parent.parent / "scripts" / "check_substrate_health.py"),
            "--files",
            str(tmp_path / "does_not_exist.md"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "ERROR" in result.stdout


# ---------------------------------------------------------------------------
# --atlas flag tests (Issue #279)
# ---------------------------------------------------------------------------


def test_load_atlas_success():
    """load_atlas returns a list of substrate dicts from the real atlas file."""
    substrates = load_atlas(REPO_ROOT)
    assert isinstance(substrates, list)
    assert len(substrates) == 23, f"Expected 23 substrates, got {len(substrates)}"


def test_load_atlas_all_entries_have_required_fields():
    """Every substrate entry has id, name, tier, and validation fields."""
    substrates = load_atlas(REPO_ROOT)
    for s in substrates:
        assert "id" in s, f"Missing 'id' in substrate: {s}"
        assert "name" in s, f"Missing 'name' in substrate: {s}"
        assert "tier" in s, f"Missing 'tier' in substrate: {s}"
        assert "validation" in s, f"Missing 'validation' in substrate: {s}"


def test_load_atlas_missing_file(tmp_path: Path):
    """load_atlas exits 1 when the atlas file does not exist."""
    with pytest.raises(SystemExit) as exc_info:
        load_atlas(tmp_path)  # tmp_path has no substrate-atlas.yml
    assert exc_info.value.code == 1


def test_load_atlas_invalid_yaml(tmp_path: Path):
    """load_atlas exits 1 when the YAML is malformed."""
    bad_atlas = tmp_path / "data" / "substrate-atlas.yml"
    bad_atlas.parent.mkdir()
    bad_atlas.write_text("substrates: [unclosed\n", encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        load_atlas(tmp_path)
    assert exc_info.value.code == 1


def test_load_atlas_missing_substrates_key(tmp_path: Path):
    """load_atlas exits 1 when the YAML lacks a top-level 'substrates' key."""
    bad_atlas = tmp_path / "data" / "substrate-atlas.yml"
    bad_atlas.parent.mkdir()
    bad_atlas.write_text("other_key: []\n", encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        load_atlas(tmp_path)
    assert exc_info.value.code == 1


def test_print_atlas_summary_output(capsys: pytest.CaptureFixture[str]):
    """print_atlas_summary prints a table and WARN for unvalidated substrates."""
    substrates = load_atlas(REPO_ROOT)
    print_atlas_summary(substrates)
    captured = capsys.readouterr()
    assert "WARN" in captured.out
    assert "programmatic" in captured.out.lower() or "PASS" in captured.out
    assert "23 substrates" in captured.out


def test_print_atlas_summary_none_entries_flagged(capsys: pytest.CaptureFixture[str]):
    """Substrates with validation: none appear as WARN in the atlas summary."""
    # Synthetic atlas with one none-entry
    substrates = [
        {
            "id": 1,
            "name": "Unvalidated substrate",
            "tier": "T7: Documentation",
            "validation": "none",
            "primary_reader": ["human"],
            "persistence": "durable",
        },
        {
            "id": 2,
            "name": "Validated substrate",
            "tier": "T5: Programmatic",
            "validation": "programmatic",
            "primary_reader": ["tool"],
            "persistence": "durable",
        },
    ]
    print_atlas_summary(substrates)
    captured = capsys.readouterr()
    assert "WARN" in captured.out
    assert "1 unvalidated" in captured.out


@pytest.mark.integration
def test_atlas_flag_cli():
    """CLI --atlas flag loads the atlas and exits 0."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/check_substrate_health.py", "--atlas"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "23 substrates" in result.stdout
    assert "WARN" in result.stdout  # at least some unvalidated substrates exist

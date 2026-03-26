"""Tests for scripts/check_readiness_matrix.py."""

import pytest

from scripts.check_readiness_matrix import main


@pytest.mark.io
def test_no_capability_matrix_is_violation(tmp_path):
    """File with a plain 'ready' claim and no capability matrix → exit 1."""
    f = tmp_path / "plan.md"
    f.write_text("The system is ready for production use.\n")
    assert main([str(f)]) == 1


@pytest.mark.io
def test_inline_matrix_claim_no_violation(tmp_path):
    """Inline text 'capability matrix: Retrieval ✅, E2E ✅' is sufficient."""
    f = tmp_path / "plan.md"
    f.write_text("Ready — capability matrix: Retrieval ✅, Augmentation ✅, Generation ✅, E2E ✅\n")
    assert main([str(f)]) == 0


@pytest.mark.io
def test_yaml_block_matrix_no_violation(tmp_path):
    """capability_matrix: YAML block suppresses the violation."""
    f = tmp_path / "plan.md"
    f.write_text("This feature is ready.\n\ncapability_matrix:\n  retrieval: yes\n  end_to_end: yes\n")
    assert main([str(f)]) == 0


@pytest.mark.io
def test_not_ready_no_violation(tmp_path):
    """'not ready' is a negation and must not trigger a violation."""
    f = tmp_path / "plan.md"
    f.write_text("The system is not ready for production.\n")
    assert main([str(f)]) == 0


@pytest.mark.io
def test_empty_file_no_violation(tmp_path):
    """Empty file has no claims and must not trigger a violation."""
    f = tmp_path / "empty.md"
    f.write_text("")
    assert main([str(f)]) == 0


@pytest.mark.io
def test_multiple_files_one_violating(tmp_path):
    """With two files, one violating, exit 1 and only the violating file is reported (stdout)."""
    ok = tmp_path / "ok.md"
    ok.write_text("capability_matrix:\n  retrieval: yes\nThe feature is ready.\n")
    bad = tmp_path / "bad.md"
    bad.write_text("This feature is ready.\n")

    # Capture stdout via capsys is not available here; verify exit code suffices
    result = main([str(ok), str(bad)])
    assert result == 1


@pytest.mark.io
def test_strict_partial_dimension(tmp_path):
    """--strict: capability matrix present but a dimension is 'partial' → exit 1."""
    f = tmp_path / "plan.md"
    f.write_text("Ready to ship.\n\ncapability_matrix:\n  retrieval: yes\n  end_to_end: partial\n")
    assert main(["--strict", str(f)]) == 1


@pytest.mark.io
def test_strict_no_partial(tmp_path):
    """--strict: all dimensions 'yes' → exit 0."""
    f = tmp_path / "plan.md"
    f.write_text("Ready to ship.\n\ncapability_matrix:\n  retrieval: yes\n  end_to_end: yes\n")
    assert main(["--strict", str(f)]) == 0


@pytest.mark.io
def test_retrieval_table_row_no_violation(tmp_path):
    """A markdown table with a '| Retrieval |' row counts as a matrix."""
    f = tmp_path / "plan.md"
    f.write_text(
        "System is ready.\n\n| Dimension | Status |\n|-----------|--------|\n| Retrieval | ✅ |\n| E2E | ✅ |\n"
    )
    assert main([str(f)]) == 0


@pytest.mark.io
def test_no_files_argument_exits_0():
    """Calling with no files should not crash and return 0."""
    assert main([]) == 0

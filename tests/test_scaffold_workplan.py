"""
tests/test_scaffold_workplan.py
--------------------------------
Tests for scripts/scaffold_workplan.py

Covers:
- sanitize_filename: spaces → hyphens, colons → hyphens, special chars stripped,
  consecutive hyphens collapsed, leading/trailing hyphens stripped, already-clean slug
- slug_to_title: dash → space + title-case conversion
- main(): creates expected file, sanitized slug reflected in filename, duplicate file
  returns exit code 1, empty-after-sanitize slug returns exit code 1, invalid CI value
  returns exit code 1, invalid issue number returns exit code 1, --issues flag appended

All filesystem side effects use tmp_path fixture (no writes to docs/plans/).

Marked @pytest.mark.io for tests performing filesystem I/O.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Module loader
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def sw_mod():
    """Load scripts/scaffold_workplan.py via importlib for in-process testing."""
    spec = importlib.util.spec_from_file_location(
        "scaffold_workplan",
        Path(__file__).parent.parent / "scripts" / "scaffold_workplan.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# sanitize_filename
# ---------------------------------------------------------------------------


class TestSanitizeFilename:
    """Unit tests for sanitize_filename(). No I/O."""

    def test_spaces_replaced_with_hyphens(self, sw_mod):
        assert sw_mod.sanitize_filename("sprint 19 planning") == "sprint-19-planning"

    def test_colons_replaced_with_hyphens(self, sw_mod):
        assert sw_mod.sanitize_filename("sprint:19") == "sprint-19"

    def test_spaces_and_colons_combined(self, sw_mod):
        result = sw_mod.sanitize_filename("sprint 19: governance l0-l3")
        assert " " not in result
        assert ":" not in result
        assert result == "sprint-19-governance-l0-l3"

    def test_special_chars_stripped(self, sw_mod):
        result = sw_mod.sanitize_filename("feat/my+workflow & plan!")
        assert "/" not in result
        assert "+" not in result
        assert "&" not in result
        assert "!" not in result

    def test_consecutive_hyphens_collapsed(self, sw_mod):
        assert sw_mod.sanitize_filename("a--b---c") == "a-b-c"

    def test_colon_space_combo_no_double_hyphen(self, sw_mod):
        # "x: y" → "x--y" before collapse → "x-y"
        assert sw_mod.sanitize_filename("x: y") == "x-y"

    def test_leading_trailing_hyphens_stripped(self, sw_mod):
        assert sw_mod.sanitize_filename("-leading-trailing-") == "leading-trailing"

    def test_already_clean_slug_unchanged(self, sw_mod):
        assert sw_mod.sanitize_filename("formalize-workflows") == "formalize-workflows"

    def test_lowercase_preserved(self, sw_mod):
        result = sw_mod.sanitize_filename("my-workplan")
        assert result == result.lower()

    def test_digits_preserved(self, sw_mod):
        assert sw_mod.sanitize_filename("sprint-19") == "sprint-19"

    def test_underscores_preserved(self, sw_mod):
        assert sw_mod.sanitize_filename("my_plan") == "my_plan"

    def test_lychee_panic_filename(self, sw_mod):
        """Reproduce the slug that caused the lychee v0.23.0 tokio SendError panic."""
        original = "sprint 19: governance l0-l3 maturity + ethics rubric + fleet integration"
        result = sw_mod.sanitize_filename(original)
        assert " " not in result
        assert ":" not in result
        assert "+" not in result
        assert len(result) > 0


# ---------------------------------------------------------------------------
# slug_to_title
# ---------------------------------------------------------------------------


class TestSlugToTitle:
    """Unit tests for slug_to_title(). No I/O."""

    def test_single_word(self, sw_mod):
        assert sw_mod.slug_to_title("workflows") == "Workflows"

    def test_multi_word(self, sw_mod):
        assert sw_mod.slug_to_title("formalize-workflows") == "Formalize Workflows"

    def test_numbers_preserved(self, sw_mod):
        assert sw_mod.slug_to_title("sprint-19-plan") == "Sprint 19 Plan"


# ---------------------------------------------------------------------------
# main() — filesystem I/O tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def plans_dir(tmp_path):
    """Return a temporary plans directory, monkeypatching _get_root()."""
    return tmp_path


@pytest.mark.io
class TestMain:
    """Tests for main() — uses tmp_path to isolate filesystem writes."""

    def _run_main(self, sw_mod, tmp_path, argv):
        """Run main() with a monkeypatched root and given sys.argv."""
        with (
            patch.object(sw_mod, "_get_root", return_value=tmp_path),
            patch.object(sw_mod, "_git_branch", return_value="test-branch"),
            patch("sys.argv", ["scaffold_workplan.py"] + argv),
        ):
            return sw_mod.main()

    def test_creates_file_with_clean_slug(self, sw_mod, tmp_path):
        rc = self._run_main(sw_mod, tmp_path, ["formalize-workflows"])
        assert rc == 0
        created = list((tmp_path / "docs" / "plans").glob("*.md"))
        assert len(created) == 1
        assert "formalize-workflows" in created[0].name

    def test_sanitized_slug_reflected_in_filename(self, sw_mod, tmp_path):
        rc = self._run_main(sw_mod, tmp_path, ["sprint 19: governance"])
        assert rc == 0
        created = list((tmp_path / "docs" / "plans").glob("*.md"))
        assert len(created) == 1
        assert " " not in created[0].name
        assert ":" not in created[0].name

    def test_duplicate_file_returns_exit_1(self, sw_mod, tmp_path):
        self._run_main(sw_mod, tmp_path, ["my-plan"])
        rc = self._run_main(sw_mod, tmp_path, ["my-plan"])
        assert rc == 1

    def test_empty_after_sanitize_returns_exit_1(self, sw_mod, tmp_path):
        # A slug of purely special chars becomes empty after sanitization
        rc = self._run_main(sw_mod, tmp_path, ["!!!"])
        assert rc == 1

    def test_invalid_ci_returns_exit_1(self, sw_mod, tmp_path):
        rc = self._run_main(sw_mod, tmp_path, ["my-plan", "--ci", "Unknown"])
        assert rc == 1

    def test_invalid_issue_number_returns_exit_1(self, sw_mod, tmp_path):
        rc = self._run_main(sw_mod, tmp_path, ["my-plan", "--issues", "notanumber"])
        assert rc == 1

    def test_issues_flag_appends_closes_lines(self, sw_mod, tmp_path):
        self._run_main(sw_mod, tmp_path, ["my-plan", "--issues", "42,43"])
        created = list((tmp_path / "docs" / "plans").glob("*.md"))[0]
        content = created.read_text()
        assert "Closes #42" in content
        assert "Closes #43" in content

    def test_created_file_contains_branch(self, sw_mod, tmp_path):
        self._run_main(sw_mod, tmp_path, ["my-plan"])
        created = list((tmp_path / "docs" / "plans").glob("*.md"))[0]
        content = created.read_text()
        assert "test-branch" in content

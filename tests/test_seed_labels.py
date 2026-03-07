"""
tests/test_seed_labels.py

Unit tests for scripts/seed_labels.py.

Coverage targets
----------------
- Happy path dry-run: correct output lines, no subprocess calls
- --delete-legacy dry-run: deletion lines printed, no subprocess calls
- Missing labels file: sys.exit(2)
- Invalid YAML: sys.exit(1)
- Missing required keys in a label entry: sys.exit(1)
- Label creation: correct gh CLI args passed to subprocess
- Label deletion: correct gh CLI args passed to subprocess
- Label deletion with "not found" response: non-fatal warning, continues
- --repo flag: passes -R owner/repo to subprocess
- gh auth failure: sys.exit(1) when not dry-run

Markers
-------
@pytest.mark.io   — tests that read/write temporary files
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------
# We import individual functions rather than running via __main__ so that we
# can test each unit in isolation.
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import seed_labels  # noqa: E402 — after sys.path manipulation

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MINIMAL_MANIFEST = {
    "labels": [
        {"name": "effort:xs", "color": "c2e0c6", "description": "< 30 min"},
        {"name": "priority:high", "color": "e4e669", "description": "This sprint"},
    ],
    "legacy_labels": ["bug", "documentation"],
}


@pytest.fixture
def labels_file(tmp_path: Path) -> Path:
    """Write a minimal labels.yml to a temp directory and return the path."""
    path = tmp_path / "labels.yml"
    path.write_text(yaml.dump(MINIMAL_MANIFEST), encoding="utf-8")
    return path


@pytest.fixture
def full_labels_file(tmp_path: Path) -> Path:
    """Write the real data/labels.yml content to a temp file."""
    real_path = Path(__file__).parent.parent / "data" / "labels.yml"
    content = real_path.read_text(encoding="utf-8")
    path = tmp_path / "labels.yml"
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# load_manifest tests
# ---------------------------------------------------------------------------


class TestLoadManifest:
    """Tests for seed_labels.load_manifest()."""

    @pytest.mark.io
    def test_loads_valid_file(self, labels_file: Path) -> None:
        """load_manifest returns a dict with 'labels' list for a valid file."""
        data = seed_labels.load_manifest(labels_file)
        assert isinstance(data, dict)
        assert "labels" in data
        assert len(data["labels"]) == 2

    @pytest.mark.io
    def test_exit_2_when_file_missing(self, tmp_path: Path) -> None:
        """load_manifest exits 2 when the labels file does not exist."""
        missing = tmp_path / "nonexistent.yml"
        with pytest.raises(SystemExit) as exc_info:
            seed_labels.load_manifest(missing)
        assert exc_info.value.code == 2

    @pytest.mark.io
    def test_exit_1_on_invalid_yaml(self, tmp_path: Path) -> None:
        """load_manifest exits 1 when YAML is malformed."""
        bad_file = tmp_path / "bad.yml"
        bad_file.write_text("labels: [unclosed: {", encoding="utf-8")
        with pytest.raises(SystemExit) as exc_info:
            seed_labels.load_manifest(bad_file)
        assert exc_info.value.code == 1

    @pytest.mark.io
    def test_exit_1_when_labels_key_missing(self, tmp_path: Path) -> None:
        """load_manifest exits 1 when top-level 'labels' key is absent."""
        no_labels = tmp_path / "no_labels.yml"
        no_labels.write_text("legacy_labels:\n  - bug\n", encoding="utf-8")
        with pytest.raises(SystemExit) as exc_info:
            seed_labels.load_manifest(no_labels)
        assert exc_info.value.code == 1

    @pytest.mark.io
    def test_exit_1_when_label_missing_required_key(self, tmp_path: Path) -> None:
        """load_manifest exits 1 when a label entry is missing 'color'."""
        broken = tmp_path / "broken.yml"
        broken.write_text(
            "labels:\n  - name: foo\n    description: bar\n",
            encoding="utf-8",
        )
        with pytest.raises(SystemExit) as exc_info:
            seed_labels.load_manifest(broken)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# create_or_update_label tests
# ---------------------------------------------------------------------------


class TestCreateOrUpdateLabel:
    """Tests for seed_labels.create_or_update_label()."""

    def test_dry_run_prints_and_does_not_call_subprocess(
        self, mocker: "MockerFixture", capsys: pytest.CaptureFixture
    ) -> None:
        """dry_run=True prints the planned action without calling subprocess."""
        mock_sp = mocker.patch("seed_labels.subprocess")
        seed_labels.create_or_update_label("effort:xs", "c2e0c6", "< 30 min", repo=None, dry_run=True)
        mock_sp.run.assert_not_called()

        out = capsys.readouterr().out
        assert "[DRY RUN]" in out
        assert "effort:xs" in out
        assert "c2e0c6" in out

    def test_calls_gh_label_create_with_force(self, mocker: "MockerFixture") -> None:
        """Non-dry-run invokes gh label create --force with correct args."""
        mock_run = mocker.patch("seed_labels.subprocess.run")
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        seed_labels.create_or_update_label("effort:xs", "c2e0c6", "< 30 min", repo=None, dry_run=False)

        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "gh" in cmd
        assert "label" in cmd
        assert "create" in cmd
        assert "effort:xs" in cmd
        assert "--force" in cmd
        assert "--color" in cmd
        assert "c2e0c6" in cmd
        assert "--description" in cmd

    def test_calls_gh_with_repo_flag_when_repo_set(self, mocker: "MockerFixture") -> None:
        """Passes -R owner/repo to gh when --repo is specified."""
        mock_run = mocker.patch("seed_labels.subprocess.run")
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        seed_labels.create_or_update_label("effort:xs", "c2e0c6", "< 30 min", repo="myorg/myrepo", dry_run=False)

        cmd = mock_run.call_args[0][0]
        assert "-R" in cmd
        assert "myorg/myrepo" in cmd

    def test_exit_1_on_gh_failure(self, mocker: "MockerFixture") -> None:
        """Exits 1 when gh label create returns a non-zero exit code."""
        mock_run = mocker.patch("seed_labels.subprocess.run")
        mock_run.return_value = MagicMock(returncode=1, stderr="label error")

        with pytest.raises(SystemExit) as exc_info:
            seed_labels.create_or_update_label("effort:xs", "c2e0c6", "< 30 min", repo=None, dry_run=False)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# delete_label tests
# ---------------------------------------------------------------------------


class TestDeleteLabel:
    """Tests for seed_labels.delete_label()."""

    def test_dry_run_prints_and_does_not_call_subprocess(
        self, mocker: "MockerFixture", capsys: pytest.CaptureFixture
    ) -> None:
        """dry_run=True prints the planned deletion without calling subprocess."""
        mock_sp = mocker.patch("seed_labels.subprocess")
        seed_labels.delete_label("bug", repo=None, dry_run=True)
        mock_sp.run.assert_not_called()

        out = capsys.readouterr().out
        assert "[DRY RUN]" in out
        assert "bug" in out

    def test_calls_gh_label_delete(self, mocker: "MockerFixture") -> None:
        """Non-dry-run invokes gh label delete --yes with correct args."""
        mock_run = mocker.patch("seed_labels.subprocess.run")
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        seed_labels.delete_label("bug", repo=None, dry_run=False)

        cmd = mock_run.call_args[0][0]
        assert "gh" in cmd
        assert "label" in cmd
        assert "delete" in cmd
        assert "bug" in cmd
        assert "--yes" in cmd

    def test_not_found_is_non_fatal(self, mocker: "MockerFixture", capsys: pytest.CaptureFixture) -> None:
        """delete_label prints a skip warning (not raises) when label not found."""
        mock_run = mocker.patch("seed_labels.subprocess.run")
        mock_run.return_value = MagicMock(returncode=1, stderr="could not find label 'bug'")

        # Should NOT raise SystemExit
        seed_labels.delete_label("bug", repo=None, dry_run=False)

        out = capsys.readouterr().out
        assert "SKIP" in out or "not found" in out.lower()

    def test_exit_1_on_unexpected_gh_failure(self, mocker: "MockerFixture") -> None:
        """delete_label exits 1 for unexpected gh errors (not 'not found')."""
        mock_run = mocker.patch("seed_labels.subprocess.run")
        mock_run.return_value = MagicMock(returncode=1, stderr="network error")

        with pytest.raises(SystemExit) as exc_info:
            seed_labels.delete_label("bug", repo=None, dry_run=False)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# main() integration tests (dry-run only — no real gh calls)
# ---------------------------------------------------------------------------


class TestMainDryRun:
    """Integration tests for seed_labels.main() in dry-run mode."""

    @pytest.mark.io
    def test_dry_run_prints_all_labels(
        self, mocker: "MockerFixture", labels_file: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """--dry-run prints one line per namespace label, no subprocess calls."""
        mock_sp = mocker.patch("seed_labels.subprocess")
        seed_labels.main(["--labels-file", str(labels_file), "--dry-run"])
        mock_sp.run.assert_not_called()

        out = capsys.readouterr().out
        assert "effort:xs" in out
        assert "priority:high" in out
        assert "[DRY RUN]" in out

    @pytest.mark.io
    def test_dry_run_delete_legacy_shows_deletions(
        self, mocker: "MockerFixture", labels_file: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """--dry-run --delete-legacy includes deletion lines for legacy labels."""
        mock_sp = mocker.patch("seed_labels.subprocess")
        seed_labels.main(["--labels-file", str(labels_file), "--dry-run", "--delete-legacy"])
        mock_sp.run.assert_not_called()

        out = capsys.readouterr().out
        assert "bug" in out
        assert "documentation" in out
        # One DRY RUN line per legacy label
        delete_lines = [line for line in out.splitlines() if "WOULD DELETE" in line]
        assert len(delete_lines) == 2  # two legacy labels in MINIMAL_MANIFEST

    @pytest.mark.io
    def test_dry_run_does_not_delete_legacy_by_default(
        self, mocker: "MockerFixture", labels_file: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Without --delete-legacy, legacy labels are not mentioned."""
        mocker.patch("seed_labels.subprocess")
        seed_labels.main(["--labels-file", str(labels_file), "--dry-run"])

        out = capsys.readouterr().out
        delete_lines = [line for line in out.splitlines() if "WOULD DELETE" in line]
        assert len(delete_lines) == 0

    @pytest.mark.io
    def test_exit_2_when_file_not_found(self, tmp_path: Path) -> None:
        """main() exits 2 when the labels file does not exist."""
        missing = str(tmp_path / "nonexistent.yml")
        with pytest.raises(SystemExit) as exc_info:
            seed_labels.main(["--labels-file", missing])
        assert exc_info.value.code == 2

    @pytest.mark.io
    def test_real_labels_file_loads_without_error(
        self, mocker: "MockerFixture", full_labels_file: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """The actual data/labels.yml loads cleanly in dry-run mode."""
        mocker.patch("seed_labels.subprocess")
        seed_labels.main(["--labels-file", str(full_labels_file), "--dry-run"])

        out = capsys.readouterr().out
        # All namespaces must appear
        for prefix in ("effort:", "priority:", "type:", "area:", "status:"):
            assert prefix in out, f"Expected '{prefix}' labels in dry-run output"


# ---------------------------------------------------------------------------
# gh auth verification tests
# ---------------------------------------------------------------------------


class TestVerifyGhAuth:
    """Tests for seed_labels._verify_gh_auth()."""

    def test_skips_check_in_dry_run(self, mocker: "MockerFixture") -> None:
        """_verify_gh_auth makes no subprocess call when dry_run=True."""
        mock_run = mocker.patch("seed_labels.subprocess.run")
        seed_labels._verify_gh_auth(repo=None, dry_run=True)
        mock_run.assert_not_called()

    def test_exits_1_when_auth_fails(self, mocker: "MockerFixture") -> None:
        """_verify_gh_auth exits 1 when gh auth status fails."""
        mock_run = mocker.patch("seed_labels.subprocess.run")
        mock_run.return_value = MagicMock(returncode=1, stderr="not logged in")

        with pytest.raises(SystemExit) as exc_info:
            seed_labels._verify_gh_auth(repo=None, dry_run=False)
        assert exc_info.value.code == 1

    def test_passes_when_auth_succeeds(self, mocker: "MockerFixture") -> None:
        """_verify_gh_auth returns normally when gh auth status exits 0."""
        mock_run = mocker.patch("seed_labels.subprocess.run")
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        # Should not raise
        seed_labels._verify_gh_auth(repo=None, dry_run=False)

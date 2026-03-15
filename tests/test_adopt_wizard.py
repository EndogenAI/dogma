"""
tests/test_adopt_wizard.py

Unit tests for scripts/adopt_wizard.py

Tests cover:
- AC1: --org and --repo flags required; exits 1 if missing
- AC2: client-values.yml written with correct schema
- AC3: AGENTS.md scaffolded with Deployment Layer comment
- AC4: validate_agent_files.py run; validation failure exits 1
- AC5: summary output structure
- --non-interactive happy path
- Duplicate run idempotency (issue #125)
- --load-values reads existing file as defaults (issue #125)
- validate_client_values catches missing required key (issue #125)
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from adopt_wizard import (  # noqa: E402
    _DEPLOYMENT_COMMENT,
    _write_agents_md,
    main,
    validate_client_values,
)

# ---------------------------------------------------------------------------
# AC1 — CLI flags
# ---------------------------------------------------------------------------


class TestAC1CliFlags:
    """--org and --repo are required; wizard exits 1 if either is missing."""

    def test_missing_org_exits_nonzero(self):
        """Missing --org causes SystemExit (argparse error)."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--repo", "platform"])
        assert exc_info.value.code != 0

    def test_missing_repo_exits_nonzero(self):
        """Missing --repo causes SystemExit (argparse error)."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--org", "MyOrg"])
        assert exc_info.value.code != 0

    def test_both_flags_present_does_not_exit_on_parse(self, tmp_path):
        """With both flags, the parser proceeds without raising SystemExit."""
        with patch("adopt_wizard._run_validation", return_value=(True, "")):
            code = main(["--org", "MyOrg", "--repo", "myrepo", "--non-interactive", "--output-dir", str(tmp_path)])
        assert code == 0


# ---------------------------------------------------------------------------
# AC2 — client-values.yml schema
# ---------------------------------------------------------------------------


class TestAC2ClientValuesSchema:
    """client-values.yml written with all required schema keys."""

    @pytest.mark.io
    def test_client_values_written(self, tmp_path):
        """client-values.yml is created in the output directory."""
        with patch("adopt_wizard._run_validation", return_value=(True, "")):
            main(["--org", "TestOrg", "--repo", "testrepo", "--non-interactive", "--output-dir", str(tmp_path)])
        assert (tmp_path / "client-values.yml").exists()

    @pytest.mark.io
    def test_client_values_has_required_keys(self, tmp_path):
        """Generated client-values.yml contains mission, priorities, axiom_emphasis."""
        with patch("adopt_wizard._run_validation", return_value=(True, "")):
            main(["--org", "TestOrg", "--repo", "testrepo", "--non-interactive", "--output-dir", str(tmp_path)])
        data = yaml.safe_load((tmp_path / "client-values.yml").read_text())
        assert "mission" in data
        assert "priorities" in data
        assert isinstance(data["priorities"], list)
        assert "axiom_emphasis" in data
        assert "deployment_layer" in data

    @pytest.mark.io
    def test_client_values_org_repo_populated(self, tmp_path):
        """Generated client-values.yml records org and repo."""
        with patch("adopt_wizard._run_validation", return_value=(True, "")):
            main(["--org", "AccessiTech", "--repo", "platform", "--non-interactive", "--output-dir", str(tmp_path)])
        data = yaml.safe_load((tmp_path / "client-values.yml").read_text())
        assert data["org"] == "AccessiTech"
        assert data["repo"] == "platform"


# ---------------------------------------------------------------------------
# AC3 — AGENTS.md scaffolding
# ---------------------------------------------------------------------------


class TestAC3AgentsMdScaffolding:
    """AGENTS.md is created with the Deployment Layer comment prepended."""

    @pytest.mark.io
    def test_agents_md_written(self, tmp_path):
        """AGENTS.md is created in the output directory."""
        with patch("adopt_wizard._run_validation", return_value=(True, "")):
            main(["--org", "TestOrg", "--repo", "testrepo", "--non-interactive", "--output-dir", str(tmp_path)])
        assert (tmp_path / "AGENTS.md").exists()

    @pytest.mark.io
    def test_agents_md_has_deployment_comment(self, tmp_path):
        """AGENTS.md starts with the Deployment Layer comment."""
        with patch("adopt_wizard._run_validation", return_value=(True, "")):
            main(["--org", "TestOrg", "--repo", "testrepo", "--non-interactive", "--output-dir", str(tmp_path)])
        content = (tmp_path / "AGENTS.md").read_text()
        assert content.startswith(_DEPLOYMENT_COMMENT)
        assert "client-values.yml" in content
        assert "Deployment Layer" in content

    @pytest.mark.io
    def test_agents_md_write_helper(self, tmp_path):
        """_write_agents_md writes a file that starts with the deployment comment."""
        path = _write_agents_md(tmp_path)
        assert path.exists()
        assert path.read_text().startswith(_DEPLOYMENT_COMMENT)


# ---------------------------------------------------------------------------
# AC4 — Automatic validation
# ---------------------------------------------------------------------------


class TestAC4AutomaticValidation:
    """validate_agent_files.py is invoked; validation failure exits 1."""

    @pytest.mark.io
    def test_validation_called(self, tmp_path):
        """_run_validation is called during main()."""
        with patch("adopt_wizard._run_validation", return_value=(True, "")) as mock_val:
            main(["--org", "T", "--repo", "r", "--non-interactive", "--output-dir", str(tmp_path)])
        mock_val.assert_called_once()

    @pytest.mark.io
    def test_validation_failure_exits_1(self, tmp_path, capsys):
        """When validation fails, main returns 1 and does not print the summary."""
        with patch("adopt_wizard._run_validation", return_value=(False, "ERROR: missing heading")):
            code = main(["--org", "T", "--repo", "r", "--non-interactive", "--output-dir", str(tmp_path)])
        assert code == 1
        captured = capsys.readouterr()
        # Success summary must NOT appear on failure
        assert "Adoption complete" not in captured.out

    @pytest.mark.io
    def test_validation_output_surfaced(self, tmp_path, capsys):
        """Raw validator output is printed to stdout (not suppressed)."""
        with patch(
            "adopt_wizard._run_validation",
            return_value=(False, "FAIL: bad-file.agent.md — missing section"),
        ):
            main(["--org", "T", "--repo", "r", "--non-interactive", "--output-dir", str(tmp_path)])
        captured = capsys.readouterr()
        assert "FAIL: bad-file.agent.md" in captured.out


# ---------------------------------------------------------------------------
# AC5 — Summary output
# ---------------------------------------------------------------------------


class TestAC5SummaryOutput:
    """On success, wizard prints a structured summary."""

    @pytest.mark.io
    def test_summary_printed_on_success(self, tmp_path, capsys):
        """Successful run prints 'Adoption complete' and 'Validation: PASSED'."""
        with patch("adopt_wizard._run_validation", return_value=(True, "")):
            code = main(["--org", "MyOrg", "--repo", "myrepo", "--non-interactive", "--output-dir", str(tmp_path)])
        assert code == 0
        captured = capsys.readouterr()
        assert "Adoption complete for MyOrg/myrepo" in captured.out
        assert "Validation: PASSED" in captured.out
        assert "Next steps:" in captured.out
        assert "client-values.yml" in captured.out
        assert "AGENTS.md" in captured.out


# ---------------------------------------------------------------------------
# --non-interactive happy path
# ---------------------------------------------------------------------------


class TestNonInteractiveHappyPath:
    """--non-interactive flag uses defaults without prompting."""

    @pytest.mark.io
    def test_non_interactive_writes_files(self, tmp_path):
        """--non-interactive creates both output files without any stdin."""
        with patch("adopt_wizard._run_validation", return_value=(True, "")):
            code = main(["--org", "ACME", "--repo", "acme-repo", "--non-interactive", "--output-dir", str(tmp_path)])
        assert code == 0
        assert (tmp_path / "client-values.yml").exists()
        assert (tmp_path / "AGENTS.md").exists()

    @pytest.mark.io
    def test_non_interactive_axiom_default(self, tmp_path):
        """Default axiom_emphasis in non-interactive mode is endogenous-first."""
        with patch("adopt_wizard._run_validation", return_value=(True, "")):
            main(["--org", "X", "--repo", "y", "--non-interactive", "--output-dir", str(tmp_path)])
        data = yaml.safe_load((tmp_path / "client-values.yml").read_text())
        assert data["axiom_emphasis"] == "endogenous-first"


# ---------------------------------------------------------------------------
# Idempotency — duplicate run
# ---------------------------------------------------------------------------


class TestIdempotency:
    """Running the wizard twice in the same directory overwrites safely."""

    @pytest.mark.io
    def test_duplicate_run_not_raises(self, tmp_path):
        """Second run completes with exit 0 (files are overwritten)."""
        with patch("adopt_wizard._run_validation", return_value=(True, "")):
            code1 = main(["--org", "OrgA", "--repo", "repoA", "--non-interactive", "--output-dir", str(tmp_path)])
            code2 = main(["--org", "OrgA", "--repo", "repoA", "--non-interactive", "--output-dir", str(tmp_path)])
        assert code1 == 0
        assert code2 == 0

    @pytest.mark.io
    def test_duplicate_run_produces_valid_yaml(self, tmp_path):
        """After two runs, client-values.yml is still valid YAML."""
        with patch("adopt_wizard._run_validation", return_value=(True, "")):
            main(["--org", "OrgA", "--repo", "repoA", "--non-interactive", "--output-dir", str(tmp_path)])
            main(["--org", "OrgA", "--repo", "repoA", "--non-interactive", "--output-dir", str(tmp_path)])
        data = yaml.safe_load((tmp_path / "client-values.yml").read_text())
        assert data is not None


# ---------------------------------------------------------------------------
# Issue #125 — --load-values and validate_client_values
# ---------------------------------------------------------------------------


class TestLoadValues:
    """--load-values reads existing client-values.yml as prompt defaults."""

    @pytest.mark.io
    def test_load_values_uses_existing_mission(self, tmp_path):
        """--load-values passes existing mission as default for --non-interactive."""
        existing = tmp_path / "client-values.yml"
        existing.write_text(
            "org: Original\nrepo: original-repo\nmission: Our specific mission.\n"
            "priorities:\n  - Local Compute-First\n"
            "axiom_emphasis: local-compute-first\nconstraints: []\ndeployment_layer: {}\n"
        )
        with patch("adopt_wizard._run_validation", return_value=(True, "")):
            main(
                [
                    "--org",
                    "Original",
                    "--repo",
                    "original-repo",
                    "--non-interactive",
                    "--load-values",
                    str(existing),
                    "--output-dir",
                    str(tmp_path),
                ]
            )
        data = yaml.safe_load((tmp_path / "client-values.yml").read_text())
        assert data["mission"] == "Our specific mission."
        assert data["priorities"] == ["Local Compute-First"]
        assert data["axiom_emphasis"] == "local-compute-first"

    def test_load_values_missing_file_warns(self, tmp_path, capsys):
        """--load-values silently continues if the file does not exist (warns to stderr)."""
        missing = tmp_path / "nonexistent.yml"
        with patch("adopt_wizard._run_validation", return_value=(True, "")):
            code = main(
                [
                    "--org",
                    "X",
                    "--repo",
                    "y",
                    "--non-interactive",
                    "--load-values",
                    str(missing),
                    "--output-dir",
                    str(tmp_path),
                ]
            )
        # Should still succeed, just uses built-in defaults
        assert code == 0


class TestValidateClientValues:
    """validate_client_values() returns errors for invalid files."""

    def test_valid_file_returns_no_errors(self, tmp_path):
        """A file with mission and priorities passes validation."""
        f = tmp_path / "client-values.yml"
        f.write_text("mission: Build good things.\npriorities:\n  - Endogenous-First\n")
        errors = validate_client_values(f)
        assert errors == []

    def test_missing_mission_returns_error(self, tmp_path):
        """Missing mission key is reported as an error."""
        f = tmp_path / "client-values.yml"
        f.write_text("priorities:\n  - Endogenous-First\n")
        errors = validate_client_values(f)
        assert any("mission" in e for e in errors)

    def test_missing_priorities_returns_error(self, tmp_path):
        """Missing priorities key is reported as an error."""
        f = tmp_path / "client-values.yml"
        f.write_text("mission: Some mission.\n")
        errors = validate_client_values(f)
        assert any("priorities" in e for e in errors)

    def test_empty_priorities_returns_error(self, tmp_path):
        """Empty priorities list is reported as an error."""
        f = tmp_path / "client-values.yml"
        f.write_text("mission: Some mission.\npriorities: []\n")
        errors = validate_client_values(f)
        assert any("priorities" in e for e in errors)

    def test_nonexistent_file_returns_error(self, tmp_path):
        """A path that does not exist returns a 'file not found' error."""
        errors = validate_client_values(tmp_path / "missing.yml")
        assert errors
        assert any("not found" in e for e in errors)

    def test_invalid_yaml_returns_error(self, tmp_path):
        """Malformed YAML returns a parse error."""
        f = tmp_path / "client-values.yml"
        f.write_text("mission: [\nunclosed bracket\n")
        errors = validate_client_values(f)
        assert errors
        assert any("YAML" in e or "yaml" in e.lower() for e in errors)

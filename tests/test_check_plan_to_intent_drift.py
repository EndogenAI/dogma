"""Tests for scripts/check_plan_to_intent_drift.py."""

import pytest

from scripts.check_plan_to_intent_drift import main


@pytest.mark.io
def test_no_contract_file_exits_0(tmp_path):
    """When no contract file exists the script exits 0 and prints a skip message."""
    workplan = tmp_path / "2026-03-26-sprint.md"
    workplan.write_text("# Sprint workplan\n\n## Acceptance criteria\n- Item A done\n")
    # No contract file present
    assert main(["--workplan", str(workplan)]) == 0


@pytest.mark.io
def test_all_acceptance_tests_covered(tmp_path):
    """Contract acceptance tests all appear in the workplan → exit 0."""
    workplan = tmp_path / "plan.md"
    workplan.write_text(
        "# Workplan\n\n## Acceptance criteria\n- run end-to-end smoke test\n- verify retrieval returns 5 results\n"
    )
    contract_dir = tmp_path / "plan"
    contract_dir.mkdir()
    contract = contract_dir / "intent-contract.md"
    contract.write_text(
        "```yaml\n"
        "acceptance_tests:\n"
        "  - name: end-to-end smoke test\n"
        "    command: pytest tests/e2e/\n"
        "  - name: verify retrieval returns 5 results\n"
        "    command: pytest tests/test_retrieval.py\n"
        "```\n"
    )
    assert main(["--workplan", str(workplan)]) == 0


@pytest.mark.io
def test_missing_acceptance_test_exits_1(tmp_path):
    """Contract test not referenced in workplan → exit 1."""
    workplan = tmp_path / "plan.md"
    workplan.write_text("# Workplan\n\n## Acceptance criteria\n- run smoke test\n")
    contract_dir = tmp_path / "plan"
    contract_dir.mkdir()
    contract = contract_dir / "intent-contract.md"
    contract.write_text(
        "```yaml\n"
        "acceptance_tests:\n"
        "  - name: run smoke test\n"
        "    command: pytest tests/smoke/\n"
        "  - name: verify citation quality\n"
        "    command: pytest tests/test_citations.py\n"
        "```\n"
    )
    assert main(["--workplan", str(workplan)]) == 1


@pytest.mark.io
def test_check_flag_always_exits_0(tmp_path):
    """--check mode: drift detected but exit 0 (advisory only)."""
    workplan = tmp_path / "plan.md"
    workplan.write_text("# Workplan\n")
    contract_dir = tmp_path / "plan"
    contract_dir.mkdir()
    contract = contract_dir / "intent-contract.md"
    contract.write_text(
        "```yaml\nacceptance_tests:\n  - name: missing test\n    command: pytest tests/missing.py\n```\n"
    )
    assert main(["--workplan", str(workplan), "--check"]) == 0


@pytest.mark.io
def test_contract_no_acceptance_tests_key(tmp_path):
    """Contract with no acceptance_tests key → exit 0 with advisory."""
    workplan = tmp_path / "plan.md"
    workplan.write_text("# Workplan\n")
    contract_dir = tmp_path / "plan"
    contract_dir.mkdir()
    contract = contract_dir / "intent-contract.md"
    contract.write_text("```yaml\nintent: do something useful\nscope:\n  in: [everything]\n```\n")
    assert main(["--workplan", str(workplan)]) == 0


@pytest.mark.io
def test_malformed_yaml_contract(tmp_path):
    """Malformed YAML in contract → exit 0 with warning (no crash)."""
    workplan = tmp_path / "plan.md"
    workplan.write_text("# Workplan\n")
    contract_dir = tmp_path / "plan"
    contract_dir.mkdir()
    contract = contract_dir / "intent-contract.md"
    # Write a raw YAML fence with invalid YAML
    contract.write_text("```yaml\n: ?: ??:\n  - [broken yaml\n```\n")
    assert main(["--workplan", str(workplan)]) == 0


@pytest.mark.io
def test_explicit_contract_path(tmp_path):
    """--contract flag resolves to the explicit path, not the auto-derived one."""
    workplan = tmp_path / "plan.md"
    workplan.write_text("# Workplan\n\n- covers my custom test\n")
    contract = tmp_path / "custom-contract.yml"
    contract.write_text("acceptance_tests:\n  - name: my custom test\n    command: pytest tests/custom.py\n")
    assert main(["--workplan", str(workplan), "--contract", str(contract)]) == 0

"""
tests/test_propose_dogma_edit.py
---------------------------------
Tests for scripts/propose_dogma_edit.py — the programmatic enforcer of the
back-propagation protocol from dogma-neuroplasticity.md.

Covers (D29-D30):
1. load_stability_tiers() — structure, T1 > T3 threshold, T1 requires_adr=True
2. extract_evidence() — watermark detection (hit/miss/empty/case-insensitive)
3. check_coherence() — removal-intent detection (passes False), additive passes True
4. generate_proposal() — output contains required template sections
5. CLI (io) — valid invocation → exit 0 + output file; missing args → non-zero
6. main() — T1 blocking exit 1; T2 non-blocking exit 0
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# Ensure scripts/ is importable for direct function imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from propose_dogma_edit import (  # noqa: E402
    check_coherence,
    enforce_tier_boundaries,
    extract_evidence,
    generate_adr_skeleton,
    generate_proposal,
    load_stability_tiers,
    main,
)

# ===========================================================================
# D29-1: load_stability_tiers() — structure and threshold checks
# ===========================================================================


def test_load_stability_tiers_returns_all_tiers():
    """load_stability_tiers() returns T1, T2, and T3 with all required keys."""
    tiers = load_stability_tiers()
    assert set(tiers.keys()) == {"T1", "T2", "T3"}
    for tier_key, meta in tiers.items():
        assert "name" in meta, f"{tier_key} missing 'name'"
        assert "session_threshold" in meta, f"{tier_key} missing 'session_threshold'"
        assert "requires_adr" in meta, f"{tier_key} missing 'requires_adr'"


def test_t1_threshold_greater_than_t3():
    """T1 session_threshold must be greater than T3 (more evidence required for axioms)."""
    tiers = load_stability_tiers()
    assert tiers["T1"]["session_threshold"] > tiers["T3"]["session_threshold"]


def test_t1_requires_adr_true():
    """T1 requires_adr must be True (formal ADR required for axiom changes)."""
    tiers = load_stability_tiers()
    assert tiers["T1"]["requires_adr"] is True


def test_t3_requires_adr_false():
    """T3 requires_adr must be False (operational constraints need no formal ADR)."""
    tiers = load_stability_tiers()
    assert tiers["T3"]["requires_adr"] is False


# ===========================================================================
# D29-2: extract_evidence() — watermark phrase detection
# ===========================================================================


def test_extract_evidence_finds_watermark_phrase():
    """extract_evidence() returns ≥1 line when text contains a WATERMARK_PHRASE."""
    text = "Governing axiom: Endogenous-First — primary source: MANIFESTO.md\nOther line\n"
    result = extract_evidence(text)
    assert len(result) >= 1
    assert any("Endogenous-First" in line for line in result)


def test_extract_evidence_case_insensitive():
    """extract_evidence() matches watermark phrases case-insensitively."""
    text = "we prefer algorithms before tokens in this workflow\n"
    result = extract_evidence(text)
    assert len(result) >= 1


def test_extract_evidence_empty_input():
    """extract_evidence() returns [] for empty string input."""
    result = extract_evidence("")
    assert result == []


def test_extract_evidence_no_watermarks():
    """extract_evidence() returns [] when no watermark phrases are present."""
    text = "This line has no special keywords.\nAnother irrelevant line.\n"
    result = extract_evidence(text)
    assert result == []


def test_extract_evidence_multiple_phrases():
    """extract_evidence() returns all lines matching any watermark phrase."""
    text = (
        "Endogenous-First is the primary axiom\nThis line is irrelevant\nAlgorithms Before Tokens avoids token waste\n"
    )
    result = extract_evidence(text)
    assert len(result) == 2


# ===========================================================================
# D29-3: check_coherence() — removal-intent sets passes: False
# ===========================================================================


def test_check_coherence_fails_on_remove_watermark():
    """T3 proposal to 'remove endogenous-first' → passes: False."""
    tiers = load_stability_tiers()
    result = check_coherence("T3", "remove endogenous-first from this section", tiers)
    assert result["passes"] is False


def test_check_coherence_fails_with_delete_keyword():
    """T3 proposal to 'delete Algorithms Before Tokens reference' → passes: False."""
    tiers = load_stability_tiers()
    result = check_coherence("T3", "delete Algorithms Before Tokens reference", tiers)
    assert result["passes"] is False


def test_check_coherence_fails_with_drop_keyword():
    """T3 proposal to 'drop the programmatic-first mention' → passes: False."""
    tiers = load_stability_tiers()
    result = check_coherence("T3", "drop the programmatic-first mention", tiers)
    assert result["passes"] is False


# ===========================================================================
# D29-4: check_coherence() — additive proposals pass
# ===========================================================================


def test_check_coherence_passes_additive_proposal():
    """T3 additive proposal with no removal intent → passes: True."""
    tiers = load_stability_tiers()
    result = check_coherence("T3", "Add signal-preservation bullet", tiers)
    assert result["passes"] is True


def test_check_coherence_passes_watermark_without_removal():
    """A proposal mentioning a watermark phrase without removal intent passes."""
    tiers = load_stability_tiers()
    result = check_coherence("T3", "Strengthen Endogenous-First signal in summary", tiers)
    assert result["passes"] is True


def test_check_coherence_returns_required_keys():
    """check_coherence() result contains all required keys."""
    tiers = load_stability_tiers()
    result = check_coherence("T2", "Clarify wording", tiers)
    assert "passes" in result
    assert "session_threshold" in result
    assert "requires_adr" in result
    assert "inheriting_layers" in result


def test_check_coherence_t1_inheriting_layers():
    """T1 inheriting_layers includes both AGENTS.md and agent files."""
    tiers = load_stability_tiers()
    result = check_coherence("T1", "Clarify axiom scope", tiers)
    assert "AGENTS.md" in result["inheriting_layers"]
    assert any("agent" in layer.lower() for layer in result["inheriting_layers"])


def test_check_coherence_t2_inheriting_layers():
    """T2 inheriting_layers contains exactly ['AGENTS.md']."""
    tiers = load_stability_tiers()
    result = check_coherence("T2", "Update principle wording", tiers)
    assert result["inheriting_layers"] == ["AGENTS.md"]


def test_check_coherence_t3_inheriting_layers_empty():
    """T3 inheriting_layers is empty (no downstream layers to audit)."""
    tiers = load_stability_tiers()
    result = check_coherence("T3", "Adjust operational constraint", tiers)
    assert result["inheriting_layers"] == []


def test_check_coherence_session_threshold_matches_tier():
    """check_coherence() session_threshold matches the tier's configured value."""
    tiers = load_stability_tiers()
    for tier_key in ("T1", "T2", "T3"):
        result = check_coherence(tier_key, "some proposal", tiers)
        assert result["session_threshold"] == tiers[tier_key]["session_threshold"]


# ===========================================================================
# D29-5: generate_proposal() — output structure
# ===========================================================================


def test_generate_proposal_contains_required_sections():
    """generate_proposal() output contains all 7 required Markdown sections."""
    tiers = load_stability_tiers()
    coherence = check_coherence("T3", "Add a bullet", tiers)
    output = generate_proposal(
        tier="T3",
        affected_axiom="Focus-on-Descent",
        proposed_delta="Add signal-preservation rules",
        evidence=["- Endogenous-First signal captured in phase 5"],
        coherence=coherence,
        tiers=tiers,
    )
    assert "## Coherence Check" in output
    assert "## Evidence" in output
    assert "## Proposed Text" in output
    assert "**Status**: Proposed" in output
    assert "DEP-DRAFT" in output
    assert "## Current Text" in output
    assert "## Consequences" in output
    assert "## References" in output


def test_generate_proposal_includes_evidence_lines():
    """Evidence lines appear in the proposal output."""
    tiers = load_stability_tiers()
    coherence = check_coherence("T3", "Add a bullet", tiers)
    evidence = ["  Governing axiom: Endogenous-First — observed in phase 5"]
    output = generate_proposal("T3", "MySection", "Some delta", evidence, coherence, tiers)
    assert "Endogenous-First" in output


def test_generate_proposal_no_evidence_fallback():
    """Empty evidence list produces the fallback 'No watermark phrases found' message."""
    tiers = load_stability_tiers()
    coherence = check_coherence("T3", "Add a bullet", tiers)
    output = generate_proposal("T3", "MySection", "Some delta", [], coherence, tiers)
    assert "No watermark phrases found in session file." in output


def test_generate_proposal_includes_tier_name():
    """Output includes the human-readable tier name."""
    tiers = load_stability_tiers()
    coherence = check_coherence("T1", "Clarify axiom", tiers)
    output = generate_proposal("T1", "Endogenous-First", "Add caveat", [], coherence, tiers)
    assert "Axioms" in output


def test_generate_proposal_coherence_result_in_output():
    """Coherence 'Fails' is surfaced in output when check does not pass."""
    tiers = load_stability_tiers()
    coherence = check_coherence("T3", "remove programmatic-first", tiers)
    assert coherence["passes"] is False
    output = generate_proposal("T3", "SomeSection", "remove programmatic-first", [], coherence, tiers)
    assert "Fails" in output


# ===========================================================================
# D29-6: @pytest.mark.io — CLI integration (success path)
# ===========================================================================


@pytest.mark.io
@pytest.mark.integration
def test_cli_success_path(tmp_path):
    """CLI: valid args with T3 tier → exit 0 and output file created with '## Coherence Check'."""
    session_file = tmp_path / "session.md"
    session_file.write_text(
        "## Reflection\nGoverning axiom: Endogenous-First — noted in phase 5.\n",
        encoding="utf-8",
    )
    out_file = tmp_path / "proposal.md"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/propose_dogma_edit.py",
            "--input",
            str(session_file),
            "--tier",
            "T3",
            "--affected-axiom",
            "Focus-on-Descent",
            "--proposed-delta",
            "Add signal-preservation bullet",
            "--output",
            str(out_file),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0; got {result.returncode}.\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert out_file.exists(), "Output file was not created"
    content = out_file.read_text(encoding="utf-8")
    assert "## Coherence Check" in content


@pytest.mark.io
@pytest.mark.integration
def test_cli_success_with_real_session_file(tmp_path):
    """CLI: real session file at .tmp/feat-value-encoding-fidelity/2026-03-09.md → exit 0.

    Opt-in only: set TEST_WITH_REAL_SESSION=1 to run. The .tmp/ directory is
    gitignored and environment-specific, so this test is skipped by default in
    CI and on machines without the specific session file.
    """
    import os

    if not os.environ.get("TEST_WITH_REAL_SESSION"):
        pytest.skip("Set TEST_WITH_REAL_SESSION=1 to enable this test")
    session_path = Path(".tmp/feat-value-encoding-fidelity/2026-03-09.md")
    if not session_path.exists():
        pytest.skip("Real session file not available in this environment")
    out_file = tmp_path / "real-proposal.md"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/propose_dogma_edit.py",
            "--input",
            str(session_path),
            "--tier",
            "T3",
            "--affected-axiom",
            "Focus-on-Descent",
            "--proposed-delta",
            "Add signal-preservation bullet",
            "--output",
            str(out_file),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert out_file.exists()
    assert "## Coherence Check" in out_file.read_text(encoding="utf-8")


# ===========================================================================
# D29-7: @pytest.mark.io — CLI integration (missing required args → non-zero)
# ===========================================================================


@pytest.mark.io
@pytest.mark.integration
def test_cli_missing_tier_arg():
    """CLI: missing required --tier arg → non-zero exit."""
    result = subprocess.run(
        [
            sys.executable,
            "scripts/propose_dogma_edit.py",
            "--input",
            "nonexistent.md",
            "--affected-axiom",
            "SomeAxiom",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


@pytest.mark.io
@pytest.mark.integration
def test_cli_missing_input_arg():
    """CLI: missing required --input arg → non-zero exit."""
    result = subprocess.run(
        [
            sys.executable,
            "scripts/propose_dogma_edit.py",
            "--tier",
            "T3",
            "--affected-axiom",
            "SomeAxiom",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


@pytest.mark.io
@pytest.mark.integration
def test_cli_missing_affected_axiom_arg():
    """CLI: missing required --affected-axiom arg → non-zero exit."""
    result = subprocess.run(
        [
            sys.executable,
            "scripts/propose_dogma_edit.py",
            "--tier",
            "T3",
            "--input",
            "nonexistent.md",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


# ===========================================================================
# main() — exit code contract
# ===========================================================================


@pytest.mark.io
def test_main_returns_1_when_t1_coherence_fails(tmp_path):
    """main() returns 1 when T1 coherence fails (watermark removal detected)."""
    session_file = tmp_path / "session.md"
    session_file.write_text("## Reflection\nNo special content here.\n", encoding="utf-8")
    out_file = tmp_path / "out.md"
    ret = main(
        [
            "--input",
            str(session_file),
            "--tier",
            "T1",
            "--affected-axiom",
            "Endogenous-First",
            "--proposed-delta",
            "remove endogenous-first from axiom list",
            "--output",
            str(out_file),
        ]
    )
    assert ret == 1


@pytest.mark.io
def test_main_returns_0_when_t2_coherence_fails(tmp_path):
    """main() returns 0 (not blocking) when T2 coherence fails — only T1 is blocking."""
    session_file = tmp_path / "session.md"
    session_file.write_text("## Reflection\nNo special content here.\n", encoding="utf-8")
    out_file = tmp_path / "out.md"
    ret = main(
        [
            "--input",
            str(session_file),
            "--tier",
            "T2",
            "--affected-axiom",
            "SomePrinciple",
            "--proposed-delta",
            "delete programmatic-first principle",
            "--output",
            str(out_file),
        ]
    )
    assert ret == 0


def test_main_returns_1_on_unreadable_input_file():
    """main() returns 1 when the session file cannot be read."""
    ret = main(
        [
            "--input",
            "/nonexistent/path/session.md",
            "--tier",
            "T3",
            "--affected-axiom",
            "SomeSection",
            "--proposed-delta",
            "Add a note",
        ]
    )
    assert ret == 1


@pytest.mark.io
def test_main_returns_0_on_successful_run(tmp_path):
    """main() returns 0 on a clean T3 run with a valid session file."""
    session_file = tmp_path / "session.md"
    session_file.write_text("## Reflection\nGoverning axiom: Endogenous-First\n", encoding="utf-8")
    out_file = tmp_path / "out.md"
    ret = main(
        [
            "--input",
            str(session_file),
            "--tier",
            "T3",
            "--affected-axiom",
            "Focus-on-Descent",
            "--proposed-delta",
            "Add signal-preservation bullet",
            "--output",
            str(out_file),
        ]
    )
    assert ret == 0
    assert out_file.exists()


# ===========================================================================
# Tests for enforce_tier_boundaries() — NEW in #121
# ===========================================================================


def test_enforce_tier_boundaries_t1_valid_axiom():
    """T1 accepts edits to core axioms (Endogenous-First, etc)."""
    tiers = load_stability_tiers()
    passes, reason = enforce_tier_boundaries("T1", "Endogenous-First", tiers)
    assert passes is True
    assert "respected" in reason.lower()


def test_enforce_tier_boundaries_t1_invalid_operational():
    """T1 rejects edits to non-axiom sections."""
    tiers = load_stability_tiers()
    passes, reason = enforce_tier_boundaries("T1", "Operational constraint", tiers)
    assert passes is False
    assert "axioms" in reason.lower()


def test_enforce_tier_boundaries_t1_algorithms_before_tokens():
    """T1 accepts 'Algorithms Before Tokens' axiom."""
    tiers = load_stability_tiers()
    passes, reason = enforce_tier_boundaries("T1", "Algorithms Before Tokens", tiers)
    assert passes is True


def test_enforce_tier_boundaries_t2_valid_principle():
    """T2 accepts edits to guiding principles."""
    tiers = load_stability_tiers()
    passes, reason = enforce_tier_boundaries("T2", "Guiding principle: Documentation first", tiers)
    assert passes is True


def test_enforce_tier_boundaries_t2_rejects_axiom():
    """T2 rejects edits to axioms."""
    tiers = load_stability_tiers()
    passes, reason = enforce_tier_boundaries("T2", "Endogenous-First", tiers)
    assert passes is False


def test_enforce_tier_boundaries_t3_valid_operational():
    """T3 accepts operational constraints."""
    tiers = load_stability_tiers()
    passes, reason = enforce_tier_boundaries("T3", "Phase-Gate-Sequence", tiers)
    assert passes is True


def test_enforce_tier_boundaries_t3_rejects_axiom():
    """T3 rejects axiom edits."""
    tiers = load_stability_tiers()
    passes, reason = enforce_tier_boundaries("T3", "Local Compute-First", tiers)
    assert passes is False
    assert "axioms" in reason.lower()


def test_enforce_tier_boundaries_t3_rejects_algorithms_axiom():
    """T3 rejects Algorithms Before Tokens axiom."""
    tiers = load_stability_tiers()
    passes, reason = enforce_tier_boundaries("T3", "Algorithms Before Tokens", tiers)
    assert passes is False


# ===========================================================================
# Tests for generate_adr_skeleton() — NEW in #121
# ===========================================================================


def test_generate_adr_skeleton_has_required_sections():
    """ADR skeleton contains all required sections."""
    tiers = load_stability_tiers()
    adr = generate_adr_skeleton("T1", "Endogenous-First", tiers)
    assert "# ADR-NNN:" in adr
    assert "## Context" in adr
    assert "## Decision" in adr
    assert "## Consequences" in adr
    assert "## References" in adr


def test_generate_adr_skeleton_includes_tier_info():
    """ADR skeleton includes tier level and name."""
    tiers = load_stability_tiers()
    adr = generate_adr_skeleton("T2", "My Principle", tiers)
    assert "T2" in adr
    assert "Guiding Principles" in adr


def test_generate_adr_skeleton_t1_metadata():
    """T1 ADR skeleton includes T1-specific metadata."""
    tiers = load_stability_tiers()
    adr = generate_adr_skeleton("T1", "Endogenous-First", tiers)
    assert "Axioms" in adr
    assert "3" in adr  # T1 session threshold


def test_generate_adr_skeleton_t3_metadata():
    """T3 ADR skeleton includes T3-specific metadata."""
    tiers = load_stability_tiers()
    adr = generate_adr_skeleton("T3", "Operation", tiers)
    assert "Operational Constraints" in adr
    assert "2" in adr  # T3 session threshold


def test_generate_adr_skeleton_requires_adr_field():
    """ADR skeleton mentions the requires_adr tier field."""
    tiers = load_stability_tiers()
    adr = generate_adr_skeleton("T1", "Test", tiers)
    assert "requires adr" in adr.lower()  # Note: with space, not underscore


# ===========================================================================
# Tests for main() with --output-adr — NEW in #121
# ===========================================================================


@pytest.mark.io
def test_main_output_adr_flag(tmp_path):
    """main() with --output-adr creates an ADR skeleton file."""
    session_file = tmp_path / "session.md"
    session_file.write_text("## Session Start\nGoverning axiom test\n", encoding="utf-8")
    adr_file = tmp_path / "adr.md"

    ret = main(
        [
            "--input",
            str(session_file),
            "--tier",
            "T2",
            "--affected-axiom",
            "Test Principle",
            "--proposed-delta",
            "Add clarification",
            "--output-adr",
            str(adr_file),
        ]
    )

    assert ret == 0
    assert adr_file.exists()
    adr_content = adr_file.read_text()
    assert "ADR-NNN" in adr_content
    assert "## Consequences" in adr_content


@pytest.mark.io
def test_main_output_and_adr_together(tmp_path):
    """main() creates both proposal and ADR when both flags are used."""
    session_file = tmp_path / "session.md"
    session_file.write_text("## Session Start\nGoverning axiom test\n", encoding="utf-8")
    proposal_file = tmp_path / "proposal.md"
    adr_file = tmp_path / "adr.md"

    ret = main(
        [
            "--input",
            str(session_file),
            "--tier",
            "T1",
            "--affected-axiom",
            "Endogenous-First",
            "--proposed-delta",
            "Clarify scope",
            "--output",
            str(proposal_file),
            "--output-adr",
            str(adr_file),
        ]
    )

    assert ret == 0
    assert proposal_file.exists()
    assert adr_file.exists()
    assert "DEP-DRAFT" in proposal_file.read_text()
    assert "ADR-NNN" in adr_file.read_text()


# ===========================================================================
# Tests for tier boundary enforcement in main() — NEW in #121
# ===========================================================================


def test_main_tier_violation_returns_1(tmp_path):
    """main() returns 1 when tier boundary is violated."""
    session_file = tmp_path / "session.md"
    session_file.write_text("test", encoding="utf-8")

    ret = main(
        [
            "--input",
            str(session_file),
            "--tier",
            "T1",
            "--affected-axiom",
            "Operational constraint",
            "--proposed-delta",
            "Change",
        ]
    )

    assert ret == 1


def test_main_parse_error_returns_2(tmp_path):
    """main() returns 2 on argument parse error."""
    session_file = tmp_path / "session.md"
    session_file.write_text("test", encoding="utf-8")

    # Invalid tier value
    ret = main(
        [
            "--input",
            str(session_file),
            "--tier",
            "INVALID",
            "--affected-axiom",
            "Test",
            "--proposed-delta",
            "Change",
        ]
    )

    assert ret == 2


def test_main_missing_input_file_returns_2():
    """main() returns 1 when input file cannot be read (I/O error)."""
    ret = main(
        [
            "--input",
            "/nonexistent/file.md",
            "--tier",
            "T1",
            "--affected-axiom",
            "Endogenous-First",
            "--proposed-delta",
            "Change",
        ]
    )

    assert ret == 1

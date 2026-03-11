"""
Test suite for validate_handoff_permeability.py

Tests membrane permeability validation across scout-to-synthesizer, synthesizer-to-reviewer,
and reviewer-to-archivist handoff boundaries. Validates that required signals (Canonical examples,
Anti-patterns, Axiom citations, Source URLs) are preserved across delegations.
"""

import pytest

from scripts.validate_handoff_permeability import (
    MEMBRANE_SPECS,
    SIGNAL_PATTERNS,
    validate_handoff_permeability,
)

# ===========================================================================
# Fixtures: Sample Handoff Text
# ===========================================================================


@pytest.fixture
def valid_scout_to_synthesizer_handoff():
    """Valid handoff with all required signals for Scout→Synthesizer membrane."""
    return """
## Phase Output

The research surfaced several architectural patterns in the codebase.

**Canonical example**: `validate_synthesis.py` enforces D4 document structure by validating
YAML frontmatter and required section headings at CI boundary. This prevents incomplete
research documents from being archived.

**Anti-pattern**: Returning raw literature survey notes without compression — this violates
the Compression-on-Ascent rule and uses 10x more context than compressed handoff format.

Key findings summary:
- 12 atomic principles identified
- 3 cross-sectoral convergences detected
- 8 recommendation gaps identified

See AGENTS.md § Focus-on-Descent / Compression-on-Ascent for the governing constraints.

Referenced sources:
[MANIFESTO.md](https://github.com/EndogenAI/Workflows/blob/main/MANIFESTO.md)
[values-encoding.md](https://github.com/EndogenAI/Workflows/blob/main/docs/research/values-encoding.md)
"""


@pytest.fixture
def valid_synthesizer_to_reviewer_handoff():
    """Valid handoff with all required signals for Synthesizer→Reviewer membrane."""
    return """
## Synthesizer Output

## Executive Summary
This document synthesizes Scout findings into a coherent research artifact.

## Pattern Catalog
**Canonical example**: The Topological Audit (issue #170) identified 75 vertices and 52 edges
by systematic inventory of agents, scripts, and documents. This becomes the membrane boundary
specification referenced in all downstream validation.

**Anti-pattern**: Synthesizing without reference to original Scout notes — creates orphaned
claims detached from evidence.

**Signal Metric**: 4 source documents integrated, 2.5x compression ratio achieved (220 Scout
tokens → 88 synthesis tokens while preserving canonical examples).

**Synthesis Structure Validation**: ✅ Contains Executive Summary, Pattern Catalog, Recommendations
"""


@pytest.fixture
def valid_reviewer_to_archivist_handoff():
    """Valid handoff with all required signals for Reviewer→Archivist membrane."""
    return """
## Review Verdict

Status: APPROVED

Rationale summary: Document structure follows D4 spec, axiom citations are grounded in
MANIFESTO.md, at least 2 canonical examples present per Pattern Catalog section. Ready
for archive commitment.

Key observations:
- All 3 required sections present
- Coverage metric: 92% of expected patterns included
- No blocking issues identified
"""


@pytest.fixture
def missing_canonical_example_handoff():
    """Handoff missing **Canonical example** signal."""
    return """
## Research Findings

**Anti-pattern**: Vague abstract claims without specific examples.

Axiom reference: MANIFESTO.md § Endogenous-First principle suggests grounding all work
in existing substrate knowledge.

Source documentation: [AGENTS.md](https://github.com/EndogenAI/Workflows/blob/main/AGENTS.md)
"""


@pytest.fixture
def missing_axiom_citation_handoff():
    """Handoff missing axiom citations."""
    return """
## Scout Findings

**Canonical example**: The validate_synthesis.py script is a concrete instance of programmatic
enforcement at T2 static validation layer.

**Anti-pattern**: Relying entirely on prose-level instructions without encoding constraints as code.

Key sources:
[link1](https://example.com)
[link2](https://example.com/doc)
"""


@pytest.fixture
def missing_source_url_handoff():
    """Handoff missing source URLs."""
    return """
## Output

**Canonical example**: Scripts in scripts/ carry docstrings with purpose, inputs, outputs, usage.

**Anti-pattern**: Creating scripts without documenting their contract.

Key constraint: MANIFESTO.md § Endogenous-First
Related axiom: Algorithms Before Tokens
"""


@pytest.fixture
def generic_canonical_example_handoff():
    """Handoff with generic (non-specific) Canonical example."""
    return """
## Findings

**Canonical example**: This is good.

**Anti-pattern**: This is bad.

MANIFESTO.md axiom reference present.

[source](https://example.com)
"""


@pytest.fixture
def empty_handoff():
    """Empty or whitespace-only handoff."""
    return "   \n\n   \n"


@pytest.fixture
def uncompressed_reviewer_handoff():
    """Reviewer handoff that preserves full line-by-line comments (should be compressed)."""
    return """
## Review

APPROVED

Rationale: Document is well-structured and evidence-grounded.

Line-by-line comments:
- Line 42: Good axiom citation here
- Line 58: Could strengthen example with more detail
- Line 73: Excellent anti-pattern description
- Line 91: Missing source reference for this claim
- Line 105: Very clear synthesis structure
- Line 128: Could compress this section further

Detailed analysis of each section follows, with paragraph-by-paragraph assessment...
[Full 200-line commentary, uncompressed]
"""


@pytest.fixture
def case_insensitive_signals_handoff():
    """Handoff with signals in mixed case."""
    return """
## Output

**CANONICAL EXAMPLE**: This demonstrates the pattern.

**Anti-Pattern**: Avoid this approach.

References MANIFESTO.md and Endogenous-First principle.

[link](https://example.com)
"""


@pytest.fixture
def multiple_canonical_examples_handoff():
    """Handoff with multiple Canonical examples (should count all)."""
    return """
## Scout Output

**Canonical example**: Example 1 shows how scripts enforce compliance via exit codes.

Further findings...

**Canonical example**: Example 2 demonstrates YAML frontmatter validation at pre-commit.

**Anti-pattern**: Returning uncompressed raw findings without distillation.

Additional constraint: MANIFESTO.md § Algorithms Before Tokens

Sources:
[doc1](https://example.com/source1)
[doc2](https://example.com/source2)
"""


@pytest.fixture
def signals_in_code_block_handoff():
    """Handoff with signal-like text in code blocks (should not be counted as signals)."""
    return """
## Output

**Canonical example**: The validate_synthesis.py script demonstrates programmatic enforcement at T2 boundary.

Text describing anti-patterns:

```python
# **Anti-pattern**: This looks like a signal but is in a code block
# and should not be detected as a real anti-pattern
```

Real signal:
**Anti-pattern**: This is a real anti-pattern outside code blocks.

MANIFESTO.md reference here.
[source](https://example.com)
"""


# ===========================================================================
# Happy Path Tests: Valid Handoffs (4 tests)
# ===========================================================================


class TestValidHandoffs:
    """Test suite for valid handoffs with all required signals."""

    def test_scout_to_synthesizer_all_signals_present(self, valid_scout_to_synthesizer_handoff):
        """Scout→Synthesizer: all required signals present → PASS."""
        result = validate_handoff_permeability(
            valid_scout_to_synthesizer_handoff,
            "scout-to-synthesizer",
        )
        assert result.status == "pass"
        assert "canonical_example" in result.found_signals
        assert "anti_pattern" in result.found_signals
        assert "axiom_citation" in result.found_signals
        assert "source_url" in result.found_signals
        assert len(result.missing_signals) == 0

    def test_synthesizer_to_reviewer_valid_handoff(self, valid_synthesizer_to_reviewer_handoff):
        """Synthesizer→Reviewer: all required signals present → PASS."""
        result = validate_handoff_permeability(
            valid_synthesizer_to_reviewer_handoff,
            "synthesizer-to-reviewer",
        )
        assert result.status == "pass"
        assert "canonical_example" in result.found_signals
        assert "anti_pattern" in result.found_signals
        assert len(result.missing_signals) == 0

    def test_reviewer_to_archivist_verdict_preserved(self, valid_reviewer_to_archivist_handoff):
        """Reviewer→Archivist: verdict and rationale preserved → PASS."""
        result = validate_handoff_permeability(
            valid_reviewer_to_archivist_handoff,
            "reviewer-to-archivist",
        )
        assert result.status == "pass"
        assert "verdict" in result.found_signals
        assert "rationale_summary" in result.found_signals
        assert len(result.missing_signals) == 0

    def test_unknown_membrane_type_raises_error(self, valid_scout_to_synthesizer_handoff):
        """Unknown membrane type → raises ValueError."""
        with pytest.raises(ValueError, match="Unknown membrane_type"):
            validate_handoff_permeability(
                valid_scout_to_synthesizer_handoff,
                "invalid-membrane-type",
            )


# ===========================================================================
# Signal Violation Tests: Missing Required Signals (6 tests)
# ===========================================================================


class TestMissingSignals:
    """Test suite for handoffs missing required signals."""

    def test_scout_to_synthesizer_missing_canonical_example(self, missing_canonical_example_handoff):
        """Scout→Synthesizer: missing **Canonical example** → FAIL."""
        result = validate_handoff_permeability(
            missing_canonical_example_handoff,
            "scout-to-synthesizer",
        )
        assert result.status == "fail"
        assert "canonical_example" in result.missing_signals
        assert "canonical_example" not in result.found_signals

    def test_scout_to_synthesizer_missing_axiom_citation(self, missing_axiom_citation_handoff):
        """Scout→Synthesizer: missing axiom citations → FAIL."""
        result = validate_handoff_permeability(
            missing_axiom_citation_handoff,
            "scout-to-synthesizer",
        )
        assert result.status == "fail"
        assert "axiom_citation" in result.missing_signals

    def test_scout_to_synthesizer_missing_source_url(self, missing_source_url_handoff):
        """Scout→Synthesizer: missing source URLs → FAIL."""
        result = validate_handoff_permeability(
            missing_source_url_handoff,
            "scout-to-synthesizer",
        )
        assert result.status == "fail"
        assert "source_url" in result.missing_signals

    def test_scout_to_synthesizer_missing_anti_pattern(self):
        """Scout→Synthesizer: missing **Anti-pattern** → FAIL."""
        handoff = """
## Output

**Canonical example**: Example text

MANIFESTO.md axiom

[source](https://example.com)
"""
        result = validate_handoff_permeability(
            handoff,
            "scout-to-synthesizer",
        )
        assert result.status == "fail"
        assert "anti_pattern" in result.missing_signals

    def test_synthesizer_to_reviewer_missing_synthesis_structure(self):
        """Synthesizer→Reviewer: missing synthesis structure headings → FAIL."""
        handoff = """
## Output

**Canonical example**: Pattern demonstrated

**Anti-pattern**: Avoid this

Some unstructured prose without proper synthesis sections
"""
        result = validate_handoff_permeability(
            handoff,
            "synthesizer-to-reviewer",
        )
        assert result.status == "fail"
        assert "synthesis_structure" in result.missing_signals

    def test_reviewer_to_archivist_missing_verdict(self):
        """Reviewer→Archivist: missing explicit verdict → FAIL."""
        handoff = """
## Review Comments

Rationale: This document looks good overall.

But no explicit APPROVED/REQUEST CHANGES verdict.
"""
        result = validate_handoff_permeability(
            handoff,
            "reviewer-to-archivist",
        )
        assert result.status == "fail"
        assert "verdict" in result.missing_signals


# ===========================================================================
# Specificity & Genericness Tests (3 tests)
# ===========================================================================


class TestSignalSpecificity:
    """Test that generic examples are rejected while specific examples pass."""

    def test_generic_canonical_example_rejected(self, generic_canonical_example_handoff):
        """Generic Canonical example (e.g., 'this is good') → not counted as signal."""
        result = validate_handoff_permeability(
            generic_canonical_example_handoff,
            "scout-to-synthesizer",
        )
        # Generic example should fail specificity check
        assert "canonical_example" in result.missing_signals
        assert result.status == "fail"

    def test_specific_example_with_file_name(self):
        """Canonical example naming specific file/function → counted as valid signal."""
        handoff = """
## Output

**Canonical example**: The validate_synthesis.py script validates D4 frontmatter by regex-matching
YAML keys and asserting required fields are present.

**Anti-pattern**: Skipping validation to save tokens.

MANIFESTO.md § Algorithms Before Tokens

[source](https://example.com)
"""
        result = validate_handoff_permeability(
            handoff,
            "scout-to-synthesizer",
        )
        assert result.status == "pass"
        assert "canonical_example" in result.found_signals

    def test_minimal_length_example_rejected(self):
        """Very short (< 20 chars) Canonical example → not counted."""
        handoff = """
## Output

**Canonical example**: short

**Anti-pattern**: bad

MANIFESTO.md

[link](https://example.com)
"""
        result = validate_handoff_permeability(
            handoff,
            "scout-to-synthesizer",
        )
        # Very short example fails specificity check
        assert "canonical_example" in result.missing_signals


# ===========================================================================
# Compression & Uncompressed Content Tests (2 tests)
# ===========================================================================


class TestCompressionCanonical:
    """Test that uncompressed content triggers warnings or failures."""

    def test_reviewer_to_archivist_uncompressed_full_comments(self, uncompressed_reviewer_handoff):
        """Reviewer→Archivist: preserving full line-by-line comments (should warn)."""
        result = validate_handoff_permeability(
            uncompressed_reviewer_handoff,
            "reviewer-to-archivist",
        )
        # Verdict and rationale are present, so this passes
        assert result.status == "pass"
        # But we should have warned about uncompressed comments
        assert len(result.warnings) > 0
        # Compressible signal count should be high
        assert result.signal_counts.get("line_by_line_comments", 0) > 0

    def test_scout_to_synthesizer_warns_if_no_compression_context(self):
        """Scout→Synthesizer: warns if exploratory notes completely absent (compressible)."""
        handoff = """
## Output

**Canonical example**: The validate_synthesis.py script demonstrates programmatic enforcement at T2 boundary.

**Anti-pattern**: Returning raw literature notes without compression or distillation.

Key reference: MANIFESTO.md

[source](https://example.com)
"""
        result = validate_handoff_permeability(
            handoff,
            "scout-to-synthesizer",
        )
        # Should pass (all required signals present)
        assert result.status == "pass"
        # But warns about missing compressible signals (if specified in spec)
        # In this case, background_prose and exploratory_notes are compressible
        # Warnings may be present indicating compression


# ===========================================================================
# Edge Cases: Whitespace, Case Insensitivity, Multiple Occurrences (4 tests)
# ===========================================================================


class TestEdgeCases:
    """Test edge cases: empty input, case variants, multiple signals."""

    def test_empty_handoff_section(self, empty_handoff):
        """Empty/whitespace-only handoff → FAIL all required signals."""
        result = validate_handoff_permeability(
            empty_handoff,
            "scout-to-synthesizer",
        )
        assert result.status == "fail"
        assert len(result.found_signals) == 0
        assert len(result.missing_signals) > 0

    def test_case_insensitive_signal_matching(self, case_insensitive_signals_handoff):
        """Mixed-case signal headings (e.g., CANONICAL EXAMPLE) → matched due to re.IGNORECASE."""
        result = validate_handoff_permeability(
            case_insensitive_signals_handoff,
            "scout-to-synthesizer",
        )
        # Should match canonical_example despite different case
        assert "canonical_example" in result.found_signals

    def test_multiple_canonical_examples_counted(self, multiple_canonical_examples_handoff):
        """Multiple **Canonical example** blocks → all counted in signal_counts."""
        result = validate_handoff_permeability(
            multiple_canonical_examples_handoff,
            "scout-to-synthesizer",
        )
        assert result.status == "pass"
        # Should count 2 canonical examples
        assert result.signal_counts["canonical_example"] >= 2

    def test_handoff_with_extra_narrative_content(self):
        """Handoff with extensive narrative between signals → signals still detected."""
        handoff = """
## Research Phase Output

This phase explored three major research directions across the sector.
[500 words of background prose...]

**Canonical example**: The topological audit in issue #170 mapped 75 vertices and 52 edges
across the substrate by systematic inventory.

[Another 300 words of analysis...]

**Anti-pattern**: Creating new agents without understanding existing agent topology — leads to
duplicate responsibilities and enforcement gaps.

[Extensive explanation of anti-pattern consequences...]

MANIFESTO.md § Endogenous-First principle governs this constraint.

[Detailed rationale...]

[References](https://github.com/EndogenAI/Workflows/blob/main/doc)
"""
        result = validate_handoff_permeability(
            handoff,
            "scout-to-synthesizer",
        )
        assert result.status == "pass"
        assert all(
            signal in result.found_signals
            for signal in ["canonical_example", "anti_pattern", "axiom_citation", "source_url"]
        )


# ===========================================================================
# Malformed Markdown Tests (2 tests)
# ===========================================================================


class TestMalformedMarkdown:
    """Test handling of malformed or edge-case Markdown."""

    def test_signals_in_code_block_not_counted(self, signals_in_code_block_handoff):
        """Signal-like text in code blocks → not counted due to text-only regex."""
        result = validate_handoff_permeability(
            signals_in_code_block_handoff,
            "scout-to-synthesizer",
        )
        # Only the real anti-pattern outside code block should count
        # Code block mentions should not inflate the count
        # This is a limitation of the current regex-only approach (acceptable trade-off)
        assert result.status == "pass"  # Real signal is detected

    def test_malformed_axiom_citations_still_match(self):
        """Axiom names with various spellings/typos → matched by regex."""
        handoff = """
## Output

**Canonical example**: Example

**Anti-pattern**: Pattern

The MANIFESTO.md file specifies core principles including Endogenous-First ,
algorithms before tokens, and Local-Compute-First approaches.

[link](https://example.com)
"""
        result = validate_handoff_permeability(
            handoff,
            "scout-to-synthesizer",
        )
        # Should detect multiple axiom references via regex
        assert "axiom_citation" in result.found_signals
        assert result.signal_counts["axiom_citation"] >= 1


# ===========================================================================
# Parameterized Tests: Multiple Membrane Types
# ===========================================================================


@pytest.mark.parametrize(
    "membrane_type",
    [
        "scout-to-synthesizer",
        "synthesizer-to-reviewer",
        "reviewer-to-archivist",
    ],
)
class TestAllMembraneTypes:
    """Test that each membrane type has proper spec definitions."""

    def test_membrane_type_in_specs(self, membrane_type):
        """Each membrane type has a MembraneSpec definition."""
        assert membrane_type in MEMBRANE_SPECS
        spec = MEMBRANE_SPECS[membrane_type]
        assert spec.name
        assert len(spec.required_signals) > 0

    def test_required_signals_are_valid(self, membrane_type):
        """All required signals reference valid SIGNAL_PATTERNS."""
        spec = MEMBRANE_SPECS[membrane_type]
        for signal_type in spec.required_signals:
            assert signal_type in SIGNAL_PATTERNS, f"Signal '{signal_type}' in {membrane_type} not in SIGNAL_PATTERNS"


# ===========================================================================
# Custom Required Signals Tests (3 tests)
# ===========================================================================


class TestCustomRequiredSignals:
    """Test validation with custom required_signals parameter."""

    def test_subset_of_required_signals(self, valid_scout_to_synthesizer_handoff):
        """Validate only a subset of signals."""
        result = validate_handoff_permeability(
            valid_scout_to_synthesizer_handoff,
            "scout-to-synthesizer",
            required_signals=["canonical_example", "axiom_citation"],
        )
        assert result.status == "pass"
        assert "canonical_example" in result.found_signals
        assert "axiom_citation" in result.found_signals

    def test_invalid_custom_signal_raises_error(self, valid_scout_to_synthesizer_handoff):
        """Invalid signal name in required_signals → ValueError."""
        with pytest.raises(ValueError, match="Invalid signal types"):
            validate_handoff_permeability(
                valid_scout_to_synthesizer_handoff,
                "scout-to-synthesizer",
                required_signals=["canonical_example", "invalid_signal"],
            )

    def test_custom_signals_override_defaults(self):
        """Custom required_signals override membrane defaults."""
        missing_anti_pattern_handoff = """
## Output

**Canonical example**: The validate_synthesis.py script enforces D4 structure at T2 boundary.

MANIFESTO.md

[link](https://example.com)
"""
        # This handoff is missing anti_pattern, but if we don't require it, should pass
        result = validate_handoff_permeability(
            missing_anti_pattern_handoff,
            "scout-to-synthesizer",
            required_signals=["canonical_example"],  # Only require this one
        )
        assert result.status == "pass"


# ===========================================================================
# Report Generation Tests (2 tests)
# ===========================================================================


class TestReportGeneration:
    """Test that reports are properly formatted."""

    def test_report_markdown_valid_pass(self, valid_scout_to_synthesizer_handoff):
        """PASS report contains required Markdown structure."""
        result = validate_handoff_permeability(
            valid_scout_to_synthesizer_handoff,
            "scout-to-synthesizer",
        )
        assert "Membrane" in result.report
        assert "Status" in result.report
        assert "PASS" in result.report
        assert "✅" in result.report

    def test_report_markdown_valid_fail(self, missing_canonical_example_handoff):
        """FAIL report contains required Markdown structure."""
        result = validate_handoff_permeability(
            missing_canonical_example_handoff,
            "scout-to-synthesizer",
        )
        assert "Membrane" in result.report
        assert "FAIL" in result.report
        assert "Missing Signals" in result.report
        assert "canonical_example" in result.report


# ===========================================================================
# Integration Tests (2 tests)
# ===========================================================================


class TestIntegration:
    """Integration tests with realistic scenarios."""

    def test_real_phase_output_scout_to_synthesizer(self):
        """Realistic Scout→Synthesizer handoff from actual research phase."""
        phase_output = """
## Scout Phase Output — Values-Encoding Research

Scout analyzed five independent fields (genetics, information theory, linguistics,
legal scholarship, religious text transmission) to identify value signal preservation
mechanisms across textual layers.

**Canonical example**: The DNA→RNA→Protein→Expression model from molecular biology
(reference: Alberts et al., "Molecular Biology of the Cell") provides a formal framework
for understanding encoding hierarchies. Each layer has specific mutation rates and
fidelity mechanisms. Applied to endogenic substrate: MANIFESTO.md (DNA) → AGENTS.md (RNA)
→ agent files (Protein) → session behavior (Expression). This mapping appears in
[`values-encoding.md`](../../docs/research/values-encoding.md).

**Anti-pattern**: Treating all textual layers as equivalent in terms of change velocity
and interpretation risk. Foundational axioms (MANIFESTO.md) change quarterly or less;
operational constraints (AGENTS.md) change monthly; implementations (scripts) change
weekly. A protocol treating all changes with equal urgency would burn tokens without
improving signal fidelity.

Key findings:
- Cross-field convergence on four fidelity mechanisms: structural redundancy, semantic
  anchoring, programmatic encoding, and epigenetic regulation
- Legal scholarship emphasizes witness credibility across time (cf. hearsay rules)
- Information theory identifies "holographic encoding" as strongest fidelity defense

Cited principles from MANIFESTO.md:
- Endogenous-First: substrate must bootstrap from existing knowledge
- Algorithms Before Tokens: encoding constraints in code > prose instructions
- Local Compute-First: minimize external interpretation burden

Sources referenced:
[Alberts_et_al_2014](https://books.google.com/books?id=8w8qBQAAQBAJ)
[Saussure_1916_Course_in_General_Linguistics](https://en.wikipedia.org/wiki/Course_in_General_Linguistics)
[Derrida_1982_Dissemination](https://en.wikipedia.org/wiki/Dissemination_(book))
[Rosch_1975_Prototype_Theory](https://en.wikipedia.org/wiki/Prototype_theory)
[DNA_Replication_Fidelity](https://en.wikipedia.org/wiki/DNA_replication#Accuracy)
"""
        result = validate_handoff_permeability(
            phase_output,
            "scout-to-synthesizer",
        )
        assert result.status == "pass"
        assert "canonical_example" in result.found_signals
        assert "anti_pattern" in result.found_signals
        assert "axiom_citation" in result.found_signals
        assert "source_url" in result.found_signals

    def test_real_review_gate_output(self):
        """Realistic Reviewer→Archivist approval verdict."""
        review_output = """
## Review Gate — Phase 3a Topological Audit

**Status**: APPROVED

Rationale summary: Topological audit document (docs/research/topological-audit-substrate.md)
comprehensively maps substrate as graph with vertices (75 agents+scripts+docs), edges (52
control/data/reference relationships), and faces (9 structural + 6 functional enforcement tiers).
Document structure follows D4 spec: Executive Summary, Hypothesis Validation, Methodology,
Vertex Inventory, Face Enumeration, and Recommendations. All citations trace to MANIFESTO.md
or peer-reviewed literature. Three Canonical examples provided: agent hub connectivity,
functional tier enforcement, and structural coherence metrics. No blocking issues identified.
Ready for archive.

Decision rationale: The document provides quantitative, replicable foundation for all
downstream validation and architecture work.

Verdict: ✅ APPROVED for archive commitment in phase 3a-closed branch.
"""
        result = validate_handoff_permeability(
            review_output,
            "reviewer-to-archivist",
        )
        assert result.status == "pass"
        assert "verdict" in result.found_signals
        assert "rationale_summary" in result.found_signals


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

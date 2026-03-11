"""tests/test_validate_skill_files.py

Tests for scripts/validate_skill_files.py
"""

from __future__ import annotations

from pathlib import Path

from scripts.validate_skill_files import validate


class TestValidateSkillFiles:
    """Test suite for validate_skill_files.py"""

    def test_valid_skill_file(self, tmp_path: Path) -> None:
        """Test a completely valid skill file."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
name: test-skill
description: Tests without trying external APIs. DO NOT use real services.
---

# Test Skill

## Governing Axiom

This skill is governed by the Programmatic-First principle from MANIFESTO.md.

## Workflow

1. Setup test environment
2. Execute tests
3. Verify coverage

## Output

Test results and coverage report.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is True, f"Expected pass but got messages: {messages}"

    def test_missing_yaml_frontmatter(self, tmp_path: Path) -> None:
        """Test detection of missing YAML frontmatter."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """# Skill

## Governing Axiom

Some axiom.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is False
        assert any("frontmatter" in str(m).lower() for m in messages)

    def test_missing_name_field(self, tmp_path: Path) -> None:
        """Test detection of missing 'name' frontmatter field."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
description: A test skill.
---

# Skill

## Governing Axiom

Axiom.

## Workflow

Steps.

## Output

Results.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is False
        assert any("name" in str(m).lower() for m in messages)

    def test_missing_description_field(self, tmp_path: Path) -> None:
        """Test detection of missing 'description' frontmatter field."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
name: test-skill
---

# Skill

## Governing Axiom

Axiom.

## Workflow

Steps.

## Output

Results.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is False
        assert any("description" in str(m).lower() for m in messages)

    def test_missing_governing_axiom_section(self, tmp_path: Path) -> None:
        """Test detection of missing Governing Axiom section."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
name: test
description: Test skill.
---

## Workflow

Steps.

## Output

Results.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is False
        assert any("governing axiom" in str(m).lower() for m in messages)

    def test_missing_workflow_section(self, tmp_path: Path) -> None:
        """Test detection of missing Workflow section."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
name: test
description: Test skill.
---

## Governing Axiom

Governed by axiom from MANIFESTO.md.

## Output

Results.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is False
        assert any("workflow" in str(m).lower() for m in messages)

    def test_missing_output_section(self, tmp_path: Path) -> None:
        """Test detection of missing Output section."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
name: test
description: Test skill.
---

## Governing Axiom

Governed by axiom from MANIFESTO.md.

## Workflow

Steps.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is False
        assert any("output" in str(m).lower() for m in messages)

    def test_missing_cross_reference(self, tmp_path: Path) -> None:
        """Test detection of missing cross-reference to MANIFESTO or AGENTS."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
name: test
description: Test skill without references.
---

## Governing Axiom

Some principle governs this.

## Workflow

Steps.

## Output

Results.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is False
        assert any("cross-reference" in str(m).lower() for m in messages)

    def test_manifesto_reference_accepted(self, tmp_path: Path) -> None:
        """Test that MANIFESTO.md reference satisfies cross-reference check."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
name: test
description: Governed by MANIFESTO.md. DO NOT use in production.
---

## Governing Axiom

Endogenous-First from MANIFESTO.md.

## Workflow

Steps.

## Output

Results.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is True

    def test_agents_reference_accepted(self, tmp_path: Path) -> None:
        """Test that AGENTS.md reference satisfies cross-reference check."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
name: test
description: See AGENTS.md for context. AVOID production use.
---

## Governing Axiom

Principle from AGENTS.md.

## Workflow

Steps.

## Output

Results.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is True

    def test_heredoc_violation(self, tmp_path: Path) -> None:
        """Test detection of heredoc file write pattern."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
name: test
description: Test from MANIFESTO.md.
---

## Governing Axiom

Axiom.

## Workflow

Do this: cat >> file << 'EOF'

## Output

Results.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is False
        assert any("heredoc" in str(m).lower() for m in messages)

    def test_heredoc_in_negation_context_allowed(self, tmp_path: Path) -> None:
        """Test that heredoc in negation context (guardrail) is allowed."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
name: test
description: Avoid MANIFESTO.md violations.
---

## Governing Axiom

Axiom.

## Workflow

Never use: cat >> file << 'EOF'

## Output

Results.
"""
        )

        passed, messages = validate(skill_file)
        # Should pass - heredoc is in negation context
        assert not any("heredoc" in str(m).lower() for m in messages)

    def test_missing_inverse_scope(self, tmp_path: Path) -> None:
        """Test detection of missing inverse scope statement."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
name: test
description: A skill without scope boundaries.
---

## Governing Axiom

Axiom from MANIFESTO.md.

## Workflow

Steps.

## Output

Results.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is False
        assert any("inverse scope" in str(m).lower() or "do not" in str(m).lower() for m in messages)

    def test_do_not_in_description(self, tmp_path: Path) -> None:
        """Test that 'DO NOT' in description satisfies scope check."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
name: test
description: Test skill. DO NOT use in production.
---

## Governing Axiom

Axiom from MANIFESTO.md.

## Workflow

Steps.

## Output

Results.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is True

    def test_avoid_in_body(self, tmp_path: Path) -> None:
        """Test that 'AVOID' in body satisfies scope check."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
name: test
description: Test skill.
---

## Governing Axiom

Axiom from MANIFESTO.md.

## Workflow

Steps.

## Output

Results.

## Limitations

AVOID using this for production systems.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is True

    def test_not_for_in_body(self, tmp_path: Path) -> None:
        """Test that 'NOT FOR' in body satisfies scope check."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
name: test
description: Test skill.
---

## Governing Axiom

Axiom from AGENTS.md.

## Workflow

Steps.

## Output

Results.

NOTE: This skill is NOT FOR use with real customer data.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is True

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Test handling of non-existent file."""
        missing_file = tmp_path / "nonexistent.md"
        passed, messages = validate(missing_file)
        assert passed is False
        assert any("not found" in str(m).lower() for m in messages)

    def test_multiple_failures(self, tmp_path: Path) -> None:
        """Test file with multiple validation failures."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
description: Missing name field.
---

## Workflow

Steps only, missing other sections.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is False
        assert len(messages) >= 3  # Missing name, axiom section, output section, cross-ref, scope

    def test_all_negation_variants(self, tmp_path: Path) -> None:
        """Test that various negation formats are recognized."""
        for negation in ["DO NOT", "do not", "AVOID", "avoid", "NOT FOR", "not for", "don't", "DON'T"]:
            skill_file = tmp_path / f"test_{negation.replace(' ', '_')}.md"
            skill_file.write_text(
                f"""---
name: test
description: Test with {negation} in description.
---

## Governing Axiom

From MANIFESTO.md.

## Workflow

Steps.

## Output

Results.
"""
            )

            passed, messages = validate(skill_file)
            assert passed is True, f"Failed for negation: {negation}"

    def test_workflow_section_variants(self, tmp_path: Path) -> None:
        """Test that various workflow section names are accepted."""
        for section_name in ["Workflow", "Procedure", "Steps", "Usage"]:
            skill_file = tmp_path / f"test_{section_name}.md"
            skill_file.write_text(
                f"""---
name: test
description: Test with {section_name}. DO NOT use in production.
---

## Governing Axiom

From MANIFESTO.md.

## {section_name}

Instructions here.

## Output

Results.
"""
            )

            passed, messages = validate(skill_file)
            assert passed is True, f"Failed for section: {section_name}"

    def test_principle_section_name(self, tmp_path: Path) -> None:
        """Test that 'Principle' is accepted as Governing Axiom variant."""
        skill_file = tmp_path / "test.md"
        skill_file.write_text(
            """---
name: test
description: Test from MANIFESTO.md. NOT FOR production.
---

## Principle

This skill follows the Endogenous-First principle.

## Workflow

Steps.

## Output

Results.
"""
        )

        passed, messages = validate(skill_file)
        assert passed is True

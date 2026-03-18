"""
tests/test_audit_structural_compliance.py
-----------------------------------------
Purpose:
    Tests the audit_structural_compliance.py script's logic.
"""

import pytest

from scripts.audit_structural_compliance import audit_agent_file


@pytest.fixture
def mock_agent_file(tmp_path):
    def _create_agent(content):
        f = tmp_path / "mock.agent.md"
        f.write_text(content, encoding="utf-8")
        return f

    return _create_agent


def test_compliant_agent(mock_agent_file):
    content = """---
name: Compliant Agent
---

<context>
## Beliefs & Context
Some context here.
</context>

<instructions>
## Workflow & Intentions
Steps to follow.
</instructions>

<constraints>
## Guardrails
Safety first.
</constraints>

<output>
## Desired Outcomes & Acceptance
Final output.
</output>
"""
    file_path = mock_agent_file(content)
    missing = audit_agent_file(file_path)
    assert not missing


def test_missing_tags(mock_agent_file):
    content = """---
name: Missing Tags Agent
---

## Beliefs & Context
Context with no tag.

<instructions>
## Workflow & Intentions
Instructions with tag.
</instructions>
"""
    file_path = mock_agent_file(content)
    missing = audit_agent_file(file_path)
    assert "context" in missing
    assert "constraints" in missing
    assert "output" in missing
    assert "instructions" not in missing


def test_misaligned_tags(mock_agent_file):
    content = """---
name: Misaligned Agent
---

<context>
## Wrong Heading
Context with tag around wrong heading.
</context>
"""
    file_path = mock_agent_file(content)
    missing = audit_agent_file(file_path)
    # Since regex pattern is <tag>...## heading, it won't find the correct alignment.
    assert "context (alignment)" in missing

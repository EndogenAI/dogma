"""tests/test_capability_gate.py

Tests for the capability gate system (scripts/capability_gate.py).

Tests cover:
  - Registry loading and validation
  - Capability checking
  - Decorator application
  - Audit logging
  - Error handling
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from scripts.capability_gate import (
    CapabilityDenied,
    audit_denied,
    audit_granted,
    get_agent_context,
    has_capability,
    load_registry,
    requires_capability,
    set_agent_context,
    set_audit_log_path,
    set_registry_path,
    validate_registry,
)


@pytest.fixture
def temp_registry(tmp_path: Path) -> Path:
    """Create a temporary capability registry."""
    registry_file = tmp_path / "agent_capabilities.yaml"
    registry_file.write_text(
        """---
github:
  capabilities:
    - github_api
    - git_operations

researcher:
  capabilities:
    - read_docs
"""
    )
    return registry_file


@pytest.fixture
def temp_audit_log(tmp_path: Path) -> Path:
    """Create a temporary audit log path."""
    log_dir = tmp_path / ".logs"
    log_dir.mkdir()
    return log_dir / "capability_audit.jsonl"


@pytest.fixture(autouse=True)
def reset_agent_context():
    """Reset agent context before each test."""
    import scripts.capability_gate as cg

    original_agent = cg._AGENT_CONTEXT
    yield
    cg._AGENT_CONTEXT = original_agent


class TestRegistryLoading:
    """Test registry loading and validation."""

    @pytest.mark.io
    def test_load_registry(self, temp_registry: Path) -> None:
        """Test loading a valid registry."""
        reg = load_registry(temp_registry)
        assert "github" in reg
        assert "researcher" in reg
        assert "github_api" in reg["github"]
        assert "git_operations" in reg["github"]

    def test_load_registry_missing_file(self, tmp_path: Path) -> None:
        """Test error when registry file is missing."""
        missing = tmp_path / "nonexistent.yaml"
        with pytest.raises(FileNotFoundError):
            load_registry(missing)

    def test_validate_registry_valid(self, temp_registry: Path) -> None:
        """Test validation of a valid registry."""
        is_valid, errors = validate_registry(temp_registry)
        assert is_valid
        assert errors == []

    def test_validate_registry_missing_file(self, tmp_path: Path) -> None:
        """Test validation error when registry is missing."""
        missing = tmp_path / "nonexistent.yaml"
        is_valid, errors = validate_registry(missing)
        assert not is_valid
        assert any("not found" in err for err in errors)

    @pytest.mark.io
    def test_validate_registry_empty_agent(self, tmp_path: Path) -> None:
        """Test validation error for agent with no capabilities."""
        registry_file = tmp_path / "bad_registry.yaml"
        registry_file.write_text(
            """---
github:
  capabilities:
    - github_api
empty_agent:
  capabilities: []
"""
        )
        is_valid, errors = validate_registry(registry_file)
        assert not is_valid
        assert any("no capabilities" in err for err in errors)

    @pytest.mark.io
    def test_validate_registry_reserved_capability(self, tmp_path: Path) -> None:
        """Test validation error for reserved capability names."""
        registry_file = tmp_path / "reserved_registry.yaml"
        registry_file.write_text(
            """---
github:
  capabilities:
    - all
"""
        )
        is_valid, errors = validate_registry(registry_file)
        assert not is_valid
        assert any("reserved" in err for err in errors)


class TestCapabilityChecking:
    """Test capability checking logic."""

    def test_has_capability(self, temp_registry: Path) -> None:
        """Test checking if an agent has a capability."""
        reg = load_registry(temp_registry)
        assert has_capability("github", "github_api", reg)
        assert has_capability("github", "git_operations", reg)
        assert not has_capability("researcher", "github_api", reg)

    def test_has_capability_nonexistent_agent(self, temp_registry: Path) -> None:
        """Test checking capability for nonexistent agent."""
        reg = load_registry(temp_registry)
        assert not has_capability("nonexistent", "any_capability", reg)

    def test_has_capability_nonexistent_capability(self, temp_registry: Path) -> None:
        """Test checking nonexistent capability."""
        reg = load_registry(temp_registry)
        assert not has_capability("github", "nonexistent_capability", reg)


class TestAgentContext:
    """Test agent context management."""

    def test_set_and_get_agent_context(self) -> None:
        """Test setting and getting agent context."""
        set_agent_context("researcher")
        assert get_agent_context() == "researcher"

    def test_get_agent_context_not_set(self) -> None:
        """Test error when agent context is not set."""
        import scripts.capability_gate as cg

        cg._AGENT_CONTEXT = None
        with pytest.raises(RuntimeError, match="not set"):
            get_agent_context()


class TestDecorator:
    """Test the @requires_capability decorator."""

    @pytest.mark.io
    def test_decorator_granted(self, temp_registry: Path, temp_audit_log: Path) -> None:
        """Test decorator allows call when capability is granted."""
        set_registry_path(temp_registry)
        set_audit_log_path(temp_audit_log)
        set_agent_context("github")

        @requires_capability("github_api")
        def protected_call() -> str:
            return "success"

        result = protected_call()
        assert result == "success"

    @pytest.mark.io
    def test_decorator_denied(self, temp_registry: Path, temp_audit_log: Path) -> None:
        """Test decorator raises CapabilityDenied when capability is denied."""
        set_registry_path(temp_registry)
        set_audit_log_path(temp_audit_log)
        set_agent_context("researcher")

        @requires_capability("github_api")
        def protected_call() -> str:
            return "should not reach here"

        with pytest.raises(CapabilityDenied) as exc_info:
            protected_call()

        assert exc_info.value.agent == "researcher"
        assert exc_info.value.capability == "github_api"

    @pytest.mark.io
    def test_decorator_preserves_function_signature(
        self, temp_registry: Path, temp_audit_log: Path
    ) -> None:
        """Test decorator preserves wrapped function name and docstring."""
        set_registry_path(temp_registry)
        set_audit_log_path(temp_audit_log)

        @requires_capability("github_api")
        def my_function() -> None:
            """My docstring."""
            pass

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."

    @pytest.mark.io
    def test_decorator_with_arguments(
        self, temp_registry: Path, temp_audit_log: Path
    ) -> None:
        """Test decorator works with functions that take arguments."""
        set_registry_path(temp_registry)
        set_audit_log_path(temp_audit_log)
        set_agent_context("github")

        @requires_capability("github_api")
        def protected_call(a: int, b: str, c: bool = False) -> str:
            return f"{a}:{b}:{c}"

        result = protected_call(42, "test", c=True)
        assert result == "42:test:True"


class TestAuditLogging:
    """Test audit logging functionality."""

    @pytest.mark.io
    def test_audit_granted_logs_event(self, temp_audit_log: Path) -> None:
        """Test audit_granted writes to JSONL log."""
        set_audit_log_path(temp_audit_log)
        audit_granted("github", "github_api", operation="create_issue", issue_number=123)

        # Read the log
        events = []
        with open(temp_audit_log) as f:
            for line in f:
                events.append(json.loads(line))

        assert len(events) == 1
        event = events[0]
        assert event["event_type"] == "GRANTED"
        assert event["agent"] == "github"
        assert event["capability"] == "github_api"
        assert event["operation"] == "create_issue"
        assert event["issue_number"] == 123
        assert "timestamp" in event

    @pytest.mark.io
    def test_audit_denied_logs_event(self, temp_audit_log: Path) -> None:
        """Test audit_denied writes to JSONL log."""
        set_audit_log_path(temp_audit_log)
        audit_denied(
            "researcher",
            "github_api",
            reason="Agent does not have capability",
            function="post_reply",
        )

        events = []
        with open(temp_audit_log) as f:
            for line in f:
                events.append(json.loads(line))

        assert len(events) == 1
        event = events[0]
        assert event["event_type"] == "DENIED"
        assert event["agent"] == "researcher"
        assert event["capability"] == "github_api"
        assert event["reason"] == "Agent does not have capability"
        assert event["function"] == "post_reply"

    @pytest.mark.io
    def test_audit_log_creates_directory(self, tmp_path: Path) -> None:
        """Test audit_log creates the .logs directory if missing."""
        log_path = tmp_path / "new" / "logs" / ".logs" / "audit.jsonl"
        set_audit_log_path(log_path)

        # Log an event (should create parent directories)
        audit_granted("test", "test_cap")

        assert log_path.parent.exists()
        assert log_path.exists()


class TestCapabilityDenied:
    """Test the CapabilityDenied exception."""

    def test_exception_message(self) -> None:
        """Test exception message formatting."""
        exc = CapabilityDenied("researcher", "github_api", "Custom reason")
        assert "researcher" in str(exc)
        assert "github_api" in str(exc)
        assert "Custom reason" in str(exc)

    def test_exception_attributes(self) -> None:
        """Test exception attributes are set correctly."""
        exc = CapabilityDenied("agent_name", "capability_name")
        assert exc.agent == "agent_name"
        assert exc.capability == "capability_name"

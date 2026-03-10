"""scripts/capability_gate.py

Runtime capability gates and audit logging for agent API access.

Purpose:
    Encodes MANIFESTO.md §2 (Algorithms Before Tokens) and the Programmatic-First Principle
    (AGENTS.md #programmatic-first-principle) — shifting AI behavioral constraints from
    token-dependent instructions into programmatically-enforced code. This implements the T4
    (execution-time intercept) governor tier from docs/research/shifting-constraints-from-tokens.md.

    Enforces capability-based access control at runtime, allowing only authorized agents to
    invoke privileged operations (e.g., GitHub API). Provides a decorator-based interface for
    protecting sensitive operations and audit logging for both authorized and denied access attempts.

Architecture:
    - Capability registry: YAML file mapping agents → [capabilities]
    - Decorator: @requires_capability("github_api") gates function calls
    - Audit logger: JSONL file (one event per line) of all access attempts
    - Exception: CapabilityDenied raised when access is denied

Inputs:
    - Agent name (dynamic, from context or environment)
    - Required capability (declared in decorator)
    - Capability registry path (defaults to scripts/agent_capabilities.yaml)
    - Audit log path (defaults to .logs/capability_audit.jsonl)

Outputs:
    - Audit log: .logs/capability_audit.jsonl (JSON Lines format)
    - Exception: CapabilityDenied on unauthorized access
    - Logging: INFO/WARNING/ERROR to Python logger

Usage examples:
    from capability_gate import requires_capability, set_agent_context, CapabilityDenied

    # Set the current agent (typically done once at session start)
    set_agent_context("github")

    # Protect a sensitive function
    @requires_capability("github_api")
    def post_to_github(endpoint: str) -> dict:
        '''Create/edit/close GitHub resource.'''
        return call_github_api(endpoint)

    # Call protected function (succeeds if agent has capability)
    try:
        result = post_to_github("/repos/owner/repo/issues")
    except CapabilityDenied as e:
        print(f"Access denied: {e}")

Exit codes:
    0  Normal operation (when used as a module)
    1  Registry validation failed (when executed as a script)
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, TypeVar

import yaml

# ============================================================================
# Configuration & Logging
# ============================================================================

_DEFAULT_REGISTRY = Path(__file__).parent / "agent_capabilities.yaml"
_DEFAULT_AUDIT_LOG = Path.cwd() / ".logs" / "capability_audit.jsonl"

logger = logging.getLogger(__name__)

# ============================================================================
# Global Context
# ============================================================================

_AGENT_CONTEXT: str | None = None
_CAPABILITY_REGISTRY: dict[str, set[str]] | None = None
_REGISTRY_PATH: Path = _DEFAULT_REGISTRY
_AUDIT_LOG_PATH: Path = _DEFAULT_AUDIT_LOG


# ============================================================================
# Exceptions
# ============================================================================


class CapabilityDenied(Exception):
    """Raised when an agent attempts to invoke a capability it does not possess."""

    def __init__(
        self,
        agent: str,
        capability: str,
        reason: str = "Agent does not have required capability",
    ):
        self.agent = agent
        self.capability = capability
        self.reason = reason
        super().__init__(f"{reason} (agent={agent}, capability={capability})")


# ============================================================================
# Registry Management
# ============================================================================


def load_registry(registry_path: Path | None = None) -> dict[str, set[str]]:
    """Load agent → capabilities mapping from YAML.

    Returns:
        dict[agent_name, set[capability_names]]
    """
    if registry_path is None:
        registry_path = _REGISTRY_PATH

    if not registry_path.exists():
        raise FileNotFoundError(f"Capability registry not found: {registry_path}")

    with open(registry_path, "r") as f:
        data = yaml.safe_load(f) or {}

    # Normalize to ensure all capabilities are sets
    registry: dict[str, set[str]] = {}
    for agent, caps in data.items():
        if isinstance(caps, (list, set)):
            registry[agent] = set(caps)
        elif isinstance(caps, dict) and "capabilities" in caps:
            registry[agent] = set(caps["capabilities"])
        else:
            registry[agent] = set()

    return registry


def set_registry_path(path: Path | str) -> None:
    """Override the default registry path."""
    global _REGISTRY_PATH
    _REGISTRY_PATH = Path(path)


def set_audit_log_path(path: Path | str) -> None:
    """Override the default audit log path."""
    global _AUDIT_LOG_PATH
    _AUDIT_LOG_PATH = Path(path)


def set_agent_context(agent_name: str) -> None:
    """Set the current agent name. Call this once at session start."""
    global _AGENT_CONTEXT
    _AGENT_CONTEXT = agent_name
    logger.info(f"Agent context set to: {agent_name}")


def get_agent_context() -> str:
    """Get the current agent name. Raises RuntimeError if not set."""
    if _AGENT_CONTEXT is None:
        raise RuntimeError("Agent context not set. Call set_agent_context() before protected operations.")
    return _AGENT_CONTEXT


# ============================================================================
# Audit Logging
# ============================================================================


def _audit_log(event_type: str, agent: str, capability: str, **metadata: Any) -> None:
    """Write an audit event to the JSONL log.

    Args:
        event_type: "GRANTED" or "DENIED"
        agent: Agent name
        capability: Capability name
        **metadata: Additional fields (operation, issue_number, etc.)
    """
    _AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "agent": agent,
        "capability": capability,
        **metadata,
    }

    try:
        with open(_AUDIT_LOG_PATH, "a") as f:
            f.write(json.dumps(event) + "\n")
    except IOError as e:
        logger.error(f"Failed to write audit log: {e}")


def audit_granted(agent: str, capability: str, **metadata: Any) -> None:
    """Log an authorized capability access."""
    _audit_log("GRANTED", agent, capability, **metadata)


def audit_denied(agent: str, capability: str, reason: str = "", **metadata: Any) -> None:
    """Log a denied capability access attempt."""
    _audit_log("DENIED", agent, capability, reason=reason, **metadata)


# ============================================================================
# Capability Checking
# ============================================================================


def has_capability(agent: str, capability: str, registry: dict[str, set[str]] | None = None) -> bool:
    """Check if an agent has a specific capability.

    Args:
        agent: Agent name
        capability: Capability name
        registry: Capability registry dict. If None, loads from file.

    Returns:
        True if agent has capability, False otherwise
    """
    if registry is None:
        registry = load_registry()

    agent_caps = registry.get(agent, set())
    return capability in agent_caps


# ============================================================================
# Decorator
# ============================================================================

F = TypeVar("F", bound=Callable[..., Any])


def requires_capability(capability: str) -> Callable[[F], F]:
    """Decorator to protect a function with capability-based access control.

    Args:
        capability: Required capability name (e.g., "github_api")

    Raises:
        CapabilityDenied: if the current agent does not have the capability

    Example:
        @requires_capability("github_api")
        def post_to_github(endpoint: str):
            return gh("api", endpoint)
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                agent = get_agent_context()
            except RuntimeError:
                # Agent context not set; log a warning and fail
                logger.error("Agent context not set for %s", func.__name__)
                raise

            registry = load_registry()

            if not has_capability(agent, capability, registry):
                reason = f"Agent does not have capability: {capability}"
                audit_denied(agent, capability, reason=reason, function=func.__name__)
                raise CapabilityDenied(agent, capability, reason)

            # Capability granted; log and execute
            audit_granted(agent, capability, function=func.__name__)
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


# ============================================================================
# Validation
# ============================================================================


def validate_registry(registry_path: Path | None = None) -> tuple[bool, list[str]]:
    """Validate the capability registry.

    Returns:
        (is_valid, error_messages)
    """
    errors: list[str] = []

    if registry_path is None:
        registry_path = _REGISTRY_PATH

    if not registry_path.exists():
        return False, [f"Registry file not found: {registry_path}"]

    try:
        registry = load_registry(registry_path)
    except Exception as e:
        return False, [f"Registry load failed: {e}"]

    # Check that all agents have valid capabilities
    for agent, caps in registry.items():
        if not caps:
            errors.append(f"Agent '{agent}' has no capabilities")
        if not isinstance(caps, (set, list)):
            errors.append(f"Agent '{agent}' capabilities must be a list or set")

    # Check for reserved capability names
    reserved = {"all", "none", "*"}
    for agent, caps in registry.items():
        for cap in caps:
            if cap in reserved:
                errors.append(f"Agent '{agent}' uses reserved capability name: {cap}")

    return len(errors) == 0, errors


# ============================================================================
# Main (validation script mode)
# ============================================================================


def main() -> int:
    """Validate the capability registry when run as a script."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate agent capability registry")
    parser.add_argument(
        "--registry",
        type=Path,
        default=_DEFAULT_REGISTRY,
        help=f"Path to registry YAML (default: {_DEFAULT_REGISTRY})",
    )
    args = parser.parse_args()

    is_valid, errors = validate_registry(args.registry)

    if is_valid:
        print(f"✓ Registry valid: {args.registry}")
        return 0

    print(f"✗ Registry invalid: {args.registry}", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

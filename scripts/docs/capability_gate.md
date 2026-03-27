# `capability\_gate`

scripts/capability_gate.py

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

## Usage

```bash
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
```

<!-- hash:82e9819af174dce3 -->

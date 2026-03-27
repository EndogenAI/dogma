# `health\_check\_services`

health_check_services.py — Poll /health endpoints for services in substrate-atlas.yml.

Purpose:
    Health check orchestrator for long-running services. Reads service registry from
    data/substrate-atlas.yml and polls each service's /health endpoint.

Inputs:
    - data/substrate-atlas.yml: service registry with health_endpoint fields
    - --timeout: HTTP request timeout in seconds (default: 5)
    - --services: comma-separated list of service names to check (default: all)

Outputs:
    - JSON to stdout: {"healthy": [...], "degraded": [...], "unreachable": [...]}
    - Exit 0 if all services healthy
    - Exit 1 if any service degraded (responding but not OK)
    - Exit 2 if any service unreachable (timeout or connection error)

Usage:
    # Check all services
    uv run python scripts/health_check_services.py

    # Check specific services with custom timeout
    uv run python scripts/health_check_services.py --services ollama,mcp-server --timeout 10

    # Dry run (list services without checking)
    uv run python scripts/health_check_services.py --dry-run

Exit codes:
    0 — all services healthy
    1 — one or more services degraded
    2 — one or more services unreachable

Reference:
    - docs/research/otel-agent-instrumentation.md § Pattern 2 (H4)
    - AGENTS.md § Async Process Handling
    - MANIFESTO.md § 3 Local-Compute-First

Closes: #342

## Usage

```bash
    # Check all services
    uv run python scripts/health_check_services.py

    # Check specific services with custom timeout
    uv run python scripts/health_check_services.py --services ollama,mcp-server --timeout 10

    # Dry run (list services without checking)
    uv run python scripts/health_check_services.py --dry-run
```

<!-- hash:c05d91667c7033fb -->

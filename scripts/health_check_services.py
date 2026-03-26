#!/usr/bin/env python3
"""
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
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

try:
    import yaml
except ImportError:
    print("Error: pyyaml not installed. Run: uv sync", file=sys.stderr)
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Error: requests not installed. Run: uv sync", file=sys.stderr)
    sys.exit(1)


def load_substrate_atlas(atlas_path: Path) -> dict:
    """Load service registry from substrate-atlas.yml.

    Args:
        atlas_path: Path to data/substrate-atlas.yml

    Returns:
        Parsed YAML dict with substrates list

    Raises:
        FileNotFoundError: If atlas file doesn't exist
        yaml.YAMLError: If atlas file is invalid YAML
    """
    if not atlas_path.exists():
        raise FileNotFoundError(f"Substrate atlas not found: {atlas_path}")

    with atlas_path.open() as f:
        return yaml.safe_load(f)


def check_service_health(service_name: str, endpoint: str, timeout: int = 5) -> Dict[str, str]:
    """Check health of a single service endpoint.

    Args:
        service_name: Human-readable service name
        endpoint: Full HTTP(S) URL to /health endpoint
        timeout: Request timeout in seconds

    Returns:
        Dict with keys: name, status (healthy|degraded|unreachable), message
    """
    try:
        response = requests.get(endpoint, timeout=timeout)

        if response.status_code == 200:
            return {
                "name": service_name,
                "status": "healthy",
                "message": f"OK ({response.elapsed.total_seconds():.2f}s)",
            }
        else:
            return {"name": service_name, "status": "degraded", "message": f"HTTP {response.status_code}"}

    except requests.Timeout:
        return {"name": service_name, "status": "unreachable", "message": f"Timeout after {timeout}s"}

    except requests.ConnectionError as e:
        return {"name": service_name, "status": "unreachable", "message": f"Connection error: {str(e)[:50]}"}

    except Exception as e:
        return {"name": service_name, "status": "unreachable", "message": f"Error: {str(e)[:50]}"}


def extract_services_with_health_endpoints(atlas: dict) -> List[Dict[str, str]]:
    """Extract services with health_endpoint field from substrate atlas.

    Args:
        atlas: Parsed substrate-atlas.yml dict

    Returns:
        List of dicts with keys: name, health_endpoint
    """
    services = []
    for substrate in atlas.get("substrates", []):
        if "health_endpoint" in substrate:
            services.append({"name": substrate["name"], "health_endpoint": substrate["health_endpoint"]})
    return services


def main():
    """CLI entry point for health check orchestrator."""
    parser = argparse.ArgumentParser(description="Poll /health endpoints for services in substrate-atlas.yml")
    parser.add_argument(
        "--atlas",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "substrate-atlas.yml",
        help="Path to substrate-atlas.yml (default: data/substrate-atlas.yml)",
    )
    parser.add_argument("--timeout", type=int, default=5, help="HTTP request timeout in seconds (default: 5)")
    parser.add_argument("--services", help="Comma-separated list of service names to check (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="List services without checking health")

    args = parser.parse_args()

    try:
        atlas = load_substrate_atlas(args.atlas)
    except FileNotFoundError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 2
    except yaml.YAMLError as e:
        print(json.dumps({"error": f"Invalid YAML: {e}"}), file=sys.stderr)
        return 2

    services = extract_services_with_health_endpoints(atlas)

    if not services:
        print(
            json.dumps(
                {
                    "healthy": [],
                    "degraded": [],
                    "unreachable": [],
                    "message": "No services with health_endpoint found in atlas",
                }
            )
        )
        return 0

    # Filter by --services if specified
    if args.services:
        requested = set(s.strip() for s in args.services.split(","))
        services = [s for s in services if s["name"] in requested]

        if not services:
            print(json.dumps({"error": f"No matching services: {args.services}"}), file=sys.stderr)
            return 2

    if args.dry_run:
        print(json.dumps({"services": [s["name"] for s in services], "count": len(services)}))
        return 0

    # Check each service
    results = []
    for service in services:
        result = check_service_health(service["name"], service["health_endpoint"], args.timeout)
        results.append(result)

    # Categorize results
    healthy = [r for r in results if r["status"] == "healthy"]
    degraded = [r for r in results if r["status"] == "degraded"]
    unreachable = [r for r in results if r["status"] == "unreachable"]

    output = {
        "healthy": [r["name"] for r in healthy],
        "degraded": [{"name": r["name"], "message": r["message"]} for r in degraded],
        "unreachable": [{"name": r["name"], "message": r["message"]} for r in unreachable],
    }

    print(json.dumps(output, indent=2))

    # Exit code logic
    if unreachable:
        return 2
    elif degraded:
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())

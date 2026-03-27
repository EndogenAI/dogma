#!/usr/bin/env python3
"""
health_check_services.py — Poll /health endpoints for services in substrate-atlas.yml.

Purpose:
    Health check orchestrator for long-running services. Reads service registry from
    data/substrate-atlas.yml and polls each service's /health endpoint.
    Optionally checks inference provider availability from data/inference-providers.yml.

Inputs:
    - data/substrate-atlas.yml: service registry with health_endpoint fields
    - data/inference-providers.yml: inference provider capability matrix (optional)
    - --timeout: HTTP request timeout in seconds (default: 5)
    - --services: comma-separated list of service names to check (default: all)
    - --provider-type: check inference providers by type (local|external|all) (optional)

Outputs:
    - JSON to stdout: {"healthy": [...], "degraded": [...], "unreachable": [...]}
    - If --provider-type specified: adds "providers": {"local": [...], "external": [...]}
    - Exit 0 if all services healthy
    - Exit 1 if any service degraded (responding but not OK)
    - Exit 2 if any service unreachable (timeout or connection error)

Usage:
    # Check all services
    uv run python scripts/health_check_services.py

    # Check specific services with custom timeout
    uv run python scripts/health_check_services.py --services ollama,mcp-server --timeout 10

    # Check local inference providers only
    uv run python scripts/health_check_services.py --provider-type local

    # Check all inference providers (local + external)
    uv run python scripts/health_check_services.py --provider-type all

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

Closes: #342, #474
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


def load_inference_providers(providers_path: Path) -> dict:
    """Load inference provider capability matrix from YAML.

    Args:
        providers_path: Path to data/inference-providers.yml

    Returns:
        Parsed YAML dict with providers list

    Raises:
        FileNotFoundError: If providers file doesn't exist
        yaml.YAMLError: If providers file is invalid YAML
    """
    if not providers_path.exists():
        raise FileNotFoundError(f"Inference providers file not found: {providers_path}")

    with providers_path.open() as f:
        return yaml.safe_load(f)


def check_inference_providers(
    providers_data: dict, provider_type: str = "all", timeout: int = 5
) -> Dict[str, List[Dict[str, str]]]:
    """Check inference provider availability based on provider type filter.

    Args:
        providers_data: Parsed inference-providers.yml dict
        provider_type: Filter by 'local', 'external', or 'all' (default: 'all')
        timeout: Request timeout in seconds for external providers

    Returns:
        Dict with keys: local (list of local providers), external (list of external providers)
        Each provider entry: {"name": str, "status": "available"|"unreachable", "message": str}
    """
    local_providers = []
    external_providers = []

    for provider in providers_data.get("providers", []):
        is_local = provider.get("local", False)

        # Apply provider_type filter
        if provider_type == "local" and not is_local:
            continue
        if provider_type == "external" and is_local:
            continue

        # Check provider availability
        endpoint = provider.get("endpoint")
        if not endpoint:
            continue

        provider_entry = {"name": provider["name"], "endpoint": endpoint}

        # For local providers, check availability
        if is_local:
            # Check if local endpoint is reachable (simple GET)
            try:
                response = requests.get(endpoint, timeout=timeout)
                # Include 401/403/405 as "reachable" - provider is up but expects POST/auth
                if response.status_code in (200, 404, 401, 403, 405):
                    provider_entry["status"] = "available"
                    provider_entry["message"] = f"Reachable ({response.status_code})"
                else:
                    provider_entry["status"] = "unreachable"
                    provider_entry["message"] = f"HTTP {response.status_code}"
            except requests.Timeout:
                provider_entry["status"] = "unreachable"
                provider_entry["message"] = f"Timeout after {timeout}s"
            except requests.ConnectionError:
                provider_entry["status"] = "unreachable"
                provider_entry["message"] = "Connection refused"
            except Exception as e:
                provider_entry["status"] = "unreachable"
                provider_entry["message"] = f"Error: {str(e)[:50]}"

            local_providers.append(provider_entry)
        else:
            # External providers: mark as configured (don't check auth endpoints)
            provider_entry["status"] = "configured"
            provider_entry["message"] = "External API endpoint configured"
            external_providers.append(provider_entry)

    return {"local": local_providers, "external": external_providers}


def main():
    """CLI entry point for health check orchestrator."""
    parser = argparse.ArgumentParser(description="Poll /health endpoints for services in substrate-atlas.yml")
    parser.add_argument(
        "--atlas",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "substrate-atlas.yml",
        help="Path to substrate-atlas.yml (default: data/substrate-atlas.yml)",
    )
    parser.add_argument(
        "--providers",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "inference-providers.yml",
        help="Path to inference-providers.yml (default: data/inference-providers.yml)",
    )
    parser.add_argument("--timeout", type=int, default=5, help="HTTP request timeout in seconds (default: 5)")
    parser.add_argument("--services", help="Comma-separated list of service names to check (default: all)")
    parser.add_argument(
        "--provider-type",
        choices=["local", "external", "all"],
        help="Check inference providers by type: local, external, or all (optional)",
    )
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

    # Check inference providers if --provider-type is specified
    if args.provider_type:
        try:
            providers_data = load_inference_providers(args.providers)
            providers_check = check_inference_providers(providers_data, args.provider_type, args.timeout)
            output["providers"] = providers_check
        except FileNotFoundError as e:
            output["providers"] = {"error": str(e)}
        except yaml.YAMLError as e:
            output["providers"] = {"error": f"Invalid providers YAML: {e}"}
        except Exception as e:
            output["providers"] = {"error": f"Provider check error: {e}"}

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

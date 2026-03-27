"""
test_inference_integration.py — Integration tests for live Ollama stack.

Tests route_inference_request and health_check_services.py with a live Ollama daemon.
All tests skip gracefully if Ollama is unreachable.

Requires:
    - Ollama running at http://localhost:11434/
    - At least one model pulled (e.g., phi3:mini)

Usage:
    uv run pytest tests/test_inference_integration.py -m integration -v
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Check if Ollama is reachable at module level
try:
    import urllib.request

    urllib.request.urlopen("http://localhost:11434/", timeout=2)
    OLLAMA_AVAILABLE = True
except Exception:
    OLLAMA_AVAILABLE = False

# Skip all tests if Ollama is unreachable
pytestmark = pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama unreachable at http://localhost:11434/")

# Add scripts/ and mcp_server/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.tools.inference import route_inference_request  # noqa: E402


@pytest.mark.integration
def test_health_check_local_providers():
    """Verify health_check_services.py --provider-type local succeeds with Ollama."""
    script_path = Path(__file__).parent.parent / "scripts" / "health_check_services.py"
    result = subprocess.run(
        ["uv", "run", "python", str(script_path), "--provider-type", "local"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=Path(__file__).parent.parent,
    )

    assert result.returncode == 0, f"health_check_services.py failed: {result.stderr}"

    # Parse JSON output
    output = json.loads(result.stdout)
    assert "providers" in output
    assert "local" in output["providers"]

    # Verify ollama appears in local providers (local_providers is a list of dicts)
    local_providers = output["providers"]["local"]
    provider_names = [p.get("name", "").lower() for p in local_providers if isinstance(p, dict)]
    assert "local-ollama" in provider_names, f"Expected 'local-ollama' in local providers, got: {provider_names}"


@pytest.mark.integration
def test_route_local_model_routing_only():
    """Verify route_inference_request routes to a local provider and sets routing metadata (no inference)."""
    result = route_inference_request(prompt="hello", model_id="phi3:mini", max_tokens=50, temperature=0.7)

    assert result["ok"] is True, f"route_inference_request failed: {result.get('errors')}"
    assert "response" in result, "Expected 'response' key in result (may be None for routing-only)"
    assert result["provider"] is not None, "Expected provider to be set"
    assert result["local"] is True, "Expected local provider for phi3:mini"


@pytest.mark.integration
def test_provider_preference_local_first():
    """Verify route_inference_request prefers local providers (Local-Compute-First)."""
    # Use a model that exists locally (assuming phi3:mini is pulled)
    result = route_inference_request(prompt="test", model_id="phi3:mini", max_tokens=10, temperature=0.5)

    assert result["ok"] is True, f"Routing failed: {result.get('errors')}"
    assert result["local"] is True, f"Expected local provider for phi3:mini, got local={result['local']}"
    assert result["provider"] is not None
    assert result["cost_tier"] == "free", f"Expected 'free' cost tier for local, got: {result['cost_tier']}"

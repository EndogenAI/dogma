"""mcp_server/tools/inference.py — MCP tool for multi-provider inference routing.

Tools:
    route_inference_request — Route inference requests to local or external providers based on YAML config.

Inputs:
    route_inference_request:
        prompt      : str  — The prompt to send to the model
        model_id    : str  — Model identifier (e.g., 'llama3.2', 'claude-3-5-haiku-20241022')
        max_tokens  : int  — Maximum tokens to generate (default: 512)
        temperature : float — Sampling temperature 0.0-1.0 (default: 0.7)

Outputs:
    {
        "ok": bool,
        "provider": str | None,          # matched provider name
        "endpoint": str | None,          # endpoint URL
        "local": bool,                   # whether provider runs locally
        "cost_tier": str | None,         # 'free' | 'low' | 'high'
        "response": str | None,          # model response text (if called)
        "errors": list[str]
    }

Usage:
    result = route_inference_request(
        prompt="What is the capital of France?",
        model_id="llama3.2"
    )
"""

from __future__ import annotations

from typing import Any

from mcp_server._security import REPO_ROOT

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def _load_providers() -> list[dict[str, Any]]:
    """Load provider configuration from data/inference-providers.yml.

    Returns:
        List of provider dicts with keys: name, endpoint, model_ids, cost_tier, local
    """
    if yaml is None:
        raise RuntimeError("PyYAML not installed — required for inference provider routing")

    config_path = REPO_ROOT / "data" / "inference-providers.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"Provider config not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data.get("providers", [])


def route_inference_request(
    prompt: str,
    model_id: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> dict[str, Any]:
    """Route an inference request to the appropriate provider based on model_id.

    Reads data/inference-providers.yml to determine which provider supports the
    requested model. Prefers local providers (Local-Compute-First principle).

    Args:
        prompt: The prompt text to send to the model.
        model_id: Model identifier from the provider config (e.g., 'llama3.2').
        max_tokens: Maximum tokens to generate (default: 512).
        temperature: Sampling temperature 0.0-1.0 (default: 0.7).

    Returns:
        {
            "ok": bool,
            "provider": str | None,
            "endpoint": str | None,
            "local": bool,
            "cost_tier": str | None,
            "response": str | None,
            "errors": list[str]
        }
    """
    try:
        providers = _load_providers()
    except Exception as exc:
        return {
            "ok": False,
            "provider": None,
            "endpoint": None,
            "local": False,
            "cost_tier": None,
            "response": None,
            "errors": [f"Failed to load provider config: {exc}"],
        }

    # Find providers that support this model_id, preferring local providers first
    candidates = [p for p in providers if model_id in p.get("model_ids", [])]
    candidates.sort(key=lambda p: (not p.get("local", False), p.get("cost_tier", "high")))

    if not candidates:
        return {
            "ok": False,
            "provider": None,
            "endpoint": None,
            "local": False,
            "cost_tier": None,
            "response": None,
            "errors": [
                f"No provider found for model_id '{model_id}'. Available models: {_list_available_models(providers)}"
            ],
        }

    provider = candidates[0]
    return {
        "ok": True,
        "provider": provider.get("name"),
        "endpoint": provider.get("endpoint"),
        "local": provider.get("local", False),
        "cost_tier": provider.get("cost_tier"),
        "response": None,  # Routing only; actual invocation is out of scope for MCP tool
        "errors": [],
    }


def _list_available_models(providers: list[dict[str, Any]]) -> list[str]:
    """Extract all model_ids from provider configs for error messages."""
    models = []
    for p in providers:
        models.extend(p.get("model_ids", []))
    return sorted(set(models))

"""
scripts/inference_router.py
---------------------------
Routes LLM inference requests through an ordered provider fallback chain.

Purpose:
    Reads data/inference-providers.yml and selects a provider for a given prompt,
    trying each in order until one succeeds. Implements Local-Compute-First by
    preferring local providers when available.

Inputs:
    - data/inference-providers.yml (provider capability matrix)
    - prompt: str — the text to send to the inference provider
    - preferred_provider: str | None — name of provider to try first

Outputs:
    - route(): returns the name of the first available provider
    - call_with_fallback(): returns dict {provider, response, attempts}

Usage example:
    uv run python scripts/inference_router.py --prompt "Summarize this." --provider local-ollama

Exit codes:
    0 — success
    1 — all providers failed or providers list is empty
    2 — config file not found

References:
    - AGENTS.md § Local Compute-First
    - data/inference-providers.yml
    - data/rate-limit-profiles.yml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

_DEFAULT_CONFIG = Path(__file__).parent.parent / "data" / "inference-providers.yml"

# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


def load_providers(config_path: Path = _DEFAULT_CONFIG) -> list[dict[str, Any]]:
    """Load provider list from YAML config.

    Args:
        config_path: Path to inference-providers.yml

    Returns:
        List of provider dicts.

    Raises:
        FileNotFoundError: if config file does not exist.
        ValueError: if YAML is malformed or missing 'providers' key.
    """
    if not config_path.exists():
        raise FileNotFoundError(
            f"Inference providers config not found: {config_path}\nExpected: data/inference-providers.yml"
        )
    with config_path.open() as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict) or "providers" not in data:
        raise ValueError(f"Config file {config_path} must contain a top-level 'providers:' list.")
    return data["providers"]


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------


def route(
    prompt: str,
    preferred_provider: str | None = None,
    config_path: Path = _DEFAULT_CONFIG,
) -> str:
    """Return the name of the first provider to use for *prompt*.

    Provider ordering:
    1. preferred_provider (if supplied and present in config)
    2. Local providers first (local: true), sorted by list order
    3. Remaining providers in list order

    Args:
        prompt: The text prompt (used for future cost/routing heuristics; not
                sent by this function).
        preferred_provider: Optional provider name to try first.
        config_path: Path to inference-providers.yml.

    Returns:
        Provider name string.

    Raises:
        ValueError: if providers list is empty.
        FileNotFoundError: if config file is missing.
    """
    providers = load_providers(config_path)
    if not providers:
        raise ValueError("Providers list is empty — cannot route request.")

    names = [p["name"] for p in providers]

    # Build ordered list: preferred → local → rest
    ordered: list[str] = []
    if preferred_provider and preferred_provider in names:
        ordered.append(preferred_provider)

    local_names = [p["name"] for p in providers if p.get("local", False)]
    for name in local_names:
        if name not in ordered:
            ordered.append(name)

    for name in names:
        if name not in ordered:
            ordered.append(name)

    return ordered[0]


def call_with_fallback(
    prompt: str,
    providers_list: list[str],
    config_path: Path = _DEFAULT_CONFIG,
) -> dict[str, Any]:
    """Try each provider in *providers_list* in order, returning on first
    simulated success.

    This function simulates provider calls (no actual HTTP requests) — it acts
    as the routing/selection layer only. Real HTTP dispatch is out of scope per
    the confirmed scope for #333 (routing + fallback only).

    Args:
        prompt: The text prompt.
        providers_list: Ordered list of provider names to try.
        config_path: Path to inference-providers.yml.

    Returns:
        dict with keys:
            provider (str): name of the provider that responded
            response (str): simulated response token ("__ROUTED__")
            attempts (int): number of providers tried before success

    Raises:
        ValueError: if providers_list is empty.
        RuntimeError: if all providers are exhausted.
        FileNotFoundError: if config file is missing.
    """
    if not providers_list:
        raise ValueError("providers_list is empty — cannot attempt fallback chain.")

    all_providers = load_providers(config_path)
    known_names = {p["name"] for p in all_providers}

    attempts = 0
    for name in providers_list:
        attempts += 1
        if name not in known_names:
            # Unknown provider — treat as unavailable, try next
            continue
        # Simulate a successful routing decision
        return {
            "provider": name,
            "response": "__ROUTED__",
            "attempts": attempts,
        }

    raise RuntimeError(f"All providers exhausted after {attempts} attempt(s). Tried: {providers_list}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Route an LLM prompt to the best available inference provider.")
    p.add_argument("--prompt", required=True, help="Text prompt to route.")
    p.add_argument(
        "--provider",
        default=None,
        help="Preferred provider name (optional).",
    )
    p.add_argument(
        "--config",
        default=str(_DEFAULT_CONFIG),
        help="Path to inference-providers.yml.",
    )
    p.add_argument(
        "--fallback",
        action="store_true",
        help="Run full fallback chain and print result dict.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    config_path = Path(args.config)

    try:
        if args.fallback:
            providers = load_providers(config_path)
            provider_names = [p["name"] for p in providers]
            result = call_with_fallback(args.prompt, provider_names, config_path)
            print(f"Provider: {result['provider']} (attempts: {result['attempts']})")
        else:
            name = route(args.prompt, args.provider, config_path)
            print(f"Route to: {name}")
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

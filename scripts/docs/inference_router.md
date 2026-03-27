# `inference\_router`

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

## Usage

```bash
    uv run python scripts/inference_router.py --prompt "Summarize this." --provider local-ollama
```

<!-- hash:66c7b70ae33c7a34 -->

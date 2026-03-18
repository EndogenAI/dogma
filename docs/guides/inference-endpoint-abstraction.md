---
governs: [local-compute-first]
status: Draft
closes_issue: 382
---

# InferenceEndpoint Abstraction

## Purpose

`InferenceEndpoint` is a planned abstraction in `packages/dogma-governance/` that decouples agent logic from specific AI provider APIs. Rather than coupling orchestration scripts and agent workflows directly to a single provider's SDK (e.g., the Anthropic Python client or Ollama's REST API), agents target a generic `InferenceEndpoint` interface that can be backed by any compatible provider at runtime.

This abstraction directly implements **Local-Compute-First** ([MANIFESTO.md § 3 — Local-Compute-First](../../MANIFESTO.md#3-local-compute-first)): by treating the provider as a swappable implementation detail, agents can run against a local Ollama instance during development and a cloud API in production without changing any orchestration logic. It also mitigates the platform lock-in risks documented in [`docs/research/ai-platform-lock-in-risks.md`](../research/ai-platform-lock-in-risks.md) — when a provider changes its ToS, pricing, or API surface, only the concrete endpoint implementation needs updating; the agent fleet is unaffected.

---

## Interface Outline

The following is a typing-stub outline, not a runnable implementation. It is intended to document intent and drive discussion before implementation begins.

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Protocol


class InferenceEndpoint(Protocol):
    """Generic inference endpoint protocol.

    All concrete provider implementations must satisfy this interface.
    Agents and orchestration scripts depend only on this protocol — never
    on a concrete provider class directly.
    """

    provider_name: str   # e.g. "ollama", "claude", "local"
    model_name: str      # e.g. "llama3.2", "claude-sonnet-4-5"
    max_tokens: int      # maximum tokens the endpoint will accept per call

    def generate(self, prompt: str, **kwargs) -> str:
        """Return a complete response string for the given prompt."""
        ...

    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Yield response tokens incrementally as they are produced."""
        ...

    def health_check(self) -> bool:
        """Return True if the endpoint is reachable and ready to serve requests."""
        ...


class BaseInferenceEndpoint(ABC):
    """Abstract base class providing shared validation and logging scaffolding.

    Concrete implementations should inherit from this class and implement
    the three abstract methods above.
    """

    provider_name: str
    model_name: str
    max_tokens: int

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str: ...

    @abstractmethod
    def stream(self, prompt: str, **kwargs) -> Iterator[str]: ...

    @abstractmethod
    def health_check(self) -> bool: ...
```

---

## Provider Implementations

Concrete implementations would live under `packages/dogma-governance/inference/`:

| Class | Module | Backed by |
|-------|--------|-----------|
| `OllamaEndpoint` | `inference/ollama.py` | Local [Ollama](https://ollama.com) daemon — preferred for Local-Compute-First posture |
| `ClaudeEndpoint` | `inference/claude.py` | Anthropic Claude API — used when local inference is insufficient |
| `LocalEndpoint` | `inference/local.py` | Any locally-hosted OpenAI-compatible endpoint (e.g. LM Studio, llama.cpp server) |

Each implementation satisfies the `InferenceEndpoint` protocol. Agent scripts select an implementation via configuration (e.g. `data/rate-limit-profiles.yml` provider key), not by importing a concrete class directly.

---

## Migration Pattern

This abstraction is the programmatic foundation for the provider-switching workflow described in [`docs/guides/platform-migration.md`](platform-migration.md). To switch providers:

1. Swap the `InferenceEndpoint` implementation bound at startup (e.g. replace `OllamaEndpoint` with `ClaudeEndpoint` in the provider factory).
2. Update the provider key in `data/rate-limit-profiles.yml` so the rate-limit gate applies the correct policy.
3. Run `uv run pytest tests/ -m "not slow"` to confirm agent logic is unaffected.

No agent or orchestration script changes are required — the interface contract is preserved across all provider backends.

---

## References

- [MANIFESTO.md § 3 — Local-Compute-First](../../MANIFESTO.md#3-local-compute-first)
- [`docs/research/ai-platform-lock-in-risks.md`](../research/ai-platform-lock-in-risks.md)
- [`docs/guides/platform-migration.md`](platform-migration.md)
- [`packages/dogma-governance/`](../../packages/dogma-governance/)

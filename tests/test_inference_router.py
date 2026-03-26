"""
tests/test_inference_router.py
-------------------------------
Tests for scripts/inference_router.py — multi-provider inference router.

Covers:
- Happy-path: route() returns first provider name
- Fallback: call_with_fallback returns second provider when first is unknown
- Empty providers list raises ValueError
- Missing YAML config raises FileNotFoundError
- CLI --prompt routes and prints provider name
- CLI --fallback runs full fallback chain

All file reads are either from a tmp_path fixture (io marker) or patched.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Module loader
# ---------------------------------------------------------------------------


def _load_module(name: str, rel_path: str):
    repo_root = Path(__file__).parent.parent
    spec = importlib.util.spec_from_file_location(name, repo_root / rel_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def router():
    return _load_module("inference_router", "scripts/inference_router.py")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def provider_config(tmp_path):
    """Write a minimal inference-providers.yml to tmp_path."""
    data = {
        "providers": [
            {
                "name": "local-test",
                "endpoint": "http://localhost:9999/api",
                "model_ids": ["test-model"],
                "cost_tier": "free",
                "local": True,
            },
            {
                "name": "remote-test",
                "endpoint": "https://example.com/api",
                "model_ids": ["remote-model"],
                "cost_tier": "low",
                "local": False,
            },
        ]
    }
    config_file = tmp_path / "inference-providers.yml"
    config_file.write_text(yaml.dump(data))
    return config_file


@pytest.fixture()
def single_provider_config(tmp_path):
    """Provider config with only one provider."""
    data = {
        "providers": [
            {
                "name": "only-provider",
                "endpoint": "http://localhost:1234/api",
                "model_ids": ["m1"],
                "cost_tier": "free",
                "local": True,
            }
        ]
    }
    config_file = tmp_path / "inference-providers.yml"
    config_file.write_text(yaml.dump(data))
    return config_file


# ---------------------------------------------------------------------------
# route() tests
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_route_returns_local_provider_first(router, provider_config):
    """Local provider should be returned first (Local-Compute-First)."""
    result = router.route("test prompt", config_path=provider_config)
    assert result == "local-test"


@pytest.mark.io
def test_route_respects_preferred_provider(router, provider_config):
    """preferred_provider overrides local-first ordering."""
    result = router.route(
        "test prompt",
        preferred_provider="remote-test",
        config_path=provider_config,
    )
    assert result == "remote-test"


@pytest.mark.io
def test_route_preferred_provider_not_in_config(router, provider_config):
    """Unknown preferred_provider falls back to default ordering."""
    result = router.route(
        "test prompt",
        preferred_provider="nonexistent",
        config_path=provider_config,
    )
    # Should still return the local provider as first in default order
    assert result == "local-test"


@pytest.mark.io
def test_route_single_provider(router, single_provider_config):
    """Single-provider config returns that provider."""
    result = router.route("test", config_path=single_provider_config)
    assert result == "only-provider"


# ---------------------------------------------------------------------------
# call_with_fallback() tests
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_call_with_fallback_happy_path(router, provider_config):
    """First known provider in list is returned on first attempt."""
    result = router.call_with_fallback(
        "test prompt",
        ["local-test", "remote-test"],
        config_path=provider_config,
    )
    assert result["provider"] == "local-test"
    assert result["attempts"] == 1
    assert result["response"] == "__ROUTED__"


@pytest.mark.io
def test_call_with_fallback_skips_unknown(router, provider_config):
    """Unknown provider is skipped; fallback reaches second provider."""
    result = router.call_with_fallback(
        "test prompt",
        ["nonexistent-provider", "remote-test"],
        config_path=provider_config,
    )
    assert result["provider"] == "remote-test"
    assert result["attempts"] == 2


@pytest.mark.io
def test_call_with_fallback_all_unknown_raises(router, provider_config):
    """RuntimeError raised if all providers in list are unknown."""
    with pytest.raises(RuntimeError, match="All providers exhausted"):
        router.call_with_fallback(
            "test prompt",
            ["ghost-a", "ghost-b"],
            config_path=provider_config,
        )


def test_call_with_fallback_empty_list_raises(router, provider_config):
    """ValueError raised when providers_list is empty."""
    with pytest.raises(ValueError, match="empty"):
        router.call_with_fallback("test prompt", [], config_path=provider_config)


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_route_raises_on_empty_providers(router, tmp_path):
    """ValueError raised when providers list in YAML is empty."""
    config_file = tmp_path / "empty.yml"
    config_file.write_text(yaml.dump({"providers": []}))
    with pytest.raises(ValueError, match="empty"):
        router.route("test", config_path=config_file)


@pytest.mark.io
def test_route_raises_on_missing_config(router, tmp_path):
    """FileNotFoundError raised when config file does not exist."""
    missing = tmp_path / "does_not_exist.yml"
    with pytest.raises(FileNotFoundError):
        router.route("test", config_path=missing)


@pytest.mark.io
def test_call_with_fallback_raises_on_missing_config(router, tmp_path):
    """FileNotFoundError raised when config file does not exist."""
    missing = tmp_path / "does_not_exist.yml"
    with pytest.raises(FileNotFoundError):
        router.call_with_fallback("test", ["local-test"], config_path=missing)


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_cli_route(router, provider_config, capsys):
    """CLI prints 'Route to: <name>' and exits 0 on happy path."""
    rc = router.main(["--prompt", "hello", "--config", str(provider_config)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "local-test" in captured.out


@pytest.mark.io
def test_cli_missing_config(router, tmp_path, capsys):
    """CLI exits 2 when config file is missing."""
    missing = tmp_path / "missing.yml"
    rc = router.main(["--prompt", "hi", "--config", str(missing)])
    assert rc == 2


@pytest.mark.io
def test_cli_fallback_flag(router, provider_config, capsys):
    """CLI --fallback runs full fallback chain and prints provider."""
    rc = router.main(["--prompt", "hi", "--config", str(provider_config), "--fallback"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Provider:" in captured.out

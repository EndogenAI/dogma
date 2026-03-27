"""tests/test_inference.py — Tests for mcp_server/tools/inference.py

Tests cover:
1. Provider routing for local models (ollama)
2. Provider routing for external models (anthropic, openai)
3. Local-Compute-First preference (local providers ranked first)
4. Invalid model_id handling
5. Missing provider config handling
"""

from __future__ import annotations

from unittest.mock import mock_open, patch

import pytest

from mcp_server.tools.inference import _list_available_models, _load_providers, route_inference_request

# Sample provider config for testing
SAMPLE_PROVIDERS_YAML = """
providers:
  - name: "local-ollama"
    endpoint: "http://localhost:11434/api/generate"
    model_ids:
      - "llama3.2"
      - "mistral"
    cost_tier: "free"
    local: true

  - name: "anthropic-claude"
    endpoint: "https://api.anthropic.com/v1/messages"
    model_ids:
      - "claude-3-5-haiku-20241022"
      - "claude-3-5-sonnet-20241022"
    cost_tier: "high"
    local: false

  - name: "openai-gpt"
    endpoint: "https://api.openai.com/v1/chat/completions"
    model_ids:
      - "gpt-4o-mini"
      - "gpt-4o"
    cost_tier: "low"
    local: false
"""


@pytest.fixture
def mock_providers_yaml():
    """Mock the providers YAML file."""
    with patch("pathlib.Path.open", mock_open(read_data=SAMPLE_PROVIDERS_YAML)):
        with patch("pathlib.Path.exists", return_value=True):
            yield


def test_route_local_model(mock_providers_yaml):
    """Test routing to local provider for ollama models."""
    result = route_inference_request(
        prompt="What is the capital of France?",
        model_id="llama3.2",
    )

    assert result["ok"] is True
    assert result["provider"] == "local-ollama"
    assert result["endpoint"] == "http://localhost:11434/api/generate"
    assert result["local"] is True
    assert result["cost_tier"] == "free"
    assert result["errors"] == []


def test_route_external_model(mock_providers_yaml):
    """Test routing to external provider for Anthropic models."""
    result = route_inference_request(
        prompt="Explain quantum entanglement",
        model_id="claude-3-5-haiku-20241022",
    )

    assert result["ok"] is True
    assert result["provider"] == "anthropic-claude"
    assert result["endpoint"] == "https://api.anthropic.com/v1/messages"
    assert result["local"] is False
    assert result["cost_tier"] == "high"
    assert result["errors"] == []


def test_local_compute_first_preference():
    """Test that local providers are preferred when multiple providers support a model."""
    # Add a duplicate model_id to both local and external providers
    yaml_with_duplicate = SAMPLE_PROVIDERS_YAML.replace(
        'model_ids:\n      - "llama3.2"',
        'model_ids:\n      - "llama3.2"\n      - "shared-model"',
    ).replace(
        'model_ids:\n      - "claude-3-5-haiku-20241022"',
        'model_ids:\n      - "claude-3-5-haiku-20241022"\n      - "shared-model"',
    )

    # Patch Path.open to return our modified YAML
    with patch("pathlib.Path.open", mock_open(read_data=yaml_with_duplicate)):
        with patch("pathlib.Path.exists", return_value=True):
            result = route_inference_request(
                prompt="Test prompt",
                model_id="shared-model",
            )

    # Local provider should be selected first
    assert result["ok"] is True
    assert result["local"] is True
    assert result["provider"] == "local-ollama"


def test_invalid_model_id(mock_providers_yaml):
    """Test handling of unknown model_id."""
    result = route_inference_request(
        prompt="Test prompt",
        model_id="nonexistent-model",
    )

    assert result["ok"] is False
    assert result["provider"] is None
    assert len(result["errors"]) == 1
    assert "No provider found" in result["errors"][0]
    assert "nonexistent-model" in result["errors"][0]


def test_missing_provider_config():
    """Test handling when provider config file is missing."""
    with patch("pathlib.Path.exists", return_value=False):
        result = route_inference_request(
            prompt="Test prompt",
            model_id="llama3.2",
        )

    assert result["ok"] is False
    assert result["provider"] is None
    assert len(result["errors"]) == 1
    assert "Failed to load provider config" in result["errors"][0]


def test_list_available_models():
    """Test extraction of available model IDs from provider config."""
    import yaml

    providers = yaml.safe_load(SAMPLE_PROVIDERS_YAML)["providers"]
    models = _list_available_models(providers)

    expected_models = [
        "claude-3-5-haiku-20241022",
        "claude-3-5-sonnet-20241022",
        "gpt-4o",
        "gpt-4o-mini",
        "llama3.2",
        "mistral",
    ]

    assert models == expected_models
    assert len(models) == 6


def test_load_providers_success(mock_providers_yaml):
    """Test successful loading of provider configuration."""
    providers = _load_providers()

    assert len(providers) == 3
    assert providers[0]["name"] == "local-ollama"
    assert providers[1]["name"] == "anthropic-claude"
    assert providers[2]["name"] == "openai-gpt"


def test_load_providers_missing_yaml():
    """Test _load_providers raises FileNotFoundError when config is missing."""
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError, match="Provider config not found"):
            _load_providers()

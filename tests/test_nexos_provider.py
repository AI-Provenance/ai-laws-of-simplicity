# tests/test_nexos_provider.py
import pytest
from experiment.providers import ModelConfig, create_provider


def test_nexos_config_from_string():
    """Test parsing Nexos.ai model string."""
    config = ModelConfig.from_string("nexos/claude-3-5-sonnet")
    assert config.provider == "nexos"
    assert config.model == "claude-3-5-sonnet"


def test_nexos_provider_creation():
    """Test creating Nexos.ai provider (uses OpenAI-compatible API)."""
    config = ModelConfig(
        provider="nexos", model="claude-3-5-sonnet", api_key="test-key"
    )
    provider = create_provider(config)
    assert provider.get_model_name() == "nexos/claude-3-5-sonnet"


def test_nexos_base_url():
    """Test that Nexos.ai provider sets correct base URL."""
    from experiment.providers.openai_provider import OpenAIProvider

    config = ModelConfig(
        provider="nexos", model="claude-3-5-sonnet", api_key="test-key"
    )
    provider = OpenAIProvider(config)
    assert provider.client.base_url.host == "api.nexos.ai"
    assert "v1" in str(provider.client.base_url)


def test_nexos_custom_base_url():
    """Test that custom base_url overrides default Nexos.ai URL."""
    from experiment.providers.openai_provider import OpenAIProvider

    config = ModelConfig(
        provider="nexos",
        model="claude-3-5-sonnet",
        api_key="test-key",
        base_url="https://custom.nexos.ai/v2",
    )
    provider = OpenAIProvider(config)
    assert "custom.nexos.ai" in str(provider.client.base_url)

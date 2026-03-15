import pytest
from experiment.providers import ModelConfig, create_provider


def test_model_config_from_string():
    """Test parsing model string into ModelConfig."""
    config = ModelConfig.from_string("anthropic/claude-3-5-sonnet-20241022")
    assert config.provider == "anthropic"
    assert config.model == "claude-3-5-sonnet-20241022"
    assert config.temperature == 0.0


def test_model_config_with_custom_params():
    """Test ModelConfig with custom parameters."""
    config = ModelConfig.from_string(
        "openai/gpt-4-turbo",
        temperature=0.7,
        max_tokens=2000,
    )
    assert config.provider == "openai"
    assert config.model == "gpt-4-turbo"
    assert config.temperature == 0.7
    assert config.max_tokens == 2000


def test_create_provider_anthropic():
    """Test creating Anthropic provider."""
    config = ModelConfig(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        api_key="test-key",
    )
    provider = create_provider(config)
    assert provider.get_model_name() == "anthropic/claude-3-5-sonnet-20241022"


def test_create_provider_openai():
    """Test creating OpenAI provider."""
    config = ModelConfig(provider="openai", model="gpt-4-turbo", api_key="test-key")
    provider = create_provider(config)
    assert provider.get_model_name() == "openai/gpt-4-turbo"

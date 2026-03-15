from experiment.providers.base import LLMProvider, CompletionResponse
from experiment.providers.config import ModelConfig
from experiment.providers.anthropic_provider import AnthropicProvider
from experiment.providers.openai_provider import OpenAIProvider
from experiment.providers.litellm_provider import LiteLLMProvider


def create_provider(config: ModelConfig) -> LLMProvider:
    """Factory function to create LLM provider from config.

    Args:
        config: ModelConfig with provider and model details

    Returns:
        Initialized LLMProvider instance

    Examples:
        >>> config = ModelConfig.from_string("anthropic/claude-3-5-sonnet-20241022")
        >>> provider = create_provider(config)
    """
    provider_map = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "openrouter": OpenAIProvider,
        "litellm": LiteLLMProvider,
    }

    provider_class = provider_map.get(config.provider)
    if not provider_class:
        raise ValueError(f"Unknown provider: {config.provider}")

    return provider_class(config)


__all__ = [
    "LLMProvider",
    "CompletionResponse",
    "ModelConfig",
    "create_provider",
    "AnthropicProvider",
    "OpenAIProvider",
    "LiteLLMProvider",
]

from dataclasses import dataclass
from typing import Literal, cast


ProviderType = Literal["anthropic", "openai", "openrouter", "litellm"]


@dataclass
class ModelConfig:
    """Configuration for LLM provider and model."""

    provider: ProviderType
    model: str
    temperature: float = 0.0
    max_tokens: int = 4096
    timeout: int = 600

    api_key: str | None = None
    base_url: str | None = None

    @classmethod
    def from_string(cls, model_string: str, **kwargs) -> "ModelConfig":
        """Parse model string like 'anthropic/claude-3-5-sonnet-20241022'.

        Examples:
            - 'anthropic/claude-3-5-sonnet-20241022'
            - 'openai/gpt-4-turbo'
            - 'openrouter/anthropic/claude-3.5-sonnet'
            - 'litellm/openai/gpt-4' (use litellm unified interface)
        """
        if "/" in model_string:
            provider, model = model_string.split("/", 1)
            return cls(provider=cast(ProviderType, provider), model=model, **kwargs)
        else:
            return cls(provider="litellm", model=model_string, **kwargs)

    def get_api_key(self) -> str:
        """Get API key from config or environment."""
        import os

        if self.api_key:
            return self.api_key

        env_var_map = {
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "litellm": "OPENAI_API_KEY",
        }

        env_var = env_var_map.get(self.provider)
        if not env_var:
            raise ValueError(f"Unknown provider: {self.provider}")

        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(f"API key not found in env: {env_var}")

        return api_key

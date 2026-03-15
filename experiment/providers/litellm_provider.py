import logging
import litellm

from experiment.providers.base import LLMProvider, CompletionResponse
from experiment.providers.config import ModelConfig


class LiteLLMProvider(LLMProvider):
    """Universal provider using LiteLLM for any model/provider."""

    def __init__(self, config: ModelConfig):
        self.config = config

        import os

        if config.api_key:
            provider_upper = config.provider.upper()
            os.environ[f"{provider_upper}_API_KEY"] = config.api_key

        if config.base_url:
            litellm.api_base = config.base_url

    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> CompletionResponse:
        """Generate completion using LiteLLM."""

        temperature = temperature or self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = litellm.completion(
                model=self.config.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return CompletionResponse(
                content=response.choices[0].message.content or "",
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                model=response.model,
                finish_reason=response.choices[0].finish_reason,
            )
        except Exception as e:
            logging.error(f"LiteLLM API error: {e}")
            raise

    def get_model_name(self) -> str:
        return f"litellm/{self.config.model}"

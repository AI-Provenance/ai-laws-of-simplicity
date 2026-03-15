import logging
from anthropic import Anthropic

from experiment.providers.base import LLMProvider, CompletionResponse
from experiment.providers.config import ModelConfig


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = Anthropic(api_key=config.get_api_key())

    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> CompletionResponse:
        """Generate completion using Claude."""

        temperature = temperature or self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens

        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.config.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        try:
            response = self.client.messages.create(**kwargs)

            return CompletionResponse(
                content=response.content[0].text,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                model=response.model,
                finish_reason=response.stop_reason,
            )
        except Exception as e:
            logging.error(f"Anthropic API error: {e}")
            raise

    def get_model_name(self) -> str:
        return f"anthropic/{self.config.model}"

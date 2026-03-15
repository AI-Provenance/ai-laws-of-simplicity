import logging
from openai import OpenAI

from experiment.providers.base import LLMProvider, CompletionResponse
from experiment.providers.config import ModelConfig


class OpenAIProvider(LLMProvider):
    """OpenAI GPT API provider."""

    def __init__(self, config: ModelConfig):
        self.config = config
        kwargs = {"api_key": config.get_api_key()}
        if config.base_url:
            kwargs["base_url"] = config.base_url
        self.client = OpenAI(**kwargs)

    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> CompletionResponse:
        """Generate completion using GPT."""

        temperature = temperature or self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
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
            logging.error(f"OpenAI API error: {e}")
            raise

    def get_model_name(self) -> str:
        return f"openai/{self.config.model}"

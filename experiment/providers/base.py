from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CompletionResponse:
    """Response from LLM completion."""

    content: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    finish_reason: str | None = None

    def __post_init__(self):
        if self.total_tokens == 0:
            self.total_tokens = self.input_tokens + self.output_tokens


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> CompletionResponse:
        """Generate completion for given prompt.

        Args:
            prompt: User message
            system_prompt: System message (optional)
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            CompletionResponse with content and token counts
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model identifier."""
        pass

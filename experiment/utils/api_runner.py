import logging
import time
from pathlib import Path
from typing import Any

from experiment.providers import create_provider, ModelConfig, CompletionResponse


class APIRunner:
    """Runs LLM tasks using direct API calls instead of OpenCode CLI."""

    def __init__(self, model_config: ModelConfig):
        """Initialize API runner.

        Args:
            model_config: Configuration for LLM provider and model
        """
        self.model_config = model_config
        self.provider = create_provider(model_config)

    def create_fresh_context(self, skills: list[Path] | None = None) -> dict[str, Any]:
        """Create context with skills loaded.

        Args:
            skills: List of skill file paths to load

        Returns:
            Context dict with skill_content
        """
        skill_content = ""

        if skills:
            for skill_path in skills:
                if skill_path.exists():
                    skill_content += f"\n\n# {skill_path.name}\n\n"
                    skill_content += skill_path.read_text()
                else:
                    logging.warning(f"Skill file not found: {skill_path}")

        return {
            "skill_content": skill_content.strip(),
            "model": self.provider.get_model_name(),
        }

    def run_agent(
        self,
        ctx: dict[str, Any],
        task_prompt: str,
        timeout: int = 600,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Run LLM on task with optional skill injection.

        Args:
            ctx: Context from create_fresh_context
            task_prompt: The task to solve
            max_tokens: Maximum tokens to generate (uses config default if None)
            timeout: Timeout in seconds (currently unused for API calls)

        Returns:
            Dict with input_tokens, output_tokens, output, iterations
        """
        start_time = time.time()

        system_prompt = None
        if ctx.get("skill_content"):
            system_prompt = (
                "You are an expert software engineer. Follow these guidelines:\n\n"
                + ctx["skill_content"]
            )

        try:
            response: CompletionResponse = self.provider.complete(
                prompt=task_prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
            )

            return {
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "output": response.content,
                "iterations": 1,
                "return_code": 0,
                "time_seconds": time.time() - start_time,
            }

        except Exception as e:
            logging.error(f"API call failed: {e}")
            return {
                "input_tokens": 0,
                "output_tokens": 0,
                "output": "",
                "iterations": 0,
                "return_code": 1,
                "error": str(e),
                "time_seconds": time.time() - start_time,
            }

    def cleanup(self, ctx: dict[str, Any]) -> None:
        """Cleanup context (no-op for API runner)."""
        pass

# experiment/utils/isolation.py
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class IsolatedRunner:
    """Runs agent in isolated environment to ensure fresh context."""

    def __init__(
        self,
        agent_command: str = "opencode",
        skills_dir: Path | None = None,
        container_image: str | None = None,
    ):
        """Initialize isolated runner.

        Args:
            agent_command: Command to invoke the agent
            skills_dir: Directory containing skill files
            container_image: Docker image for isolation (optional)
        """
        self.agent_command = agent_command
        self.skills_dir = skills_dir
        self.container_image = container_image

    def create_fresh_context(self) -> dict[str, Any]:
        """Create a fresh context for agent run.

        Returns:
            Context dict with temporary directory and environment
        """
        temp_dir = tempfile.mkdtemp(prefix="experiment_run_")

        env = os.environ.copy()
        env["OPENCODE_CONTEXT_DIR"] = temp_dir
        env["OPENCODE_NO_CACHE"] = "1"

        return {
            "temp_dir": temp_dir,
            "env": env,
            "skills_loaded": [],
        }

    def load_skill(self, ctx: dict, skill_path: Path) -> None:
        """Load a skill into the context.

        Args:
            ctx: Context from create_fresh_context
            skill_path: Path to skill markdown file
        """
        ctx["skills_loaded"].append(str(skill_path))

    def run_agent(
        self,
        ctx: dict,
        task_prompt: str,
        max_tokens: int = 100000,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Run agent with specified context and prompt.

        Args:
            ctx: Context from create_fresh_context
            task_prompt: The task to solve
            max_tokens: Maximum tokens to generate
            timeout: Timeout in seconds

        Returns:
            Dict with input_tokens, output_tokens, output, iterations
        """
        cmd = [self.agent_command]

        for skill_path in ctx["skills_loaded"]:
            cmd.extend(["--skill", str(skill_path)])

        result = subprocess.run(
            cmd,
            input=task_prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=ctx["env"],
            cwd=ctx["temp_dir"],
        )

        input_tokens = self._extract_token_count(result.stderr, "input")
        output_tokens = self._extract_token_count(result.stderr, "output")
        iterations = result.stderr.count("ITERATION_START")

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "output": result.stdout,
            "iterations": iterations,
            "return_code": result.returncode,
        }

    def _extract_token_count(self, log_text: str, token_type: str) -> int:
        """Extract token count from agent logs.

        This is a placeholder - actual implementation depends on
        agent's log format.
        """
        pattern = rf"{token_type}_tokens:\s*(\d+)"
        match = re.search(pattern, log_text)
        if match:
            return int(match.group(1))
        return 0

    def cleanup(self, ctx: dict) -> None:
        """Clean up temporary context."""
        if Path(ctx["temp_dir"]).exists():
            shutil.rmtree(ctx["temp_dir"])

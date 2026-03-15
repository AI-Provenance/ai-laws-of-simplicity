# experiment/utils/isolation.py
import json
import logging
import os
import re
import shutil
import sqlite3
import subprocess
import tempfile
import time
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
        # Record timestamp before agent run
        start_time = time.time() * 1000  # OpenCode uses milliseconds

        cmd = [self.agent_command, "--no-tui"]  # Use non-interactive mode

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

        # Extract tokens from OpenCode database
        tokens = self._extract_tokens_from_db(start_time)

        # Count iterations (if agent logs them)
        iterations = result.stderr.count("ITERATION_START")

        return {
            "input_tokens": tokens["input"],
            "output_tokens": tokens["output"],
            "output": result.stdout,
            "iterations": max(iterations, 1),  # At least 1 iteration
            "return_code": result.returncode,
        }

    def _extract_tokens_from_db(self, start_time: float) -> dict[str, int]:
        """Extract token counts from OpenCode database.

        Queries the OpenCode SQLite database for messages created after start_time
        and sums up token usage.

        Args:
            start_time: Timestamp in milliseconds when agent run started

        Returns:
            Dict with 'input', 'output', 'cache_read', 'cache_write' token counts
        """
        db_path = Path.home() / ".local/share/opencode/opencode.db"

        if not db_path.exists():
            logging.warning(f"OpenCode database not found at {db_path}")
            return {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Query messages created after start_time with assistant role
            cursor.execute(
                """
                SELECT data
                FROM message
                WHERE time_created >= ?
                AND json_extract(data, '$.role') = 'assistant'
                ORDER BY time_created DESC
                LIMIT 10
            """,
                (int(start_time),),
            )

            rows = cursor.fetchall()
            conn.close()

            # Sum up tokens from all relevant messages
            total_input = 0
            total_output = 0
            total_cache_read = 0
            total_cache_write = 0

            for row in rows:
                try:
                    data = json.loads(row[0])
                    tokens = data.get("tokens", {})
                    total_input += tokens.get("input", 0)
                    total_output += tokens.get("output", 0)
                    cache = tokens.get("cache", {})
                    total_cache_read += cache.get("read", 0)
                    total_cache_write += cache.get("write", 0)
                except (json.JSONDecodeError, KeyError) as e:
                    logging.warning(f"Failed to parse message data: {e}")
                    continue

            return {
                "input": total_input,
                "output": total_output,
                "cache_read": total_cache_read,
                "cache_write": total_cache_write,
            }

        except Exception as e:
            logging.error(f"Failed to extract tokens from OpenCode database: {e}")
            return {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}

    def _extract_token_count(self, log_text: str, token_type: str) -> int:
        """Deprecated: Use _extract_tokens_from_db instead.

        This method is kept for backwards compatibility but always returns 0.
        Token extraction now happens via OpenCode database query.
        """
        return 0

    def cleanup(self, ctx: dict) -> None:
        """Clean up temporary context."""
        if Path(ctx["temp_dir"]).exists():
            shutil.rmtree(ctx["temp_dir"])

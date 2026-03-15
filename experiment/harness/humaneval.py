import json
import random
from pathlib import Path
from typing import Any

from .base import BenchmarkHarness, TaskSpec


class HumanEvalHarness(BenchmarkHarness):
    """Harness for HumanEval benchmark."""

    def __init__(self, data_path: Path | None = None):
        """Initialize HumanEval harness.

        Args:
            data_path: Path to HumanEval dataset (optional, downloads if not provided)
        """
        self.data_path = data_path
        self._tasks_cache: dict[str, TaskSpec] | None = None

    def _load_dataset(self) -> list[dict[str, Any]]:
        """Load HumanEval dataset."""
        from datasets import load_dataset

        dataset = load_dataset("openai/humaneval", split="test")
        return [item for item in dataset]

    def load_tasks(self, num_tasks: int, seed: int) -> list[TaskSpec]:
        """Load a random sample of HumanEval tasks.

        Difficulty based on expected solution length:
        - Simple: <10 lines
        - Medium: 10-50 lines
        - Complex: >50 lines (rare in HumanEval)
        """
        all_tasks = self._load_dataset()

        rng = random.Random(seed)
        sampled = rng.sample(all_tasks, min(num_tasks, len(all_tasks)))

        task_specs = []
        for task in sampled:
            # HumanEval tasks are mostly simple
            # Estimate from canonical solution if available
            canonical = task.get("canonical_solution", "")
            lines = len(canonical.split("\n")) if canonical else 10

            if lines < 10:
                difficulty = "simple"
            elif lines <= 50:
                difficulty = "medium"
            else:
                difficulty = "complex"

            spec = TaskSpec(
                task_id=task["task_id"],
                benchmark="human_eval",
                prompt=task["prompt"],
                test_file=None,
                expected_solution=canonical,
                difficulty=difficulty,
                function_signature=task["prompt"].split("\n")[0],
                test_cases=None,  # HumanEval uses test column in dataset
            )
            task_specs.append(spec)

        self._tasks_cache = {t.task_id: t for t in task_specs}
        return task_specs

    def verify_solution(self, task: TaskSpec, solution_path: Path) -> bool:
        """Verify solution using HumanEval test runner."""
        import subprocess

        try:
            # HumanEval uses exec-based testing
            result = subprocess.run(
                ["python", "-m", "human_eval.execution", str(solution_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_task_metadata(self, task_id: str) -> dict[str, Any]:
        """Get HumanEval task metadata."""
        if self._tasks_cache and task_id in self._tasks_cache:
            task = self._tasks_cache[task_id]
            return {
                "difficulty": task.difficulty,
                "function_signature": task.function_signature,
            }
        return {}

import json
import random
from pathlib import Path
from typing import Any

from .base import BenchmarkHarness, TaskSpec


class SWEBenchHarness(BenchmarkHarness):
    """Harness for SWE-bench Lite benchmark."""

    def __init__(self, data_path: Path | None = None):
        """Initialize SWE-bench harness.

        Args:
            data_path: Path to SWE-bench dataset (optional, downloads if not provided)
        """
        self.data_path = data_path
        self._tasks_cache: dict[str, TaskSpec] | None = None

    def _load_dataset(self) -> list[dict[str, Any]]:
        """Load SWE-bench Lite dataset."""
        from datasets import load_dataset

        dataset = load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
        return [item for item in dataset]

    def load_tasks(self, num_tasks: int, seed: int) -> list[TaskSpec]:
        """Load a random sample of SWE-bench tasks.

        Simple/Medium/Complex classification based on patches:
        - Simple: <10 lines changed
        - Medium: 10-50 lines changed
        - Complex: >50 lines changed
        """
        all_tasks = self._load_dataset()

        rng = random.Random(seed)
        sampled = rng.sample(all_tasks, min(num_tasks, len(all_tasks)))

        task_specs = []
        for task in sampled:
            # Estimate difficulty from patch
            patch = task.get("patch", "")
            lines_changed = len(patch.split("\n")) if patch else 0

            if lines_changed < 10:
                difficulty = "simple"
            elif lines_changed <= 50:
                difficulty = "medium"
            else:
                difficulty = "complex"

            spec = TaskSpec(
                task_id=task["instance_id"],
                benchmark="swe_bench_lite",
                prompt=task["problem_statement"],
                test_file=None,  # SWE-bench has test_patch
                expected_solution=task.get("patch"),
                difficulty=difficulty,
                repo=task.get("repo", ""),
                base_commit=task.get("base_commit"),
                problem_statement=task["problem_statement"],
            )
            task_specs.append(spec)

        # Cache tasks outside the loop
        self._tasks_cache = {t.task_id: t for t in task_specs}

        return task_specs

    def verify_solution(self, task: TaskSpec, solution_path: Path) -> bool:
        """Verify solution using SWE-bench test harness."""
        from swebench.metrics import get_test_results

        try:
            # SWE-bench requires test_patch from the instance
            # The solution_path should be a repo with the patch applied
            results = get_test_results(
                instance_id=task.task_id,
                test_patch=task.expected_solution or "",  # Use patch from task
                repo_path=str(solution_path),
            )
            return results.get("passed", 0) == results.get("total", 1)
        except Exception:
            return False

    def get_task_metadata(self, task_id: str) -> dict[str, Any]:
        """Get SWE-bench task metadata."""
        if self._tasks_cache and task_id in self._tasks_cache:
            task = self._tasks_cache[task_id]
            return {
                "difficulty": task.difficulty,
                "repo": task.repo,
                "base_commit": task.base_commit,
            }
        return {}

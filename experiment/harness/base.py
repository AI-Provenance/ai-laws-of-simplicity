from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class TaskResult:
    """Result from running a single task."""

    task_id: str
    benchmark: str
    condition: str  # "control" or "treatment"

    # Token metrics
    input_tokens: int
    output_tokens: int
    total_tokens: int

    # Secondary metrics
    success: bool
    time_seconds: float
    iterations: int

    # Metadata
    error: str | None = None
    output_files: list[Path] | None = None


@dataclass
class TaskSpec:
    """Specification for a benchmark task."""

    task_id: str
    benchmark: str
    prompt: str
    test_file: Path | None
    expected_solution: str | None
    difficulty: str  # "simple", "medium", "complex"

    # SWE-bench specific
    repo: str | None = None
    base_commit: str | None = None
    problem_statement: str | None = None

    # HumanEval specific
    function_signature: str | None = None
    test_cases: list[str] | None = None


class BenchmarkHarness(ABC):
    """Abstract base class for benchmark harnesses."""

    @abstractmethod
    def load_tasks(self, num_tasks: int, seed: int) -> list[TaskSpec]:
        """Load a random sample of tasks from the benchmark.

        Args:
            num_tasks: Number of tasks to sample
            seed: Random seed for reproducibility

        Returns:
            List of TaskSpec objects
        """
        pass

    @abstractmethod
    def verify_solution(self, task: TaskSpec, solution_path: Path) -> bool:
        """Verify that a solution passes the task's tests.

        Args:
            task: Task specification
            solution_path: Path to generated solution

        Returns:
            True if solution passes all tests
        """
        pass

    @abstractmethod
    def get_task_metadata(self, task_id: str) -> dict[str, Any]:
        """Get metadata for a specific task.

        Args:
            task_id: Task identifier

        Returns:
            Dictionary with task metadata (difficulty, lines_changed, etc.)
        """
        pass

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class ExperimentConfig:
    """Configuration for A/B experiment."""

    benchmarks: list[Literal["swe_bench_lite", "human_eval"]]
    num_tasks_per_benchmark: int = 100

    agent_model: str = "opencode-go/glm-5"
    temperature: float = 0.0
    timeout_seconds: int = 600

    conditions: tuple[str, str] = ("control", "treatment")

    control_skills: list[Path] = []
    treatment_skills: list[Path] = [Path("skills/laws-of-simplicity/SKILL.md")]

    raw_data_dir: Path = Path("data/raw")
    results_dir: Path = Path("data/results")

    random_seed: int = 42
    counterbalance: bool = True

    required_sample_size: int = 90
    planned_sample_size: int = 100


DEFAULT_CONFIG = ExperimentConfig(benchmarks=["swe_bench_lite", "human_eval"])

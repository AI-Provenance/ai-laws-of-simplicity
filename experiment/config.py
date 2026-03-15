from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass
class ExperimentConfig:
    """Configuration for A/B experiment to measure the impact of Laws of Simplicity skill.

    Controls treatment assignment, skill loading, and sample sizes for the RCT.
    Sample sizes based on G*Power: d=0.3, α=0.05, power=0.80 requires n=90.
    """

    benchmarks: list[Literal["swe_bench_lite", "human_eval"]]
    num_tasks_per_benchmark: int = 100

    runner_type: Literal["api", "cli"] = "api"

    model_string: str = "anthropic/claude-3-5-sonnet-20241022"
    temperature: float = 0.0
    max_tokens: int = 4096
    timeout_seconds: int = 600

    agent_model: str = "opencode-go/glm-5"

    conditions: tuple[str, str] = ("control", "treatment")

    control_skills: list[Path] = field(default_factory=list)
    treatment_skills: list[Path] = field(
        default_factory=lambda: [Path("skills/laws-of-simplicity/SKILL.md")]
    )

    raw_data_dir: Path = Path("data/raw")
    results_dir: Path = Path("data/results")

    random_seed: int = 42
    counterbalance: bool = True

    required_sample_size: int = 90
    planned_sample_size: int = 100


DEFAULT_CONFIG = ExperimentConfig(
    benchmarks=["swe_bench_lite"],
    runner_type="api",
    model_string="anthropic/claude-3-5-sonnet-20241022",
)

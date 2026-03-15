# experiment/runner.py
import json
from pathlib import Path
from typing import Any

from experiment.config import DEFAULT_CONFIG, ExperimentConfig
from experiment.harness.base import TaskSpec
from experiment.harness.humaneval import HumanEvalHarness
from experiment.harness.swe_bench import SWEBenchHarness
from experiment.metrics.collector import MetricsCollector
from experiment.utils.isolation import IsolatedRunner


class ExperimentRunner:
    """Orchestrates A/B experiments across benchmarks."""

    def __init__(self, config: ExperimentConfig | None = None):
        """Initialize experiment runner.

        Args:
            config: Experiment configuration (uses default if not provided)
        """
        self.config = config or DEFAULT_CONFIG
        self.config.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.config.results_dir.mkdir(parents=True, exist_ok=True)

        self.collector = MetricsCollector(self.config.raw_data_dir)

        if self.config.runner_type == "api":
            from experiment.utils.api_runner import APIRunner
            from experiment.providers import ModelConfig

            model_config = ModelConfig.from_string(
                self.config.model_string,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout_seconds,
            )
            self.runner = APIRunner(model_config)
        elif self.config.runner_type == "cli":
            from experiment.utils.isolation import IsolatedRunner

            if not self.config.agent_model:
                raise ValueError("agent_model must be specified when runner_type='cli'")

            self.runner = IsolatedRunner(
                agent_command=self.config.agent_model,
                skills_dir=Path("skills"),
            )
        elif self.config.runner_type == "mini_agent":
            from experiment.mini_agent.runner import MiniAgentRunner
            from experiment.providers import ModelConfig

            model_config = ModelConfig.from_string(self.config.model_string)
            # Convert to litellm model name format
            litellm_model = f"{model_config.provider}/{model_config.model}"

            self.runner = MiniAgentRunner(
                model_name=litellm_model,
                step_limit=self.config.step_limit,
                cost_limit=self.config.cost_limit,
                temperature=self.config.temperature,
                output_dir=self.config.raw_data_dir,
            )

        self.harnesses: dict[str, Any] = {}
        if "swe_bench_lite" in self.config.benchmarks:
            self.harnesses["swe_bench_lite"] = SWEBenchHarness()
        if "human_eval" in self.config.benchmarks:
            self.harnesses["human_eval"] = HumanEvalHarness()

        self.task_metadata: dict[str, dict[str, Any]] = {}

    def run(self) -> None:
        """Run the full experiment."""
        # Print relevant config info
        print(f"Starting experiment:")
        print(f"  Runner: {self.config.runner_type}")
        if self.config.runner_type in ("api", "mini_agent"):
            print(f"  Model: {self.config.model_string}")
            print(f"  Temperature: {self.config.temperature}")
        if self.config.runner_type == "mini_agent":
            print(f"  Step limit: {self.config.step_limit}")
            print(f"  Cost limit: ${self.config.cost_limit}")
        if self.config.runner_type == "cli":
            print(f"  Agent: {self.config.agent_model}")
        print(f"  Benchmarks: {', '.join(self.config.benchmarks)}")
        print(f"  Tasks per benchmark: {self.config.num_tasks_per_benchmark}")
        print(f"  Conditions: {', '.join(self.config.conditions)}")

        for benchmark_name in self.config.benchmarks:
            print(f"\n=== Running {benchmark_name} ===")
            harness = self.harnesses[benchmark_name]

            tasks = harness.load_tasks(
                self.config.num_tasks_per_benchmark,
                self.config.random_seed,
            )
            print(f"Loaded {len(tasks)} tasks")

            for task in tasks:
                self.task_metadata[task.task_id] = {
                    "benchmark": task.benchmark,
                    "difficulty": task.difficulty,
                }

            for i, task in enumerate(tasks, 1):
                print(f"\n[{i}/{len(tasks)}] Task: {task.task_id}")
                self._run_task(task, harness)

        print("\n=== Aggregating results ===")
        self.collector.to_csv(self.config.results_dir / "aggregate_results.csv")

        with open(self.config.results_dir / "task_metadata.json", "w") as f:
            json.dump(self.task_metadata, f, indent=2)

        print(f"Results saved to {self.config.results_dir}")

    def _run_task(self, task: TaskSpec, harness: Any) -> None:
        """Run a single task in both conditions.

        Uses counterbalanced design: hash(task_id) % 2 determines condition order.
        """
        if hash(task.task_id) % 2 == 0:
            conditions = ["control", "treatment"]
        else:
            conditions = ["treatment", "control"]

        solution_paths = {}

        for condition in conditions:
            print(f"  Running {condition}...")

            # Create context and load skills based on runner type
            if self.config.runner_type == "api":
                # API runner: pass skills to create_fresh_context
                skills = (
                    self.config.treatment_skills
                    if condition == "treatment"
                    else self.config.control_skills
                )
                # Type assertion for API runner
                from experiment.utils.api_runner import APIRunner

                assert isinstance(self.runner, APIRunner)
                ctx = self.runner.create_fresh_context(skills=skills)
            else:
                # CLI runner (IsolatedRunner)
                from experiment.utils.isolation import IsolatedRunner

                assert isinstance(self.runner, IsolatedRunner)
                ctx = self.runner.create_fresh_context()
                if condition == "treatment":
                    for skill_path in self.config.treatment_skills:
                        self.runner.load_skill(ctx, skill_path)

            metrics_ctx = self.collector.start_run(
                task.task_id,
                task.benchmark,
                condition,
            )

            try:
                result = self.runner.run_agent(
                    ctx,
                    task.prompt,
                    timeout=self.config.timeout_seconds,
                )

                self.collector.update_tokens(
                    metrics_ctx,
                    result["input_tokens"],
                    result["output_tokens"],
                )
                for _ in range(result["iterations"]):
                    self.collector.increment_iteration(metrics_ctx)

                # For verification, write solution to temp file
                import tempfile

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".txt", delete=False
                ) as f:
                    f.write(result["output"])
                    solution_path = Path(f.name)

                solution_paths[condition] = solution_path

                try:
                    success = harness.verify_solution(task, solution_path)
                except Exception as verify_error:
                    print(f"  Verification error: {verify_error}")
                    success = False
                finally:
                    # Clean up temp file
                    if solution_path.exists():
                        solution_path.unlink()

                self.collector.end_run(metrics_ctx, success=success)

            except Exception as e:
                print(f"  ERROR: {e}")
                self.collector.end_run(metrics_ctx, success=False, error=str(e))

            finally:
                self.runner.cleanup(ctx)

    def analyze(self) -> dict[str, Any]:
        """Run statistical analysis on collected results."""
        from experiment.metrics.analyzer import run_full_analysis

        results_csv = self.config.results_dir / "aggregate_results.csv"
        metadata_json = self.config.results_dir / "task_metadata.json"

        with open(metadata_json) as f:
            metadata = json.load(f)

        results = run_full_analysis(results_csv, metadata)

        return {
            "token_analysis": {
                "mean_control": results.token_mean_control,
                "mean_treatment": results.token_mean_treatment,
                "mean_diff": results.token_mean_diff,
                "p_value": results.token_p_value,
                "cohens_d": results.token_cohens_d,
                "ci_95": [results.token_ci_lower, results.token_ci_upper],
            },
            "success_analysis": {
                "rate_control": results.success_rate_control,
                "rate_treatment": results.success_rate_treatment,
                "p_value": results.success_p_value,
            },
            "difficulty_analysis": results.token_diff_by_difficulty,
            "time_analysis": {
                "median_control": results.time_median_control,
                "median_treatment": results.time_median_treatment,
                "effect_size": results.time_effect_size,
            },
        }


def main():
    """Entry point for experiment runner with CLI argument parsing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run LLM experiment with Laws of Simplicity skill"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="anthropic/claude-3-5-sonnet-20241022",
        help="Model string (e.g., 'nexos/claude-4-5-sonnet', 'anthropic/claude-3-5-sonnet-20241022')",
    )
    parser.add_argument(
        "--benchmarks",
        type=str,
        nargs="+",
        default=["swe_bench_lite"],
        choices=["swe_bench_lite", "human_eval"],
        help="Benchmarks to run",
    )
    parser.add_argument(
        "--num-tasks", type=int, default=100, help="Number of tasks per benchmark"
    )
    parser.add_argument(
        "--runner-type",
        type=str,
        default="api",
        choices=["api", "cli", "mini_agent"],
        help="Runner type (api for direct API calls, cli for OpenCode, mini_agent for mini-swe-agent)",
    )
    parser.add_argument(
        "--temperature", type=float, default=0.0, help="LLM temperature"
    )
    parser.add_argument(
        "--timeout", type=int, default=600, help="Timeout in seconds per task"
    )

    args = parser.parse_args()

    config = ExperimentConfig(
        benchmarks=args.benchmarks,
        num_tasks_per_benchmark=args.num_tasks,
        runner_type=args.runner_type,
        model_string=args.model,
        temperature=args.temperature,
        timeout_seconds=args.timeout,
    )

    runner = ExperimentRunner(config)
    runner.run()
    analysis = runner.analyze()

    print("\n=== Analysis Summary ===")

    # Primary Metric: Wall-Clock Time-to-Completion
    time_diff = (
        analysis["time_analysis"]["median_treatment"]
        - analysis["time_analysis"]["median_control"]
    )
    time_pct = (time_diff / analysis["time_analysis"]["median_control"]) * 100
    print(f"⏱️  Time-to-Completion (PRIMARY METRIC):")
    print(f"  Control:   {analysis['time_analysis']['median_control']:.1f}s (median)")
    print(f"  Treatment: {analysis['time_analysis']['median_treatment']:.1f}s (median)")
    print(f"  Difference: {time_diff:+.1f}s ({time_pct:+.1f}%)")
    print(f"  Effect size: {analysis['time_analysis']['effect_size']:.3f}")

    # Secondary Metric: Token Usage (cost)
    token_diff = analysis["token_analysis"]["mean_diff"]
    token_pct = (token_diff / analysis["token_analysis"]["mean_control"]) * 100
    print(f"\n💰 Token Usage (cost proxy):")
    print(
        f"  Control:   {analysis['token_analysis']['mean_control']:.0f} tokens (mean)"
    )
    print(
        f"  Treatment: {analysis['token_analysis']['mean_treatment']:.0f} tokens (mean)"
    )
    print(f"  Difference: {token_diff:+.0f} tokens ({token_pct:+.1f}%)")
    print(f"  p-value: {analysis['token_analysis']['p_value']:.4f}")
    print(f"  Cohen's d: {analysis['token_analysis']['cohens_d']:.3f}")

    # Quality Metric: Success Rate
    print(f"\n✅ Success Rate:")
    print(f"  Control:   {analysis['success_analysis']['rate_control']:.1%}")
    print(f"  Treatment: {analysis['success_analysis']['rate_treatment']:.1%}")

    with open(runner.config.results_dir / "analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"\nFull analysis saved to {runner.config.results_dir / 'analysis.json'}")


if __name__ == "__main__":
    main()

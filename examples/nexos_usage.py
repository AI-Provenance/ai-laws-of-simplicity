#!/usr/bin/env python3
"""Example: Using Nexos.ai API for the experiment.

This example shows how to run the experiment using Nexos.ai's API
with the Laws of Simplicity skill.
"""

from experiment.config import ExperimentConfig
from experiment.runner import ExperimentRunner

# Configure experiment with Nexos.ai
config = ExperimentConfig(
    benchmarks=["swe_bench_lite"],
    num_tasks_per_benchmark=5,
    runner_type="api",
    model_string="nexos/claude-3-5-sonnet",  # Nexos.ai model
    timeout_seconds=120,
)

# Run experiment
runner = ExperimentRunner(config)
runner.run()

# Analyze results
analysis = runner.analyze()
print(f"\nToken reduction: {analysis['token_analysis']['reduction_percentage']:.1f}%")
print(f"Cohen's d: {analysis['token_analysis']['cohens_d']:.3f}")

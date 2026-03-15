#!/usr/bin/env python3

"""Pilot test for API-based experiment runner.

Tests end-to-end flow with 2 tasks from SWE-bench Lite.
Requires ANTHROPIC_API_KEY or OPENAI_API_KEY in environment.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiment.config import ExperimentConfig
from experiment.runner import ExperimentRunner


def main():
    """Run pilot with 2 tasks."""
    print("=" * 60)
    print("API Runner Pilot Test")
    print("=" * 60)

    import os

    if os.getenv("ANTHROPIC_API_KEY"):
        model_string = "anthropic/claude-3-5-sonnet-20241022"
    elif os.getenv("OPENAI_API_KEY"):
        model_string = "openai/gpt-4-turbo"
    else:
        print("ERROR: Set ANTHROPIC_API_KEY or OPENAI_API_KEY")
        return 1

    config = ExperimentConfig(
        benchmarks=["swe_bench_lite"],
        num_tasks_per_benchmark=2,
        runner_type="api",
        model_string=model_string,
        timeout_seconds=120,
    )

    runner = ExperimentRunner(config)
    runner.run()

    results_file = config.results_dir / "aggregate_results.csv"
    if results_file.exists():
        import pandas as pd

        df = pd.read_csv(results_file)

        print("\n" + "=" * 60)
        print("Results Summary:")
        print("=" * 60)
        print(f"Total runs: {len(df)}")
        print(f"Successful: {df['success'].sum()}")
        print(f"Total input tokens: {df['input_tokens'].sum()}")
        print(f"Total output tokens: {df['output_tokens'].sum()}")
        print("\nPer-condition breakdown:")
        print(df.groupby("condition")[["input_tokens", "output_tokens"]].sum())

        if df["input_tokens"].sum() == 0:
            print("\n⚠️  WARNING: No tokens recorded!")
            return 1
        else:
            print("\n✅ SUCCESS: Tokens recorded correctly!")
            return 0
    else:
        print(f"\n❌ ERROR: Results file not found: {results_file}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

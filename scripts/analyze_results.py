#!/usr/bin/env python3
# scripts/analyze_results.py
# Post-experiment statistical analysis

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiment.config import DEFAULT_CONFIG
from experiment.runner import ExperimentRunner


def main():
    """Analyze existing results without re-running experiments."""
    runner = ExperimentRunner(DEFAULT_CONFIG)

    results_csv = runner.config.results_dir / "aggregate_results.csv"
    if not results_csv.exists():
        print(f"Error: No results found at {results_csv}")
        print("Run the experiment first: ./scripts/run_experiment.sh")
        sys.exit(1)

    analysis = runner.analyze()

    generate_figures(runner.config.results_dir, analysis)

    print("Analysis complete. See:")
    print(f"  - {runner.config.results_dir / 'analysis.json'}")
    print(f"  - {runner.config.results_dir / 'figures/'}")


def generate_figures(output_dir: Path, analysis: dict) -> None:
    """Generate paper figures."""
    import pandas as pd

    figures_dir = output_dir / "figures"
    figures_dir.mkdir(exist_ok=True)

    df = pd.read_csv(output_dir / "aggregate_results.csv")

    # Figure 1: Token reduction distribution
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6))
    control = df[df["condition"] == "control"]["total_tokens"]
    treatment = df[df["condition"] == "treatment"]["total_tokens"]

    ax.hist(control, bins=30, alpha=0.6, label="Control", color="blue")
    ax.hist(treatment, bins=30, alpha=0.6, label="Treatment", color="green")
    ax.axvline(
        control.mean(),
        color="blue",
        linestyle="--",
        label=f"Control mean: {control.mean():.0f}",
    )
    ax.axvline(
        treatment.mean(),
        color="green",
        linestyle="--",
        label=f"Treatment mean: {treatment.mean():.0f}",
    )
    ax.set_xlabel("Total Tokens")
    ax.set_ylabel("Frequency")
    ax.set_title("Token Distribution: Control vs Treatment")
    ax.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "figure1_token_distribution.png", dpi=150)
    plt.close()

    # Figure 2: Time-to-completion histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    time_control = df[df["condition"] == "control"]["time_seconds"]
    time_treatment = df[df["condition"] == "treatment"]["time_seconds"]

    ax.hist(time_control, bins=30, alpha=0.6, label="Control", color="blue")
    ax.hist(time_treatment, bins=30, alpha=0.6, label="Treatment", color="green")
    ax.axvline(time_control.median(), color="blue", linestyle="--")
    ax.axvline(time_treatment.median(), color="green", linestyle="--")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Frequency")
    ax.set_title("Time-to-Completion Distribution")
    ax.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "figure2_time_distribution.png", dpi=150)
    plt.close()

    print(f"Figures saved to {figures_dir}")


if __name__ == "__main__":
    main()

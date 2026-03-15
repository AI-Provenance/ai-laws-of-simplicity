from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class AnalysisResults:
    """Results from statistical analysis."""

    # RQ1: Token reduction
    token_mean_control: float
    token_mean_treatment: float
    token_mean_diff: float
    token_p_value: float
    token_cohens_d: float
    token_ci_lower: float
    token_ci_upper: float

    # RQ2: Success rate
    success_rate_control: float
    success_rate_treatment: float
    success_p_value: float  # McNemar's test

    # RQ3: By difficulty
    token_diff_by_difficulty: dict[str, Any]

    # Time distribution
    time_median_control: float
    time_median_treatment: float
    time_effect_size: float  # Rank-biserial correlation


def load_results(csv_path: Path) -> pd.DataFrame:
    """Load results from CSV."""
    return pd.read_csv(csv_path)


def paired_token_test(df: pd.DataFrame) -> tuple[float, float, float, float, float]:
    """Run paired t-test for token reduction (RQ1).

    Returns:
        Tuple of (mean_diff, p_value, cohens_d, ci_lower, ci_upper)
    """
    control = df[df["condition"] == "control"]["total_tokens"]
    treatment = df[df["condition"] == "treatment"]["total_tokens"]

    # Validate paired data
    if len(control) != len(treatment):
        raise ValueError(
            f"Paired test requires equal sample sizes: control={len(control)}, treatment={len(treatment)}"
        )

    # Paired t-test (tasks are paired)
    t_stat, p_value = stats.ttest_rel(control, treatment)

    # Effect size (Cohen's d)
    mean_diff = (control - treatment).mean()
    pooled_std = np.sqrt((control.std() ** 2 + treatment.std() ** 2) / 2)
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0

    # Bootstrap 95% CI for mean difference
    diffs = control - treatment
    n_bootstrap = 10000
    rng = np.random.default_rng(42)
    bootstrap_samples = rng.choice(diffs, size=(n_bootstrap, len(diffs)), replace=True)
    bootstrap_means = bootstrap_samples.mean(axis=1)
    ci_lower = np.percentile(bootstrap_means, 2.5)
    ci_upper = np.percentile(bootstrap_means, 97.5)

    return mean_diff, p_value, cohens_d, ci_lower, ci_upper


def success_rate_test(df: pd.DataFrame) -> tuple[float, float, float]:
    """Run McNemar's test for success rate (RQ2).

    Returns:
        Tuple of (success_rate_control, success_rate_treatment, p_value)
    """
    # Create contingency table
    pivot = df.pivot_table(
        index="task_id", columns="condition", values="success", aggfunc="first"
    )

    # McNemar's test requires paired binary outcomes
    # Count discordant pairs
    control_success = pivot["control"].astype(int)
    treatment_success = pivot["treatment"].astype(int)

    # Contingency table
    #                    Treatment
    # Control        Success    Failure
    # Success        a          b
    # Failure        c          d

    a = ((control_success == 1) & (treatment_success == 1)).sum()
    b = ((control_success == 1) & (treatment_success == 0)).sum()
    c = ((control_success == 0) & (treatment_success == 1)).sum()
    d = ((control_success == 0) & (treatment_success == 0)).sum()

    # McNemar's test (exact binomial for small samples)
    from statsmodels.stats.contingency_tables import mcnemar

    table = np.array([[a, b], [c, d]])
    result = mcnemar(table, exact=True)

    success_rate_control = control_success.mean()
    success_rate_treatment = treatment_success.mean()

    return success_rate_control, success_rate_treatment, result.pvalue


def analyze_by_difficulty(df: pd.DataFrame, metadata: dict[str, Any]) -> dict[str, Any]:
    """Analyze token reduction by task difficulty (RQ3).

    Two-way ANOVA: Condition × Complexity
    Post-hoc pairwise comparisons with Bonferroni correction.

    Returns:
        Dict with 'mean_diffs', 'anova_results', and 'posthoc' keys
    """
    from statsmodels.stats.anova import anova_lm
    from statsmodels.formula.api import ols
    from statsmodels.stats.multicomp import pairwise_tukeyhsd

    # Add difficulty column to dataframe
    df_with_diff = df.copy()
    df_with_diff["difficulty"] = df_with_diff["task_id"].map(
        lambda tid: metadata.get(tid, {}).get("difficulty", "unknown")
    )

    results = {"mean_diffs": {}, "anova_results": None, "posthoc": None}

    # Mean difference by difficulty
    for difficulty in ["simple", "medium", "complex"]:
        task_ids = [
            tid
            for tid, meta in metadata.items()
            if meta.get("difficulty") == difficulty
        ]

        if not task_ids:
            continue

        subset = df_with_diff[df_with_diff["task_id"].isin(task_ids)]
        if len(subset) < 10:
            continue

        control = subset[subset["condition"] == "control"]["total_tokens"]
        treatment = subset[subset["condition"] == "treatment"]["total_tokens"]

        results["mean_diffs"][difficulty] = control.mean() - treatment.mean()

    # Two-way ANOVA (if we have enough data for each difficulty)
    valid_difficulties = [
        d for d in ["simple", "medium", "complex"] if d in results["mean_diffs"]
    ]

    if len(valid_difficulties) >= 2:
        try:
            # Filter to valid difficulties only
            df_anova = df_with_diff[df_with_diff["difficulty"].isin(valid_difficulties)]

            # Two-way ANOVA: total_tokens ~ C(condition) + C(difficulty) + C(condition):C(difficulty)
            model = ols(
                "total_tokens ~ C(condition) + C(difficulty) + C(condition):C(difficulty)",
                data=df_anova,
            ).fit()
            anova_table = anova_lm(model, typ=2)
            results["anova_results"] = {
                "condition_pvalue": anova_table.loc["C(condition)", "PR(>F)"],
                "difficulty_pvalue": anova_table.loc["C(difficulty)", "PR(>F)"],
                "interaction_pvalue": anova_table.loc[
                    "C(condition):C(difficulty)", "PR(>F)"
                ],
            }

            # Post-hoc with Bonferroni correction
            tukey = pairwise_tukeyhsd(
                df_anova["total_tokens"],
                df_anova["condition"] + "_" + df_anova["difficulty"],
                alpha=0.05 / 3,  # Bonferroni correction
            )
            results["posthoc"] = {
                "groups": tukey.groupsunique.tolist(),
                "reject": tukey.reject.tolist(),
            }
        except Exception as e:
            import logging

            logging.warning(f"ANOVA failed: {e}")
            results["anova_error"] = str(e)

    return results


def time_distribution_test(df: pd.DataFrame) -> tuple[float, float, float]:
    """Run Mann-Whitney U test for time distribution.

    Returns:
        Tuple of (median_control, median_treatment, effect_size)
    """
    control = df[df["condition"] == "control"]["time_seconds"]
    treatment = df[df["condition"] == "treatment"]["time_seconds"]

    median_control = control.median()
    median_treatment = treatment.median()

    # Mann-Whitney U test
    u_stat, _ = stats.mannwhitneyu(control, treatment, alternative="two-sided")

    # Rank-biserial correlation (effect size)
    n1 = len(control)
    n2 = len(treatment)
    effect_size = 1 - (2 * u_stat) / (n1 * n2)

    return median_control, median_treatment, effect_size


def run_full_analysis(results_csv: Path, metadata: dict[str, Any]) -> AnalysisResults:
    """Run complete statistical analysis pipeline.

    Args:
        results_csv: Path to results CSV
        metadata: Task metadata dict mapping task_id to difficulty

    Returns:
        AnalysisResults with all computed statistics
    """
    df = load_results(results_csv)

    # RQ1: Token reduction
    mean_diff, p_token, d, ci_lo, ci_hi = paired_token_test(df)

    control = df[df["condition"] == "control"]["total_tokens"]
    treatment = df[df["condition"] == "treatment"]["total_tokens"]

    # RQ2: Success rate
    sr_ctrl, sr_treat, p_success = success_rate_test(df)

    # RQ3: By difficulty
    diff_breakdown = analyze_by_difficulty(df, metadata)

    # Time distribution
    time_ctrl, time_treat, time_eff = time_distribution_test(df)

    return AnalysisResults(
        token_mean_control=control.mean(),
        token_mean_treatment=treatment.mean(),
        token_mean_diff=mean_diff,
        token_p_value=p_token,
        token_cohens_d=d,
        token_ci_lower=ci_lo,
        token_ci_upper=ci_hi,
        success_rate_control=sr_ctrl,
        success_rate_treatment=sr_treat,
        success_p_value=p_success,
        token_diff_by_difficulty=diff_breakdown,
        time_median_control=time_ctrl,
        time_median_treatment=time_treat,
        time_effect_size=time_eff,
    )

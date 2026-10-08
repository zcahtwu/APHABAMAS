"""Analyse pairwise agreement between the three simulation algorithms.

Run from the repository root with::

    python -m experiments.motion_type_investigation.analyse_between_algorithms

Compare the three plotted algorithm-pair metrics with one another, pairing
values by trajectory repeat within each scan, motion type, severity, and metric.
Shapiro-Wilk tests the paired differences. Normal differences use a two-sided
paired t-test; otherwise use a two-sided Wilcoxon signed-rank test. Apply Holm
correction across the three comparisons within each case and metric.
"""

import json
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


MOTION_TYPES = {
    "slow_drift": "Slow drift",
    "spikes": "Spikes",
    "stepwise": "Step-wise",
}
SEVERITIES = ("low", "medium", "high")
SCANS = ("real_brain", "phantom")
METRICS = ("SSIM", "RMSD")
ALGORITHM_PAIRS = (
    (
        "Type-2 NUFFT vs. Image-based",
        "type2_with_image_based",
        "#CC6677",
    ),
    (
        "Type-1 NUFFT vs. Image-based",
        "type1_with_image_based",
        "#DDCC77",
    ),
    (
        "Type-1 NUFFT vs. Type-2 NUFFT",
        "type1_with_type2",
        "#807dba",
    ),
)
PAIR_COMPARISONS = tuple(combinations([pair[0] for pair in ALGORITHM_PAIRS], 2))
ALPHA = 0.05

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
OUTPUT_DIRECTORY = SCRIPT_DIRECTORY / "results" / "between_algorithms"
METRICS_OUTPUT_PATH = OUTPUT_DIRECTORY / "between_algorithm_metrics.csv"
TESTS_OUTPUT_PATH = OUTPUT_DIRECTORY / "between_algorithm_tests.csv"
SIGNIFICANCE_TABLE_PATH = (
    OUTPUT_DIRECTORY / "between_algorithm_significance_table.md"
)
NORMALITY_DIRECTORY = OUTPUT_DIRECTORY / "normality_plots"

PAIR_ABBREVIATIONS = {
    "Type-2 NUFFT vs. Image-based": "T2 vs. image",
    "Type-1 NUFFT vs. Image-based": "T1 vs. image",
    "Type-1 NUFFT vs. Type-2 NUFFT": "T1 vs. T2",
}

SCAN_LABELS = {
    "real_brain": "Real-brain data",
    "phantom": "Digital phantom",
}


def load_experiment_metrics():
    """Load the canonical metrics file for each motion type."""
    records = []
    for motion_type in MOTION_TYPES:
        result_directory = SCRIPT_DIRECTORY / motion_type / "results"
        metrics_paths = [result_directory / "metrics.json"]

        motion_records = []
        for metrics_path in metrics_paths:
            if not metrics_path.exists():
                raise FileNotFoundError(
                    f"Missing {metrics_path}. Run that motion experiment "
                    "first."
                )
            with metrics_path.open("r") as file:
                motion_records.extend(json.load(file))

        records.extend(motion_records)

    dataframe = pd.DataFrame(records)
    required_metadata = {"motion_type", "severity", "repeat", "scan"}
    missing_metadata = required_metadata.difference(dataframe.columns)
    if missing_metadata:
        raise ValueError(
            f"Metrics are missing metadata columns: {sorted(missing_metadata)}"
        )

    duplicate_cases = dataframe.duplicated(
        ["motion_type", "severity", "repeat", "scan"]
    )
    if duplicate_cases.any():
        raise ValueError(
            "Duplicate scan/repeat records remain after severity mapping."
        )

    return dataframe


def create_long_metrics(dataframe):
    """Convert pairwise metrics to one plotting/statistics row per value."""
    rows = []
    for scan in SCANS:
        for motion_type, motion_label in MOTION_TYPES.items():
            for severity in SEVERITIES:
                case_data = dataframe[
                    (dataframe["scan"] == scan)
                    & (dataframe["motion_type"] == motion_type)
                    & (dataframe["severity"] == severity)
                ].sort_values("repeat")

                if case_data.empty:
                    raise ValueError(
                        f"No results for {scan}, {motion_type}, {severity}"
                    )

                for metric in METRICS:
                    for pair_label, pair_key, color in ALGORITHM_PAIRS:
                        metric_column = f"{metric}_{pair_key}"
                        if metric_column not in case_data:
                            raise ValueError(
                                f"Metrics are missing column {metric_column}"
                            )

                        pair_values = case_data[
                            ["repeat", metric_column]
                        ].dropna()
                        for _, pair_value in pair_values.iterrows():
                            value = float(pair_value[metric_column])
                            rows.append(
                                {
                                    "scan": scan,
                                    "motion_type": motion_type,
                                    "motion_label": motion_label,
                                    "severity": severity,
                                    "repeat": int(pair_value["repeat"]),
                                    "metric": metric,
                                    "algorithm_pair": pair_label,
                                    "color": color,
                                    "value": value,
                                }
                            )

    return pd.DataFrame(rows)


def holm_correction(p_values):
    """Apply Holm's step-down family-wise error correction."""
    p_values = np.asarray(p_values, dtype=float)
    order = np.argsort(p_values)
    ordered_adjusted = np.maximum.accumulate(
        (len(p_values) - np.arange(len(p_values))) * p_values[order]
    )
    corrected = np.empty(len(p_values), dtype=float)
    corrected[order] = np.minimum(ordered_adjusted, 1.0)
    return corrected


def select_paired_test(values_1, values_2, shapiro_p):
    """Compare two algorithm-pair metrics matched by trajectory repeat."""
    differences = values_1 - values_2
    if np.all(differences == 0):
        return "No difference", 1.0, 0.0
    if shapiro_p >= ALPHA:
        statistic, p_value = stats.ttest_rel(values_1, values_2, alternative="two-sided")
        return "Paired t-test", float(p_value), float(statistic)
    statistic, p_value = stats.wilcoxon(differences, alternative="two-sided")
    return "Wilcoxon signed-rank", float(p_value), float(statistic)


def paired_values(case_data, metric, pair_1, pair_2):
    """Align groups by repeat, retaining only finite matched observations."""
    wide = case_data[case_data["metric"] == metric].pivot(
        index="repeat", columns="algorithm_pair", values="value"
    )
    paired = wide[[pair_1, pair_2]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(paired) < 3:
        raise ValueError(f"Fewer than three matched repeats: {metric}, {pair_1}, {pair_2}")
    return paired[pair_1].to_numpy(), paired[pair_2].to_numpy()


def assess_normality(differences):
    """Constant differences cannot be assessed by Shapiro-Wilk."""
    if np.all(differences == differences[0]):
        return np.nan, np.nan
    result = stats.shapiro(differences)
    return float(result.statistic), float(result.pvalue)


def create_normality_plot(case_data, scan, motion_type, severity):
    """Save Q-Q plots of the actual paired differences used by the tests."""
    figure, axes = plt.subplots(2, 3, figsize=(15, 9))

    for metric_index, metric in enumerate(METRICS):
        for pair_index, (pair_1, pair_2) in enumerate(PAIR_COMPARISONS):
            values_1, values_2 = paired_values(case_data, metric, pair_1, pair_2)
            differences = values_1 - values_2
            axis = axes[metric_index, pair_index]
            stats.probplot(differences, dist="norm", plot=axis)
            _, shapiro_p = assess_normality(differences)
            normality_text = (f"Shapiro p={shapiro_p:.3g}" if np.isfinite(shapiro_p)
                              else "Constant differences: normality unavailable")
            axis.set_title(
                f"{metric}: ({PAIR_ABBREVIATIONS[pair_1]}) − "
                f"({PAIR_ABBREVIATIONS[pair_2]})\n{normality_text}"
            )
            axis.set_ylabel("Paired metric difference")

    figure.suptitle(
        f"{scan}: {MOTION_TYPES[motion_type]} — {severity.capitalize()}"
    )
    figure.tight_layout(rect=(0, 0, 1, 0.95))
    figure.savefig(
        NORMALITY_DIRECTORY
        / f"{scan}_{motion_type}_{severity}_normality.svg",
        dpi=300,
    )
    plt.close(figure)


def test_between_algorithm_differences(long_metrics):
    """Compare each pair of plotted groups within every experiment case."""
    results = []
    NORMALITY_DIRECTORY.mkdir(parents=True, exist_ok=True)

    for scan in SCANS:
        for motion_type in MOTION_TYPES:
            for severity in SEVERITIES:
                case_data = long_metrics[
                    (long_metrics["scan"] == scan)
                    & (long_metrics["motion_type"] == motion_type)
                    & (long_metrics["severity"] == severity)
                ]
                create_normality_plot(
                    case_data,
                    scan,
                    motion_type,
                    severity,
                )

                for metric in METRICS:
                    case_metric_results = []
                    for pair_1, pair_2 in PAIR_COMPARISONS:
                        values_1, values_2 = paired_values(case_data, metric, pair_1, pair_2)
                        differences = values_1 - values_2
                        shapiro_statistic, shapiro_p = assess_normality(differences)
                        test_name, raw_p, test_statistic = select_paired_test(
                            values_1,
                            values_2,
                            shapiro_p,
                        )
                        case_metric_results.append(
                            {
                                "scan": scan,
                                "motion_type": motion_type,
                                "severity": severity,
                                "metric": metric,
                                "algorithm_pair_1": pair_1,
                                "algorithm_pair_2": pair_2,
                                "n": len(differences),
                                "mean_value_1": float(np.mean(values_1)),
                                "mean_value_2": float(np.mean(values_2)),
                                "mean_difference": float(
                                    np.mean(differences)
                                ),
                                "median_difference": float(
                                    np.median(differences)
                                ),
                                "Shapiro_W": shapiro_statistic,
                                "Shapiro_p": shapiro_p,
                                "normal_differences": shapiro_p >= ALPHA,
                                "test": test_name,
                                "test_statistic": test_statistic,
                                "p_raw": raw_p,
                            }
                        )

                    corrected_values = holm_correction(
                        [result["p_raw"] for result in case_metric_results]
                    )
                    for result, corrected_p in zip(
                        case_metric_results,
                        corrected_values,
                    ):
                        result["p_Holm"] = corrected_p
                        result["significant"] = corrected_p < ALPHA
                    results.extend(case_metric_results)

    return pd.DataFrame(results)


def significance_symbol(p_value):
    """Return the conventional symbol for an adjusted p-value."""
    if p_value < 0.001:
        return "***"
    if p_value < 0.01:
        return "**"
    if p_value < 0.05:
        return "*"
    return "ns"


def format_p_value(p_value):
    """Format a p-value compactly without replacing it by a threshold."""
    if p_value < 0.001:
        return f"{p_value:.2e}"
    return f"{p_value:.3f}"


def format_significance_cell(result):
    """Format one supplementary-table cell."""
    test_abbreviation = {
        "Paired t-test": "t",
        "Wilcoxon signed-rank": "W",
        "No difference": "none",
    }[result["test"]]
    adjusted_p = float(result["p_Holm"])
    return (
        f"{format_p_value(adjusted_p)} "
        f"({significance_symbol(adjusted_p)}; {test_abbreviation})"
    )


def create_significance_table(statistical_results):
    """Create a compact Markdown table for supplementary material."""
    lines = [
        "# Between-algorithm significance table",
        "",
        (
            "Each entry is the Holm-adjusted p-value followed by its "
            "significance symbol and test abbreviation. Each test compares "
            "two plotted algorithm-pair metrics, matched by trajectory repeat. "
            "Differences are the first listed group's metric minus the second's."
        ),
        "",
        "T1 = Type-1 NUFFT; T2 = Type-2 NUFFT; image = image-based. "
        "For example, (T2 vs. image) vs. (T1 vs. image) compares their SSIM "
        "or RMSD values for the same trajectories.",
        "",
    ]

    pair_columns = [f"({PAIR_ABBREVIATIONS[a]}) vs. ({PAIR_ABBREVIATIONS[b]})"
                    for a, b in PAIR_COMPARISONS]

    for scan in SCANS:
        for metric in METRICS:
            lines.extend(
                [
                    f"## {SCAN_LABELS[scan]} — {metric}",
                    "",
                    (
                        "| Motion type | Severity | "
                        + " | ".join(pair_columns)
                        + " |"
                    ),
                    "| --- | --- | ---: | ---: | ---: |",
                ]
            )

            for motion_type, motion_label in MOTION_TYPES.items():
                for severity in SEVERITIES:
                    row = [motion_label, {"low": "Mild", "medium": "Medium", "high": "Severe"}[severity]]
                    for pair_1, pair_2 in PAIR_COMPARISONS:
                        matching_result = statistical_results[
                            (statistical_results["scan"] == scan)
                            & (
                                statistical_results["motion_type"]
                                == motion_type
                            )
                            & (
                                statistical_results["severity"]
                                == severity
                            )
                            & (statistical_results["metric"] == metric)
                            & (
                                statistical_results["algorithm_pair_1"]
                                == pair_1
                            )
                            & (
                                statistical_results["algorithm_pair_2"]
                                == pair_2
                            )
                        ]
                        if len(matching_result) != 1:
                            raise ValueError(
                                "Expected exactly one statistical result for "
                                f"{scan}, {motion_type}, {severity}, {metric}, "
                                f"{pair_1}, {pair_2}; found {len(matching_result)}."
                            )
                        row.append(
                            format_significance_cell(
                                matching_result.iloc[0]
                            )
                        )
                    lines.append("| " + " | ".join(row) + " |")
            lines.append("")

    lines.extend(
        [
            "**Significance:** `***` p < 0.001; `**` p < 0.01; "
            "`*` p < 0.05; `ns` p ≥ 0.05.",
            "",
            (
                "**Tests:** `t`, two-sided paired t-test (mean paired difference = 0); "
                "`W`, Wilcoxon signed-rank test. Normality of the paired "
                "differences was assessed using the Shapiro–Wilk test (alpha = 0.05). "
                "Wilcoxon tests whether the paired-difference distribution is "
                "symmetric about zero. Constant differences skip Shapiro–Wilk; "
                "all-zero differences return p = 1, otherwise Wilcoxon is used."
            ),
            "",
            (
                "Holm correction was applied across the three algorithm-pair "
                "comparisons within each scan, motion type, severity, and "
                "metric. Only finite matched repeats are used for each comparison; "
                "the CSV reports n, group means, and signed mean/median differences."
            ),
            "",
        ]
    )

    SIGNIFICANCE_TABLE_PATH.write_text("\n".join(lines), encoding="utf-8")


def main():
    """Create plotting, statistical, significance, and normality outputs."""
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    experiment_metrics = load_experiment_metrics()
    long_metrics = create_long_metrics(experiment_metrics)
    statistical_results = test_between_algorithm_differences(long_metrics)

    long_metrics.to_csv(METRICS_OUTPUT_PATH, index=False)
    statistical_results.to_csv(TESTS_OUTPUT_PATH, index=False)
    create_significance_table(statistical_results)
    print(statistical_results.to_string(index=False))
    print(f"\nSupplementary table: {SIGNIFICANCE_TABLE_PATH}")


if __name__ == "__main__":
    main()

"""Figure 6/7 boxplots comparing each pair of simulation algorithms."""

import numpy as np
import pandas as pd
from matplotlib.ticker import FormatStrFormatter, MultipleLocator

from manuscript_figures.shared.grouped_boxplots import OFFSETS
from manuscript_figures.shared.metric_grid import SEVERITIES, create_metric_figure
from manuscript_figures.shared.style import GRAYS, REPOSITORY_ROOT


RESULTS = (REPOSITORY_ROOT / "experiments" / "motion_type_investigation" /
           "results" / "between_algorithms")
PAIRS = (
    ("Type-2 NUFFT vs. Image-based", GRAYS[0]),
    ("Type-1 NUFFT vs. Image-based", GRAYS[1]),
    ("Type-1 NUFFT vs. Type-2 NUFFT", GRAYS[2]),
)
SSIM_YLIM = (0.80, 1.005)
RMSD_YLIM = (0.00, 0.06)


def _load(filename, scan):
    path = RESULTS / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run analyse_between_algorithms first.")
    rows = pd.read_csv(path)
    rows = rows[rows.scan == scan]
    if rows.empty:
        raise ValueError(f"No rows found for {scan} in {path}")
    return rows


def _format_axis(axis, metric, panel):
    if metric == "SSIM":
        axis.set_ylim(*SSIM_YLIM)
        axis.yaxis.set_major_locator(MultipleLocator(0.10))
    else:
        axis.set_ylim(*RMSD_YLIM)
        axis.yaxis.set_major_locator(MultipleLocator(0.03))
    axis.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))


def _add_brackets(axis, data, tests, motion, metric):
    """Mark Holm-adjusted non-significant comparisons."""
    rows = tests[(tests.motion_type == motion) & (tests.metric == metric) &
                 (tests.p_Holm >= 0.05)]
    offsets = dict(zip((name for name, _ in PAIRS), OFFSETS))
    direction = -1 if metric == "SSIM" else 1
    span = np.ptp(axis.get_ylim())

    for severity_index, (severity, _) in enumerate(SEVERITIES):
        case = data[(data.motion_type == motion) & (data.metric == metric) &
                    (data.severity == severity)]
        for level, result in enumerate(rows[rows.severity == severity].itertuples()):
            left, right = sorted((offsets[result.algorithm_pair_1],
                                  offsets[result.algorithm_pair_2]))
            included = [name for name, offset in offsets.items()
                        if left <= offset <= right]
            values = case[case.algorithm_pair.isin(included)].value
            edge = values.min() if direction < 0 else values.max()
            y = edge + direction * (0.04 + level * 0.13) * span
            tip = y + direction * 0.025 * span
            left, right = severity_index + left, severity_index + right
            axis.plot((left, left, right, right), (y, tip, tip, y),
                      color="black", linewidth=0.8)
            axis.text((left + right) / 2, tip + direction * 0.01 * span, "ns",
                      ha="center", va="top" if direction < 0 else "bottom",
                      fontsize=8.5, fontweight="bold")


def create_figure(scan, output_path, panel_label=None, show_samples=False):
    metrics = _load("between_algorithm_metrics.csv", scan)
    tests = _load("between_algorithm_tests.csv", scan)
    required = {"algorithm_pair_1", "algorithm_pair_2", "p_Holm"}
    if not required.issubset(tests) or not tests.p_Holm.between(0, 1).all():
        raise ValueError("Outdated statistical table. Rerun the analysis.")
    return create_metric_figure(
        metrics, tests, output_path,
        series=PAIRS,
        series_column="algorithm_pair",
        legend_labels=tuple(name for name, _ in PAIRS),
        format_axis=_format_axis,
        annotate=_add_brackets,
        ylabels=("Pairwise SSIM", "Pairwise RMSD"),
        panel_label=panel_label,
        show_samples=show_samples,
    )

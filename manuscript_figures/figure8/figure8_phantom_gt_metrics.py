"""Create Figure 8 from phantom metrics relative to ground truth.

Run: ``python -m manuscript_figures.figure8.figure8_phantom_gt_metrics``
"""

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.ticker import FormatStrFormatter, MultipleLocator

from manuscript_figures.shared.grouped_boxplots import OFFSETS
from manuscript_figures.shared.metric_grid import SEVERITIES, create_metric_figure
from manuscript_figures.shared.style import GRAYS, REPOSITORY_ROOT


HERE = Path(__file__).resolve().parent
OUTPUT_PATH = HERE / "figure8_phantom_gt_metrics.svg"
SI_OUTPUT_PATH = HERE / "figure8_phantom_gt_metrics_SI.svg"
RESULTS = (REPOSITORY_ROOT / "experiments" / "motion_type_investigation" /
           "results" / "phantom")
ALGORITHMS = (("Image-based", GRAYS[0]), ("Type 2", GRAYS[1]),
              ("Type 1", GRAYS[2]))
LEGEND_LABELS = ("Image-based", "Type-2 NUFFT-based", "Type-1 NUFFT-based")


def _load_results():
    paths = (RESULTS / "phantom_GT_metrics.csv",
             RESULTS / "paired_algorithm_tests.csv")
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. Run analyse_phantom_results first.")
    return tuple(pd.read_csv(path) for path in paths)


def _format_axis(axis, metric, _panel):
    limits, spacing = ((0.80, 1.005), 0.05) if metric == "SSIM" else ((0, 0.06), 0.02)
    axis.set_ylim(*limits)
    axis.yaxis.set_major_locator(MultipleLocator(spacing))
    axis.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))


def _add_brackets(axis, data, tests, motion, metric):
    """Mark comparisons that remain non-significant after Holm correction."""
    rows = tests[(tests.motion_type == motion) & (tests.metric == metric) &
                 ~tests.significant]
    algorithms = {name: index for index, (name, _) in enumerate(ALGORITHMS)}
    severities = {name: index for index, (name, _) in enumerate(SEVERITIES)}
    span = np.ptp(axis.get_ylim())

    for result in rows.itertuples():
        left, right = result.comparison.split(" vs ")
        center = severities[result.severity]
        x1 = center + OFFSETS[algorithms[left]]
        x2 = center + OFFSETS[algorithms[right]]
        values = data[(data.motion_type == motion) &
                      (data.severity == result.severity) &
                      (data.metric == metric) & data.algorithm.isin((left, right))].value
        y, height = values.max() + 0.025 * span, 0.015 * span
        axis.plot((x1, x1, x2, x2), (y, y + height, y + height, y),
                  color="black", linewidth=0.8, clip_on=False)
        axis.text((x1 + x2) / 2, y + height, "ns", ha="center", va="bottom",
                  fontsize=8.5, fontweight="bold")


def create_figure(output_path=OUTPUT_PATH, show_samples=False):
    data, tests = _load_results()
    return create_metric_figure(
        data, tests, output_path,
        series=ALGORITHMS,
        series_column="algorithm",
        legend_labels=LEGEND_LABELS,
        format_axis=_format_axis,
        annotate=_add_brackets,
        show_samples=show_samples,
        height=5.5,
        top=0.96,
        bottom=0.22,
        label_y=0.135,
        legend_y=0.055,
        legend_spacing=8.0,
        hspace=0.33,
        crop=(0.35, 0),
    )


if __name__ == "__main__":
    create_figure()
    create_figure(SI_OUTPUT_PATH, show_samples=True)

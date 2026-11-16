"""Create Figure 9 SI: quantitative accuracy assessment for random jitter.

Run: ``python -m manuscript_figures.figure9_ground_truth_accuracy.si_random_jitter_gt_metrics``
"""

from pathlib import Path

import matplotlib.pyplot as plt

from experiments.utils.figure_output import configure_figure_output, save_figure
from manuscript_figures.figure9_ground_truth_accuracy.figure9_phantom_gt_metrics import (
    ALGORITHMS,
    LEGEND_LABELS,
    add_brackets,
    format_axis,
    load_results,
)
from manuscript_figures.shared.grouped_boxplots import add_legend, draw_boxes
from manuscript_figures.shared.metric_grid import METRICS, SEVERITIES, STYLE
from manuscript_figures.shared.style import PUBLICATION_WIDTH


OUTPUT_PATH = (Path(__file__).resolve().parent / "Supporting_Information" /
               "random_jitter_ground_truth_accuracy.svg")


def create_figure(output_path=OUTPUT_PATH):
    """Show random-jitter SSIM and RMSD side by side on independent scales."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data, tests = load_results()
    data = data[data.motion_type == "random_jitter"]
    tests = tests[tests.motion_type == "random_jitter"]
    with plt.rc_context(STYLE):
        # Approximately 69 × 69 mm per metric panel.
        figure, axes = plt.subplots(1, 2, figsize=(PUBLICATION_WIDTH, 4.55))
        for axis, metric in zip(axes, METRICS):
            panel = data[data.metric == metric]
            draw_boxes(axis, panel, SEVERITIES, ALGORITHMS,
                       category_column="severity", series_column="algorithm")
            format_axis(axis, metric, panel)
            add_brackets(axis, data, tests, "random_jitter", metric)
            axis.set_ylabel(metric)
        figure.suptitle("Random jitter", fontsize=12, fontweight="bold", y=0.885)
        figure.text(0.5425, 0.065, "Motion severity", ha="center", va="center",
                    fontsize=11, fontweight="bold")
        add_legend(figure, LEGEND_LABELS, ALGORITHMS, y=0.92)
        figure.subplots_adjust(left=0.10, right=0.985, top=0.80, bottom=0.20,
                               wspace=0.30)
        save_figure(figure, output_path, dpi=300)
        plt.close(figure)
    return output_path


if __name__ == "__main__":
    configure_figure_output()
    create_figure()

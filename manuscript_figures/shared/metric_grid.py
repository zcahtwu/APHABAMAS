"""Shared metric-grid renderer for quantitative figures."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox

from experiments.utils.figure_output import save_figure
from manuscript_figures.shared.grouped_boxplots import add_legend, draw_boxes
from manuscript_figures.shared.style import FONT, PUBLICATION_WIDTH


MOTIONS = (("slow_drift", "Slow drift"), ("spikes", "Spikes"),
           ("stepwise", "Step-wise"), ("random_jitter", "Random jitter"))
SEVERITIES = (("low", "Mild"), ("medium", "Moderate"), ("high", "Severe"))
METRICS = ("SSIM", "RMSD")
STYLE = {
    **FONT,
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.labelweight": "bold",
    "axes.titlesize": 12,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 10,
}


def create_metric_figure(
    data,
    tests,
    output_path,
    *,
    series,
    series_column,
    legend_labels,
    format_axis,
    annotate,
    ylabels=("SSIM", "RMSD"),
    panel_label=None,
    show_samples=False,
    motions=MOTIONS,
    width=PUBLICATION_WIDTH,
    height=6.2,
    top=0.89,
    bottom=0.12,
    label_y=0.045,
    legend_y=0.95,
    hspace=0.28,
    wspace=0,
    motion_separators=True,
    crop=(0, 0),
):
    """Render a metric-by-motion grid from a tidy ``value`` table."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with plt.rc_context(STYLE):
        figure, axes = plt.subplots(len(METRICS), len(motions), figsize=(width, height),
                                    sharex=True, sharey="row", squeeze=False)
        for row, metric in enumerate(METRICS):
            for column, (motion, title) in enumerate(motions):
                axis = axes[row, column]
                panel = data[(data.motion_type == motion) & (data.metric == metric)]
                draw_boxes(
                    axis,
                    panel,
                    SEVERITIES,
                    series,
                    category_column="severity",
                    series_column=series_column,
                    show_samples=show_samples,
                )
                format_axis(axis, metric, panel)
                annotate(axis, data, tests, motion, metric)
                axis.tick_params(axis="x", labelbottom=True)
                if motion_separators and column > 0:
                    axis.tick_params(axis="y", left=False)
                    axis.spines["left"].set_color("0.15")
                    axis.spines["left"].set_linewidth(1.2)
                if row == 0:
                    axis.set_title(title, fontweight="bold", pad=7)

        axes[0, 0].set_ylabel(ylabels[0])
        axes[1, 0].set_ylabel(ylabels[1])
        add_legend(figure, legend_labels, series, y=legend_y)
        figure.text(0.5425, label_y, "Motion severity", ha="center", va="center",
                    fontsize=11, fontweight="bold")
        if panel_label:
            figure.text(0.005, 0.95, panel_label, ha="left", va="top",
                        fontsize=13, fontweight="bold")
        figure.subplots_adjust(left=0.10,
                               right=0.985,
                               top=top, bottom=bottom,
                               hspace=hspace, wspace=wspace)
        width, figure_height = figure.get_size_inches()
        bounds = Bbox.from_extents(0, crop[0], width, figure_height - crop[1])
        save_figure(figure, output_path, dpi=300, bbox_inches=bounds)
        plt.close(figure)
    return output_path

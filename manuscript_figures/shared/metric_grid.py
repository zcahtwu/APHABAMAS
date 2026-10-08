"""Shared 2 x 3 metric-grid renderer for Figures 6--8."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox

from manuscript_figures.shared.grouped_boxplots import draw_boxes, legend_handles
from manuscript_figures.shared.style import FONT, PUBLICATION_WIDTH


MOTIONS = (("slow_drift", "Slow drift"), ("spikes", "Spikes"),
           ("stepwise", "Step-wise"))
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
    "legend.fontsize": 8.3,
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
    height=5.0,
    top=0.88,
    bottom=0.28,
    label_y=0.18,
    legend_y=0.095,
    legend_spacing=0.6,
    hspace=0.25,
    crop=(0.38, 0.18),
):
    """Render a metric-by-motion grid from a tidy ``value`` table."""
    output_path = Path(output_path)
    with plt.rc_context(STYLE):
        figure, axes = plt.subplots(2, 3, figsize=(PUBLICATION_WIDTH, height),
                                    sharex=True, sharey="row")
        for row, metric in enumerate(METRICS):
            for column, (motion, title) in enumerate(MOTIONS):
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
                if row == 0:
                    axis.set_title(title, fontweight="bold", pad=7)

        axes[0, 0].set_ylabel(ylabels[0])
        axes[1, 0].set_ylabel(ylabels[1])
        figure.legend(handles=legend_handles(legend_labels, series), loc="lower center",
                      ncol=3, frameon=False, bbox_to_anchor=(0.5425, legend_y),
                      columnspacing=legend_spacing, handlelength=2.4,
                      handleheight=1.15, handletextpad=0.5, borderpad=0.2)
        figure.text(0.5425, label_y, "Motion severity", ha="center", va="center",
                    fontsize=11, fontweight="bold")
        if panel_label:
            figure.text(0.005, 0.95, panel_label, ha="left", va="top",
                        fontsize=13, fontweight="bold")
        figure.subplots_adjust(left=0.10, right=0.985, top=top, bottom=bottom,
                               hspace=hspace, wspace=0.20)
        width, figure_height = figure.get_size_inches()
        bounds = Bbox.from_extents(0, crop[0], width, figure_height - crop[1])
        figure.savefig(output_path, dpi=300, bbox_inches=bounds)
        plt.close(figure)
    return output_path

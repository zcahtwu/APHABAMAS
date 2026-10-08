"""Minimal primitives shared by the Figure 6--8 grouped boxplots."""

import numpy as np
from matplotlib.colors import to_rgba
from matplotlib.patches import Patch


BACKGROUNDS = ("#FFFFFF", "#F3F3F3", "#E6E6E6")
OFFSETS = (-0.24, 0.0, 0.24)


def draw_boxes(
    axis,
    data,
    categories,
    series,
    category_column,
    series_column,
    show_samples=False,
):
    """Draw three series for each category in a prepared data subset."""
    for index, background in enumerate(BACKGROUNDS):
        axis.axvspan(index - 0.5, index + 0.5, color=background, zorder=-2)
    for boundary in (0.5, 1.5):
        axis.axvline(boundary, color="0.60", ls="--", lw=0.7, zorder=-1)

    for category_index, (category, _) in enumerate(categories):
        category_data = data[data[category_column] == category]
        for series_index, (name, color) in enumerate(series):
            values = category_data[category_data[series_column] == name]["value"].to_numpy()
            if not len(values):
                raise ValueError(f"No data for {category}, {name}")
            position = category_index + OFFSETS[series_index]
            axis.boxplot(
                values,
                positions=[position],
                widths=0.20,
                patch_artist=True,
                whis=1.5,
                showfliers=not show_samples,
                boxprops={"facecolor": color, "edgecolor": "black"},
                medianprops={"color": "black"},
                whiskerprops={"color": "black", "linewidth": 0.7},
                capprops={"color": "black", "linewidth": 0.7},
                flierprops={
                    "marker": "o",
                    "markersize": 3,
                    "markerfacecolor": color,
                    "markeredgecolor": "black",
                    "markeredgewidth": 0.2,
                },
            )
            if show_samples:
                axis.scatter(
                    position + np.linspace(-0.035, 0.035, len(values)),
                    values,
                    s=7,
                    facecolor=color,
                    edgecolor="black",
                    linewidth=0.2,
                    zorder=3,
                )

    axis.set(xlim=(-0.5, 2.5), xticks=range(len(categories)))
    axis.set_xticklabels([label for _, label in categories], fontweight="bold")
    axis.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.65)
    axis.set_axisbelow(True)
    axis.spines[["top", "right"]].set_visible(False)


def legend_handles(labels, series):
    return [
        Patch(facecolor=to_rgba(color), edgecolor="black", label=label)
        for label, (_, color) in zip(labels, series)
    ]

"""Shared loading and plotting helpers for Figure 5 trajectories."""

import json

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator

from manuscript_figures.shared.style import FONT


DURATION = 2.3 * 256
TIME_TICKS = (0, 200, 400)
Y_LIMITS = (-8, 8)
COLORS = ("#CC6677", "#C2A64B", "#4477AA")
COMPONENTS = (r"$x$", r"$y$", r"$z$")
STYLE = {
    **FONT,
    "font.size": 9,
    "axes.labelsize": 10,
    "axes.titlesize": 13,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8,
    "legend.fontsize": 11,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
}


def load_piecewise(path):
    """Load a converted trajectory and extend its final pose when needed."""
    with path.open() as file:
        saved = json.load(file)
    data = {
        "time": np.asarray(saved["time_points"]) * DURATION,
        "translation": np.asarray(saved["translation"]),
        "rotation": np.asarray(saved["rotation"]),
    }
    pose_length = len(data["translation"])
    if len(data["time"]) == pose_length + 1:
        for key in ("translation", "rotation"):
            data[key] = np.vstack((data[key], data[key][-1]))
    elif not len(data["time"]) == pose_length == len(data["rotation"]):
        raise ValueError(f"Inconsistent trajectory lengths in {path}")
    return data


def draw_pose(axis, time, values, stepped=True):
    """Draw and format one three-component translation or rotation axis."""
    plot = axis.step if stepped else axis.plot
    for component, color in enumerate(COLORS):
        options = {"where": "post"} if stepped else {}
        plot(time, values[:, component], color=color, linewidth=0.45,
             solid_capstyle="round", **options)
    axis.set(xlim=(0, DURATION), ylim=Y_LIMITS, xticks=TIME_TICKS)
    axis.yaxis.set_major_locator(MultipleLocator(4))
    axis.grid(axis="y", color="#C7C7C7", linestyle=":", linewidth=0.45)


def add_pose_pair(figure, grid_spec, data, *, title=None, stepped=True,
                  show_y=True, show_x=True):
    """Add translation-over-rotation axes and return them."""
    grid = grid_spec.subgridspec(2, 1, hspace=0.15)
    translation = figure.add_subplot(grid[0])
    rotation = figure.add_subplot(grid[1], sharex=translation)
    draw_pose(translation, data["time"], data["translation"], stepped)
    draw_pose(rotation, data["time"], data["rotation"], stepped)
    translation.tick_params(axis="x", labelbottom=False)

    if title:
        translation.set_title(title, pad=4, fontweight="bold")
    if show_y:
        translation.set_ylabel(r"$T$ (mm)")
        rotation.set_ylabel(r"$\theta$ (°)")
    else:
        translation.tick_params(axis="y", labelleft=False)
        rotation.tick_params(axis="y", labelleft=False)
    if show_x:
        rotation.set_xlabel("Time (s)", fontsize=11.5)
        rotation.tick_params(axis="x", labelsize=9.5)
    else:
        rotation.tick_params(axis="x", labelbottom=False)
    return translation, rotation


def add_header(figure, panel_label=None, legend_y=0.985):
    handles = [Line2D([], [], color=color, linewidth=0.9, label=label)
               for label, color in zip(COMPONENTS, COLORS)]
    figure.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.56, legend_y),
                  ncol=3, frameon=False, title="Motion component",
                  title_fontsize=13, handlelength=2.2, columnspacing=1.2)
    if panel_label:
        figure.text(0.015, 0.975, panel_label, ha="left", va="top",
                    fontsize=15, fontweight="bold")


def save(figure, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=300)
    plt.close(figure)
    return output_path

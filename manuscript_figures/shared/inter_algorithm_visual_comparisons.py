"""Shared Figure 6/7 renderer for algorithm images and differences."""

from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import Normalize

from manuscript_figures.shared.style import (
    FONT,
    PUBLICATION_WIDTH,
    REPOSITORY_ROOT,
    SUBJECTS,
)


RESULTS = REPOSITORY_ROOT / "experiments" / "real_motion_traces"
ALGORITHMS = ("Image-based", "Type-2 NUFFT", "Type-1 NUFFT")
POSITIONS = ((0, 0), (1, 0), (1, 1), (2, 0), (2, 1), (2, 2))
FILES = ("image_based.nii.gz", "type2.nii.gz", "type1_original.nii.gz")
SCAN_CONFIG = {
    "real": ("real_scan_results", 165),
    "phantom": ("phantom_results", 96),
}
IMAGE_LIMITS = (0.0, 2.0)
DIFFERENCE_LIMITS = (-0.2, 0.2)


def _slice(path, index):
    image = nib.load(path)
    return np.asanyarray(image.dataobj[:, :, index]).T


def load_subject(scan, subject):
    """Load the three simulated-result slices required for one subject."""
    if scan not in SCAN_CONFIG:
        raise ValueError(f"Unsupported scan type: {scan}")
    directory, slice_index = SCAN_CONFIG[scan]
    paths = [RESULTS / directory / subject / filename for filename in FILES]
    missing = [path for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing simulation result(s):\n" +
                                "\n".join(map(str, missing)))
    image_based, type_2, type_1 = (_slice(path, slice_index) for path in paths)
    return (image_based, type_2 - image_based, type_2,
            type_1 - image_based, type_1 - type_2, type_1)


def _draw_panel(figure, grid_spec, subject_data, shift=0.0):
    grid = grid_spec.subgridspec(3, 4, width_ratios=(0.27, 1, 1, 1),
                                 wspace=0.01, hspace=0.02)
    panel_axes, image_axes = [], []

    for row, label in enumerate(ALGORITHMS):
        axis = figure.add_subplot(grid[row, 0])
        axis.text(1.15, 0.5, label, ha="center", va="center", rotation=90,
                  fontsize=8.5, fontweight="bold")
        axis.axis("off")
        panel_axes.append(axis)

    for image, (row, column) in zip(subject_data, POSITIONS):
        axis = figure.add_subplot(grid[row, column + 1])
        limits = IMAGE_LIMITS if row == column else DIFFERENCE_LIMITS
        axis.imshow(image, cmap="gray", vmin=limits[0], vmax=limits[1],
                    origin="lower", interpolation="nearest")
        axis.axis("off")
        if row == 2:
            axis.text(0.5, -0.08, ALGORITHMS[column], transform=axis.transAxes,
                      ha="center", va="top", fontsize=8.5, fontweight="bold")
        panel_axes.append(axis)
        image_axes.append((axis, column))

    figure.canvas.draw()
    for axis, column in image_axes:
        position = axis.get_position()
        axis.set_position((position.x0 + (0.014, 0, -0.014)[column], position.y0,
                           position.width, position.height))
    for axis in panel_axes:
        position = axis.get_position()
        axis.set_position((position.x0 + shift, position.y0,
                           position.width, position.height))
    return image_axes[0][0]


def _colorbar(axis, title, limits):
    colorbar = ColorbarBase(axis, cmap="gray", norm=Normalize(*limits),
                            ticks=(limits[0], sum(limits) / 2, limits[1]),
                            format="%.1f")
    colorbar.ax.tick_params(labelsize=7.5, length=1.8, width=0.5, pad=1.5)
    colorbar.outline.set_linewidth(0.4)
    colorbar.ax.set_title(title, fontsize=8, fontweight="bold", pad=5)


def create_visual_comparison(scan, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subjects = [load_subject(scan, subject) for subject in SUBJECTS]

    with plt.rc_context({**FONT, "font.size": 8}):
        figure = plt.figure(figsize=(PUBLICATION_WIDTH, 4.3))
        grid = figure.add_gridspec(1, 3, width_ratios=(1, 1, 0.03),
                                   left=0.012, right=0.945, bottom=0.10,
                                   top=0.90, wspace=0.04)
        for index, subject in enumerate(subjects):
            anchor = _draw_panel(figure, grid[index], subject,
                                 shift=-0.025 if index else 0)
            position = anchor.get_position()
            figure.text(position.x0 - 0.055, position.y1 + 0.055,
                        f"({chr(98 + index)})", ha="left", va="top",
                        fontsize=13, fontweight="bold")

        bars = grid[2].subgridspec(2, 1, hspace=0.30)
        for index, (title, limits) in enumerate((
            ("Intensity", IMAGE_LIMITS), ("Difference", DIFFERENCE_LIMITS)
        )):
            axis = figure.add_subplot(bars[index])
            _colorbar(axis, title, limits)
            position = axis.get_position()
            height = 0.88 * position.height
            axis.set_position((position.x0 - 0.033, position.y0 - 0.025 +
                               (position.height - height) / 2, position.width, height))

        figure.savefig(output_path, dpi=300)
        plt.close(figure)
    return output_path

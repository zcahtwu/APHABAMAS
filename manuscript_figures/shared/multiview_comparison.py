"""Shared three-view renderer for the real-brain and phantom SI figures."""

from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import Normalize

from manuscript_figures.shared.style import FONT, SUBJECTS


VIEWS = (("Sagittal", 0), ("Coronal", 1), ("Axial", 2))
IMAGE_LIMITS, DIFFERENCE_LIMITS = (0, 2), (-0.2, 0.2)
SI_SIZE = (250 / 25.4, 240 / 25.4)


def _load(directory, subject, filenames):
    paths = [directory / subject / name for name in filenames]
    missing = [path for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing simulation result(s):\n" +
                                "\n".join(map(str, missing)))
    return [nib.load(path).dataobj for path in paths]


def _slice(volume, axis, index):
    selection = [slice(None)] * 3
    selection[axis] = index
    return np.asanyarray(volume[tuple(selection)]).T


def _colorbar(figure, bounds, title, limits):
    axis = figure.add_axes(bounds)
    bar = ColorbarBase(axis, cmap="gray", norm=Normalize(*limits),
                       ticks=(limits[0], sum(limits) / 2, limits[1]),
                       format="%.1f", orientation="horizontal")
    bar.ax.tick_params(labelsize=7, length=1.5, width=0.5, pad=1.5)
    bar.outline.set_linewidth(0.4)
    axis.set_title(title, fontsize=8, fontweight="bold", pad=4)


def create_multiview_figure(output_path, results, filenames, image_titles,
                            differences, difference_titles, axial_index):
    """Plot three orthogonal views for both measured trajectories."""
    output_path, results = Path(output_path), Path(results)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    titles = (*image_titles, *difference_titles)
    gap = len(filenames) + 1
    widths = (0.75, *([1] * len(filenames)), 0.12,
              *([1] * len(differences)))

    with plt.rc_context({**FONT, "font.size": 8}):
        figure = plt.figure(figsize=SI_SIZE)
        grid = figure.add_gridspec(
            6, len(widths), width_ratios=widths,
            left=0.045, right=0.985, bottom=0.10, top=0.94,
            wspace=0.08, hspace=0.14,
        )

        for subject_number, subject in enumerate(SUBJECTS):
            volumes = _load(results, subject, filenames)
            for view_number, (view, axis) in enumerate(VIEWS):
                index = axial_index if axis == 2 else volumes[0].shape[axis] // 2
                slices = [_slice(volume, axis, index) for volume in volumes]
                panels = (*slices, *(slices[a] - slices[b]
                                      for a, b in differences))
                row = 3 * subject_number + view_number

                label = figure.add_subplot(grid[row, 0])
                label.text(0.70, 0.5, f"{view}\n({chr(120 + axis)} = {index})",
                           ha="center", va="center", rotation=90,
                           fontsize=8, fontweight="bold")
                label.axis("off")

                for column, panel in enumerate(panels):
                    grid_column = column + 1 + (column >= len(filenames))
                    panel_axis = figure.add_subplot(grid[row, grid_column])
                    limits = (IMAGE_LIMITS if column < len(filenames)
                              else DIFFERENCE_LIMITS)
                    panel_axis.imshow(panel, cmap="gray", vmin=limits[0],
                                      vmax=limits[1], origin="lower",
                                      interpolation="nearest")
                    panel_axis.axis("off")
                    if row == 0:
                        panel_axis.set_title(titles[column], fontsize=7,
                                             fontweight="bold", pad=5)

            top = grid[3 * subject_number, 0].get_position(figure).y1
            figure.text(0.009, top + 0.012, f"({chr(97 + subject_number)})",
                        ha="left", va="top", fontsize=14, fontweight="bold")
            figure.text(0.045, top + 0.012, f"Trajectory {subject_number + 1}",
                        ha="left", va="top", fontsize=9.5, fontweight="bold")

        image_left = grid[0, 1].get_position(figure).x0
        image_right = grid[0, len(filenames)].get_position(figure).x1
        difference_left = grid[0, gap + 1].get_position(figure).x0
        difference_right = grid[0, -1].get_position(figure).x1
        figure.text((image_left + image_right) / 2, 0.982, "Reconstructions",
                    ha="center", va="top", fontsize=10, fontweight="bold")
        figure.text((difference_left + difference_right) / 2, 0.982,
                    "Difference maps", ha="center", va="top",
                    fontsize=10, fontweight="bold")

        for left, right, title, limits in (
            (image_left, image_right, "Intensity", IMAGE_LIMITS),
            (difference_left, difference_right, "Difference", DIFFERENCE_LIMITS),
        ):
            width = (right - left) * 0.78
            _colorbar(figure, ((left + right - width) / 2, 0.055, width, 0.013),
                      title, limits)
        figure.savefig(output_path, dpi=1200)
        plt.close(figure)
    return output_path

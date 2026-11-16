"""Figure 8: brain and phantom comparisons for measured trajectories 1 and 2."""

from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import Normalize

from experiments.utils.figure_output import configure_figure_output, save_figure
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


def _draw_panel(figure, grid_spec, subject_data):
    grid = grid_spec.subgridspec(3, 4, width_ratios=(0.27, 1, 1, 1),
                                 wspace=0.06, hspace=0.02)

    for row, label in enumerate(ALGORITHMS):
        axis = figure.add_subplot(grid[row, 0])
        axis.text(0.75, 0.5, label, ha="center", va="center", rotation=90,
                  fontsize=8.5, fontweight="bold")
        axis.axis("off")

    for image, (row, column) in zip(subject_data, POSITIONS):
        axis = figure.add_subplot(grid[row, column + 1])
        limits = IMAGE_LIMITS if row == column else DIFFERENCE_LIMITS
        axis.imshow(image, cmap="gray", vmin=limits[0], vmax=limits[1],
                    origin="lower", interpolation="nearest")
        axis.axis("off")
        if row == 2:
            axis.text(0.5, -0.08, ALGORITHMS[column].replace(" NUFFT", "\nNUFFT"),
                      transform=axis.transAxes,
                      ha="center", va="top", fontsize=8.5, fontweight="bold")


def _colorbar(axis, title, limits):
    colorbar = ColorbarBase(axis, cmap="gray", norm=Normalize(*limits),
                            ticks=(limits[0], sum(limits) / 2, limits[1]),
                            format="%.1f")
    colorbar.ax.tick_params(labelsize=7.5, length=1.8, width=0.5, pad=1.5)
    colorbar.outline.set_linewidth(0.4)
    colorbar.ax.set_title(title, fontsize=8, fontweight="bold", pad=5)


OUTPUT_PATH = Path(__file__).resolve().parent / "figure8_algorithm_comparisons.svg"


def create_figure(output_path=OUTPUT_PATH):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scans = (("real", "Brain"), ("phantom", "Phantom"))
    data = {scan: [load_subject(scan, subject) for subject in SUBJECTS]
            for scan, _ in scans}

    with plt.rc_context({**FONT, "font.size": 8}):
        figure = plt.figure(figsize=(PUBLICATION_WIDTH, 8.3))
        grid = figure.add_gridspec(
            2, 2, left=0.055, right=0.91, bottom=0.055, top=0.92,
            wspace=0.0, hspace=0.18,
        )
        for column, title in enumerate(("Trajectory 1 (Mild)", "Trajectory 2 (Severe)")):
            bounds = grid[0, column].get_position(figure)
            figure.text((bounds.x0 + bounds.x1) / 2, 0.955, title,
                        ha="center", va="center", fontsize=12, fontweight="bold")
        for row, (scan, label) in enumerate(scans):
            bounds = grid[row, 0].get_position(figure)
            figure.text(0.015, (bounds.y0 + bounds.y1) / 2, label,
                        ha="center", va="center", rotation=90,
                        fontsize=12, fontweight="bold")
            for column, subject in enumerate(data[scan]):
                _draw_panel(figure, grid[row, column], subject)
        bar_height = 0.22
        for row, (title, limits) in enumerate((
            ("Intensity", IMAGE_LIMITS),
            ("Difference", DIFFERENCE_LIMITS),
        )):
            bounds = grid[row, 0].get_position(figure)
            bottom = (bounds.y0 + bounds.y1 - bar_height) / 2
            _colorbar(figure.add_axes((0.943, bottom, 0.012, bar_height)), title, limits)
        save_figure(figure, output_path, dpi=300)
        plt.close(figure)
    return output_path


if __name__ == "__main__":
    configure_figure_output()
    create_figure()

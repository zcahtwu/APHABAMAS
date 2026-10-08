"""Create the combined Figure 9 phantom assessment.

Run: ``python -m manuscript_figures.figure9.figure9_algorithm_assessment_visual``
"""

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


HERE = Path(__file__).resolve().parent
OUTPUT_PATH = HERE / "figure9_algorithm_assessment_visual.svg"
RESULTS = REPOSITORY_ROOT / "experiments" / "real_motion_traces" / "phantom_results"
ROWS = (
    "Simulated Scan",
    "Error Map (Scan)",
    "Simulated Signal",
    "Error Map (Signal)",
)
COLUMNS = ("Ground Truth", "Image-Based", "Type-2 NUFFT", "Type-1 NUFFT")
LIMITS = ((0, 2), (-0.2, 0.2), (0, 10), (-1, 1))


def _slice(path, index):
    image = nib.load(path)
    return np.asanyarray(image.dataobj[:, :, index]).T


def load_subject(subject):
    """Load the phantom images and signals required for one subject."""
    directory = RESULTS / subject
    image_paths = [directory / name for name in
                   ("GT.nii.gz", "image_based.nii.gz", "type2.nii.gz",
                    "type1_original.nii.gz")]
    signal_paths = [directory / name for name in
                    ("GT_signal.npy", "image_based_signal.npy", "type2_signal.npy")]
    missing = [path for path in image_paths + signal_paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing simulation result(s):\n" +
                                "\n".join(map(str, missing)))

    images = [_slice(path, 96) for path in image_paths]
    signals = [np.log(np.abs(np.load(path)[:, :, 128])).T for path in signal_paths]
    return (
        images,
        (None, *(image - images[0] for image in images[1:])),
        (*signals, None),
        (None, *(signal - signals[0] for signal in signals[1:]), None),
    )


def _colorbar(axis, limits):
    colorbar = ColorbarBase(axis, cmap="gray", norm=Normalize(*limits),
                            ticks=(limits[0], sum(limits) / 2, limits[1]),
                            format="%.1f")
    colorbar.ax.tick_params(labelsize=6.5, length=1.5, width=0.5, pad=1.5)
    for label in colorbar.ax.get_yticklabels():
        label.set_fontweight("bold")
    colorbar.outline.set_linewidth(0.4)


def _draw_subject(figure, grid_spec, subject, panel_label):
    grid = grid_spec.subgridspec(4, 6, width_ratios=(0.23, 1, 1, 1, 1, 0.10),
                                 wspace=0.02, hspace=0.12)
    for row, (row_label, row_panels, limits) in enumerate(zip(ROWS, subject, LIMITS)):
        label_axis = figure.add_subplot(grid[row, 0])
        label_axis.text(0.65, 0.5, row_label, ha="center", va="center", rotation=90,
                        fontsize=6.5, fontweight="bold")
        label_axis.axis("off")

        for column, panel in enumerate(row_panels):
            axis = figure.add_subplot(grid[row, column + 1])
            if panel is not None:
                axis.imshow(panel, cmap="gray", vmin=limits[0], vmax=limits[1],
                            origin="lower", interpolation="nearest")
            if row == 0:
                axis.set_title(COLUMNS[column], fontsize=6.3, fontweight="bold", pad=4)
            axis.axis("off")
        _colorbar(figure.add_subplot(grid[row, 5]), limits)

    position = grid_spec.get_position(figure)
    figure.text(position.x0 - 0.014, min(0.995, position.y1 + 0.055), panel_label,
                fontsize=13, fontweight="bold", ha="left", va="top")


def create_figure(output_path=OUTPUT_PATH):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with plt.rc_context({**FONT, "font.size": 7}):
        figure = plt.figure(figsize=(PUBLICATION_WIDTH, 4.25))
        grid = figure.add_gridspec(1, 3, width_ratios=(1, 0.12, 1),
                                   left=0.014, right=0.960, bottom=0.025,
                                   top=0.93, wspace=0)
        for index, subject in enumerate(SUBJECTS):
            _draw_subject(figure, grid[index * 2], load_subject(subject),
                          f"({chr(97 + index)})")
        figure.savefig(output_path, dpi=300)
        plt.close(figure)
    return output_path


if __name__ == "__main__":
    create_figure()

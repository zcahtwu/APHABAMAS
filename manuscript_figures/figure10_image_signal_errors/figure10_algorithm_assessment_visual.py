"""Create Figure 10: Visual accuracy assessment.

Compare phantom images with analytical ground truth and show error maps.

Run: ``python -m manuscript_figures.figure10_image_signal_errors.figure10_algorithm_assessment_visual``
"""

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


HERE = Path(__file__).resolve().parent
OUTPUT_PATH = HERE / "figure10_algorithm_assessment_visual.svg"
RESULTS = REPOSITORY_ROOT / "experiments" / "real_motion_traces" / "phantom_results"
ROWS = (
    "Simulated Scan",
    "Error Map (Scan)",
    "Simulated Signal",
    "Error Map (Signal)",
)
COLUMNS = ("Ground truth", "Image-based", "Type-2 NUFFT", "Type-1 NUFFT")
LIMITS = ((0, 2), (-0.2, 0.2), (0, 10), (-1, 1))
TRAJECTORY_TITLES = ("(a) Trajectory 1 (Mild)", "(b) Trajectory 2 (Severe)")


def _slice(path, index):
    image = nib.load(path)
    return np.asanyarray(image.dataobj[:, :, index]).T


def load_subject(subject, *, include_signals=False):
    """Load image comparisons, optionally including the signal comparisons."""
    directory = RESULTS / subject
    image_paths = [directory / name for name in
                   ("GT.nii.gz", "image_based.nii.gz", "type2.nii.gz",
                    "type1_original.nii.gz")]
    signal_paths = [directory / name for name in
                    ("GT_signal.npy", "image_based_signal.npy", "type2_signal.npy")]
    required_paths = image_paths + signal_paths if include_signals else image_paths
    missing = [path for path in required_paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing simulation result(s):\n" +
                                "\n".join(map(str, missing)))

    images = [_slice(path, 96) for path in image_paths]
    image_rows = (
        images,
        (None, *(image - images[0] for image in images[1:])),
    )
    if not include_signals:
        return image_rows
    signals = [np.log(np.abs(np.load(path, mmap_mode="r")[:, :, 128])).T
               for path in signal_paths]
    return (
        *image_rows,
        (*signals, None),
        (None, *(signal - signals[0] for signal in signals[1:]), None),
    )


def _draw_subject(figure, subject, *, left, bottom, panel_width, panel_height,
                  panel_gap, title):
    """Draw one trajectory with its own color bars, using millimetre positions."""
    width, height = figure.get_size_inches() * 25.4
    group_width = 4 * panel_width + 3 * panel_gap
    group_top = bottom + len(subject) * panel_height + (len(subject) - 1) * panel_gap
    figure.text((left + group_width / 2) / width, (group_top + 8) / height,
                title, ha="center", va="bottom", fontsize=16, fontweight="bold")

    for row, (panels, label, limits) in enumerate(zip(subject, ROWS, LIMITS)):
        y = bottom + (len(subject) - 1 - row) * (panel_height + panel_gap)
        for column, panel in enumerate(panels):
            x = left + column * (panel_width + panel_gap)
            axis = figure.add_axes((x / width, y / height,
                                    panel_width / width, panel_height / height))
            if panel is not None:
                axis.imshow(panel, cmap="gray", vmin=limits[0], vmax=limits[1],
                            origin="lower", interpolation="nearest")
            if row == 0:
                axis.set_title(COLUMNS[column], fontsize=12, fontweight="bold", pad=6)
            axis.axis("off")

        center = y + panel_height / 2
        figure.text((left - 6.5) / width, center / height, label,
                    ha="center", va="center", rotation=90,
                    fontsize=12, fontweight="bold")
        bar_height = panel_height * 0.94
        axis = figure.add_axes(((left + group_width + 2) / width,
                                (center - bar_height / 2) / height,
                                2.2 / width, bar_height / height))
        bar = ColorbarBase(
            axis, cmap="gray", norm=Normalize(*limits),
            ticks=(limits[0], sum(limits) / 2, limits[1]), format="%.1f",
        )
        bar.ax.tick_params(labelsize=11.5, length=2.2, width=0.6, pad=2)
        bar.outline.set_linewidth(0.5)


def create_figure(output_path=OUTPUT_PATH):
    """Stack image and ground-truth error comparisons for trajectories 1 and 2."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subjects = [load_subject(subject) for subject in SUBJECTS]

    with plt.rc_context({**FONT, "font.size": 8}):
        width = PUBLICATION_WIDTH * 25.4
        panel_gap, trajectory_gap = 1.5, 21.0
        left, right, bottom, top = 12.0, 18.0, 4.0, 18.0
        panel_width = (width - left - right - 3 * panel_gap) / 4
        image_height, image_width = subjects[0][0][0].shape
        panel_height = panel_width * image_height / image_width
        group_height = 2 * panel_height + panel_gap
        height = bottom + 2 * group_height + trajectory_gap + top
        figure = plt.figure(figsize=(width / 25.4, height / 25.4))

        for index, (subject, title) in enumerate(zip(subjects, TRAJECTORY_TITLES)):
            _draw_subject(
                figure, subject, left=left,
                bottom=bottom + (1 - index) * (group_height + trajectory_gap),
                panel_width=panel_width, panel_height=panel_height,
                panel_gap=panel_gap, title=title,
            )

        save_figure(figure, output_path, dpi=300)
        plt.close(figure)
    return output_path


if __name__ == "__main__":
    configure_figure_output()
    create_figure()

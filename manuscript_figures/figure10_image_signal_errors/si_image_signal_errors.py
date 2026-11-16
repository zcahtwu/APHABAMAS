"""Create Figure 10 SI: visual accuracy assessment of images and signals.

Run: ``python -m manuscript_figures.figure10_image_signal_errors.si_image_signal_errors``
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import Normalize

from experiments.utils.figure_output import configure_figure_output, save_figure
from manuscript_figures.shared.style import (
    FONT,
    PUBLICATION_WIDTH,
    SUBJECTS,
)
from .figure10_algorithm_assessment_visual import (
    COLUMNS,
    LIMITS,
    ROWS,
    TRAJECTORY_TITLES,
    load_subject,
)


HERE = Path(__file__).resolve().parent
OUTPUT_PATH = HERE / "Supporting_Information" / "image_signal_errors.svg"


def create_figure(output_path=OUTPUT_PATH):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subjects = [load_subject(subject, include_signals=True) for subject in SUBJECTS]

    with plt.rc_context({**FONT, "font.size": 8}):
        width = PUBLICATION_WIDTH * 25.4
        panel_gap, trajectory_gap = 1.5, 3.0
        left, right, bottom = 9.0, 11.0, 4.0
        panel_width = (width - left - right - trajectory_gap - 6 * panel_gap) / 8
        image_height, image_width = subjects[0][0][0].shape
        panel_height = panel_width * image_height / image_width
        content_height = 4 * panel_height + 3 * panel_gap
        height = max(4.8 * 25.4, bottom + content_height + 14)
        group_width = 4 * panel_width + 3 * panel_gap
        figure = plt.figure(figsize=(width / 25.4, height / 25.4))

        for index, (subject, title) in enumerate(zip(subjects, TRAJECTORY_TITLES)):
            group_left = left + index * (group_width + trajectory_gap)
            figure.text((group_left + group_width / 2) / width, 1 - 4.5 / height, title,
                        ha="center", va="top", fontsize=10, fontweight="bold")

            for row, (panels, limits) in enumerate(zip(subject, LIMITS)):
                for column, panel in enumerate(panels):
                    x = group_left + column * (panel_width + panel_gap)
                    y = bottom + (3 - row) * (panel_height + panel_gap)
                    axis = figure.add_axes((x / width, y / height,
                                            panel_width / width, panel_height / height))
                    if panel is not None:
                        axis.imshow(panel, cmap="gray", vmin=limits[0], vmax=limits[1],
                                    origin="lower", interpolation="nearest")
                    if row == 0:
                        axis.set_title(COLUMNS[column], fontsize=7, fontweight="bold", pad=5)
                    axis.axis("off")

        for row, (label, limits) in enumerate(zip(ROWS, LIMITS)):
            y = bottom + (3 - row) * (panel_height + panel_gap)
            center = y + panel_height / 2
            figure.text(5.5 / width, center / height, label,
                        ha="center", va="center", rotation=90,
                        fontsize=8, fontweight="bold")
            bar_height = panel_height * 0.88
            axis = figure.add_axes(((width - right + 2) / width,
                                    (center - bar_height / 2) / height,
                                    1.4 / width, bar_height / height))
            bar = ColorbarBase(
                axis, cmap="gray", norm=Normalize(*limits),
                ticks=(limits[0], sum(limits) / 2, limits[1]), format="%.1f",
            )
            bar.ax.tick_params(labelsize=7, length=1.5, width=0.5, pad=2)
            bar.outline.set_linewidth(0.4)

        save_figure(figure, output_path, dpi=300)
        plt.close(figure)
    return output_path


if __name__ == "__main__":
    configure_figure_output()
    create_figure()

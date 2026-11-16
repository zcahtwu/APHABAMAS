"""Create supporting tracking/conversion plots for examples 1–4 and 5–8."""

from pathlib import Path

from experiments.utils.figure_output import configure_figure_output
from .figure7_real_trajectories import (
    SUBJECTS,
    create_figure,
)


OUTPUT_DIRECTORY = Path(__file__).resolve().parent / "Supporting_Information"


def generate_figures():
    outputs = []
    for start, stop in ((0, 4), (4, 8)):
        outputs.append(create_figure(
            SUBJECTS[start:stop],
            OUTPUT_DIRECTORY / f"real_trajectories_{start + 1}_{stop}.svg",
            tuple(f"Trajectory {index}" for index in range(start + 1, stop + 1)),
        ))
    return outputs


if __name__ == "__main__":
    configure_figure_output()
    generate_figures()

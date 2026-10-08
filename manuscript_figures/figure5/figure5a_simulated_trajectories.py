"""Create Figure 5a from saved simulated trajectories.

Run: ``python -m manuscript_figures.figure5.figure5a_simulated_trajectories``
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from manuscript_figures.shared.style import PUBLICATION_WIDTH, REPOSITORY_ROOT
from manuscript_figures.shared.trajectories import (
    DURATION,
    STYLE,
    add_header,
    add_pose_pair,
    save,
)


HERE = Path(__file__).resolve().parent
OUTPUT_PATH = HERE / "figure5a_simulated_trajectories.svg"
EXPERIMENTS = REPOSITORY_ROOT / "experiments" / "motion_type_investigation"
MOTIONS = (("Slow drift", "slow_drift"), ("Spikes", "spikes"),
           ("Step-wise", "stepwise"))
SEVERITIES = (("low", "Mild"), ("medium", "Moderate"), ("high", "Severe"))


def load_trajectory(motion, severity, repeat):
    path = EXPERIMENTS / motion / "trajectories" / f"{severity}_repeat_{repeat:02d}.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Generate the trajectories first.")
    with path.open() as file:
        saved = json.load(file)
    if (saved.get("severity"), saved.get("repeat")) != (severity, repeat):
        raise ValueError(f"Metadata does not match {path}")

    pose = np.column_stack((saved["translation"], saved["rotation"]))
    time = np.asarray(saved["time_points"]) * DURATION
    if len(time) == len(pose) + 1:
        pose = np.vstack((pose, pose[-1]))
    elif len(time) != len(pose):
        raise ValueError(f"Inconsistent trajectory lengths in {path}")
    return {"time": time, "translation": pose[:, :3], "rotation": pose[:, 3:]}


def create_figure(output_path=OUTPUT_PATH):
    output_path = Path(output_path)
    with plt.rc_context(STYLE):
        figure = plt.figure(figsize=(PUBLICATION_WIDTH, 6.5))
        grid = figure.add_gridspec(3, 3, left=0.14, right=0.985, bottom=0.075,
                                   top=0.865, wspace=0.11, hspace=0.24)
        add_header(figure, "(a)")

        for row, (severity, label) in enumerate(SEVERITIES):
            for column, (title, motion) in enumerate(MOTIONS):
                axes = add_pose_pair(
                    figure,
                    grid[row, column],
                    load_trajectory(motion, severity, repeat=row + 9),
                    title=title if row == 0 else None,
                    show_y=column == 0,
                    show_x=row == 2,
                )
                if column == 0:
                    axes[0].annotate(label, (-0.34, -0.04), xycoords="axes fraction",
                                     ha="center", va="center", rotation=90,
                                     fontsize=13, fontweight="bold")
        return save(figure, output_path)


if __name__ == "__main__":
    create_figure()

"""Create Figure 5b and two supporting tracking-comparison pages.

Run: ``python -m manuscript_figures.figure5.figure5b_real_trajectory_conversion``
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.transform import Rotation

from manuscript_figures.shared.style import PUBLICATION_WIDTH, REPOSITORY_ROOT
from manuscript_figures.shared.trajectories import (
    DURATION,
    STYLE,
    add_header,
    add_pose_pair,
    load_piecewise,
    save,
)


HERE = Path(__file__).resolve().parent
DATA = REPOSITORY_ROOT / "experiments" / "real_motion_traces"
TRACKING = DATA / "tracking_json"
CONVERTED = DATA / "piecewise_trajectories"
OUTPUT_PATH = HERE / "figure5b_real_trajectory_conversion.svg"
SI_DIRECTORY = HERE / "supporting_material"

SUBJECTS = (
    "BrainMRIMotionDB_2021-02-18_15_18_49447_Prospective-TracOline-Patient-5Y",
    "BrainMRIMotionDB_2021-02-26_13_13_45700_Prospective-TracOline-Patient-8Y",
    "BrainMRIMotionDB_2021-02-18_14_37_34483_Prospective-TracOline-Patient-8Y",
    "BrainMRIMotionDB_2021-04-15_13_29_72620_Prospective-TracOline-Patient-4Y",
    "BrainMRIMotionDB_2021-05-06_13_45_50298_Prospective-TracOline-Patient-7Y",
    "BrainMRIMotionDB_2021-06-03_13_41_53795_Prospective-TracOline-Patient-6Y",
    "BrainMRIMotionDB_2021-10-29_13_11_63503_Prospective-TracOline-Patient-6Y",
    "BrainMRIMotionDB_2021-11-05_14_17_54888_Prospective-TracOline-Patient-4Y",
)
MAIN_TITLES = ("Trajectory 1 (Mild)", "Trajectory 2 (Severe)")
COMPARISON_SOURCES = (
    ("tracking", "Tracking data", False),
    ("converted", "Converted trajectory", True),
)


def _seconds(timestamp):
    hour, minute, second = timestamp.split(":")
    return int(hour) * 3600 + int(minute) * 60 + float(second)


def load_tracking(subject):
    path = TRACKING / f"{subject}.json"
    with path.open() as file:
        motion = json.load(file)["MotionData"][0]

    absolute_time = np.asarray([_seconds(value) for value in motion["TimeStamp"]])
    time = (absolute_time - absolute_time[0]) % 86400
    keep = time < DURATION
    translation = np.column_stack([motion[f"M{row}4"] for row in range(1, 4)])[keep]
    matrices = np.stack([
        np.column_stack([motion[f"M{row}{column}"] for column in range(1, 4)])
        for row in range(1, 4)
    ], axis=1)[keep]
    return {
        "time": time[keep],
        "translation": translation,
        "rotation": Rotation.from_matrix(matrices).as_euler("xyz", degrees=True),
    }


def load_subject(subject, include_tracking):
    data = {"converted": load_piecewise(CONVERTED / f"{subject}.json")}
    if include_tracking:
        data["tracking"] = load_tracking(subject)
    return data


def require_json_files(subjects, include_tracking):
    """Fail before rendering when any required source JSON is unavailable."""
    required = [CONVERTED / f"{subject}.json" for subject in subjects]
    if include_tracking:
        required.extend(TRACKING / f"{subject}.json" for subject in subjects)
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing required Figure 5 trajectory JSON files:\n"
            + "\n".join(f"- {path}" for path in missing)
        )


def create_figure(subjects, output_path, sources, titles, panel_label=None):
    """Render one or more two-subject blocks with a shared legend."""
    if len(subjects) != len(titles) or len(subjects) % 2:
        raise ValueError("Subjects and titles must form matching pairs")
    output_path = Path(output_path)
    comparison = len(sources) == 2
    require_json_files(subjects, include_tracking=comparison)
    subject_data = [load_subject(subject, comparison) for subject in subjects]
    block_count = len(subjects) // 2

    with plt.rc_context(STYLE):
        figure = plt.figure(figsize=(
            PUBLICATION_WIDTH,
            4.75 * block_count if comparison else 3.0,
        ))
        grid = figure.add_gridspec(
            block_count, 1,
            left=0.14, right=0.985,
            bottom=0.05 if block_count > 1 else (0.09 if comparison else 0.16),
            top=0.91 if block_count > 1 else (0.835 if comparison else 0.70),
            hspace=0.19,
        )
        add_header(figure, panel_label, legend_y=0.995 if block_count > 1 else 0.985)

        for block in range(block_count):
            panel_grid = grid[block].subgridspec(
                len(sources), 2, wspace=0.11, hspace=0.42
            )
            for row, (source, row_label, stepped) in enumerate(sources):
                for column in range(2):
                    subject_index = 2 * block + column
                    axes = add_pose_pair(
                        figure,
                        panel_grid[row, column],
                        subject_data[subject_index][source],
                        title=titles[subject_index] if row == 0 else None,
                        stepped=stepped,
                        show_y=column == 0,
                    )
                    if column == 0 and row_label:
                        axes[0].annotate(
                            row_label, (-0.24, -0.08), xycoords="axes fraction",
                            ha="center", va="center", rotation=90,
                            fontsize=13, fontweight="bold",
                        )
        return save(figure, output_path)


def generate_all_figures():
    outputs = [create_figure(SUBJECTS[:2], OUTPUT_PATH,
                             (("converted", None, True),), MAIN_TITLES, "(b)")]
    titles = MAIN_TITLES + tuple(
        f"Trajectory {index}" for index in range(3, len(SUBJECTS) + 1)
    )
    for start in (0, 4):
        outputs.append(create_figure(
            SUBJECTS[start:start + 4],
            SI_DIRECTORY / f"real_trajectory_conversion_indices_{start + 1}_{start + 4}.svg",
            COMPARISON_SOURCES,
            titles[start:start + 4],
        ))
    return outputs


if __name__ == "__main__":
    generate_all_figures()

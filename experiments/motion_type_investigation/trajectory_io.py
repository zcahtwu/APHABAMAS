"""Shared JSON/plot output for motion trajectory generators."""

import json
from pathlib import Path

from experiments.utils.plot_trajectory import plot_motion_trajectory


def save_outputs(
    *,
    motion_type,
    title,
    severity,
    trajectory_index,
    seed,
    settings,
    information,
    trajectory,
    time_points,
    output_folder,
    save_trajectory,
    plot_trajectory,
):
    """Save one trajectory using the repository's established schema."""
    if not (save_trajectory or plot_trajectory):
        return
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    stem = f"{severity}_repeat_{trajectory_index + 1:02d}"

    if save_trajectory:
        data = {
            "motion_type": motion_type,
            "severity": severity,
            "repeat": trajectory_index + 1,
            "seed": seed,
            "settings": settings,
            "trajectory_information": information,
            "time_points": time_points.tolist(),
            "translation": trajectory[:, :3].tolist(),
            "rotation": trajectory[:, 3:6].tolist(),
        }
        with (output_folder / f"{stem}.json").open("w") as file:
            json.dump(data, file, indent=4)

    if plot_trajectory:
        plot_motion_trajectory(
            trajectory,
            time_points,
            output_folder / f"{stem}.svg",
            f"{title}: {severity}, repeat {trajectory_index + 1}",
        )


def generate_all(create_trajectory, severities, count, base_seed):
    """Generate the standard deterministic trajectory collection."""
    for severity in severities:
        for index in range(count):
            create_trajectory(
                severity_name=severity,
                trajectory_index=index,
                seed=base_seed + index,
                save_trajectory=True,
                plot_trajectory=True,
            )

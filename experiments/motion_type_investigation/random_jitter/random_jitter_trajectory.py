"""Generate Gaussian-derived poses normalized to maximum motion magnitudes."""

from pathlib import Path

import numpy as np

from experiments.utils.figure_output import configure_figure_output
from experiments.motion_type_investigation.trajectory_io import (
    generate_all,
    save_outputs,
)

DEFAULT_BASE_SEED = 0
DEFAULT_NUMBER_OF_TRAJECTORIES = 20
NUMBER_OF_TIME_POINTS = 256

# Maximum vector norms: translation in mm, rotation parameters in degrees.
SEVERITY_SETTINGS = {
    'low': {'translation': 0.5, 'rotation': 0.5},
    'medium': {'translation': 1.0, 'rotation': 1.0},
    'high': {'translation': 1.5, 'rotation': 1.5},
}

script_dir = Path(__file__).resolve().parent
default_output_folder = script_dir / 'trajectories'


def create_random_jitter_trajectory(
    severity_name,
    trajectory_index,
    seed=None,
    output_folder=default_output_folder,
    save_trajectory=True,
    plot_trajectory=False
):
    """Return poses [Tx, Ty, Tz, Rx, Ry, Rz], time boundaries, and settings."""
    if seed is None:
        seed = DEFAULT_BASE_SEED + trajectory_index

    settings = SEVERITY_SETTINGS[severity_name]
    rng = np.random.default_rng(seed)

    # Start at zero, then draw Gaussian poses for the remaining intervals.
    trajectory = np.zeros((NUMBER_OF_TIME_POINTS, 6))
    trajectory[1:] = rng.standard_normal((NUMBER_OF_TIME_POINTS - 1, 6))

    # Scale translation and rotation separately, preserving component ratios.
    translation_scale = settings['translation'] / np.max(
        np.linalg.norm(trajectory[:, :3], axis=1)
    )
    rotation_scale = settings['rotation'] / np.max(
        np.linalg.norm(trajectory[:, 3:6], axis=1)
    )
    trajectory[:, :3] *= translation_scale
    trajectory[:, 3:6] *= rotation_scale
    time_points = np.linspace(0, 1, NUMBER_OF_TIME_POINTS + 1)

    trajectory_information = settings.copy()

    save_outputs(
        motion_type='random_jitter',
        title='Random jitter',
        severity=severity_name,
        trajectory_index=trajectory_index,
        seed=seed,
        settings=settings,
        information=trajectory_information,
        trajectory=trajectory,
        time_points=time_points,
        output_folder=output_folder,
        save_trajectory=save_trajectory,
        plot_trajectory=plot_trajectory,
    )

    return trajectory, time_points, trajectory_information


if __name__ == '__main__':
    configure_figure_output()
    generate_all(create_random_jitter_trajectory, SEVERITY_SETTINGS,
                 DEFAULT_NUMBER_OF_TRAJECTORIES, DEFAULT_BASE_SEED)

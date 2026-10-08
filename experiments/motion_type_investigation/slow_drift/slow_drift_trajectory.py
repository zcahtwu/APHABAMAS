from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

from experiments.motion_type_investigation.trajectory_io import (
    generate_all,
    save_outputs,
)


# default settings shared by trajectory generation and the simulation experiment
DEFAULT_BASE_SEED = 0
DEFAULT_NUMBER_OF_TRAJECTORIES = 20
NUMBER_OF_TIME_POINTS = 256
NUMBER_OF_CONTROL_POINTS = 128
DIRECTION_CHANGE_PROBABILITY = 0.5

# slow-drift severity is controlled by the accumulated pose change, not by a
# number of separate motion events
SEVERITY_SETTINGS = {
    'low': {'translation': 1.0, 'rotation': 1.0},
    'medium': {'translation': 3.0, 'rotation': 3.0},
    'high': {'translation': 5.0, 'rotation': 5.0},
}

SEVERITIES = ('low', 'medium', 'high')

CONTROL_TIME_POINTS = np.linspace(
    0,
    (NUMBER_OF_TIME_POINTS - 1) / NUMBER_OF_TIME_POINTS,
    NUMBER_OF_CONTROL_POINTS
)

script_dir = Path(__file__).resolve().parent
default_output_folder = script_dir / 'trajectories'


def create_control_points(rng, motion_style):
    control_points = np.zeros((NUMBER_OF_CONTROL_POINTS, 6))
    directions = rng.choice([-1.0, 1.0], size=6)
    weights = rng.uniform(0.1, 0.25, size=6)

    if motion_style == 'nodding':
        weights[3], weights[5], weights[2] = 1.0, 0.25, 0.25
    else:
        weights[5], weights[3], weights[0] = 1.0, 0.25, 0.25

    for control_index in range(1, NUMBER_OF_CONTROL_POINTS):
        change_direction = rng.random(6) < DIRECTION_CHANGE_PROBABILITY
        directions[change_direction] *= -1
        increments = directions * rng.uniform(0.85, 1.15, size=6)
        control_points[control_index] = (
            control_points[control_index - 1] + increments * weights
        )

    # round the direction changes so they look like smooth waves rather than corners
    smoothing_weights = np.array([1.0, 2.0, 3.0, 2.0, 1.0]) / 9.0
    for DOF_index in range(6):
        padded_values = np.pad(control_points[:, DOF_index], 2, mode='edge')
        control_points[:, DOF_index] = np.convolve(
            padded_values,
            smoothing_weights,
            mode='valid'
        )

    # keep the trajectory starting from the reference pose
    control_points -= control_points[0]

    return control_points


def create_slow_drift_trajectory(
    severity_name,
    trajectory_index,
    seed=None,
    output_folder=default_output_folder,
    save_trajectory=True,
    plot_trajectory=False
):
    if seed is None:
        seed = DEFAULT_BASE_SEED + trajectory_index

    settings = SEVERITY_SETTINGS[severity_name]
    rng = np.random.default_rng(seed)
    motion_style = 'nodding' if trajectory_index % 2 == 0 else 'head_shaking'
    control_points = create_control_points(rng, motion_style)

    time_points = np.linspace(0, 1, NUMBER_OF_TIME_POINTS + 1)
    trajectory_time_points = time_points[:-1]

    # PCHIP gives a smooth, shape-preserving path without spline overshoot
    trajectory_interpolator = PchipInterpolator(
        CONTROL_TIME_POINTS,
        control_points,
        axis=0
    )
    trajectory = trajectory_interpolator(trajectory_time_points)

    translation_target = settings['translation']
    rotation_target = settings['rotation']
    translation_scale = translation_target / np.max(
        np.linalg.norm(trajectory[:, 0:3], axis=1)
    )
    rotation_scale = rotation_target / np.max(
        np.linalg.norm(trajectory[:, 3:6], axis=1)
    )
    trajectory[:, 0:3] *= translation_scale
    trajectory[:, 3:6] *= rotation_scale

    trajectory_information = {
        'motion_style': motion_style,
        'dominant_DOF': 'Rx' if motion_style == 'nodding' else 'Rz',
        'secondary_DOF': 'Rz' if motion_style == 'nodding' else 'Rx',
        'translation_target': translation_target,
        'rotation_target': rotation_target
    }

    save_outputs(
        motion_type='slow_drift',
        title='Slow drift',
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
    generate_all(create_slow_drift_trajectory, SEVERITIES,
                 DEFAULT_NUMBER_OF_TRAJECTORIES, DEFAULT_BASE_SEED)

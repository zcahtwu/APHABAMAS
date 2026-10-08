from pathlib import Path

import numpy as np

from experiments.motion_type_investigation.trajectory_io import (
    generate_all,
    save_outputs,
)


DEFAULT_BASE_SEED = 1
DEFAULT_NUMBER_OF_TRAJECTORIES = 20

SEVERITY_SETTINGS = {
    'low': {'minimum_steps': 2, 'maximum_steps': 3, 'translation': 1.0, 'rotation': 1.0},
    'medium': {'minimum_steps': 4, 'maximum_steps': 5, 'translation': 3.0, 'rotation': 3.0},
    'high': {'minimum_steps': 6, 'maximum_steps': 7, 'translation': 5.0, 'rotation': 5.0}
}

script_dir = Path(__file__).resolve().parent
default_output_folder = script_dir / 'trajectories'


def create_stepwise_trajectory(
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
    number_of_steps = rng.integers(
        settings['minimum_steps'], settings['maximum_steps'] + 1
    )

    # Random state lengths, with no state longer than one third of the scan.
    if number_of_steps == 2:
        state_durations = np.ones(3) / 3
    else:
        while True:
            state_durations = rng.dirichlet(np.ones(number_of_steps + 1) * 2)
            if np.max(state_durations) <= 1 / 3:
                break

    motion_times = np.cumsum(state_durations)[:-1]
    trajectory = np.zeros((number_of_steps + 1, 6))

    for step_index in range(number_of_steps):
        weights = rng.uniform(0.05, 0.25, size=6)
        weights *= rng.choice([-1.0, 1.0], size=6)

        # Alternate between nodding and head-shaking dominated steps.
        if (trajectory_index + step_index) % 2 == 0:
            weights[3] = rng.choice([-1.0, 1.0])
            weights[5] = rng.choice([-0.25, 0.25])
            weights[2] = rng.choice([-0.25, 0.25])
        else:
            weights[5] = rng.choice([-1.0, 1.0])
            weights[3] = rng.choice([-0.25, 0.25])
            weights[0] = rng.choice([-0.25, 0.25])

        pose_change = weights * rng.uniform(0.6, 1.0)
        trajectory[step_index + 1] = trajectory[step_index] + pose_change

    translation_scale = settings['translation'] / np.max(
        np.linalg.norm(trajectory[:, 0:3], axis=1)
    )
    rotation_scale = settings['rotation'] / np.max(
        np.linalg.norm(trajectory[:, 3:6], axis=1)
    )
    trajectory[:, 0:3] *= translation_scale
    trajectory[:, 3:6] *= rotation_scale

    time_points = np.hstack(([0], motion_times, [1]))
    trajectory_information = {'number_of_steps': int(number_of_steps)}

    save_outputs(
        motion_type='stepwise',
        title='Step-wise',
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
    generate_all(create_stepwise_trajectory, SEVERITY_SETTINGS,
                 DEFAULT_NUMBER_OF_TRAJECTORIES, DEFAULT_BASE_SEED)

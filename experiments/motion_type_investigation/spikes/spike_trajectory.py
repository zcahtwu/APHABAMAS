from pathlib import Path

import numpy as np

from experiments.motion_type_investigation.trajectory_io import (
    generate_all,
    save_outputs,
)


DEFAULT_BASE_SEED = 2
DEFAULT_NUMBER_OF_TRAJECTORIES = 20
NUMBER_OF_TIME_POINTS = 256

SEVERITY_SETTINGS = {
    'low': {'minimum_spikes': 2, 'maximum_spikes': 3, 'translation': 1.0, 'rotation': 1.0},
    'medium': {'minimum_spikes': 4, 'maximum_spikes': 5, 'translation': 3.0, 'rotation': 3.0},
    'high': {'minimum_spikes': 6, 'maximum_spikes': 7, 'translation': 5.0, 'rotation': 5.0}
}

script_dir = Path(__file__).resolve().parent
default_output_folder = script_dir / 'trajectories'


def create_spike_trajectory(
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
    number_of_spikes = rng.integers(
        settings['minimum_spikes'], settings['maximum_spikes'] + 1
    )
    trajectory = [np.zeros(6)]
    time_points = [0]

    # Distribute the spikes across the acquisition and keep away from its ends.
    spike_sections = np.array_split(
        np.arange(8, NUMBER_OF_TIME_POINTS - 8), number_of_spikes
    )

    for spike_index, section in enumerate(spike_sections):
        duration = int(1)
        start = int(rng.choice(section[:-duration]))
        spike_pose = np.zeros(6)
        direction = rng.choice([-1.0, 1.0])

        # Alternate between nodding (Tz, Rx) and head shaking (Tx, Rz).
        if (trajectory_index + spike_index) % 2 == 0:
            translation_index, rotation_index = 2, 3
        else:
            translation_index, rotation_index = 0, 5

        amplitude = direction * rng.uniform(0.7, 1.0)
        spike_pose[translation_index] = settings['translation'] * amplitude
        spike_pose[rotation_index] = settings['rotation'] * amplitude

        time_points.extend([
            start / NUMBER_OF_TIME_POINTS,
            (start + duration) / NUMBER_OF_TIME_POINTS
        ])
        trajectory.extend([spike_pose, np.zeros(6)])

    time_points.append(1)
    trajectory = np.array(trajectory)
    time_points = np.array(time_points)

    trajectory_information = {'number_of_spikes': int(number_of_spikes)}

    save_outputs(
        motion_type='spikes',
        title='Spikes',
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
    generate_all(create_spike_trajectory, SEVERITY_SETTINGS,
                 DEFAULT_NUMBER_OF_TRAJECTORIES, DEFAULT_BASE_SEED)

"""Run one phantom repeat per spike severity for a quick smoke test."""

from pathlib import Path

from experiments.motion_type_investigation.experiment import run_experiment
from experiments.motion_type_investigation.spikes.spike_trajectory import (
    DEFAULT_BASE_SEED,
    SEVERITY_SETTINGS,
    create_spike_trajectory,
)


HERE = Path(__file__).resolve().parent


def main():
    return run_experiment(
        motion_type="spikes",
        create_trajectory=create_spike_trajectory,
        severity_settings=SEVERITY_SETTINGS,
        base_seed=DEFAULT_BASE_SEED,
        number_of_repeats=1,
        working_directory=HERE,
        metadata=lambda _settings, info: {"number_of_spikes": info["number_of_spikes"]},
        scan_selection="phantom",
        output_directory=HERE / "temp",
        trajectory_directory=HERE / "temp" / "trajectories",
        metrics_filename="test_metrics.json",
        include_repeat_directory=False,
    )


if __name__ == "__main__":
    main()

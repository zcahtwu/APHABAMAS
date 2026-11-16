"""Run one phantom repeat per random-jitter severity for a smoke test."""

from pathlib import Path

from experiments.utils.figure_output import configure_figure_output
from experiments.motion_type_investigation.experiment import run_experiment
from experiments.motion_type_investigation.random_jitter.random_jitter_trajectory import (
    DEFAULT_BASE_SEED,
    SEVERITY_SETTINGS,
    create_random_jitter_trajectory,
)


HERE = Path(__file__).resolve().parent


def main():
    return run_experiment(
        motion_type="random_jitter",
        create_trajectory=create_random_jitter_trajectory,
        severity_settings=SEVERITY_SETTINGS,
        base_seed=DEFAULT_BASE_SEED,
        number_of_repeats=1,
        working_directory=HERE,
        metadata=lambda settings, _info: settings.copy(),
        scan_selection="phantom",
        output_directory=HERE / "temp",
        trajectory_directory=HERE / "temp" / "trajectories",
        metrics_filename="test_metrics.json",
        include_repeat_directory=False,
    )


if __name__ == "__main__":
    configure_figure_output()
    main()

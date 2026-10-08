"""Run one phantom repeat per slow-drift severity for a quick smoke test."""

from pathlib import Path

from experiments.motion_type_investigation.experiment import run_experiment
from experiments.motion_type_investigation.slow_drift.slow_drift_trajectory import (
    DEFAULT_BASE_SEED,
    SEVERITY_SETTINGS,
    create_slow_drift_trajectory,
)


HERE = Path(__file__).resolve().parent


def main():
    return run_experiment(
        motion_type="slow_drift",
        create_trajectory=create_slow_drift_trajectory,
        severity_settings=SEVERITY_SETTINGS,
        base_seed=DEFAULT_BASE_SEED,
        number_of_repeats=1,
        working_directory=HERE,
        metadata=lambda _settings, info: {"motion_style": info["motion_style"]},
        scan_selection="phantom",
        output_directory=HERE / "temp",
        trajectory_directory=HERE / "temp" / "trajectories",
        metrics_filename="test_metrics.json",
        include_repeat_directory=False,
    )


if __name__ == "__main__":
    main()

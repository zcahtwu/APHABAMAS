"""Run the complete spike-motion simulation experiment."""

from pathlib import Path

from experiments.motion_type_investigation.experiment import run_experiment
from experiments.motion_type_investigation.spikes.spike_trajectory import (
    DEFAULT_BASE_SEED,
    DEFAULT_NUMBER_OF_TRAJECTORIES,
    SEVERITY_SETTINGS,
    create_spike_trajectory,
)


HERE = Path(__file__).resolve().parent
SCAN_SELECTION = "both"
SAVE_SIMULATED_IMAGES = True
SAVE_TRAJECTORIES = True
PLOT_TRAJECTORIES = True


def _metadata(settings, information):
    return {
        "number_of_spikes": information["number_of_spikes"],
        "translation": settings["translation"],
        "rotation": settings["rotation"],
    }


def main():
    return run_experiment(
        motion_type="spikes",
        create_trajectory=create_spike_trajectory,
        severity_settings=SEVERITY_SETTINGS,
        base_seed=DEFAULT_BASE_SEED,
        number_of_repeats=DEFAULT_NUMBER_OF_TRAJECTORIES,
        working_directory=HERE,
        metadata=_metadata,
        scan_selection=SCAN_SELECTION,
        save_simulated_images=SAVE_SIMULATED_IMAGES,
        save_trajectory=SAVE_TRAJECTORIES,
        plot_trajectory=PLOT_TRAJECTORIES,
    )


if __name__ == "__main__":
    main()

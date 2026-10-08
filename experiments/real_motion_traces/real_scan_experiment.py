"""Run measured motion trajectories on the preprocessed real-brain scan."""

from pathlib import Path

from experiments.real_motion_traces.experiment import run_experiment


HERE = Path(__file__).resolve().parent
TRAJECTORY_DIRECTORY = HERE / "piecewise_trajectories"
OUTPUT_DIRECTORY = HERE / "real_scan_results"
IMAGE_PATH = OUTPUT_DIRECTORY / "normalized_real_data.nii.gz"
SAVE_SIMULATED_OUTPUTS = True


def main():
    return run_experiment(
        image_path=IMAGE_PATH,
        trajectory_directory=TRAJECTORY_DIRECTORY,
        output_directory=OUTPUT_DIRECTORY,
        save_simulated_outputs=SAVE_SIMULATED_OUTPUTS,
    )


if __name__ == "__main__":
    main()

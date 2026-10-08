"""Run measured motion trajectories on the digital phantom."""

from pathlib import Path

import nibabel as nib
import numpy as np

from experiments.real_motion_traces.experiment import run_experiment
from experiments.utils.shepp_logan_motion import SheppLoganMotionSimulator


HERE = Path(__file__).resolve().parent
TRAJECTORY_DIRECTORY = HERE / "piecewise_trajectories"
OUTPUT_DIRECTORY = HERE / "phantom_results"
IMAGE_PATH = OUTPUT_DIRECTORY / "Motion_free_192_256_256_1mm_1mm_1mm.nii.gz"
SAVE_SIMULATED_OUTPUTS = True


def ensure_motion_free_phantom():
    if IMAGE_PATH.exists():
        return
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    print(f"{IMAGE_PATH} not found. Simulating the motion-free phantom...")
    simulator = SheppLoganMotionSimulator(
        matrix_size=(192, 256, 256), delta_r=(1, 1, 1)
    )
    phantom = simulator.simulate(motion=False, magnitude=True)
    nib.save(nib.Nifti1Image(phantom, np.eye(4)), IMAGE_PATH)


def main():
    ensure_motion_free_phantom()
    return run_experiment(
        image_path=IMAGE_PATH,
        trajectory_directory=TRAJECTORY_DIRECTORY,
        output_directory=OUTPUT_DIRECTORY,
        phantom=True,
        save_simulated_outputs=SAVE_SIMULATED_OUTPUTS,
    )


if __name__ == "__main__":
    main()

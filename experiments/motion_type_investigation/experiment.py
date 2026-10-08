"""Shared runner for the slow-drift, spike, and step-wise experiments."""

import json
from pathlib import Path

import nibabel as nib
import numpy as np
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm

from experiments.utils.image_based_simulator import MotionSimulation as ImageBasedSimulator
from experiments.utils.k_space_based_simulator import MotionSimulation as KSpaceBasedSimulator
from experiments.utils.shepp_logan_motion import SheppLoganMotionSimulator


SCAN_FILES = {
    "phantom": "Motion_free_192_256_256_1mm_1mm_1mm.nii.gz",
    "real_brain": "normalized_real_data.nii.gz",
}


def select_scans(motion_free_directory, selection):
    scans = {name: motion_free_directory / filename
             for name, filename in SCAN_FILES.items()}
    if selection == "both":
        return scans
    key = {"real": "real_brain", "phantom": "phantom"}.get(selection)
    if key is None:
        raise ValueError("scan_selection must be 'real', 'phantom', or 'both'")
    return {key: scans[key]}


def calculate_metrics(image_based, type_1, type_2, ground_truth):
    """Calculate metrics in the same order used by the original scripts."""
    metrics = {
        "SSIM_type1_with_type2": ssim(type_1, type_2, data_range=2),
        "SSIM_type1_with_image_based": ssim(type_1, image_based, data_range=2),
        "SSIM_type2_with_image_based": ssim(type_2, image_based, data_range=2),
        "RMSD_type1_with_type2": np.sqrt(np.mean((type_1 - type_2) ** 2)),
        "RMSD_type1_with_image_based": np.sqrt(np.mean((type_1 - image_based) ** 2)),
        "RMSD_type2_with_image_based": np.sqrt(np.mean((type_2 - image_based) ** 2)),
    }
    if ground_truth is not None:
        metrics.update({
            "SSIM_image_based_with_GT": ssim(image_based, ground_truth, data_range=2),
            "SSIM_type1_with_GT": ssim(type_1, ground_truth, data_range=2),
            "SSIM_type2_with_GT": ssim(type_2, ground_truth, data_range=2),
            "RMSD_image_based_with_GT": np.sqrt(np.mean((image_based - ground_truth) ** 2)),
            "RMSD_type1_with_GT": np.sqrt(np.mean((type_1 - ground_truth) ** 2)),
            "RMSD_type2_with_GT": np.sqrt(np.mean((type_2 - ground_truth) ** 2)),
        })
    return metrics


def simulate_scan(image_path, trajectory, time_points, phantom):
    """Run the three algorithms and optional analytical phantom simulation."""
    image = nib.load(image_path)
    matrix_size = image.get_fdata().shape
    voxel_size = image.header.get_zooms()[:3]
    k_space_time = time_points * matrix_size[0] * matrix_size[1]

    k_space = KSpaceBasedSimulator(
        image_path=image_path,
        trajectory=trajectory.copy(),
        time_points=k_space_time,
        voxel_size=voxel_size,
    )
    type_1 = k_space.simulate(nufft_type="type1", phase_ramp_adjust=False)
    type_2 = k_space.simulate(nufft_type="type2")
    image_based = ImageBasedSimulator(
        image=str(image_path),
        trajectory=trajectory.copy(),
        time_points=time_points.copy(),
    ).simulate()

    ground_truth = None
    if phantom:
        simulator = SheppLoganMotionSimulator(
            matrix_size=matrix_size,
            delta_r=voxel_size,
            trajectory=trajectory.copy(),
            time_points=k_space_time.copy(),
        )
        ground_truth = np.abs(simulator.simulate(motion=True, magnitude=False))
    return image, image_based, type_1, type_2, ground_truth


def save_images(directory, affine, image_based, type_1, type_2, ground_truth):
    directory.mkdir(parents=True, exist_ok=True)
    images = {
        "image_based": image_based,
        "type1_original": type_1,
        "type2": type_2,
    }
    if ground_truth is not None:
        images["GT"] = ground_truth
    for name, image in images.items():
        nib.save(nib.Nifti1Image(image.astype(np.float32), affine),
                 directory / f"{name}.nii.gz")


def run_experiment(
    *,
    motion_type,
    create_trajectory,
    severity_settings,
    base_seed,
    number_of_repeats,
    working_directory,
    metadata,
    scan_selection="both",
    output_directory=None,
    trajectory_directory=None,
    metrics_filename="metrics.json",
    save_simulated_images=True,
    save_trajectory=True,
    plot_trajectory=True,
    include_repeat_directory=True,
):
    """Run one motion experiment without changing its seed or call ordering."""
    working_directory = Path(working_directory)
    output_directory = Path(output_directory or working_directory / "results")
    trajectory_directory = Path(trajectory_directory or working_directory / "trajectories")
    scans = select_scans(working_directory.parent / "motion_free_scans", scan_selection)
    output_directory.mkdir(parents=True, exist_ok=True)
    results = []

    for severity, settings in severity_settings.items():
        for repeat in tqdm(range(number_of_repeats), desc=severity):
            seed = base_seed + repeat
            trajectory, time_points, information = create_trajectory(
                severity_name=severity,
                trajectory_index=repeat,
                seed=seed,
                output_folder=trajectory_directory,
                save_trajectory=save_trajectory,
                plot_trajectory=plot_trajectory,
            )
            for scan, image_path in scans.items():
                image, image_based, type_1, type_2, ground_truth = simulate_scan(
                    image_path, trajectory, time_points, scan == "phantom"
                )
                result = {
                    "motion_type": motion_type,
                    "severity": severity,
                    "repeat": repeat + 1,
                    "seed": seed,
                    "scan": scan,
                    **metadata(settings, information),
                    **calculate_metrics(image_based, type_1, type_2, ground_truth),
                }
                results.append(result)

                if save_simulated_images:
                    directory = output_directory / severity
                    if include_repeat_directory:
                        directory /= f"repeat_{repeat + 1:02d}"
                    save_images(directory / scan, image.affine, image_based,
                                type_1, type_2, ground_truth)

    for result in results:
        for key, value in result.items():
            if isinstance(value, np.floating):
                result[key] = float(value)
    with (output_directory / metrics_filename).open("w") as file:
        json.dump(results, file, indent=4)
    return results

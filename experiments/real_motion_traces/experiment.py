"""Shared runner for experiments using measured motion trajectories."""

import json
from pathlib import Path

import nibabel as nib
import numpy as np
from numpy.fft import fftn, fftshift
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm

from experiments.utils.image_based_simulator import MotionSimulation as ImageBasedSimulator
from experiments.utils.k_space_based_simulator import MotionSimulation as KSpaceBasedSimulator
from experiments.utils.shepp_logan_motion import SheppLoganMotionSimulator


GT_METHODS = ("type1_original", "type1_adjusted", "type2", "image_based")
METHOD_PAIRS = (
    ("type1_original", "type2"),
    ("type1_original", "image_based"),
    ("type1_adjusted", "type2"),
    ("type1_adjusted", "image_based"),
    ("type2", "image_based"),
)


def load_trajectory(path, matrix_size):
    with Path(path).open() as file:
        data = json.load(file)
    time_points = np.asarray(data["time_points"])
    trajectory = np.hstack((data["translation"], data["rotation"]))
    k_space_time = time_points * matrix_size[0] * matrix_size[1]
    return trajectory, time_points, k_space_time


def _signal(image):
    return fftshift(fftn(fftshift(image)))


def simulate(image_path, matrix_size, trajectory, time_points, k_space_time,
             phantom):
    """Run the original simulations in their established call order."""
    images, signals = {}, {}

    if phantom:
        ground_truth = SheppLoganMotionSimulator(
            matrix_size=matrix_size,
            delta_r=(1, 1, 1),
            trajectory=trajectory,
            time_points=k_space_time,
        ).simulate(motion=True, magnitude=False)
        signals["GT"] = _signal(ground_truth)
        images["GT"] = np.abs(ground_truth)

    k_space = KSpaceBasedSimulator(
        image_path=image_path,
        trajectory=trajectory,
        time_points=k_space_time,
    )
    images["type1_original"] = k_space.simulate(
        nufft_type="type1", phase_ramp_adjust=False
    )
    images["type1_adjusted"] = k_space.simulate(
        nufft_type="type1", phase_ramp_adjust=True
    )

    if phantom:
        type_2 = k_space.simulate(nufft_type="type2", magnitude=False)
        signals["type2"] = _signal(type_2)
        images["type2"] = np.abs(type_2)
        image_based = ImageBasedSimulator(
            image=str(image_path), trajectory=trajectory, time_points=time_points
        ).simulate(magnitude=False)
        signals["image_based"] = _signal(image_based)
        images["image_based"] = np.abs(image_based)
    else:
        images["type2"] = k_space.simulate(nufft_type="type2")
        images["image_based"] = ImageBasedSimulator(
            image=str(image_path), trajectory=trajectory, time_points=time_points
        ).simulate()

    return images, signals


def _compare(metric, first, second):
    if metric == "SSIM":
        return float(ssim(first, second, data_range=2))
    return float(np.sqrt(np.mean((first - second) ** 2)))


def metric_keys(phantom):
    keys = []
    if phantom:
        keys.extend(
            f"{metric}_{method}_with_GT"
            for metric in ("SSIM", "RMSD")
            for method in GT_METHODS
        )
    keys.extend(
        f"{metric}_{first}_with_{second}"
        for metric in ("SSIM", "RMSD")
        for first, second in METHOD_PAIRS
    )
    return keys


def calculate_metrics(images, phantom):
    """Return metrics in the same key order as the existing JSON files."""
    metrics = {}
    if phantom:
        for metric in ("SSIM", "RMSD"):
            for method in GT_METHODS:
                metrics[f"{metric}_{method}_with_GT"] = _compare(
                    metric, images[method], images["GT"]
                )
    for metric in ("SSIM", "RMSD"):
        for first, second in METHOD_PAIRS:
            metrics[f"{metric}_{first}_with_{second}"] = _compare(
                metric, images[first], images[second]
            )
    return metrics


def save_outputs(directory, affine, images, signals):
    directory.mkdir(parents=True, exist_ok=True)
    for name, image in images.items():
        nib.save(nib.Nifti1Image(image, affine), directory / f"{name}.nii.gz")
    for name, signal in signals.items():
        np.save(directory / f"{name}_signal.npy", signal)


def run_experiment(
    *,
    image_path,
    trajectory_directory,
    output_directory,
    phantom=False,
    save_simulated_outputs=True,
):
    """Run every converted trajectory and retain the established output schema."""
    image_path = Path(image_path)
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    image = nib.load(image_path)
    matrix_size = image.get_fdata().shape

    trajectories = sorted(Path(trajectory_directory).glob("*.json"))
    names = []
    metric_lists = {key: [] for key in metric_keys(phantom)}
    for path in tqdm(trajectories):
        names.append(path.stem)
        trajectory, time_points, k_space_time = load_trajectory(path, matrix_size)
        images, signals = simulate(
            image_path, matrix_size, trajectory, time_points, k_space_time, phantom
        )
        if save_simulated_outputs:
            save_outputs(output_directory / path.stem, image.affine, images, signals)
        for key, value in calculate_metrics(images, phantom).items():
            metric_lists[key].append(value)

    results = {"traj_list": names, **metric_lists}
    with (output_directory / "metrics.json").open("w") as file:
        json.dump(results, file, indent=4)
    return results

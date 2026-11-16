# Figure 10: Visual accuracy assessment

[Figure guide](../)

Measured Trajectories 1 (mild) and 2 (severe) reveal where simulations depart from ground truth, including image blurring, ghosting, and signal errors. The main figure focuses on images and ground-truth error maps; the SI also includes log-magnitude signal comparisons.

## Inputs

Run the [measured-motion phantom experiment](../../experiments/real_motion_traces/#run-the-experiments) with `SAVE_SIMULATED_OUTPUTS = True`. Each selected trajectory folder under `experiments/real_motion_traces/phantom_results/` must contain:

- **Main figure and SI:** `GT.nii.gz`, `image_based.nii.gz`, `type2.nii.gz`, and `type1_original.nii.gz`.
- **SI only:** `GT_signal.npy`, `image_based_signal.npy`, and `type2_signal.npy`.

These files are generated locally. Type-1 signals are omitted because their non-uniform sampling locations prevent direct point-by-point comparison.

## Generate

Run from the repository root; add `--add-pdf` for matching PDF output.

```bash
python -m manuscript_figures.figure10_image_signal_errors.figure10_algorithm_assessment_visual
python -m manuscript_figures.figure10_image_signal_errors.si_image_signal_errors
```

## Outputs

- [Main figure](figure10_algorithm_assessment_visual.svg): reconstructed images and ground-truth error maps, with Trajectory 1 above Trajectory 2.
- [Image/signal SI](Supporting_Information/image_signal_errors.svg): images, error maps, log-magnitude signals, and signal errors for the two trajectories side by side.

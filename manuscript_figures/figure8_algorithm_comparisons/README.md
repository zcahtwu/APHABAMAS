# Figure 8: Algorithm comparisons

[Figure guide](../)

Different simulation algorithms produce different but visually plausible artifacts on brain and phantom images. The main figure shows simulated images and pairwise differences for measured Trajectories 1 (mild) and 2 (severe). Separate SI figures quantify pairwise agreement across four synthetic motion types. Multiplanar SI figures show sagittal, coronal, and axial views of brain and phantom simulations for both measured trajectories.

## Inputs

- **Main figure:** local `image_based.nii.gz`, `type2.nii.gz`, and `type1_original.nii.gz` for Trajectories 1–2 in `real_scan_results/` and `phantom_results/`; run the [measured-motion experiments](../../experiments/real_motion_traces/).
- **Quantitative SI:** included `between_algorithm_metrics.csv` and `between_algorithm_tests.csv` from the [pairwise analysis](../../experiments/motion_type_investigation/results/between_algorithms/).
- **Multiplanar SI:** the same local simulated images as the main figure, plus `GT.nii.gz` for Trajectories 1–2 in `phantom_results/`. No additional simulations are needed when these outputs already exist.

## Generate

Run from the repository root once the inputs are available; add `--add-pdf` for matching PDF output.

```bash
python -m manuscript_figures.figure8_algorithm_comparisons.figure8_algorithm_comparisons
python -m manuscript_figures.figure8_algorithm_comparisons.si_quantitative_comparisons
python -m manuscript_figures.figure8_algorithm_comparisons.si_real_brain_multiview
python -m manuscript_figures.figure8_algorithm_comparisons.si_phantom_multiview
```

## Outputs

- [Main figure](figure8_algorithm_comparisons.svg): brain comparisons above phantom comparisons, with Trajectories 1–2 side by side.
- [Brain SI](Supporting_Information/real_brain_quantitative_comparisons.svg): pairwise SSIM and RMSD across motion types and severities.
- [Phantom SI](Supporting_Information/phantom_quantitative_comparisons.svg): the corresponding phantom metrics.
- [Brain multiplanar SI](Supporting_Information/real_brain_multiview.svg): sagittal, coronal, and axial reconstructions and pairwise algorithm differences for Trajectories 1–2.
- [Phantom multiplanar SI](Supporting_Information/phantom_multiview.svg): the same three views, including ground truth and error maps against ground truth for Trajectories 1–2.

The multiplanar generators use the [shared renderer](../shared/multiview_comparison.py). They use scan-specific slice indices and intensity ranges, display the simulation differences, and export images at 1200 dpi.

SI boxplots include outliers; `ns` marks non-significant comparisons after Holm correction. These metrics measure agreement between algorithms.

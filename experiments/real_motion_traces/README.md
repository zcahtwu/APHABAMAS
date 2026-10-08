# Tracking-data-derived motion

[Experiments](../) · [Setup](../../docs/#setup)

Eight recorded head-motion traces from [Brain MRI Motion Database](http://brainmrimotion.org/)
are used in both phases. Phase 1 compares
algorithms on brain and phantom images to demonstrate their differences.
Phase 2 assesses phantom image and signal errors against analytical ground truth.

## Prepare inputs

Raw records in `tracking_json/` and converted JSONs in `piecewise_trajectories/`
are included. [data_description.txt](data_description.txt) lists their source
and trajectory order.

For brain simulations, place the MR-ART scan
`sub-000103_acq-standard_T1w.nii.gz` in `real_scan_results/`, then preprocess it:

```bash
python -m experiments.real_scan_preprocessing
```

This creates `real_scan_results/normalized_real_data.nii.gz`. The phantom
driver creates `phantom_results/Motion_free_192_256_256_1mm_1mm_1mm.nii.gz`
if absent. MRI inputs and simulation images/signals are not included in Git.

## Run the experiments

Run from the repository root:

```bash
python -m experiments.real_motion_traces.trajectory_convert
python -m experiments.real_motion_traces.phantom_experiment
python -m experiments.real_motion_traces.real_scan_experiment
```

A phantom-only run needs the first two commands. Keep
`SAVE_SIMULATED_OUTPUTS = True` in the drivers to generate image and signal figures.

## Outputs

`phantom_results/` and `real_scan_results/` contain `metrics.json` and a folder
per trajectory with `image_based.nii.gz`, `type1_original.nii.gz`,
`type1_adjusted.nii.gz`, and `type2.nii.gz`. Phantom runs also save `GT.nii.gz`
and ground-truth, image-based, and Type-2 signals as `*_signal.npy`.

Phase 1 results feed [Figure 6b/c](../../manuscript_figures/figure6/)
and [Figure 7b/c](../../manuscript_figures/figure7/); phase 2 results
feed [Figure 9](../../manuscript_figures/figure9/).
[Figure 5b](../../manuscript_figures/figure5/) illustrates the motion inputs.

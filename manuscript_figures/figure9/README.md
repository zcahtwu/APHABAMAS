# Figure 9: Image and signal errors

[Figure guide](../)

Measured Trajectories 1 and 2 reveal where simulations depart from ground
truth, including image blurring, ghosting, and high-frequency signal errors.

## Inputs

Run the [measured-motion phantom experiment](../../experiments/real_motion_traces/#run-the-experiments)
with `SAVE_SIMULATED_OUTPUTS = True`. Each selected trajectory folder under
`experiments/real_motion_traces/phantom_results/` must contain:

- `GT.nii.gz`, `image_based.nii.gz`, `type2.nii.gz`, and `type1_original.nii.gz`.
- `GT_signal.npy`, `image_based_signal.npy`, and `type2_signal.npy`.

These files are generated locally. Type-1 signals are omitted because their
non-uniform sampling locations prevent direct point-by-point comparison.

## Generate

From the repository root:

```bash
python -m manuscript_figures.figure9.figure9_algorithm_assessment_visual
```

## Output

[Figure 9](figure9_algorithm_assessment_visual.svg): reconstructed images,
ground-truth error maps, and log-magnitude signal comparisons.

# Figure 7: Phantom algorithm comparisons

[Figure guide](../)

Algorithm disagreement on the phantom resembles that on brain data, supporting
its use as a surrogate for accuracy assessment.

## Inputs

- **7a:** included `between_algorithm_metrics.csv` and `between_algorithm_tests.csv` from the [controlled-motion analysis](../../experiments/motion_type_investigation/results/), filtered to phantom data.
- **7b/c and multiview SI:** local `image_based.nii.gz`, `type1_original.nii.gz`, and `type2.nii.gz` for measured Trajectories 1 and 2 in `phantom_results/`. Multiview SI also needs `GT.nii.gz`; run the [measured-motion phantom experiment](../../experiments/real_motion_traces/).

## Generate

Run each command from the repository root once its inputs are available:

```bash
python -m manuscript_figures.figure7.figure7a_between_algorithm_phantom
python -m manuscript_figures.figure7.figure7bc_phantom_visual_comparison
python -m manuscript_figures.figure7.figure7_phantom_multiview_SI
```

## Outputs

- [7a: agreement metrics](figure7a_between_algorithm_phantom.svg) and [sample-point SI](figure7a_between_algorithm_phantom_SI.svg).
- [7b/c: image comparisons](figure7bc_phantom_visual_comparison.svg).
- [Multiview SI](figure7_phantom_multiview_SI.svg): orthogonal views, ground truth, and error maps.

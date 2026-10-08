# Figure 6: Brain algorithm comparisons

[Figure guide](../)

Different algorithms generate different but visually plausible brain artifacts.
Pairwise agreement establishes the need for a ground-truth accuracy assessment.

## Inputs

- **6a:** included `between_algorithm_metrics.csv` and `between_algorithm_tests.csv` from the [controlled-motion analysis](../../experiments/motion_type_investigation/results/), filtered to brain data.
- **6b/c and multiview SI:** local `image_based.nii.gz`, `type1_original.nii.gz`, and `type2.nii.gz` for measured Trajectories 1 and 2 in `real_scan_results/`; run the [measured-motion brain experiment](../../experiments/real_motion_traces/).

## Generate

Run each command from the repository root once its inputs are available:

```bash
python -m manuscript_figures.figure6.figure6a_between_algorithm_real
python -m manuscript_figures.figure6.figure6bc_real_visual_comparison
python -m manuscript_figures.figure6.figure6_real_multiview_SI
```

## Outputs

- [6a: agreement metrics](figure6a_between_algorithm_real.svg) and [sample-point SI](figure6a_between_algorithm_real_SI.svg).
- [6b/c: image comparisons](figure6bc_real_visual_comparison.svg).
- [Multiview SI](figure6_real_multiview_SI.svg): orthogonal views and pairwise differences.

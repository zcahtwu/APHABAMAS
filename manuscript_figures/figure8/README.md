# Figure 8: Accuracy against ground truth

[Figure guide](../)

SSIM and RMSD against the analytical phantom reference reveal simulation
accuracy across synthetic motion types and severities. Type-2 NUFFT shows
the most consistent agreement in the study.

## Inputs

Included tables in `experiments/motion_type_investigation/results/phantom/`:

- [phantom_GT_metrics.csv](../../experiments/motion_type_investigation/results/phantom/phantom_GT_metrics.csv): ground-truth accuracy metrics.
- [paired_algorithm_tests.csv](../../experiments/motion_type_investigation/results/phantom/paired_algorithm_tests.csv): paired statistical comparisons.

No MRI files are needed. To regenerate the tables, follow the
[analysis guide](../../experiments/motion_type_investigation/results/).

## Generate

From the repository root:

```bash
python -m manuscript_figures.figure8.figure8_phantom_gt_metrics
```

## Outputs

- [Main figure](figure8_phantom_gt_metrics.svg): boxplots with outliers.
- [Sample-point SI](figure8_phantom_gt_metrics_SI.svg): boxplots with all samples.

Higher SSIM and lower RMSD indicate better agreement. `ns` marks comparisons
that are non-significant after Holm correction.

# Figure 9: Quantitative accuracy assessment

[Figure guide](../)

SSIM and RMSD against the analytical phantom reference measure simulation accuracy across motion types and severities. The main figure shows slow-drift, spikes, and step-wise motion. Random jitter is presented separately in SI because it requires wider axis ranges, allowing clearer comparisons in the main figure.

## Inputs

Included tables in `experiments/motion_type_investigation/results/phantom/`:

- [phantom_GT_metrics.csv](../../experiments/motion_type_investigation/results/phantom/phantom_GT_metrics.csv): quantitative accuracy metrics against ground truth.
- [paired_algorithm_tests.csv](../../experiments/motion_type_investigation/results/phantom/paired_algorithm_tests.csv): paired statistical comparisons.

No MRI files are needed. To regenerate the tables, follow the [analysis guide](../../experiments/motion_type_investigation/results/).

## Generate

Run from the repository root; add `--add-pdf` for matching PDF output.

```bash
python -m manuscript_figures.figure9_ground_truth_accuracy.figure9_phantom_gt_metrics
python -m manuscript_figures.figure9_ground_truth_accuracy.si_random_jitter_gt_metrics
```

## Outputs

- [Main figure](figure9_phantom_gt_metrics.svg): SSIM above RMSD for three motion types, grouped by mild, moderate, and severe motion.
- [Random-jitter SI](Supporting_Information/random_jitter_ground_truth_accuracy.svg): SSIM and RMSD with wider axis ranges.

Higher SSIM and lower RMSD indicate closer agreement with ground truth. Dots mark outliers; `ns` marks non-significant paired comparisons after Holm correction.

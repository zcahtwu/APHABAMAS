# Controlled-motion analysis outputs

[Controlled motion](../) · [Figures](../../../manuscript_figures/)

These tables combine the four motion models. Each model stores `metrics.json` and simulation images in its own `results/` folder.

| Folder | Included tables | Phase and figures |
| --- | --- | --- |
| [between_algorithms/](between_algorithms/) | `between_algorithm_metrics.csv`, `between_algorithm_tests.csv`, and a significance summary | Phase 1: algorithm differences (Figure 8 supporting information) |
| [phantom/](phantom/) | `phantom_GT_metrics.csv` and `paired_algorithm_tests.csv` | Phase 2: quantitative accuracy assessment (Figure 9 and its random-jitter supporting information) |

## Regenerate

From the repository root, using the saved per-model metrics:

```bash
python -m experiments.motion_type_investigation.analyse_between_algorithms
python -m experiments.motion_type_investigation.analyse_phantom_results
```

Analyses compare paired metric values using a paired t-test or Wilcoxon test, selected by Shapiro–Wilk testing of paired differences, with Holm correction. Diagnostic Q–Q plots go to `normality_plots/`. Use the [Figure 9 quantitative accuracy assessment generators](../../../manuscript_figures/figure9_ground_truth_accuracy/) for the manuscript accuracy plots.

# Controlled-motion analysis outputs

[Controlled motion](../) · [Figures](../../../manuscript_figures/)

These tables combine the three motion models. Each model's original
`metrics.json` and simulation images remain in its own `results/` folder.

| Folder | Included tables | Phase and figures |
| --- | --- | --- |
| [between_algorithms/](between_algorithms/) | `between_algorithm_metrics.csv`, `between_algorithm_tests.csv`, and a significance summary | Phase 1: algorithm differences (Figures 6a and 7a) |
| [phantom/](phantom/) | `phantom_GT_metrics.csv` and `paired_algorithm_tests.csv` | Phase 2: ground-truth accuracy (Figure 8) |

## Regenerate

From the repository root, using the saved per-model metrics:

```bash
python -m experiments.motion_type_investigation.analyse_between_algorithms
python -m experiments.motion_type_investigation.analyse_phantom_results
```

Analyses compare paired metric values using a paired t-test or Wilcoxon test,
selected by Shapiro–Wilk testing of paired differences, with Holm correction.
Diagnostic Q–Q plots go to `normality_plots/`. Use the
[Figure 8 generator](../../../manuscript_figures/figure8/) for the
manuscript accuracy plots; the older `phantom_GT_boxplots.svg` is not regenerated.

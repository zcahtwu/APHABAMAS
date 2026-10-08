# Between-algorithm significance table

Each entry is the Holm-adjusted p-value followed by its significance symbol and test abbreviation. Each test compares two plotted algorithm-pair metrics, matched by trajectory repeat. Differences are the first listed group's metric minus the second's.

T1 = Type-1 NUFFT; T2 = Type-2 NUFFT; image = image-based. For example, (T2 vs. image) vs. (T1 vs. image) compares their SSIM or RMSD values for the same trajectories.

## Real-brain data — SSIM

| Motion type | Severity | (T2 vs. image) vs. (T1 vs. image) | (T2 vs. image) vs. (T1 vs. T2) | (T1 vs. image) vs. (T1 vs. T2) |
| --- | --- | ---: | ---: | ---: |
| Slow drift | Mild | 4.20e-08 (***; t) | 3.28e-16 (***; t) | 3.28e-16 (***; t) |
| Slow drift | Medium | 8.96e-08 (***; t) | 5.01e-12 (***; t) | 1.91e-06 (***; W) |
| Slow drift | Severe | 5.85e-09 (***; t) | 4.00e-05 (***; t) | 5.50e-13 (***; t) |
| Spikes | Mild | 5.72e-06 (***; W) | 5.72e-06 (***; W) | 0.120 (ns; t) |
| Spikes | Medium | 1.62e-08 (***; t) | 1.62e-08 (***; t) | 1.28e-08 (***; t) |
| Spikes | Severe | 8.92e-10 (***; t) | 7.41e-10 (***; t) | 3.81e-06 (***; W) |
| Step-wise | Mild | 3.81e-06 (***; W) | 0.005 (**; W) | 2.27e-19 (***; t) |
| Step-wise | Medium | 2.19e-09 (***; t) | 2.26e-05 (***; t) | 5.45e-15 (***; t) |
| Step-wise | Severe | 2.20e-10 (***; t) | 1.84e-07 (***; t) | 5.24e-12 (***; t) |

## Real-brain data — RMSD

| Motion type | Severity | (T2 vs. image) vs. (T1 vs. image) | (T2 vs. image) vs. (T1 vs. T2) | (T1 vs. image) vs. (T1 vs. T2) |
| --- | --- | ---: | ---: | ---: |
| Slow drift | Mild | 1.53e-06 (***; t) | 3.19e-18 (***; t) | 3.19e-18 (***; t) |
| Slow drift | Medium | 8.61e-11 (***; t) | 2.16e-14 (***; t) | 5.53e-18 (***; t) |
| Slow drift | Severe | 2.28e-11 (***; t) | 4.85e-04 (***; t) | 1.07e-08 (***; t) |
| Spikes | Mild | 5.72e-06 (***; W) | 5.72e-06 (***; W) | 5.72e-06 (***; W) |
| Spikes | Medium | 3.81e-06 (***; W) | 7.95e-10 (***; t) | 3.81e-06 (***; W) |
| Spikes | Severe | 1.75e-12 (***; t) | 1.44e-12 (***; t) | 1.81e-13 (***; t) |
| Step-wise | Mild | 1.91e-06 (***; W) | 1.27e-19 (***; t) | 8.56e-21 (***; t) |
| Step-wise | Medium | 1.91e-06 (***; W) | 5.77e-07 (***; t) | 3.17e-15 (***; t) |
| Step-wise | Severe | 2.51e-09 (***; t) | 0.024 (*; t) | 2.86e-10 (***; t) |

## Digital phantom — SSIM

| Motion type | Severity | (T2 vs. image) vs. (T1 vs. image) | (T2 vs. image) vs. (T1 vs. T2) | (T1 vs. image) vs. (T1 vs. T2) |
| --- | --- | ---: | ---: | ---: |
| Slow drift | Mild | 0.003 (**; t) | 4.37e-14 (***; t) | 7.87e-14 (***; t) |
| Slow drift | Medium | 1.86e-08 (***; t) | 5.61e-09 (***; t) | 1.21e-18 (***; t) |
| Slow drift | Severe | 9.38e-11 (***; t) | 1.07e-07 (***; t) | 3.31e-14 (***; t) |
| Spikes | Mild | 9.13e-08 (***; t) | 7.93e-08 (***; t) | 2.72e-08 (***; t) |
| Spikes | Medium | 1.68e-10 (***; t) | 1.27e-10 (***; t) | 1.80e-15 (***; t) |
| Spikes | Severe | 6.20e-11 (***; t) | 6.00e-11 (***; t) | 1.92e-19 (***; t) |
| Step-wise | Mild | 3.81e-06 (***; W) | 0.651 (ns; t) | 1.40e-17 (***; t) |
| Step-wise | Medium | 1.51e-09 (***; t) | 1.38e-07 (***; t) | 1.33e-11 (***; t) |
| Step-wise | Severe | 6.96e-10 (***; t) | 8.37e-09 (***; t) | 4.23e-07 (***; t) |

## Digital phantom — RMSD

| Motion type | Severity | (T2 vs. image) vs. (T1 vs. image) | (T2 vs. image) vs. (T1 vs. T2) | (T1 vs. image) vs. (T1 vs. T2) |
| --- | --- | ---: | ---: | ---: |
| Slow drift | Mild | 3.17e-05 (***; t) | 1.78e-18 (***; t) | 1.78e-18 (***; t) |
| Slow drift | Medium | 5.13e-11 (***; t) | 1.08e-15 (***; t) | 7.18e-19 (***; t) |
| Slow drift | Severe | 1.22e-11 (***; t) | 0.017 (*; t) | 7.94e-11 (***; t) |
| Spikes | Mild | 3.81e-06 (***; W) | 3.81e-06 (***; W) | 2.15e-12 (***; t) |
| Spikes | Medium | 2.97e-09 (***; t) | 2.77e-09 (***; t) | 1.14e-13 (***; t) |
| Spikes | Severe | 7.42e-10 (***; t) | 5.97e-10 (***; t) | 1.91e-06 (***; W) |
| Step-wise | Mild | 1.91e-06 (***; W) | 2.59e-18 (***; t) | 4.32e-20 (***; t) |
| Step-wise | Medium | 2.10e-08 (***; t) | 5.10e-04 (***; t) | 5.36e-14 (***; t) |
| Step-wise | Severe | 3.18e-09 (***; t) | 0.012 (*; t) | 2.08e-10 (***; t) |

**Significance:** `***` p < 0.001; `**` p < 0.01; `*` p < 0.05; `ns` p ≥ 0.05.

**Tests:** `t`, two-sided paired t-test (mean paired difference = 0); `W`, Wilcoxon signed-rank test. Normality of the paired differences was assessed using the Shapiro–Wilk test (alpha = 0.05). Wilcoxon tests whether the paired-difference distribution is symmetric about zero. Constant differences skip Shapiro–Wilk; all-zero differences return p = 1, otherwise Wilcoxon is used.

Holm correction was applied across the three algorithm-pair comparisons within each scan, motion type, severity, and metric. Only finite matched repeats are used for each comparison; the CSV reports n, group means, and signed mean/median differences.

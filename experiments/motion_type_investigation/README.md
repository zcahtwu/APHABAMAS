# Controlled motion

[Experiments](../) · [Setup](../../docs/#setup)

This study separates the effects of motion type and severity: three models,
three severity levels, and 20 trajectories per level (180 trajectories total).
In phase 1, brain and phantom runs demonstrate differences between algorithms.
In phase 2, phantom ground truth enables accuracy assessment.

## Specify a motion pattern

| Pattern | Description | Low / medium / high settings |
| --- | --- | --- |
| [Slow drift](slow_drift/) | Smooth accumulated pose changes | Maximum translation/rotation norms: 1 / 3 / 5 mm/degrees |
| [Spikes](spikes/) | Brief departures from the reference pose | 2–3 / 4–5 / 6–7 events; amplitude limits: 1 / 3 / 5 mm/degrees |
| [Step-wise](stepwise/) | Sustained pose changes | 2–3 / 4–5 / 6–7 steps; maximum pose norms: 1 / 3 / 5 mm/degrees |

Each model guide includes a trajectory-only command that needs no MRI files.

## Run the complete experiment

Prepare the [motion-free scans](motion_free_scans/), then run from the
repository root:

```bash
python -m experiments.motion_type_investigation.slow_drift.slow_drift
python -m experiments.motion_type_investigation.spikes.spikes
python -m experiments.motion_type_investigation.stepwise.stepwise
```

The drivers default to both scans. Set `SCAN_SELECTION` to `"phantom"` or
`"real"` to select one; set `SAVE_SIMULATED_IMAGES = False` to retain only metrics.
Each model writes `results/metrics.json` and optional images under
`results/<severity>/repeat_<NN>/<scan>/`.

## Analyse and plot

Saved metrics are included. For phase 1 (inter-algorithm comparisons):

```bash
python -m experiments.motion_type_investigation.analyse_between_algorithms
```

For phase 2 (accuracy against ground truth):

```bash
python -m experiments.motion_type_investigation.analyse_phantom_results
```

See [analysis outputs](results/) for the tables. They feed
[Figures 6 and 7](../../manuscript_figures/) (algorithm agreement) and
[Figure 8](../../manuscript_figures/figure8/) (ground-truth accuracy).

# Slow drift

[Controlled motion](../) · [Scan inputs](../motion_free_scans/)

Smooth accumulated pose changes alternate between nodding and head shaking.
Low, medium, and high severity use maximum translation/rotation norms of
1, 3, and 5 mm/degrees, with 20 trajectories each.

## Run

From the repository root, generate trajectories without MRI inputs:

```bash
python -m experiments.motion_type_investigation.slow_drift.slow_drift_trajectory
```

With the scan inputs prepared, run the full experiment:

```bash
python -m experiments.motion_type_investigation.slow_drift.slow_drift
```

## Outputs

Trajectory JSONs and SVGs go to `trajectories/`; metrics and optional simulation
images go to `results/`. Settings are in [slow_drift.py](slow_drift.py).
Continue with the [combined analysis](../#analyse-and-plot).

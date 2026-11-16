# Random jitter

[Controlled motion](../) · [Scan inputs](../motion_free_scans/)

Gaussian-generated poses fluctuate around the reference position, starting at zero and held constant during each acquisition interval. Translation and rotation are scaled separately to maximum vector norms of 0.5, 1, and 1.5 mm/degrees for low, medium, and high severity, with 20 trajectories each.

## Run

From the repository root, generate trajectories without MRI inputs:

```bash
python -m experiments.motion_type_investigation.random_jitter.random_jitter_trajectory
```

With the scan inputs prepared, run the full experiment:

```bash
python -m experiments.motion_type_investigation.random_jitter.random_jitter
```

## Outputs

Trajectory JSONs and SVGs go to `trajectories/`; metrics and optional simulation images go to `results/`. Settings are in [random_jitter.py](random_jitter.py). Continue with the [combined analysis](../#analyse-and-plot).

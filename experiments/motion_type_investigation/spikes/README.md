# Spikes

[Controlled motion](../) · [Scan inputs](../motion_free_scans/)

Brief motion events return to the reference pose after one acquisition time
point (one TR). Low, medium, and high severity use 2–3, 4–5, and 6–7 events
with amplitude limits of 1, 3, and 5 mm/degrees, with 20 trajectories each.

## Run

From the repository root, generate trajectories without MRI inputs:

```bash
python -m experiments.motion_type_investigation.spikes.spike_trajectory
```

With the scan inputs prepared, run the full experiment:

```bash
python -m experiments.motion_type_investigation.spikes.spikes
```

## Outputs

Trajectory JSONs and SVGs go to `trajectories/`; metrics and optional simulation
images go to `results/`. Settings are in [spikes.py](spikes.py).
Continue with the [combined analysis](../#analyse-and-plot).

# Figure 7: Motion trajectories

[Figure guide](../)

Measured head-motion tracking is compared with the converted trajectories used in the simulations for Trajectories 1 (mild) and 2 (severe). The SI includes Trajectories 1–8, repeating Trajectories 1–2 from the main figure, and examples of four synthetic motion types at three severities.

## Inputs

- Tracking and converted trajectory JSONs from the [measured-motion experiments](../../experiments/real_motion_traces/).
- Slow-drift, spikes, step-wise, and random-jitter trajectory JSONs from the [controlled-motion experiments](../../experiments/motion_type_investigation/).

No MRI files are needed. Generate the synthetic trajectories before rendering that SI figure.

## Generate

Run from the repository root; add `--add-pdf` for matching PDF output.

```bash
python -m manuscript_figures.figure7_motion_trajectories.figure7_real_trajectories
python -m manuscript_figures.figure7_motion_trajectories.si_simulated_trajectories
python -m manuscript_figures.figure7_motion_trajectories.si_real_trajectories
```

## Outputs

- [Main figure](figure7_real_trajectories.svg): measured and converted Trajectories 1–2.
- [Simulated-motion SI](Supporting_Information/simulated_trajectories.svg): translations and rotations for four motion types at mild, moderate, and severe levels.
- Supporting tracking/conversion figures: [Trajectories 1–4](Supporting_Information/real_trajectories_1_4.svg) and [5–8](Supporting_Information/real_trajectories_5_8.svg), using the same four-trajectory layout.

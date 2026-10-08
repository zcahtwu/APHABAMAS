# Figure 5: Motion trajectories

[Figure guide](../)

This figure documents motion inputs shared by both experiment phases: three
synthetic motion models at three severities (5a), and measured head motion
converted to discrete states (5b and supporting pages).

## Inputs

Generate JSONs using the three [motion-model guides](../../experiments/motion_type_investigation/#choose-a-motion-model)
for 5a. Raw and converted [measured trajectories](../../experiments/real_motion_traces/)
are included for 5b. No MRI files are needed.

## Generate

From the repository root, after preparing the synthetic trajectories:

```bash
python -m manuscript_figures.figure5.figure5a_simulated_trajectories
python -m manuscript_figures.figure5.figure5b_real_trajectory_conversion
```

## Outputs

- [5a: synthetic trajectories](figure5a_simulated_trajectories.svg).
- [5b: measured Trajectories 1 and 2](figure5b_real_trajectory_conversion.svg).
- Supporting pages: [Trajectories 1–4](supporting_material/real_trajectory_conversion_indices_1_4.svg) and [5–8](supporting_material/real_trajectory_conversion_indices_5_8.svg).

# Paper figures

[Repository home](https://github.com/zcahtwu/APHABAMAS_temp) · [Experiments](../experiments/) · [Setup](../docs/#setup)

The main results follow the two experiment phases.

[Figure 5](figure5/) documents the synthetic and tracking-data-derived motion trajectories used in all experiments.

## Phase 1: Demonstrate the need for assessment

| Figure | Question answered | Inputs |
| --- | --- | --- |
| [6: Brain comparisons](figure6/) | Do algorithms produce the same artifacts on brain data? | Saved metric tables for (a); local brain images for (b/c) and multiview SI |
| [7: Phantom comparisons](figure7/) | Does the phantom reproduce the disagreement seen on brain data? | Saved metric tables for (a); local phantom images for (b/c) and multiview SI |

## Phase 2: Evaluate simulation accuracy

| Figure | Question answered | Inputs |
| --- | --- | --- |
| [8: Ground-truth accuracy](figure8/) | Which algorithm agrees most closely with the analytical reference? | Saved phantom accuracy tables |
| [9: Image and signal errors](figure9/) | Where do simulations deviate from ground truth? | Local phantom images and signals |

## Generate a figure

Each guide lists its inputs, commands, and saved SVGs. Run commands from the
repository root; outputs are written beside the generators.

[Shared rendering code](shared/) provides styles and common layouts.
The [assessment scheme](../docs/assessment_scheme.png) is supplied separately
and displayed on the repository landing page.

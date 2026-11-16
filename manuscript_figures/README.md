# Paper figures

[Repository home](https://github.com/zcahtwu/APHABAMAS) · [Experiments](../experiments/) · [Setup](../docs/#setup)

The main results follow the two experiment phases. [Figure 7](figure7_motion_trajectories/) documents the measured and synthetic motion trajectories used in the experiments.

## Phase 1: Demonstrate the need for assessment

| Figure | Question answered | Inputs |
| --- | --- | --- |
| [8: Algorithm comparisons](figure8_algorithm_comparisons/) | Do algorithms produce the same artifacts on brain and phantom images? | Local simulated images for the main figure and multiplanar SI (plus phantom ground truth); saved pairwise metric tables for quantitative SI |

## Phase 2: Evaluate simulation accuracy

| Figure | Question answered | Inputs |
| --- | --- | --- |
| [9: Quantitative accuracy assessment](figure9_ground_truth_accuracy/) | Which algorithm agrees most closely with the analytical reference? | Saved phantom accuracy tables |
| [10: Visual accuracy assessment](figure10_image_signal_errors/) | Where do simulations deviate from ground truth? | Local phantom images and signals |

## Generate a figure

Each guide describes its inputs, commands, and outputs. Run commands from the repository root; figures are saved as SVG beside their generators, with supporting information (SI) in `Supporting_Information/`. Add `--add-pdf` to save matching PDFs. Generated PDFs are ignored by Git.

[Shared rendering code](shared/) provides styles and common layouts. The [assessment scheme](../docs/assessment_scheme.png) is supplied separately.

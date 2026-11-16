# Experiments

[Repository home](https://github.com/zcahtwu/APHABAMAS) · [Setup](../docs/#setup) · [Figures](../manuscript_figures/)

The experiments compare image-based, Type-1 NUFFT, and Type-2 NUFFT algorithms.

## Phase 1: Demonstrate the need for assessment

Compare algorithms with one another on brain and phantom images. Their outputs differ despite appearing visually plausible, showing why accuracy requires a ground-truth reference. Results appear in [Figure 8](../manuscript_figures/figure8_algorithm_comparisons/) and its supporting information for brain and phantom comparisons.

## Phase 2: Evaluate simulation accuracy

Compare phantom simulations with analytical ground truth. Image and signal errors reveal which algorithms are more accurate. Results appear in [Figure 9: Quantitative accuracy assessment](../manuscript_figures/figure9_ground_truth_accuracy/) and [Figure 10: Visual accuracy assessment](../manuscript_figures/figure10_image_signal_errors/).

## Code and inputs

Both phases use synthetic and measured motion; these folders organise the code by input type.

| Guide | Role in the study |
| --- | --- |
| [Simulation methods](utils/) | Generate the analytical reference and implement the three algorithms |
| [Synthetic motion](motion_type_investigation/) | Quantify agreement and accuracy across motion types and severities |
| [Tracking-data-derived motion](real_motion_traces/) | Inspect image and signal errors using eight recorded head-motion traces |

The study guides contain commands and input paths. Saved metrics are included, so analysis and metric plots can run without repeating the MRI simulations.

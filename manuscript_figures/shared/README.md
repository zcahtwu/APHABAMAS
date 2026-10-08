# Shared figure code

[Figure guide](../)

These modules provide consistent styling and layouts for the figure generators.

| Module | Used for |
| --- | --- |
| [style.py](style.py) | Fonts, colours, figure width, and selected measured subjects |
| [trajectories.py](trajectories.py) | Figure 5 trajectory loading and layout |
| [grouped_boxplots.py](grouped_boxplots.py), [metric_grid.py](metric_grid.py) | Common metric plots |
| [between_algorithm_boxplots.py](between_algorithm_boxplots.py) | Figures 6a and 7a |
| [inter_algorithm_visual_comparisons.py](inter_algorithm_visual_comparisons.py) | Figures 6b/c and 7b/c |
| [multiview_comparison.py](multiview_comparison.py) | Figure 6/7 multiview supporting information |

Run the figure-specific entry points. Changes here can affect multiple figures.

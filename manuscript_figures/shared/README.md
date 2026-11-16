# Shared figure code

[Figure guide](../)

These modules provide consistent styling and layouts for the figure generators.

| Module | Used for |
| --- | --- |
| [style.py](style.py) | Fonts, grey fills, figure width, and selected measured subjects |
| [trajectories.py](trajectories.py) | Figure 7 trajectory loading and layout |
| [grouped_boxplots.py](grouped_boxplots.py), [metric_grid.py](metric_grid.py) | Common boxplots, legends, and metric panels |
| [between_algorithm_boxplots.py](between_algorithm_boxplots.py) | Figure 8 pairwise-comparison SI |
| [multiview_comparison.py](multiview_comparison.py) | Figure 8 brain and phantom multiplanar SI |

Run the figure-specific entry points. Changes here can affect multiple figures.

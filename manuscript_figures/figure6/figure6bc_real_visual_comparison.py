"""Create the combined Figure 6b/c real-brain visual comparison.

Run from the repository root::

    python -m manuscript_figures.figure6.figure6bc_real_visual_comparison
"""

from pathlib import Path

from manuscript_figures.shared.inter_algorithm_visual_comparisons import (
    create_visual_comparison,
)


OUTPUT_PATH = (
    Path(__file__).resolve().parent / "figure6bc_real_visual_comparison.svg"
)


if __name__ == "__main__":
    create_visual_comparison(scan="real", output_path=OUTPUT_PATH)

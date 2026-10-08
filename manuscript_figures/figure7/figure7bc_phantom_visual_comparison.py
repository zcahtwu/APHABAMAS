"""Create the combined Figure 7b/c digital-phantom visual comparison.

Run from the repository root::

    python -m manuscript_figures.figure7.figure7bc_phantom_visual_comparison
"""

from pathlib import Path

from manuscript_figures.shared.inter_algorithm_visual_comparisons import (
    create_visual_comparison,
)


OUTPUT_PATH = (
    Path(__file__).resolve().parent / "figure7bc_phantom_visual_comparison.svg"
)


if __name__ == "__main__":
    create_visual_comparison(scan="phantom", output_path=OUTPUT_PATH)

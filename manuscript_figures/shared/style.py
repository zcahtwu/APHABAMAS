"""Small set of visual constants shared by the manuscript figures."""

from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_WIDTH = 180 / 25.4

SUBJECTS = (
    "BrainMRIMotionDB_2021-02-18_15_18_49447_Prospective-TracOline-Patient-5Y",
    "BrainMRIMotionDB_2021-02-26_13_13_45700_Prospective-TracOline-Patient-8Y",
)

FONT = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
}

# Light-to-dark algorithm palette.
GRAYS = ("#FFFFFF", "#B9B9B9", "#606060")

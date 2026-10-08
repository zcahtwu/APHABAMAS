"""Create the phantom three-view supporting-information figure.

Run: ``python -m manuscript_figures.figure7.figure7_phantom_multiview_SI``
"""

from pathlib import Path

from manuscript_figures.shared.multiview_comparison import create_multiview_figure
from manuscript_figures.shared.style import REPOSITORY_ROOT


OUTPUT_PATH = Path(__file__).resolve().parent / "figure7_phantom_multiview_SI.svg"
RESULTS = REPOSITORY_ROOT / "experiments/real_motion_traces/phantom_results"


if __name__ == "__main__":
    create_multiview_figure(
        OUTPUT_PATH, RESULTS,
        ("GT.nii.gz", "image_based.nii.gz", "type2.nii.gz", "type1_original.nii.gz"),
        ("Ground truth", "Image-based", "Type-2 NUFFT", "Type-1 NUFFT"),
        ((1, 0), (2, 0), (3, 0)),
        ("Image-based − GT", "Type-2 − GT", "Type-1 − GT"),
        axial_index=96,
    )

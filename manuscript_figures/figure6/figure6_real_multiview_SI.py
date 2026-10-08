"""Create the real-brain three-view supporting-information figure.

Run: ``python -m manuscript_figures.figure6.figure6_real_multiview_SI``
"""

from pathlib import Path

from manuscript_figures.shared.multiview_comparison import create_multiview_figure
from manuscript_figures.shared.style import REPOSITORY_ROOT


OUTPUT_PATH = Path(__file__).resolve().parent / "figure6_real_multiview_SI.svg"
RESULTS = REPOSITORY_ROOT / "experiments/real_motion_traces/real_scan_results"


if __name__ == "__main__":
    create_multiview_figure(
        OUTPUT_PATH, RESULTS,
        ("image_based.nii.gz", "type2.nii.gz", "type1_original.nii.gz"),
        ("Image-based", "Type-2 NUFFT", "Type-1 NUFFT"),
        ((1, 0), (2, 0), (2, 1)),
        ("Type-2 − Image-based", "Type-1 − Image-based", "Type-1 − Type-2"),
        axial_index=165,
    )

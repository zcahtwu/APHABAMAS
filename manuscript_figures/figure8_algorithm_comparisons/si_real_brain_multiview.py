"""Create Figure 8 SI: brain orthogonal views and pairwise differences.

Run: ``python -m manuscript_figures.figure8_algorithm_comparisons.si_real_brain_multiview``
"""

from pathlib import Path

from experiments.utils.figure_output import configure_figure_output
from manuscript_figures.shared.multiview_comparison import create_multiview_figure
from manuscript_figures.shared.style import REPOSITORY_ROOT


OUTPUT_PATH = (Path(__file__).resolve().parent / "Supporting_Information"
               / "real_brain_multiview.svg")
RESULTS = REPOSITORY_ROOT / "experiments/real_motion_traces/real_scan_results"


def create_figure(output_path=OUTPUT_PATH):
    return create_multiview_figure(
        output_path, RESULTS,
        ("image_based.nii.gz", "type2.nii.gz", "type1_original.nii.gz"),
        ("Image-based", "Type-2 NUFFT", "Type-1 NUFFT"),
        ((1, 0), (2, 0), (2, 1)),
        ("Type-2 − Image-based", "Type-1 − Image-based", "Type-1 − Type-2"),
        axial_index=165,
    )


if __name__ == "__main__":
    configure_figure_output()
    create_figure()

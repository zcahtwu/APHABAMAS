"""Create Figure 8 SI: phantom orthogonal views and ground-truth errors.

Run: ``python -m manuscript_figures.figure8_algorithm_comparisons.si_phantom_multiview``
"""

from pathlib import Path

from experiments.utils.figure_output import configure_figure_output
from manuscript_figures.shared.multiview_comparison import create_multiview_figure
from manuscript_figures.shared.style import REPOSITORY_ROOT


OUTPUT_PATH = (Path(__file__).resolve().parent / "Supporting_Information"
               / "phantom_multiview.svg")
RESULTS = REPOSITORY_ROOT / "experiments/real_motion_traces/phantom_results"


def create_figure(output_path=OUTPUT_PATH):
    return create_multiview_figure(
        output_path, RESULTS,
        ("GT.nii.gz", "image_based.nii.gz", "type2.nii.gz", "type1_original.nii.gz"),
        ("Ground truth", "Image-based", "Type-2 NUFFT", "Type-1 NUFFT"),
        ((1, 0), (2, 0), (3, 0)),
        ("Image-based − GT", "Type-2 − GT", "Type-1 − GT"),
        axial_index=96,
    )


if __name__ == "__main__":
    configure_figure_output()
    create_figure()

"""Create separate brain and phantom quantitative supporting figures."""

from pathlib import Path

from experiments.utils.figure_output import configure_figure_output
from manuscript_figures.shared.between_algorithm_boxplots import create_figure


OUTPUT_DIRECTORY = Path(__file__).resolve().parent / "Supporting_Information"


def generate_figures():
    return [
        create_figure(
            scan=scan,
            output_path=OUTPUT_DIRECTORY / f"{label}_quantitative_comparisons.svg",
            show_samples=False,
        )
        for scan, label in (("real_brain", "real_brain"), ("phantom", "phantom"))
    ]


if __name__ == "__main__":
    configure_figure_output()
    generate_figures()

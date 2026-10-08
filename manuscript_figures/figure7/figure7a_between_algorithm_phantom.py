"""Create Figure 7a from the digital-phantom between-algorithm metrics.

Run from the repository root after generating the shared analysis CSV::

    python -m manuscript_figures.figure7.figure7a_between_algorithm_phantom
"""

from pathlib import Path

from manuscript_figures.shared.between_algorithm_boxplots import create_figure


OUTPUT_PATH = (
    Path(__file__).resolve().parent / "figure7a_between_algorithm_phantom.svg"
)
SI_OUTPUT_PATH = OUTPUT_PATH.with_name(f"{OUTPUT_PATH.stem}_SI{OUTPUT_PATH.suffix}")


if __name__ == "__main__":
    create_figure(
        scan="phantom",
        output_path=OUTPUT_PATH,
        panel_label="(a)",
        show_samples=False,
    )
    create_figure(
        scan="phantom",
        output_path=SI_OUTPUT_PATH,
        panel_label="(a)",
        show_samples=True,
    )

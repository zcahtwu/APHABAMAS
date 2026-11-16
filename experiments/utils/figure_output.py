"""Consistent SVG/PDF export for manuscript and experiment figures."""

import argparse
from pathlib import Path


_save_pdf = False


def configure_figure_output(argv=None):
    """Read the common figure CLI options; export SVG by default."""
    parser = argparse.ArgumentParser(description="Generate SVG figures with optional PDFs.")
    parser.add_argument(
        "--add-pdf", action="store_true",
        help="Also save a matching PDF for each SVG figure.",
    )
    options = parser.parse_args(argv)
    global _save_pdf
    _save_pdf = options.add_pdf


def save_figure(figure, output_path, *, save_pdf=None, **kwargs):
    """Save SVG and optionally PDF with identical rendering options.

    ``save_pdf`` overrides the CLI setting when supplied. ``output_path``
    determines the directory and stem; each format gets its own suffix.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path.with_suffix(".svg"), **kwargs)
    pdf_enabled = _save_pdf if save_pdf is None else save_pdf
    if pdf_enabled:
        figure.savefig(output_path.with_suffix(".pdf"), **kwargs)

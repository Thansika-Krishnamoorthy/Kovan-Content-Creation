"""Command-line interface shared by the Kovan template renderers."""

from __future__ import annotations

import argparse
from pathlib import Path

from .core import ROOT, RenderError, render_file


def run(forced_template: str | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render Markdown into a Kovan blog HTML template.")
    parser.add_argument("files", nargs="+", type=Path, help="Markdown files under content/")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "output" / "website",
        help="Base directory for generated HTML",
    )
    parser.add_argument("--download-remote-images", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    failed = False
    for source in args.files:
        source = source if source.is_absolute() else ROOT / source
        try:
            source.resolve().relative_to((ROOT / "content").resolve())
            output = render_file(
                source,
                args.output_dir,
                forced_template=forced_template,
                download_remote_images=args.download_remote_images,
                overwrite=args.overwrite,
            )
            try:
                output_display = output.relative_to(ROOT)
            except ValueError:
                output_display = output
            print(f"Rendered {source.relative_to(ROOT)} -> {output_display}")
        except (RenderError, ValueError) as error:
            failed = True
            print(f"ERROR: {source}: {error}")
    return 1 if failed else 0

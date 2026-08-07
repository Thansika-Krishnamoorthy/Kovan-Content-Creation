"""Command-line interface shared by the Kovan template renderers."""

from __future__ import annotations

import argparse
from pathlib import Path

from .core import ROOT, RenderError, load_manifest, render_file, render_file_with_manifest, save_manifest


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
    parser.add_argument(
        "--branch",
        help="Source branch to read the Markdown and images from "
        "(e.g. blog-md-intake). Defaults to the current worktree.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Track Markdown source hashes and stable HTML outputs in this JSON file.",
    )
    args = parser.parse_args()

    manifest_path = args.manifest.resolve() if args.manifest else None
    manifest = load_manifest(manifest_path) if manifest_path else None
    failed = False
    for source in args.files:
        source = source if source.is_absolute() else ROOT / source
        try:
            source.resolve().relative_to((ROOT / "content").resolve())
            if manifest is not None:
                output, status = render_file_with_manifest(
                    source,
                    args.output_dir,
                    manifest,
                    forced_template=forced_template,
                    download_remote_images=args.download_remote_images,
                    source_branch=args.branch,
                )
            else:
                output = render_file(
                    source,
                    args.output_dir,
                    forced_template=forced_template,
                    download_remote_images=args.download_remote_images,
                    overwrite=args.overwrite,
                    source_branch=args.branch,
                )
                status = "rendered"
            try:
                output_display = output.relative_to(ROOT) if output else "(unchanged)"
            except ValueError:
                output_display = output
            print(f"{status.title()} {source.relative_to(ROOT)} -> {output_display}")
        except (RenderError, ValueError) as error:
            failed = True
            print(f"ERROR: {source}: {error}")
    if manifest_path and manifest is not None and not failed:
        save_manifest(manifest_path, manifest)
    return 1 if failed else 0

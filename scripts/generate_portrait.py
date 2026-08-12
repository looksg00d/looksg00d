"""Entry point: turn a photo into a typing-animation ASCII portrait SVG.

Standalone tool, not part of the nightly workflow — a portrait is generated
once from a photo you choose and committed as a static asset, not
regenerated on a schedule like the stats graphics.

Usage:
    python scripts/generate_portrait.py --input path/to/photo.jpg --login <you>

Requires (dev-time only, not needed by generate_stats.py or CI):
    pip install pillow numpy opencv-python-headless rembg onnxruntime

First run downloads a ~176MB background-removal model to ~/.u2net/,
cached after that.

Read this before choosing a photo (from the pipeline's own limits):
  - side light at roughly 45 degrees, not flat frontal light
  - tight crop, chin to just above the hair
  - 1200px+ source resolution — small photos lose glasses frames, brow
    lines, anything thin, on the downscale
  - plain background, and avoid dark clothing against a dark wall
  - a slight angle rather than dead-on, for a shadow edge on the nose/jaw

Only use a photo you have the rights to publish — the output SVG gets
committed to a public repository.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from portrait_data import build_char_grid, load_image
from render_portrait import build_portrait_svg

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", required=True, help="path to the source photo")
    parser.add_argument("--login", required=True, help="GitHub username, used in the SVG's accessible title")
    parser.add_argument("--cols", type=int, default=90, help="character columns (default: 90)")
    parser.add_argument("--no-bg-removal", action="store_true", help="skip rembg (photo already on a plain background)")
    parser.add_argument("--out-prefix", default="portrait", help="output filename prefix (default: portrait)")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"error: no such file: {input_path}", file=sys.stderr)
        return 1

    print(f"loading {input_path}...")
    image = load_image(str(input_path))

    print(f"processing ({image.size[0]}x{image.size[1]} -> {args.cols} columns)...")
    if not args.no_bg_removal:
        print("  removing background (first run downloads a model, ~176MB)...")
    grid = build_char_grid(image, cols=args.cols, remove_background=not args.no_bg_removal)
    print(f"  grid: {grid.cols} cols x {len(grid.rows)} rows")

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    for theme in ("light", "dark"):
        svg = build_portrait_svg(grid, theme, args.login)
        out_path = ASSETS_DIR / f"{args.out_prefix}-{theme}.svg"
        out_path.write_text(svg, encoding="utf-8", newline="\n")
        print(f"  wrote {out_path.relative_to(ASSETS_DIR.parent)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

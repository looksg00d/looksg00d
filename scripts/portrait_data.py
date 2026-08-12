"""Photo → character grid. Implements the pipeline from the ASCII Portrait
README Guide (burly-handstand-0dc.notion.site/ASCII-Portrait-README-Guide),
with one deviation from its defaults — see DARKEN_GAMMA below.

Stage order and why each one is there:
  1. rembg cut-out    background forced to white, which maps to the blank
                       end of the ramp. Skip it and the background fills
                       with dense glyphs and drowns the portrait.
  2. bilateral filter  smooths skin while keeping edges (unlike a plain
                       gaussian blur, which would also soften the edges the
                       ramp needs to render as contrast).
  3. CLAHE             local (tiled) contrast instead of global autocontrast
                       — a flatly-lit face stays one tone under global
                       autocontrast; CLAHE pulls local shadow detail out.
  4. darkening curve   the fix on top of the guide's defaults. Their linear
                       mapping renders a washed-out, featureless face; an
                       exponential curve pushes midtones down so glasses,
                       brows and lips survive the trip to 13 brightness
                       levels.
  5. map to ramp       ' .`:-=+*cs#%@' — darkest character last.
"""
from __future__ import annotations

import io
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image

from svg_kit import RAMP

# (v/255)^DARKEN_GAMMA. >1 pushes midtones toward black before they're
# quantized to the ramp — see module docstring. 1.7 is the article's fix;
# lower values wash out, much higher ones crush shadow detail to solid @.
DARKEN_GAMMA = 1.7

CLAHE_CLIP_LIMIT = 3.0
CLAHE_TILE_GRID = (8, 8)
BILATERAL_D = 9
BILATERAL_SIGMA_COLOR = 75
BILATERAL_SIGMA_SPACE = 75

# Monospace characters run about twice as tall as wide, so a column grid
# needs its row count scaled down from a naive aspect-ratio fit.
ROW_ASPECT_CORRECTION = 0.48


@dataclass(frozen=True)
class CharGrid:
    rows: list[str]  # each string is `cols` characters wide
    cols: int


def _remove_background(image: Image.Image) -> Image.Image:
    from rembg import remove  # deferred: heavy import (onnxruntime + model)

    cutout = remove(image)  # RGBA, transparent background
    canvas = Image.new("RGB", cutout.size, (255, 255, 255))
    canvas.paste(cutout, mask=cutout.split()[3])
    return canvas


def _to_gray_array(image: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)


def _apply_bilateral(gray: np.ndarray) -> np.ndarray:
    return cv2.bilateralFilter(gray, BILATERAL_D, BILATERAL_SIGMA_COLOR, BILATERAL_SIGMA_SPACE)


def _apply_clahe(gray: np.ndarray) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_TILE_GRID)
    return clahe.apply(gray)


def _apply_darkening_curve(gray: np.ndarray) -> np.ndarray:
    normalized = gray.astype(np.float64) / 255.0
    curved = np.power(normalized, DARKEN_GAMMA)
    return (curved * 255.0).astype(np.uint8)


def _resize_to_grid(gray: np.ndarray, cols: int) -> np.ndarray:
    h, w = gray.shape
    rows = max(1, round(cols * (h / w) * ROW_ASPECT_CORRECTION))
    return cv2.resize(gray, (cols, rows), interpolation=cv2.INTER_AREA)


def _to_ramp_text(gray: np.ndarray) -> list[str]:
    # Darkest pixel (0) -> densest glyph (last); brightest (255) -> blank.
    indices = ((255 - gray.astype(np.int32)) * (len(RAMP) - 1) / 255).round().astype(int)
    indices = np.clip(indices, 0, len(RAMP) - 1)
    return ["".join(RAMP[i] for i in row) for row in indices]


def load_image(path: str) -> Image.Image:
    with open(path, "rb") as f:
        data = f.read()
    return Image.open(io.BytesIO(data)).convert("RGB")


def build_char_grid(image: Image.Image, cols: int = 90, remove_background: bool = True) -> CharGrid:
    """Runs the full pipeline and returns a `cols`-wide character grid.

    Set `remove_background=False` to skip rembg (faster iteration, or for
    photos already shot on a clean plain background).
    """
    if cols < 10:
        raise ValueError(f"cols must be at least 10, got {cols}")

    working = _remove_background(image) if remove_background else image

    gray = _to_gray_array(working)
    gray = _apply_bilateral(gray)
    gray = _apply_clahe(gray)
    gray = _apply_darkening_curve(gray)
    gray = _resize_to_grid(gray, cols)

    rows = _to_ramp_text(gray)
    return CharGrid(rows=rows, cols=cols)

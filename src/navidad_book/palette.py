"""Colour palettes.

The default "bw" palette uses K-only CMYK greys, which is what a KDP
black & white interior prints best. "color" is available for a premium
colour interior.
"""
from dataclasses import dataclass

from reportlab.lib.colors import CMYKColor, Color


def gray(k: float) -> CMYKColor:
    """K-only grey: k=0 is white, k=1 is full black."""
    return CMYKColor(0, 0, 0, k)


@dataclass(frozen=True)
class Palette:
    ink: Color          # outlines of drawings, text
    paper: Color        # fill of colourable shapes
    guide: Color        # dotted tracing guides
    example: Color      # solid "watch me" example lines
    start: Color        # start dot
    soft: Color         # background snow, subtle decoration
    accent: Color       # small accents (stars, arrows)


BW = Palette(
    ink=gray(1.0),
    paper=gray(0.0),
    guide=gray(0.55),
    example=gray(0.75),
    start=gray(0.85),
    soft=gray(0.10),
    accent=gray(0.70),
)

COLOR = Palette(
    ink=CMYKColor(0, 0, 0, 1),
    paper=CMYKColor(0, 0, 0, 0),
    guide=CMYKColor(0.55, 0.25, 0, 0.1),
    example=CMYKColor(0.85, 0.2, 0.9, 0.1),
    start=CMYKColor(0.8, 0, 0.9, 0),
    soft=CMYKColor(0.10, 0.02, 0, 0),
    accent=CMYKColor(0, 0.95, 0.85, 0),
)


def get_palette(mode: str) -> Palette:
    try:
        return {"bw": BW, "color": COLOR}[mode]
    except KeyError:
        raise ValueError(f"Unknown colour mode {mode!r} (use 'bw' or 'color')")

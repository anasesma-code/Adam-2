"""Colour palettes.

"color" (default) is a full-colour interior: illustrations, guides and page
decoration are painted, while the drawings meant to be coloured in by the
child stay as black line art (see Palette.line_art).

"bw" uses K-only CMYK greys, which is what a cheaper KDP black & white
interior prints best.
"""
import dataclasses
from dataclasses import dataclass, field

from reportlab.lib.colors import CMYKColor, Color


def gray(k: float) -> CMYKColor:
    """K-only grey: k=0 is white, k=1 is full black."""
    return CMYKColor(0, 0, 0, k)


@dataclass(frozen=True)
class Palette:
    ink: Color          # outlines of drawings, body text
    paper: Color        # fill of colourable shapes
    guide: Color        # dotted tracing guides
    example: Color      # solid "watch me" example lines
    start: Color        # start dot
    soft: Color         # background snow, subtle decoration
    accent: Color       # small accents (arrows, hints, dashed boxes)
    title: Color = None             # page titles (defaults to ink)
    maze: Color = None              # maze walls (defaults to ink)
    fills: dict = field(default_factory=dict)   # semantic fills for figures
    decorate: bool = False          # print the coloured top garland

    def line_art(self):
        """Same palette without fills: figures print as colour-me outlines."""
        return dataclasses.replace(self, fills={})


BW = Palette(
    ink=gray(1.0),
    paper=gray(0.0),
    guide=gray(0.55),
    example=gray(0.75),
    start=gray(0.85),
    soft=gray(0.10),
    accent=gray(0.70),
)

FILLS = {
    "red": CMYKColor(0, 0.88, 0.80, 0),
    "brick": CMYKColor(0.1, 0.75, 0.75, 0.15),
    "green": CMYKColor(0.78, 0, 0.85, 0.12),
    "gold": CMYKColor(0, 0.22, 0.92, 0),
    "orange": CMYKColor(0, 0.55, 0.95, 0),
    "brown": CMYKColor(0.25, 0.60, 0.85, 0.30),
    "tan": CMYKColor(0.08, 0.28, 0.50, 0),
    "cookie": CMYKColor(0.05, 0.42, 0.75, 0.05),
    "cream": CMYKColor(0, 0.05, 0.22, 0),
    "blue": CMYKColor(0.80, 0.35, 0, 0),
    "navy": CMYKColor(0.85, 0.65, 0.20, 0.35),
    "ice": CMYKColor(0.60, 0.15, 0, 0),
    "ice_light": CMYKColor(0.18, 0.03, 0, 0),
    "snow": CMYKColor(0.05, 0.01, 0, 0),
    "dark": CMYKColor(0.6, 0.5, 0.4, 0.75),
}

COLOR = Palette(
    ink=gray(1.0),
    paper=CMYKColor(0, 0, 0, 0),
    guide=CMYKColor(0.70, 0.30, 0, 0),
    example=CMYKColor(0.78, 0, 0.85, 0.12),
    start=CMYKColor(0.78, 0, 0.85, 0.12),
    soft=CMYKColor(0.14, 0.03, 0, 0),
    accent=CMYKColor(0, 0.88, 0.80, 0),
    title=CMYKColor(0, 0.90, 0.85, 0.08),
    maze=CMYKColor(0.85, 0.45, 0, 0.10),
    fills=FILLS,
    decorate=True,
)


def get_palette(mode: str) -> Palette:
    try:
        return {"bw": BW, "color": COLOR}[mode]
    except KeyError:
        raise ValueError(f"Unknown colour mode {mode!r} (use 'bw' or 'color')")

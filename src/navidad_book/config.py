"""Book geometry and KDP print specifications.

All measurements are in PostScript points (1 in = 72 pt).

KDP paperback with bleed:
  * page size = trim + 0.125" in width and + 0.25" in height
    (bleed is added to the top, bottom and *outside* edge only; the spine
    edge never has bleed).
  * minimum outside/top/bottom margin with bleed: 0.375"
  * minimum inside (gutter) margin for 24-150 pages: 0.375"
We use more generous safe margins so nothing gets close to the trim.
"""
from dataclasses import dataclass, field

INCH = 72.0


@dataclass(frozen=True)
class BookConfig:
    trim_w: float = 8.5 * INCH
    trim_h: float = 11.0 * INCH
    bleed: float = 0.125 * INCH
    use_bleed: bool = True

    # Safe-area margins, measured from the trim edge.
    margin_outside: float = 0.5 * INCH
    margin_inside: float = 0.625 * INCH
    margin_top: float = 0.5 * INCH
    margin_bottom: float = 0.5 * INCH

    total_pages: int = 40
    color_mode: str = "bw"  # "bw" (cheaper KDP interior) or "color"
    seed: int = 2026

    title: str = "Mi Libro de Navidad"
    subtitle: str = "de Trazos y Actividades"
    author: str = ""
    language: str = "es"
    keywords: tuple = field(default=("preescritura", "trazos", "navidad", "3-5 años"))

    # ------------------------------------------------------------------ #
    @property
    def bleed_pts(self) -> float:
        return self.bleed if self.use_bleed else 0.0

    @property
    def page_w(self) -> float:
        return self.trim_w + self.bleed_pts

    @property
    def page_h(self) -> float:
        return self.trim_h + 2 * self.bleed_pts

    @staticmethod
    def is_recto(page_num: int) -> bool:
        """Page 1 is a right-hand (recto) page; odd pages are rectos."""
        return page_num % 2 == 1

    def trim_origin(self, page_num: int) -> tuple:
        """Bottom-left corner of the trim box, in page coordinates.

        Rectos have their outside edge on the right, so the bleed is on the
        right and the trim starts at x=0. Versos have bleed on the left.
        """
        b = self.bleed_pts
        ox = 0.0 if self.is_recto(page_num) else b
        return ox, b

    def safe_rect(self, page_num: int) -> tuple:
        """Safe area (x0, y0, x1, y1) in trim coordinates."""
        if self.is_recto(page_num):
            left, right = self.margin_inside, self.margin_outside
        else:
            left, right = self.margin_outside, self.margin_inside
        return (left, self.margin_bottom,
                self.trim_w - right, self.trim_h - self.margin_top)

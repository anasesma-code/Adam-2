"""Font registration.

KDP rejects PDFs with non-embedded fonts, so we only use TrueType files,
which ReportLab always embeds (subset). Drop a child-friendly font such as
Andika (single-storey "a") into assets/fonts/ and point FONT_FILES at it to
change the look of the book.
"""
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"
SYSTEM_DIR = Path("/usr/share/fonts/truetype/dejavu")

REGULAR = "BookRegular"
BOLD = "BookBold"

FONT_FILES = {
    REGULAR: "DejaVuSans.ttf",
    BOLD: "DejaVuSans-Bold.ttf",
}

_registered = False


def register_fonts() -> None:
    global _registered
    if _registered:
        return
    for name, filename in FONT_FILES.items():
        for folder in (FONT_DIR, SYSTEM_DIR):
            path = folder / filename
            if path.exists():
                pdfmetrics.registerFont(TTFont(name, str(path)))
                break
        else:
            raise FileNotFoundError(
                f"Font {filename!r} not found in {FONT_DIR} or {SYSTEM_DIR}")
    _registered = True

"""Assemble the 40-page book."""
from pathlib import Path

from reportlab.pdfgen import canvas

from .config import BookConfig
from .fonts import REGULAR, register_fonts
from .layout import PageContext
from .pages import coloring, dots, ending, front, mazes, tracing
from .palette import get_palette

SECTIONS = [
    ("Inicio", front.PAGES),            # 1-3
    ("Trazos", tracing.PAGES),          # 4-20
    ("Une los puntos", dots.PAGES),     # 21-28
    ("Laberintos", mazes.PAGES),        # 29-35
    ("Colorear", coloring.PAGES),       # 36-38
    ("Final", ending.PAGES),            # 39-40
]


def page_plan():
    return [(section, fn) for section, fns in SECTIONS for fn in fns]


class LayoutError(RuntimeError):
    pass


def build(out_path, cfg: BookConfig = BookConfig(), strict=True):
    """Render the book. Returns (page_plan, list_of_layout_issues)."""
    register_fonts()
    plan = page_plan()
    if len(plan) != cfg.total_pages:
        raise LayoutError(f"Page plan has {len(plan)} pages, "
                          f"expected {cfg.total_pages}")
    pal = get_palette(cfg.color_mode)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # initialFontName avoids ReportLab's default (non-embedded) Helvetica,
    # which KDP would reject.
    c = canvas.Canvas(str(out_path), pagesize=(cfg.page_w, cfg.page_h),
                      pageCompression=1, initialFontName=REGULAR)
    c.setTitle(f"{cfg.title} {cfg.subtitle}")
    c.setAuthor(cfg.author)
    c.setSubject("Libro de actividades de preescritura navideño (3-5 años)")
    c.setKeywords(", ".join(cfg.keywords))
    c.setCreator("navidad_book")

    issues = []
    for num, (section, fn) in enumerate(plan, start=1):
        ox, oy = cfg.trim_origin(num)
        trim = (ox, oy, ox + cfg.trim_w, oy + cfg.trim_h)
        c.setTrimBox(trim)
        c.setArtBox(trim)
        c.setBleedBox((0, 0, cfg.page_w, cfg.page_h))
        c.saveState()
        c.translate(ox, oy)
        ctx = PageContext(c, cfg, num, pal)
        fn(ctx)
        c.restoreState()
        issues.extend(ctx.validate())
        c.showPage()
    c.save()
    if strict and issues:
        raise LayoutError("Layout problems:\n  " + "\n  ".join(issues))
    return plan, issues

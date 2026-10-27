"""Page context: coordinate system, text helpers and layout validation.

Every page is drawn in *trim coordinates*: (0, 0) is the bottom-left corner
of the trimmed page, regardless of which side the bleed is on.

Everything that is drawn registers a bounding box. After drawing, validate()
checks that:
  * all text and artwork stay inside the KDP safe area,
  * text never overlaps other text or artwork,
  * page chrome (header/footer items) never overlaps page content,
  * bleed backgrounds really reach the bleed edge.
"""
from dataclasses import dataclass

from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase.pdfmetrics import getAscentDescent, stringWidth

from .config import BookConfig
from .fonts import BOLD, REGULAR
from .palette import Palette

EPS = 0.01


@dataclass
class Rect:
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def w(self):
        return self.x1 - self.x0

    @property
    def h(self):
        return self.y1 - self.y0

    @property
    def cx(self):
        return (self.x0 + self.x1) / 2

    @property
    def cy(self):
        return (self.y0 + self.y1) / 2

    def inset(self, dx, dy=None):
        dy = dx if dy is None else dy
        return Rect(self.x0 + dx, self.y0 + dy, self.x1 - dx, self.y1 - dy)

    def intersects(self, o, tol=EPS):
        return (self.x0 < o.x1 - tol and o.x0 < self.x1 - tol and
                self.y0 < o.y1 - tol and o.y0 < self.y1 - tol)

    def contains(self, o, tol=EPS):
        return (o.x0 >= self.x0 - tol and o.y0 >= self.y0 - tol and
                o.x1 <= self.x1 + tol and o.y1 <= self.y1 + tol)


@dataclass
class Box(Rect):
    kind: str = "art"      # text | art | chrome | background
    group: str = ""
    label: str = ""


class PageContext:
    def __init__(self, canvas, cfg: BookConfig, page_num: int, pal: Palette):
        self.c = canvas
        self.cfg = cfg
        self.page_num = page_num
        self.pal = pal
        self.boxes: list = []
        self.ox, self.oy = cfg.trim_origin(page_num)
        self.safe = Rect(*cfg.safe_rect(page_num))
        self.trim = Rect(0, 0, cfg.trim_w, cfg.trim_h)
        b = cfg.bleed_pts
        # Full page (including bleed) in trim coordinates.
        self.page = Rect(-self.ox, -b, cfg.page_w - self.ox, cfg.trim_h + b)
        self.content = self.safe
        self.recto = cfg.is_recto(page_num)
        self._group_counter = 0

    # ------------------------------------------------------------ boxes
    def register(self, x0, y0, x1, y1, kind="art", group="", label=""):
        box = Box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1),
                  kind=kind, group=group, label=label)
        self.boxes.append(box)
        return box

    def new_group(self, prefix="g"):
        self._group_counter += 1
        return f"{prefix}{self._group_counter}"

    def art(self, fn, cx, cy, size, kind="art", group="", label="", **kw):
        """Draw a graphics.* figure and register its bounding box."""
        fn(self.c, cx, cy, size, self.pal, **kw)
        h = size / 2
        return self.register(cx - h, cy - h, cx + h, cy + h, kind=kind,
                             group=group, label=label or fn.__name__)

    # ------------------------------------------------------------- text
    @staticmethod
    def font_name(bold):
        return BOLD if bold else REGULAR

    def text_width(self, text, size, bold=False):
        return stringWidth(text, self.font_name(bold), size)

    def text(self, text, x, y, size, bold=False, align="center", color=None,
             kind="text", group="", label=""):
        """Draw one line of text with its baseline at y. Returns its Box."""
        font = self.font_name(bold)
        w = stringWidth(text, font, size)
        asc, desc = getAscentDescent(font, size)
        x0 = {"left": x, "center": x - w / 2, "right": x - w}[align]
        self.c.setFillColor(color or self.pal.ink)
        self.c.setFont(font, size)
        self.c.drawString(x0, y, text)
        return self.register(x0, y + desc, x0 + w, y + asc, kind=kind,
                             group=group, label=label or text[:30])

    def fit_size(self, text, max_w, size, bold=False, min_size=8):
        while size > min_size and self.text_width(text, size, bold) > max_w:
            size -= 0.5
        return size

    def text_fit(self, text, x, y, max_w, size, bold=False, align="center",
                 min_size=8, **kw):
        size = self.fit_size(text, max_w, size, bold, min_size)
        return self.text(text, x, y, size, bold=bold, align=align, **kw)

    def line_height(self, size, bold=False, leading=1.25):
        asc, desc = getAscentDescent(self.font_name(bold), size)
        return (asc - desc) * leading

    def paragraph(self, text, x, top, width, size, bold=False, align="left",
                  leading=1.3, **kw):
        """Wrap text into width, first line's ascent touching `top`.

        Returns the y coordinate just below the last line.
        """
        font = self.font_name(bold)
        asc, desc = getAscentDescent(font, size)
        lines = simpleSplit(text, font, size, width)
        step = (asc - desc) * leading
        y = top - asc
        ax = {"left": x, "center": x + width / 2, "right": x + width}[align]
        for line in lines:
            self.text(line, ax, y, size, bold=bold, align=align, **kw)
            y -= step
        return y + step + desc

    # ------------------------------------------------------- validation
    def validate(self):
        issues = []
        p = self.page_num
        for b in self.boxes:
            if b.kind == "background":
                continue
            if not self.safe.contains(b):
                issues.append(f"p{p}: {b.kind} '{b.label}' outside safe area "
                              f"({b.x0:.1f},{b.y0:.1f},{b.x1:.1f},{b.y1:.1f})")
        bg = [b for b in self.boxes if b.kind == "background"]
        for b in bg:
            if b.label.startswith("bleed") and not (
                    b.x0 <= self.page.x0 + EPS and b.x1 >= self.page.x1 - EPS):
                issues.append(f"p{p}: bleed background '{b.label}' does not "
                              f"reach the bleed edge")
        fg = [b for b in self.boxes if b.kind != "background"]
        for i, a in enumerate(fg):
            for b in fg[i + 1:]:
                if a.group and a.group == b.group:
                    continue
                kinds = {a.kind, b.kind}
                clash = ("text" in kinds) or kinds == {"chrome", "art"}
                if clash and a.intersects(b):
                    issues.append(f"p{p}: overlap {a.kind} '{a.label}' <-> "
                                  f"{b.kind} '{b.label}'")
        return issues

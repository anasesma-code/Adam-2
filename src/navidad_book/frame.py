"""Common page chrome: snowy ground in the bleed, header, footer, reward."""
import math

from .config import INCH
from .layout import Rect

TITLE_SIZE = 25
INSTR_SIZE = 14
REWARD_SIZE = 76
FOOTER_GAP = 14
HEADER_GAP = 14


def snow_ground(ctx, height=0.78 * INCH, waves=3):
    """Soft snowy hills printed to the bleed edge along the bottom."""
    c, pg = ctx.c, ctx.page
    c.saveState()
    c.setFillColor(ctx.pal.soft)
    p = c.beginPath()
    p.moveTo(pg.x0, pg.y0)
    n = 60
    for i in range(n + 1):
        x = pg.x0 + pg.w * i / n
        phase = 0.0 if ctx.recto else math.pi / 2
        y = height - 10 + 10 * math.sin(waves * 2 * math.pi * i / n + phase)
        p.lineTo(x, y)
    p.lineTo(pg.x1, pg.y0)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()
    ctx.register(pg.x0, pg.y0, pg.x1, height, kind="background",
                 label="bleed-snow")


def page_number(ctx):
    c, s = ctx.c, ctx.safe
    r = 13
    cx, cy = s.cx, s.y0 + r + 1
    g = ctx.new_group("pn")
    c.saveState()
    c.setFillColor(ctx.pal.paper)
    c.setStrokeColor(ctx.pal.ink)
    c.setLineWidth(1.2)
    c.circle(cx, cy, r, stroke=1, fill=1)
    c.restoreState()
    ctx.register(cx - r, cy - r, cx + r, cy + r, kind="chrome", group=g,
                 label="page-number")
    ctx.text(str(ctx.page_num), cx, cy - 4.2, 12, bold=True, group=g)


def reward(ctx, icon, label="¡Colorea!"):
    """Small colouring reward in the outside bottom corner."""
    c, s = ctx.c, ctx.safe
    size = REWARD_SIZE
    x0 = s.x1 - size if ctx.recto else s.x0
    y0 = s.y0
    g = ctx.new_group("rw")
    c.saveState()
    c.setFillColor(ctx.pal.paper)
    c.setStrokeColor(ctx.pal.accent)
    c.setLineWidth(1.5)
    c.setDash([4, 3])
    c.roundRect(x0, y0, size, size, 10, stroke=1, fill=1)
    c.restoreState()
    ctx.register(x0, y0, x0 + size, y0 + size, kind="chrome", group=g,
                 label="reward-box")
    ctx.art(icon, x0 + size / 2, y0 + size / 2 + 7, size * 0.62,
            kind="chrome", group=g, label="reward-icon")
    ctx.text(label, x0 + size / 2, y0 + 6, 9, bold=True, group=g)
    return Rect(x0, y0, x0 + size, y0 + size)


def header(ctx, title, instruction=""):
    s = ctx.safe
    asc = TITLE_SIZE * 0.93
    y = s.y1 - asc
    box = ctx.text_fit(title, s.cx, y, s.w, TITLE_SIZE, bold=True,
                       kind="text", label="title")
    bottom = box.y0
    if instruction:
        bottom = ctx.paragraph(instruction, s.x0 + 20, bottom - 6, s.w - 40,
                               INSTR_SIZE, align="center")
    return bottom


def activity_frame(ctx, title, instruction, icon, number=True):
    """Draw page chrome and set ctx.content to the free area."""
    snow_ground(ctx)
    top = header(ctx, title, instruction)
    reward(ctx, icon)
    if number:
        page_number(ctx)
    s = ctx.safe
    ctx.content = Rect(s.x0, s.y0 + REWARD_SIZE + FOOTER_GAP, s.x1,
                       top - HEADER_GAP)
    return ctx.content

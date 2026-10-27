"""Closing pages: maze solutions and the reward diploma."""
from .. import graphics as g
from ..frame import activity_frame, decorate, page_number
from ..layout import Rect
from ..maze import generate
from .mazes import MAZES, draw_maze, draw_solution, maze_seed


def solutions_page(ctx):
    activity_frame(ctx, "Soluciones de los laberintos",
                   "Para los mayores: aquí está el camino de cada laberinto.",
                   g.snowflake)
    area = ctx.content
    cols = 3
    rows = (len(MAZES) + cols - 1) // cols
    cw, rh = area.w / cols, area.h / rows
    for i, (mc, mr, *_rest) in enumerate(MAZES):
        col, row = i % cols, i // cols
        cell = Rect(area.x0 + col * cw, area.y1 - (row + 1) * rh,
                    area.x0 + (col + 1) * cw, area.y1 - row * rh)
        grp = ctx.new_group("sol")
        label = ctx.text(f"Laberinto {i + 1}", cell.cx, cell.y1 - 14, 12,
                         bold=True, group=grp)
        avail = Rect(cell.x0 + 14, cell.y0 + 16, cell.x1 - 14, label.y0 - 14)
        cs = min(avail.w / mc, avail.h / (mr + 0.8))  # room for path ends
        x0 = avail.cx - mc * cs / 2
        y_top = avail.cy + mr * cs / 2
        m = generate(mc, mr, maze_seed(ctx.cfg, i))
        draw_maze(ctx.c, m, x0, y_top, cs, 1.8, ctx.pal.ink)
        draw_solution(ctx.c, m, x0, y_top, cs, 3.0,
                      ctx.pal.accent if ctx.pal.fills else ctx.pal.guide)
        ctx.register(x0 - 1, y_top - mr * cs - cs * 0.4 - 2, x0 + mc * cs + 1,
                     y_top + cs * 0.4 + 2, group=grp, label=f"solution{i + 1}")


def diploma_page(ctx):
    s = ctx.safe
    decorate(ctx)
    page_number(ctx)
    c = ctx.c
    frame = Rect(s.x0 + 4, s.y0 + 40, s.x1 - 4, s.y1 - 4)
    c.saveState()
    c.setStrokeColor(ctx.pal.ink)
    c.setFillColor(ctx.pal.paper)
    c.setLineWidth(3)
    c.roundRect(frame.x0, frame.y0, frame.w, frame.h, 22, stroke=1, fill=1)
    c.setLineWidth(1.2)
    c.setDash([5, 4])
    inner = frame.inset(10)
    c.roundRect(inner.x0, inner.y0, inner.w, inner.h, 16, stroke=1, fill=0)
    c.restoreState()
    ctx.register(frame.x0 - 1.5, frame.y0 - 1.5, frame.x1 + 1.5, frame.y1 + 1.5,
                 kind="chrome", group="diploma", label="diploma-frame")

    grp = "diploma"
    corner = 62
    for cx, cy in ((inner.x0 + corner / 2 + 8, inner.y1 - corner / 2 - 8),
                   (inner.x1 - corner / 2 - 8, inner.y1 - corner / 2 - 8)):
        ctx.art(g.holly, cx, cy, corner, group=grp)
    y = inner.y1 - 60
    t = ctx.text("¡DIPLOMA!", inner.cx, y, 46, bold=True, group=grp,
                 color=ctx.pal.title)
    t = ctx.text_fit("Pequeño gran artista de Navidad", inner.cx, t.y0 - 34,
                     inner.w - 40, 24, bold=True, group=grp)
    t = ctx.text("Este diploma es para:", inner.cx, t.y0 - 40, 17, group=grp)
    line_y = t.y0 - 52
    c.saveState()
    c.setStrokeColor(ctx.pal.ink)
    c.setLineWidth(2)
    c.line(inner.x0 + 50, line_y, inner.x1 - 50, line_y)
    c.restoreState()
    ctx.register(inner.x0 + 50, line_y - 1, inner.x1 - 50, line_y + 1,
                 group=grp, label="diploma-name")
    bottom = ctx.paragraph(
        "por repasar líneas, unir puntos, resolver laberintos y colorear "
        "con mucha alegría todo su libro de Navidad.",
        inner.x0 + 50, line_y - 28, inner.w - 100, 15, align="center",
        group=grp)

    medal = min(bottom - inner.y0 - 80, 190)
    ctx.art(g.star, inner.cx, bottom - 20 - medal / 2, medal, group=grp)
    for dx in (-1, 1):
        ctx.art(g.gift, inner.cx + dx * (medal / 2 + 60), bottom - 20 - medal * 0.6,
                70, group=grp)
    fy = inner.y0 + 22
    ctx.text("Fecha: ____________________", inner.cx, fy, 14, group=grp)


PAGES = [solutions_page, diploma_page]

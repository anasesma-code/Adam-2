"""Simple mazes for small children, growing from 3x3 to 6x7 cells."""
from .. import graphics as g
from ..frame import activity_frame
from ..maze import generate

WALL_LW = 5.0

# (cols, rows, start icon, end icon, title, instruction, reward)
MAZES = [
    (3, 3, g.reindeer, g.sleigh, "Laberinto del reno",
     "Ayuda al reno a llegar a su trineo.", g.star),
    (4, 4, g.gingerbread, g.house, "La galleta vuelve a casa",
     "Busca el camino hasta la casita.", g.gingerbread),
    (4, 5, g.penguin, g.igloo, "El pingüino y su iglú",
     "¿Por dónde llega el pingüino a su iglú?", g.penguin),
    (5, 5, g.snowman, g.mitten, "El guante perdido",
     "El muñeco de nieve busca su guante.", g.snowman),
    (5, 6, g.star, g.tree, "La estrella del árbol",
     "Lleva la estrella hasta la punta del árbol.", g.tree),
    (6, 6, g.santa_hat, g.stocking, "Regalos en el calcetín",
     "Encuentra el camino hasta el calcetín.", g.stocking),
    (6, 7, g.sleigh, g.gift, "El gran viaje del trineo",
     "¡El último laberinto! Lleva el trineo hasta el regalo.", g.gift),
]


def maze_seed(cfg, index):
    return cfg.seed * 100 + index


def layout(area, cols, rows, icon_max=72):
    """Cell size and grid origin leaving room for icons above and below."""
    for icon in range(int(icon_max), 30, -2):
        cs = min(area.w / cols, (area.h - 2 * icon - 8) / rows)
        if cs >= icon * 0.8 or icon <= 32:
            break
    gw, gh = cols * cs, rows * cs
    x0 = area.cx - gw / 2
    y_top = area.cy + gh / 2
    return cs, x0, y_top, icon


def draw_maze(c, m, x0, y_top, cs, lw, ink):
    """Draw walls. Entrance: top of cell (0,0). Exit: bottom of last cell."""
    c.saveState()
    c.setStrokeColor(ink)
    c.setLineWidth(lw)
    c.setLineCap(1)
    c.setLineJoin(1)
    cols, rows = m.cols, m.rows
    X = lambda col: x0 + col * cs
    Y = lambda row: y_top - row * cs
    # outer border with gaps
    c.line(X(1), Y(0), X(cols), Y(0))
    c.line(X(0), Y(rows), X(cols - 1), Y(rows))
    c.line(X(0), Y(0), X(0), Y(rows))
    c.line(X(cols), Y(0), X(cols), Y(rows))
    for (col, row), opened in m.open.items():
        if col + 1 < cols and (col + 1, row) not in opened:
            c.line(X(col + 1), Y(row), X(col + 1), Y(row + 1))
        if row + 1 < rows and (col, row + 1) not in opened:
            c.line(X(col), Y(row + 1), X(col + 1), Y(row + 1))
    c.restoreState()


def draw_solution(c, m, x0, y_top, cs, lw, colour):
    path = m.solve((0, 0), (m.cols - 1, m.rows - 1))
    pts = [(x0 + (col + 0.5) * cs, y_top - (row + 0.5) * cs) for col, row in path]
    pts = [(pts[0][0], y_top + cs * 0.4)] + pts + [(pts[-1][0], y_top - m.rows * cs - cs * 0.4)]
    c.saveState()
    c.setStrokeColor(colour)
    c.setLineWidth(lw)
    c.setLineCap(1)
    c.setLineJoin(1)
    p = c.beginPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    c.drawPath(p, stroke=1, fill=0)
    c.restoreState()


def maze_page(ctx, index):
    cols, rows, start, end, title, instr, reward = MAZES[index]
    activity_frame(ctx, title, instr, reward)
    area = ctx.content
    m = generate(cols, rows, maze_seed(ctx.cfg, index))
    cs, x0, y_top, icon = layout(area, cols, rows)
    draw_maze(ctx.c, m, x0, y_top, cs, WALL_LW, ctx.pal.ink)
    pad = WALL_LW / 2
    ctx.register(x0 - pad, y_top - rows * cs - pad, x0 + cols * cs + pad,
                 y_top + pad, label="maze")
    ctx.art(start, x0 + cs / 2, y_top + 4 + icon / 2, icon, label="maze-start")
    ctx.art(end, x0 + (cols - 0.5) * cs, y_top - rows * cs - 4 - icon / 2,
            icon, label="maze-end")


def make_pages():
    pages = []
    for i in range(len(MAZES)):
        def page(ctx, i=i):
            maze_page(ctx, i)
        page.__name__ = f"maze_{i + 1}"
        pages.append(page)
    return pages


PAGES = make_pages()

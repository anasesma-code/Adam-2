"""Progressive tracing (pre-writing) exercises.

Order of difficulty, as recommended for 3-5 year olds:
horizontal -> vertical -> diagonal -> curves/waves -> zigzag -> loops ->
spirals -> circles -> shapes -> whole pictures.
"""
import dataclasses
import math

from .. import graphics as g
from ..draw import GUIDE_LW, guide, set_dotted, start_dot
from ..frame import activity_frame

SAMPLES = 240


# ------------------------------------------------------------ path shapes
def straight(x0, x1, y, amp):
    return [(x0, y), (x1, y)]


def wave(humps):
    def fn(x0, x1, y, amp):
        return [(x0 + (x1 - x0) * t / SAMPLES,
                 y + amp * math.sin(math.pi * humps * t / SAMPLES))
                for t in range(SAMPLES + 1)]
    return fn


def arches(humps):
    def fn(x0, x1, y, amp):
        base = y - amp * 0.5
        return [(x0 + (x1 - x0) * t / SAMPLES,
                 base + 1.6 * amp * abs(math.sin(math.pi * humps * t / SAMPLES)))
                for t in range(SAMPLES + 1)]
    return fn


def zigzag(teeth):
    def fn(x0, x1, y, amp):
        n = 2 * teeth
        return [(x0 + (x1 - x0) * i / n, y + (amp if i % 2 else -amp))
                for i in range(n + 1)]
    return fn


def loops(x0, x1, y, amp):
    """Cursive-style loops ("eee"), loops on top."""
    length = x1 - x0
    k = 3 if length / amp > 6 else 2
    c1 = length / (2 * math.pi * k)
    d = min(amp, 1.7 * c1)
    pts = []
    n = SAMPLES * 2
    for i in range(n + 1):
        t = 2 * math.pi * k * i / n
        pts.append((x0 + c1 * t + d * math.sin(t), y - d * math.cos(t)))
    return pts


# ---------------------------------------------------------------- layouts
def rows_exercise(ctx, n_rows, path_fn, left_icon, right_icon, amp_ratio=0.30,
                  example=True):
    area = ctx.content
    row_h = area.h / n_rows
    icon = min(row_h * 0.78, 74)
    gap = 12
    for i in range(n_rows):
        cy = area.y1 - row_h * (i + 0.5)
        ctx.art(left_icon, area.x0 + icon / 2, cy, icon)
        ctx.art(right_icon, area.x1 - icon / 2, cy, icon)
        x0 = area.x0 + icon + gap + 14
        x1 = area.x1 - icon - gap
        amp = row_h * amp_ratio
        pts = path_fn(x0, x1, cy, amp)
        guide(ctx, pts, example=example and i == 0)
        start_dot(ctx, *pts[0], direction=_direction(pts))


def columns_exercise(ctx, n_cols, top_icon, bottom_icon, path_fn=straight,
                     amp_ratio=0.25):
    area = ctx.content
    col_w = area.w / n_cols
    icon = min(col_w * 0.78, 70)
    gap = 12
    for i in range(n_cols):
        cx = area.x0 + col_w * (i + 0.5)
        ctx.art(top_icon, cx, area.y1 - icon / 2, icon)
        ctx.art(bottom_icon, cx, area.y0 + icon / 2, icon)
        y0 = area.y1 - icon - gap - 14
        y1 = area.y0 + icon + gap
        # reuse the horizontal path shapes rotated by 90 degrees
        pts = [(cx + offset, y)
               for y, offset in path_fn(y0, y1, 0, col_w * amp_ratio)]
        guide(ctx, pts, example=(i == 0))
        start_dot(ctx, *pts[0], direction=_direction(pts))


def _direction(pts):
    (x0, y0), (x1, y1) = pts[0], pts[min(len(pts) - 1, 6)]
    return (x1 - x0, y1 - y0)


def traced(pal):
    """Palette whose 'ink' is the guide colour (for trace-the-picture)."""
    return dataclasses.replace(pal.line_art(), ink=pal.guide)


def trace_figure(ctx, fn, cx, cy, size, **kw):
    c = ctx.c
    c.saveState()
    set_dotted(c, ctx.pal)
    fn(c, cx, cy, size, traced(ctx.pal), lw=GUIDE_LW, **kw)
    c.restoreState()
    h = size / 2
    return ctx.register(cx - h, cy - h, cx + h, cy + h, label=fn.__name__)


# ------------------------------------------------------------------ pages
def reindeer_to_sleigh(ctx):
    activity_frame(ctx, "Lleva al reno hasta el trineo",
                   "Repasa las líneas de izquierda a derecha. "
                   "Empieza en el punto.", g.star)
    rows_exercise(ctx, 5, straight, g.reindeer, g.sleigh)


def gifts_to_houses(ctx):
    activity_frame(ctx, "Reparte los regalos",
                   "Lleva cada regalo hasta su casita.", g.gift)
    rows_exercise(ctx, 6, straight, g.gift, g.house)


def falling_snow(ctx):
    activity_frame(ctx, "¡Cae la nieve!",
                   "Repasa las líneas de arriba hacia abajo.", g.snowflake)
    columns_exercise(ctx, 6, g.cloud, g.snowflake)


def stars_to_trees(ctx):
    activity_frame(ctx, "Una estrella para cada árbol",
                   "Baja cada estrella hasta la punta de su arbolito.", g.tree)
    columns_exercise(ctx, 5, g.star, lambda c, x, y, s, p, **k:
                     g.tree(c, x, y, s, p, topper=False, **k))


def hang_ornaments(ctx):
    activity_frame(ctx, "Cuelga los adornos",
                   "Lleva cada bola hasta su ganchito en el árbol.",
                   g.ornament)
    area = ctx.content
    ts = min(area.h, area.w * 0.68)
    tcx, tcy = area.x1 - ts / 2, area.cy
    ctx.art(g.tree, tcx, tcy, ts, ornaments=False)
    targets = [(0.02, 0.32), (0.22, 0.05), (-0.20, -0.08), (0.40, -0.42),
               (-0.36, -0.48)]
    targets = sorted(((tcx + x * ts / 2, tcy + y * ts / 2 * 0.95)
                      for x, y in targets), key=lambda p: -p[1])
    n = len(targets)
    col_top = tcy + ts / 2 * 0.40
    col_h = col_top - area.y0
    osz = min(col_h / n * 0.85, 62)
    step = (col_h - osz) / (n - 1)
    c = ctx.c
    for i, (tx, ty) in enumerate(targets):
        ox, oy = area.x0 + osz / 2, col_top - osz / 2 - i * step
        ctx.art(g.ornament, ox, oy, osz)
        sx = ox + osz / 2 + 10
        pts = [(sx, oy), (tx - 8, ty)]
        guide(ctx, pts, example=(i == 0))
        start_dot(ctx, sx, oy, direction=(tx - sx, ty - oy), arrow=False)
        c.saveState()
        c.setStrokeColor(ctx.pal.ink)
        c.setFillColor(ctx.pal.paper)
        c.setLineWidth(1.5)
        c.circle(tx, ty, 6, stroke=1, fill=1)
        c.restoreState()


def shooting_stars(ctx):
    activity_frame(ctx, "Estrellas fugaces",
                   "Repasa las líneas inclinadas, siempre de arriba abajo.",
                   g.moon)
    area = ctx.content
    rows, per_row = 4, 5
    row_h = area.h / rows
    sp = area.w / per_row
    star = 24
    for r in range(rows):
        top = area.y1 - r * row_h - star - 4
        bottom = area.y1 - (r + 1) * row_h + 22
        down_right = r % 2 == 0
        for k in range(per_row):
            xa = area.x0 + sp * k + sp * 0.28
            xb = area.x0 + sp * k + sp * 0.78
            sx, ex = (xa, xb) if down_right else (xb, xa)
            ctx.art(g.star, sx, top + star / 2 + 2, star)
            guide(ctx, [(sx, top), (ex, bottom)], example=(k == 0))
            start_dot(ctx, sx, top, arrow=False, r=5.5)


def hopping_penguin(ctx):
    activity_frame(ctx, "El pingüino saltarín",
                   "Ayuda al pingüino a saltar hasta su iglú.", g.penguin)
    rows_exercise(ctx, 4, arches(3), g.penguin, g.igloo, amp_ratio=0.28)


def snowy_hills(ctx):
    activity_frame(ctx, "Por las colinas nevadas",
                   "Sigue las olas con el trineo, sin levantar el lápiz.",
                   g.sleigh)
    rows_exercise(ctx, 4, wave(4), g.sleigh, g.house, amp_ratio=0.24)


def gingerbread_zigzag(ctx):
    activity_frame(ctx, "La galleta corre en zigzag",
                   "Repasa los picos para que la galleta llegue a casa.",
                   g.gingerbread)
    area_rows = 4
    area = ctx.content
    row_h = area.h / area_rows
    icon = min(row_h * 0.78, 74)
    for i, teeth in enumerate((3, 4, 5, 6)):
        cy = area.y1 - row_h * (i + 0.5)
        ctx.art(g.gingerbread, area.x0 + icon / 2, cy, icon)
        ctx.art(g.house, area.x1 - icon / 2, cy, icon)
        pts = zigzag(teeth)(area.x0 + icon + 26, area.x1 - icon - 12, cy,
                            row_h * 0.26)
        guide(ctx, pts, example=(i == 0))
        start_dot(ctx, *pts[0], direction=_direction(pts))


def snowy_mountains(ctx):
    activity_frame(ctx, "Montañas nevadas",
                   "Sube y baja las montañas hasta llegar a la estrella.",
                   g.mitten)
    rows_exercise(ctx, 4, zigzag(3), g.reindeer, g.star, amp_ratio=0.34)


def chimney_smoke(ctx):
    activity_frame(ctx, "El humo de la chimenea",
                   "Haz bucles como el humo que sale de la casita.", g.house)
    rows_exercise(ctx, 4, loops, g.house, g.cloud, amp_ratio=0.30)


def snow_swirls(ctx):
    activity_frame(ctx, "Remolinos de nieve",
                   "Empieza en el centro y gira hacia afuera.", g.snowman)
    area = ctx.content
    cols, rows = 3, 2
    cw, rh = area.w / cols, area.h / rows
    for r in range(rows):
        for k in range(cols):
            cx = area.x0 + cw * (k + 0.5)
            cy = area.y1 - rh * (r + 0.5)
            rmax = min(cw, rh) * 0.40
            turns = 3
            n = 360
            pts = []
            for i in range(n + 1):
                th = 2 * math.pi * turns * i / n
                rad = rmax * i / n
                pts.append((cx + rad * math.cos(th), cy + rad * math.sin(th)))
            guide(ctx, pts, example=(r == 0 and k == 0))
            start_dot(ctx, cx, cy, arrow=False, r=5.5)


def circle_pts(cx, cy, r, start=90, ccw=True, n=120):
    sgn = 1 if ccw else -1
    return [(cx + r * math.cos(math.radians(start + sgn * 360 * i / n)),
             cy + r * math.sin(math.radians(start + sgn * 360 * i / n)))
            for i in range(n + 1)]


def snowballs(ctx):
    activity_frame(ctx, "Bolas de nieve",
                   "Repasa los círculos empezando por arriba.", g.snowman)
    area = ctx.content
    cols, rows = 3, 3
    cw, rh = area.w / cols, area.h / rows
    sizes = [0.42, 0.36, 0.30]
    for r in range(rows):
        for k in range(cols):
            cx = area.x0 + cw * (k + 0.5)
            cy = area.y1 - rh * (r + 0.5)
            rad = min(cw, rh) * sizes[r]
            pts = circle_pts(cx, cy, rad)
            guide(ctx, pts, example=(r == 0 and k == 0))
            start_dot(ctx, cx, cy + rad, direction=(-1, 0))


def christmas_shapes(ctx):
    activity_frame(ctx, "Formas de Navidad",
                   "Triángulo como el árbol, cuadrado como el regalo "
                   "y círculo como la bola.", g.gift)
    area = ctx.content
    rows = 3
    rh = area.h / rows
    icon = min(rh * 0.7, 72)
    size = min(rh * 0.72, 92)
    free = area.w - icon - 20
    for r, (fn, shape) in enumerate(((g.tree, "triangle"), (g.gift, "square"),
                                     (g.ornament, "circle"))):
        cy = area.y1 - rh * (r + 0.5)
        ctx.art(fn, area.x0 + icon / 2, cy, icon)
        for k in range(3):
            cx = area.x0 + icon + 20 + free * (k + 0.5) / 3
            h = size / 2
            if shape == "triangle":
                pts = [(cx, cy + h), (cx - h, cy - h * 0.85),
                       (cx + h, cy - h * 0.85), (cx, cy + h)]
            elif shape == "square":
                q = h * 0.85
                pts = [(cx - q, cy + q), (cx + q, cy + q), (cx + q, cy - q),
                       (cx - q, cy - q), (cx - q, cy + q)]
            else:
                pts = circle_pts(cx, cy, h * 0.9)
            guide(ctx, pts, example=(k == 0))
            start_dot(ctx, *pts[0], direction=_direction(pts), arrow=False)


def trace_tree(ctx):
    activity_frame(ctx, "Repasa el árbol de Navidad",
                   "Sigue los puntitos y después decóralo con muchos colores.",
                   g.star)
    area = ctx.content
    size = min(area.w, area.h)
    trace_figure(ctx, g.tree, area.cx, area.cy, size, ornaments=False)


def trace_star(ctx):
    activity_frame(ctx, "Repasa las estrellas",
                   "Sigue los puntitos de la estrella grande y las pequeñas.",
                   g.moon)
    area = ctx.content
    big = min(area.w * 0.62, area.h * 0.78)
    trace_figure(ctx, g.star, area.cx, area.y1 - big / 2, big)
    small = min(area.h - big - 10, area.w / 4 - 10, 110)
    for k in range(3):
        cx = area.x0 + area.w * (k + 0.5) / 3
        trace_figure(ctx, g.star, cx, area.y0 + small / 2, small)


def trace_pictures(ctx):
    activity_frame(ctx, "Repasa y colorea",
                   "Un gorro, un regalo, una campana y un calcetín.",
                   g.candy_cane)
    area = ctx.content
    cw, rh = area.w / 2, area.h / 2
    size = min(cw, rh) * 0.88
    for i, fn in enumerate((g.santa_hat, g.gift, g.bell, g.stocking)):
        cx = area.x0 + cw * (i % 2 + 0.5)
        cy = area.y1 - rh * (i // 2 + 0.5)
        trace_figure(ctx, fn, cx, cy, size)


PAGES = [reindeer_to_sleigh, gifts_to_houses, falling_snow, stars_to_trees,
         hang_ornaments, shooting_stars, hopping_penguin, snowy_hills,
         gingerbread_zigzag, snowy_mountains, chimney_smoke, snow_swirls,
         snowballs, christmas_shapes, trace_tree, trace_star, trace_pictures]

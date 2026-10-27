"""Connect-the-dots pages with simple Christmas shapes (8-12 dots)."""
import math
from dataclasses import dataclass, field

from .. import graphics as g
from ..frame import activity_frame
from ..layout import Rect

LABEL_SIZE = 17
DOT_R = 4.5


@dataclass
class DotShape:
    name: str
    points: list                       # closed polygon, unit coordinates
    deco: object = None                # fn(u) drawing solid details
    deco_boxes: list = field(default_factory=list)  # unit bboxes of deco
    icon: object = g.star


def _gift_deco(u):
    for sx in (-1, 1):
        u.draw(u.path().m(0, 0.45)
               .cv(sx * 0.15, 0.95, sx * 0.62, 0.90, sx * 0.52, 0.58)
               .cv(sx * 0.45, 0.45, sx * 0.20, 0.45, 0, 0.45).close())
    u.line([(-0.12, -0.80), (-0.12, 0.30)])
    u.line([(0.12, -0.80), (0.12, 0.30)])


def _tree_deco(u):
    u.rect(-0.14, -0.98, 0.28, 0.24)
    with g._Unit(u.c, u.X(0), u.Y(0.99), u.s * 0.26, u.pal, u.lw) as s:
        s.poly(g.star_points())


def _hat_deco(u):
    u.rect(-0.88, -0.70, 1.76, 0.36, r=0.17)
    u.circle(0.70, 0.42, 0.17)


def _bell_deco(u):
    u.circle(0, -0.76, 0.12)
    u.draw(u.path().arc(0, 0.80, 0.12, -50, 280, move=True), fill=False)


def _ornament_deco(u):
    u.draw(u.path().arc(0, 0.82, 0.10, -60, 300, move=True), fill=False)
    u.rect(-0.16, 0.56, 0.32, 0.18, r=0.04)


def _stocking_deco(u):
    u.rect(-0.52, 0.52, 0.84, 0.36, r=0.12)


def _house_deco(u):
    u.rect(-0.18, -0.90, 0.36, 0.56, r=0.08)
    u.rect(-0.56, -0.45, 0.26, 0.26)
    u.rect(0.30, -0.45, 0.26, 0.26)


def _circle(cx, cy, r, n, start=90):
    return [(cx + r * math.cos(math.radians(start - 360 * i / n)),
             cy + r * math.sin(math.radians(start - 360 * i / n)))
            for i in range(n)]


SHAPES = {
    "regalo": DotShape("regalo", [(-0.75, -0.90), (0.75, -0.90), (0.75, 0.15),
                                  (0.86, 0.15), (0.86, 0.45), (-0.86, 0.45),
                                  (-0.86, 0.15), (-0.75, 0.15)],
                       _gift_deco, [(-0.65, 0.42, 0.65, 0.84)], g.gift),
    "estrella": DotShape("estrella", g.star_points(), icon=g.star),
    "gorro": DotShape("gorro de Papá Noel",
                      [(-0.67, -0.26), (-0.63, 0.02), (-0.47, 0.38),
                       (-0.16, 0.62), (0.20, 0.68), (0.52, 0.60),
                       (0.55, 0.30), (0.56, 0.02), (0.63, -0.18),
                       (0.69, -0.26)],
                      _hat_deco, [(-0.90, -0.72, 0.90, -0.32),
                                  (0.51, 0.23, 0.89, 0.61)], g.santa_hat),
    "campana": DotShape("campana",
                        [(-0.82, -0.62), (-0.62, -0.42), (-0.58, 0.0),
                         (-0.50, 0.42), (-0.22, 0.66), (0.22, 0.66),
                         (0.50, 0.42), (0.58, 0.0), (0.62, -0.42),
                         (0.82, -0.62)],
                        _bell_deco, [(-0.14, -0.90, 0.14, -0.62),
                                     (-0.13, 0.66, 0.13, 0.94)], g.bell),
    "arbolito": DotShape("arbolito", g.tree_points(), _tree_deco,
                         [(-0.16, -1.0, 0.16, -0.70),
                          (-0.14, 0.85, 0.14, 1.12)], g.tree),
    "casita": DotShape("casita",
                       [(-0.70, -0.90), (0.70, -0.90), (0.70, 0.08),
                        (0.88, 0.08), (0.52, 0.375), (0.52, 0.75),
                        (0.30, 0.75), (0.30, 0.555), (0.0, 0.80),
                        (-0.88, 0.08), (-0.70, 0.08)],
                       _house_deco, [(-0.58, -0.92, 0.58, -0.17)], g.house),
    "bola": DotShape("bola de Navidad", _circle(0, -0.16, 0.74, 12),
                     _ornament_deco, [(-0.18, 0.54, 0.18, 0.94)], g.ornament),
    "calcetín": DotShape("calcetín",
                         [(-0.40, 0.52), (-0.40, -0.10), (-0.40, -0.55),
                          (-0.25, -0.85), (0.05, -0.92), (0.45, -0.92),
                          (0.75, -0.75), (0.68, -0.48), (0.45, -0.40),
                          (0.20, -0.40), (0.20, 0.05), (0.20, 0.52)],
                         _stocking_deco, [(-0.54, 0.50, 0.34, 0.90)],
                         g.stocking),
}

ORDER = ["regalo", "estrella", "gorro", "campana", "arbolito", "casita",
         "bola", "calcetín"]


# ------------------------------------------------------------- geometry
def _seg_hits_rect(a, b, r, steps=24):
    for i in range(steps + 1):
        t = i / steps
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        if r.x0 <= x <= r.x1 and r.y0 <= y <= r.y1:
            return True
    return False


def _outward_normal(pts, i):
    """Bisector of the outward edge normals at vertex i."""
    n = len(pts)
    area = sum(pts[k][0] * pts[(k + 1) % n][1] - pts[(k + 1) % n][0] * pts[k][1]
               for k in range(n))
    sign = 1 if area > 0 else -1   # CCW: outward normal is (ey, -ex)
    nx = ny = 0.0
    for a, b in ((pts[i - 1], pts[i]), (pts[i], pts[(i + 1) % n])):
        ex, ey = b[0] - a[0], b[1] - a[1]
        length = math.hypot(ex, ey) or 1
        nx += ey / length * sign
        ny += -ex / length * sign
    length = math.hypot(nx, ny)
    if length < 1e-6:
        return 0.0, 1.0
    return nx / length, ny / length


def place_labels(ctx, pts, obstacles, bounds):
    """Choose a non-colliding position for each number label."""
    placed = []
    segs = [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
    for i, (x, y) in enumerate(pts):
        txt = str(i + 1)
        w = ctx.text_width(txt, LABEL_SIZE, bold=True)
        h = LABEL_SIZE * 0.75
        nx, ny = _outward_normal(pts, i)
        base = math.atan2(ny, nx)
        best = None
        candidates = [(d, k) for k in (0, 6, 14)
                      for d in (0, 25, -25, 50, -50, 75, -75, 105, -105, 140,
                                -140, 180)]
        for delta, extra in candidates:
            a = base + math.radians(delta)
            dx, dy = math.cos(a), math.sin(a)
            dist = DOT_R + 5 + extra + abs(dx) * w / 2 + abs(dy) * h / 2
            cx, cy = x + dx * dist, y + dy * dist
            r = Rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
            pad = r.inset(-3)
            if not bounds.contains(r):
                continue
            if any(pad.intersects(o) for o in obstacles + placed):
                continue
            if any(_seg_hits_rect(a_, b_, pad) for a_, b_ in segs):
                continue
            best = r
            break
        if best is None:
            raise RuntimeError(f"Could not place label {txt} on p{ctx.page_num}")
        placed.append(best)
    return placed


# ----------------------------------------------------------------- page
def dot_page(ctx, key, hint=False):
    shape = SHAPES[key]
    n = len(shape.points)
    activity_frame(ctx, f"Une los puntos: {shape.name}",
                   f"Une los números del 1 al {n} y vuelve al 1. "
                   "¡Después coloréalo!", shape.icon)
    area = ctx.content
    margin = 34
    size = min(area.w, area.h) - 2 * margin
    cx, cy = area.cx, area.cy
    s = size / 2
    pts = [(cx + x * s, cy + y * s) for x, y in shape.points]
    group = ctx.new_group("dots")
    c = ctx.c

    obstacles = [Rect(cx + x0 * s, cy + y0 * s, cx + x1 * s, cy + y1 * s)
                 for x0, y0, x1, y1 in shape.deco_boxes]
    if shape.deco:
        with g._Unit(c, cx, cy, size, ctx.line_pal) as u:
            shape.deco(u)
        for o in obstacles:
            ctx.register(o.x0, o.y0, o.x1, o.y1, group=group, label="deco")

    if hint:
        c.saveState()
        c.setStrokeColor(ctx.pal.guide if ctx.pal.fills else ctx.pal.example)
        c.setLineWidth(1)
        c.setDash([2, 5])
        p = c.beginPath()
        p.moveTo(*pts[0])
        for pt in pts[1:]:
            p.lineTo(*pt)
        p.close()
        c.drawPath(p, stroke=1, fill=0)
        c.restoreState()

    dot_boxes = [Rect(x - DOT_R - 2, y - DOT_R - 2, x + DOT_R + 2, y + DOT_R + 2)
                 for x, y in pts]
    labels = place_labels(ctx, pts, obstacles + dot_boxes, area)

    c.saveState()
    c.setFillColor(ctx.pal.ink)
    c.setStrokeColor(ctx.pal.ink)
    for i, (x, y) in enumerate(pts):
        if i == 0:
            c.setLineWidth(1.5)
            c.setStrokeColor(ctx.pal.start)
            c.setFillColor(ctx.pal.paper)
            c.circle(x, y, DOT_R + 3.5, stroke=1, fill=1)
            c.setFillColor(ctx.pal.ink)
        c.circle(x, y, DOT_R, stroke=0, fill=1)
        ctx.register(x - DOT_R, y - DOT_R, x + DOT_R, y + DOT_R, group=group,
                     label=f"dot{i + 1}")
    c.restoreState()
    for i, r in enumerate(labels):
        ctx.text(str(i + 1), r.cx, r.y0 + 0.5, LABEL_SIZE, bold=True,
                 group=group, label=f"n{i + 1}")


def make_pages():
    pages = []
    for i, key in enumerate(ORDER):
        def page(ctx, key=key, hint=i < 2):
            dot_page(ctx, key, hint=hint)
        page.__name__ = f"dots_{key}"
        pages.append(page)
    return pages


PAGES = make_pages()

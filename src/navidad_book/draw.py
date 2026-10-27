"""Drawing primitives for pre-writing exercises."""
import math

GUIDE_LW = 4.5      # dotted tracing line weight (pt)
EXAMPLE_LW = 3.5    # solid example line weight (pt)


def bbox(pts, pad=0.0):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad


def set_dotted(c, pal, lw=GUIDE_LW):
    """Round dots: zero-length dashes with round caps."""
    c.setStrokeColor(pal.guide)
    c.setLineWidth(lw)
    c.setLineCap(1)
    c.setLineJoin(1)
    c.setDash([0.01, lw * 2.3])


def polyline(c, pts, close=False):
    p = c.beginPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    if close:
        p.close()
    c.drawPath(p, stroke=1, fill=0)


def guide(ctx, pts, example=False, close=False, group="", label="guide"):
    """Dotted tracing path (or solid example path) through `pts`."""
    c = ctx.c
    c.saveState()
    if example:
        c.setStrokeColor(ctx.pal.example)
        c.setLineWidth(EXAMPLE_LW)
        c.setLineCap(1)
        c.setLineJoin(1)
        lw = EXAMPLE_LW
    else:
        set_dotted(c, ctx.pal)
        lw = GUIDE_LW
    polyline(c, pts, close)
    c.restoreState()
    return ctx.register(*bbox(pts, lw / 2), kind="art", group=group, label=label)


def start_dot(ctx, x, y, direction=(1, 0), r=6.5, arrow=True, group=""):
    """Start marker: a filled dot plus a small arrow showing the direction."""
    c = ctx.c
    c.saveState()
    c.setFillColor(ctx.pal.start)
    c.setStrokeColor(ctx.pal.start)
    c.circle(x, y, r, stroke=0, fill=1)
    ctx.register(x - r, y - r, x + r, y + r, group=group, label="start")
    if arrow:
        dx, dy = direction
        n = math.hypot(dx, dy) or 1
        dx, dy = dx / n, dy / n
        nx, ny = -dy, dx                     # left-hand normal
        off, length = r + 9, 18
        ax, ay = x + nx * off, y + ny * off
        bx, by = ax + dx * length, ay + dy * length
        c.setLineWidth(2)
        c.setLineCap(1)
        c.line(ax, ay, bx, by)
        h = 6
        p = c.beginPath()
        p.moveTo(bx + dx * 2, by + dy * 2)
        p.lineTo(bx - dx * h + nx * h * 0.6, by - dy * h + ny * h * 0.6)
        p.lineTo(bx - dx * h - nx * h * 0.6, by - dy * h - ny * h * 0.6)
        p.close()
        c.drawPath(p, stroke=0, fill=1)
        ctx.register(*bbox([(ax, ay), (bx + dx * 2, by + dy * 2)], 4),
                     group=group, label="arrow")
    c.restoreState()

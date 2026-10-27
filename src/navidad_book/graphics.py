"""Vector line-art library of simple Christmas figures.

Every figure has the signature

    figure(canvas, cx, cy, size, pal, lw=None, fill=True)

and draws itself inside the size x size square centred on (cx, cy). Shapes
are outlined in `pal.ink`. Each part names a semantic colour ("red",
"gold", "snow"...): palettes with `fills` paint it, palettes without them
fill it with `pal.paper` (white), giving a ready-to-colour line drawing.
Shapes overlap cleanly either way. With fill=False only outlines
are drawn, which combined with a dash pattern set by the caller turns any
simple figure into a "trace me" drawing.

Figures are designed in a unit square [-1, 1] x [-1, 1] (y up).
All output is pure vector paths, so it stays sharp at any print resolution.
"""
import math


def default_lw(size):
    return max(1.2, min(4.0, size * 0.028))


class _Path:
    def __init__(self, u):
        self.u = u
        self.p = u.c.beginPath()

    def m(self, x, y):
        self.p.moveTo(self.u.X(x), self.u.Y(y))
        return self

    def l(self, x, y):
        self.p.lineTo(self.u.X(x), self.u.Y(y))
        return self

    def cv(self, x1, y1, x2, y2, x3, y3):
        u = self.u
        self.p.curveTo(u.X(x1), u.Y(y1), u.X(x2), u.Y(y2), u.X(x3), u.Y(y3))
        return self

    def arc(self, cx, cy, r, start, extent, move=False):
        u = self.u
        args = (u.X(cx - r), u.Y(cy - r), u.X(cx + r), u.Y(cy + r), start, extent)
        (self.p.arc if move else self.p.arcTo)(*args)
        return self

    def poly(self, pts, close=True):
        self.m(*pts[0])
        for pt in pts[1:]:
            self.l(*pt)
        if close:
            self.close()
        return self

    def close(self):
        self.p.close()
        return self


class _Unit:
    """Maps unit-square coordinates to the page and keeps drawing state."""

    def __init__(self, c, cx, cy, size, pal, lw=None, fill=True):
        self.c, self.cx, self.cy, self.s, self.pal = c, cx, cy, size / 2, pal
        self.lw = default_lw(size) if lw is None else lw
        self.fill = fill

    def __enter__(self):
        c = self.c
        c.saveState()
        c.setLineJoin(1)
        c.setLineCap(1)
        c.setLineWidth(self.lw)
        c.setStrokeColor(self.pal.ink)
        c.setFillColor(self.pal.paper)
        return self

    def __exit__(self, *exc):
        self.c.restoreState()

    @property
    def colored(self):
        return bool(self.pal.fills)

    def colour(self, key):
        """Fill colour for a semantic key (white for line-art palettes)."""
        return self.pal.fills.get(key, self.pal.paper) if key else self.pal.paper

    def X(self, x):
        return self.cx + x * self.s

    def Y(self, y):
        return self.cy + y * self.s

    def path(self):
        return _Path(self)

    def _paint(self, op, fill, col):
        fill = self.fill if fill is None else fill
        self.c.saveState()
        self.c.setFillColor(self.colour(col))
        op(1 if fill else 0)
        self.c.restoreState()

    def draw(self, path, fill=None, stroke=True, col=None):
        self._paint(lambda f: self.c.drawPath(path.p, stroke=1 if stroke else 0,
                                              fill=f), fill, col)

    def poly(self, pts, close=True, fill=None, col=None):
        self.draw(self.path().poly(pts, close), fill=fill if close else False,
                  col=col)

    def circle(self, x, y, r, fill=None, col=None):
        self._paint(lambda f: self.c.circle(self.X(x), self.Y(y), r * self.s,
                                            stroke=1, fill=f), fill, col)

    def ellipse(self, x, y, rx, ry, fill=None, col=None):
        self._paint(lambda f: self.c.ellipse(self.X(x - rx), self.Y(y - ry),
                                             self.X(x + rx), self.Y(y + ry),
                                             stroke=1, fill=f), fill, col)

    def rect(self, x, y, w, h, r=0.0, fill=None, col=None):
        if r:
            op = lambda f: self.c.roundRect(self.X(x), self.Y(y), w * self.s,
                                            h * self.s, r * self.s, stroke=1, fill=f)
        else:
            op = lambda f: self.c.rect(self.X(x), self.Y(y), w * self.s,
                                       h * self.s, stroke=1, fill=f)
        self._paint(op, fill, col)

    def dot(self, x, y, r):
        self.c.saveState()
        self.c.setFillColor(self.pal.ink)
        self.c.circle(self.X(x), self.Y(y), r * self.s, stroke=0, fill=1)
        self.c.restoreState()

    def line(self, pts, width=None, col=None):
        """Open stroke; `col` recolours the stroke only on coloured palettes."""
        self.c.saveState()
        if width is not None:
            self.c.setLineWidth(width)
        if col and self.colored:
            self.c.setStrokeColor(self.colour(col))
        self.draw(self.path().poly(pts, close=False), fill=False)
        self.c.restoreState()

    def capsules(self, strokes, width, col=None):
        """Draw thick round strokes as one outlined, colourable silhouette."""
        c = self.c
        for colour, w in ((self.pal.ink, width * self.s + 2 * self.lw),
                          (self.colour(col), width * self.s)):
            c.saveState()
            c.setStrokeColor(colour)
            c.setLineWidth(w)
            c.setDash()
            for pts in strokes:
                self.draw(self.path().poly(pts, close=False), fill=False)
            c.restoreState()


# ---------------------------------------------------------------- helpers
def star_points(n=5, r_out=0.95, r_in=0.42, cy=-0.07, rot=90):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append((r * math.cos(a), cy + r * math.sin(a)))
    return pts


TREE_RIGHT = [(0.0, 0.80), (0.38, 0.30), (0.18, 0.30), (0.58, -0.20),
              (0.30, -0.20), (0.80, -0.68)]


def tree_points():
    right = TREE_RIGHT
    left = [(-x, y) for x, y in reversed(right[1:])]
    return right + [(-0.80, -0.68)] + left[1:]


# ---------------------------------------------------------------- figures
def star(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        u.poly(star_points(), col="gold")


def tree(c, cx, cy, size, pal, lw=None, fill=True, ornaments=True, topper=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        top = 0.62 if topper else 0.80
        k = 0.88 if topper else 1.0
        u.rect(-0.14, -0.96, 0.28, 0.32, col="brown")
        sy = (top + 0.66) / 1.48  # foliage spans y = -0.68..0.80 in tree_points
        pts = [(x * k, -0.66 + (y + 0.68) * sy) for x, y in tree_points()]
        u.poly(pts, col="green")
        if ornaments and fill:
            balls = ["red", "gold", "blue"]
            for i, (x, y) in enumerate([(-0.30, -0.45), (0.22, -0.40), (0.48, -0.55),
                                        (-0.55, -0.56), (0.0, -0.05), (-0.22, -0.10),
                                        (0.28, 0.0), (0.05, 0.33), (-0.04, -0.52)]):
                u.circle(x, y, 0.065, col=balls[i % 3])
        if topper:
            with _Unit(c, u.X(0), u.Y(0.76), size * 0.36, pal, u.lw * 0.8, fill) as s:
                s.poly(star_points(), col="gold")


def santa_hat(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        body = (u.path().m(-0.68, -0.38)
                .cv(-0.62, 0.30, -0.05, 0.80, 0.52, 0.62)
                .cv(0.62, 0.58, 0.66, 0.50, 0.66, 0.42)
                .cv(0.40, 0.40, 0.56, -0.05, 0.70, -0.38).close())
        u.draw(body, col="red")
        u.rect(-0.88, -0.70, 1.76, 0.38, r=0.17, col="snow")
        u.circle(0.68, 0.40, 0.19, col="snow")


def ornament(c, cx, cy, size, pal, lw=None, fill=True, tone="red"):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        u.draw(u.path().arc(0, 0.80, 0.11, -60, 300, move=True), fill=False)
        u.rect(-0.17, 0.54, 0.34, 0.20, r=0.04, col="gold")
        u.circle(0, -0.16, 0.72, col=tone)
        zig = [(-0.71, -0.05)]
        for i in range(1, 8):
            zig.append((-0.71 + i * 1.42 / 8, -0.05 + (0.13 if i % 2 else 0)))
        zig.append((0.71, -0.05))
        u.line(zig)
        u.line([(-0.62, -0.50), (0.62, -0.50)])
        for x in (-0.3, 0.0, 0.3):
            u.circle(x, 0.28, 0.06, col="gold")


def gift(c, cx, cy, size, pal, lw=None, fill=True, tone="red", ribbon="gold"):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        for sx in (-1, 1):
            loop = (u.path().m(0, 0.45)
                    .cv(sx * 0.15, 0.95, sx * 0.62, 0.90, sx * 0.52, 0.58)
                    .cv(sx * 0.45, 0.45, sx * 0.20, 0.45, 0, 0.45).close())
            u.draw(loop, col=ribbon)
        u.rect(-0.75, -0.92, 1.5, 1.07, col=tone)
        u.rect(-0.12, -0.92, 0.24, 1.07, col=ribbon)
        u.rect(-0.86, 0.15, 1.72, 0.30, col=tone)
        u.rect(-0.12, 0.15, 0.24, 0.30, col=ribbon)
        u.circle(0, 0.50, 0.09, col=ribbon)


def candy_cane(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        n = 24
        hook = [(0.0 + 0.36 * math.cos(math.radians(a)),
                 0.42 + 0.36 * math.sin(math.radians(a)))
                for a in [180 - i * 180 / n for i in range(n + 1)]]
        pts = [(-0.36, 0.20)] + hook + [(0.36, -0.78)]
        u.capsules([pts], 0.30)
        w = u.lw * 2.4 if u.colored else None
        for y in (-0.62, -0.34, -0.06, 0.20):
            u.line([(0.24, y - 0.05), (0.48, y + 0.11)], width=w, col="red")
        for a in (40, 90, 140):
            ra = math.radians(a)
            u.line([(0.21 * math.cos(ra), 0.42 + 0.21 * math.sin(ra)),
                    (0.51 * math.cos(ra + 0.25), 0.42 + 0.51 * math.sin(ra + 0.25))],
                   width=w, col="red")


def snowman(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        u.line([(-0.30, 0.05), (-0.72, 0.30), (-0.82, 0.42)], col="brown")
        u.line([(-0.68, 0.27), (-0.74, 0.12)], col="brown")
        u.line([(0.30, 0.05), (0.72, 0.30), (0.82, 0.42)], col="brown")
        u.line([(0.68, 0.27), (0.80, 0.18)], col="brown")
        u.circle(0, -0.55, 0.42, col="snow")
        u.circle(0, -0.02, 0.32, col="snow")
        u.circle(0, 0.47, 0.24, col="snow")
        u.rect(-0.30, 0.66, 0.60, 0.07, col="dark")
        u.rect(-0.18, 0.72, 0.36, 0.25, col="dark")
        u.dot(-0.09, 0.53, 0.04)
        u.dot(0.09, 0.53, 0.04)
        u.poly([(0, 0.47), (0.24, 0.42), (0, 0.41)], col="orange")
        for y in (0.12, -0.04, -0.20):
            u.dot(0, y, 0.035)


def snowflake(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        if u.colored:
            c.setStrokeColor(u.colour("ice"))
        for i in range(6):
            a = math.radians(90 + i * 60)
            ca, sa = math.cos(a), math.sin(a)
            u.line([(0, 0), (0.92 * ca, 0.92 * sa)])
            for d, b in ((0.5, 0.22), (0.72, 0.15)):
                for s in (-1, 1):
                    a2 = a + s * math.radians(45)
                    u.line([(d * ca, d * sa),
                            (d * ca + b * math.cos(a2), d * sa + b * math.sin(a2))])
        u.circle(0, 0, 0.10, col="snow")


def bell(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        u.circle(0, -0.72, 0.13, col="orange")
        u.draw(u.path().arc(0, 0.78, 0.12, -50, 280, move=True), fill=False)
        body = (u.path().m(-0.82, -0.62)
                .cv(-0.62, -0.45, -0.62, -0.10, -0.58, 0.20)
                .cv(-0.52, 0.55, -0.30, 0.68, 0, 0.68)
                .cv(0.30, 0.68, 0.52, 0.55, 0.58, 0.20)
                .cv(0.62, -0.10, 0.62, -0.45, 0.82, -0.62).close())
        u.draw(body, col="gold")
        u.line([(-0.64, -0.32), (0.64, -0.32)])
        u.line([(-0.62, -0.20), (0.62, -0.20)])


def reindeer(c, cx, cy, size, pal, lw=None, fill=True):
    """Friendly reindeer head."""
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        for s in (-1, 1):
            u.capsules([[(s * 0.16, 0.18), (s * 0.30, 0.52), (s * 0.40, 0.84)],
                        [(s * 0.27, 0.48), (s * 0.06, 0.70)],
                        [(s * 0.36, 0.70), (s * 0.64, 0.80)]], 0.10, col="tan")
        for s in (-1, 1):
            ear = (u.path().m(s * 0.30, 0.14)
                   .cv(s * 0.55, 0.36, s * 0.85, 0.28, s * 0.86, 0.18)
                   .cv(s * 0.70, 0.02, s * 0.50, 0.00, s * 0.34, 0.02).close())
            u.draw(ear, col="brown")
        u.ellipse(0, -0.12, 0.40, 0.44, col="brown")
        u.ellipse(0, -0.55, 0.30, 0.24, col="tan")
        u.circle(0, -0.42, 0.12, col="red")
        u.dot(-0.16, 0.02, 0.055)
        u.dot(0.16, 0.02, 0.055)
        u.draw(u.path().arc(0, -0.60, 0.10, 200, 140, move=True), fill=False)


def sleigh(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        gift(c, u.X(-0.30), u.Y(0.28), size * 0.36, pal, u.lw * 0.8, fill,
             tone="green", ribbon="red")
        gift(c, u.X(0.12), u.Y(0.20), size * 0.30, pal, u.lw * 0.8, fill,
             tone="blue")
        for x in (-0.55, 0.30):
            u.line([(x, -0.35), (x, -0.62)])
        runner = (u.path().m(-0.95, -0.62).l(0.55, -0.62)
                  .cv(0.88, -0.62, 0.95, -0.36, 0.76, -0.30))
        u.draw(runner, fill=False)
        body = (u.path().m(-0.82, -0.38).l(0.45, -0.38)
                .cv(0.78, -0.38, 0.92, -0.05, 0.86, 0.40)
                .l(0.68, 0.40)
                .cv(0.62, 0.15, 0.50, 0.04, 0.24, 0.04)
                .l(-0.62, 0.04).l(-0.70, 0.36).l(-0.92, 0.36).close())
        u.draw(body, col="red")
        u.line([(-0.70, -0.17), (0.60, -0.17)], width=u.lw * 2 if u.colored else None,
               col="gold")


def stocking(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        body = (u.path().m(-0.40, 0.60).l(-0.40, -0.48)
                .cv(-0.40, -0.80, -0.20, -0.92, 0.05, -0.92)
                .l(0.45, -0.92)
                .cv(0.82, -0.92, 0.85, -0.42, 0.50, -0.40)
                .l(0.20, -0.40).l(0.20, 0.60).close())
        u.draw(body, col="red")
        u.rect(-0.52, 0.52, 0.84, 0.40, r=0.12, col="snow")
        u.draw(u.path().m(0.28, -0.92).cv(0.30, -0.70, 0.40, -0.55, 0.62, -0.47),
               fill=False)
        u.draw(u.path().m(-0.40, -0.55).cv(-0.18, -0.55, -0.08, -0.70, -0.08, -0.92),
               fill=False)


def gingerbread(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        u.capsules([[(0, 0.55), (0, -0.25)],
                    [(-0.60, 0.02), (0, 0.18), (0.60, 0.02)],
                    [(-0.38, -0.76), (0, -0.25), (0.38, -0.76)],
                    [(0, 0.55), (0, 0.56)]], 0.36, col="cookie")
        c.saveState()
        c.setLineWidth(u.lw)
        u.circle(0, 0.60, 0.32, col="cookie")
        c.restoreState()
        u.dot(-0.11, 0.66, 0.045)
        u.dot(0.11, 0.66, 0.045)
        u.draw(u.path().arc(0, 0.60, 0.15, 210, 120, move=True), fill=False)
        for y in (0.15, -0.02, -0.19):
            u.dot(0, y, 0.045)
        for s in (-1, 1):
            u.line([(s * 0.48, 0.12), (s * 0.54, -0.04)])
            u.line([(s * 0.26, -0.58), (s * 0.40, -0.54)])


def cloud(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        circles = [(-0.55, -0.12, 0.33), (-0.18, 0.15, 0.42), (0.30, 0.18, 0.38),
                   (0.60, -0.10, 0.30), (0.05, -0.20, 0.36)]
        k = u.lw / u.s
        for colour, dr in ((pal.ink, k / 2), (u.colour("snow"), -k / 2)):
            c.saveState()
            c.setFillColor(colour)
            for x, y, r in circles:
                c.circle(u.X(x), u.Y(y), (r + dr) * u.s, stroke=0, fill=1)
            c.restoreState()


def house(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        u.rect(0.30, 0.25, 0.22, 0.55, col="brick")
        u.rect(-0.70, -0.90, 1.40, 1.0, col="cream")
        u.poly([(-0.88, 0.08), (0, 0.80), (0.88, 0.08)], col="red")
        u.rect(-0.20, -0.90, 0.40, 0.62, r=0.08, col="brown")
        u.rect(-0.58, -0.45, 0.28, 0.28, col="gold")
        u.rect(0.30, -0.45, 0.28, 0.28, col="gold")
        u.dot(0.12, -0.60, 0.035)


def penguin(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        for s in (-1, 1):
            u.ellipse(s * 0.20, -0.86, 0.20, 0.09, col="orange")
            u.ellipse(s * 0.52, -0.12, 0.13, 0.36, col="navy")
        u.ellipse(0, -0.05, 0.52, 0.82, col="navy")
        u.ellipse(0, -0.22, 0.34, 0.58, col="snow")
        if u.colored:   # eyes on a white face patch so they stay visible
            u.ellipse(0, 0.42, 0.28, 0.16, col="snow")
        u.dot(-0.15, 0.45, 0.05)
        u.dot(0.15, 0.45, 0.05)
        u.poly([(-0.10, 0.32), (0.10, 0.32), (0, 0.18)], col="orange")


def igloo(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        dome = u.path().m(-0.92, -0.62).arc(0, -0.62, 0.92, 180, -180).close()
        u.draw(dome, col="ice_light")
        for y, half in ((-0.30, 0.84), (0.02, 0.63), (0.18, 0.44)):
            u.line([(-half, y), (half, y)])
        door = u.path().m(-0.30, -0.62).arc(0, -0.30, 0.30, 180, -180).l(0.30, -0.62).close()
        u.draw(door, col="navy")
        u.line([(-0.92, -0.62), (0.92, -0.62)])


def holly(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        for s in (-1, 1):
            leaf = (u.path().m(0, -0.05)
                    .cv(s * 0.25, 0.35, s * 0.65, 0.40, s * 0.95, 0.20)
                    .cv(s * 0.70, 0.00, s * 0.45, -0.25, 0, -0.05).close())
            u.draw(leaf, col="green")
            u.line([(0, -0.05), (s * 0.80, 0.18)])
        for x, y in ((-0.16, -0.22), (0.16, -0.22), (0, -0.45)):
            u.circle(x, y, 0.16, col="red")


def mitten(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        body = (u.path().m(-0.40, -0.45)
                .l(-0.42, 0.40)
                .cv(-0.42, 0.95, 0.38, 0.95, 0.38, 0.40)
                .l(0.38, 0.15)
                .cv(0.55, 0.30, 0.78, 0.25, 0.72, 0.05)
                .cv(0.66, -0.12, 0.45, -0.30, 0.38, -0.45).close())
        u.draw(body, col="blue")
        u.rect(-0.50, -0.92, 0.98, 0.48, r=0.10, col="snow")
        u.line([(-0.30, 0.05), (0.20, 0.05)])
        u.line([(-0.30, 0.25), (0.20, 0.25)])


def moon(c, cx, cy, size, pal, lw=None, fill=True):
    with _Unit(c, cx, cy, size, pal, lw, fill) as u:
        crescent = (u.path().m(0.25, 0.85)
                    .cv(-0.65, 0.85, -0.65, -0.85, 0.25, -0.85)
                    .cv(-0.20, -0.45, -0.20, 0.45, 0.25, 0.85).close())
        u.draw(crescent, col="gold")


# Icons used as small rewards in the corner of each activity page.
REWARD_ICONS = [star, ornament, bell, gift, candy_cane, snowman, stocking,
                santa_hat, gingerbread, tree, reindeer, mitten, holly, penguin,
                snowflake, sleigh]

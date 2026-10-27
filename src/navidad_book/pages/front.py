"""Front matter: title page, "this book belongs to", guide for grown-ups."""
from .. import graphics as g
from ..draw import EXAMPLE_LW, guide, start_dot
from ..frame import activity_frame, snow_ground, header, reward, page_number
from ..layout import Rect


def _rounded(ctx, r, radius=14, lw=2.0, dash=None, group="", label="panel"):
    c = ctx.c
    c.saveState()
    c.setStrokeColor(ctx.pal.ink)
    c.setFillColor(ctx.pal.paper)
    c.setLineWidth(lw)
    if dash:
        c.setDash(dash)
    c.roundRect(r.x0, r.y0, r.w, r.h, radius, stroke=1, fill=1)
    c.restoreState()
    return ctx.register(r.x0 - lw / 2, r.y0 - lw / 2, r.x1 + lw / 2,
                        r.y1 + lw / 2, kind="art", group=group, label=label)


def title_page(ctx):
    cfg, s = ctx.cfg, ctx.safe
    snow_ground(ctx, height=80)
    y = s.y1 - 48
    t1 = ctx.text_fit(cfg.title, s.cx, y, s.w, 50, bold=True)
    t2 = ctx.text_fit(cfg.subtitle, s.cx, t1.y0 - 36, s.w, 32, bold=True)
    sub = ("Preescritura · Une los puntos · Laberintos · Para colorear")
    t3 = ctx.text_fit(sub, s.cx, t2.y0 - 26, s.w, 15)

    badge_w, badge_h = 150, 40
    badge = Rect(s.cx - badge_w / 2, t3.y0 - 18 - badge_h, s.cx + badge_w / 2,
                 t3.y0 - 18)
    g_badge = ctx.new_group("badge")
    _rounded(ctx, badge, radius=20, lw=2.5, group=g_badge, label="badge")
    ctx.text("3 a 5 años", badge.cx, badge.y0 + 13, 20, bold=True,
             group=g_badge)

    art = Rect(s.x0, s.y0, s.x1, badge.y0 - 16)
    group = ctx.new_group("cover")
    unit = min(art.w, art.h)
    items = [
        (g.tree, 0.50, 0.55, 0.80),
        (g.gift, 0.30, 0.10, 0.20),
        (g.gift, 0.70, 0.09, 0.17),
        (g.reindeer, 0.13, 0.30, 0.30),
        (g.snowman, 0.88, 0.30, 0.32),
        (g.star, 0.08, 0.85, 0.12),
        (g.snowflake, 0.92, 0.86, 0.13),
        (g.snowflake, 0.15, 0.62, 0.09),
        (g.star, 0.86, 0.62, 0.08),
    ]
    for fn, ux, uy, us in items:
        size = us * unit
        cx = art.x0 + ux * art.w
        cy = art.y0 + uy * art.h
        cx = min(max(cx, art.x0 + size / 2), art.x1 - size / 2)
        cy = min(max(cy, art.y0 + size / 2), art.y1 - size / 2)
        ctx.art(fn, cx, cy, size, group=group)


def belongs_page(ctx):
    s = ctx.safe
    snow_ground(ctx)
    top = header(ctx, "Este libro pertenece a:")
    reward(ctx, g.santa_hat)
    page_number(ctx)
    c = ctx.c

    # name line
    line_y = top - 70
    c.saveState()
    c.setStrokeColor(ctx.pal.ink)
    c.setLineWidth(2)
    c.line(s.x0 + 40, line_y, s.x1 - 40, line_y)
    c.restoreState()
    ctx.register(s.x0 + 40, line_y - 1, s.x1 - 40, line_y + 1, label="name-line")
    hint = ctx.text("(escribe aquí tu nombre)", s.cx, line_y - 20, 11,
                    color=ctx.pal.accent)

    # age
    age_y = hint.y0 - 52
    lbl = ctx.text("Mi edad:", s.x0 + 40, age_y, 20, bold=True, align="left")
    x = lbl.x1 + 50
    for n in ("3", "4", "5"):
        grp = ctx.new_group("age")
        c.saveState()
        c.setStrokeColor(ctx.pal.ink)
        c.setFillColor(ctx.pal.paper)
        c.setLineWidth(2)
        c.circle(x, age_y + 7, 22, stroke=1, fill=1)
        c.restoreState()
        ctx.register(x - 23, age_y + 7 - 23, x + 23, age_y + 7 + 23, group=grp,
                     label="age-circle")
        ctx.text(n, x, age_y, 22, bold=True, group=grp)
        x += 70
    ctx.text("¡Rodea tu edad!", x + 10, age_y + 1, 13, align="left",
             color=ctx.pal.accent)

    # portrait frame
    frame = Rect(s.x0 + 40, s.y0 + 76 + 20, s.x1 - 40, age_y - 50)
    grp = ctx.new_group("portrait")
    _rounded(ctx, frame, radius=18, lw=2.5, group=grp, label="portrait")
    ctx.text("Dibújate aquí con tu gorro de Navidad", frame.cx,
             frame.y0 + 14, 13, group=grp, color=ctx.pal.accent)
    corner = 54
    for cx, cy in ((frame.x0 + 6, frame.y1 - 6), (frame.x1 - 6, frame.y1 - 6)):
        cx = min(max(cx, s.x0 + corner / 2), s.x1 - corner / 2)
        ctx.art(g.holly, cx, cy, corner, group=grp)


TIPS = [
    "Busca un momento tranquilo y sesiones cortas (10-15 minutos).",
    "Usa lápices gruesos o ceras: son más fáciles de agarrar.",
    "Empieza siempre en el punto de inicio y sigue la flecha.",
    "La primera línea de cada página es un ejemplo para mirar.",
    "Si se sale de la línea, ¡no pasa nada! Lo importante es practicar.",
    "Al terminar cada página, deja que coloree el dibujo de premio.",
]


def guide_page(ctx):
    activity_frame(ctx, "Para mamás, papás y educadores",
                   "Cómo aprovechar este libro de preescritura", g.bell)
    area = ctx.content
    c = ctx.c
    y = area.y1
    for tip in TIPS:
        grp = ctx.new_group("tip")
        ctx.art(g.star, area.x0 + 11, y - 10, 18, group=grp)
        y = ctx.paragraph(tip, area.x0 + 30, y, area.w - 30, 14, group=grp)
        y -= 14

    # legend
    y -= 6
    ctx.text("Así son los símbolos del libro:", area.x0, y - 18, 16, bold=True,
             align="left")
    y -= 60
    lx0, lx1 = area.x0 + 20, area.x0 + 150
    rows = [
        ("start", "Punto de inicio: empieza aquí y sigue la flecha."),
        ("example", "Línea de ejemplo: mírala antes de empezar."),
        ("dotted", "Línea punteada: repásala con el lápiz."),
        ("reward", "¡Colorea! Un premio en cada página."),
    ]
    for kind, label in rows:
        grp = ctx.new_group("legend")
        if kind == "start":
            start_dot(ctx, lx0 + 10, y, group=grp)
        elif kind == "example":
            guide(ctx, [(lx0, y), (lx1, y)], example=True, group=grp)
        elif kind == "dotted":
            guide(ctx, [(lx0, y), (lx1, y)], group=grp)
        else:
            ctx.art(g.gift, lx0 + 22, y, 40, group=grp)
        ctx.paragraph(label, lx1 + 20, y + 9, area.x1 - lx1 - 20, 13, group=grp)
        y -= 50
    # a little colouring scene in the free space left at the bottom
    scene = Rect(area.x0, area.y0, area.x1, y + 10)
    grp = ctx.new_group("scene")
    size = min(scene.h, scene.w / 3.4)
    if size > 50:
        for fn, fx, k in ((g.reindeer, 0.17, 0.9), (g.sleigh, 0.50, 1.0),
                          (g.snowman, 0.83, 0.9)):
            ctx.art(fn, scene.x0 + fx * scene.w, scene.y0 + size * k / 2,
                    size * k, group=grp)


PAGES = [title_page, belongs_page, guide_page]

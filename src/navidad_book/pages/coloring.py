"""Full-page colouring scenes."""
from .. import graphics as g
from ..frame import activity_frame


def _scene(ctx, items):
    """items: (fn, ux, uy, usize, kwargs) in content-relative units 0..1."""
    area = ctx.content
    unit = min(area.w, area.h)
    group = ctx.new_group("scene")
    for fn, ux, uy, us, kw in items:
        size = us * unit
        cx = area.x0 + ux * area.w
        cy = area.y0 + uy * area.h
        ctx.art(fn, cx, cy, size, group=group, **kw)


def color_tree(ctx):
    activity_frame(ctx, "Colorea el árbol de Navidad",
                   "Usa tus colores favoritos para las bolas y los regalos.",
                   g.ornament)
    _scene(ctx, [
        (g.snowflake, 0.08, 0.90, 0.12, {}),
        (g.snowflake, 0.92, 0.84, 0.10, {}),
        (g.tree, 0.50, 0.56, 0.86, {}),
        (g.gift, 0.17, 0.13, 0.24, {}),
        (g.gift, 0.83, 0.12, 0.22, {}),
        (g.gift, 0.66, 0.08, 0.15, {}),
        (g.candy_cane, 0.34, 0.09, 0.17, {}),
    ])


def color_snowman(ctx):
    activity_frame(ctx, "Mi muñeco de nieve",
                   "Colorea su gorro, sus botones y los copos de nieve.",
                   g.snowflake)
    _scene(ctx, [
        (g.snowman, 0.50, 0.50, 0.86, {}),
        (g.snowflake, 0.10, 0.88, 0.14, {}),
        (g.snowflake, 0.88, 0.90, 0.12, {}),
        (g.snowflake, 0.08, 0.52, 0.10, {}),
        (g.snowflake, 0.92, 0.55, 0.11, {}),
        (g.tree, 0.12, 0.13, 0.24, {"ornaments": False}),
        (g.holly, 0.88, 0.10, 0.18, {}),
    ])


def color_night(ctx):
    activity_frame(ctx, "La noche de Navidad",
                   "El reno y el trineo van cargados de regalos.", g.moon)
    _scene(ctx, [
        (g.moon, 0.12, 0.86, 0.22, {}),
        (g.star, 0.40, 0.92, 0.10, {}),
        (g.star, 0.62, 0.84, 0.08, {}),
        (g.star, 0.88, 0.92, 0.12, {}),
        (g.reindeer, 0.24, 0.48, 0.38, {}),
        (g.sleigh, 0.70, 0.48, 0.50, {}),
        (g.bell, 0.12, 0.12, 0.18, {}),
        (g.stocking, 0.50, 0.12, 0.20, {}),
        (g.gingerbread, 0.86, 0.12, 0.20, {}),
    ])


PAGES = [color_tree, color_snowman, color_night]

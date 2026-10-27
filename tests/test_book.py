import dataclasses
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from navidad_book.book import build, page_plan  # noqa: E402
from navidad_book.config import INCH, BookConfig  # noqa: E402
from navidad_book.maze import generate  # noqa: E402
import preflight  # noqa: E402


def test_plan_has_40_pages():
    assert len(page_plan()) == 40


@pytest.mark.parametrize("bleed,color", [(True, "color"), (False, "bw")])
def test_build_passes_layout_and_preflight(tmp_path, bleed, color):
    cfg = dataclasses.replace(BookConfig(), use_bleed=bleed, color_mode=color)
    out = tmp_path / "book.pdf"
    _, issues = build(out, cfg, strict=False)
    assert issues == []
    n, errors, _ = preflight.check(out, cfg)
    assert n == 40
    assert errors == []


def test_colouring_pages_stay_line_art():
    from navidad_book.palette import COLOR
    assert COLOR.fills and COLOR.line_art().fills == {}


def test_kdp_geometry():
    cfg = BookConfig()
    assert cfg.page_w == pytest.approx(8.625 * INCH)
    assert cfg.page_h == pytest.approx(11.25 * INCH)
    # bleed sits on the outside edge: right for rectos, left for versos
    assert cfg.trim_origin(1) == (0.0, 0.125 * INCH)
    assert cfg.trim_origin(2) == (0.125 * INCH, 0.125 * INCH)
    x0, y0, x1, y1 = cfg.safe_rect(1)
    assert x0 >= 0.375 * INCH and cfg.trim_w - x1 >= 0.375 * INCH


@pytest.mark.parametrize("cols,rows", [(3, 3), (6, 7), (10, 10)])
def test_maze_is_perfect_and_solvable(cols, rows):
    m = generate(cols, rows, seed=1)
    edges = sum(len(v) for v in m.open.values()) // 2
    assert edges == cols * rows - 1          # spanning tree: no loops
    path = m.solve((0, 0), (cols - 1, rows - 1))
    assert path[0] == (0, 0) and path[-1] == (cols - 1, rows - 1)
    assert generate(cols, rows, seed=1).open == m.open   # deterministic

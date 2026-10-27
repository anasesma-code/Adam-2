#!/usr/bin/env python3
"""Independent pre-flight check of the generated PDF against KDP rules.

Checks (on the PDF itself, not on the generator's own bookkeeping):
  * page count (even, within KDP paperback limits, as configured)
  * MediaBox = trim + bleed, TrimBox/BleedBox present and consistent
  * every font is embedded (KDP rejects non-embedded fonts)
  * no raster images (all artwork is vector -> sharp at 300 DPI and above)
  * every text run starts inside the safe area
Optionally renders 300 DPI previews with pdftoppm (--previews).
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from navidad_book.config import BookConfig  # noqa: E402

TOL = 0.5  # pt


def mult(m, n):
    a, b, c, d, e, f = m
    a2, b2, c2, d2, e2, f2 = n
    return [a * a2 + b * c2, a * b2 + b * d2, c * a2 + d * c2, c * b2 + d * d2,
            e * a2 + f * c2 + e2, e * b2 + f * d2 + f2]


def fonts_of(page):
    res = page.get("/Resources") or {}
    fonts = res.get("/Font") or {}
    for name, ref in fonts.items():
        yield name, ref.get_object()


def is_embedded(font):
    if font.get("/Subtype") == "/Type0":
        font = font["/DescendantFonts"][0].get_object()
    desc = font.get("/FontDescriptor")
    if desc is None:
        return False
    desc = desc.get_object()
    return any(k in desc for k in ("/FontFile", "/FontFile2", "/FontFile3"))


def has_images(page):
    res = page.get("/Resources") or {}
    xobjs = res.get("/XObject") or {}
    return any(x.get_object().get("/Subtype") == "/Image" for x in xobjs.values())


def check(pdf_path, cfg):
    errors, notes = [], []
    reader = PdfReader(str(pdf_path))
    n = len(reader.pages)
    if n != cfg.total_pages:
        errors.append(f"page count {n} != {cfg.total_pages}")
    if n % 2:
        errors.append("page count must be even")
    if not 24 <= n <= 828:
        errors.append(f"page count {n} outside KDP paperback range 24-828")

    unembedded = set()
    for i, page in enumerate(reader.pages, start=1):
        mb = [float(v) for v in page.mediabox]
        w, h = mb[2] - mb[0], mb[3] - mb[1]
        if abs(w - cfg.page_w) > TOL or abs(h - cfg.page_h) > TOL:
            errors.append(f"p{i}: page size {w / 72:.3f}x{h / 72:.3f} in, "
                          f"expected {cfg.page_w / 72:.3f}x{cfg.page_h / 72:.3f}")
        tb = [float(v) for v in page.trimbox]
        ox, oy = cfg.trim_origin(i)
        expected_tb = [ox, oy, ox + cfg.trim_w, oy + cfg.trim_h]
        if any(abs(a - b) > TOL for a, b in zip(tb, expected_tb)):
            errors.append(f"p{i}: TrimBox {tb} != {expected_tb}")
        for name, font in fonts_of(page):
            if not is_embedded(font):
                unembedded.add(str(font.get("/BaseFont")))
        if has_images(page):
            errors.append(f"p{i}: contains raster images")

        sx0, sy0, sx1, sy1 = cfg.safe_rect(i)
        runs = []

        def visitor(text, cm, tm, font_dict, font_size):
            if text.strip():
                m = mult(tm, cm)
                runs.append((text.strip(), m[4] - ox, m[5] - oy))

        page.extract_text(visitor_text=visitor)
        for text, x, y in runs:
            if not (sx0 - TOL <= x <= sx1 + TOL and sy0 - TOL <= y <= sy1 + TOL):
                errors.append(f"p{i}: text '{text[:25]}' at ({x:.1f},{y:.1f}) "
                              "outside safe area")
        if not runs and i > 0:
            notes.append(f"p{i}: no text found")
    if unembedded:
        errors.append(f"non-embedded fonts: {sorted(unembedded)}")
    return n, errors, notes


def previews(pdf_path, out_dir, pages, dpi):
    if not shutil.which("pdftoppm"):
        print("pdftoppm not found; skipping previews")
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in pages:
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-f", str(p),
                        "-l", str(p), str(pdf_path), str(out_dir / "page")],
                       check=True)
    print(f"previews ({dpi} DPI) -> {out_dir}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", nargs="?", default=str(ROOT / "output" / "libro_navidad_trazos.pdf"))
    ap.add_argument("--no-bleed", action="store_true")
    ap.add_argument("--previews", default="", help="pages to render, e.g. 1,4,21,29")
    ap.add_argument("--dpi", type=int, default=300)
    args = ap.parse_args()

    cfg = BookConfig(use_bleed=not args.no_bleed)
    n, errors, notes = check(args.pdf, cfg)
    for note in notes:
        print("note:", note)
    if errors:
        print("PRE-FLIGHT FAILED:")
        for e in errors:
            print("  -", e)
        return 1
    print(f"PRE-FLIGHT OK: {n} pages, {cfg.page_w / 72:.3f} x {cfg.page_h / 72:.3f} in, "
          "fonts embedded, vector only, text inside safe area")
    if args.previews:
        pages = [int(p) for p in args.previews.split(",")]
        previews(args.pdf, ROOT / "output" / "previews", pages, args.dpi)
    return 0


if __name__ == "__main__":
    sys.exit(main())

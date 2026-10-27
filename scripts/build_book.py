#!/usr/bin/env python3
"""Build the KDP-ready interior PDF.

Usage:
    python scripts/build_book.py                 # colour interior with bleed
    python scripts/build_book.py --bw            # black & white interior
    python scripts/build_book.py --no-bleed      # 8.5x11 without bleed
"""
import argparse
import dataclasses
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from navidad_book.book import LayoutError, build  # noqa: E402
from navidad_book.config import BookConfig  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--output", default=str(ROOT / "output" / "libro_navidad_trazos.pdf"))
    ap.add_argument("--bw", action="store_true",
                    help="black & white interior (cheaper to print on KDP)")
    ap.add_argument("--no-bleed", action="store_true", help="no bleed (8.5x11 page)")
    ap.add_argument("--seed", type=int, default=BookConfig.seed, help="maze seed")
    ap.add_argument("--author", default="")
    ap.add_argument("--lenient", action="store_true",
                    help="write the PDF even if layout validation finds problems")
    args = ap.parse_args()

    cfg = dataclasses.replace(BookConfig(), color_mode="bw" if args.bw else "color",
                              use_bleed=not args.no_bleed, seed=args.seed,
                              author=args.author)
    try:
        plan, issues = build(args.output, cfg, strict=not args.lenient)
    except LayoutError as e:
        print(e, file=sys.stderr)
        return 1
    for i, (section, fn) in enumerate(plan, 1):
        print(f"  {i:2d}  {section:<15} {fn.__name__}")
    for issue in issues:
        print("WARNING:", issue, file=sys.stderr)
    print(f"\nOK: {len(plan)} pages -> {args.output}")
    print(f"Page size: {cfg.page_w / 72:.3f} x {cfg.page_h / 72:.3f} in "
          f"(trim 8.5 x 11 in, bleed {'yes' if cfg.use_bleed else 'no'}, "
          f"{'colour' if cfg.color_mode == 'color' else 'B&W'} interior)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

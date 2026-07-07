#!/usr/bin/env python3
"""Fuse three monochrome frames (R-, G-, B-illuminated) into one color image.

Host-side prototype for Camera Variant A (HM01B0 + sequential RGB flash).
Validate white-balance gains and inspect motion fringing on the PC before
implementing the same math in Apollo510 firmware.

Usage:
    python rgb_fusion.py frame_r.png frame_g.png frame_b.png -o color.png
    python rgb_fusion.py r.pgm g.pgm b.pgm --calibrate          # print gains from a gray target
    python rgb_fusion.py r.pgm g.pgm b.pgm --gains 1.00 1.18 1.42 -o out.png

Requires: pip install pillow numpy
"""
import argparse
import sys

import numpy as np
from PIL import Image


def load_gray(path: str) -> np.ndarray:
    img = Image.open(path).convert("L")
    return np.asarray(img, dtype=np.float32)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("frames", nargs=3, metavar=("R", "G", "B"),
                    help="grayscale frames captured under R, G, B illumination")
    ap.add_argument("-o", "--out", default="fused.png", help="output color image")
    ap.add_argument("--gains", nargs=3, type=float, metavar=("GR", "GG", "GB"),
                    help="per-channel white-balance gains (from --calibrate)")
    ap.add_argument("--calibrate", action="store_true",
                    help="treat inputs as shots of a neutral gray target and print gains")
    ap.add_argument("--target", type=float, default=180.0,
                    help="target gray level for calibration (default 180)")
    args = ap.parse_args()

    r, g, b = (load_gray(p) for p in args.frames)
    if not (r.shape == g.shape == b.shape):
        sys.exit(f"frame sizes differ: {r.shape} {g.shape} {b.shape}")

    if args.calibrate:
        gains = [args.target / max(ch.mean(), 1e-6) for ch in (r, g, b)]
        print(f"means   R={r.mean():7.2f}  G={g.mean():7.2f}  B={b.mean():7.2f}")
        print(f"--gains {gains[0]:.3f} {gains[1]:.3f} {gains[2]:.3f}")
        return 0

    gains = args.gains or [1.0, 1.0, 1.0]
    rgb = np.stack([np.clip(ch * k, 0, 255) for ch, k in zip((r, g, b), gains)],
                   axis=-1).astype(np.uint8)
    Image.fromarray(rgb, "RGB").save(args.out)
    print(f"wrote {args.out}  ({rgb.shape[1]}x{rgb.shape[0]})")
    print("inspect edges of moving objects for color fringing - that is the "
          "field-sequential-color artifact discussed in the Variant A doc.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

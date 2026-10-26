"""Bake the dock "liquid glass" refraction into static textures.

The runtime once rendered this with an SVG <feDisplacementMap> +
<feGaussianBlur> filter every frame, which is slow on webOS. Because the
dock bar has fixed dimensions and the backdrop is a static photo, the whole
filtered result is constant. This script pre-renders it with numpy/Pillow so
the runtime just displays a static image (no SVG filter at all).

It reproduces the original SVG filter pipeline:
  - feImage displacement map (dock-displacement.png), upscaled to the tex
  - feDisplacementMap scale=28, R->X, G->Y
  - feGaussianBlur stdDeviation=2.2
and adds a soft baked specular rim highlight along the glass bezel.

Usage: python3 scripts/bake-dock-glass.py
"""
from math import pi, sin
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'launcher/assets'

WIDTH, HEIGHT = 1824, 230
PADDING = 24
SCALE = 28.0          # feDisplacementMap scale (max pixel shift)
BLUR = 2.2            # feGaussianBlur stdDeviation
SPECULAR_STRENGTH = 34.0


def load_displacement():
    image = Image.open(ASSETS / 'dock-displacement.png').convert('RGB')
    # The filter applies the map over the 1872x278 tex, so upscale.
    image = image.resize((WIDTH + 2 * PADDING, HEIGHT + 2 * PADDING), Image.BILINEAR)
    a = np.asarray(image, dtype=np.float32)
    # R -> X, G -> Y, 128 neutral, remap to [-1, 1].
    dx = (a[..., 0] - 128.0) / 127.0 * SCALE
    dy = (a[..., 1] - 128.0) / 127.0 * SCALE
    return dx, dy


def refract(src: np.ndarray, dx: np.ndarray, dy: np.ndarray) -> np.ndarray:
    H, W, C = src.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # Sample the source at the displaced position (matches feDisplacementMap).
    sx = np.clip(xx + dx, 0, W - 1)
    sy = np.clip(yy + dy, 0, H - 1)
    x0 = np.floor(sx).astype(int); y0 = np.floor(sy).astype(int)
    x1 = np.minimum(x0 + 1, W - 1); y1 = np.minimum(y0 + 1, H - 1)
    fx = (sx - x0)[..., None]; fy = (sy - y0)[..., None]
    top = src[y0, x0] * (1 - fx) + src[y0, x1] * fx
    bot = src[y1, x0] * (1 - fx) + src[y1, x1] * fx
    return top * (1 - fy) + bot * fy


def specular(displacement_mag: np.ndarray) -> np.ndarray:
    # Soft rim highlight where the bezel bends (high displacement gradient).
    mag = displacement_mag
    glow = np.clip(mag / np.max(mag) if mag.max() > 0 else mag, 0, 1)
    # Smooth, modulate by a gentle top-weighted sheen.
    sheen = np.clip(1.0 - (np.arange(HEIGHT + 2 * PADDING) / (HEIGHT + 2 * PADDING)), 0.25, 1.0)
    r = glow * sheen[:, None] * SPECULAR_STRENGTH
    return r[..., None]


def bake(name, source):
    crop = Image.open(ASSETS / source).convert('RGB')
    arr = np.asarray(crop, dtype=np.float32)
    dx, dy = load_displacement()
    mag = np.sqrt(dx ** 2 + dy ** 2)
    refracted = refract(arr, dx, dy)
    # Re-apply the gaussian blur from the original filter.
    blurred = Image.fromarray(np.clip(refracted, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(BLUR))
    out = np.asarray(blurred, dtype=np.float32)
    out += specular(mag)
    out = np.clip(out, 0, 255).astype(np.uint8)
    target = ASSETS / name
    Image.fromarray(out).save(target, quality=90, optimize=True)
    print('baked', target.name, target.stat().st_size, 'bytes')


def main():
    bake('dock-glass-home.jpg', 'dock-home.jpg')
    bake('dock-glass-grid.jpg', 'dock-grid.jpg')
    print('done')


if __name__ == '__main__':
    main()

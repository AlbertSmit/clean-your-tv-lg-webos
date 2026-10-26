"""Rebuild checked-in dock textures with Pillow; not required by normal builds."""
from math import hypot, pi, sin
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'launcher/assets'
WIDTH, HEIGHT, RADIUS = 1824, 230, 72
PADDING = 24


def displacement_map():
    # Half-resolution, smooth deterministic field. 128 is neutral in sRGB.
    image = Image.new('RGB', (WIDTH // 2, HEIGHT // 2), (128, 128, 128))
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            dx, dy = (x + .5) * 2 - WIDTH / 2, (y + .5) * 2 - HEIGHT / 2
            qx, qy = abs(dx) - (WIDTH / 2 - RADIUS), abs(dy) - (HEIGHT / 2 - RADIUS)
            distance = RADIUS - hypot(max(qx, 0), max(qy, 0)) - min(max(qx, qy), 0)
            if not 0 < distance < 28:
                continue
            if qx > 0 and qy > 0:
                length = hypot(qx, qy)
                nx, ny = qx / length, qy / length
            else:
                nx, ny = (1, 0) if qx > qy else (0, 1)
            nx *= -1 if dx < 0 else 1
            ny *= -1 if dy < 0 else 1
            t = distance / 28
            strength = sin(pi * t) * (1 - t) ** .35
            pixels[x, y] = (round(128 - 127 * nx * strength), round(128 - 127 * ny * strength), 128)
    padded = Image.new('RGB', (image.width + PADDING, image.height + PADDING), (128, 128, 128))
    padded.paste(image, (PADDING // 2, PADDING // 2))
    padded.save(ASSETS / 'dock-displacement.png', optimize=True)


def crop_backdrop(name, source, top):
    image = Image.open(ASSETS / source).convert('RGB').resize((1920, 1080), Image.Resampling.LANCZOS)
    image = image.crop((40 - PADDING, top - PADDING, 40 + WIDTH + PADDING, top + HEIGHT + PADDING))
    image.save(ASSETS / name, quality=90, optimize=True)


if __name__ == '__main__':
    displacement_map()
    crop_backdrop('dock-home.jpg', 'cinema-backdrop.jpg', 784)
    crop_backdrop('dock-grid.jpg', 'cinema-backdrop-soft.jpg', 60)
    print('Rebuilt dock displacement map and padded backdrop crops.')

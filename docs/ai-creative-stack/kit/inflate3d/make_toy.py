#!/usr/bin/env python3
"""Draw an original test toy (a stylised tin fish) as an RGBA PNG, so tests need no external images.

  python make_toy.py out/toy_fish.png [--size 512]
"""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw


def draw_fish(size=512):
    w, h = size, int(size * 0.72)
    s = size / 512
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body = [(70 * s, 90 * s), (380 * s, 290 * s)]
    tail = [(360 * s, 190 * s), (480 * s, 95 * s), (455 * s, 190 * s), (480 * s, 285 * s)]
    fin = [(190 * s, 110 * s), (260 * s, 40 * s), (300 * s, 115 * s)]
    d.polygon(tail, fill=(214, 92, 38, 255))
    d.polygon(fin, fill=(232, 150, 40, 255))
    d.ellipse(body, fill=(240, 176, 52, 255))
    for k in range(4):  # painted stripes, clipped to the body by drawing on a mask
        stripe = Image.new("L", (w, h), 0)
        ImageDraw.Draw(stripe).rectangle([(150 + 55 * k) * s, 80 * s, (172 + 55 * k) * s, 300 * s], fill=255)
        body_mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(body_mask).ellipse(body, fill=255)
        stripe = Image.composite(stripe, Image.new("L", (w, h), 0), body_mask)
        img.paste((196, 70, 40, 255), mask=stripe)
    d.ellipse([(110 * s, 150 * s), (150 * s, 190 * s)], fill=(250, 245, 230, 255))
    d.ellipse([(122 * s, 162 * s), (142 * s, 182 * s)], fill=(30, 30, 40, 255))
    d.arc([(85 * s, 190 * s), (135 * s, 230 * s)], 300, 60, fill=(120, 40, 20, 255), width=max(1, int(4 * s)))
    for k in range(9):  # rivets along the seam, the tin-toy detail
        x = (120 + 28 * k) * s
        y = 190 * s + math.sin(k * 0.8) * 4 * s
        d.ellipse([(x - 4 * s, y - 4 * s), (x + 4 * s, y + 4 * s)], fill=(150, 110, 60, 255))
    return img


def draw_rocket(size=512):
    """A second original test toy: a stubby wind-up rocket, upright."""
    w, h = int(size * 0.6), size
    s = size / 512
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w / 2
    d.polygon([(cx - 70 * s, 330 * s), (cx - 120 * s, 440 * s), (cx - 60 * s, 420 * s)], fill=(40, 110, 170, 255))
    d.polygon([(cx + 70 * s, 330 * s), (cx + 120 * s, 440 * s), (cx + 60 * s, 420 * s)], fill=(40, 110, 170, 255))
    d.rounded_rectangle([(cx - 72 * s, 150 * s), (cx + 72 * s, 430 * s)], radius=int(40 * s), fill=(225, 225, 215, 255))
    d.polygon([(cx - 72 * s, 170 * s), (cx, 30 * s), (cx + 72 * s, 170 * s)], fill=(205, 60, 50, 255))
    d.ellipse([(cx - 38 * s, 210 * s), (cx + 38 * s, 286 * s)], fill=(40, 110, 170, 255))
    d.ellipse([(cx - 26 * s, 222 * s), (cx + 26 * s, 274 * s)], fill=(170, 215, 240, 255))
    d.rectangle([(cx - 72 * s, 360 * s), (cx + 72 * s, 380 * s)], fill=(205, 60, 50, 255))
    d.polygon([(cx - 40 * s, 430 * s), (cx + 40 * s, 430 * s), (cx + 20 * s, 480 * s), (cx - 20 * s, 480 * s)], fill=(90, 90, 100, 255))
    return img


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--size", type=int, default=512)
    a = ap.parse_args()
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    draw_fish(a.size).save(a.out)
    print(a.out)

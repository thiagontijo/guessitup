#!/usr/bin/env python3
"""Draws the Guessitup Arena app icons (needs Pillow). Run from the repo root."""
import math
import os

from PIL import Image, ImageDraw

BG1, BG2 = (33, 45, 99), (14, 19, 48)
BARS = [(57, 135, 229), (25, 158, 112), (217, 89, 38)]   # Chico, Arnaldo, Herman
CHALK = (241, 239, 230)


def icon(size, scale=1.0):
    s = size * 4
    im = Image.new("RGB", (s, s), BG2)
    d = ImageDraw.Draw(im)
    for y in range(s):
        t = y / s
        d.line([(0, y), (s, y)], fill=tuple(round(BG1[i] + (BG2[i] - BG1[i]) * t) for i in range(3)))
    w = s * 0.60 * scale
    left, base = s / 2 - w / 2, s / 2 + w * 0.46
    bw = w * 0.27
    gap = (w - 3 * bw) / 2
    heights = [0.44, 0.70, 0.28]
    for i, h in enumerate(heights):
        x0, y0 = left + i * (bw + gap), base - w * h
        d.rounded_rectangle([x0, y0, x0 + bw, base], radius=bw * 0.3, fill=BARS[i])
        d.rectangle([x0, base - bw * 0.35, x0 + bw, base], fill=BARS[i])
    d.rounded_rectangle([left - w * 0.07, base, left + w * 1.07, base + w * 0.045], radius=w * 0.02, fill=CHALK)
    cx, cy, r = left + bw + gap + bw / 2, base - w * 0.70 - w * 0.19, w * 0.135
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=CHALK)
    return im.resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    os.makedirs("icons", exist_ok=True)
    icon(180).save("icons/icon-180.png")
    icon(192).save("icons/icon-192.png")
    icon(512).save("icons/icon-512.png")
    icon(512, 0.78).save("icons/icon-maskable-512.png")
    print("icons written")

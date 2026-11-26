"""materialforge: procedural, tileable PBR texture sets.

Every field is built from periodic pieces (FFT-filtered noise on an integer
frequency lattice, wrapped domain warps, wrapped Voronoi cells, integer thread
and ring counts), so every map tiles seamlessly in both directions.

Usage:
    python materialforge.py <preset> --size 1024 --seed 7 --out out/<name>/

Presets: wood, brushed-metal, painted-plastic, fabric, stone, rust.
"""
from __future__ import annotations

import argparse
import json
import sys
import zlib
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates
from scipy.spatial import cKDTree

PRESETS = ["wood", "brushed-metal", "painted-plastic", "fabric", "stone", "rust"]


# ----------------------------------------------------------------------------
# Periodic building blocks
# ----------------------------------------------------------------------------

def _smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _normalize(a):
    a = a - a.mean()
    s = a.std()
    return a / s if s > 0 else a


def spectral_noise(rng, n, f_lo=1.0, f_hi=64.0, beta=2.0, stretch=(1.0, 1.0), angle=0.0):
    """Periodic noise: white noise filtered in the frequency domain.

    Frequencies are measured in cycles per tile, so the look does not change
    with resolution. Only integer frequencies exist on the FFT lattice, so the
    result is exactly periodic. ``beta`` sets the power-law falloff (2 is
    fBm-like). ``stretch`` scales the frequency axes after rotating them by
    ``angle``; a large stretch[0] makes features long along x.
    Returns a zero-mean, unit-variance field.
    """
    white = rng.standard_normal((n, n))
    spec = np.fft.fft2(white)
    f = np.fft.fftfreq(n) * n
    fy, fx = np.meshgrid(f, f, indexing="ij")
    c, s = np.cos(angle), np.sin(angle)
    u = (c * fx + s * fy) * stretch[0]
    v = (-s * fx + c * fy) * stretch[1]
    r = np.hypot(u, v)
    amp = np.where(r > 0, np.maximum(r, 1e-6), 1.0) ** (-beta / 2.0)
    # soft band window in (stretched) frequency
    amp *= _smoothstep(f_lo * 0.5, f_lo, r)
    amp *= 1.0 - _smoothstep(f_hi, f_hi * 1.5, r)
    amp[0, 0] = 0.0
    out = np.real(np.fft.ifft2(spec * amp))
    return _normalize(out)


def warp(field, dx, dy):
    """Resample ``field`` at (x + dx, y + dy), wrapping at the tile edges.

    dx, dy are in pixels and must themselves be periodic fields.
    """
    n = field.shape[0]
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float64)
    return map_coordinates(field, [yy + dy, xx + dx], order=1, mode="grid-wrap")


def tile_coords(n):
    """Pixel-centre coordinates in tile units [0, 1)."""
    t = (np.arange(n) + 0.5) / n
    y, x = np.meshgrid(t, t, indexing="ij")
    return x, y


def periodic_voronoi(rng, n, grid, jitter=0.4, warp_px=None):
    """Jittered-grid Voronoi on a torus.

    Returns (cell_id, edge_distance) where edge_distance is the distance to
    the nearest cell border in tile units.
    """
    gy, gx = np.meshgrid(np.arange(grid), np.arange(grid), indexing="ij")
    pts = np.stack([(gx.ravel() + 0.5 + rng.uniform(-jitter, jitter, gx.size)) / grid,
                    (gy.ravel() + 0.5 + rng.uniform(-jitter, jitter, gy.size)) / grid], axis=1)
    pts %= 1.0
    k = len(pts)
    offs = np.array([(ox, oy) for oy in (-1, 0, 1) for ox in (-1, 0, 1)], dtype=np.float64)
    all_pts = (pts[None, :, :] + offs[:, None, :]).reshape(-1, 2)
    tree = cKDTree(all_pts)
    x, y = tile_coords(n)
    if warp_px is not None:
        x = (x + warp_px[0] / n) % 1.0
        y = (y + warp_px[1] / n) % 1.0
    q = np.stack([x.ravel(), y.ravel()], axis=1)
    _, idx = tree.query(q, k=2)
    a = all_pts[idx[:, 0]]
    b = all_pts[idx[:, 1]]
    ab = b - a
    ab_len = np.linalg.norm(ab, axis=1, keepdims=True)
    mid = 0.5 * (a + b)
    edge = np.abs(np.sum((q - mid) * (ab / ab_len), axis=1))
    cell = (idx[:, 0] % k).reshape(n, n)
    return cell, edge.reshape(n, n)


def periodic_segments_distance(n, segs):
    """Min distance (tile units) from each pixel to a set of short segments, on a torus."""
    x, y = tile_coords(n)
    best = np.full((n, n), np.inf)
    for (ax, ay, bx, by) in segs:
        dx = x - ax
        dy = y - ay
        dx -= np.round(dx)
        dy -= np.round(dy)
        ex, ey = bx - ax, by - ay
        L2 = ex * ex + ey * ey
        t = np.clip((dx * ex + dy * ey) / L2, 0.0, 1.0)
        px = dx - t * ex
        py = dy - t * ey
        best = np.minimum(best, np.sqrt(px * px + py * py))
    return best


def srgb_mix(a, b, t):
    """Blend two sRGB colours with weight field t -> (n, n, 3)."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    t = np.asarray(t)[..., None]
    return a * (1.0 - t) + b * t


# ----------------------------------------------------------------------------
# Presets. Each returns a dict of float fields:
#   base (n,n,3) sRGB 0..1, rough (n,n), metal (n,n), height (n,n) 0..1
# plus physical scale info and BSDF suggestions.
# ----------------------------------------------------------------------------

def preset_wood(rng, n):
    x, y = tile_coords(n)
    big = spectral_noise(rng, n, 1, 6, 2.5, stretch=(4.0, 1.0))
    mid = spectral_noise(rng, n, 2, 24, 2.0, stretch=(6.0, 1.0))
    rings = 14  # integer: rings per tile, keeps y periodic
    t = rings * (y + 0.035 * big + 0.008 * mid)
    r = t - np.floor(t)
    late = _smoothstep(0.55, 0.85, r) * (1.0 - _smoothstep(0.9, 1.0, r))
    streak = spectral_noise(rng, n, 8, 220, 1.2, stretch=(30.0, 1.0))
    pores = spectral_noise(rng, n, 60, 400, 0.5, stretch=(12.0, 1.0))
    pores = _smoothstep(1.3, 2.4, pores)  # sparse dark pore streaks
    tone = 0.5 + 0.18 * mid + 0.12 * streak
    base = srgb_mix((0.70, 0.49, 0.29), (0.43, 0.25, 0.12), np.clip(late * 0.85 + 0.25 * (1 - tone), 0, 1))
    base *= (1.0 - 0.35 * pores)[..., None]
    height = 0.55 - 0.18 * late + 0.06 * streak - 0.25 * pores
    rough = 0.62 - 0.10 * late + 0.05 * streak + 0.12 * pores
    metal = np.zeros((n, n))
    return dict(base=base, rough=rough, metal=metal, height=height,
                tile_size_m=0.6, height_depth_m=0.0015,
                bsdf={"Base Color": "base_color.png", "Metallic": 0.0, "Roughness": "roughness.png",
                      "IOR": 1.5, "Coat Weight": 0.0},
                notes="Plain-sawn grain running along +X. Rings per tile: 14.")


def preset_brushed_metal(rng, n):
    brush = spectral_noise(rng, n, 4, 500, 0.9, stretch=(60.0, 1.0))
    fine = spectral_noise(rng, n, 100, 600, 0.3, stretch=(25.0, 1.0))
    blot = spectral_noise(rng, n, 1, 8, 2.5)
    segs = []
    for _ in range(28):
        ax, ay = rng.uniform(0, 1, 2)
        ang = rng.normal(0.0, 0.25)
        length = rng.uniform(0.08, 0.35)
        segs.append((ax, ay, ax + length * np.cos(ang), ay + length * np.sin(ang)))
    d = periodic_segments_distance(n, segs)
    scratch = 1.0 - _smoothstep(0.0, 1.2 / 512.0 + 0.6 / n, d)
    v = 0.74 + 0.035 * brush + 0.015 * fine + 0.02 * blot
    base = np.stack([v * 0.97, v * 0.98, v * 1.0], axis=-1) + 0.06 * scratch[..., None]
    height = 0.5 + 0.10 * brush + 0.04 * fine - 0.35 * scratch
    rough = 0.30 + 0.05 * brush + 0.03 * blot - 0.10 * scratch
    metal = np.ones((n, n))
    return dict(base=base, rough=rough, metal=metal, height=height,
                tile_size_m=0.25, height_depth_m=0.0002,
                bsdf={"Base Color": "base_color.png", "Metallic": 1.0, "Roughness": "roughness.png",
                      "Anisotropic": 0.6, "Anisotropic Rotation": 0.0},
                notes="Brush direction along +X. Use the tangent along U for anisotropy.")


def preset_painted_plastic(rng, n):
    peel = spectral_noise(rng, n, 20, 110, 1.5)
    blot = spectral_noise(rng, n, 1, 6, 2.5)
    segs = []
    for _ in range(10):
        ax, ay = rng.uniform(0, 1, 2)
        ang = rng.uniform(0, np.pi)
        length = rng.uniform(0.04, 0.15)
        segs.append((ax, ay, ax + length * np.cos(ang), ay + length * np.sin(ang)))
    d = periodic_segments_distance(n, segs)
    scuff = 1.0 - _smoothstep(0.0, 2.5 / 512.0 + 0.8 / n, d)
    base = np.empty((n, n, 3))
    col = np.array([0.08, 0.30, 0.62])
    base[:] = col
    base *= (1.0 + 0.025 * blot)[..., None]
    base = base * (1 - 0.25 * scuff[..., None]) + 0.25 * scuff[..., None] * 0.7
    height = 0.5 + 0.22 * peel - 0.25 * scuff
    rough = 0.38 + 0.02 * peel + 0.02 * blot + 0.25 * scuff
    metal = np.zeros((n, n))
    return dict(base=base, rough=rough, metal=metal, height=height,
                tile_size_m=0.3, height_depth_m=0.00015,
                bsdf={"Base Color": "base_color.png", "Metallic": 0.0, "Roughness": "roughness.png",
                      "IOR": 1.46, "Coat Weight": 0.15, "Coat Roughness": 0.2},
                notes="Orange-peel paint with a few light scuffs.")


def preset_fabric(rng, n):
    T = 32  # threads per tile; even so the over/under parity tiles
    x, y = tile_coords(n)
    u = x * T
    v = y * T
    i = np.floor(u).astype(np.int64)
    j = np.floor(v).astype(np.int64)
    fu = u - i
    fv = v - j

    def prof(f):
        return np.sqrt(np.clip(1.0 - (2.0 * f - 1.0) ** 2 / 0.82, 0.0, 1.0))

    lift_w = np.cos(np.pi * (v - 0.5 + i))
    lift_f = np.cos(np.pi * (u - 0.5 + j))
    fib_w = spectral_noise(rng, n, 30, 400, 0.6, stretch=(1.0, 20.0))  # long along y
    fib_f = spectral_noise(rng, n, 30, 400, 0.6, stretch=(20.0, 1.0))  # long along x
    warp_h = prof(fu) * (0.72 + 0.28 * lift_w) + 0.03 * fib_w
    weft_h = prof(fv) * (0.72 - 0.28 * lift_f) + 0.03 * fib_f
    top_warp = warp_h >= weft_h
    height = np.maximum(warp_h, weft_h)
    shade_w = rng.normal(0, 0.03, T)[i % T]
    shade_f = rng.normal(0, 0.03, T)[j % T]
    warp_col = srgb_mix((0.16, 0.24, 0.42), (0.22, 0.31, 0.52), 0.5 + 0.5 * np.tanh(fib_w))
    warp_col += shade_w[..., None]
    weft_col = srgb_mix((0.72, 0.70, 0.64), (0.80, 0.78, 0.72), 0.5 + 0.5 * np.tanh(fib_f))
    weft_col += shade_f[..., None]
    base = np.where(top_warp[..., None], warp_col, weft_col)
    base *= (0.55 + 0.45 * np.clip(height, 0, 1))[..., None]
    height = 0.1 + 0.8 * np.clip(height, 0, 1)
    rough = 0.88 + 0.04 * (1 - height) + 0.02 * np.where(top_warp, fib_w, fib_f)
    metal = np.zeros((n, n))
    return dict(base=base, rough=rough, metal=metal, height=height,
                tile_size_m=0.04, height_depth_m=0.0004,
                bsdf={"Base Color": "base_color.png", "Metallic": 0.0, "Roughness": "roughness.png",
                      "Sheen Weight": 0.6, "Sheen Roughness": 0.4},
                notes="Plain weave, 32 threads per tile each way. Dark warp along V, light weft along U.")


def preset_stone(rng, n):
    wx = spectral_noise(rng, n, 2, 16, 2.0) * (0.018 * n)
    wy = spectral_noise(rng, n, 2, 16, 2.0) * (0.018 * n)
    grid = 5
    cell, edge = periodic_voronoi(rng, n, grid, jitter=0.38, warp_px=(wx, wy))
    k = grid * grid
    cell_h = rng.uniform(0.0, 0.18, k)[cell]
    cell_tint = rng.uniform(-0.06, 0.06, k)[cell]
    cell_hue = rng.uniform(0, 1, k)[cell]
    gap = 0.012
    bevel = _smoothstep(gap, gap + 0.035, edge)
    detail = spectral_noise(rng, n, 4, 200, 1.6)
    grit = spectral_noise(rng, n, 80, 500, 0.4)
    stone = bevel > 0.0
    height = 0.12 + bevel * (0.62 + cell_h) + 0.05 * detail * bevel + 0.015 * grit
    mortar_mask = 1.0 - _smoothstep(gap * 0.6, gap * 1.4, edge)
    c_a = srgb_mix((0.47, 0.45, 0.42), (0.55, 0.50, 0.43), cell_hue)
    c_b = srgb_mix(c_a, (0.36, 0.35, 0.34), np.clip(0.5 + 0.25 * detail, 0, 1))
    stone_col = c_b + (cell_tint + 0.03 * grit)[..., None]
    mortar_col = np.array([0.30, 0.29, 0.27]) + (0.03 * grit)[..., None]
    base = stone_col * (1 - mortar_mask[..., None]) + mortar_col * mortar_mask[..., None]
    rough = 0.78 + 0.08 * mortar_mask + 0.04 * grit - 0.04 * detail * stone
    metal = np.zeros((n, n))
    return dict(base=base, rough=rough, metal=metal, height=height,
                tile_size_m=1.0, height_depth_m=0.02,
                bsdf={"Base Color": "base_color.png", "Metallic": 0.0, "Roughness": "roughness.png",
                      "IOR": 1.5},
                notes="Irregular flagstones, 5x5 cells per tile, with mortar gaps.")


def preset_rust(rng, n):
    w1 = spectral_noise(rng, n, 1, 10, 2.0) * (0.04 * n)
    w2 = spectral_noise(rng, n, 1, 10, 2.0) * (0.04 * n)
    m = spectral_noise(rng, n, 2, 160, 1.8)
    m = _normalize(warp(m, w1, w2))
    thr = np.quantile(m, 0.55)  # about 45 percent of the tile is rust
    rust = _smoothstep(thr - 0.03, thr + 0.03, m)
    flake = spectral_noise(rng, n, 16, 400, 1.0)
    tone = spectral_noise(rng, n, 2, 40, 1.8)
    brush = spectral_noise(rng, n, 4, 400, 0.9, stretch=(50.0, 1.0))
    metal_col = np.stack([0.60 + 0.03 * brush] * 3, axis=-1) * np.array([0.98, 0.98, 1.0])
    dark = np.array([0.24, 0.10, 0.05])
    orange = np.array([0.62, 0.28, 0.09])
    yellow = np.array([0.74, 0.50, 0.22])
    t = np.clip(0.5 + 0.35 * tone, 0, 1)
    rust_col = srgb_mix(dark, orange, t)
    rust_col = srgb_mix(rust_col, yellow, np.clip(0.6 * flake - 0.5, 0, 1))
    base = metal_col * (1 - rust[..., None]) + rust_col * rust[..., None]
    pits = _smoothstep(1.8, 2.6, -flake) * (1 - rust)
    height = 0.35 + 0.02 * brush - 0.12 * pits + rust * (0.25 + 0.12 * flake + 0.08 * tone)
    rough = (0.32 + 0.04 * brush) * (1 - rust) + (0.88 + 0.05 * flake) * rust
    metal = 1.0 - rust
    return dict(base=base, rough=rough, metal=metal, height=height,
                tile_size_m=0.5, height_depth_m=0.0012,
                bsdf={"Base Color": "base_color.png", "Metallic": "metallic.png", "Roughness": "roughness.png"},
                notes="Bare steel (metallic 1) with rust patches (metallic 0). Metallic is a near-binary mask.")


PRESET_FUNCS = {
    "wood": preset_wood,
    "brushed-metal": preset_brushed_metal,
    "painted-plastic": preset_painted_plastic,
    "fabric": preset_fabric,
    "stone": preset_stone,
    "rust": preset_rust,
}


# ----------------------------------------------------------------------------
# Derived maps
# ----------------------------------------------------------------------------

def normal_from_height(height01, depth_m, tile_m):
    """Tangent-space normal (OpenGL, +Y up the image) from a height field.

    Height in [0, 1] maps to ``depth_m`` metres; one texel is tile_m / n metres.
    Central differences with wrap-around, so the normal map tiles too.
    Returns (n, n, 3) unit vectors.
    """
    n = height01.shape[0]
    texel = tile_m / n
    h = height01 * depth_m
    dh_dx = (np.roll(h, -1, axis=1) - np.roll(h, 1, axis=1)) / (2.0 * texel)
    dh_drow = (np.roll(h, -1, axis=0) - np.roll(h, 1, axis=0)) / (2.0 * texel)
    # image rows grow downward; tangent-space +Y points up the image
    nx = -dh_dx
    ny = dh_drow
    nz = np.ones_like(h)
    nrm = np.sqrt(nx * nx + ny * ny + nz * nz)
    return np.stack([nx / nrm, ny / nrm, nz / nrm], axis=-1)


def ambient_occlusion(height01, depth_m, tile_m, strength=1.6):
    """Cheap multi-scale cavity AO from the height field (wrapped blurs)."""
    n = height01.shape[0]
    texel = tile_m / n
    h = height01 * depth_m
    occ = np.zeros_like(h)
    radii = [1, 2, 4, 8, 16]
    for r in radii:
        s = r * n / 256.0
        diff = gaussian_filter(h, s, mode="wrap") - h
        occ += np.clip(diff / (s * texel * 2.0), 0.0, 1.0)
    occ /= len(radii)
    return np.clip(1.0 - strength * occ, 0.0, 1.0)


def _to8(a):
    return np.clip(np.round(np.clip(a, 0.0, 1.0) * 255.0), 0, 255).astype(np.uint8)


def generate(preset, size=1024, seed=7):
    """Return a dict of numpy arrays and metadata for a preset (no file IO)."""
    if preset not in PRESET_FUNCS:
        raise ValueError(f"unknown preset {preset!r}; choose from {', '.join(PRESETS)}")
    if size < 32:
        raise ValueError("size must be at least 32")
    ss = np.random.SeedSequence([int(seed) & 0xFFFFFFFF, zlib.crc32(preset.encode())])
    rng = np.random.default_rng(ss)
    f = PRESET_FUNCS[preset](rng, size)
    h = f["height"]
    h = (h - h.min()) / max(h.max() - h.min(), 1e-9)
    nrm = normal_from_height(h, f["height_depth_m"], f["tile_size_m"])
    ao = ambient_occlusion(h, f["height_depth_m"], f["tile_size_m"])
    return {
        "base_color": _to8(f["base"]),
        "roughness": _to8(np.clip(f["rough"], 0.02, 1.0)),
        "metallic": _to8(f["metal"]),
        "normal": _to8(nrm * 0.5 + 0.5),
        "height": np.round(h * 65535.0).astype(np.uint16),
        "ao": _to8(ao),
        "meta": {k: f[k] for k in ("tile_size_m", "height_depth_m", "bsdf", "notes")},
    }


def write(result, preset, size, seed, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    Image.fromarray(result["base_color"], "RGB").save(out / "base_color.png", optimize=True)
    Image.fromarray(result["roughness"], "L").save(out / "roughness.png", optimize=True)
    Image.fromarray(result["metallic"], "L").save(out / "metallic.png", optimize=True)
    Image.fromarray(result["normal"], "RGB").save(out / "normal.png", optimize=True)
    Image.fromarray(result["height"]).save(out / "height.png")  # 16-bit grayscale
    Image.fromarray(result["ao"], "L").save(out / "ao.png", optimize=True)
    meta = result["meta"]
    rough = result["roughness"].astype(np.float64) / 255.0
    metal = result["metallic"].astype(np.float64) / 255.0
    bsdf = dict(meta["bsdf"])
    bsdf.setdefault("Normal", "normal.png via a Normal Map node (Tangent Space, Strength 1.0)")
    doc = {
        "generator": "materialforge",
        "preset": preset,
        "size": size,
        "seed": seed,
        "tileable": True,
        "tile_size_m": meta["tile_size_m"],
        "height_depth_m": meta["height_depth_m"],
        "notes": meta["notes"],
        "maps": {
            "base_color": {"file": "base_color.png", "colorspace": "sRGB", "bits": 8, "channels": "RGB",
                           "gltf": "baseColorTexture"},
            "roughness": {"file": "roughness.png", "colorspace": "Non-Color", "bits": 8, "channels": "L",
                          "gltf": "metallicRoughnessTexture.g", "mean": round(float(rough.mean()), 4)},
            "metallic": {"file": "metallic.png", "colorspace": "Non-Color", "bits": 8, "channels": "L",
                         "gltf": "metallicRoughnessTexture.b", "mean": round(float(metal.mean()), 4)},
            "normal": {"file": "normal.png", "colorspace": "Non-Color", "bits": 8, "channels": "RGB",
                       "convention": "OpenGL (+Y up), tangent space", "gltf": "normalTexture",
                       "derived_from": "height.png with tile_size_m and height_depth_m"},
            "height": {"file": "height.png", "colorspace": "Non-Color", "bits": 16, "channels": "L",
                       "gltf": None, "range_m": [0.0, meta["height_depth_m"]]},
            "ao": {"file": "ao.png", "colorspace": "Non-Color", "bits": 8, "channels": "L",
                   "gltf": "occlusionTexture.r"},
        },
        "principled_bsdf": bsdf,
        "displacement": {"node": "Displacement", "input": "height.png", "Midlevel": 0.0,
                         "Scale": meta["height_depth_m"], "units": "metres, for a mesh at real scale"},
        "mapping": {"Scale": [round(1.0 / meta["tile_size_m"], 6)] * 2,
                    "note": "texture repeats once per tile_size_m when UVs are in metres"},
    }
    (out / "material.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Procedural tileable PBR texture sets.")
    ap.add_argument("preset", choices=PRESETS)
    ap.add_argument("--size", type=int, default=1024)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default=None, help="output folder (default out/<preset>/)")
    a = ap.parse_args(argv)
    out = a.out or str(Path("out") / a.preset)
    res = generate(a.preset, a.size, a.seed)
    path = write(res, a.preset, a.size, a.seed, out)
    print(f"wrote {a.preset} {a.size}px seed {a.seed} -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

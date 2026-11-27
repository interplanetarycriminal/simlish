"""synth: write a synthetic Gaussian splat scene for tests.

Usage:
    python synth.py out.ply [--seed 3]

Scene (Y up): a torus around the Y axis (major radius 1.0, minor 0.25) shaded
from gold to violet, a red sphere above it and green and blue spheres on the
+X and -X sides. A sidecar <out>.json lists the objects, centres, radii and colours.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from splatply import surface_gaussians, write_ply  # noqa: E402

SPHERES = [
    {"name": "red", "center": [0.0, 1.15, 0.0], "radius": 0.35, "color": [0.92, 0.08, 0.08]},
    {"name": "green", "center": [1.9, 0.0, 0.0], "radius": 0.35, "color": [0.08, 0.85, 0.12]},
    {"name": "blue", "center": [-1.9, 0.0, 0.0], "radius": 0.35, "color": [0.10, 0.18, 0.95]},
]
TORUS = {"name": "torus", "major": 1.0, "minor": 0.25,
         "color_a": [0.95, 0.75, 0.25], "color_b": [0.62, 0.42, 0.90]}


def torus_samples(rng, n, R, r):
    # area element is proportional to (R + r cos(theta)): rejection-sample theta
    theta = np.empty(0)
    while len(theta) < n:
        t = rng.uniform(0, 2 * np.pi, n)
        keep = rng.uniform(0, R + r, n) < (R + r * np.cos(t))
        theta = np.concatenate([theta, t[keep]])
    theta = theta[:n]
    phi = rng.uniform(0, 2 * np.pi, n)
    ring = np.stack([np.cos(phi), np.zeros(n), np.sin(phi)], 1)
    nrm = np.cos(theta)[:, None] * ring + np.sin(theta)[:, None] * np.array([0.0, 1.0, 0.0])
    pts = R * ring + r * nrm
    return pts, nrm, phi


def sphere_samples(rng, n, c, rad):
    d = rng.standard_normal((n, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    return np.asarray(c) + rad * d, d


def build(seed=3, torus_n=30000, sphere_n=6000):
    rng = np.random.default_rng(seed)
    P, N, C = [], [], []
    S, Q = [], []
    pts, nrm, phi = torus_samples(rng, torus_n, TORUS["major"], TORUS["minor"])
    t = (0.5 + 0.5 * np.cos(phi))[:, None]
    col = np.asarray(TORUS["color_a"]) * t + np.asarray(TORUS["color_b"]) * (1 - t)
    s, q = surface_gaussians(pts, nrm)
    P.append(pts); N.append(nrm); C.append(col); S.append(s); Q.append(q)
    for sp in SPHERES:
        pts, nrm = sphere_samples(rng, sphere_n, sp["center"], sp["radius"])
        s, q = surface_gaussians(pts, nrm)
        P.append(pts); N.append(nrm); C.append(np.tile(sp["color"], (sphere_n, 1))); S.append(s); Q.append(q)
    P, N, C, S, Q = (np.concatenate(x) for x in (P, N, C, S, Q))
    return P, N, C, np.full(len(P), 0.95), S, Q


def main(argv=None):
    ap = argparse.ArgumentParser(description="Write a synthetic splat scene.")
    ap.add_argument("output")
    ap.add_argument("--seed", type=int, default=3)
    a = ap.parse_args(argv)
    P, N, C, A, S, Q = build(a.seed)
    out = write_ply(a.output, P, N, C, A, S, Q)
    meta = {"count": int(len(P)), "torus": TORUS, "spheres": SPHERES, "up": "+Y"}
    Path(out).with_suffix(".json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(out), "count": int(len(P))}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Test remesh: decimate the inflated toy fish to 1,600 and 800 faces and measure what was kept."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
ROOT = HERE.parents[1]
INFLATE = ROOT / "kit" / "inflate3d"
BLENDER = os.environ.get("BLENDER", "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe")
sys.path.insert(0, str(INFLATE))
from make_toy import draw_fish  # noqa: E402


def point_triangle_distance(p, a, b, c):
    """Exact distance from points p to triangles (a, b, c), vectorised (closest point by Voronoi region)."""
    ab, ac, ap = b - a, c - a, p - a
    d1, d2 = (ab * ap).sum(-1), (ac * ap).sum(-1)
    bp = p - b
    d3, d4 = (ab * bp).sum(-1), (ac * bp).sum(-1)
    cp = p - c
    d5, d6 = (ab * cp).sum(-1), (ac * cp).sum(-1)
    va, vb, vc = d3 * d6 - d5 * d4, d5 * d2 - d1 * d6, d1 * d4 - d3 * d2
    denom = np.where(np.abs(va + vb + vc) < 1e-30, 1e-30, va + vb + vc)
    v, w = vb / denom, vc / denom
    q = a + ab * v[..., None] + ac * w[..., None]  # interior by default
    def put(mask, val):
        q[mask] = val[mask]
    t = np.clip(d1 / np.where(np.abs(d1 - d3) < 1e-30, 1e-30, d1 - d3), 0, 1)
    put((vc <= 0) & (d1 >= 0) & (d3 <= 0), a + ab * t[..., None])
    t = np.clip(d2 / np.where(np.abs(d2 - d6) < 1e-30, 1e-30, d2 - d6), 0, 1)
    put((vb <= 0) & (d2 >= 0) & (d6 <= 0), a + ac * t[..., None])
    t = np.clip((d4 - d3) / np.where(np.abs((d4 - d3) + (d5 - d6)) < 1e-30, 1e-30, (d4 - d3) + (d5 - d6)), 0, 1)
    put((va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0), b + (c - b) * t[..., None])
    put((d1 <= 0) & (d2 <= 0), a)
    put((d3 >= 0) & (d4 <= d3), b)
    put((d6 >= 0) & (d5 <= d6), c)
    return np.linalg.norm(p - q, axis=-1)


def closest_distance(mesh, pts, k=24):
    from scipy.spatial import cKDTree
    tri = mesh.triangles
    _, idx = cKDTree(tri.mean(1)).query(pts, k=min(k, len(tri)))
    a, b, c = tri[idx, 0], tri[idx, 1], tri[idx, 2]
    return point_triangle_distance(pts[:, None, :], a, b, c).min(1)


def surface_error(src, dst, n=4000):
    """Distance from points sampled on the source to the decimated surface, as a share of the bbox diagonal."""
    pts, _ = trimesh.sample.sample_surface(src, n, seed=3)
    dist = closest_distance(dst, pts)
    diag = np.linalg.norm(src.extents)
    return float(dist.mean() / diag), float(dist.max() / diag)


def main():
    OUT.mkdir(exist_ok=True)
    draw_fish(512).save(OUT / "toy_fish.png")
    subprocess.run([sys.executable, str(INFLATE / "inflate3d.py"), str(OUT / "toy_fish.png"), str(OUT / "source.glb"), "--height", "0.2"],
                   check=True, capture_output=True)
    src = trimesh.load(OUT / "source.glb", force="mesh", process=False)
    checks, runs = {}, {}
    for budget in (1600, 800):
        t0 = time.time()
        r = subprocess.run([sys.executable, str(HERE / "remesh.py"), str(OUT / "source.glb"), str(OUT / f"remesh_{budget}.glb"), "--faces", str(budget)],
                           capture_output=True, text=True)
        secs = time.time() - t0
        dst = trimesh.load(OUT / f"remesh_{budget}.glb", force="mesh", process=False)
        mean_err, max_err = surface_error(src, dst)
        runs[budget] = {"seconds": round(secs, 2), "faces": len(dst.faces), "watertight": bool(dst.is_watertight),
                        "mean_error_of_diag": round(mean_err, 5), "max_error_of_diag": round(max_err, 5),
                        "volume_ratio": round(float(dst.volume / src.volume), 4)}
        checks[f"{budget}_runs"] = r.returncode == 0
        checks[f"{budget}_within_budget"] = len(dst.faces) <= budget
        checks[f"{budget}_close_to_budget"] = len(dst.faces) >= 0.9 * budget
        checks[f"{budget}_watertight"] = bool(dst.is_watertight)
        checks[f"{budget}_mean_error<1%"] = mean_err < 0.01
        checks[f"{budget}_max_error<5%"] = max_err < 0.05
        checks[f"{budget}_volume_kept"] = abs(runs[budget]["volume_ratio"] - 1) < 0.05
        checks[f"{budget}_uvs_kept"] = dst.visual.uv is not None and len(dst.visual.uv) == len(dst.vertices)

    if Path(BLENDER).exists():
        r = subprocess.run([BLENDER, "--background", "--factory-startup", "--python-exit-code", "1", "--python",
                            str(ROOT / "scripts" / "blender" / "validate_asset.py"), "--", str(OUT / "remesh_1600.glb"), str(OUT / "validate_1600.json")],
                           capture_output=True, text=True)
        checks["1600_blender_floor_checks"] = r.returncode == 0

    for name in ("toy_fish.png", "source.json"):
        (OUT / name).unlink(missing_ok=True)
    checks = {k: bool(v) for k, v in checks.items()}
    result = {"tool": "remesh", "source_faces": len(src.faces), "runs": runs, "checks": checks, "pass": all(checks.values())}
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for k, v in checks.items():
        print(("PASS " if v else "FAIL ") + k)
    print(json.dumps(runs))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

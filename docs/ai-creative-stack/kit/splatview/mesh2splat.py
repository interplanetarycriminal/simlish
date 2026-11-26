"""mesh2splat: turn a textured or vertex-coloured mesh into a 3D Gaussian Splatting PLY.

Usage:
    python mesh2splat.py in.glb out.ply --count 50000 [--seed 1]

Area-weighted surface samples; colour from the base-colour texture via UVs
(bilinear, wrapped), else vertex or face colours, else the material colour.
Each sample becomes a flat Gaussian: two in-plane scales from the local sample
spacing, a thin third axis along the normal, rotation from the tangent frame.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
from splatply import surface_gaussians, write_ply  # noqa: E402


def _image_rgba(img):
    return np.asarray(img.convert("RGBA"), dtype=np.float64) / 255.0


def sample_texture(img_rgba, uv):
    """Bilinear lookup with wrap. glTF/trimesh convention: v = 0 is the bottom row."""
    h, w = img_rgba.shape[:2]
    x = uv[:, 0] * w - 0.5
    y = (1.0 - uv[:, 1]) * h - 0.5
    x0 = np.floor(x).astype(np.int64)
    y0 = np.floor(y).astype(np.int64)
    fx = (x - x0)[:, None]
    fy = (y - y0)[:, None]
    x0w, x1w = x0 % w, (x0 + 1) % w
    y0w, y1w = y0 % h, (y0 + 1) % h
    c00 = img_rgba[y0w, x0w]
    c10 = img_rgba[y0w, x1w]
    c01 = img_rgba[y1w, x0w]
    c11 = img_rgba[y1w, x1w]
    return (c00 * (1 - fx) * (1 - fy) + c10 * fx * (1 - fy) + c01 * (1 - fx) * fy + c11 * fx * fy)


def _factor(v):
    if v is None:
        return np.ones(4)
    v = np.asarray(v, dtype=np.float64).ravel()
    if v.max() > 1.0:
        v = v / 255.0
    if len(v) == 3:
        v = np.append(v, 1.0)
    return v


def mesh_colors(mesh, face_idx, bary):
    """RGBA in [0,1] for samples on one mesh."""
    n = len(face_idx)
    vis = mesh.visual
    tri = mesh.faces[face_idx]
    kind = getattr(vis, "kind", None)
    if kind == "texture":
        mat = vis.material
        img = None
        factor = np.ones(4)
        if hasattr(mat, "baseColorTexture"):
            img = mat.baseColorTexture
            factor = _factor(getattr(mat, "baseColorFactor", None))
        elif hasattr(mat, "image"):
            img = mat.image
            factor = _factor(getattr(mat, "diffuse", None)) if img is None else np.ones(4)
        if img is not None and vis.uv is not None and len(vis.uv) == len(mesh.vertices):
            uv = np.einsum("nk,nkd->nd", bary, np.asarray(vis.uv, dtype=np.float64)[tri])
            return sample_texture(_image_rgba(img), uv) * factor, "texture"
        return np.tile(factor, (n, 1)), "material"
    if kind == "vertex":
        vc = np.asarray(vis.vertex_colors, dtype=np.float64) / 255.0
        return np.einsum("nk,nkd->nd", bary, vc[tri]), "vertex"
    if kind == "face":
        fc = np.asarray(vis.face_colors, dtype=np.float64) / 255.0
        return fc[face_idx], "face"
    return np.tile([0.7, 0.7, 0.7, 1.0], (n, 1)), "default"


def load_meshes(path):
    scene = trimesh.load(str(path), force="scene")
    meshes = [g for g in scene.dump(concatenate=False) if isinstance(g, trimesh.Trimesh) and len(g.faces)]
    if not meshes:
        raise SystemExit(f"no triangle meshes in {path}")
    return meshes


def mesh_to_splats(meshes, count, seed=1, opacity=0.9, size_factor=1.0, smooth_normals=False):
    rng = np.random.default_rng(seed)
    areas = [m.area_faces for m in meshes]
    total = np.concatenate(areas)
    if total.sum() <= 0:
        raise SystemExit("mesh has zero surface area")
    owner = np.concatenate([np.full(len(a), i) for i, a in enumerate(areas)])
    local = np.concatenate([np.arange(len(a)) for a in areas])
    pick = rng.choice(len(total), size=count, p=total / total.sum())
    r1 = rng.random(count)
    r2 = rng.random(count)
    s = np.sqrt(r1)
    bary_all = np.stack([1 - s, s * (1 - r2), s * r2], axis=1)
    pts = np.zeros((count, 3))
    nrm = np.zeros((count, 3))
    rgba = np.zeros((count, 4))
    sources = {}
    for i, m in enumerate(meshes):
        sel = np.nonzero(owner[pick] == i)[0]
        if len(sel) == 0:
            continue
        fidx = local[pick[sel]]
        bary = bary_all[sel]
        tri = m.vertices[m.faces[fidx]]
        pts[sel] = np.einsum("nk,nkd->nd", bary, tri)
        if smooth_normals:
            vn = m.vertex_normals[m.faces[fidx]]
            nn = np.einsum("nk,nkd->nd", bary, vn)
        else:
            nn = m.face_normals[fidx]
        nrm[sel] = nn / np.maximum(np.linalg.norm(nn, axis=1, keepdims=True), 1e-12)
        col, src = mesh_colors(m, fidx, bary)
        rgba[sel] = col
        sources[src] = sources.get(src, 0) + len(sel)
    scales, quats = surface_gaussians(pts, nrm, size_factor=size_factor)
    alpha = opacity * np.clip(rgba[:, 3], 0.0, 1.0)
    return pts, nrm, rgba[:, :3], alpha, scales, quats, sources


def main(argv=None):
    ap = argparse.ArgumentParser(description="Mesh (GLB/OBJ/PLY mesh) to 3D Gaussian Splatting PLY.")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--count", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--opacity", type=float, default=0.9)
    ap.add_argument("--size-factor", type=float, default=1.0,
                    help="in-plane Gaussian sigma as a multiple of local sample spacing")
    ap.add_argument("--smooth-normals", action="store_true", help="interpolate vertex normals")
    a = ap.parse_args(argv)
    if a.count < 4:
        ap.error("--count must be at least 4")
    meshes = load_meshes(a.input)
    pts, nrm, rgb, alpha, scales, quats, sources = mesh_to_splats(
        meshes, a.count, a.seed, a.opacity, a.size_factor, a.smooth_normals)
    write_ply(a.output, pts, nrm, rgb, alpha, scales, quats)
    print(json.dumps({"output": str(a.output), "count": int(len(pts)), "meshes": len(meshes),
                      "colour_sources": sources,
                      "bounds": [pts.min(0).round(4).tolist(), pts.max(0).round(4).tolist()],
                      "median_scale": float(np.median(scales[:, :2]))}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

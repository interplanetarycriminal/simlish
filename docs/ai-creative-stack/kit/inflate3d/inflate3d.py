#!/usr/bin/env python3
"""inflate3d: turn one image of an object into a closed, textured GLB by inflating its silhouette.

Our own stand-in for single-image 3D generators (Stable Fast 3D, SAM 3D Objects, TRELLIS.2).
No neural network: the object's outline is inflated like a balloon, so depth comes from the
distance to the silhouette edge. An optional depth map (from any depth estimator) shapes the front.

  python inflate3d.py toy.png out/toy.glb [--height 0.25] [--res 96] [--thickness 0.6]
                      [--back 1.0] [--depth depth.png --depth-scale 0.5] [--smooth 8]

Output: a watertight triangle mesh in meters, glTF Y up, front facing +Z, with the image as its
base-color texture (front and back share one planar UV projection, so there is no UV seam), plus
a JSON report beside the GLB.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image
from scipy import ndimage


def object_mask(rgba, tolerance):
    """Alpha if the image has it; otherwise everything that differs from the corner background colour."""
    alpha = rgba[..., 3]
    if alpha.min() < 250:
        mask = alpha > 127
    else:
        rgb = rgba[..., :3].astype(np.float32)
        h, w = mask_shape = rgb.shape[:2]
        corners = np.array([rgb[0, 0], rgb[0, w - 1], rgb[h - 1, 0], rgb[h - 1, w - 1]])
        bg = np.median(corners, axis=0)
        mask = np.linalg.norm(rgb - bg, axis=2) > tolerance
    labels, n = ndimage.label(mask)
    if n == 0:
        raise SystemExit("No object found in the image.")
    sizes = ndimage.sum(mask, labels, range(1, n + 1))
    mask = labels == (1 + int(np.argmax(sizes)))  # keep the largest object
    return ndimage.binary_fill_holes(mask)


def bleed(rgb, mask, radius=16):
    """Spread edge colours outward so texture filtering at the silhouette never samples the background."""
    out = rgb.astype(np.float32).copy()
    filled = mask.copy()
    for _ in range(radius):
        grown = ndimage.binary_dilation(filled)
        ring = grown & ~filled
        if not ring.any():
            break
        acc = np.zeros_like(out)
        cnt = np.zeros(mask.shape, np.float32)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                src = np.roll(np.roll(filled, dy, 0), dx, 1)
                acc += np.roll(np.roll(out, dy, 0), dx, 1) * src[..., None]
                cnt += src
        sel = ring & (cnt > 0)
        out[sel] = acc[sel] / cnt[sel][:, None]
        filled = filled | sel
    return out.clip(0, 255).astype(np.uint8)


def boundary_loops(edges_once):
    """Order boundary edges into loops (lists of vertex ids)."""
    nxt = {}
    for a, b in edges_once:
        nxt.setdefault(a, []).append(b)
        nxt.setdefault(b, []).append(a)
    seen, loops = set(), []
    for start in nxt:
        if start in seen:
            continue
        loop, prev, cur = [start], None, start
        seen.add(start)
        while True:
            options = [v for v in nxt[cur] if v != prev and v not in seen]
            if not options:
                break
            prev, cur = cur, options[0]
            loop.append(cur)
            seen.add(cur)
        loops.append(loop)
    return loops


def inflate(image_path, height_m=0.25, res=96, thickness=0.6, back=1.0, depth_path=None, depth_scale=0.5,
            smooth=8, tolerance=40.0, texture_size=1024):
    img = Image.open(image_path)
    rgba = np.asarray(img.convert("RGBA"))
    H, W = rgba.shape[:2]
    full_mask = object_mask(rgba, tolerance)

    # Work grid: `res` samples along the longer side.
    step = max(H, W) / res
    gh, gw = int(np.ceil(H / step)), int(np.ceil(W / step))
    ys = (np.arange(gh) + 0.5) * step
    xs = (np.arange(gw) + 0.5) * step
    grid = full_mask[np.clip(ys.astype(int), 0, H - 1)[:, None], np.clip(xs.astype(int), 0, W - 1)[None, :]]
    grid = ndimage.binary_opening(grid)  # drop one-cell spurs that would pinch the surface

    # Two triangles per fully-inside cell, wound so the front faces +Z (image y points down).
    quad = grid[:-1, :-1] & grid[1:, :-1] & grid[:-1, 1:] & grid[1:, 1:]
    qi, qj = np.nonzero(quad)
    if len(qi) == 0:
        raise SystemExit("The object is too small for this --res.")
    vid = -np.ones(grid.shape, int)
    used = np.zeros(grid.shape, bool)
    for di in (0, 1):
        for dj in (0, 1):
            used[qi + di, qj + dj] = True
    vi, vj = np.nonzero(used)
    vid[vi, vj] = np.arange(len(vi))
    a, b, c, d = vid[qi, qj], vid[qi, qj + 1], vid[qi + 1, qj], vid[qi + 1, qj + 1]
    tris = np.concatenate([np.stack([a, c, b], 1), np.stack([b, c, d], 1)])

    # Boundary of the triangulated region: edges used by exactly one triangle.
    e = np.sort(np.concatenate([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]]), axis=1)
    uniq, counts = np.unique(e, axis=0, return_counts=True)
    once = uniq[counts == 1]
    is_boundary = np.zeros(len(vi), bool)
    is_boundary[once.ravel()] = True
    px = np.stack([xs[vj], ys[vi]], 1)

    # Chords: interior edges whose two ends are both on the rim (one-cell-wide strips). Front and back
    # would share such an edge and make it non-manifold, so split each chord at its midpoint.
    chords = [tuple(x) for x, cnt in zip(uniq, counts) if cnt == 2 and is_boundary[x[0]] and is_boundary[x[1]]]
    tri_list = [list(t) for t in tris]
    extra_px, extra_parent = [], []
    for a_, b_ in chords:
        m = len(vi) + len(extra_px)
        extra_px.append(0.5 * (px[a_] + px[b_]))
        extra_parent.append(a_)
        for t in [t for t in tri_list if a_ in t and b_ in t]:
            i = t.index(a_)
            if t[(i + 1) % 3] == b_:      # winding a -> b -> c
                c_ = t[(i + 2) % 3]
                tri_list.remove(t)
                tri_list += [[a_, m, c_], [m, b_, c_]]
            else:                          # winding b -> a -> c
                c_ = t[(i + 1) % 3]
                tri_list.remove(t)
                tri_list += [[b_, m, c_], [m, a_, c_]]
    tris = np.array(tri_list)
    if extra_px:
        px = np.vstack([px, np.array(extra_px)])
        is_boundary = np.concatenate([is_boundary, np.zeros(len(extra_px), bool)])
    e = np.sort(np.concatenate([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]]), axis=1)
    uniq, counts = np.unique(e, axis=0, return_counts=True)
    once = uniq[counts == 1]

    # Image-plane positions (pixels), with the silhouette smoothed along each boundary loop.
    loops = boundary_loops([tuple(x) for x in once])
    for _ in range(4):
        for loop in loops:
            if len(loop) < 5:
                continue
            idx = np.array(loop)
            ring = px[idx]
            px[idx] = 0.5 * ring + 0.25 * (np.roll(ring, 1, 0) + np.roll(ring, -1, 0))

    # Inflation height: a circular cross-section of the local thickness, in pixels.
    dist = ndimage.distance_transform_edt(np.pad(used, 1))[1:-1, 1:-1]
    labels, _ = ndimage.label(used)
    dmax = np.asarray(ndimage.maximum(dist, labels, labels[vi, vj]))
    dv = dist[vi, vj] - 0.5
    if extra_px:  # chord midpoints sit half a cell inside the rim
        dv = np.concatenate([dv, np.full(len(extra_px), 0.5)])
        dmax = np.concatenate([dmax, dmax[np.array(extra_parent)]])
    dv[is_boundary] = 0.0
    h = np.sqrt(np.clip(2 * dmax * dv - dv * dv, 0, None)) * step * thickness
    if depth_path:
        depth = np.asarray(Image.open(depth_path).convert("L").resize((W, H)), np.float32) / 255.0
        dval = depth[np.clip(px[:, 1].astype(int), 0, H - 1), np.clip(px[:, 0].astype(int), 0, W - 1)]
        h = h + depth_scale * (dval - dval.min()) * dmax.max() * step * (~is_boundary)

    # Laplacian smoothing of height over the mesh graph; the rim stays at zero.
    nbr = [[] for _ in range(len(px))]
    for x, y in uniq:
        nbr[x].append(y)
        nbr[y].append(x)
    deg = np.array([len(n) for n in nbr], np.float32)
    rows = np.repeat(np.arange(len(px)), [len(n) for n in nbr])
    cols = np.concatenate([np.array(n, int) for n in nbr])
    for _ in range(smooth):
        avg = np.bincount(rows, weights=h[cols], minlength=len(px)) / np.maximum(deg, 1)
        h = np.where(is_boundary, 0.0, 0.5 * h + 0.5 * avg)

    # Front surface uses every vertex; the back duplicates interior vertices and shares the rim.
    n = len(px)
    back_index = np.arange(n)
    interior = np.nonzero(~is_boundary)[0]
    back_index[interior] = n + np.arange(len(interior))
    front_xyz = np.column_stack([px[:, 0], -px[:, 1], h])
    back_xyz = np.column_stack([px[interior, 0], -px[interior, 1], -h[interior] * back])
    verts = np.vstack([front_xyz, back_xyz])
    faces = np.vstack([tris, back_index[tris][:, ::-1]])
    uv_px = np.vstack([px, px[interior]])
    uv = np.column_stack([uv_px[:, 0] / W, 1.0 - uv_px[:, 1] / H])

    # Meters, base on y = 0, centred in x and z.
    scale = height_m / (np.ptp(verts[:, 1]) or 1.0)
    verts = verts * scale
    verts[:, 0] -= verts[:, 0].mean()
    verts[:, 1] -= verts[:, 1].min()
    verts[:, 2] -= 0.5 * (verts[:, 2].max() + verts[:, 2].min())

    # Texture: the source image with colours bled past the silhouette, capped in size.
    tex = Image.fromarray(bleed(rgba[..., :3], full_mask))
    if max(tex.size) > texture_size:
        tex.thumbnail((texture_size, texture_size), Image.LANCZOS)
    material = trimesh.visual.material.PBRMaterial(baseColorTexture=tex, metallicFactor=0.0, roughnessFactor=0.55, name="inflated")
    mesh = trimesh.Trimesh(verts, faces, visual=trimesh.visual.TextureVisuals(uv=uv, material=material), process=False)
    return mesh, {"grid": [gh, gw], "step_px": round(step, 3), "boundary_loops": len(loops), "mask_pixels": int(full_mask.sum()), "image": [W, H]}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image")
    ap.add_argument("out")
    ap.add_argument("--height", type=float, default=0.25, help="object height in meters")
    ap.add_argument("--res", type=int, default=96, help="grid samples along the longer image side")
    ap.add_argument("--thickness", type=float, default=0.6, help="inflation as a share of the local width")
    ap.add_argument("--back", type=float, default=1.0, help="back depth relative to the front")
    ap.add_argument("--depth", help="optional depth map aligned to the image (white = near)")
    ap.add_argument("--depth-scale", type=float, default=0.5)
    ap.add_argument("--smooth", type=int, default=8)
    ap.add_argument("--tolerance", type=float, default=40.0, help="background colour distance when there is no alpha")
    a = ap.parse_args()

    mesh, info = inflate(a.image, a.height, a.res, a.thickness, a.back, a.depth, a.depth_scale, a.smooth, a.tolerance)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(out)
    report = {
        "tool": "inflate3d", "input": Path(a.image).name,
        "input_sha256": hashlib.sha256(Path(a.image).read_bytes()).hexdigest(),
        "params": {k: v for k, v in vars(a).items() if k not in ("image", "out")},
        "vertices": len(mesh.vertices), "triangles": len(mesh.faces), "watertight": bool(mesh.is_watertight),
        "bbox_m": np.round(mesh.extents, 5).tolist(), **info,
    }
    out.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return 0 if mesh.is_watertight else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""remesh: reduce a mesh to a face budget with quadric error metrics, keeping it manifold and its UVs valid.

Our own stand-in for budgeted retopology (MeshAnything V2's 1,600-face meshes, Blender decimation).
It is a decimator, not a quad retopologiser: output is triangles, and edge flow is not designed for
deformation. Each step collapses an edge onto one of its existing vertices (a half-edge collapse), so
every surviving vertex keeps its original UV and no texture is resampled.

  python remesh.py in.glb out.glb --faces 1600 [--keep-boundary 1000] [--max-flip 0.2]

Rules on every collapse:
- link condition: the two vertices may share only the two opposite vertices of the edge (no pinches);
- no face may flip or turn more than the --max-flip normal threshold;
- open edges and UV seams carry a strong penalty, so silhouettes and seams stay put.
"""
import argparse
import heapq
import json
import sys
from pathlib import Path

import numpy as np
import trimesh


def plane_quadrics(v, f):
    """Area-weighted fundamental quadric per face, summed onto its vertices."""
    p0, p1, p2 = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    n = np.cross(p1 - p0, p2 - p0)
    area = np.linalg.norm(n, axis=1)
    nn = n / np.maximum(area[:, None], 1e-20)
    d = -(nn * p0).sum(1)
    plane = np.column_stack([nn, d])
    Kf = plane[:, :, None] * plane[:, None, :] * (area[:, None, None] * 0.5)
    Q = np.zeros((len(v), 4, 4))
    for k in range(3):
        np.add.at(Q, f[:, k], Kf)
    return Q, nn


def boundary_quadrics(v, f, Q, weight):
    """Penalty planes through each open edge, perpendicular to its face, so open edges resist moving."""
    e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    fid = np.tile(np.arange(len(f)), 3)
    key = np.sort(e, 1)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    open_edges = cnt[inv] == 1
    p0, p1, p2 = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    fn = np.cross(p1 - p0, p2 - p0)
    for (a, b), face in zip(e[open_edges], fid[open_edges]):
        d = v[b] - v[a]
        n = np.cross(d, fn[face])
        ln = np.linalg.norm(n)
        if ln < 1e-20:
            continue
        n /= ln
        plane = np.append(n, -n.dot(v[a]))
        K = np.outer(plane, plane) * weight * np.dot(d, d)
        Q[a] += K
        Q[b] += K
    return int(open_edges.sum())


def decimate(v, f, target, keep_boundary=1000.0, max_flip=0.2):
    v = np.asarray(v, float)
    f = np.asarray(f, int).copy()
    Q, _ = plane_quadrics(v, f)
    n_open = boundary_quadrics(v, f, Q, keep_boundary)
    alive = np.ones(len(f), bool)
    vfaces = [set() for _ in range(len(v))]
    for i, (a, b, c) in enumerate(f):
        vfaces[a].add(i); vfaces[b].add(i); vfaces[c].add(i)
    version = np.zeros(len(v), int)
    removed = np.zeros(len(v), bool)

    def neighbors(x):
        s = set()
        for fi in vfaces[x]:
            s.update(f[fi])
        s.discard(x)
        return s

    def cost(u, w):  # move u onto w
        q = Q[u] + Q[w]
        p = np.append(v[w], 1.0)
        return float(p @ q @ p)

    heap = []

    def push_vertex(x):
        for y in neighbors(x):
            heapq.heappush(heap, (cost(x, y), x, y, version[x], version[y]))
            heapq.heappush(heap, (cost(y, x), y, x, version[y], version[x]))

    for x in range(len(v)):
        for y in neighbors(x):
            if x < y:
                heapq.heappush(heap, (cost(x, y), x, y, 0, 0))
                heapq.heappush(heap, (cost(y, x), y, x, 0, 0))

    faces_left = int(alive.sum())
    while faces_left > target and heap:
        c, u, w, vu, vw = heapq.heappop(heap)
        if removed[u] or removed[w] or vu != version[u] or vw != version[w]:
            continue
        shared = vfaces[u] & vfaces[w]
        if not shared:
            continue
        # Link condition: common neighbours must be exactly the opposite vertices of the shared faces.
        opposite = {x for fi in shared for x in f[fi]} - {u, w}
        if (neighbors(u) & neighbors(w)) != opposite:
            continue
        # Flip check on faces that move.
        ok = True
        for fi in vfaces[u] - shared:
            a, b, cc = f[fi]
            old = np.cross(v[b] - v[a], v[cc] - v[a])
            pts = [v[w] if x == u else v[x] for x in (a, b, cc)]
            new = np.cross(pts[1] - pts[0], pts[2] - pts[0])
            lo, ln = np.linalg.norm(old), np.linalg.norm(new)
            if ln < 1e-20 or lo < 1e-20 or old.dot(new) / (lo * ln) < max_flip:
                ok = False
                break
        if not ok:
            continue
        for fi in shared:
            alive[fi] = False
            for x in f[fi]:
                vfaces[x].discard(fi)
        faces_left -= len(shared)
        for fi in list(vfaces[u]):
            f[fi][f[fi] == u] = w
            vfaces[w].add(fi)
        vfaces[u].clear()
        removed[u] = True
        Q[w] += Q[u]
        version[w] += 1
        for x in neighbors(w):
            version[x] += 1
        push_vertex(w)
        for x in neighbors(w):
            push_vertex(x)

    f = f[alive]
    used = np.unique(f)
    remap = -np.ones(len(v), int)
    remap[used] = np.arange(len(used))
    return used, remap[f], n_open


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--faces", type=int, default=1600)
    ap.add_argument("--keep-boundary", type=float, default=1000.0, help="penalty weight for moving open edges and seams")
    ap.add_argument("--max-flip", type=float, default=0.2, help="minimum cosine between a face's old and new normal")
    a = ap.parse_args()

    mesh = trimesh.load(a.inp, force="mesh", process=False)
    before = {"vertices": len(mesh.vertices), "faces": len(mesh.faces), "watertight": bool(mesh.is_watertight)}
    keep, faces, n_open = decimate(mesh.vertices, mesh.faces, a.faces, a.keep_boundary, a.max_flip)
    visual = None
    uv = getattr(mesh.visual, "uv", None)
    if uv is not None:
        visual = trimesh.visual.TextureVisuals(uv=uv[keep], material=mesh.visual.material)
    out_mesh = trimesh.Trimesh(mesh.vertices[keep], faces, visual=visual, process=False)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    out_mesh.export(a.out)
    report = {"tool": "remesh", "input": Path(a.inp).name, "target_faces": a.faces, "before": before,
              "after": {"vertices": len(out_mesh.vertices), "faces": len(out_mesh.faces), "watertight": bool(out_mesh.is_watertight)},
              "open_edges_in_input": n_open, "params": {"keep_boundary": a.keep_boundary, "max_flip": a.max_flip}}
    Path(a.out).with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())

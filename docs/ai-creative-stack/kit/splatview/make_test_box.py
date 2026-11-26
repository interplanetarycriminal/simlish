"""Test fixture: a 2 x 1.4 x 1.2 box with a 2x2-colour texture on every face, saved as GLB.

Usage: python make_test_box.py out/box.glb
       python make_test_box.py --vertex-sphere out/vc_sphere.glb

Texture (image rows top to bottom): red | green, then blue | yellow; 32 px
blocks, 64 px image. Each face maps the whole texture with UV (0, 0) at the
face's lower-left corner seen from outside, v up. QUADRANTS_PLUS_Z lists the
colour expected in each quarter of the +Z face.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image

COLORS = {"red": (230, 30, 30), "green": (30, 200, 40), "blue": (30, 50, 230), "yellow": (240, 220, 30)}
HALF = np.array([1.0, 0.7, 0.6])
# image quadrant -> colour: top-left, top-right, bottom-left, bottom-right
LAYOUT = [["red", "green"], ["blue", "yellow"]]
# For the +Z face (u along +X, v along +Y): u<.5,v>.5 top-left red; u>.5,v>.5 green;
# u<.5,v<.5 blue; u>.5,v<.5 yellow.
QUADRANTS_PLUS_Z = {"x<0,y>0": "red", "x>0,y>0": "green", "x<0,y<0": "blue", "x>0,y<0": "yellow"}


def texture(block=32):
    img = np.zeros((2 * block, 2 * block, 3), np.uint8)
    for r in range(2):
        for c in range(2):
            img[r * block:(r + 1) * block, c * block:(c + 1) * block] = COLORS[LAYOUT[r][c]]
    return Image.fromarray(img, "RGB")


def box_mesh():
    # each face: origin corner, u axis, v axis (outward normal = u x v)
    faces = [
        ((-1, -1, 1), (1, 0, 0), (0, 1, 0)),    # +Z
        ((1, -1, -1), (-1, 0, 0), (0, 1, 0)),   # -Z
        ((1, -1, 1), (0, 0, -1), (0, 1, 0)),    # +X
        ((-1, -1, -1), (0, 0, 1), (0, 1, 0)),   # -X
        ((-1, 1, 1), (1, 0, 0), (0, 0, -1)),    # +Y
        ((-1, -1, -1), (1, 0, 0), (0, 0, 1)),   # -Y
    ]
    V, F, UV = [], [], []
    for o, u, v in faces:
        o, u, v = (np.array(a, float) for a in (o, u, v))
        base = len(V)
        for (a, b) in ((0, 0), (1, 0), (1, 1), (0, 1)):
            V.append((o + 2 * a * u + 2 * b * v) * HALF)
            UV.append((a, b))
        F += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    V, F, UV = np.array(V), np.array(F), np.array(UV, float)
    mat = trimesh.visual.material.PBRMaterial(baseColorTexture=texture(), baseColorFactor=[255, 255, 255, 255],
                                              metallicFactor=0.0, roughnessFactor=0.8)
    vis = trimesh.visual.TextureVisuals(uv=UV, material=mat)
    return trimesh.Trimesh(vertices=V, faces=F, visual=vis, process=False)


def vertex_colour_sphere():
    """Icosphere, radius 0.5: vertex colours red where y > 0, blue where y <= 0."""
    m = trimesh.creation.icosphere(subdivisions=3, radius=0.5)
    vc = np.where(m.vertices[:, 1:2] > 0, [[230, 30, 30, 255]], [[30, 50, 230, 255]]).astype(np.uint8)
    m.visual = trimesh.visual.ColorVisuals(m, vertex_colors=vc)
    return m


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--vertex-sphere":
        out = Path(sys.argv[2])
        out.parent.mkdir(parents=True, exist_ok=True)
        vertex_colour_sphere().export(out)
        print(json.dumps({"output": str(out)}))
        return
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "out/box.glb")
    out.parent.mkdir(parents=True, exist_ok=True)
    m = box_mesh()
    assert np.allclose(m.face_normals[0], [0, 0, 1]), "winding check failed"
    m.export(out)
    meta = {"half_extents": HALF.tolist(), "colors": COLORS, "plus_z_quadrants": QUADRANTS_PLUS_Z,
            "area": float(m.area)}
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(out), "faces": int(len(m.faces))}))


if __name__ == "__main__":
    main()

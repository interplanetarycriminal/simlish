#!/usr/bin/env python3
"""Test inflate3d on a drawn toy fish and an alpha-free variant. Writes out/result.json."""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image
from skimage.draw import polygon as fill_polygon

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
ROOT = HERE.parents[1]
BLENDER = os.environ.get("BLENDER", "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe")
sys.path.insert(0, str(HERE))
from make_toy import draw_fish  # noqa: E402


def silhouette_iou(mesh, mask, height_px):
    """Rasterise the mesh's front projection and compare it with the image mask."""
    v = mesh.vertices
    scale = height_px / np.ptp(v[:, 1])
    xs = (v[:, 0] - v[:, 0].min()) * scale
    ys = (v[:, 1].max() - v[:, 1]) * scale
    h, w = int(np.ceil(ys.max())) + 2, int(np.ceil(xs.max())) + 2
    raster = np.zeros((h, w), bool)
    for f in mesh.faces[: len(mesh.faces) // 2]:  # the front sheet covers the silhouette
        rr, cc = fill_polygon(ys[f], xs[f], raster.shape)
        raster[rr, cc] = True
    rows, cols = np.nonzero(mask)
    crop = mask[rows.min(): rows.max() + 1, cols.min(): cols.max() + 1]
    target = np.array(Image.fromarray(crop.astype(np.uint8) * 255).resize((w - 2, h - 2), Image.NEAREST)) > 0
    raster = raster[: h - 2, : w - 2]
    return float((raster & target).sum() / (raster | target).sum())


def run(args):
    r = subprocess.run([sys.executable, str(HERE / "inflate3d.py"), *args], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr)
    return r.returncode


def main():
    OUT.mkdir(exist_ok=True)
    checks = {}
    img = draw_fish(512)
    img.save(OUT / "toy_fish.png")
    mask = np.asarray(img)[..., 3] > 127

    checks["runs"] = run([str(OUT / "toy_fish.png"), str(OUT / "toy_fish.glb"), "--height", "0.2"]) == 0
    mesh = trimesh.load(OUT / "toy_fish.glb", force="mesh")
    checks["watertight"] = bool(mesh.is_watertight)
    checks["volume_positive"] = bool(mesh.volume > 0)
    checks["height_m"] = abs(mesh.extents[1] - 0.2) < 0.002
    checks["has_texture"] = getattr(mesh.visual, "uv", None) is not None and mesh.visual.material.baseColorTexture is not None
    checks["uv_in_range"] = bool(((mesh.visual.uv >= -1e-6) & (mesh.visual.uv <= 1 + 1e-6)).all())
    iou = silhouette_iou(mesh, mask, 400)
    checks["silhouette_iou>0.9"] = iou > 0.9

    # No alpha: a white background is keyed out by colour distance.
    flat = Image.new("RGB", img.size, (255, 255, 255))
    flat.paste(img, mask=img.split()[3])
    flat.save(OUT / "toy_fish_flat.jpg", quality=92)
    checks["keys_flat_background"] = run([str(OUT / "toy_fish_flat.jpg"), str(OUT / "toy_fish_flat.glb")]) == 0

    # The catalogue's Blender validator must pass the GLB's Floor checks.
    validator = ROOT / "scripts" / "blender" / "validate_asset.py"
    blender_ok, reflex = None, None
    if Path(BLENDER).exists():
        r = subprocess.run([BLENDER, "--background", "--factory-startup", "--python-exit-code", "1", "--python", str(validator), "--",
                            str(OUT / "toy_fish.glb"), str(OUT / "validate.json")], capture_output=True, text=True)
        blender_ok = r.returncode == 0
        reflex = json.loads((OUT / "validate.json").read_text())["reflex"]
        checks["blender_floor_checks"] = blender_ok
    (OUT / "toy_fish_flat.glb").unlink(missing_ok=True)
    (OUT / "toy_fish_flat.json").unlink(missing_ok=True)

    checks = {k: bool(v) for k, v in checks.items()}
    result = {"tool": "inflate3d", "checks": checks, "silhouette_iou": round(iou, 4), "triangles": len(mesh.faces),
              "extents_m": np.round(mesh.extents, 4).tolist(), "blender_reflex": reflex, "pass": all(checks.values())}
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for k, v in checks.items():
        print(("PASS " if v else "FAIL ") + k)
    print(f"IoU {iou:.3f}, {len(mesh.faces)} triangles")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

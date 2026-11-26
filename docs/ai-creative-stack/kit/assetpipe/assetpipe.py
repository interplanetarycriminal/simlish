#!/usr/bin/env python3
"""assetpipe: run a reviewed 3D asset workflow over a batch of images, with a manifest per asset.

Our own stand-in for ComfyUI-3D-Pack used as a repeatable batch pipeline. Instead of a node graph,
a workflow is a JSON list of steps that call the kit's tools as separate processes. Each step's
parameters, tool version, inputs and outputs (with SHA-256) are recorded, every stage is a separate
versioned file, and an asset that fails validation is rejected with the reason.

  python assetpipe.py run workflows/toy-factory.json img1.png img2.png ... --out out/batch

Step types: inflate (kit/inflate3d), remesh (kit/remesh), autorig (kit/autorig, Blender),
validate (scripts/blender/validate_asset.py, Blender), mesh2splat (kit/splatview, optional).
A step's "input" names an earlier step whose output it consumes (default: the previous step).
"optional": true lets the asset continue when that step's tool is missing or fails, and marks the step
as a side output: it never becomes the input of the next step or the asset's delivery version.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
ROOT = KIT.parent
BLENDER = os.environ.get("BLENDER", "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def blender(script, *args):
    return [BLENDER, "--background", "--factory-startup", "--python-exit-code", "1", "--python", str(script), "--", *map(str, args)]


def command(step, src, out_dir, asset):
    """Return (argv, primary output path) for a step."""
    p = step.get("params", {})
    kind = step["run"]
    flags = [x for k, v in p.items() for x in (f"--{k.replace('_', '-')}", str(v))]
    if kind == "inflate":
        dst = out_dir / f"{asset}.v1-original.glb"
        return [sys.executable, str(KIT / "inflate3d/inflate3d.py"), str(src), str(dst), *flags], dst
    if kind == "remesh":
        dst = out_dir / f"{asset}.v2-retopo.glb"
        return [sys.executable, str(KIT / "remesh/remesh.py"), str(src), str(dst), *flags], dst
    if kind == "autorig":
        rig_dir = out_dir / "rig"
        dst = rig_dir / f"{Path(src).stem}_rigged.glb"
        return blender(KIT / "autorig/autorig.py", src, rig_dir, *flags), dst
    if kind == "validate":
        dst = out_dir / f"{asset}.validation.json"
        return blender(ROOT / "scripts/blender/validate_asset.py", src, dst), dst
    if kind == "mesh2splat":
        dst = out_dir / f"{asset}.splat.ply"
        return [sys.executable, str(KIT / "splatview/mesh2splat.py"), str(src), str(dst), *flags], dst
    raise SystemExit(f"Unknown step type: {kind}")


def run_asset(workflow, image, out_root):
    asset = Path(image).stem
    out_dir = out_root / asset
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)
    outputs = {"input": Path(image)}
    prev = "input"
    stages, status, reason = [], "accepted", None
    for step in workflow["steps"]:
        src = outputs[step.get("input", prev)]
        argv, dst = command(step, src, out_dir, asset)
        t0 = time.time()
        tool = Path(argv[1]) if argv[0] == sys.executable else Path(argv[6])
        tool_missing = not tool.exists() or (argv[0] == BLENDER and not Path(BLENDER).exists())
        r = None if tool_missing else subprocess.run(argv, capture_output=True, text=True)
        ok = r is not None and r.returncode == 0 and Path(dst).exists()
        stage = {"version": step["id"], "run": step["run"], "consumes": None if step.get("input", prev) == "input" else step.get("input", prev),
                 "params": step.get("params", {}), "input": Path(src).name, "input_sha256": sha(src) if Path(src).exists() else None,
                 "output": str(Path(dst).relative_to(out_root)) if ok else None, "output_sha256": sha(dst) if ok else None,
                 "seconds": round(time.time() - t0, 2), "ok": ok}
        if not ok:
            stage["error"] = "tool not installed" if tool_missing else (r.stderr or r.stdout)[-400:]
        if step["run"] == "validate" and ok:
            report = json.loads(Path(dst).read_text())
            stage["floor"], stage["reflex"] = report["floor"], report["reflex"]
            if not report["pass"]:
                ok = False
                stage["ok"] = False
                stage["error"] = "Floor checks failed: " + ", ".join(k for k, v in report["floor"].items() if not v)
        stages.append(stage)
        if not ok and not step.get("optional"):
            status, reason = "rejected", f"{step['id']}: {stage.get('error', 'failed')}".strip()
            break
        if ok:
            outputs[step["id"]] = dst
            # Validation and optional side outputs never advance the main chain or become the delivery.
            if step["run"] != "validate" and not step.get("optional"):
                prev = step["id"]
    manifest = {
        "asset_id": asset, "workflow": {"name": workflow["name"], "version": workflow["version"]},
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"), "status": status, "reason": reason,
        "source_references": [{"path": Path(image).name, "sha256": sha(image)}],
        "coordinate_system": {"delivery": "glTF, right-handed, Y up", "units": "meters"},
        "stages": stages,
        "delivery": {"version": prev if status == "accepted" else None},
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("workflow")
    r.add_argument("images", nargs="+")
    r.add_argument("--out", default="out/batch")
    a = ap.parse_args()
    workflow = json.loads(Path(a.workflow).read_text(encoding="utf-8"))
    out_root = Path(a.out)
    out_root.mkdir(parents=True, exist_ok=True)
    results = [run_asset(workflow, img, out_root) for img in a.images]
    summary = {"workflow": workflow["name"], "assets": len(results),
               "accepted": [m["asset_id"] for m in results if m["status"] == "accepted"],
               "rejected": {m["asset_id"]: m["reason"] for m in results if m["status"] == "rejected"}}
    (out_root / "batch.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())

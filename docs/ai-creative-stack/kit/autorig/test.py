#!/usr/bin/env python3
"""Test autorig on the inflated, remeshed toy fish: rig, validate in Blender, then load and seek in Three.js."""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
ROOT = HERE.parents[1]
BLENDER = os.environ.get("BLENDER", "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe")
sys.path.insert(0, str(ROOT / "kit" / "inflate3d"))
from make_toy import draw_fish  # noqa: E402

CHECK_JS = r"""
import { launch, open, evaluate, screenshot, serve } from '../../fixtures/lib/cdp.mjs';
import { writeFileSync } from 'node:fs';
const [file, bone, out] = process.argv.slice(2);
const server = await serve(process.cwd());
const cdp = await launch(undefined, { width: 520, height: 420 });
await open(cdp, `http://127.0.0.1:${server.address().port}/fixtures/blender-glb/viewer.html?file=${encodeURIComponent(file)}&bone=${bone}`);
const stats = await evaluate(cdp, 'window.__asset.stats');
const tips = [];
const shots = [];
for (const t of [0, 0.5, 1.0, 1.5]) { tips.push(await evaluate(cdp, `window.__asset.seek(${t}, 0.6)`)); shots.push(await screenshot(cdp)); }
const again = await evaluate(cdp, 'window.__asset.seek(0.5, 0.6)');
shots.forEach((s, i) => writeFileSync(`${out}-${i}.png`, s));
console.log(JSON.stringify({ stats, tips, again }));
await cdp.close(); server.close();
"""


def blender(*args):
    return subprocess.run([BLENDER, "--background", "--factory-startup", "--python-exit-code", "1", "--python", *args],
                          capture_output=True, text=True)


def main():
    OUT.mkdir(exist_ok=True)
    checks = {}
    draw_fish(512).save(OUT / "toy_fish.png")
    subprocess.run([sys.executable, str(ROOT / "kit/inflate3d/inflate3d.py"), str(OUT / "toy_fish.png"), str(OUT / "fish.glb"), "--height", "0.2"], check=True, capture_output=True)
    subprocess.run([sys.executable, str(ROOT / "kit/remesh/remesh.py"), str(OUT / "fish.glb"), str(OUT / "fish_lo.glb"), "--faces", "2400"], check=True, capture_output=True)

    r = blender(str(HERE / "autorig.py"), "--", str(OUT / "fish_lo.glb"), str(OUT), "--bones", "4", "--anim", "swim")
    checks["rig_runs"] = r.returncode == 0
    rig = json.loads((OUT / "fish_lo_rigged.rig.json").read_text())
    joints = np.array(rig["joints_m"])
    checks["four_bones"] = rig["bones"] == 4 and len(joints) == 5
    checks["chain_along_length"] = abs(rig["axis"][0]) > 0.9  # the fish is long in x
    lengths = np.array(rig["bone_lengths_m"])
    checks["even_bone_lengths"] = lengths.max() / lengths.min() < 1.6
    checks["root_at_head"] = joints[0][0] < joints[-1][0]  # the drawn fish faces left, so the head is at lower x

    r = blender(str(ROOT / "scripts/blender/validate_asset.py"), "--", str(OUT / "fish_lo_rigged.glb"), str(OUT / "validate.json"))
    report = json.loads((OUT / "validate.json").read_text())
    checks["blender_floor_checks"] = r.returncode == 0
    checks["weights_normalised_max4"] = all(x["non_normalised_vertices"] == 0 and x["vertices_over_4_influences"] == 0 and x["unweighted_vertices"] == 0 for x in report["rigs"])
    checks["clip_exported"] = any(a["name"] == "swim" for a in report["animations"])

    (ROOT / "kit/autorig/_check.mjs").write_text(CHECK_JS, encoding="utf-8")
    r = subprocess.run(["node", "kit/autorig/_check.mjs", "../../kit/autorig/out/fish_lo_rigged.glb", "seg_3", str(OUT / "three")],
                       cwd=ROOT, capture_output=True, text=True)
    (ROOT / "kit/autorig/_check.mjs").unlink(missing_ok=True)
    three = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else {}
    stats = three.get("stats", {})
    tips = np.array([p for p in three.get("tips", []) if p], float)
    checks["three_loads_skinned"] = stats.get("skinnedMeshes") == 1 and len(stats.get("bones", [])) == 4
    checks["three_clip"] = any(a["name"] == "swim" for a in stats.get("animations", []))
    swing = float(np.ptp(tips[:, 2])) if len(tips) else 0.0  # the tail swings in depth (glTF z)
    checks["tail_swings>1cm"] = swing > 0.01
    checks["seek_repeatable"] = three.get("again") == (three.get("tips") or [None, None])[1]
    if r.returncode == 0:
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *sum([["-i", str(OUT / f"three-{i}.png")] for i in range(4)], []),
                        "-filter_complex", "hstack=4", str(OUT / "swim-sheet.png")], check=True)
        for i in range(4):
            (OUT / f"three-{i}.png").unlink(missing_ok=True)

    for n in ("toy_fish.png", "fish.glb", "fish.json", "fish_lo.json", "fish_lo_rigged.fbx"):
        (OUT / n).unlink(missing_ok=True)
    checks = {k: bool(v) for k, v in checks.items()}
    result = {"tool": "autorig", "checks": checks, "rig": rig, "tail_swing_m": round(swing, 4), "three_stats": stats, "pass": all(checks.values())}
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for k, v in checks.items():
        print(("PASS " if v else "FAIL ") + k)
    print("tail swing", round(swing, 4), "m; bone lengths", rig["bone_lengths_m"])
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

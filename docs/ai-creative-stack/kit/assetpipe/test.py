#!/usr/bin/env python3
"""Test assetpipe: a batch of two toys and one empty image, run twice to prove repeatability."""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
KIT = HERE.parent
sys.path.insert(0, str(KIT / "inflate3d"))
from make_toy import draw_fish, draw_rocket  # noqa: E402


def batch(dest):
    imgs = [OUT / "inputs" / n for n in ("fish.png", "rocket.png", "empty.png")]
    r = subprocess.run([sys.executable, str(HERE / "assetpipe.py"), "run", str(HERE / "workflows/toy-factory.json"), *map(str, imgs), "--out", str(dest)],
                       capture_output=True, text=True)
    return r.returncode, json.loads((dest / "batch.json").read_text())


def stage(manifest, version):
    return next((s for s in manifest["stages"] if s["version"] == version), None)


def main():
    (OUT / "inputs").mkdir(parents=True, exist_ok=True)
    draw_fish(512).save(OUT / "inputs/fish.png")
    draw_rocket(512).save(OUT / "inputs/rocket.png")
    Image.new("RGBA", (256, 256), (0, 0, 0, 0)).save(OUT / "inputs/empty.png")

    code, summary = batch(OUT / "batch")
    checks = {"runs": code == 0,
              "two_accepted": sorted(summary["accepted"]) == ["fish", "rocket"],
              "empty_rejected_with_reason": "empty" in summary["rejected"] and "v1-original" in summary["rejected"]["empty"]}
    manifests = {n: json.loads((OUT / "batch" / n / "manifest.json").read_text()) for n in ("fish", "rocket", "empty")}
    for n in ("fish", "rocket"):
        m = manifests[n]
        rig = stage(m, "v3-rigged")
        checks[f"{n}_stages_versioned"] = all(stage(m, v) and stage(m, v)["ok"] for v in ("v1-original", "v2-retopo", "check-geometry", "v3-rigged", "check-rig"))
        checks[f"{n}_consumes_chain"] = stage(m, "v2-retopo")["consumes"] == "v1-original" and rig["consumes"] == "v2-retopo"
        checks[f"{n}_hashes_recorded"] = all(s["output_sha256"] for s in m["stages"] if s["ok"])
        checks[f"{n}_rig_floor_pass"] = all(stage(m, "check-rig")["floor"].values())
        checks[f"{n}_delivery_is_rig"] = m["delivery"]["version"] == "v3-rigged"

    # Repeatability: a second run gives byte-identical geometry stages.
    _, _ = batch(OUT / "batch2")
    again = json.loads((OUT / "batch2/fish/manifest.json").read_text())
    for v in ("v1-original", "v2-retopo"):
        checks[f"repeatable_{v}"] = stage(manifests["fish"], v)["output_sha256"] == stage(again, v)["output_sha256"]
    splat = stage(manifests["fish"], "splat")
    import shutil
    shutil.rmtree(OUT / "batch2", ignore_errors=True)
    for pattern in ("*.fbx", "*.splat.ply"):  # keep the committed evidence small; hashes stay in the manifests
        for p in (OUT / "batch").rglob(pattern):
            p.unlink()

    checks = {k: bool(v) for k, v in checks.items()}
    result = {"tool": "assetpipe", "summary": summary, "splat_step": {"ok": splat["ok"], "error": splat.get("error")} if splat else None,
              "checks": checks, "pass": all(checks.values())}
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for k, v in checks.items():
        print(("PASS " if v else "FAIL ") + k)
    print(json.dumps(summary), "splat:", result["splat_step"])
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

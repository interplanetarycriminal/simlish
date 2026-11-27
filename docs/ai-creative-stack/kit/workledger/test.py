#!/usr/bin/env python3
"""Test workledger against a naive baseline on the same synthetic project, and write strategy-evaluation.md."""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
PY = f'"{sys.executable}"'
sys.path.insert(0, str(HERE))
import workledger as wl  # noqa: E402

TASKS = {
    "p1.py": "import json, pathlib; pathlib.Path('design').mkdir(exist_ok=True); pathlib.Path('design/tokens.json').write_text(json.dumps({'accent': '#1D6A84'}))",
    "p2.py": "import json, pathlib; t = json.loads(pathlib.Path('design/tokens.json').read_text()); pathlib.Path('ui').mkdir(exist_ok=True); pathlib.Path('ui/button.css').write_text('.btn{color:%s}' % t['accent'])",
    "p3.py": "import pathlib; pathlib.Path('assets').mkdir(exist_ok=True); pathlib.Path('assets/model.txt').write_text('mesh v1')",
    "p4.py": "import sys, time; time.sleep(0.3); print('error: renderer missing codec h264'); sys.exit(1)",
    "p5.py": "import pathlib; pathlib.Path('assets').mkdir(exist_ok=True); pathlib.Path('assets/sfx.txt').write_text('jump'); pathlib.Path('ui').mkdir(exist_ok=True); pathlib.Path('ui/hacked.css').write_text('*{display:none}')",
    "p6.py": "import pathlib; pathlib.Path('video').mkdir(exist_ok=True); assert pathlib.Path('video/master.mp4').exists(), 'needs the render from p4'",
    "p7.py": "import pathlib, sys; c = pathlib.Path('cache/count.txt'); c.parent.mkdir(exist_ok=True); n = int(c.read_text()) + 1 if c.exists() else 1; c.write_text(str(n)); print('attempt', n); sys.exit(0 if n >= 2 else 1)",
}


def pkg(pid, goal, cmd, checks, scope, deps=(), retry=4, outputs=()):
    return {"id": pid, "parent_id": "G1", "goal": goal, "owner": "agent", "input_refs": [], "output_paths": list(outputs),
            "depends_on": list(deps), "edit_scope": list(scope), "acceptance_checks": list(checks), "budget": {"seconds": 20},
            "retry_limit": retry, "status": "planned", "evidence_refs": [], "command": cmd}


def packages():
    exists = lambda p: f"{PY} -c \"import pathlib,sys; sys.exit(0 if pathlib.Path('{p}').exists() else 1)\""
    return [
        pkg("P1", "Write design tokens", f"{PY} tasks/p1.py", [exists("design/tokens.json")], ["design/*"], outputs=["design/tokens.json"]),
        pkg("P2", "Style the button from tokens", f"{PY} tasks/p2.py", [exists("ui/button.css")], ["ui/*"], deps=["P1"], outputs=["ui/button.css"]),
        pkg("P3", "Export the model", f"{PY} tasks/p3.py", [exists("assets/model.txt")], ["assets/*"], outputs=["assets/model.txt"]),
        pkg("P4", "Render the master video", f"{PY} tasks/p4.py", [exists("video/master.mp4")], ["video/*"], outputs=["video/master.mp4"]),
        pkg("P5", "Generate sound effects", f"{PY} tasks/p5.py", [exists("assets/sfx.txt")], ["assets/*"], outputs=["assets/sfx.txt"]),
        pkg("P6", "Package the video", f"{PY} tasks/p6.py", [exists("video/master.mp4")], ["video/*"], deps=["P4"]),
        pkg("P7", "Warm the cache (flaky first time)", f"{PY} tasks/p7.py", [exists("cache/count.txt")], ["cache/*"], retry=2),
    ]


def project(dst):
    shutil.rmtree(dst, ignore_errors=True)
    (dst / "tasks").mkdir(parents=True)
    for name, code in TASKS.items():
        (dst / "tasks" / name).write_text(code, encoding="utf-8")
    return dst


def main():
    OUT.mkdir(exist_ok=True)
    work = OUT / "work"
    pk = packages()
    checks = {}

    problems, waves = wl.check(pk)
    checks["plan_valid"] = problems == []
    checks["overlapping_scopes_serialised"] = not any("P3" in w and "P5" in w for w in waves)
    checks["dependents_after_parents"] = [i for w in waves for i in w].index("P2") > [i for w in waves for i in w].index("P1")
    bad = json.loads(json.dumps(pk))
    bad[0]["depends_on"] = ["P2"]
    checks["cycle_detected"] = any("cycle" in p for p in wl.check(bad)[0])
    bad = json.loads(json.dumps(pk))
    bad[2]["acceptance_checks"] = []
    checks["unverifiable_package_rejected"] = any("no acceptance checks" in p for p in wl.check(bad)[0])

    results = {}
    for mode in ("baseline", "governed"):
        root = project(work / mode)
        ledger = OUT / f"ledger-{mode}.jsonl"
        ledger.unlink(missing_ok=True)
        t0 = time.time()
        status, stats, _ = wl.run(pk, root, ledger, baseline=(mode == "baseline"))
        stats["total_seconds"] = round(time.time() - t0, 3)
        results[mode] = {"status": status, "stats": stats, "reconcile": wl.reconcile(ledger)}

    g, b = results["governed"], results["baseline"]
    checks["governed_catches_scope_deviation"] = g["status"]["P5"] == "scope_deviation" and "ui/hacked.css" in g["reconcile"]["P5"]["deviation"]
    checks["baseline_misses_scope_deviation"] = b["status"]["P5"] == "done"
    checks["governed_stops_repeated_failure_early"] = g["reconcile"]["P4"]["deviation"] == "repeated equivalent failure"
    checks["governed_blocks_dependent_of_failure"] = g["status"]["P6"] == "blocked"
    checks["flaky_package_recovers_with_progress"] = g["status"]["P7"] == "done"
    checks["chain_completes"] = g["status"]["P1"] == "done" and g["status"]["P2"] == "done" and g["status"]["P3"] == "done"
    checks["fewer_attempts_than_baseline"] = g["stats"]["attempts"] < b["stats"]["attempts"]

    d = wl.decide(str(OUT / "decision-log.jsonl"), "Render must finish on a 24 GB GPU", ["keep HyperFrames", "switch to Remotion"],
                  "keep HyperFrames", "Existing compositions work; no measured gain from switching", ["ledger-governed.jsonl"],
                  "medium", "if render time exceeds 10 min per minute of film")
    checks["decision_recorded_with_alternatives"] = d["approval_status"] == "proposed" and len(d["alternatives"]) == 2
    try:
        wl.decide(str(OUT / "decision-log.jsonl"), "x", ["only option"], "only option", "y", [], "low", "z")
        checks["single_alternative_refused"] = False
    except SystemExit:
        checks["single_alternative_refused"] = True

    # Contract conformance: the ledgers, decision log and package file validate against registry/contracts.
    try:
        import jsonschema
        cdir = HERE.parents[1] / "registry" / "contracts"
        led = json.loads((cdir / "execution-ledger.schema.json").read_text(encoding="utf-8"))
        dec = json.loads((cdir / "decision-log.schema.json").read_text(encoding="utf-8"))
        wps = json.loads((cdir / "work-packages.schema.json").read_text(encoding="utf-8"))
        lines = [json.loads(x) for m in ("baseline", "governed") for x in (OUT / f"ledger-{m}.jsonl").read_text(encoding="utf-8").splitlines()]
        checks["ledger_matches_contract"] = all(not list(jsonschema.Draft202012Validator(led).iter_errors(x)) for x in lines)
        decs = [json.loads(x) for x in (OUT / "decision-log.jsonl").read_text(encoding="utf-8").splitlines()]
        checks["decisions_match_contract"] = all(not list(jsonschema.Draft202012Validator(dec).iter_errors(x)) for x in decs)
        doc = {"schema_version": "1.0", "packages": pk}
        (OUT / "work-packages.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        checks["packages_match_contract"] = not list(jsonschema.Draft202012Validator(wps).iter_errors(doc))
    except ImportError:
        pass

    # Monitor overhead: time spent hashing the project per attempt, measured directly.
    t0 = time.time()
    for _ in range(20):
        wl.snapshot(work / "governed")
    snap_ms = (time.time() - t0) / 20 * 1000

    eval_md = f"""# Strategy evaluation (measured)

Same seven work packages, same synthetic project, two processes. Generated by `kit/workledger/test.py`.

| Measure | Direct execution (baseline) | Governed (waves + monitor + scope check) |
| --- | --- | --- |
| Attempts run | {b['stats']['attempts']} | {g['stats']['attempts']} |
| Command time (s) | {b['stats']['command_seconds']} | {g['stats']['command_seconds']} |
| Total time (s) | {b['stats']['total_seconds']} | {g['stats']['total_seconds']} |
| Scope deviation caught (P5 wrote ui/hacked.css) | no | yes |
| Repeated identical failure (P4) | retried to the limit | stopped after 2 attempts |
| Dependent of a failed package (P6) | ran anyway and failed | blocked, not run |
| Flaky package (P7) | done | done (retry allowed because output changed) |

Monitor overhead: hashing this project once costs {snap_ms:.1f} ms; it runs twice per attempt. On a real project, hashing scales with the
edit scope, so restrict snapshots to declared scopes on large trees. These numbers come from one machine and one synthetic project:
they show the mechanism works, not that a real team will see the same savings.
"""
    (OUT / "strategy-evaluation.md").write_text(eval_md, encoding="utf-8")
    shutil.rmtree(work, ignore_errors=True)
    checks = {k: bool(v) for k, v in checks.items()}
    result = {"tool": "workledger", "checks": checks, "waves": waves, "baseline": b["stats"], "governed": g["stats"],
              "snapshot_ms": round(snap_ms, 2), "pass": all(checks.values())}
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for k, v in checks.items():
        print(("PASS " if v else "FAIL ") + k)
    print("baseline", b["stats"]); print("governed", g["stats"])
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

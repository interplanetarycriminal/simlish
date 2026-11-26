#!/usr/bin/env python3
"""Run every kit tool's test and write kit/results.json.

  python kit/run-tests.py [tool ...]

Each test builds its own fixtures, writes kit/<tool>/out/result.json with "pass", and exits 0 on pass.
Tests that need Blender, Chrome or FFmpeg find them the same way the tools do (BLENDER and CHROME env vars).
"""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

KIT = Path(__file__).resolve().parent
ORDER = ["inflate3d", "remesh", "autorig", "materialforge", "splatview", "assetpipe", "designlint", "tokenextract",
         "framecap", "silencecut", "sketchy", "projectgraph", "decisionlog", "specflow"]


def main():
    only = sys.argv[1:] or ORDER
    results = {}
    for tool in only:
        folder = KIT / tool
        test = next((folder / n for n in ("test.py", "test.mjs") if (folder / n).exists()), None)
        if not test:
            results[tool] = {"pass": False, "error": "no test"}
            continue
        argv = [sys.executable, test.name] if test.suffix == ".py" else ["node", test.name]
        t0 = time.time()
        r = subprocess.run(argv, cwd=folder, capture_output=True, text=True)
        rec = {"pass": r.returncode == 0, "seconds": round(time.time() - t0, 1)}
        res = folder / "out" / "result.json"
        if res.exists():
            data = json.loads(res.read_text(encoding="utf-8"))
            rec["recorded_pass"] = data.get("pass")
            checks = data.get("checks")
            if isinstance(checks, dict):
                rec["checks"] = f"{sum(bool(v) for v in checks.values())}/{len(checks)}"
            elif isinstance(checks, list):
                rec["checks"] = f"{sum(bool(c.get('pass', c.get('ok'))) for c in checks)}/{len(checks)}"
        if r.returncode != 0:
            rec["tail"] = (r.stdout + r.stderr)[-600:]
        results[tool] = rec
        print(f"{'PASS' if rec['pass'] else 'FAIL'}  {tool:14} {rec.get('checks', ''):>7}  {rec['seconds']} s", flush=True)
    summary = {"date": datetime.now(timezone.utc).isoformat(timespec="seconds"), "passed": sum(r["pass"] for r in results.values()),
               "total": len(results), "results": results}
    if not sys.argv[1:]:
        (KIT / "results.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"{summary['passed']}/{summary['total']} kit tests passed")
    return 0 if summary["passed"] == summary["total"] else 1


if __name__ == "__main__":
    sys.exit(main())

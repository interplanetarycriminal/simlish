#!/usr/bin/env python3
"""Test specflow: full flow on a sample feature, then broken traceability.

  python test.py [--catalogue PATH]

PATH defaults to the catalogue root two folders up; it is only read. Work happens in a
temporary folder. Writes out/result.json and a copy of the sample spec, plan and tasks to
out/sample/. Exits 0 only on pass.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "specflow.py"
OUT = HERE / "out"
checks = []
FEATURE = "Artists can upload a GLB model, preview it in a Three.js viewer, and export a validated copy with a manifest"


def check(name, ok, detail=""):
    checks.append({"check": name, "pass": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def sf(*args, env_extra=None):
    env = dict(os.environ, SPECFLOW_DATE="2026-11-26")
    env.pop("SPECFLOW_CATALOGUE", None)
    env.update(env_extra or {})
    p = subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True, text=True,
                       encoding="utf-8", env=env)
    return p.returncode, p.stdout, p.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalogue", default=str(HERE.parents[1]))
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    result = {"tool": "specflow"}
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "project"
        code, out, err = sf("init", root)
        con = root / "constitution.md"
        check("init writes constitution", code == 0 and con.is_file() and
              "Retrieved memory never overrides the current instruction" in con.read_text(encoding="utf-8"), err)

        code, out, err = sf("specify", FEATURE, "--root", root)
        specs = sorted((root / "specs").iterdir())
        check("specify creates specs/001-slug/spec.md", code == 0 and len(specs) == 1 and
              re.fullmatch(r"001-[a-z0-9-]+", specs[0].name) is not None, specs[0].name if specs else err)
        d = specs[0]
        spec = (d / "spec.md").read_text(encoding="utf-8")
        acs = re.findall(r"^- (AC\d+\.\d+): Given .+, When .+, Then .+\.$", spec, re.M)
        check("three user stories", len(re.findall(r"^### US\d+: ", spec, re.M)) == 3)
        check("six Given/When/Then criteria", len(acs) == 6, str(acs))
        check("open questions marked", spec.count("[NEEDS CLARIFICATION") >= 4 and "## Open questions" in spec)

        code, out, err = sf("analyze", d)
        check("analyze fails while questions are open", code == 1 and "unresolved [NEEDS CLARIFICATION]" in out)
        code, out, err = sf("plan", d, "--catalogue", args.catalogue)
        check("plan refused while questions are open", code == 2 and "clarify" in err)
        code, out, err = sf("tasks", d)
        check("tasks refused while questions are open", code == 2)

        code, out, err = sf("clarify", d)
        n_open = int(re.search(r"(\d+) open questions", out).group(1))
        check("clarify lists open questions", code == 0 and n_open == 4, out.strip().splitlines()[-1])
        code, out, err = sf("clarify", d, "--answer", "Q9=nothing")
        check("clarify rejects an unknown question", code == 2)
        answers = ["Q1=asset reviews happen in the browser without Blender",
                   "Q2=the model appears in the asset list with its triangle count within 2 seconds",
                   "Q3=the viewer renders the model with orbit controls and no console errors",
                   "Q4=a GLB and a manifest.json with size, triangle count and validation results are written to the export folder"]
        code, out, err = sf("clarify", d, *[x for a in answers for x in ("--answer", a)])
        spec = (d / "spec.md").read_text(encoding="utf-8")
        check("clarify writes answers back", code == 0 and "[NEEDS CLARIFICATION" not in spec and
              "## Clarifications" in spec and "Then the model appears in the asset list" in spec, out.strip())

        code, out, err = sf("plan", d, "--catalogue", args.catalogue)
        plan = (d / "plan.md").read_text(encoding="utf-8")
        sections = ["## Approach", "## Artifacts and handoffs", "## Tools from the catalogue", "## Risks", "## Quality gates"]
        check("plan has the five sections", code == 0 and all(s in plan for s in sections), err)
        check("plan picks Three.js from TOOL_SELECTION.md with a line citation",
              re.search(r"Three\.js with a validated GLB.*\(TOOL_SELECTION\.md line \d+\)", plan) is not None)
        gates = re.findall(r"^- \[ \] Gate: ([^(:]+)", plan, re.M)
        gates = [g.strip() for g in gates]
        check("plan names quality gates", {"Delivery", "Engineering", "Interactive 3D"} <= set(gates), str(gates))
        check("plan has no absolute paths", not re.search(r"[A-Za-z]:[\\/]|/tmp/|/Users/", plan))

        code, out, err = sf("tasks", d)
        tasks = (d / "tasks.md").read_text(encoding="utf-8")
        tlines = re.findall(r"^- \[ \] (T\d{3}) .*\(traces: ([^)]+)\)$", tasks, re.M)
        traced = {x.strip() for _, t in tlines for x in t.split(",")}
        check("tasks numbered and all traced", code == 0 and len(tlines) == len(re.findall(r"^- \[ \] T", tasks, re.M))
              and [t for t, _ in tlines] == [f"T{i:03d}" for i in range(1, len(tlines) + 1)], f"{len(tlines)} tasks")
        check("every criterion has a task", set(acs) <= traced and traced <= set(acs))

        code, out, err = sf("analyze", d)
        check("analyze passes on the full flow", code == 0 and out.startswith("analyze: OK"), out.strip())
        result["sample"] = {"criteria": len(acs), "tasks": len(tlines), "gates": gates}
        sample_dir = OUT / "sample"
        if sample_dir.exists():
            shutil.rmtree(sample_dir)
        sample_dir.mkdir(parents=True)
        for name in ("spec.md", "plan.md", "tasks.md"):
            shutil.copy(d / name, sample_dir / name)
        shutil.copy(con, sample_dir / "constitution.md")

        good_tasks, good_plan, good_spec = tasks, plan, spec

        def broken(label, path, new_text, expect):
            path.write_text(new_text, encoding="utf-8")
            code, out, _ = sf("analyze", d)
            check(f"analyze fails: {label}", code == 1 and expect in out, out.strip().replace("\n", " | ")[:160])
            (d / "tasks.md").write_text(good_tasks, encoding="utf-8")
            (d / "plan.md").write_text(good_plan, encoding="utf-8")
            (d / "spec.md").write_text(good_spec, encoding="utf-8")

        t3 = re.search(r"^- \[ \] T003 .*$", tasks, re.M).group(0)
        broken("task without a trace", d / "tasks.md", tasks.replace(t3, re.sub(r" \(traces: [^)]+\)", "", t3)),
               "T003 traces to no acceptance criterion")
        no_ac21 = "\n".join(l for l in tasks.split("\n") if not ("(traces: AC2.1)" in l))
        no_ac21 = no_ac21.replace("AC2.1, ", "")
        broken("criterion without a task", d / "tasks.md", no_ac21, "coverage: AC2.1 has no task")
        broken("trace to an unknown criterion", d / "tasks.md", tasks.replace("(traces: AC1.2)", "(traces: AC9.9)", 1),
               "unknown criterion AC9.9")
        broken("new open question in spec", d / "spec.md",
               spec.replace("## Edge cases", "## Edge cases\n\n- [NEEDS CLARIFICATION: Q5 maximum file size?]"),
               "unresolved [NEEDS CLARIFICATION]")
        broken("plan without gates", d / "plan.md", re.sub(r"^- \[ \] Gate: .*\n", "", plan, flags=re.M),
               "plan: names no quality gates")
        code, out, _ = sf("analyze", d)
        check("restored files pass again", code == 0)

        code, out, err = sf("approve", d, "--by", "project owner")
        spec2 = (d / "spec.md").read_text(encoding="utf-8")
        code2, out2, _ = sf("analyze", d)
        check("approve records the owner and analyze still passes",
              code == 0 and "- Status: approved by project owner on 2026-11-26" in spec2 and code2 == 0, out2.strip())

        # second feature: no actor in the text, no catalogue reachable -> built-in gates
        code, out, err = sf("specify", "Generate a weekly report of render times; then post a summary to the team page",
                            "--root", root)
        d2 = sorted((root / "specs").iterdir())[1]
        check("second spec numbered 002", code == 0 and d2.name.startswith("002-"), d2.name)
        s2 = (d2 / "spec.md").read_text(encoding="utf-8")
        check("unknown actor becomes a question", "Who is the primary user" in s2)
        qs = sorted(set(re.findall(r"\[NEEDS CLARIFICATION: (Q\d+)", s2)))
        code, _, _ = sf("clarify", d2, *[x for q in qs for x in ("--answer", f"{q}=answer for {q}")])
        code, out, err = sf("plan", d2)
        p2 = (d2 / "plan.md").read_text(encoding="utf-8")
        check("plan works without the catalogue", code == 0 and "built-in" in p2 and "Gate: Delivery" in p2, err)
        code, _, _ = sf("tasks", d2)
        code, out, _ = sf("analyze", d2)
        check("second flow passes analyze", code == 0, out.strip())

    result["checks"] = checks
    result["pass"] = all(c["pass"] for c in checks)
    (OUT / "result.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(f"{sum(c['pass'] for c in checks)}/{len(checks)} checks passed")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

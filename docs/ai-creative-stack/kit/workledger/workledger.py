#!/usr/bin/env python3
"""workledger: plan, run and reconcile bounded work packages with a deterministic monitor and an evidence ledger.

Our own executable version of the V7 strategy layer (spec-first packages, bounded delegation, independent
monitoring, plan/action reconciliation, alternatives). Standard library only. No agent framework.

  python workledger.py check    work-packages.json            # schema, cycles, edit-scope conflicts, waves
  python workledger.py run      work-packages.json --root DIR  [--ledger execution-ledger.jsonl] [--baseline]
  python workledger.py decide   decision-log.jsonl --constraints ... --alternative A --alternative B --chosen A --rationale ...
  python workledger.py reconcile execution-ledger.jsonl

A package's "command" is run from --root. Its "acceptance_checks" are commands that must exit 0.
"edit_scope" lists glob patterns (relative to --root) the package may change; anything else it changes is a
scope deviation, which stops that package and its dependents. The monitor stops a package early when two
attempts fail with byte-identical output (repeated equivalent failure) or when an attempt changes nothing
and still fails (no progress), and enforces budget.seconds per attempt and retry_limit overall.
--baseline runs the same packages the naive way, for comparison: in file order, every retry used, no scope
checks and no early stopping.
"""
import argparse
import fnmatch
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

FIELDS = ["id", "parent_id", "goal", "owner", "input_refs", "output_paths", "depends_on", "edit_scope",
          "acceptance_checks", "budget", "retry_limit", "status", "evidence_refs"]
RUNTIME = ["command"]  # fixture extension: how to execute the package


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def load_packages(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    pkgs = data["packages"] if isinstance(data, dict) else data
    return pkgs


def check(pkgs):
    """Return (problems, waves). Waves are lists of package ids that may run in parallel."""
    problems = []
    ids = [p.get("id") for p in pkgs]
    if len(ids) != len(set(ids)):
        problems.append("duplicate package ids")
    by = {p["id"]: p for p in pkgs}
    for p in pkgs:
        missing = [f for f in FIELDS if f not in p]
        if missing:
            problems.append(f"{p.get('id')}: missing fields {missing}")
        for d in p.get("depends_on", []):
            if d not in by:
                problems.append(f"{p['id']}: depends on unknown package {d}")
        if not p.get("acceptance_checks"):
            problems.append(f"{p['id']}: no acceptance checks (a package must be verifiable)")
        if not p.get("edit_scope"):
            problems.append(f"{p['id']}: empty edit scope")
    # Cycle detection and levels.
    level, visiting = {}, set()

    def depth(i):
        if i in level:
            return level[i]
        if i in visiting:
            raise ValueError(f"dependency cycle through {i}")
        visiting.add(i)
        level[i] = 1 + max([depth(d) for d in by[i].get("depends_on", []) if d in by] or [-1])
        visiting.discard(i)
        return level[i]

    try:
        for i in by:
            depth(i)
    except ValueError as e:
        problems.append(str(e))
        return problems, []
    waves = []
    for lv in sorted(set(level.values())):
        group = [i for i in ids if level[i] == lv]
        # Packages in one wave whose edit scopes overlap are serialised into separate waves.
        lanes = []
        for i in group:
            for lane in lanes:
                if not any(scopes_overlap(by[i]["edit_scope"], by[j]["edit_scope"]) for j in lane):
                    lane.append(i)
                    break
            else:
                lanes.append([i])
        waves.extend(lanes)
    return problems, waves


def scopes_overlap(a, b):
    for x in a:
        for y in b:
            if fnmatch.fnmatch(x, y) or fnmatch.fnmatch(y, x) or x == y:
                return True
            # Same directory prefix before a wildcard counts as overlap.
            px, py = x.split("*")[0], y.split("*")[0]
            if px and py and (px.startswith(py) or py.startswith(px)):
                return True
    return False


def snapshot(root):
    out = {}
    for f in Path(root).rglob("*"):
        if f.is_file() and ".ledger" not in f.parts:
            out[f.relative_to(root).as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def diff(before, after):
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    return changed


def in_scope(path, scope):
    return any(fnmatch.fnmatch(path, s) for s in scope)


def sh(cmd, root, timeout):
    t0 = time.time()
    try:
        r = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr)[-2000:], time.time() - t0, False
    except subprocess.TimeoutExpired:
        return 124, "timeout", time.time() - t0, True


def run(pkgs, root, ledger_path, baseline=False):
    by = {p["id"]: p for p in pkgs}
    problems, waves = check(pkgs)
    if problems and not baseline:
        raise SystemExit("Refusing to run: " + "; ".join(problems))
    order = [p["id"] for p in pkgs] if baseline else [i for w in waves for i in w]
    status = {}
    stats = {"attempts": 0, "command_seconds": 0.0, "stopped_early": 0, "scope_deviations": 0, "blocked": 0}
    ledger = open(ledger_path, "a", encoding="utf-8", newline="\n")
    t_start = time.time()
    for pid in order:
        p = by[pid]
        if not baseline and any(status.get(d) != "done" for d in p["depends_on"]):
            status[pid] = "blocked"
            stats["blocked"] += 1
            ledger.write(json.dumps({"ts": now(), "work_package_id": pid, "planned_effect": p["goal"], "observed_effect": None,
                                     "changed_paths": [], "validation_result": "not run", "deviation_reason": "dependency not done",
                                     "evidence_refs": [], "status": "blocked"}) + "\n")
            continue
        budget = p.get("budget") or {}
        timeout = float(budget.get("seconds", 60))
        limit = int(p.get("retry_limit", 0)) + 1
        last_output, outcome = None, "failed"
        for attempt in range(1, limit + 1):
            before = snapshot(root)
            code, out, secs, timed_out = sh(p["command"], root, timeout)
            checks = [sh(c, root, timeout)[0] == 0 for c in p["acceptance_checks"]] if code == 0 else [False]
            after = snapshot(root)
            changed = diff(before, after)
            outside = [c for c in changed if not in_scope(c, p["edit_scope"])]
            stats["attempts"] += 1
            stats["command_seconds"] += secs
            entry = {"ts": now(), "work_package_id": pid, "attempt": attempt, "planned_effect": p["goal"],
                     "observed_effect": f"exit {code}{' (timeout)' if timed_out else ''}; {len(changed)} file(s) changed",
                     "changed_paths": changed, "validation_result": "pass" if all(checks) else "fail",
                     "deviation_reason": None, "evidence_refs": p.get("output_paths", []), "status": "running"}
            if outside and not baseline:
                entry["deviation_reason"] = f"changed outside edit scope: {outside}"
                entry["status"] = "stopped"
                stats["scope_deviations"] += 1
                ledger.write(json.dumps(entry) + "\n")
                outcome = "scope_deviation"
                break
            if all(checks):
                entry["status"] = "done"
                ledger.write(json.dumps(entry) + "\n")
                outcome = "done"
                break
            if not baseline:
                if last_output is not None and out == last_output:
                    entry["deviation_reason"] = "repeated equivalent failure"
                    entry["status"] = "stopped"
                    stats["stopped_early"] += 1
                    ledger.write(json.dumps(entry) + "\n")
                    break
                if not changed and attempt > 1:
                    entry["deviation_reason"] = "no progress: attempt changed nothing"
                    entry["status"] = "stopped"
                    stats["stopped_early"] += 1
                    ledger.write(json.dumps(entry) + "\n")
                    break
            entry["status"] = "retrying" if attempt < limit else "failed"
            ledger.write(json.dumps(entry) + "\n")
            last_output = out
        status[pid] = outcome
    ledger.close()
    stats["wall_seconds"] = round(time.time() - t_start, 3)
    stats["command_seconds"] = round(stats["command_seconds"], 3)
    return status, stats, waves


def reconcile(ledger_path):
    final = {}
    for line in Path(ledger_path).read_text(encoding="utf-8").splitlines():
        e = json.loads(line)
        final[e["work_package_id"]] = e
    return {pid: {"status": e["status"], "planned": e["planned_effect"], "observed": e["observed_effect"],
                  "changed": e["changed_paths"], "deviation": e["deviation_reason"]} for pid, e in final.items()}


def decide(log, constraints, alternatives, chosen, rationale, evidence, uncertainty, review_trigger):
    if chosen not in alternatives:
        raise SystemExit("--chosen must be one of the --alternative values")
    if len(alternatives) < 2:
        raise SystemExit("record at least two alternatives, including keeping the existing solution where relevant")
    entry = {"id": f"D{int(time.time() * 1000)}", "timestamp": now(), "constraints": constraints, "alternatives": alternatives,
             "chosen_option": chosen, "concise_rationale": rationale, "evidence_refs": evidence, "uncertainty": uncertainty,
             "review_trigger": review_trigger, "approval_status": "proposed"}
    with open(log, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("packages")
    r = sub.add_parser("run"); r.add_argument("packages"); r.add_argument("--root", required=True)
    r.add_argument("--ledger", default="execution-ledger.jsonl"); r.add_argument("--baseline", action="store_true")
    d = sub.add_parser("decide"); d.add_argument("log"); d.add_argument("--constraints", required=True)
    d.add_argument("--alternative", action="append", required=True); d.add_argument("--chosen", required=True)
    d.add_argument("--rationale", required=True); d.add_argument("--evidence", action="append", default=[])
    d.add_argument("--uncertainty", default="unknown"); d.add_argument("--review-trigger", default="on contradicting evidence")
    q = sub.add_parser("reconcile"); q.add_argument("ledger")
    a = ap.parse_args()
    if a.cmd == "check":
        problems, waves = check(load_packages(a.packages))
        print(json.dumps({"problems": problems, "waves": waves}, indent=2))
        return 1 if problems else 0
    if a.cmd == "run":
        status, stats, waves = run(load_packages(a.packages), a.root, a.ledger, a.baseline)
        print(json.dumps({"status": status, "stats": stats, "waves": waves}, indent=2))
        return 0 if all(v == "done" for v in status.values()) else 1
    if a.cmd == "decide":
        print(json.dumps(decide(a.log, a.constraints, a.alternative, a.chosen, a.rationale, a.evidence, a.uncertainty, a.review_trigger), indent=2))
        return 0
    if a.cmd == "reconcile":
        print(json.dumps(reconcile(a.ledger), indent=2))
        return 0


if __name__ == "__main__":
    sys.exit(main())

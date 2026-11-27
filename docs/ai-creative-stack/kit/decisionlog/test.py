#!/usr/bin/env python3
"""Test decisionlog end to end in a temporary folder.

  python test.py

Writes out/result.json and out/DECISIONS.sample.md; exits 0 only on pass.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "decisionlog.py"
OUT = HERE / "out"
checks = []


def check(name, ok, detail=""):
    checks.append({"check": name, "pass": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def main():
    OUT.mkdir(exist_ok=True)
    result = {"tool": "decisionlog"}
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        log = tmp / "decisions.jsonl"

        def dl(*args):
            p = subprocess.run([sys.executable, str(TOOL), "--log", str(log), *args],
                               capture_output=True, text=True, encoding="utf-8")
            return p.returncode, p.stdout, p.stderr

        def disk_text():
            return "".join(p.read_text(encoding="utf-8") for p in tmp.rglob("*") if p.is_file())

        secret_phrase = "client is Zebra Holdings budget 41k"
        fake_key = "sk-" + "abcdefghij" * 4  # built at run time so no key-shaped string sits in the file
        code, out, err = dl("add", "--title", "Use one critic per design pass",
                            "--decision", "Impeccable detector in CI; Hallmark owns the review.",
                            "--why", f"One authority per pass avoids contradictory fix lists. <private>{secret_phrase}</private>",
                            "--evidence", "docs/workflows/design-system-extraction.md, review run 14",
                            "--tags", "design,review")
        check("add D-0001", code == 0 and "D-0001" in out, err)
        code, out, err = dl("add", "--title", "Gaussian splats only for research scenes",
                            "--decision", "Do not ship the Inria trainer in a commercial product.",
                            "--why", "The licence is research and evaluation only.",
                            "--evidence", "docs/3d-pipeline/gaussian-splatting.md#license", "--tags", "3d,license")
        check("add D-0002", code == 0 and "D-0002" in out, err)
        code, out, err = dl("add", "--title", "Store renders on the NAS",
                            "--decision", "Keep render outputs off the system drive.",
                            "--why", "Disk space on C is limited.", "--evidence", "ops note 3")
        check("add D-0003", code == 0, err)
        code, out, err = dl("add", "--title", "Leaky", "--decision", f"use key {fake_key}",
                            "--why", "x", "--evidence", "y")
        check("secret-looking text refused", code == 2 and "secret" in err and fake_key not in err + out, err.strip())
        code, out, err = dl("add", "--title", "Wrapped key ok", "--decision", f"Rotate <private>{fake_key}</private> monthly",
                            "--why", "hygiene", "--evidence", "security review")
        check("secret inside <private> accepted and dropped", code == 0 and fake_key not in disk_text(), err)

        recs = [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines()]
        check("entries start as proposed", all(r["status"] == "proposed" for r in recs if r["type"] == "entry"))
        check("private text never on disk", secret_phrase not in disk_text() and "Zebra" not in disk_text())
        check("private placeholder kept", "[private]" in log.read_text(encoding="utf-8"))

        code, out, err = dl("approve", "D-0001")
        check("approve without --by refused", code != 0)
        code, out, err = dl("approve", "D-0001", "--by", "project owner")
        check("approve D-0001", code == 0, err)
        code, out, err = dl("approve", "D-0002", "--by", "project owner")
        check("approve D-0002", code == 0, err)
        code, out, err = dl("reject", "D-0003", "--by", "project owner", "--reason", "NAS policy already covers it")
        check("reject D-0003", code == 0, err)
        code, out, err = dl("approve", "D-0003", "--by", "someone")
        check("cannot approve a rejected entry", code == 2, err.strip())
        code, out, err = dl("approve", "D-0001", "--by", "someone")
        check("cannot approve twice", code == 2)

        # supersede: a newer approved decision replaces an older one
        code, out, err = dl("add", "--title", "Hallmark is the only critic", "--decision", "Drop the Impeccable CI detector.",
                            "--why", "Single tool is easier to audit.", "--evidence", "review run 20", "--supersedes", "D-0001")
        code2, _, _ = dl("approve", "D-0005", "--by", "project owner")
        check("superseding entry approved", code == 0 and code2 == 0, err)

        lines_before = log.read_text(encoding="utf-8").splitlines()
        check("append-only: status changes are new records", len(lines_before) == 9, str(len(lines_before)))
        first_line_hash = json.loads(lines_before[0])["hash"]

        code, out, _ = dl("list", "--status", "approved")
        check("list --status approved", code == 0 and "D-0001" in out and "D-0002" in out and "D-0003" not in out
              and "3 entries" in out, out.strip().splitlines()[-1])
        code, out, _ = dl("search", "gaussian licence commercial")
        check("search ranks the licence decision first", code == 0 and out.splitlines()[0].startswith("D-0002"), out.strip()[:120])
        code, out, _ = dl("search", "critic review", "--status", "approved")
        check("search with status filter", code == 0 and "D-0003" not in out and "D-0001" in out)

        code, out, err = dl("export", "--md", "--out", str(tmp / "DECISIONS.md"))
        md = (tmp / "DECISIONS.md").read_text(encoding="utf-8")
        check("export writes approved only", code == 0 and "D-0001" in md and "D-0002" in md and "D-0005" in md
              and "D-0003" not in md and "Wrapped key ok" not in md, err)
        check("export names approver and evidence", "Approved by: project owner" in md and
              "- Evidence: docs/3d-pipeline/gaussian-splatting.md#license" in md)
        check("export marks superseded", "Superseded by: D-0005" in md)
        check("export has precedence sentence", "never overrides the current instruction" in md)
        shutil.copy(tmp / "DECISIONS.md", OUT / "DECISIONS.sample.md")

        code, out, _ = dl("verify")
        check("verify passes on clean log", code == 0 and out.startswith("OK 9 records"), out.strip())

        # tamper 1: change the text of an approved entry
        good = log.read_text(encoding="utf-8")
        lines = good.splitlines()
        rec = json.loads(lines[1])
        rec["content"]["decision"] = "Ship the Inria trainer anyway."
        lines[1] = json.dumps(rec, sort_keys=True, separators=(",", ":"))
        log.write_text("\n".join(lines) + "\n", encoding="utf-8")
        code, out, _ = dl("verify")
        check("verify fails on edited content", code == 1 and "content does not match" in out, out.strip()[:120])
        code, out, err = dl("add", "--title", "t", "--decision", "d", "--why", "w", "--evidence", "e")
        check("append refused on a tampered log", code == 2 and "refusing" in err)
        # tamper 2: flip a status
        lines = good.splitlines()
        rec = json.loads(lines[6])
        assert rec["type"] == "status" and rec["status"] == "rejected"
        rec["status"] = "approved"
        lines[6] = json.dumps(rec, sort_keys=True, separators=(",", ":"))
        log.write_text("\n".join(lines) + "\n", encoding="utf-8")
        code, out, _ = dl("verify")
        check("verify fails on edited status record", code == 1 and "hash mismatch" in out, out.strip()[:120])
        # tamper 3: delete a line from the middle
        lines = good.splitlines()
        del lines[3]
        log.write_text("\n".join(lines) + "\n", encoding="utf-8")
        code, out, _ = dl("verify")
        check("verify fails on deleted record", code == 1 and "prev hash" in out)
        log.write_text(good, encoding="utf-8")
        code, out, _ = dl("verify")
        check("restored log verifies", code == 0)

        # redact + compact
        target_text = "Disk space on C is limited."
        code, out, err = dl("redact", "D-0003", "--by", "project owner", "--reason", "obsolete and sensitive")
        check("redact appends tombstone", code == 0 and target_text in log.read_text(encoding="utf-8"), err)
        code, out, _ = dl("list")
        check("redacted text hidden from list", "Store renders on the NAS" not in out and "redacted" in out)
        code, out, _ = dl("search", "render NAS disk")
        check("redacted text hidden from search", "D-0003" not in out)
        code, out, err = dl("compact")
        text = log.read_text(encoding="utf-8")
        check("compact removes redacted text from disk", code == 0 and target_text not in text
              and "Store renders on the NAS" not in disk_text(), out.strip() + err)
        last = json.loads(text.splitlines()[-1])
        check("checkpoint entry appended", last["type"] == "checkpoint" and last["compacted"] == ["D-0003"])
        code, out, _ = dl("verify")
        check("verify passes after compact", code == 0, out.strip())
        check("history untouched by compact", json.loads(text.splitlines()[0])["hash"] == first_line_hash)
        # dropping content of a NON-redacted entry is still caught
        lines = text.splitlines()
        rec = json.loads(lines[1])
        del rec["content"]
        lines[1] = json.dumps(rec, sort_keys=True, separators=(",", ":"))
        log.write_text("\n".join(lines) + "\n", encoding="utf-8")
        code, out, _ = dl("verify")
        check("removing content without redaction is caught", code == 1 and "without a redaction" in out)
        log.write_text(text, encoding="utf-8")
        code, out, _ = dl("export", "--md", "--out", str(tmp / "DECISIONS.md"))
        check("export still works after compact", code == 0)
        check("no network or auto-capture code", not any(w in TOOL.read_text(encoding="utf-8")
                                                         for w in ("urllib", "socket", "http.client", "requests")))
        result["records"] = len(text.splitlines())

    result["checks"] = checks
    result["pass"] = all(c["pass"] for c in checks)
    (OUT / "result.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(f"{sum(c['pass'] for c in checks)}/{len(checks)} checks passed")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

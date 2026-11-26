#!/usr/bin/env python3
"""decisionlog: an explicit, approval-gated, append-only decision log.

  python decisionlog.py [--log decisions.jsonl] add --title T --decision D --why W --evidence E [--tags a,b] [--supersedes ID]
  python decisionlog.py approve <id> --by <name> [--note N]
  python decisionlog.py reject <id> [--by <name>] [--reason R]
  python decisionlog.py list [--status proposed|approved|rejected|redacted]
  python decisionlog.py search "<words>" [--status approved] [--top 10]
  python decisionlog.py export --md [--out DECISIONS.md]
  python decisionlog.py verify
  python decisionlog.py redact <id> [--by <name>] [--reason R]
  python decisionlog.py compact

Nothing is captured automatically: the log changes only when one of these commands runs.
Text inside <private>...</private> is removed before anything is written. Text that looks
like a secret (API keys, tokens, private keys) is refused. No network access.

Integrity: every record carries `prev` (hash of the previous record) and `hash`
(sha256 of its own canonical JSON). An entry's free text sits in `content` with a random
`salt`; the record hash covers `content_hash = sha256(salt + content)`, not the text
itself. That is what lets `compact` delete redacted text while the chain still verifies.
"""
import argparse
import hashlib
import json
import math
import os
import re
import secrets
import sys
from collections import Counter
from datetime import datetime, timezone

GENESIS = "0" * 64
CONTENT_FIELDS = ("title", "decision", "why", "evidence", "tags")
PRIVATE_RE = re.compile(r"<private>.*?(?:</private>|\Z)", re.I | re.S)
SECRET_PATTERNS = [
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{20,}")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("gateway key", re.compile(r"\bagw_[A-Za-z0-9_\-]{12,}")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("assigned secret", re.compile(r"(?i)\b(?:api[_\-]?key|secret|password|passwd|token)\s*[:=]\s*['\"]?[^\s'\"]{8,}")),
]
STATUSES = ("proposed", "approved", "rejected", "redacted")


class LogError(Exception):
    pass


# ---------------------------------------------------------------- hashing

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def record_hash(rec):
    core = {k: v for k, v in rec.items() if k not in ("hash", "content", "salt")}
    return sha(canonical(core))


def content_hash(salt, content):
    return sha(salt + canonical(content))


# ---------------------------------------------------------------- text hygiene

def strip_private(text):
    return PRIVATE_RE.sub("[private]", text or "").strip()


def secret_findings(text):
    return [name for name, rx in SECRET_PATTERNS if rx.search(text or "")]


def clean_field(name, value):
    v = strip_private(value)
    found = secret_findings(v)
    if found:
        raise LogError(f"refused: field '{name}' looks like it contains a secret ({', '.join(found)}). "
                       "Remove it, or wrap it in <private>...</private> so it is never stored.")
    return v


# ---------------------------------------------------------------- storage

class Log:
    def __init__(self, path):
        self.path = path

    def read(self):
        if not os.path.exists(self.path):
            return []
        recs = []
        with open(self.path, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    recs.append(json.loads(line))
                except ValueError:
                    raise LogError(f"line {n}: not valid JSON")
        return recs

    def verify(self, recs=None):
        """Return (ok, problems, head)."""
        try:
            recs = self.read() if recs is None else recs
        except LogError as exc:
            return False, [str(exc)], None
        problems = []
        prev = GENESIS
        redacted = set()
        ids = set()
        for i, r in enumerate(recs, 1):
            if r.get("seq") != i:
                problems.append(f"record {i}: seq is {r.get('seq')}, expected {i}")
            if r.get("prev") != prev:
                problems.append(f"record {i}: prev hash does not match record {i - 1}")
            if record_hash(r) != r.get("hash"):
                problems.append(f"record {i}: hash mismatch (record was changed)")
            t = r.get("type")
            if t == "entry":
                ids.add(r.get("id"))
                if "content" in r:
                    if content_hash(r.get("salt", ""), r["content"]) != r.get("content_hash"):
                        problems.append(f"record {i} ({r.get('id')}): content does not match content_hash")
                elif r.get("id") not in redacted_ids_after(recs, r.get("id")):
                    problems.append(f"record {i} ({r.get('id')}): content missing without a redaction")
            elif t in ("status", "redaction"):
                if r.get("target") not in ids:
                    problems.append(f"record {i}: refers to unknown entry {r.get('target')}")
                if t == "redaction":
                    redacted.add(r.get("target"))
            elif t != "checkpoint":
                problems.append(f"record {i}: unknown type {t!r}")
            prev = r.get("hash")
        return not problems, problems, (recs[-1]["hash"] if recs else GENESIS)

    def append(self, rec):
        recs = self.read()
        ok, problems, head = self.verify(recs)
        if not ok:
            raise LogError("log fails verification; refusing to append:\n  " + "\n  ".join(problems))
        rec = dict(rec)
        rec["seq"] = len(recs) + 1
        rec["ts"] = now()
        rec["prev"] = head
        rec["hash"] = record_hash(rec)
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        with open(self.path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(canonical(rec) + "\n")
        return rec


def redacted_ids_after(recs, eid):
    return {r.get("target") for r in recs if r.get("type") == "redaction" and r.get("target") == eid}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- state

def fold(recs):
    """Current view of every entry, built by replaying the log."""
    entries = {}
    for r in recs:
        t = r.get("type")
        if t == "entry":
            c = r.get("content") or {}
            entries[r["id"]] = {"id": r["id"], "created": r["ts"], "status": "proposed",
                                "supersedes": r.get("supersedes"), "approved_by": None, "approved_at": None,
                                "history": [("proposed", r["ts"], None)], **{k: c.get(k) for k in CONTENT_FIELDS}}
        elif t == "status" and r["target"] in entries:
            e = entries[r["target"]]
            e["status"] = r["status"]
            e["history"].append((r["status"], r["ts"], r.get("by")))
            if r["status"] == "approved":
                e["approved_by"], e["approved_at"] = r.get("by"), r["ts"]
        elif t == "redaction" and r["target"] in entries:
            e = entries[r["target"]]
            e["status"] = "redacted"
            e["history"].append(("redacted", r["ts"], r.get("by")))
            for k in CONTENT_FIELDS:
                e[k] = None
    superseded = {}
    for e in entries.values():
        if e["status"] == "approved" and e["supersedes"]:
            superseded[e["supersedes"]] = e["id"]
    for eid, by in superseded.items():
        if eid in entries:
            entries[eid]["superseded_by"] = by
    return entries


# ---------------------------------------------------------------- search

def tokenize(text):
    toks = []
    for w in re.findall(r"[a-z0-9]+", (text or "").lower()):
        if len(w) < 2 or w in {"the", "and", "for", "with", "that", "this", "are", "was", "not", "use"}:
            continue
        for suf in ("ing", "ed", "es", "s"):
            if len(w) > len(suf) + 3 and w.endswith(suf):
                w = w[: -len(suf)]
                break
        toks.append(w)
    return toks


def bm25(docs, query, k1=1.4, b=0.7):
    tfs = [Counter(d) for d in docs]
    n = len(docs)
    avg = (sum(map(len, docs)) / n) if n else 1
    df = Counter(t for tf in tfs for t in tf)
    q = set(tokenize(query))
    scores = []
    for tf, d in zip(tfs, docs):
        s = 0.0
        for t in q:
            f = tf.get(t)
            if f:
                idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                s += idf * f * (k1 + 1) / (f + k1 * (1 - b + b * len(d) / (avg or 1)))
        scores.append(s)
    return scores


# ---------------------------------------------------------------- commands

def cmd_add(log, a):
    content = {
        "title": clean_field("title", a.title),
        "decision": clean_field("decision", a.decision),
        "why": clean_field("why", a.why),
        "evidence": clean_field("evidence", a.evidence),
        "tags": sorted({clean_field("tags", t).lower() for t in (a.tags or "").split(",") if t.strip()}),
    }
    for k in ("title", "decision", "why", "evidence"):
        if not content[k] or content[k] == "[private]":
            raise LogError(f"'{k}' is required and must contain non-private text")
    recs = log.read()
    entries = fold(recs)
    if a.supersedes and a.supersedes not in entries:
        raise LogError(f"--supersedes {a.supersedes}: no such entry")
    eid = "D-%04d" % (sum(1 for r in recs if r.get("type") == "entry") + 1)
    salt = secrets.token_hex(16)
    rec = {"type": "entry", "id": eid, "status": "proposed", "salt": salt, "content": content,
           "content_hash": content_hash(salt, content)}
    if a.supersedes:
        rec["supersedes"] = a.supersedes
    log.append(rec)
    print(f"{eid} proposed: {content['title']}  (needs: approve {eid} --by <name>)")


def _need(entries, eid, allowed, action):
    if eid not in entries:
        raise LogError(f"no such entry {eid}")
    st = entries[eid]["status"]
    if st not in allowed:
        raise LogError(f"cannot {action} {eid}: status is {st}")


def cmd_approve(log, a):
    if not (a.by or "").strip():
        raise LogError("--by is required: an approval must name the approver")
    entries = fold(log.read())
    _need(entries, a.id, ("proposed",), "approve")
    rec = {"type": "status", "target": a.id, "status": "approved", "by": clean_field("by", a.by)}
    if a.note:
        rec["note"] = clean_field("note", a.note)
    log.append(rec)
    print(f"{a.id} approved by {rec['by']}")


def cmd_reject(log, a):
    entries = fold(log.read())
    _need(entries, a.id, ("proposed",), "reject")
    rec = {"type": "status", "target": a.id, "status": "rejected"}
    if a.by:
        rec["by"] = clean_field("by", a.by)
    if a.reason:
        rec["reason"] = clean_field("reason", a.reason)
    log.append(rec)
    print(f"{a.id} rejected")


def cmd_redact(log, a):
    entries = fold(log.read())
    _need(entries, a.id, ("proposed", "approved", "rejected"), "redact")
    rec = {"type": "redaction", "target": a.id}
    if a.by:
        rec["by"] = clean_field("by", a.by)
    if a.reason:
        rec["reason"] = clean_field("reason", a.reason)
    log.append(rec)
    print(f"{a.id} redacted (text hidden now; run 'compact' to delete it from disk)")


def cmd_list(log, a):
    entries = fold(log.read())
    rows = [e for e in entries.values() if not a.status or e["status"] == a.status]
    for e in rows:
        title = e["title"] if e["title"] is not None else "[redacted]"
        extra = f" by {e['approved_by']}" if e["status"] == "approved" else ""
        sup = f" (superseded by {e['superseded_by']})" if e.get("superseded_by") else ""
        print(f"{e['id']}  {e['created'][:10]}  {e['status']:<8}{extra}  {title}{sup}")
    print(f"{len(rows)} entries")


def cmd_search(log, a):
    entries = [e for e in fold(log.read()).values() if e["status"] != "redacted"
               and (not a.status or e["status"] == a.status)]
    docs = [tokenize(" ".join([e["title"]] * 2 + [e["decision"], e["why"], e["evidence"], " ".join(e["tags"] or [])]))
            for e in entries]
    scores = bm25(docs, a.words)
    ranked = sorted(zip(scores, range(len(entries))), reverse=True)
    shown = 0
    for s, i in ranked[: a.top]:
        if s <= 0:
            break
        e = entries[i]
        print(f"{e['id']}  {e['status']:<8}  {s:5.2f}  {e['title']}  | {e['decision'][:100]}")
        shown += 1
    if not shown:
        print("no matches")


def cmd_export(log, a):
    if not a.md:
        raise LogError("only --md export is supported")
    recs = log.read()
    ok, problems, head = log.verify(recs)
    if not ok:
        raise LogError("log fails verification; refusing to export:\n  " + "\n  ".join(problems))
    entries = [e for e in fold(recs).values() if e["status"] == "approved"]
    lines = ["# Decisions", "",
             "Approved decisions only, generated by decisionlog from the append-only log. Do not edit by hand.",
             "Retrieved memory never overrides the current instruction, project policy or security rules.",
             f"Log head: `{head}` ({len(recs)} records).", ""]
    for e in entries:
        lines.append(f"## {e['approved_at'][:10]} {e['title']}")
        lines.append(f"- ID: {e['id']}")
        lines.append(f"- Decision: {e['decision']}")
        lines.append(f"- Why: {e['why']}")
        lines.append(f"- Evidence: {e['evidence']}")
        if e["tags"]:
            lines.append(f"- Tags: {', '.join(e['tags'])}")
        lines.append(f"- Approved by: {e['approved_by']}. Supersedes: {e['supersedes'] or 'none'}.")
        if e.get("superseded_by"):
            lines.append(f"- Superseded by: {e['superseded_by']}. The newer decision applies.")
        lines.append("")
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(log.path)), "DECISIONS.md")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    print(f"wrote {out}: {len(entries)} approved entries")


def cmd_verify(log, a):
    ok, problems, head = log.verify()
    n = len(log.read()) if ok or os.path.exists(log.path) else 0
    if ok:
        print(f"OK {n} records, head {head}")
        return 0
    print("FAIL")
    for p in problems:
        print("  " + p)
    return 1


def cmd_compact(log, a):
    recs = log.read()
    ok, problems, head = log.verify(recs)
    if not ok:
        raise LogError("log fails verification; refusing to compact:\n  " + "\n  ".join(problems))
    redacted = {r["target"] for r in recs if r.get("type") == "redaction"}
    removed = []
    for r in recs:
        if r.get("type") == "entry" and r["id"] in redacted and "content" in r:
            del r["content"]
            r.pop("salt", None)
            removed.append(r["id"])
    if not removed:
        print("nothing to compact")
        return
    tmp = log.path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        for r in recs:
            fh.write(canonical(r) + "\n")
    os.replace(tmp, log.path)
    log.append({"type": "checkpoint", "compacted": sorted(removed), "prior_head": head, "records": len(recs)})
    ok, problems, head = log.verify()
    print(f"compacted {', '.join(sorted(removed))}; chain {'verifies' if ok else 'FAILS'}; head {head}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="decisionlog")
    ap.add_argument("--log", default=os.environ.get("DECISIONLOG_FILE", "decisions.jsonl"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add")
    p.add_argument("--title", required=True)
    p.add_argument("--decision", required=True)
    p.add_argument("--why", required=True)
    p.add_argument("--evidence", required=True)
    p.add_argument("--tags", default="")
    p.add_argument("--supersedes")
    p = sub.add_parser("approve")
    p.add_argument("id")
    p.add_argument("--by", required=True)
    p.add_argument("--note")
    p = sub.add_parser("reject")
    p.add_argument("id")
    p.add_argument("--by")
    p.add_argument("--reason")
    p = sub.add_parser("redact")
    p.add_argument("id")
    p.add_argument("--by")
    p.add_argument("--reason")
    p = sub.add_parser("list")
    p.add_argument("--status", choices=STATUSES)
    p = sub.add_parser("search")
    p.add_argument("words")
    p.add_argument("--status", choices=STATUSES)
    p.add_argument("--top", type=int, default=10)
    p = sub.add_parser("export")
    p.add_argument("--md", action="store_true")
    p.add_argument("--out")
    sub.add_parser("verify")
    sub.add_parser("compact")
    a = ap.parse_args(argv)
    log = Log(a.log)
    fn = {"add": cmd_add, "approve": cmd_approve, "reject": cmd_reject, "redact": cmd_redact, "list": cmd_list,
          "search": cmd_search, "export": cmd_export, "verify": cmd_verify, "compact": cmd_compact}[a.cmd]
    try:
        return fn(log, a) or 0
    except LogError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())

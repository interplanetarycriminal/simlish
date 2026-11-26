#!/usr/bin/env python3
"""specflow: a small spec-driven flow, from description to traceable tasks.

  python specflow.py init <dir>
  python specflow.py specify "<feature description>" [--root DIR]
  python specflow.py clarify <spec> [--answer "Q1=text" ...]
  python specflow.py plan <spec> [--catalogue DIR] [--allow-open]
  python specflow.py tasks <spec> [--allow-open]
  python specflow.py analyze <spec>
  python specflow.py approve <spec> --by <name>

<spec> is a spec folder (specs/NNN-slug) or its spec.md. Standard library only. No model,
no network: the text is built from the description with fixed rules, and everything the rules
cannot know is written as [NEEDS CLARIFICATION: Qn ...] for a person to answer.
"""
import argparse
import hashlib
import math
import os
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

MARKER = "NEEDS CLARIFICATION"
MARKER_RE = re.compile(r"\[NEEDS CLARIFICATION: (Q\d+)\b[^\]]*\]")
ANY_MARKER_RE = re.compile(r"\[NEEDS CLARIFICATION[^\]]*\]")
AC_RE = re.compile(r"^\s*-\s*(AC\d+\.\d+):\s*(.+)$", re.M)
TASK_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s*(T\d{3})\b(.*)$", re.M)
TRACE_RE = re.compile(r"\(traces:\s*([^)]*)\)")
ACTOR_RE = re.compile(r"^(?:as an?\s+)?(?P<actor>[A-Za-z][\w\s\-]{0,40}?)\s+(?:can|could|should be able to|must be able to|"
                      r"wants? to|needs? to|is able to|are able to)\s+(?P<rest>.+)$", re.I | re.S)
FALLBACK_GATES = {
    "Delivery": "Every declared artifact opens and matches its format. Rights recorded for fonts, images, audio, weights and code.",
    "Engineering": "Clean rebuild from the lockfile. No console errors on the primary path. Error and empty states exist.",
}


# words in a spec that point at a gate whose own text may not use them (stemmed tokens)
GATE_HINTS = [
    (("glb", "gltf", "threej", "webgl", "viewer", "scene", "3d"), "Interactive 3D"),
    (("mesh", "triangle", "topology", "retopology"), "Geometry"),
    (("video", "mp4", "ffmpeg", "film", "clip", "footage"), "Motion and video"),
    (("page", "screen", "website", "button", "form", "ui", "layout"), "Visual design Accessibility"),
    (("rig", "skin", "bone", "skeleton"), "Rigging"),
    (("splat", "gaussian", "capture", "photogrammetry"), "Gaussian reconstruction"),
    (("lesson", "learner", "explainer", "learning"), "Learning"),
]


class FlowError(Exception):
    pass


# ---------------------------------------------------------------- small helpers

def today():
    return os.environ.get("SPECFLOW_DATE") or date.today().isoformat()


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def slugify(text, words=5):
    toks = [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in {"a", "an", "the", "and", "to", "of", "it", "with", "in"}]
    return "-".join(toks[:words]) or "feature"


def tokenize(text):
    out = []
    for w in re.findall(r"[a-z0-9]+", (text or "").lower().replace(".js", "js")):
        if len(w) < 2 or w in {"the", "and", "for", "with", "that", "this", "are", "can", "into", "from", "it", "its", "to", "of", "in", "or", "on", "is", "as", "be", "an"}:
            continue
        for suf in ("ing", "ed", "es", "s"):
            if len(w) > len(suf) + 3 and w.endswith(suf):
                w = w[: -len(suf)]
                break
        out.append(w)
    return out


def bm25_scores(docs, query, k1=1.4, b=0.6):
    docs = [tokenize(d) for d in docs]
    n = len(docs)
    if not n:
        return []
    avg = sum(map(len, docs)) / n or 1
    df = Counter(t for d in docs for t in set(d))
    q = set(tokenize(query))
    res = []
    for d in docs:
        tf = Counter(d)
        s = 0.0
        for t in q:
            f = tf.get(t)
            if f:
                s += math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5)) * f * (k1 + 1) / (f + k1 * (1 - b + b * len(d) / avg))
        res.append(s)
    return res


def spec_paths(spec):
    p = Path(spec)
    d = p if p.is_dir() else p.parent
    s = d / "spec.md"
    if not s.is_file():
        raise FlowError(f"no spec.md in {d}")
    return d, s


def read(p):
    return Path(p).read_text(encoding="utf-8")


def write(p, text):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(text, encoding="utf-8", newline="\n")


def find_root(start):
    """The project root: the nearest folder above the spec that holds constitution.md or specs/."""
    for d in [Path(start).resolve(), *Path(start).resolve().parents]:
        if (d / "constitution.md").is_file():
            return d
    return Path(start).resolve().parent.parent


def find_catalogue(explicit, start):
    cands = [explicit, os.environ.get("SPECFLOW_CATALOGUE")]
    cands += [str(d) for d in [Path(start).resolve(), *Path(start).resolve().parents]]
    for c in cands:
        if c and (Path(c) / "TOOL_SELECTION.md").is_file():
            return Path(c)
    return None


def spec_meta(text):
    m = re.search(r"^# Feature spec: (.+)$", text, re.M)
    title = m.group(1).strip() if m else "Feature"
    stories = re.findall(r"^### (US\d+): (.+)$", text, re.M)
    acs = AC_RE.findall(text)
    return title, stories, acs


# ---------------------------------------------------------------- init

CONSTITUTION = """# Project constitution

The rules every spec, plan and task in this project follows. Change them only by an owner decision
recorded in the decision log.

## Precedence

1. The current instruction from the owner.
2. Project policy and security rules.
3. The approved spec.
4. The decision log (approved entries only).
5. Retrieved memory and notes.

Retrieved memory never overrides the current instruction, project policy or security rules.
When two sources conflict, follow the higher one and report the conflict with both sources.

## Articles

### I. Smallest coherent toolchain
Use the existing stack first. Add a tool only when it closes a documented gap in the spec.

### II. Test-first traceability
Every acceptance criterion has at least one task and one automated check. Every task names the
criterion it serves.

### III. Evidence over claims
Say "tested" only for what was run. Record the command, version and result for each quality gate.

### IV. Privacy
Nothing leaves the machine unless the owner approved the destination. No secrets in specs,
plans, tasks or logs.

### V. One authority
One owner per asset, timeline, specification and design document.

## Governance

- Open questions are written as [NEEDS CLARIFICATION: ...] and answered by the owner with `clarify`.
- The owner approves the spec before implementation starts.
- `analyze` must pass before implementation and again before release.
"""


def cmd_init(a):
    root = Path(a.dir)
    root.mkdir(parents=True, exist_ok=True)
    c = root / "constitution.md"
    if c.exists() and not a.force:
        print(f"{c} exists; leaving it unchanged (use --force to overwrite)")
    else:
        write(c, CONSTITUTION)
        print(f"wrote {c}")
    (root / "specs").mkdir(exist_ok=True)
    return 0


# ---------------------------------------------------------------- specify

def split_capabilities(rest):
    rest = rest.strip().rstrip(".")
    parts = re.split(r";\s*|,\s*(?:and\s+then\s+|and\s+|then\s+)?|\s+and\s+then\s+|\s+then\s+", rest)
    caps = [p.strip() for p in parts if p and p.strip()]
    return caps or [rest]


def cmd_specify(a):
    desc = " ".join(a.description.split())
    if len(desc) < 8:
        raise FlowError("the feature description is too short")
    root = Path(a.root).resolve()
    specs = root / "specs"
    specs.mkdir(parents=True, exist_ok=True)
    nums = [int(m.group(1)) for d in specs.iterdir() if d.is_dir() and (m := re.match(r"(\d{3})-", d.name))]
    num = (max(nums) + 1) if nums else 1

    benefit = None
    body = desc
    m = re.search(r"\s+so that\s+(.+)$", desc, re.I)
    if m:
        benefit, body = m.group(1).strip().rstrip("."), desc[: m.start()]
    qs = []

    def ask(question):
        qid = f"Q{len(qs) + 1}"
        qs.append((qid, question))
        return f"[{MARKER}: {qid} {question}]"

    m = ACTOR_RE.match(body)
    if m:
        actor, rest = m.group("actor").strip().lower(), m.group("rest")
        plural = actor.endswith("s") and not actor.endswith("ss")
        story_actor = f"one of the {actor}" if plural else (actor if re.match(r"(a|an|the)\s", actor) else f"a {actor}")
        given_actor = f"{actor} have" if plural else f"{story_actor} has"
    else:
        rest = body
        story_actor = ask("Who is the primary user of this feature?")
        given_actor = f"{story_actor} has"
        actor = story_actor
    caps = split_capabilities(rest)
    benefit_text = benefit or ask("What outcome makes this feature worth building?")
    title = (rest[0].upper() + rest[1:]).rstrip(".")
    if len(title) > 120:
        title = title[:120].rsplit(" ", 1)[0].rstrip(",;") + " ..."
    slug = f"{num:03d}-{slugify(rest)}"
    d = specs / slug

    lines = [f"# Feature spec: {title}", "",
             f"- ID: {slug}", "- Status: draft", f"- Created: {today()}", f"- Input: \"{desc}\"", "",
             "## Summary", "", desc, "",
             "## User stories", ""]
    reqs = []
    for i, cap in enumerate(caps, 1):
        outcome = ask(f"What observable result shows that \"{cap}\" worked (format, threshold, where it appears)?")
        lines += [f"### US{i}: {cap[0].upper() + cap[1:]}", "",
                  f"- Priority: P{min(i, 3)}",
                  f"- Story: As {story_actor}, I want to {cap}, so that {benefit_text}.", "",
                  "#### Acceptance criteria", "",
                  f"- AC{i}.1: Given {given_actor} valid input, When they {cap}, Then {outcome}.",
                  f"- AC{i}.2: Given the input for this step is missing or invalid, When they {cap}, "
                  "Then the system stops with a clear error message and leaves existing data unchanged.", ""]
        reqs.append(f"- FR-{i}: The system must let {actor} {cap}. (US{i})")
    lines += ["## Functional requirements", "", *reqs, "",
              "## Edge cases", "",
              "- Empty input, very large input and repeated runs.",
              "- An interrupted run leaves no half-written output.", "",
              "## Out of scope", "", "- Anything not named in the user stories above.", "",
              "## Open questions", ""]
    lines += [f"- {qid}: {q} -> [{MARKER}: {qid}]" for qid, q in qs]
    lines.append("")
    write(d / "spec.md", "\n".join(lines))
    print(f"wrote {d / 'spec.md'}: {len(caps)} stories, {2 * len(caps)} criteria, {len(qs)} open questions")
    return 0


# ---------------------------------------------------------------- clarify

def cmd_clarify(a):
    d, s = spec_paths(a.spec)
    text = read(s)
    if not a.answer:
        open_q = re.findall(r"^- (Q\d+): (.+?) -> \[NEEDS CLARIFICATION: Q\d+\]$", text, re.M)
        for qid, q in open_q:
            print(f"{qid}: {q}")
        print(f"{len(open_q)} open questions")
        return 0
    answers = {}
    for item in a.answer:
        if "=" not in item:
            raise FlowError(f"--answer expects Qn=text, got {item!r}")
        k, v = item.split("=", 1)
        k, v = k.strip().upper(), " ".join(v.split()).rstrip(".")
        if not re.fullmatch(r"Q\d+", k) or not v or "[" in v or "]" in v:
            raise FlowError(f"bad answer {item!r}")
        answers[k] = v
    found = set(MARKER_RE.findall(text))
    missing = set(answers) - found
    if missing:
        raise FlowError(f"no open question {', '.join(sorted(missing))}")
    log = []
    for qid, v in answers.items():
        qline = re.search(rf"^- {qid}: (.+?) -> \[NEEDS CLARIFICATION: {qid}\]$", text, re.M)
        log.append(f"- {qid}: {qline.group(1) if qline else qid} -> {v}")
        text = re.sub(rf"\[NEEDS CLARIFICATION: {qid}\b[^\]]*\]", lambda _m: v, text)
    if "## Clarifications" not in text:
        text = text.rstrip("\n") + "\n\n## Clarifications\n"
    text = text.rstrip("\n") + f"\n\n### Session {today()}\n\n" + "\n".join(log) + "\n"
    write(s, text)
    left = len(set(MARKER_RE.findall(text)))
    print(f"answered {len(answers)}; {left} open questions left")
    return 0


# ---------------------------------------------------------------- plan

def parse_tool_selection(cat):
    rows = []
    if not cat:
        return rows
    path = cat / "TOOL_SELECTION.md"
    section = None
    for n, line in enumerate(read(path).split("\n"), 1):
        h = re.match(r"^## (.+)$", line)
        if h:
            section = h.group(1).strip()
            continue
        if section and section != "Classifications" and line.startswith("|") and not re.match(r"^\|\s*(Need|---)", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3:
                rows.append({"category": section, "need": cells[0], "pick": cells[1], "reason": cells[2], "line": n})
    return rows


def parse_gates(cat):
    if not cat or not (cat / "QUALITY_GATES.md").is_file():
        return [{"gate": k, "floor": v, "line": None, "source": "built-in default"} for k, v in FALLBACK_GATES.items()]
    gates = []
    in_gates = False
    for n, line in enumerate(read(cat / "QUALITY_GATES.md").split("\n"), 1):
        if line.startswith("## "):
            in_gates = line.strip() == "## Gates"
            continue
        if in_gates and line.startswith("|") and not re.match(r"^\|\s*(Gate|---)", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2:
                gates.append({"gate": cells[0], "floor": cells[1], "reflex": cells[2] if len(cells) > 2 else "",
                              "line": n, "source": "QUALITY_GATES.md"})
    return gates


def strip_md(text):
    return re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text).replace("`", "")


def cmd_plan(a):
    d, s = spec_paths(a.spec)
    text = read(s)
    open_q = sorted(set(MARKER_RE.findall(text)) | ({"?"} if ANY_MARKER_RE.search(text) and not MARKER_RE.search(text) else set()))
    if open_q and not a.allow_open:
        raise FlowError(f"spec has open questions ({', '.join(open_q)}); answer them with clarify first")
    title, stories, acs = spec_meta(text)
    if not stories or not acs:
        raise FlowError("spec has no user stories or acceptance criteria")
    cat = find_catalogue(a.catalogue, d)
    rows = parse_tool_selection(cat)
    gates = parse_gates(cat)
    # what the feature is about: title, stories and specific outcomes (not the generic error criteria)
    specific = [body for _, body in acs if "stops with a clear error message" not in body]
    query = " ".join([title, *[x[1] for x in stories], *specific])

    picked = []
    if rows:
        scores = bm25_scores([f"{r['need']} {r['need']} {r['pick']} {r['reason']}" for r in rows], query)
        best = max(scores) if scores else 0
        order = sorted(range(len(rows)), key=lambda i: -scores[i])
        qset = set(tokenize(query))
        picked = [rows[i] for i in order[:4] if scores[i] > 0 and scores[i] >= 0.7 * best
                  and len(qset & set(tokenize(f"{rows[i]['need']} {rows[i]['pick']} {rows[i]['reason']}"))) >= 2]
    hints = [gate for words, gate in GATE_HINTS if set(tokenize(query)) & set(words)]
    gate_scores = bm25_scores([f"{g['gate']} {g['gate']} {g['floor']} {g.get('reflex', '')}" for g in gates],
                              query + " " + " ".join(hints * 2))
    gbest = max(gate_scores) if gate_scores else 0
    ranked_gates = sorted(zip(gate_scores, range(len(gates))), key=lambda x: -x[0])
    chosen = [gates[i] for sc, i in ranked_gates if sc > 0 and sc >= 0.5 * gbest][:2]
    for must in ("Engineering", "Delivery"):
        g = next((x for x in gates if x["gate"] == must), None)
        if g and g not in chosen:
            chosen.append(g)

    root = find_root(d)
    constitution = root / "constitution.md"
    articles = re.findall(r"^### ([IVX]+\. .+)$", read(constitution), re.M) if constitution.is_file() else []
    rel_spec = os.path.relpath(s, root).replace("\\", "/")
    L = [f"# Implementation plan: {title}", "",
         f"- Spec: {rel_spec}", f"- Spec digest: {digest(text)}", f"- Created: {today()}",
         f"- Catalogue: {'TOOL_SELECTION.md and QUALITY_GATES.md' if cat else 'not found; built-in gate defaults used'}", "",
         "## Approach", ""]
    if articles:
        L += ["Constitution articles that apply: " + "; ".join(articles) + ".", ""]
    for i, (us, cap) in enumerate(stories, 1):
        ids = [ac for ac, _ in acs if ac.startswith(f"AC{us[2:]}.")]
        L.append(f"{i}. {us} ({cap}): build the smallest working path, then prove {', '.join(ids)} with automated checks.")
    L += [f"{len(stories) + 1}. Run the quality gates below, record evidence, and re-run `specflow analyze`.", "",
          "## Artifacts and handoffs", "",
          "| Producer | Consumer | Artifact | Check |", "| --- | --- | --- | --- |",
          f"| Owner | Implementer | {rel_spec} (approved) | `analyze` passes; no open questions |"]
    for us, cap in stories:
        ids = [ac for ac, _ in acs if ac.startswith(f"AC{us[2:]}.")]
        L.append(f"| Implementer | Reviewer | Output of {us}: {cap} | {', '.join(ids)} |")
    L += ["| Implementer | Owner | Execution report with gate evidence | Every gate below has a result |", "",
          "## Tools from the catalogue", ""]
    if picked:
        for r in picked:
            src = f"TOOL_SELECTION.md line {r['line']}"
            L.append(f"- {r['category']} / {strip_md(r['need'])}: {strip_md(r['pick'])}. "
                     f"{strip_md(r['reason']).split('. ')[0].rstrip('.')}. ({src})")
        L.append("- Existing stack first: add a listed tool only when the spec shows a gap it closes.")
    else:
        L.append("- Existing stack. No catalogue row matched this spec.")
    L += ["", "## Risks", ""]
    risks = []
    low = query.lower()
    for words, risk in ((("licen", "commercial", "rights"), "License terms may limit commercial use; record rights per artifact."),
                        (("gpu", "vram", "render", "train", "model"), "Hardware limits (GPU memory, render time); check HARDWARE.md before installing."),
                        (("upload", "cloud", "api", "share", "publish"), "Data may leave the machine; confirm every destination with the owner."),
                        (("glb", "mesh", "3d", "viewer", "scene"), "Asset scale, materials or size may not survive export; validate the GLB.")):
        if any(w in low for w in words):
            risks.append(risk)
    for r in picked:
        cls = strip_md(r["reason"]).lower()
        if "conflict" in cls or "redundant" in cls:
            risks.append(f"{strip_md(r['pick'])}: {strip_md(r['reason']).split('. ')[0]}. Pick one authority.")
    risks += ["Scope creep beyond the user stories; anything else is out of scope.",
              "An acceptance criterion that cannot be checked automatically; rewrite it before tasks."]
    L += [f"- {x}" for x in risks]
    L += ["", "## Quality gates", ""]
    for g in chosen:
        where = f"QUALITY_GATES.md line {g['line']}" if g.get("line") else g["source"]
        L.append(f"- [ ] Gate: {g['gate']} (Floor): {strip_md(g['floor'])} ({where})")
    L.append("- [ ] Gate: Traceability: `specflow analyze` passes (every criterion has a task, every task traces to a criterion).")
    L.append("")
    write(d / "plan.md", "\n".join(L))
    print(f"wrote {d / 'plan.md'}: {len(picked)} catalogue tools, {len(chosen) + 1} gates")
    return 0


# ---------------------------------------------------------------- tasks

def cmd_tasks(a):
    d, s = spec_paths(a.spec)
    text = read(s)
    if ANY_MARKER_RE.search(text) and not a.allow_open:
        raise FlowError("spec has unresolved [NEEDS CLARIFICATION] markers; run clarify before tasks")
    if not (d / "plan.md").is_file():
        raise FlowError("no plan.md; run plan first")
    title, stories, acs = spec_meta(text)
    plan = read(d / "plan.md")
    gates = re.findall(r"^- \[ \] Gate: ([^:(]+)", plan, re.M)
    all_ids = ", ".join(ac for ac, _ in acs)
    tasks = []
    tasks.append(("Setup", "Create the feature skeleton, fixtures and a test runner that exits nonzero on failure", all_ids))
    for us, cap in stories:
        for ac, body in acs:
            if not ac.startswith(f"AC{us[2:]}."):
                continue
            then = body.split("Then", 1)[-1].strip().rstrip(".")
            tasks.append((us, f"Write a failing automated check for {ac}: then {then}", ac))
            tasks.append((us, f"Implement \"{cap}\" until the {ac} check passes", ac))
    tasks.append(("Polish", f"Run the plan's quality gates ({', '.join(g.strip() for g in gates)}) and record evidence", all_ids))
    tasks.append(("Polish", "Write the execution report: commands, versions, gate results, open issues", all_ids))
    L = [f"# Tasks: {title}", "", f"- Spec: spec.md (digest {digest(text)})", f"- Plan: plan.md (digest {digest(plan)})",
         f"- Created: {today()}", "",
         "Each task names the acceptance criteria it serves. Write the check before the code.", ""]
    phase = None
    for i, (ph, desc, trace) in enumerate(tasks, 1):
        if ph != phase:
            label = {"Setup": "Setup", "Polish": "Gates and report"}.get(ph, f"{ph}: {dict(stories).get(ph, '')}")
            L += ["", f"## {label}", ""]
            phase = ph
        L.append(f"- [ ] T{i:03d} {desc} (traces: {trace})")
    L.append("")
    write(d / "tasks.md", "\n".join(L).replace("\n\n\n", "\n\n"))
    print(f"wrote {d / 'tasks.md'}: {len(tasks)} tasks")
    return 0


# ---------------------------------------------------------------- analyze

def analyze(d, s):
    gaps = []
    text = read(s)
    title, stories, acs = spec_meta(text)
    ac_ids = [ac for ac, _ in acs]
    if not stories:
        gaps.append("spec: no user stories")
    if not acs:
        gaps.append("spec: no acceptance criteria")
    for ac, body in acs:
        if not re.search(r"\bGiven\b.+\bWhen\b.+\bThen\b", body):
            gaps.append(f"spec: {ac} is not in Given/When/Then form")
    for dup in [k for k, v in Counter(ac_ids).items() if v > 1]:
        gaps.append(f"spec: duplicate criterion {dup}")
    for us, _ in stories:
        if not any(ac.startswith(f"AC{us[2:]}.") for ac in ac_ids):
            gaps.append(f"spec: {us} has no acceptance criteria")
    unresolved = ANY_MARKER_RE.findall(text)
    if unresolved:
        gaps.append(f"spec: {len(unresolved)} unresolved [NEEDS CLARIFICATION] markers")
    plan_p, tasks_p = d / "plan.md", d / "tasks.md"
    if not plan_p.is_file():
        gaps.append("plan: missing plan.md")
    else:
        plan = read(plan_p)
        m = re.search(r"^## Quality gates\s*$(.*?)(?=^## |\Z)", plan, re.M | re.S)
        named = re.findall(r"^- \[[ xX]\] Gate: (\S.+)$", m.group(1), re.M) if m else []
        if not named:
            gaps.append("plan: names no quality gates")
        dm = re.search(r"Spec digest: (\w+)", plan)
        if dm and dm.group(1) != digest(text):
            gaps.append("plan: stale (spec.md changed after the plan was written)")
    if not tasks_p.is_file():
        gaps.append("tasks: missing tasks.md")
    else:
        tasks_text = read(tasks_p)
        tasks = TASK_RE.findall(tasks_text)
        if not tasks:
            gaps.append("tasks: no tasks found")
        covered = set()
        for tid, dup in [(k, v) for k, v in Counter(t for t, _ in tasks).items() if v > 1]:
            gaps.append(f"tasks: duplicate task id {tid}")
        for tid, rest in tasks:
            m = TRACE_RE.search(rest)
            ids = [x.strip() for x in m.group(1).split(",") if x.strip()] if m else []
            if not ids:
                gaps.append(f"tasks: {tid} traces to no acceptance criterion")
            for x in ids:
                if x not in ac_ids:
                    gaps.append(f"tasks: {tid} traces to unknown criterion {x}")
                covered.add(x)
        for ac in ac_ids:
            if ac not in covered:
                gaps.append(f"coverage: {ac} has no task")
        dm = re.search(r"Spec: spec.md \(digest (\w+)\)", tasks_text)
        if dm and dm.group(1) != digest(text):
            gaps.append("tasks: stale (spec.md changed after tasks were written)")
        pm = re.search(r"Plan: plan.md \(digest (\w+)\)", tasks_text)
        if pm and plan_p.is_file() and pm.group(1) != digest(read(plan_p)):
            gaps.append("tasks: stale (plan.md changed after tasks were written)")
    return gaps, {"stories": len(stories), "criteria": len(ac_ids)}


def cmd_analyze(a):
    d, s = spec_paths(a.spec)
    gaps, info = analyze(d, s)
    if gaps:
        print(f"analyze: {len(gaps)} gaps")
        for g in gaps:
            print(f"  - {g}")
        return 1
    tasks = len(TASK_RE.findall(read(d / "tasks.md")))
    print(f"analyze: OK ({info['stories']} stories, {info['criteria']} criteria, {tasks} tasks, all traced)")
    return 0


def cmd_approve(a):
    d, s = spec_paths(a.spec)
    if not (a.by or "").strip():
        raise FlowError("--by is required")
    gaps, _ = analyze(d, s)
    if gaps:
        raise FlowError("analyze has gaps; fix them before approval:\n  " + "\n  ".join(gaps))
    text = read(s)
    text = re.sub(r"^- Status: .*$", f"- Status: approved by {a.by.strip()} on {today()}", text, count=1, flags=re.M)
    write(s, text)
    # the status line is metadata; keep plan and tasks digests current
    plan = re.sub(r"(Spec digest: )\w+", lambda m: m.group(1) + digest(text), read(d / "plan.md"))
    write(d / "plan.md", plan)
    t = re.sub(r"(Spec: spec.md \(digest )\w+", lambda m: m.group(1) + digest(text), read(d / "tasks.md"))
    t = re.sub(r"(Plan: plan.md \(digest )\w+", lambda m: m.group(1) + digest(plan), t)
    write(d / "tasks.md", t)
    print(f"spec approved by {a.by.strip()}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="specflow")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init")
    p.add_argument("dir")
    p.add_argument("--force", action="store_true")
    p = sub.add_parser("specify")
    p.add_argument("description")
    p.add_argument("--root", default=".")
    p = sub.add_parser("clarify")
    p.add_argument("spec")
    p.add_argument("--answer", action="append", default=[])
    p = sub.add_parser("plan")
    p.add_argument("spec")
    p.add_argument("--catalogue")
    p.add_argument("--allow-open", action="store_true")
    p = sub.add_parser("tasks")
    p.add_argument("spec")
    p.add_argument("--allow-open", action="store_true")
    p = sub.add_parser("analyze")
    p.add_argument("spec")
    p = sub.add_parser("approve")
    p.add_argument("spec")
    p.add_argument("--by", required=True)
    a = ap.parse_args(argv)
    fn = {"init": cmd_init, "specify": cmd_specify, "clarify": cmd_clarify, "plan": cmd_plan,
          "tasks": cmd_tasks, "analyze": cmd_analyze, "approve": cmd_approve}[a.cmd]
    try:
        return fn(a)
    except FlowError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())

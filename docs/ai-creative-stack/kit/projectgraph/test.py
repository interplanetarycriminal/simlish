#!/usr/bin/env python3
"""Test projectgraph on a synthetic project and on the catalogue (read-only).

  python test.py [--catalogue PATH]

PATH defaults to the catalogue root two folders up. The catalogue graph is written to a
temporary folder, never into the catalogue. Writes out/result.json; exits 0 only on pass.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "projectgraph.py"
OUT = HERE / "out"

checks = []


def check(name, ok, detail=""):
    checks.append({"check": name, "pass": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def run(*args):
    p = subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout, p.stderr


def has_edge(g, src, dst, etype):
    return any(e["source"] == src and e["target"] == dst and e["type"] == etype for e in g["edges"])


def write(root, rel, content, binary=False):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if binary:
        p.write_bytes(content)
    else:
        p.write_text(content, encoding="utf-8")


def synthetic(tmp):
    root = tmp / "synthetic"
    write(root, ".gitignore", "# local\nsecret.txt\nbuild/\n")
    write(root, "README.md", """# Demo project

See the [guide](docs/guide.md) and the [install steps](docs/guide.md#install-steps).
The second usage section is [here](docs/guide.md#usage-1). ![logo](assets/logo.png)
External [site](https://example.com/x.md) is ignored. A [missing page](missing.md).
A [bad anchor](docs/guide.md#nope). A [local anchor](#demo-project).

```md
[inside a fence](fence-only.md)
# not a heading
```
""")
    write(root, "docs/guide.md", """# Guide

## Install steps

Run `src/app.py` after reading the viewer notes. Call load_config first.

## Usage

Gaussian splat viewer usage and its licence terms.

## Usage

Second usage block. Back to the [readme](../README.md).
""")
    write(root, "src/app.py", '''"""App entry point."""
import json
from util import helper


def load_config(path):
    """Read the JSON config."""
    return json.loads(open(path).read())


class AppServer:
    def run(self):
        return helper()
''')
    write(root, "src/util.py", "def helper():\n    return 1\n")
    write(root, "src/broken_syntax.py", "def oops(:\n")
    write(root, "web/main.mjs", """// import ghost from './ghost.mjs';
/* import ghost2 from './ghost2.mjs'; */
import { libFn } from './lib.mjs';
import fs from 'node:fs';
import * as THREE from 'three';
const fake = "import notReal from './fake.mjs'";
const re = /'/g;
export async function startServer(port) { return port; }
export class Viewer {}
const helperFn = (a) => a + 1;
function internalOnly() { return 2; }
export { helperFn as publicHelper };
const tpl = `export function notExported() {}`;
""")
    write(root, "web/lib.mjs", "export function libFn() { return 1; }\nexport default function () {}\n")
    write(root, "data/registry.json", json.dumps([
        {"id": "alpha", "description": "gaussian splat viewer"},
        {"id": "beta", "description": "mesh tool"},
    ]))
    write(root, "data/config.json", json.dumps({"name": "demo", "version": 2}))
    write(root, "assets/logo.png", b"\x89PNG\r\n\x1a\n\x00\x00binary", binary=True)
    write(root, "assets/blob.dat", b"abc\x00def", binary=True)
    write(root, "node_modules/pkg/index.js", "export function shouldNotAppear() {}\n")
    write(root, "out/old.md", "# Should not appear\n")
    write(root, "__pycache__/x.md", "# Nope\n")
    write(root, "secret.txt", "do not index\n")
    write(root, "build/gen.md", "# Generated\n")
    return root


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalogue", default=str(HERE.parents[1]))
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    result = {"tool": "projectgraph"}

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        root = synthetic(tmp)
        gpath = tmp / "syn.json"
        code, out, err = run("build", root, "--out", gpath)
        check("synthetic build exits 0", code == 0, err.strip()[-200:])
        g = json.loads(gpath.read_text(encoding="utf-8"))
        ids = {n["id"] for n in g["nodes"]}
        check("ignored paths absent", not any(x in i for i in ids for x in
                                             ("node_modules", "out/old", "__pycache__", "secret.txt", "build/gen")))
        check("README links to guide", has_edge(g, "file:README.md", "file:docs/guide.md", "links_to"))
        check("anchor resolves to heading node", has_edge(g, "file:README.md", "docs/guide.md#install-steps", "links_to"))
        check("duplicate heading slug -1", "docs/guide.md#usage-1" in ids and
              has_edge(g, "file:README.md", "docs/guide.md#usage-1", "links_to"))
        check("same-file anchor", has_edge(g, "file:README.md", "README.md#demo-project", "links_to"))
        check("image embed to asset", has_edge(g, "file:README.md", "file:assets/logo.png", "embeds"))
        check("fenced code ignored", "README.md#not-a-heading" not in ids and
              not any("fence-only" in b["target"] for b in g["broken"]))
        btargets = sorted(b["target"] for b in g["broken"])
        check("broken links found exactly", btargets == ["docs/guide.md#nope", "missing.md"], str(btargets))
        check("binary file is asset, not parsed", any(n["id"] == "file:assets/blob.dat" and n["kind"] == "asset"
                                                      for n in g["nodes"]))
        check("python import stdlib", has_edge(g, "file:src/app.py", "py:json", "imports"))
        check("python import local sibling", has_edge(g, "file:src/app.py", "file:src/util.py", "imports"))
        check("python symbols", {"src/app.py::load_config", "src/app.py::AppServer", "src/app.py::AppServer.run"} <= ids)
        check("python syntax error recorded", any(n["id"] == "file:src/broken_syntax.py" and "parse_error" in n
                                                  for n in g["nodes"]))
        check("js relative import", has_edge(g, "file:web/main.mjs", "file:web/lib.mjs", "imports"))
        check("js builtin and npm imports", has_edge(g, "file:web/main.mjs", "node:fs", "imports") and
              has_edge(g, "file:web/main.mjs", "npm:three", "imports"))
        check("js commented and string imports ignored", not any(x in i for i in ids for x in ("ghost", "fake.mjs")) and
              not any("ghost" in b["target"] or "fake" in b["target"] for b in g["broken"]))
        js_syms = {i for i in ids if i.startswith("web/main.mjs::")}
        want = {"web/main.mjs::startServer", "web/main.mjs::Viewer", "web/main.mjs::publicHelper"}
        check("js exported symbols exact", js_syms == want, str(sorted(js_syms)))
        check("json registry items", {"data/registry.json$alpha", "data/registry.json$beta",
                                      "data/config.json$name"} <= ids)
        check("mention of file path (inferred)", any(e["source"] == "file:docs/guide.md" and e["target"] == "file:src/app.py"
                                                     and e["type"] == "mentions" and e["confidence"] == "INFERRED"
                                                     for e in g["edges"]))
        check("mention of symbol (inferred)", has_edge(g, "file:docs/guide.md", "src/app.py::load_config", "mentions"))
        code, out, _ = run("broken", gpath)
        check("broken command exits 1 and lists 2", code == 1 and out.strip().endswith("2 broken"))
        code, out, _ = run("query", gpath, "gaussian splat viewer licence", "--json")
        hits = json.loads(out)
        top = [h["id"] for h in hits[:3]]
        check("synthetic query finds usage section", "docs/guide.md#usage" in top, str(top))
        code, out, _ = run("query", gpath, "viewer", "--budget", "300")
        check("query respects budget", len(out.rstrip("\n")) <= 300, f"{len(out)} chars")
        result["synthetic"] = {"nodes": len(g["nodes"]), "edges": len(g["edges"]), "broken": len(g["broken"])}

        # ---- the catalogue, read-only
        cat = Path(args.catalogue)
        if not (cat / "TOOL_SELECTION.md").is_file():
            check("catalogue found", False, str(cat))
        else:
            cpath = tmp / "catalogue.json"
            # kit/ is excluded: sibling tools are written concurrently and are not part of the catalogue docs.
            code, out, err = run("build", cat, "--out", cpath, "--ignore", "kit/")
            check("catalogue build exits 0", code == 0, err.strip()[-200:])
            cg = json.loads(cpath.read_text(encoding="utf-8"))
            check("README.md links to TOOL_SELECTION.md", has_edge(cg, "file:README.md", "file:TOOL_SELECTION.md", "links_to"))
            check("validate-registry.py imports json", has_edge(cg, "file:scripts/validate-registry.py", "py:json", "imports"))
            check("cdp.mjs exports findChrome", "fixtures/lib/cdp.mjs::findChrome" in {n["id"] for n in cg["nodes"]})
            check("catalogue has zero broken links", len(cg["broken"]) == 0, json.dumps(cg["broken"][:3]))
            code, out, _ = run("broken", cpath)
            check("broken command exits 0 on catalogue", code == 0)
            code, out, _ = run("query", cpath, "gaussian splat viewer licence", "--json")
            hits = json.loads(out)
            top3 = [h["id"] for h in hits[:3]]
            wanted = {"file:docs/repositories/gaussian-splatting.md", "file:docs/3d-pipeline/gaussian-splatting.md"}
            check("gaussian query top 3", bool(wanted & set(top3)), str(top3))
            code, out, _ = run("query", cpath, "gaussian splat viewer licence", "--budget", "1500", "--hops", "2")
            check("text query within budget", 0 < len(out.rstrip("\n")) <= 1500, f"{len(out)} chars")
            code, out, _ = run("stats", cpath)
            st = json.loads(out)
            (OUT / "catalogue-stats.json").write_text(json.dumps(st, indent=1), encoding="utf-8")
            (OUT / "catalogue-query.txt").write_text(
                run("query", cpath, "gaussian splat viewer licence", "--top", "5", "--budget", "2500")[1], encoding="utf-8")
            result["catalogue"] = {"nodes": st["nodes"], "edges": st["edges"], "broken": st["broken_links"],
                                   "edge_types": st["edge_types"], "gaussian_top3": top3}

    result["checks"] = checks
    result["pass"] = all(c["pass"] for c in checks)
    (OUT / "result.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(f"{sum(c['pass'] for c in checks)}/{len(checks)} checks passed")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

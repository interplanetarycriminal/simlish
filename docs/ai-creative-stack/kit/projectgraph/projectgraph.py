#!/usr/bin/env python3
"""projectgraph: a local, offline knowledge graph of a project.

  python projectgraph.py build <root> [--out out/graph.json] [--ignore PATTERN ...]
  python projectgraph.py query <graph.json> "<words>" [--hops 1] [--top 8] [--budget 4000] [--json]
  python projectgraph.py stats [graph.json]
  python projectgraph.py broken [graph.json]

Standard library only. No model, no network. Every edge carries a confidence:
EXTRACTED when it comes from syntax (a Markdown link, an import, a containment),
INFERRED when it comes from a name match in plain text (a "mention").
"""
import argparse
import ast
import bisect
import fnmatch
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

GRAPH_VERSION = 1
DEFAULT_IGNORES = [".git/", "node_modules/", "out/", "__pycache__/", ".venv/", "venv/", ".mypy_cache/",
                   ".pytest_cache/", "*.pyc", "*.pyo"]
BINARY_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico", ".tif", ".tiff", ".psd", ".exr", ".hdr",
    ".mp4", ".mov", ".webm", ".mkv", ".avi", ".mp3", ".wav", ".ogg", ".flac", ".m4a",
    ".glb", ".gltf.bin", ".bin", ".fbx", ".obj.bin", ".blend", ".ply", ".splat", ".ksplat", ".usdz", ".stl",
    ".zip", ".gz", ".tgz", ".7z", ".rar", ".tar", ".xz", ".bz2",
    ".pdf", ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".exe", ".dll", ".so", ".dylib", ".pyd", ".class", ".jar", ".wasm", ".npy", ".npz", ".pt", ".pth",
    ".safetensors", ".ckpt", ".onnx", ".sqlite", ".db",
}
MAX_TEXT_BYTES = 2_000_000
JS_EXT = {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".mts", ".cts"}
FILE_TEXT_CAP = 12000
SECTION_TEXT_CAP = 4000
JSON_TEXT_CAP = 3000
JSON_NODE_CAP = 500


# ---------------------------------------------------------------- ignore rules

class IgnoreRules:
    """A small subset of .gitignore: '#' comments, trailing '/' for directories,
    patterns with a '/' anchor to the root, others match any path component.
    Negation ('!') is not supported."""

    def __init__(self, patterns):
        self.rules = []
        for raw in patterns:
            p = raw.strip()
            if not p or p.startswith("#") or p.startswith("!"):
                continue
            dir_only = p.endswith("/")
            p = p.rstrip("/")
            anchored = "/" in p
            self.rules.append((p.lstrip("/"), dir_only, anchored))

    def ignored(self, rel, is_dir):
        parts = rel.split("/")
        for pat, dir_only, anchored in self.rules:
            if anchored:
                # match the path itself or any parent directory of it
                for i in range(len(parts), 0, -1):
                    sub = "/".join(parts[:i])
                    sub_is_dir = is_dir or i < len(parts)
                    if fnmatch.fnmatchcase(sub, pat) and (sub_is_dir or not dir_only):
                        return True
            else:
                for i, comp in enumerate(parts):
                    comp_is_dir = is_dir or i < len(parts) - 1
                    if fnmatch.fnmatchcase(comp, pat) and (comp_is_dir or not dir_only):
                        return True
        return False


def is_binary(path):
    if path.suffix.lower() in BINARY_EXT:
        return True
    try:
        with open(path, "rb") as fh:
            head = fh.read(8192)
    except OSError:
        return True
    return b"\x00" in head


def walk(root, rules):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root).as_posix()
        rel_dir = "" if rel_dir == "." else rel_dir
        keep = []
        for d in sorted(dirnames):
            rel = f"{rel_dir}/{d}" if rel_dir else d
            if not rules.ignored(rel, True):
                keep.append(d)
        dirnames[:] = keep
        for f in sorted(filenames):
            rel = f"{rel_dir}/{f}" if rel_dir else f
            if not rules.ignored(rel, False):
                files.append(rel)
    return files


# ---------------------------------------------------------------- text helpers

US_SPELLING = {"licence": "license", "licences": "licenses", "licenced": "licensed", "colour": "color",
               "colours": "colors", "behaviour": "behavior", "optimise": "optimize", "optimised": "optimized",
               "organise": "organize", "favour": "favor", "centre": "center", "defence": "defense",
               "catalog": "catalogue", "analyse": "analyze", "modelling": "modeling", "grey": "gray"}
STOPWORDS = set("""a an and are as at be by can do does for from has have how i if in into is it its of on or
that the their then there these this to was what when where which who why will with you your not no""".split())


def split_identifier(word):
    parts = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", word)
    parts = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", parts)
    return [p for p in re.split(r"[_\s]+", parts) if p]


def stem(w):
    w = US_SPELLING.get(w, w)
    if len(w) > 5 and w.endswith("ies"):
        return w[:-3] + "y"
    for suf in ("ing", "ed"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            w = w[: -len(suf)]
            if len(w) > 3 and w[-1] == w[-2] and w[-1] not in "lsz":
                w = w[:-1]
            return w
    if len(w) > 4 and w.endswith("es") and w[-3] in "sxz":
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss") and not w.endswith("us"):
        return w[:-1]
    return w


def tokenize(text):
    out = []
    for raw in re.findall(r"[A-Za-z0-9]+(?:[_'][A-Za-z0-9]+)*", text):
        pieces = split_identifier(raw)
        for p in dict.fromkeys([raw.lower()] + [x.lower() for x in pieces]):
            p = p.replace("'", "")
            if p in STOPWORDS or len(p) < 2:
                continue
            out.append(stem(p))
    return out


class BM25:
    def __init__(self, docs, k1=1.4, b=0.6):
        self.k1, self.b = k1, b
        self.tfs = [Counter(d) for d in docs]
        self.lens = [len(d) for d in docs]
        self.avg = (sum(self.lens) / len(self.lens)) if self.lens else 1.0
        df = Counter()
        for tf in self.tfs:
            df.update(tf.keys())
        n = len(docs)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def score(self, query_tokens, i):
        tf, ln, s = self.tfs[i], self.lens[i], 0.0
        for t in set(query_tokens):
            f = tf.get(t)
            if not f:
                continue
            s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * ln / (self.avg or 1)))
        return s


def github_slug(heading):
    h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)  # keep link text only
    h = h.strip().lower()
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def line_index(text):
    return [i for i, c in enumerate(text) if c == "\n"]


def line_of(nl, offset):
    return bisect.bisect_right(nl, offset - 1) + 1 if nl else 1


# ---------------------------------------------------------------- graph builder

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.edge_keys = set()
        self.broken = []

    def node(self, nid, kind, label, path=None, line=None, text=""):
        if nid not in self.nodes:
            self.nodes[nid] = {"id": nid, "kind": kind, "label": label, "path": path, "line": line, "text": text}
        return self.nodes[nid]

    def edge(self, src, dst, etype, confidence="EXTRACTED", line=None):
        key = (src, dst, etype)
        if key in self.edge_keys or src == dst:
            return
        self.edge_keys.add(key)
        e = {"source": src, "target": dst, "type": etype, "confidence": confidence}
        if line:
            e["line"] = line
        self.edges.append(e)


def file_id(rel):
    return f"file:{rel}"


class Builder:
    def __init__(self, root, ignores):
        self.root = Path(root).resolve()
        patterns = list(DEFAULT_IGNORES)
        for name in (".gitignore", ".projectgraphignore"):
            p = self.root / name
            if p.is_file():
                patterns += p.read_text(encoding="utf-8", errors="replace").splitlines()
        patterns += ignores or []
        self.rules = IgnoreRules(patterns)
        self.g = Graph()
        self.texts = {}        # rel -> text for text files
        self.slugs = {}        # rel -> set of heading slugs (Markdown)
        self.pending_links = []  # (src_rel, line, target_string)

    # -- helpers
    def rel_exists(self, rel):
        p = self.root / rel
        return p.exists(), p.is_dir()

    def ensure_target_node(self, rel, is_dir):
        nid = file_id(rel)
        if nid not in self.g.nodes:
            kind = "dir" if is_dir else "asset"
            self.g.node(nid, kind, rel, path=rel, text=rel)
        return nid

    def build(self):
        files = walk(self.root, self.rules)
        for rel in files:
            p = self.root / rel
            try:
                size = p.stat().st_size
            except OSError:
                continue
            if is_binary(p) or size > MAX_TEXT_BYTES:
                self.g.node(file_id(rel), "asset", rel, path=rel, text=rel)
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            self.texts[rel] = text
            self.g.node(file_id(rel), "file", rel, path=rel, line=1, text="")
        for rel, text in self.texts.items():
            suffix = PurePosixPath(rel).suffix.lower()
            if suffix in (".md", ".markdown", ".mdx"):
                self.markdown(rel, text)
            elif suffix == ".py":
                self.python(rel, text)
            elif suffix in JS_EXT:
                self.javascript(rel, text)
            elif suffix == ".json":
                self.json_file(rel, text)
            fnode = self.g.nodes[file_id(rel)]
            if not fnode["text"]:
                fnode["text"] = text[:FILE_TEXT_CAP]
        self.resolve_links()
        self.mentions()
        return self.g

    # -- Markdown
    def markdown(self, rel, text):
        fid = file_id(rel)
        lines = text.split("\n")
        in_fence, fence = False, ""
        stack = []  # (level, node_id)
        seen = Counter()
        sections = []  # [node_id, [body lines]]
        title = None
        for i, line in enumerate(lines, 1):
            s = line.lstrip()
            m = re.match(r"(`{3,}|~{3,})", s)
            if m:
                if not in_fence:
                    in_fence, fence = True, m.group(1)[0] * len(m.group(1))
                elif s.startswith(fence):
                    in_fence = False
                if sections:
                    sections[-1][1].append(line)
                continue
            if in_fence:
                if sections:
                    sections[-1][1].append(line)
                continue
            h = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
            if h:
                level, htext = len(h.group(1)), h.group(2).strip()
                base = github_slug(htext)
                slug = base if seen[base] == 0 else f"{base}-{seen[base]}"
                seen[base] += 1
                nid = f"{rel}#{slug}"
                self.g.node(nid, "heading", htext, path=rel, line=i)
                while stack and stack[-1][0] >= level:
                    stack.pop()
                self.g.edge(stack[-1][1] if stack else fid, nid, "contains")
                stack.append((level, nid))
                sections.append([nid, []])
                if title is None:
                    title = htext
                continue
            if sections:
                sections[-1][1].append(line)
            clean = re.sub(r"`[^`]*`", "", line)
            for target in re.findall(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)", clean):
                self.pending_links.append((rel, i, target))
            ref = re.match(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s+\"[^\"]*\")?\s*$", clean)
            if ref:
                self.pending_links.append((rel, i, ref.group(1)))
        self.slugs[rel] = {n.split("#", 1)[1] for n, _ in sections}
        for nid, body in sections:
            node = self.g.nodes[nid]
            node["text"] = (node["label"] + "\n" + "\n".join(body))[:SECTION_TEXT_CAP]
        fnode = self.g.nodes[fid]
        fnode["title"] = title or rel
        heads = " ".join(self.g.nodes[n]["label"] for n, _ in sections)
        fnode["text"] = f"{title or ''}\n{heads}\n{text}"[:FILE_TEXT_CAP]

    def resolve_links(self):
        for src, line, target in self.pending_links:
            url = urlsplit(target)
            if url.scheme or url.netloc:
                continue
            path, frag = unquote(url.path), unquote(url.fragment)
            if path:
                base = PurePosixPath(src).parent
                joined = PurePosixPath(path.lstrip("/")) if path.startswith("/") else base / path
                parts = []
                outside = False
                for part in joined.parts:
                    if part == "..":
                        if parts:
                            parts.pop()
                        else:
                            outside = True
                    elif part != ".":
                        parts.append(part)
                rel = "/".join(parts)
                if outside:
                    self.g.broken.append({"source": src, "line": line, "target": target,
                                          "reason": "points outside the project root"})
                    continue
                exists, is_dir = self.rel_exists(rel) if rel else (True, True)
                if not exists:
                    self.g.broken.append({"source": src, "line": line, "target": target, "reason": "missing file"})
                    continue
            else:
                rel, is_dir = src, False
            if not rel:
                continue
            dst = file_id(rel) if file_id(rel) in self.g.nodes else self.ensure_target_node(rel, is_dir)
            etype = "embeds" if PurePosixPath(rel).suffix.lower() in BINARY_EXT | {".svg"} else "links_to"
            if frag and rel in self.slugs:
                if frag not in self.slugs[rel]:
                    self.g.broken.append({"source": src, "line": line, "target": target, "reason": "missing heading"})
                    continue
                dst = f"{rel}#{frag}"
            self.g.edge(file_id(src), dst, etype, "EXTRACTED", line)

    # -- Python
    def python(self, rel, text):
        fid = file_id(rel)
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            self.g.nodes[fid]["parse_error"] = f"line {exc.lineno}: {exc.msg}"
            return
        doc = ast.get_docstring(tree) or ""
        self.g.nodes[fid]["title"] = doc.strip().split("\n")[0][:120] if doc else rel

        def add_symbol(node, prefix, parent):
            kind = "class" if isinstance(node, ast.ClassDef) else "function"
            name = f"{prefix}{node.name}"
            nid = f"{rel}::{name}"
            args = ""
            if kind == "function":
                args = ", ".join(a.arg for a in node.args.args)
            ds = ast.get_docstring(node) or ""
            self.g.node(nid, "symbol", f"{kind} {name}({args})" if kind == "function" else f"class {name}",
                        path=rel, line=node.lineno, text=f"{name} {args}\n{ds}"[:SECTION_TEXT_CAP])
            self.g.nodes[nid]["symbol"] = node.name
            self.g.nodes[nid]["lang"] = "python"
            self.g.edge(parent, nid, "contains")
            if kind == "class":
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        add_symbol(child, f"{name}.", nid)

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                add_symbol(node, "", fid)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.py_import(rel, alias.name, 0, node.lineno)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if node.level and not mod:
                    for alias in node.names:
                        self.py_import(rel, alias.name, node.level, node.lineno)
                else:
                    self.py_import(rel, mod, node.level, node.lineno)

    def py_import(self, rel, module, level, line):
        here = PurePosixPath(rel).parent
        candidates = []
        mpath = module.replace(".", "/")
        if level:
            base = here
            for _ in range(level - 1):
                base = base.parent
            candidates.append(base / mpath if mpath else base)
        else:
            candidates += [here / mpath, PurePosixPath(mpath)]
        for c in candidates:
            for opt in (f"{c.as_posix()}.py", f"{c.as_posix()}/__init__.py"):
                opt = opt.lstrip("./") if opt.startswith("./") else opt
                if opt in self.texts:
                    self.g.edge(file_id(rel), file_id(opt), "imports", "EXTRACTED", line)
                    return
        name = ("." * level) + module
        nid = f"py:{name}"
        self.g.node(nid, "module", name, text=f"python module {name}")
        self.g.edge(file_id(rel), nid, "imports", "EXTRACTED", line)

    # -- JavaScript
    @staticmethod
    def js_strip(src):
        """Return (no_comments, no_comments_no_strings), both the same length as src."""
        n = len(src)
        a = list(src)
        b = list(src)
        i = 0
        prev_sig = ""
        while i < n:
            c = src[i]
            nxt = src[i + 1] if i + 1 < n else ""
            if c == "/" and nxt == "/":
                j = src.find("\n", i)
                j = n if j < 0 else j
                for k in range(i, j):
                    a[k] = b[k] = " "
                i = j
                continue
            if c == "/" and nxt == "*":
                j = src.find("*/", i + 2)
                j = n if j < 0 else j + 2
                for k in range(i, j):
                    if src[k] != "\n":
                        a[k] = b[k] = " "
                i = j
                continue
            if c in "'\"`":
                j = i + 1
                while j < n and src[j] != c:
                    if src[j] == "\\":
                        j += 1
                    elif src[j] == "\n" and c != "`":
                        break
                    j += 1
                for k in range(i + 1, min(j, n)):
                    if src[k] != "\n":
                        b[k] = " "
                i = j + 1
                prev_sig = c
                continue
            if c == "/" and (prev_sig == "" or prev_sig in "(,=:[!&|?{};+-*%<>~^"):
                # regex literal
                j = i + 1
                in_class = False
                while j < n and src[j] != "\n":
                    if src[j] == "\\":
                        j += 2
                        continue
                    if src[j] == "[":
                        in_class = True
                    elif src[j] == "]":
                        in_class = False
                    elif src[j] == "/" and not in_class:
                        break
                    j += 1
                for k in range(i + 1, min(j, n)):
                    b[k] = " "
                i = j + 1
                prev_sig = "/"
                continue
            if not c.isspace():
                if c.isalnum() or c in "_$":
                    m = re.match(r"[\w$]+", src[i:i + 64])
                    word = m.group(0)
                    prev_sig = "(" if word in ("return", "typeof", "case", "in", "of", "delete", "void",
                                               "throw", "new", "yield", "await") else "a"
                    i += len(word)
                    continue
                prev_sig = c
            i += 1
        return "".join(a), "".join(b)

    def js_resolve(self, rel, spec):
        if spec.startswith((".", "/")):
            base = PurePosixPath(rel).parent
            joined = PurePosixPath(spec.lstrip("/")) if spec.startswith("/") else base / spec
            parts = []
            for part in joined.parts:
                if part == "..":
                    if parts:
                        parts.pop()
                elif part != ".":
                    parts.append(part)
            target = "/".join(parts)
            for opt in (target, *(target + e for e in (".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx")),
                        *(f"{target}/index{e}" for e in (".js", ".mjs", ".ts"))):
                if opt in self.texts or (self.root / opt).is_file():
                    return file_id(opt) if file_id(opt) in self.g.nodes else self.ensure_target_node(opt, False)
            return None
        name = spec if spec.startswith("node:") else "npm:" + "/".join(spec.split("/")[:2 if spec.startswith("@") else 1])
        self.g.node(name, "module", name, text=f"javascript module {spec}")
        return name

    def javascript(self, rel, text):
        fid = file_id(rel)
        code, bare = self.js_strip(text)
        nl = line_index(text)
        imports = []
        for pat in (r"\bimport\s+(?:[\w*{}\s,$]+?\s+from\s*)?(['\"])([^'\"\n]+)\1",
                    r"\bexport\s+(?:\*\s*(?:as\s+[\w$]+\s*)?|\{[^}]*\}\s*)from\s*(['\"])([^'\"\n]+)\1",
                    r"\bimport\s*\(\s*(['\"])([^'\"\n]+)\1\s*\)",
                    r"\brequire\s*\(\s*(['\"])([^'\"\n]+)\1\s*\)"):
            for m in re.finditer(pat, code):
                # the keyword must not sit inside a string literal
                if bare[m.start()] != code[m.start()]:
                    continue
                imports.append((m.start(), m.group(2)))
        for off, spec in imports:
            dst = self.js_resolve(rel, spec)
            line = line_of(nl, off)
            if dst is None:
                self.g.broken.append({"source": rel, "line": line, "target": spec, "reason": "unresolved import"})
            else:
                self.g.edge(fid, dst, "imports", "EXTRACTED", line)
        local_defs = {}
        for m in re.finditer(r"\b(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)\s*\(", bare):
            local_defs.setdefault(m.group(1), ("function", m.start()))
        for m in re.finditer(r"\bclass\s+([A-Za-z_$][\w$]*)", bare):
            local_defs.setdefault(m.group(1), ("class", m.start()))
        for m in re.finditer(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s+)?"
                             r"(?:function\b|\([^()]*\)\s*=>|[A-Za-z_$][\w$]*\s*=>)", bare):
            local_defs.setdefault(m.group(1), ("function", m.start()))
        exported = {}
        for m in re.finditer(r"\bexport\s+(default\s+)?(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)", bare):
            exported[m.group(2)] = ("function", m.start())
        for m in re.finditer(r"\bexport\s+(default\s+)?class\s+([A-Za-z_$][\w$]*)", bare):
            exported[m.group(2)] = ("class", m.start())
        for m in re.finditer(r"\bexport\s+(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s+)?"
                             r"(?:function\b|\([^()]*\)\s*=>|[A-Za-z_$][\w$]*\s*=>)", bare):
            exported[m.group(1)] = ("function", m.start())
        for m in re.finditer(r"\bexport\s*\{([^}]*)\}(?!\s*from)", bare):
            for item in m.group(1).split(","):
                bits = item.split()
                if not bits:
                    continue
                local = bits[0]
                public = bits[2] if len(bits) == 3 and bits[1] == "as" else local
                if local in local_defs:
                    exported[public] = (local_defs[local][0], local_defs[local][1])
        for m in re.finditer(r"\bexport\s+default\s+([A-Za-z_$][\w$]*)\s*;?\s*$", bare, re.M):
            if m.group(1) in local_defs:
                exported[m.group(1)] = local_defs[m.group(1)]
        for name, (kind, off) in sorted(exported.items(), key=lambda kv: kv[1][1]):
            line = line_of(nl, off)
            snippet = "\n".join(text.split("\n")[max(0, line - 4): line + 1])
            nid = f"{rel}::{name}"
            self.g.node(nid, "symbol", f"{kind} {name}", path=rel, line=line, text=f"{name}\n{snippet}"[:SECTION_TEXT_CAP])
            self.g.nodes[nid]["symbol"] = name
            self.g.nodes[nid]["lang"] = "javascript"
            self.g.edge(fid, nid, "contains")
        first = re.search(r"/\*\*?\s*([^*\n][^\n]*)", text) or re.search(r"//\s*([^\n]+)", text)
        self.g.nodes[fid]["title"] = first.group(1).strip()[:120] if first else rel

    # -- JSON
    def json_file(self, rel, text):
        if PurePosixPath(rel).name in ("package-lock.json", "composer.lock"):
            return
        try:
            data = json.loads(text)
        except ValueError as exc:
            self.g.nodes[file_id(rel)]["parse_error"] = str(exc)[:120]
            return
        fid = file_id(rel)

        def flat(v, out, depth=0):
            if sum(len(x) for x in out) > JSON_TEXT_CAP or depth > 6:
                return
            if isinstance(v, dict):
                for k, x in v.items():
                    out.append(str(k))
                    flat(x, out, depth + 1)
            elif isinstance(v, list):
                for x in v:
                    flat(x, out, depth + 1)
            elif v is not None:
                out.append(str(v))

        items = []
        if isinstance(data, dict):
            items = list(data.items())[:JSON_NODE_CAP]
        elif isinstance(data, list) and data and all(isinstance(x, dict) for x in data):
            keyf = next((k for k in ("id", "name", "key", "slug") if all(k in x for x in data)), None)
            if keyf:
                items = [(str(x[keyf]), x) for x in data[:JSON_NODE_CAP]]
        lines = text.split("\n")
        for key, value in items:
            out = []
            flat(value, out)
            needle = f'"{key}"'
            line = next((i for i, ln in enumerate(lines, 1) if needle in ln), None)
            nid = f"{rel}${key}"
            self.g.node(nid, "json_key", key, path=rel, line=line, text=f"{key}\n" + " ".join(out)[:JSON_TEXT_CAP])
            self.g.edge(fid, nid, "contains")

    # -- mentions (INFERRED)
    def mentions(self):
        basenames = defaultdict(list)
        for nid, n in self.g.nodes.items():
            if n["kind"] in ("file", "asset") and n["path"]:
                basenames[PurePosixPath(n["path"]).name].append(n["path"])
        symbols = defaultdict(list)
        for nid, n in self.g.nodes.items():
            name = n.get("symbol")
            if n["kind"] == "symbol" and name and "." not in nid.split("::", 1)[1]:
                distinctive = len(name) >= 5 and ("_" in name.strip("_") or re.search(r"[a-z][A-Z]", name))
                if distinctive:
                    symbols[name].append(nid)
        linked = {(e["source"], e["target"]) for e in self.g.edges}
        file_paths = {n["path"] for n in self.g.nodes.values() if n["kind"] in ("file", "asset")}
        for rel, text in self.texts.items():
            src = file_id(rel)
            nl = None
            here = PurePosixPath(rel).parent
            seen = set()
            for m in re.finditer(r"[A-Za-z0-9_][A-Za-z0-9_.\-/]*[A-Za-z0-9_]", text):
                tok = m.group(0)
                targets = []
                if "." in tok or "/" in tok:
                    t = tok.lstrip("./")
                    norm = os.path.normpath(str(here / tok)).replace("\\", "/") if not tok.startswith("/") else t
                    if t in file_paths:
                        targets.append(file_id(t))
                    elif norm in file_paths:
                        targets.append(file_id(norm))
                    elif "/" not in tok and len(basenames.get(tok, [])) == 1 and "." in tok:
                        targets.append(file_id(basenames[tok][0]))
                if tok in symbols and len(symbols[tok]) <= 3:
                    targets += symbols[tok]
                for dst in targets:
                    if dst == src or (src, dst) in linked or dst in seen:
                        continue
                    if self.g.nodes[dst].get("path") == rel:
                        continue
                    if any((src, d) in linked for d in (dst,)):
                        continue
                    seen.add(dst)
                    if nl is None:
                        nl = line_index(text)
                    self.g.edge(src, dst, "mentions", "INFERRED", line_of(nl, m.start()))


def build_graph(root, ignores=None):
    b = Builder(root, ignores)
    g = b.build()
    return {
        "version": GRAPH_VERSION,
        "root": b.root.name,
        "tool": "projectgraph",
        "nodes": sorted(g.nodes.values(), key=lambda n: n["id"]),
        "edges": g.edges,
        "broken": g.broken,
    }


# ---------------------------------------------------------------- queries

def load_graph(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def node_doc(n):
    label = n.get("label") or ""
    path = n.get("path") or ""
    title = n.get("title") or ""
    # weight names over bodies by repeating them
    return tokenize(" ".join([label] * 3 + [path.replace("/", " ")] * 2 + [title] * 2 + [n.get("text") or ""]))


def best_line(text, qtokens):
    q = set(qtokens)
    best, best_score = "", 0
    for line in (text or "").split("\n"):
        s = len(q & set(tokenize(line)))
        if s > best_score and line.strip():
            best, best_score = line.strip(), s
    return best


def query(graph, words, top=8, hops=1, max_neighbors=6):
    nodes = [n for n in graph["nodes"] if n["kind"] not in ("module",)]
    docs = [node_doc(n) for n in nodes]
    bm = BM25(docs)
    q = tokenize(words)
    scored = sorted(((bm.score(q, i), i) for i in range(len(nodes))), reverse=True)
    adj = defaultdict(list)
    for e in graph["edges"]:
        adj[e["source"]].append(("->", e))
        adj[e["target"]].append(("<-", e))
    hits = []
    for s, i in scored[:top]:
        if s <= 0:
            break
        n = nodes[i]
        frontier, seen, neigh = [n["id"]], {n["id"]}, []
        for depth in range(1, hops + 1):
            nxt = []
            for nid in frontier:
                # syntax-derived edges first, then inferred ones
                for direction, e in sorted(adj[nid], key=lambda d: (d[1]["confidence"] != "EXTRACTED", d[1]["type"] == "contains")):
                    other = e["target"] if direction == "->" else e["source"]
                    if other in seen:
                        continue
                    seen.add(other)
                    nxt.append(other)
                    neigh.append({"id": other, "via": e["type"], "dir": direction, "depth": depth,
                                  "confidence": e["confidence"], "line": e.get("line")})
            frontier = nxt
        hits.append({"id": n["id"], "kind": n["kind"], "label": n["label"], "path": n.get("path"),
                     "line": n.get("line"), "score": round(s, 3), "snippet": best_line(n.get("text"), q)[:200],
                     "neighbors": neigh[: max_neighbors * hops]})
    return hits


def format_hits(hits, budget):
    out = []
    used = 0
    for rank, h in enumerate(hits, 1):
        cite = f"{h['path']}:{h['line']}" if h.get("path") and h.get("line") else (h.get("path") or h["id"])
        block = [f"[{rank}] {h['kind']} {h['id']}  score={h['score']}  ({cite})"]
        if h["snippet"]:
            block.append(f"    > {h['snippet'][:160]}")
        for nb in h["neighbors"]:
            mark = "" if nb["confidence"] == "EXTRACTED" else " (inferred)"
            block.append(f"    {nb['dir']} {nb['via']} {nb['id']}{mark}")
        text = "\n".join(block)
        if used + len(text) + 1 > budget:
            room = budget - used - 1
            if room > 80:
                out.append(text[:room - 15].rsplit("\n", 1)[0] + "\n    [truncated]")
            break
        out.append(text)
        used += len(text) + 1
    return "\n".join(out)


def stats(graph):
    kinds = Counter(n["kind"] for n in graph["nodes"])
    etypes = Counter(e["type"] for e in graph["edges"])
    conf = Counter(e["confidence"] for e in graph["edges"])
    deg = Counter()
    for e in graph["edges"]:
        if e["type"] != "contains":
            deg[e["target"]] += 1
    return {"root": graph.get("root"), "nodes": len(graph["nodes"]), "edges": len(graph["edges"]),
            "node_kinds": dict(sorted(kinds.items())), "edge_types": dict(sorted(etypes.items())),
            "confidence": dict(conf), "broken_links": len(graph.get("broken", [])),
            "most_referenced": deg.most_common(10)}


# ---------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(prog="projectgraph", description="Local project knowledge graph (no LLM, no network).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="walk a project and write graph.json")
    b.add_argument("root")
    b.add_argument("--out", default=os.path.join("out", "graph.json"))
    b.add_argument("--ignore", action="append", default=[], help="extra ignore pattern (gitignore-like); repeatable")
    q = sub.add_parser("query", help="BM25 search over nodes, with neighbors")
    q.add_argument("graph")
    q.add_argument("words")
    q.add_argument("--hops", type=int, default=1)
    q.add_argument("--top", type=int, default=8)
    q.add_argument("--budget", type=int, default=4000, help="maximum characters of text output")
    q.add_argument("--json", action="store_true")
    s = sub.add_parser("stats", help="counts of nodes and edges")
    s.add_argument("graph", nargs="?", default=os.path.join("out", "graph.json"))
    br = sub.add_parser("broken", help="list dangling links and unresolved imports; exit 1 if any")
    br.add_argument("graph", nargs="?", default=os.path.join("out", "graph.json"))
    br.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.cmd == "build":
        graph = build_graph(a.root, a.ignore)
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(graph, fh, ensure_ascii=False, separators=(",", ":"))
        st = stats(graph)
        print(f"wrote {a.out}: {st['nodes']} nodes, {st['edges']} edges, {st['broken_links']} broken links")
        return 0
    graph = load_graph(a.graph)
    if a.cmd == "query":
        hits = query(graph, a.words, a.top, a.hops)
        if a.json:
            print(json.dumps(hits, indent=1, ensure_ascii=False))
        else:
            print(format_hits(hits, a.budget) or "no matches")
        return 0
    if a.cmd == "stats":
        print(json.dumps(stats(graph), indent=1))
        return 0
    if a.cmd == "broken":
        broken = graph.get("broken", [])
        if a.json:
            print(json.dumps(broken, indent=1))
        else:
            for x in broken:
                print(f"{x['source']}:{x['line']}: {x['target']} ({x['reason']})")
            print(f"{len(broken)} broken")
        return 1 if broken else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())

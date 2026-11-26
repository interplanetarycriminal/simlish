#!/usr/bin/env python3
"""Validate documentation: required files, local links, diagrams, workflows, JSON files, secrets and private paths.

  python scripts/validate-documentation.py
"""
import importlib.util
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SVG_NS = "{http://www.w3.org/2000/svg}"

REQUIRED = """README.md AGENTS.md CLAUDE.md DESIGN.md AI_CREATIVE_STACK.md AI_CREATIVE_STACK_VISUAL.md ARCHITECTURE.md
REPOSITORIES.md SOURCES.md WORKFLOWS.md TOOL_SELECTION.md COMPATIBILITY.md INSTALLATION.md HARDWARE.md SECURITY.md
QUALITY_GATES.md CHANGELOG.md TAXONOMY.md
docs/3d-pipeline/image-to-3d.md docs/3d-pipeline/retopology.md docs/3d-pipeline/uv-and-materials.md
docs/3d-pipeline/rigging-and-skinning.md docs/3d-pipeline/animation-and-physics.md docs/3d-pipeline/gaussian-splatting.md
docs/3d-pipeline/comfyui-orchestration.md docs/3d-pipeline/asset-validation.md docs/3d-pipeline/export-contracts.md
registry/repositories.json registry/repositories.txt registry/core-repositories.txt registry/supplementary-repositories.txt
registry/compatibility.json registry/schema.json
prompts/activate-creative-agent.md prompts/creative-director.md prompts/frontend-design.md prompts/motion-design.md
prompts/3d-technical-artist.md prompts/3d-asset-factory.md prompts/spatial-reconstruction.md prompts/video-production.md
prompts/project-intelligence.md
templates/creative-brief.md templates/design-system.md templates/toolchain-plan.md templates/asset-manifest.json
templates/mesh-quality-report.md templates/rig-validation-report.md templates/shot-list.md templates/execution-report.md
scripts/validate-registry.py scripts/check-repositories.py scripts/validate-documentation.py""".split()

WORKFLOWS = """premium-website application-interface interactive-3d illustration-and-animation cinematic-video full-creative-pipeline
persistent-intelligence design-system-extraction 3d-asset-factory animation-ready-character spatial-reconstruction
comfyui-asset-processing surreal-cinematic-3d interactive-learning""".split()

DIAGRAMS = """collection-provenance creative-architecture 3d-asset-production mesh-vs-gaussian rigging-and-skinning
comfyui-orchestration agent-decision-loop design-system-intelligence persistent-intelligence cinematic-video
asset-handoffs capability-matrix hardware-execution compatibility-overlap""".split()

EMBEDS = {
    "README.md": ["collection-provenance", "creative-architecture", "3d-asset-production", "mesh-vs-gaussian", "capability-matrix", "compatibility-overlap"],
    "AI_CREATIVE_STACK_VISUAL.md": ["agent-decision-loop", "creative-architecture", "3d-asset-production", "mesh-vs-gaussian", "asset-handoffs"],
}

SECRETS = [r"gh[pousr]_[A-Za-z0-9]{30,}", r"github_pat_[A-Za-z0-9_]{40,}", r"sk-ant-[A-Za-z0-9-]{20,}", r"\bsk-[A-Za-z0-9]{32,}",
           r"AKIA[0-9A-Z]{16}", r"\bhf_[A-Za-z0-9]{30,}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----", r"xox[baprs]-[A-Za-z0-9-]{10,}",
           r"AIza[0-9A-Za-z_-]{35}", r"\bagw_[A-Za-z0-9]{16,}"]
PRIVATE = [r"[A-Za-z]:\\Users\\", r"/Users/[a-z]", r"[A-Za-z]:[\\/]Aitrepreneur", r"AppData[\\/]Local", r"scratchpad"]
TEXT = {".md", ".json", ".py", ".mjs", ".js", ".html", ".mmd", ".svg", ".txt", ".yml", ".yaml"}


def fail(msg):
    raise SystemExit(f"FAIL {msg}")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    for rel in REQUIRED:
        p = ROOT / rel
        if not p.is_file():
            fail(f"missing required file {rel}")
        if rel != "CLAUDE.md" and p.stat().st_size < 200:
            fail(f"{rel} looks like a placeholder ({p.stat().st_size} bytes)")

    files = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and "node_modules" not in p.parts]
    md = [p for p in files if p.suffix == ".md"]

    def anchors(doc):
        heads = re.findall(r"^#+\s+(.+)$", doc.read_text(encoding="utf-8"), re.M)
        return {re.sub(r"[^\w\- ]", "", h.strip().lower()).replace(" ", "-") for h in heads}

    links = 0
    for path in md:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)\s]+)\)", text):
            url = urlsplit(target)
            if url.scheme or url.netloc:
                continue
            dest = (path.parent / unquote(url.path)) if url.path else path
            if not dest.exists():
                fail(f"{path.relative_to(ROOT)} links to missing {target}")
            if url.fragment and dest.suffix == ".md" and url.fragment not in anchors(dest):
                fail(f"{path.relative_to(ROOT)} links to missing heading {target}")
            links += 1

    for p in files:
        if p.suffix == ".json":
            json.loads(p.read_text(encoding="utf-8"))

    svgs = sorted((ROOT / "docs/diagrams").glob("*.svg"))
    mmds = sorted((ROOT / "docs/diagrams").glob("*.mmd"))
    if [p.stem for p in svgs] != [p.stem for p in mmds]:
        fail("every diagram needs an .svg and an .mmd with the same name")
    for name in DIAGRAMS:
        if not (ROOT / f"docs/diagrams/{name}.svg").is_file():
            fail(f"missing required diagram {name}")
    for p in svgs:
        root = ET.parse(p).getroot()
        if root.tag != f"{SVG_NS}svg" or not root.get("viewBox") or root.get("role") != "img":
            fail(f"{p.name}: needs an svg root with viewBox and role=img")
        if root.find(f"{SVG_NS}title") is None or root.find(f"{SVG_NS}desc") is None:
            fail(f"{p.name}: needs <title> and <desc>")
        if "prefers-color-scheme:dark" not in p.read_text(encoding="utf-8").replace(" ", ""):
            fail(f"{p.name}: no dark theme")
        if not re.search(r"^\s*flowchart ", (p.with_suffix(".mmd")).read_text(encoding="utf-8"), re.M):
            fail(f"{p.stem}.mmd: not a Mermaid flowchart")

    renderer = load("render_diagrams", ROOT / "scripts/render-diagrams.py")
    auto = 0
    for mmd in mmds:
        if mmd.read_text(encoding="utf-8").startswith(renderer.MARK):
            auto += 1
            if renderer.render(mmd) != mmd.with_suffix(".svg").read_text(encoding="utf-8"):
                fail(f"{mmd.stem}.svg is stale: run scripts/render-diagrams.py")
    matrix = load("render_matrix", ROOT / "scripts/render-matrix.py")
    records = json.loads((ROOT / "registry/repositories.json").read_text(encoding="utf-8"))
    if matrix.svg(records) != (ROOT / "docs/diagrams/capability-matrix.svg").read_text(encoding="utf-8"):
        fail("capability-matrix.svg is stale: run scripts/render-matrix.py")

    for doc, names in EMBEDS.items():
        text = (ROOT / doc).read_text(encoding="utf-8")
        for n in names:
            if f"docs/diagrams/{n}.svg" not in text:
                fail(f"{doc} does not embed {n}.svg")
            if f"docs/diagrams/{n}.mmd" not in text:
                fail(f"{doc} does not link the editable source {n}.mmd")

    index = (ROOT / "WORKFLOWS.md").read_text(encoding="utf-8")
    for w in WORKFLOWS:
        p = ROOT / f"docs/workflows/{w}.md"
        if not p.is_file():
            fail(f"missing workflow {w}")
        if f"docs/workflows/{w}.md" not in index:
            fail(f"workflow {w} is not listed in WORKFLOWS.md")
        text = p.read_text(encoding="utf-8")
        if not re.search(r"!\[[^\]]+\]\(\.\./diagrams/[\w-]+\.svg\)", text) or "[Editable diagram]" not in text:
            fail(f"workflow {w} needs an embedded diagram and an editable source link")
        if "QUALITY_GATES.md" not in text:
            fail(f"workflow {w} does not reference the quality gates")
    extra = sorted(p.stem for p in (ROOT / "docs/workflows").glob("*.md") if p.stem not in WORKFLOWS)
    if extra:
        fail(f"unlisted workflow files: {extra}")

    evidence = 0
    for f in sorted(ROOT.glob("fixtures/*/out/*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        if "pass" in data:
            evidence += 1
            if data["pass"] is not True:
                fail(f"recorded fixture evidence {f.relative_to(ROOT)} shows a failed check")
    if evidence < 4:
        fail(f"expected fixture evidence for both fixtures, found {evidence} files")

    scanned = 0
    for p in files:
        if p.suffix.lower() not in TEXT:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        scanned += 1
        for pat in SECRETS:
            if re.search(pat, text):
                fail(f"possible secret in {p.relative_to(ROOT)} (pattern {pat})")
        if p.name != "validate-documentation.py":
            for pat in PRIVATE:
                if re.search(pat, text):
                    fail(f"private machine path in {p.relative_to(ROOT)} (pattern {pat})")

    print(f"Validated {len(REQUIRED)} required files, {links} local links in {len(md)} Markdown files, "
          f"{len(svgs)} diagrams ({auto} rendered from source plus the generated matrix), {len(WORKFLOWS)} workflows, {evidence} passing fixture records, "
          f"and scanned {scanned} text files for secrets and private paths")


if __name__ == "__main__":
    main()

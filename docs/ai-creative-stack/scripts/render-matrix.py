#!/usr/bin/env python3
"""Render docs/diagrams/capability-matrix.svg and its Mermaid source from the registry.

  python scripts/render-matrix.py          # write both files
  python scripts/render-matrix.py --check  # exit 1 if either is out of date
"""
import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPS = [
    ("Creative direction", "CD", "#733ed0"), ("Design critique", "DC", "#198047"), ("Design-system extraction", "DX", "#733ed0"),
    ("Project intelligence", "PI", "#733ed0"), ("Specification", "SP", "#596b84"), ("Discovery", "DI", "#596b84"),
    ("Prototyping", "PR", "#2363cf"), ("Component generation", "CG", "#2363cf"), ("Frontend implementation", "FE", "#2363cf"),
    ("Illustration", "IL", "#a05212"), ("Visual effects", "FX", "#a05212"), ("Animation", "AN", "#087d73"),
    ("3D authoring", "3A", "#a05212"), ("3D rendering", "3R", "#a05212"), ("Image-to-3D", "I3", "#a05212"), ("Retopology", "RT", "#a05212"),
    ("Texturing", "TX", "#a05212"), ("Rigging", "RG", "#a05212"), ("3D orchestration", "3O", "#a05212"), ("Spatial reconstruction", "SR", "#087d73"),
    ("Shot planning", "SH", "#087d73"), ("Video composition", "VC", "#087d73"), ("Video editing", "VE", "#bf315c"), ("Upscaling", "UP", "#bf315c"),
    ("Media processing", "MP", "#bf315c"),
]
GROUPS = {"A": "Creative direction", "B": "Design and prototyping", "C": "Frontend and creative coding", "D": "Illustration and animation",
          "E": "Core 3D", "F": "Video and post-production", "G": "AI-assisted 3D (source C)", "H": "Supplementary candidates"}
STYLE = """<style>
svg{font-family:system-ui,-apple-system,sans-serif} .bg{fill:#fbfcff} text{fill:#152137} .sub{fill:#465773} .grid{stroke:#e3e8f0;stroke-width:1} .band{fill:#f1f4f9} .na{fill:#b8c2d3}
@media(prefers-color-scheme:dark){.bg{fill:#101829} text{fill:#f2f5fb} .sub{fill:#c2cee1} .grid{stroke:#2a3850} .band{fill:#16223a} .na{fill:#52627c}}
</style>"""

ROW, COL, LEFT, TOP = 24, 30, 250, 300


def svg(records):
    n_groups = len(GROUPS)
    width = LEFT + COL * len(CAPS) + 40
    height = TOP + ROW * len(records) + 34 * n_groups + 90
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
           '<title id="title">Capability matrix</title>',
           f'<desc id="desc">{len(records)} references against {len(CAPS)} capabilities. Filled: primary. Ring: supporting. Square: tested by a fixture here. Dot: not applicable. Generated from the registry.</desc>',
           STYLE, f'<rect width="{width}" height="{height}" rx="22" class="bg"/>',
           '<text x="36" y="48" font-size="29" font-weight="750">Capability matrix</text>',
           f'<text x="37" y="75" font-size="15" font-weight="450" class="sub">{len(records)} references × {len(CAPS)} capabilities, from pinned documentation. No ratings: a mark says what a tool is for, not how good it is.</text>']
    # legend
    lx = 37
    for label, draw in (("Primary", lambda x, y: f'<circle cx="{x}" cy="{y}" r="6.5" fill="#596b84"/>'),
                        ("Supporting", lambda x, y: f'<circle cx="{x}" cy="{y}" r="5.5" fill="none" stroke="#596b84" stroke-width="2.2"/>'),
                        ("Primary, tested here", lambda x, y: f'<rect x="{x - 6}" y="{y - 6}" width="12" height="12" rx="2" fill="#198047"/>'),
                        ("Not applicable", lambda x, y: f'<circle cx="{x}" cy="{y}" r="1.8" class="na"/>')):
        out.append(draw(lx + 6, 101) + f'<text x="{lx + 18}" y="106" font-size="13" class="sub">{label}</text>')
        lx += 40 + 7.2 * len(label)
    out.append(f'<text x="{lx}" y="106" font-size="13" class="sub">Unverified capabilities are not drawn: every mark has pinned evidence.</text>')
    for i, (name, abbr, colour) in enumerate(CAPS):
        x = LEFT + COL * i + COL / 2
        out.append(f'<text transform="translate({x + 4:.0f},{TOP - 10}) rotate(-58)" font-size="12.5" font-weight="600" fill="{colour}" style="fill:{colour}">{escape(name)}</text>')
    y = TOP
    for key, title in GROUPS.items():
        group = [r for r in records if r["category"] == key]
        out.append(f'<rect x="24" y="{y + 4}" width="{width - 48}" height="26" rx="7" class="band"/>'
                   f'<text x="36" y="{y + 22}" font-size="13" font-weight="700">{key}. {escape(title)}</text>')
        y += 34
        for r in group:
            out.append(f'<line x1="36" y1="{y + ROW}" x2="{width - 28}" y2="{y + ROW}" class="grid"/>'
                       f'<text x="44" y="{y + 17}" font-size="13" font-weight="550">{escape(r["name"])}</text>')
            tested = r["smoke_test"]["status"] == "passed"
            for i, (name, abbr, colour) in enumerate(CAPS):
                cx, cy = LEFT + COL * i + COL / 2, y + ROW / 2 + 1
                if name in r["primary_capabilities"]:
                    out.append(f'<rect x="{cx - 6}" y="{cy - 6}" width="12" height="12" rx="2" fill="#198047"/>' if tested
                               else f'<circle cx="{cx}" cy="{cy}" r="6.5" fill="{colour}"/>')
                elif name in r["secondary_capabilities"]:
                    out.append(f'<circle cx="{cx}" cy="{cy}" r="5.5" fill="none" stroke="{colour}" stroke-width="2.2"/>')
                else:
                    out.append(f'<circle cx="{cx}" cy="{cy}" r="1.8" class="na"/>')
            y += ROW
    out.append(f'<text x="37" y="{height - 28}" font-size="12.5" class="sub">Source: registry/repositories.json. Regenerate with python scripts/render-matrix.py.</text>')
    return "\n".join(out) + "\n</svg>\n"


def mermaid(records):
    lines = ["%% Generated by scripts/render-matrix.py from registry/repositories.json. Edit the registry, not this file.",
             "%% Capability to reference map: solid = primary, dashed = supporting.", "flowchart LR"]
    for i, (name, abbr, _) in enumerate(CAPS):
        lines.append(f'    C{i}["{name}"]')
    for r in records:
        node = r["id"].replace("-", "_")
        lines.append(f'    {node}["{r["name"]}"]')
        for i, (name, _, _) in enumerate(CAPS):
            if name in r["primary_capabilities"]:
                lines.append(f"    C{i} --> {node}")
            elif name in r["secondary_capabilities"]:
                lines.append(f"    C{i} -.-> {node}")
    return "\n".join(lines) + "\n"


def main():
    records = json.loads((ROOT / "registry/repositories.json").read_text(encoding="utf-8"))
    unknown = {c for r in records for c in r["primary_capabilities"] + r["secondary_capabilities"]} - {c[0] for c in CAPS}
    if unknown:
        print(f"Capabilities missing from the matrix: {sorted(unknown)}", file=sys.stderr)
        return 1
    files = {ROOT / "docs/diagrams/capability-matrix.svg": svg(records), ROOT / "docs/diagrams/capability-matrix.mmd": mermaid(records)}
    if "--check" in sys.argv:
        stale = [p.name for p, t in files.items() if not p.exists() or p.read_text(encoding="utf-8") != t]
        if stale:
            print("Out of date: " + ", ".join(stale) + ". Run python scripts/render-matrix.py", file=sys.stderr)
            return 1
        return 0
    for p, t in files.items():
        p.write_text(t, encoding="utf-8", newline="\n")
    print("wrote capability matrix")
    return 0


if __name__ == "__main__":
    sys.exit(main())

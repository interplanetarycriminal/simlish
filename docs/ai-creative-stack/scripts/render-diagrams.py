#!/usr/bin/env python3
"""Render layered Mermaid flowcharts in docs/diagrams to SVG in the catalogue style.

Supports the subset the catalogue uses: `flowchart TD`; nodes written as ID["Title • subtitle"]:::class or,
for decisions, ID{"Question"}; `class A,B name` assignments; edges `-->`, `-.->` and `---` with optional
|labels|; classDef fill/stroke colours; and `subgraph ID ["Label"]` ... `end`, drawn as a dashed boundary.
Only files whose first comment line reads `%% render: auto` are rendered; hand-drawn SVGs are left alone.

  python scripts/render-diagrams.py          # write SVGs
  python scripts/render-diagrams.py --check  # exit 1 if any SVG is out of date
"""
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIAGRAMS = ROOT / "docs/diagrams"
MARK = "%% render: auto"

NODE = re.compile(r'^\s*(\w+)([\[{])"([^"]+)"[\]}](?::::(\w+))?\s*$')
ASSIGN = re.compile(r'^\s*class\s+([\w,]+)\s+(\w+)\s*$')
SUBGRAPH = re.compile(r'^\s*subgraph\s+(\w+)\s*\["([^"]+)"\]\s*$')
END = re.compile(r'^\s*end\s*$')
EDGE = re.compile(r'^\s*(\w+)\s*(-->|-\.->|---)\s*(?:\|([^|]*)\|\s*)?(\w+)\s*$')
CLASS = re.compile(r'^\s*classDef\s+(\w+)\s+fill:(#[0-9a-fA-F]{6}),stroke:(#[0-9a-fA-F]{6})')
META = re.compile(r'^%%\s*(title|desc):\s*(.+)$')
RANK = re.compile(r'^\s*%%\s*rank:\s*(\w+)\s+(\d+)\s*$')  # optional layout hint: minimum row for a node

STYLE = """<style>
svg{font-family:system-ui,-apple-system,sans-serif} .bg{fill:#fbfcff} text{fill:#152137} .sub{fill:#465773} .line{stroke:#62738d;fill:none;stroke-width:2} .dash{stroke-dasharray:6 5} .panel{fill:#fff;stroke:#d0d9e7} .lab{fill:#fbfcff} .arrow{fill:#62738d}
@media(prefers-color-scheme:dark){.bg{fill:#101829} text{fill:#f2f5fb} .sub{fill:#c2cee1} .line{stroke:#a4b7d1} .panel{fill:#182439;stroke:#435570} .lab{fill:#101829} .arrow{fill:#a4b7d1}}
</style>"""

W_NODE, H_ONE, H_TWO, GAP_X, GAP_Y, PAD = 300, 54, 72, 76, 64, 36
TOP = 108


def parse(text):
    nodes, edges, classes, meta, groups = {}, [], {}, {}, {}
    current = None
    for line in text.splitlines():
        if m := META.match(line):
            meta[m[1]] = m[2].strip()
        elif m := RANK.match(line):
            meta.setdefault("ranks", {})[m[1]] = int(m[2])
        elif m := SUBGRAPH.match(line):
            current = m[1]
            groups[current] = {"label": m[2], "members": []}
        elif END.match(line):
            current = None
        elif m := NODE.match(line):
            title, _, sub = m[3].partition(" • ")
            nodes[m[1]] = {"title": title.strip(), "sub": sub.strip(), "cls": m[4], "decision": m[2] == "{"}
            if current:
                groups[current]["members"].append(m[1])
        elif m := EDGE.match(line):
            edges.append({"a": m[1], "b": m[4], "dash": m[2] == "-.->", "arrow": m[2] != "---", "label": (m[3] or "").strip()})
        elif m := ASSIGN.match(line):
            for n in m[1].split(","):
                if n in nodes:
                    nodes[n]["cls"] = m[2]
        elif m := CLASS.match(line):
            classes[m[1]] = {"fill": m[2], "stroke": m[3]}
    return nodes, edges, classes, meta, groups


def ranks(nodes, edges, hints=None):
    order = list(nodes)
    rank = {n: (hints or {}).get(n, 0) for n in order}
    forward = [e for e in edges if order.index(e["a"]) < order.index(e["b"])]
    for _ in order:
        for e in forward:
            rank[e["b"]] = max(rank[e["b"]], rank[e["a"]] + 1)
    return rank


def render(path):
    nodes, edges, classes, meta, groups = parse(path.read_text(encoding="utf-8"))
    rank = ranks(nodes, edges, meta.get("ranks"))
    rows = {}
    for n in nodes:
        rows.setdefault(rank[n], []).append(n)
    widest = max(len(r) for r in rows.values())
    width = max(745, PAD * 2 + widest * W_NODE + (widest - 1) * GAP_X + 160)
    pos, y = {}, TOP
    for r in sorted(rows):
        row = rows[r]
        h = max(H_TWO if nodes[n]["sub"] else H_ONE for n in row)
        span = len(row) * W_NODE + (len(row) - 1) * GAP_X
        x0 = (width - span) / 2
        for i, n in enumerate(row):
            pos[n] = (x0 + i * (W_NODE + GAP_X), y, h)
        y += h + GAP_Y
    height = y - GAP_Y + PAD + 8

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-labelledby="title desc">',
           f'<title id="title">{escape(meta.get("title", path.stem))}</title><desc id="desc">{escape(meta.get("desc", ""))}</desc>',
           STYLE,
           '<defs><marker id="end" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path class="arrow" d="M0 0 7 3.5 0 7z"/></marker></defs>',
           f'<rect width="{width:.0f}" height="{height:.0f}" rx="22" class="bg"/>',
           f'<text x="36" y="48" font-size="29" font-weight="750">{escape(meta.get("title", path.stem))}</text>',
           f'<text x="37" y="75" font-size="15" font-weight="450" class="sub">{escape(meta.get("desc", ""))}</text>']
    for g in groups.values():  # dashed boundaries sit behind everything else
        if not g["members"]:
            continue
        xs = [pos[n][0] for n in g["members"]]
        ys = [pos[n][1] for n in g["members"]]
        x0, y0 = min(xs) - 18, min(ys) - 34
        x1 = max(xs) + W_NODE + 18
        y1 = max(pos[n][1] + pos[n][2] for n in g["members"]) + 16
        out.append(f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{x1 - x0:.0f}" height="{y1 - y0:.0f}" rx="18" class="line dash" style="stroke-width:1.5"/>'
                   f'<text x="{x0 + 14:.0f}" y="{y0 + 20:.0f}" font-size="12.5" font-weight="650" class="sub">{escape(g["label"])}</text>')
    labels = []
    loops = 0
    order = list(nodes)
    incoming = {}
    for e in edges:
        if rank[e["b"]] > rank[e["a"]]:
            incoming[e["b"]] = incoming.get(e["b"], 0) + 1
    for e in edges:
        ax, ay, ah = pos[e["a"]]
        bx, by, bh = pos[e["b"]]
        cls = "line dash" if e["dash"] else "line"
        mark = ' marker-end="url(#end)"' if e["arrow"] else ""
        if rank[e["a"]] == rank[e["b"]]:  # same row: straight across between facing sides
            left_to_right = ax < bx
            x1 = ax + W_NODE if left_to_right else ax
            x2 = bx if left_to_right else bx + W_NODE
            y1 = y2 = ay + ah / 2
            d = f"M{x1:.0f} {y1:.0f} H{x2 + (-2 if left_to_right else 2):.0f}"
            lx, ly = min(x1, x2) + 6, y1 - 10
        elif rank[e["b"]] - rank[e["a"]] > 1 and abs(ax - bx) < 1:  # skip edge in one column: route down the left side
            x1, y1 = ax, ay + ah / 2
            x2, y2 = bx, by + bh / 2
            xl = ax - 40
            d = f"M{x1:.0f} {y1:.0f} H{xl:.0f} V{y2:.0f} H{x2 - 2:.0f}"
            lx, ly = xl - 7.1 * len(e["label"]) - 14, (y1 + y2) / 2 + 5
        elif order.index(e["a"]) < order.index(e["b"]):
            x1, y1 = ax + W_NODE / 2, ay + ah
            x2, y2 = bx + W_NODE / 2, by
            if abs(x1 - x2) < 1:
                d = f"M{x1:.0f} {y1:.0f} V{y2 - 2:.0f}"
                lx, ly = x1 + 10, (y1 + y2) / 2 + 5
            else:
                # Turn just above the target row, so an edge that skips rows never crosses a card's row mid-way.
                mid = y2 - GAP_Y / 2 if rank[e["b"]] - rank[e["a"]] > 1 else (y1 + y2) / 2
                d = f"M{x1:.0f} {y1:.0f} V{mid:.0f} H{x2:.0f} V{y2 - 2:.0f}"
                if incoming.get(e["b"], 0) > 1:  # merging edges share the last segment: label their own horizontal run
                    tw = 7.1 * len(e["label"]) + 12
                    lx = x1 + 10 if x2 > x1 else x1 - tw - 6
                    ly = mid - 8
                else:
                    lx, ly = x2 + 10, mid + (y2 - mid) / 2 + 5
        else:  # loop back on the right-hand side
            x1, y1 = ax + W_NODE, ay + ah / 2
            x2, y2 = bx + W_NODE, by + bh / 2
            xr = max(px + W_NODE for px, _, _ in pos.values()) + 36 + 18 * loops  # outside every box
            loops += 1
            d = f"M{x1:.0f} {y1:.0f} H{xr:.0f} V{y2:.0f} H{x2 + 2:.0f}"
            lx, ly = x1 + 8, y1 - 9
        out.append(f'<path d="{d}" class="{cls}"{mark}/>')
        if e["label"]:
            labels.append((lx, ly, e["label"]))
    for lx, ly, text in labels:
        w = 7.1 * len(text) + 12
        out.append(f'<rect x="{lx - 4:.0f}" y="{ly - 14:.0f}" width="{w:.0f}" height="20" rx="5" class="lab"/>'
                   f'<text x="{lx + 2:.0f}" y="{ly:.0f}" font-size="12.5" font-weight="560" class="sub">{escape(text)}</text>')
    for n, (x, y, h) in pos.items():
        node = nodes[n]
        colour = classes.get(node["cls"], {"stroke": "#596b84"})["stroke"]
        if node["decision"]:  # decisions carry a small diamond instead of the bar
            cx, cy = x + 16, y + h / 2
            out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{W_NODE}" height="{h}" rx="13" class="panel" style="stroke-dasharray:4 3"/>'
                       f'<path d="M{cx:.0f} {cy - 9:.0f} L{cx + 9:.0f} {cy:.0f} L{cx:.0f} {cy + 9:.0f} L{cx - 9:.0f} {cy:.0f}Z" fill="{colour}"/>')
        else:
            out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{W_NODE}" height="{h}" rx="13" class="panel"/>'
                       f'<rect x="{x + 12:.0f}" y="{y + h / 2 - 12:.0f}" width="7" height="24" rx="3.5" fill="{colour}"/>')
        if node["sub"]:
            out.append(f'<text x="{x + 28:.0f}" y="{y + h / 2 - 4:.0f}" font-size="16.5" font-weight="720">{escape(node["title"])}</text>'
                       f'<text x="{x + 28:.0f}" y="{y + h / 2 + 16:.0f}" font-size="13" font-weight="450" class="sub">{escape(node["sub"])}</text>')
        else:
            out.append(f'<text x="{x + 28:.0f}" y="{y + h / 2 + 6:.0f}" font-size="17" font-weight="720">{escape(node["title"])}</text>')
    out.append("</svg>\n")
    return "\n".join(out)


def main():
    check = "--check" in sys.argv
    stale = []
    for mmd in sorted(DIAGRAMS.glob("*.mmd")):
        if not mmd.read_text(encoding="utf-8").startswith(MARK):
            continue
        svg = render(mmd)
        target = mmd.with_suffix(".svg")
        if check:
            if not target.exists() or target.read_text(encoding="utf-8") != svg:
                stale.append(target.name)
        else:
            target.write_text(svg, encoding="utf-8", newline="\n")
            print(f"rendered {target.relative_to(ROOT)}")
    if check and stale:
        print("Out of date: " + ", ".join(stale) + ". Run python scripts/render-diagrams.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

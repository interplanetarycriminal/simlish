#!/usr/bin/env python3
"""Generate one guide per registry entry in docs/repositories/ and the REPOSITORIES.md index.

The registry is the single source of truth. Edit registry/repositories.json, then run:
  python scripts/build-guides.py          # write guides and index
  python scripts/build-guides.py --check  # exit 1 if any generated file is out of date
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    "A": "Creative direction and design intelligence",
    "B": "Design and prototyping",
    "C": "Frontend components and creative coding",
    "D": "Illustration and animation",
    "E": "Core 3D authoring and rendering",
    "F": "Video composition and post-production",
    "G": "AI-assisted 3D asset production",
    "H": "Supplementary research candidates",
}
SOURCE = {"A": "Source A", "B": "Source B", "A+B": "Sources A and B", "C": "Source C", "supplementary": "Supplementary"}


def link(i):
    return f"[{i}]({i}.md)"


def relation(e):
    consider = ", ".join(link(x) for x in e["overlapping_tools"]) or "the existing project toolchain"
    comp = ", ".join(link(x) for x in e["complementary_tools"])
    return f"{e['conflicts'][0]} Consider {consider}." + (f" Complementary tools include {comp}." if comp else "")


def short(sha):
    return sha[:12] if sha else "unknown"


def fmt(v, empty="Not documented"):
    if v is None or v == "" or v == []:
        return empty
    if isinstance(v, list):
        return ", ".join(v)
    return str(v)


def guide(e):
    m = e["maintenance"]
    base = e["verified_url"].split("/tree/")[0]
    lines = [f"# {e['name']}", "", e["intended_use"], "",
             f"> {CATEGORIES[e['category']]} · {SOURCE[e['source_group']]} · smoke test: **{e['smoke_test']['status']}**", "",
             "## Evidence and maintenance", ""]
    lines += [f"- [Canonical reference]({e['verified_url']})"]
    if e["original_url"].rstrip("/").lower() != e["verified_url"].rstrip("/").lower():
        lines += [f"- Original reference: {e['original_url']} (status: {e['verification_status']}; see security notes for the evidence)"]
    lines += [f"- Verified {e['verification_date']} against default branch `{m['default_branch']}` at [`{short(e['inspected_commit'])}`]({base}/commit/{e['inspected_commit']}).",
              f"- GitHub reports archive state **{str(m['archived']).lower()}** and a repository push at `{m['last_repository_push']}`. Push activity is a maintenance signal, not a quality rating.",
              f"- Attribution: {e['attribution_status']}", ""]
    lines += [f"- [{s.rsplit('/', 1)[-1]}]({s})" for s in e["documentation_sources"]] + [""]

    h = e["hardware"] or {}
    lines += ["## Runtime, hardware and setup", "",
              f"- **Type** {e['tool_type']}." + (f" Primary language {e['language']}." if e.get("language") else ""),
              f"- **Platforms** {fmt(e['supported_platforms'], 'Unverified')}.",
              f"- **Runtime** {e['runtime_requirements']}",
              f"- **Execution** {e['execution']}.",
              f"- **Agent paths** {fmt(e['supported_agents'])}. Client claims describe documentation and remain untested here unless the smoke test says otherwise.",
              f"- **Configuration** {e['configuration']}",
              f"- **Credentials and services** {e['credentials_required']}", ""]
    if e["model"] or (h.get("gpu") not in (None, "not applicable", "none")):
        lines += ["| Hardware | Documented value |", "| --- | --- |",
                  f"| GPU | {fmt(h.get('gpu'), 'Unverified')} |",
                  f"| Minimum VRAM | {fmt(h.get('min_vram_gb'), 'Not documented')}{' GB' if isinstance(h.get('min_vram_gb'), (int, float)) else ''} |",
                  f"| Recommended VRAM | {fmt(h.get('recommended_vram_gb'), 'Not documented')}{' GB' if isinstance(h.get('recommended_vram_gb'), (int, float)) else ''} |",
                  f"| System RAM | {fmt(h.get('system_ram_gb'), 'Not documented')}{' GB' if isinstance(h.get('system_ram_gb'), (int, float)) else ''} |",
                  f"| Storage | {fmt(h.get('storage'))} |",
                  f"| CPU fallback | {fmt(h.get('cpu_fallback'))} |",
                  f"| Training versus inference | {fmt(h.get('training_vs_inference'))} |"]
        if e["model"]:
            mo = e["model"]
            lines += [f"| Weights | {fmt(mo.get('weights_source'))} ({fmt(mo.get('access'), 'access unknown')}) |",
                      f"| Weights size | {fmt(mo.get('weights_size'))} |"]
        if h.get("notes"):
            lines += [f"| Notes | {h['notes']} |"]
        lines += [""]
    if e["installation"]:
        lines += ["Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.", "",
                  "```sh", e["installation"].strip(), "```", ""]
    else:
        lines += ["No install command is documented upstream. Follow the pinned documentation.", ""]

    lines += ["## Contracts and selection", "", "| Boundary | Contract |", "| --- | --- |",
              f"| Input | {fmt(e['inputs'])} |", f"| Output | {fmt(e['outputs'])} |",
              f"| Primary | {fmt(e['primary_capabilities'])} |", f"| Supporting | {fmt(e['secondary_capabilities'], '—')} |", "",
              relation(e), ""]
    if e.get("integration_notes"):
        lines += [e["integration_notes"], ""]
    for c in e["conflicts"][1:]:
        lines += [f"- {c}"]
    if len(e["conflicts"]) > 1:
        lines += [""]

    lines += ["## Craft notes", ""] + [f"- {n}" for n in e["craft_notes"]] + [""]
    ex = e["examples"] or {}
    lines += ["## Examples", "",
              f"1. **Independent** {ex.get('independent') or 'Not recorded.'}",
              f"2. **Combined** {ex.get('combined') or 'Not recorded.'}", "",
              "For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.", ""]
    st = e["smoke_test"]
    lines += ["## Smoke test", "", f"**{st['status']}**." + (f" {st['evidence']}" if st.get("evidence") else " No run is recorded."), ""]

    lines += ["## Security, privacy and licensing", ""] + [f"- {s}" for s in e["security_notes"]] + [f"- {p}" for p in e["privacy_notes"]] + [""]
    lines += [f"**Software license** {e['license']}."]
    if e.get("model_license"):
        lines += ["", f"**Model license** {e['model_license']}."]
    lines += ["", f"**Commercial use** {e['commercial_use_notes']}", ""]
    if e.get("evidence"):
        lines += ["## Evidence quotes", "", "| Field | Upstream wording and file |", "| --- | --- |"]
        lines += [f"| {k} | {str(v).replace('|', '/')} |" for k, v in e["evidence"].items()] + [""]
    return "\n".join(lines)


def index(records):
    lines = ["# Repository index", "",
             "One guide per reference, generated from [the registry](registry/repositories.json) by `scripts/build-guides.py`. "
             "Each guide carries pinned evidence, hardware, licences, craft notes and a smoke-test status. "
             "The [taxonomy](TAXONOMY.md) sorts the same references by how they behave in a workflow, and [SOURCES.md](SOURCES.md) records where each came from.", ""]
    for k, title in CATEGORIES.items():
        group = [e for e in records if e["category"] == k]
        lines += [f"## {k}. {title}", "", "| Reference | Type | Primary | Licence | Source | Smoke test |", "| --- | --- | --- | --- | --- | --- |"]
        for e in group:
            lic = e["license"] if len(e["license"]) < 48 else e["license"][:45] + "…"
            lines += [f"| [{e['name']}](docs/repositories/{e['id']}.md) | {e['tool_type']} | {', '.join(e['primary_capabilities'])} | {lic} | {SOURCE[e['source_group']]} | {e['smoke_test']['status']} |"]
        lines += [""]
    return "\n".join(lines)


def main():
    check = "--check" in sys.argv
    records = json.loads((ROOT / "registry/repositories.json").read_text(encoding="utf-8"))
    targets = {ROOT / f"docs/repositories/{e['id']}.md": guide(e) for e in records}
    targets[ROOT / "REPOSITORIES.md"] = index(records)
    stale = []
    for path, text in targets.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(path.name)
        else:
            path.write_text(text, encoding="utf-8", newline="\n")
    if check and stale:
        print("Out of date: " + ", ".join(stale) + ". Run python scripts/build-guides.py", file=sys.stderr)
        return 1
    if not check:
        print(f"wrote {len(targets)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())

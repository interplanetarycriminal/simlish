#!/usr/bin/env python3
"""Validate the registry against its schema, its source counts, its URL lists and the generated guides.

  python scripts/validate-registry.py

Uses the jsonschema package when it is installed; otherwise runs the structural checks below,
which cover the same required fields. Documentation, links, diagrams and secrets are checked by
scripts/validate-documentation.py.
"""
import importlib.util
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"total": 44, "post_associated": 32, "supplementary": 12, "A_only": 10, "B_only": 10, "A+B": 5, "C": 7}


def require(condition, message):
    if not condition:
        raise SystemExit(f"FAIL {message}")


def github(value):
    u = urlsplit(value)
    return u.scheme == "https" and u.netloc == "github.com"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    records = json.loads((ROOT / "registry/repositories.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "registry/schema.json").read_text(encoding="utf-8"))
    required = schema["items"]["required"]

    try:
        import jsonschema
        errors = list(jsonschema.Draft202012Validator(schema).iter_errors(records))
        require(not errors, "schema: " + "; ".join(f"{list(e.path)[:3]} {e.message[:120]}" for e in errors[:5]))
        mode = "jsonschema"
    except ImportError:
        mode = "built-in"

    ids = [r["id"] for r in records]
    require(len(ids) == len(set(ids)), "duplicate ids")
    idset = set(ids)
    for key in ("original_url", "verified_url"):
        urls = [r[key].rstrip("/").lower() for r in records]
        require(len(urls) == len(set(urls)), f"duplicate {key}")

    for r in records:
        slug = r["id"]
        require(list(r) == required, f"{slug}: fields differ from schema order")
        require(re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug), f"{slug}: invalid id")
        require(github(r["original_url"]) and github(r["verified_url"]), f"{slug}: non-GitHub URL")
        date.fromisoformat(r["verification_date"])
        if r["verification_status"] in ("verified", "redirected"):
            sha = r["inspected_commit"] or ""
            require(re.fullmatch(r"[a-f0-9]{40}", sha), f"{slug}: invalid SHA")
            pinned = [s for s in r["documentation_sources"] if github(s)]
            require(pinned and all(sha in s for s in pinned), f"{slug}: GitHub evidence not pinned to the inspected commit")
        if r["verification_status"] == "redirected":
            require(any("404" in s or "renamed" in s or "canonical" in s for s in r["security_notes"]), f"{slug}: redirect without recorded evidence")
        for key in ("complementary_tools", "overlapping_tools"):
            require(set(r[key]) <= idset - {slug}, f"{slug}: unknown {key}")
        require(not set(r["complementary_tools"]) & set(r["overlapping_tools"]), f"{slug}: tool both complementary and overlapping")
        require(r["conflicts"] and r["conflicts"][0].startswith("Skip "), f"{slug}: first conflict must start with 'Skip '")
        require(len(r["craft_notes"]) >= 2, f"{slug}: needs at least two craft notes")
        if r["model"]:
            require(r["model_license"] or r["model"].get("weights_license"), f"{slug}: model without a model licence statement")
        if r["smoke_test"]["status"] == "passed":
            require(r["smoke_test"]["evidence"], f"{slug}: passed smoke test without evidence")

    by = {r["id"]: r for r in records}
    for r in records:
        for x in r["complementary_tools"]:
            require(r["id"] in by[x]["complementary_tools"], f"{r['id']} -> {x}: complementary link not mirrored")
        for x in r["overlapping_tools"]:
            require(r["id"] in by[x]["overlapping_tools"], f"{r['id']} -> {x}: overlap link not mirrored")

    groups = [r["source_group"] for r in records]
    counts = {"total": len(records), "post_associated": sum(g != "supplementary" for g in groups), "supplementary": groups.count("supplementary"),
              "A_only": groups.count("A"), "B_only": groups.count("B"), "A+B": groups.count("A+B"), "C": groups.count("C")}
    require(counts == EXPECTED, f"source counts {counts} differ from {EXPECTED}")
    require(counts["A_only"] + counts["A+B"] == 15 and counts["B_only"] + counts["A+B"] == 15, "sources A and B must each hold 15")

    lists = {
        "registry/repositories.txt": [r["original_url"] for r in records],
        "registry/core-repositories.txt": [r["original_url"] for r in records if r["source_group"] != "supplementary"],
        "registry/supplementary-repositories.txt": [r["original_url"] for r in records if r["source_group"] == "supplementary"],
    }
    for path, expected in lists.items():
        require((ROOT / path).read_text(encoding="utf-8").splitlines() == expected, f"{path} differs from the registry")

    compat = json.loads((ROOT / "registry/compatibility.json").read_text(encoding="utf-8"))
    kinds = set(compat["classifications"])
    for pair in compat["pairs"]:
        require(set(pair["tools"]) <= idset | set(compat.get("non_registry_tools", [])), f"compatibility: unknown tool in {pair['tools']}")
        require(pair["classification"] in kinds, f"compatibility: unknown classification {pair['classification']}")
        require(pair.get("evidence"), f"compatibility: {pair['tools']} has no evidence status")

    builder = load_module("build_guides", ROOT / "scripts/build-guides.py")
    for r in records:
        guide = ROOT / f"docs/repositories/{r['id']}.md"
        require(guide.is_file(), f"{r['id']}: missing guide")
        require(guide.read_text(encoding="utf-8") == builder.guide(r), f"{r['id']}: guide is stale, run scripts/build-guides.py")
    require((ROOT / "REPOSITORIES.md").read_text(encoding="utf-8") == builder.index(records), "REPOSITORIES.md is stale")
    require(sorted(p.stem for p in (ROOT / "docs/repositories").glob("*.md")) == sorted(ids), "guides without registry entries")

    smoke = {}
    for r in records:
        smoke[r["smoke_test"]["status"]] = smoke.get(r["smoke_test"]["status"], 0) + 1
    print(f"Validated {len(records)} records ({mode} schema check): {counts['post_associated']} post-associated "
          f"(A {counts['A_only']}, B {counts['B_only']}, shared {counts['A+B']}, C {counts['C']}) and {counts['supplementary']} supplementary; "
          f"{sum(r['verification_status'] == 'verified' for r in records)} verified, {sum(r['verification_status'] == 'redirected' for r in records)} redirected; "
          f"smoke tests {smoke}; {len(compat['pairs'])} compatibility pairs; guides and index current")


if __name__ == "__main__":
    main()

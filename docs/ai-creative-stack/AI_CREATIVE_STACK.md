# AI Creative Engineering Stack: maintenance

Agents use the [operating manual](AI_CREATIVE_STACK_VISUAL.md). This page is for whoever maintains the catalogue.

## The source of truth

[registry/repositories.json](registry/repositories.json) holds every fact about every tool, validated by [registry/schema.json](registry/schema.json). The 75 guides, [REPOSITORIES.md](REPOSITORIES.md), the URL lists in `registry/*.txt` and the capability matrix are generated from it. Never edit a generated file by hand.

| Generated file | Generator |
| --- | --- |
| `docs/repositories/*.md`, `REPOSITORIES.md`, `registry/*.txt` | `scripts/build-guides.py` |
| `docs/diagrams/capability-matrix.svg` and `.mmd` | `scripts/render-matrix.py` |
| Every other `docs/diagrams/*.svg` | `scripts/render-diagrams.py`, from the `.mmd` beside it |

## Add or update a reference

1. Resolve the original URL through the GitHub API. Record the canonical owner and repository, the default branch and the head commit. Keep the original URL when it redirects, and record the evidence for any correction. Never substitute a different project silently.
2. Read the README, license and the manifests, requirements or setup files at that commit. For models, read the Hugging Face card or API metadata for size, gating and license.
3. Fill every schema field. Use null or "Unverified" when the evidence is missing. Quote the evidence for hardware, installation, licenses and formats in `evidence`.
4. Set `source_group` and `attribution_status` from provenance, separately from verification.
5. Run a smoke test only when it needs no gated or multi-gigabyte download, and record the result in `smoke_test`.
6. Add the pair to [registry/compatibility.json](registry/compatibility.json) when it competes with or complements an existing tool.
7. Regenerate and validate:

```sh
python scripts/build-guides.py
python scripts/render-matrix.py
python scripts/render-diagrams.py
python scripts/validate-registry.py
python scripts/validate-documentation.py
```

Update [SOURCES.md](SOURCES.md) if the counts change. The validator holds the expected counts and fails until both agree.

## Recheck drift

`python scripts/check-repositories.py` reports URL, default-branch and archive changes. Push activity is a maintenance signal. Archive state, release availability and production readiness are separate questions. Resolve package versions from their distribution upstream before installing.

## Rerun the fixtures

```sh
node fixtures/seekable-scene/render.mjs
cd fixtures/blender-glb && blender --background --factory-startup --python-exit-code 1 --python make_asset.py -- out && node check.mjs
```

Commit the new evidence files. The documentation validator fails when a committed `evidence.json` records a failed check.

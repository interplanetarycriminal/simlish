# Changelog

## 2026-11-26 (V3.2: 53 references)

- **Nine references added by the user**, kept as their own source group (D) and category (I, motion films, explainers and engines): Huashu Motion, anything2explainer, OpenScreen, OneTake, Lemo Opuscar, EffectCraft, GSAP, ComfyUI and Remotion's skills. All resolved; each has a pinned guide with evidence.
- **Smoke tests.** GSAP ran inside kit/framecap's new GSAP check. A running local ComfyUI answered its `/system_stats` API.
- **framecap seeks GSAP.** It pauses `gsap.globalTimeline` and seeks it per frame, from the earliest tween start: within 0.054 px in its test.
- **Diagrams remapped.** Provenance shows four sources and 53 in total. The architecture names GSAP, EffectCraft, OpenScreen and ComfyUI. The overlap map adds the explainer-pipeline choice and the tested GSAP-to-framecap link. The capability matrix has 53 rows.
- **Licences no longer steer recommendations.** The README's licence section is replaced by security notes. Licence facts stay in the registry and SECURITY.md.
- **Finding.** Four independent film tools (OneTake, Lemo Opuscar, anything2explainer, Huashu Motion) render a page whose state is a function of time: the catalogue's time contract.

## 2026-11-26 (V3.1: the kit)

- **Our own versions.** [`kit/`](kit/README.md) adds 14 original tools and 4 skills that do what the catalogue's key tools do, written for this catalogue rather than copied from upstream. Each has a self-building test, and `kit/run-tests.py` runs them all.
  - 3D chain: inflate3d (image to watertight textured GLB), remesh (QEM to a face budget), autorig (centreline chain, own weights, swim clip), materialforge (tileable PBR), splatview (mesh to Gaussian PLY plus our own WebGL2 splat renderer) and assetpipe (batch workflows with versioned manifests).
  - Design, motion and intelligence: designlint, tokenextract, framecap, silencecut, sketchy, projectgraph, decisionlog and specflow.
- **Bugs found by looking, then fixed.**
  - autorig first rooted the fish at its tail, because the fin had the most vertices; it now roots at the thicker end.
  - assetpipe let an optional side step become the delivery.
  - framecap captured frames from the wrong moment under load. Compositor-thread CSS animations ignore a JavaScript seek, so it now runs animations on the main thread and captures until settled.
  - splatview's depth sort mixed float32 and float64 keys.
- **Shared helper.** `fixtures/lib/cdp.mjs` accepts extra Chrome flags and serves SVG and CSS with correct types. The GLB viewer can track any bone with `?bone=`.

## 2026-11-26 (V3)

- **44 references.** Added the seven repositories from source C (SAM 3D Objects, Stable Fast 3D, MeshAnything V2, UniRig, Dream Textures, ComfyUI-3D-Pack, Gaussian Splatting) and twelve supplementary candidates, kept as a separate collection. Attribution is tracked apart from verification; see [SOURCES.md](SOURCES.md).
- **One correction.** `Manavarya09/designlang` returned 404; the npm package `designlang` names `Manavarya09/design-extract` as its repository, recorded as `redirected` with that evidence.
- **Registry V3.** A JSON Schema, category, source group, attribution, hardware, model and model-license, execution, privacy, examples, smoke-test status and quoted evidence for every entry; complementary and overlap links are mirrored; `compatibility.json` classifies 23 pairs by evidence level and role; core and supplementary URL lists.
- **Generated guides.** All 44 guides and the index are now built from the registry by `scripts/build-guides.py`, so they cannot drift.
- **3D subsystem.** Nine `docs/3d-pipeline/` guides; `scripts/blender/validate_asset.py`, a headless geometry, UV, color-space and rig validator; and the Blender → GLB → Three.js fixture, which passed and recorded five handoff lessons (glTF seam splitting, FBX clip renaming, importer helper meshes, creases despite valid weights, four influences).
- **Seven new workflows**, for fourteen in total, each with objectives and rejected alternatives: persistent intelligence, design-system extraction, 3D asset factory, animation-ready character, spatial reconstruction, ComfyUI asset processing, and an original surreal cinematic 3D piece.
- **Fourteen system diagrams** plus workflow diagrams, 25 in all, rendered from Mermaid sources with decisions, dashed boundaries and row hints; a 44 × 25 capability matrix generated from the registry.
- **New pages**: SOURCES, HARDWARE, DESIGN, eight templates, four prompts and smoke-test records. Security now covers risky installers, memory-tool privacy and a license table for code and weights. Quality gates add geometry, UV and materials, rigging, physics and animation, and Gaussian reconstruction.
- **Validation.** `validate-registry.py` checks schema, counts, lists, mirrored links and generated guides. `validate-documentation.py` checks required files, links, diagram accessibility and freshness, workflow structure, secrets and private paths.
- **Smoke tests.** FFmpeg's documented example, Rough.js 4.6.6 and Spec Kit 1.4.5 passed. No model was run and no weights were downloaded.

## 2026-11-26 (v2)

- **Ran something.** Added the [seekable scene fixture](fixtures/seekable-scene/README.md): a Three.js lesson that plays live and renders to MP4 from one module, with a dependency-free DevTools renderer. Seekable, repeatable, pause-to-play and stream checks pass on Chrome 158, three r187 and FFmpeg 7.1. This is the catalogue's first runtime-verified route.
- **New contract and workflow.** The [time contract](docs/contracts/time-contract.md) defines scene state as a function of story time and classifies clocks as wall, stepped or seekable. The [interactive 3D learning](docs/workflows/interactive-learning.md) workflow adds beats, teaching moves, a prediction before the reveal and a learner test.
- **Taxonomy.** [TAXONOMY.md](TAXONOMY.md) sorts all 25 references by whether they make or narrow options, their surface, whether they check their own output and their clock.
- **Tiered gates with numbers.** [Quality gates](QUALITY_GATES.md) now have Floor, Reflex and Finish tiers, starting thresholds and new time-contract and learning gates.
- **Craft notes.** Every registry entry and guide carries two or three notes on what the tool is best at and where it fails, from the pinned READMEs.
- **Corrections from the pinned READMEs.** Meng To Skills gains 3D rendering and illustration (30 Three.js skills, 14 illustration styles). Video Use documents HyperFrames and Remotion overlays, so they are complementary rather than overlapping. HyperFrames documents a Remotion port skill. Scarlet documents transparent ProRes 4444 motion graphics. Remotion publishes `@remotion/three`. Line Art Animation documents DevTools frame capture into FFmpeg.
- **Diagrams from source.** `scripts/render-diagrams.py` renders the workflow diagrams from their `.mmd` files with labelled handoffs. Two new diagrams. The overlap diagram names its two sets by content.
- **Stricter validation.** Explicit UTF-8 reads (on Windows the default codec silently misreads the catalogue's arrows and dashes), guide-to-registry drift checks for relationships and craft notes, stale-diagram and workflow-index checks, and fixture evidence must pass. `check-repositories.py` also watches the default branch and accepts `GITHUB_TOKEN`.
- `CLAUDE.md` imports `AGENTS.md` instead of duplicating it. Added an interactive learning prompt.

## 2026-11-26

Initial catalogue of 25 commit-pinned upstream references, six production workflows, agent entry points, registry validation and editable visual explainers. Setup was verified through documentation inspection. Toolchain runtime tests belong to projects selecting those tools.

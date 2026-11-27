# The kit: our own versions

Original, working implementations of what the catalogue's key tools do. Each was written for this catalogue from first principles, not copied from the upstream project it stands in for. Each tool runs locally and offline, and has a README and a test that builds its own fixtures and checks real properties of the output.

```sh
python kit/run-tests.py            # all 15 tool tests; writes kit/results.json
python kit/run-tests.py remesh     # one tool
```

## The 3D chain

```text
image ──inflate3d──▶ GLB v1 ──remesh──▶ GLB v2 (budget) ──autorig──▶ GLB v3 (rig + clip)
                                   │                                       │
                                   ├──mesh2splat──▶ Gaussian PLY ──▶ splatview
                                   └──validate_asset.py (Blender) ◀────────┘
materialforge ──▶ tileable PBR maps            assetpipe runs the whole chain per image, with manifests
```

| Tool | What it does | Stands in for |
| --- | --- | --- |
| [inflate3d](inflate3d/README.md) | One image to a closed, textured GLB by inflating the silhouette; optional depth map | SAM 3D Objects, Stable Fast 3D, TRELLIS.2 |
| [remesh](remesh/README.md) | Quadric-error decimation to a face budget, manifold-safe, UVs kept | MeshAnything V2, Blender retopology |
| [autorig](autorig/README.md) | Centreline bone chain, our own segment weights, swim or bend clip; GLB and FBX | UniRig |
| [materialforge](materialforge/README.md) | Six tileable PBR presets with correct color spaces and normals from height | Dream Textures |
| [splatview](splatview/README.md) | Mesh to 3D Gaussian Splatting PLY, synthetic scenes, and our own WebGL2 splat renderer | Gaussian Splatting viewers |
| [assetpipe](assetpipe/README.md) | JSON workflows over image batches, a versioned manifest per asset, rejects with reasons | ComfyUI-3D-Pack batch processing |

## Design, motion and intelligence

| Tool | What it does | Stands in for |
| --- | --- | --- |
| [designlint](designlint/README.md) | 17 deterministic rules on rendered pages at four widths, tiered Floor, Reflex and Finish | Impeccable's detector, Hallmark's gates |
| [tokenextract](tokenextract/README.md) | Color, type, spacing, radius, shadow, breakpoint and motion tokens from a page; DTCG JSON, CSS and a draft DESIGN.md | Designlang (design-extract) |
| [framecap](framecap/README.md) | Frame-exact video of any seekable page or CSS animation; H.264, ProRes 4444 alpha, PNG; audio mux; ffprobe checks | HyperFrames and Remotion rendering, Motion Canvas export |
| [silencecut](silencecut/README.md) | Silence-based cutting with an EDL, 30 ms fades, A/V sync and a self-checking render | Video Use's editing pass |
| [sketchy](sketchy/README.md) | Seeded hand-drawn SVG shapes and paths with hachure and zigzag fills | Rough.js |
| [projectgraph](projectgraph/README.md) | Local knowledge graph of files, headings, symbols, links and imports, with BM25 search | Graphify |
| [decisionlog](decisionlog/README.md) | Append-only, hash-chained, approval-gated decision log with private-text stripping | Claude Mem |
| [specflow](specflow/README.md) | Constitution, spec, clarify, plan, tasks and a traceability check | Spec Kit |
| [workledger](workledger/README.md) | Work packages checked for cycles and scope overlap, run in waves under a monitor, with an execution ledger, a decision log that needs two alternatives, and a measured comparison with direct execution | The strategy layer (no upstream reference) |

## Skills

Guidance-type references are skills upstream, so our versions are skills too, written to drive the kit's tools.

| Skill | Stands in for |
| --- | --- |
| [creative-direction](skills/creative-direction/SKILL.md) | Taste Skill, Anthropic Frontend Design, UI/UX Pro Max, Meng To's direction skills |
| [design-critique](skills/design-critique/SKILL.md) | Impeccable's commands, Hallmark's fresh review |
| [blender-craft](skills/blender-craft/SKILL.md) | Blender Skills, Blender MCP's agent loop, Dream Loop's generate-and-judge cycle |
| [shot-planning](skills/shot-planning/SKILL.md) | Video Shotcraft's planning, HyperFrames and Remotion workflows, Video Use's pass |

## Coverage of the 75 references

| Covered by the kit | References |
| --- | --- |
| A kit tool | SAM 3D Objects, Stable Fast 3D, TRELLIS.2 (inflate3d) · MeshAnything V2 (remesh) · UniRig (autorig) · Dream Textures (materialforge) · Gaussian Splatting (splatview, viewing only) · ComfyUI-3D-Pack (assetpipe) · Impeccable, Hallmark (designlint) · Designlang (tokenextract) · HyperFrames, Remotion, Motion Canvas (framecap) · Video Use, Scarlet's cutting (silencecut) · Rough.js (sketchy) · Graphify (projectgraph) · Claude Mem (decisionlog) · Spec Kit (specflow) |
| A kit skill | Taste Skill, Anthropic Frontend Design, UI/UX Pro Max, Meng To Skills, Blender Skills, Blender MCP, Dream Loop, Video Shotcraft, Remotion's skills, and the film pipelines anything2explainer, OneTake, Huashu Motion and Lemo Opuscar (shot-planning plus framecap cover their render path, not their styles, narration or music) |
| Used as is, not rebuilt | Three.js and FFmpeg are the runtimes the kit is built on. GSAP is used as is too: framecap seeks GSAP pages. Motion, Theatre.js and React Three Fiber are seekable libraries that framecap's approach already covers (tested in fixtures/expressive-motion) |
| Not rebuilt | Penpot, Open Design and Stitch (design applications and hosted generation); Figma Context MCP (needs Figma); Astryx, Magic UI, React Bits and 21st MCP (component libraries, which are project-specific by nature); Sakuga VFX and Line Art Animation (hand-crafted art styles); Anatomy (explainer illustration); Real-ESRGAN (needs a trained super-resolution model); OpenScreen and EffectCraft (desktop applications); ComfyUI (assetpipe batches the kit's own tools, not diffusion graphs); Awesome DESIGN.md and Awesome Claude Skills (curated lists; the kit's skills are our own small collection). The game references (engines, physics, editors, audio, Ink, servers) and pixelfx, motionmaxxing and reanimate: mature libraries and editors with no gap to fill; the fixtures test them directly instead |
| Strategy layer | No reference; the article that prompted it is pending. workledger is the kit's own runner for it |

## Test results

One run of `python kit/run-tests.py` on 2026-11-27: **15 of 15 tools pass** (projectgraph rerun after the V7 files landed; see below). Windows 11, Python 3.14, Node 24, Chrome 158 headless with software WebGL, Blender 5.2.2, FFmpeg 7.1.

| Tool | Checks | Time | Key result |
| --- | --- | --- | --- |
| inflate3d | 9/9 | 40 s | Watertight; silhouette IoU 0.913; Blender Floor and Reflex pass |
| remesh | 17/17 | 39 s | 8,032 → 1,600 faces, mean error 0.044 % of size, 99.4 % volume kept |
| autorig | 12/12 | 29 s | Root at the head; tail sweeps 0.10 m; weights normalized, at most 4 influences |
| materialforge | all | 20 s | Six presets tile in both directions; normals unit length within 0.0063 |
| splatview | 6/6 | 24 s | Texture colors 98.7–100 % correct; renders byte-identical when repeated |
| assetpipe | 15/15 | 144 s | Two toys accepted, empty image rejected with a reason, stages byte-repeatable |
| designlint | 24/24 | 4 s | Bad page: every planted problem found; clean page: zero findings |
| tokenextract | 31/31 | 3 s | Planted brand colors, spacing scale, fonts, radii, breakpoint and easing recovered |
| framecap | 6/6 | 43 s | CSS within 0.27 px, GSAP within 0.054 px; ProRes alpha; audio mux |
| silencecut | 6/6 | 4 s | Three segments found; click-free cuts; A/V sync off by 0 frames |
| sketchy | 5/5 | 2 s | Deterministic by seed; 0 of about 26,000 fill samples outside their shapes |
| projectgraph | 32/32 | 5 s | Catalogue graph with 0 broken links; the right Gaussian docs ranked first |
| decisionlog | 39/39 | 4 s | Tampering detected; private text never written; redaction keeps the chain valid |
| specflow | 29/29 | 4 s | Full flow traced; all five planted breaks fail `analyze` |
| workledger | 17/17 | 6 s | Governed 8 attempts against 16 for direct execution on 7 packages; repeated failure stopped early, out-of-scope write caught, blocked dependent skipped |

Per-tool details are in each tool's `out/result.json`. `kit/results.json` is written by a full run.

## Honest limits

- No tool here is a trained model. inflate3d reads depth from the silhouette, not from learned shape priors.
- remesh decimates; it does not lay out quad edge flow.
- autorig handles single chains, not bipeds.
- splatview renders splats but does not train them from photographs.
- silencecut cuts on loudness, not on words.

Each README states its own limits. Where a learned model is needed, use the catalogue's guide for the upstream tool.

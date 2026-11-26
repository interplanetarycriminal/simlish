# Integrated workflows

Each workflow states its objectives, prerequisites, tool selection, rejected alternatives, execution steps, handoff contracts, diagram, quality gates and deliverables. Use one as a starting point and cut what the brief does not need.

## Web and product

1. [Premium marketing website](docs/workflows/premium-website.md). Creative direction → design system → components → implementation → motion → critique → testing.
2. [Production application interface](docs/workflows/application-interface.md). Requirements → specification → information architecture → prototype → components → accessibility → testing.
3. [Interactive 3D website](docs/workflows/interactive-3d.md). Concept → validated asset → optimization → GLB → Three.js → interaction and performance testing.
4. [Design-system extraction and adaptation](docs/workflows/design-system-extraction.md). Authorized reference analysis → principles → an original `DESIGN.md` → components → audit.

## Story, motion and learning

5. [Illustrated and animated storytelling](docs/workflows/illustration-and-animation.md). Direction → illustration → scalable assets → animation → composition → accessible delivery.
6. [Cinematic promotional video](docs/workflows/cinematic-video.md). Concept → storyboard → shot plan → assets → composition → editing → encoding.
7. [Interactive 3D learning](docs/workflows/interactive-learning.md). Beats → a seekable scene → an explorable and a film from the same module, with a prediction before the reveal.
8. [Surreal cinematic 3D art](docs/workflows/surreal-cinematic-3d.md). An original glass head of liquid and toys, used to show which tools a shot needs and which it does not.

## 3D production and capture

9. [AI-assisted 3D asset factory](docs/workflows/3d-asset-factory.md). Reference images → one image-to-3D model → cleanup → optional retopology → UVs → materials → validation → export.
10. [Animation-ready character production](docs/workflows/animation-ready-character.md). Reference → deformation topology → UVs and materials → UniRig → Blender correction → test poses → animation → validated export.
11. [Real-world spatial reconstruction](docs/workflows/spatial-reconstruction.md). Authorized photographs → camera calibration → Gaussian Splatting → validation → splat viewer → optional verified conversion.
12. [Repeatable ComfyUI asset processing](docs/workflows/comfyui-asset-processing.md). An approved workflow JSON → verified nodes → generation → geometry → baking → export → batch QA.

## Whole projects

13. [Coordinated creative ecosystem](docs/workflows/full-creative-pipeline.md). One identity governs the site, app, illustrations, 3D assets, animation and promotional media.
14. [Persistent project intelligence](docs/workflows/persistent-intelligence.md). Authorized documents → relevant context → specification → execution → validation → approved decision log.

## Contracts

- [Time contract](docs/contracts/time-contract.md). Scene state as a function of story time, so one scene plays live, renders frame-exact and reopens any paused frame. Proved by the [seekable scene fixture](fixtures/seekable-scene/README.md).
- [Asset contract example](docs/examples/asset-contract.md) and the machine-readable [asset manifest](templates/asset-manifest.json). Producer, consumer, format, versioned stages and validation.
- [Export contracts](docs/3d-pipeline/export-contracts.md). Which format carries what, and what each one loses.

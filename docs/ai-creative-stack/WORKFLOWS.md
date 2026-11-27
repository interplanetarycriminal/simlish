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
9. [Expressive motion production](docs/workflows/expressive-motion-production.md). A hand-drawn interactive character, motion rebuilt from an authorized reference, or a cinematic motion pass with a scoped critique; one owner per property throughout.
10. [Interactive React 3D](docs/workflows/interactive-react-3d.md). Validated GLB → React Three Fiber → optional Theatre.js keyframes for a human-editable camera → performance checks → fixed-frame capture when a film is needed.

## 3D production and capture

11. [AI-assisted 3D asset factory](docs/workflows/3d-asset-factory.md). Reference images → one image-to-3D model → cleanup → optional retopology → UVs → materials → validation → export.
12. [Animation-ready character production](docs/workflows/animation-ready-character.md). Reference → deformation topology → UVs and materials → UniRig → Blender correction → test poses → animation → validated export.
13. [Real-world spatial reconstruction](docs/workflows/spatial-reconstruction.md). Authorized photographs → camera calibration → Gaussian Splatting → validation → splat viewer → optional verified conversion.
14. [Repeatable ComfyUI asset processing](docs/workflows/comfyui-asset-processing.md). An approved workflow JSON → verified nodes → generation → geometry → baking → export → batch QA.

## Games

15. [2D web game](docs/workflows/web-2d-game.md). Phaser with its bundled physics → sprites, effects and levels → jsfxr with engine audio or Howler.js → optional Ink → browser tests.
16. [Standalone game](docs/workflows/standalone-game.md). A 2D indie game in Godot, a low-poly 3D adventure in Godot or Babylon.js, or a Rust simulation in Bevy with Rapier; then a launch trailer from real gameplay.
17. [Multiplayer arena](docs/workflows/multiplayer-arena.md). A chosen client engine → Colyseus or Nakama with server authority → two-client, invalid-input and reconnect tests.

## Whole projects

18. [Coordinated creative ecosystem](docs/workflows/full-creative-pipeline.md). One identity governs the site, app, illustrations, 3D assets, animation and promotional media.
19. [Persistent project intelligence](docs/workflows/persistent-intelligence.md). Authorized documents → relevant context → specification → execution → validation → approved decision log.

## Contracts

- [Time contract](docs/contracts/time-contract.md). Scene state as a function of story time, so one scene plays live, renders frame-exact and reopens any paused frame. Proved by the [seekable scene fixture](fixtures/seekable-scene/README.md).
- [Asset contract example](docs/examples/asset-contract.md) and the machine-readable [asset manifest](templates/asset-manifest.json). Producer, consumer, format, versioned stages and validation.
- [Export contracts](docs/3d-pipeline/export-contracts.md). Which format carries what, and what each one loses.
- [Game artifact contracts](docs/game-development/artifact-contracts.md). Game design, assets, levels, audio, narrative, multiplayer and delivery.
- [Motion ownership contract](docs/expressive-motion/ownership.md). One owner per property and per clock, proved by the [expressive-motion fixture](fixtures/expressive-motion/README.md).
- [Strategy contracts](docs/strategy/README.md). Work packages, the execution ledger and the decision log, as JSON Schemas in `registry/contracts/`.

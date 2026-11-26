# Taxonomy

The [capability matrix](docs/diagrams/capability-matrix.svg) says what each reference does. This page sorts all 53 references by how they behave in a workflow, which predicts how they combine and where the gaps are.

## Four questions

1. **Does it make options or narrow them?** Generators, catalogues and renderers add possibilities. Direction skills, critics, design systems and sources of truth remove them. A workflow needs both, and two tools on the same side of one decision conflict.
2. **Does it work on a flat surface or in space and time?** Pages and components, or scenes, sequences and footage.
3. **Does it check its own output?** Does the tool render what it made and inspect the result, or does it stop at the source?
4. **What clock does it run on?** For anything that moves: wall, stepped or seekable. See the [time contract](docs/contracts/time-contract.md).

| Reference | Makes or narrows | Surface | Checks its own output | Clock |
| --- | --- | --- | --- | --- |
| [Taste Skill](docs/repositories/taste-skill.md) | Narrows | Flat | Headless Chrome at four widths | — |
| [Impeccable](docs/repositories/impeccable.md) | Narrows | Flat | 62-rule detector, edit-time hook | — |
| [Hallmark](docs/repositories/hallmark.md) | Narrows | Flat | Lint at eight widths, fresh-context reviewer | — |
| [Anthropic Frontend Design](docs/repositories/anthropic-frontend.md) | Narrows | Flat | Critique from screenshots | — |
| [Astryx](docs/repositories/astryx.md) | Narrows (a system) | Flat | — | — |
| [Penpot](docs/repositories/penpot.md) | Narrows (source of truth) | Flat | — | — |
| [Figma Context MCP](docs/repositories/figma-context.md) | Narrows (source of truth) | Flat | — | — |
| [UI/UX Pro Max](docs/repositories/ui-ux-pro-max.md) | Makes | Flat | — | — |
| [Stitch Skills](docs/repositories/stitch-skills.md) | Makes | Flat | — | — |
| [Magic MCP](docs/repositories/magic-mcp.md) | Makes | Flat | — | — |
| [Magic UI](docs/repositories/magic-ui.md) | Makes | Flat | — | Wall |
| [Open Design](docs/repositories/open-design.md) | Makes | Flat and time | — | Seekable, through HyperFrames |
| [Rough.js](docs/repositories/rough-js.md) | Makes | Flat | — | — |
| [Meng To Skills](docs/repositories/mengto-skills.md) | Makes, some narrow | Flat and space | Illustration linters, a 3D lighting scorecard | Varies by skill |
| [Line Art Animation](docs/repositories/line-art-animation.md) | Makes | Space and time | Frame-by-frame motion checks | Stepped |
| [Sakuga VFX](docs/repositories/sakuga-vfx.md) | Makes | Time | `look.mjs` frame sheets, touch and key tests | Wall, steppable for review |
| [Three.js](docs/repositories/three-js.md) | Makes | Space | — | Whatever the scene author writes |
| [Blender MCP](docs/repositories/blender-mcp.md) | Makes | Space | `look`: angles, wireframe, X-ray, animation strips | Blender timeline |
| [Motion Canvas](docs/repositories/motion-canvas.md) | Makes | Time | Editor preview | Seekable |
| [HyperFrames](docs/repositories/hyperframes.md) | Makes | Time | Deterministic render | Seekable |
| [Remotion](docs/repositories/remotion.md) | Makes | Time | Player preview | Seekable |
| [Scarlet](docs/repositories/scarlet.md) | Makes | Time | Before and after playback, review queue | Footage timeline |
| [Video Use](docs/repositories/video-use.md) | Makes | Time | Inspects every cut boundary of its render | Footage timeline |
| [Real-ESRGAN](docs/repositories/real-esrgan.md) | Makes | Flat and time | — | — |
| [FFmpeg](docs/repositories/ffmpeg.md) | Neither: transforms | Time | ffprobe | Explicit frame rate |
| [SAM 3D Objects](docs/repositories/sam-3d-objects.md) | Makes | Space | — | — |
| [Stable Fast 3D](docs/repositories/stable-fast-3d.md) | Makes | Space | — | — |
| [TRELLIS.2](docs/repositories/trellis-2.md) | Makes | Space | Renders an MP4 preview | — |
| [MeshAnything V2](docs/repositories/meshanything-v2.md) | Narrows (geometry to a 1,600-face budget) | Space | — | — |
| [UniRig](docs/repositories/unirig.md) | Makes | Space and time | — | — |
| [Dream Textures](docs/repositories/dream-textures.md) | Makes | Flat and space | — | — |
| [ComfyUI-3D-Pack](docs/repositories/comfyui-3d-pack.md) | Neither: orchestrates | Space | Node previews | Per node |
| [Gaussian Splatting](docs/repositories/gaussian-splatting.md) | Makes | Space | Held-out view metrics | — |
| [Blender Skills](docs/repositories/blender-skills.md) | Narrows (procedures) | Space and time | Headless renders | Blender timeline |
| [Dream Loop](docs/repositories/dream-loop.md) | Narrows (judge loop) | Space | A judge subagent scores screenshots against a target | — |
| [Video Shotcraft](docs/repositories/video-shotcraft.md) | Makes | Time | — | Seekable, through Remotion |
| [Anatomy](docs/repositories/anatomy.md) | Makes | Flat and space | Geometry and line audits in Chrome | — |
| [React Bits](docs/repositories/react-bits.md) | Makes | Flat | — | Wall |
| [Designlang](docs/repositories/designlang.md) | Narrows (extracts a system) | Flat | CSS health and WCAG audits | — |
| [Awesome DESIGN.md](docs/repositories/awesome-design-md.md) | Narrows (examples of systems) | Flat | — | — |
| [Graphify](docs/repositories/graphify.md) | Neither: remembers | — | — | — |
| [Claude Mem](docs/repositories/claude-mem.md) | Neither: remembers | — | — | — |
| [Spec Kit](docs/repositories/spec-kit.md) | Narrows (specification) | — | An analyze step checks artifact consistency | — |
| [Awesome Claude Skills](docs/repositories/awesome-claude-skills.md) | Makes (discovery) | — | — | — |
| [Huashu Motion](docs/repositories/huashu-motion.md) | Makes | Time | Point-and-comment studio review | Own renderer, local Chrome |
| [anything2explainer](docs/repositories/anything2explainer.md) | Makes | Time | — | Seekable, through Remotion |
| [OneTake](docs/repositories/onetake.md) | Makes | Space and time | — | Seekable: `window.__seek(t)` |
| [Lemo Opuscar](docs/repositories/lemo-opuscar.md) | Makes | Space and time | — | Seekable: `render(t)` pages |
| [OpenScreen](docs/repositories/openscreen.md) | Makes | Time | — | Footage timeline |
| [EffectCraft](docs/repositories/effectcraft.md) | Makes | Time | — | Compositor timeline |
| [GSAP](docs/repositories/gsap.md) | Makes | Flat and time | — | Seekable timelines |
| [ComfyUI](docs/repositories/comfyui.md) | Neither: orchestrates | Flat and space | Node previews | Per node |
| [Remotion skills](docs/repositories/remotion-skills.md) | Narrows (procedures) | Time | — | Seekable, through Remotion |

## What the sort shows

**The design tools judge; the motion tools look.** Almost every flat-surface tool that narrows options carries named rules and tiers. Almost every time-based tool checks its own render: Video Use inspects every cut, Sakuga saves frame sheets, Line Art checks motion frame by frame, Blender MCP renders multi-angle sheets. Neither group borrows the other's habit. The [quality gates](QUALITY_GATES.md) now put tiered rules on space and time, and rendered checks on everything.

**Judgment in space and time exists, but it judges the picture.** It is tempting to say 3D has no critic, but that is too strong. Meng To's lighting scorecard rates a render out of 10, and Blender MCP's `look` tool lets the agent see its own scene. Both answer "is this good to look at?". No reference here asks whether the viewer understood: none holds an audience model, a learning goal, a misconception or a test with a real person. The [interactive learning workflow](docs/workflows/interactive-learning.md) and the Learning gate add that layer.

**The most valuable handoff is a function, not a file.** File handoffs (GLB, SVG, numbered frames, masters) are well covered by the [asset contract](docs/examples/asset-contract.md). The handoff that lets one scene be both an explorable and a film is `setTime(t)`. All three compositors in the catalogue are already seekable, so the work sits in the scene author's habits, not in new tools.

**Several "unverified" routes were documented upstream.** Video Use generates overlays with HyperFrames and Remotion. HyperFrames ships a Remotion port skill. Scarlet renders HTML motion graphics to transparent ProRes 4444. Remotion publishes `@remotion/three`. The registry and guides now record these as documented, and still untested here, except the DevTools frame route that the [seekable scene fixture](fixtures/seekable-scene/README.md) proves.

**The 3D additions make cheaply and check little.** The seven source-C tools and TRELLIS.2 all generate, and none judges its own geometry, UVs or deformation. That is why the catalogue adds `scripts/blender/validate_asset.py` and the geometry, UV, rigging and splat gates: the checking layer for AI-generated 3D did not exist in the collection.

**Memory is a fourth kind of tool.** Graphify, Claude Mem and a decision log neither make nor narrow options; they decide what the next session knows. That makes them powerful and risky: they need the same authorization and privacy review as any external service, and two of them installed together compete for the same hooks.

**The newest film tools converge on the time contract.** OneTake seeks `window.__seek(t)`, Opuscar renders `render(t)` pages, anything2explainer uses Remotion's frame clock and Huashu Motion drives GSAP in Chrome. Four independent projects arrived at the rule this catalogue's time contract states: a film is a page whose state is a function of time.

**Meng To Skills was filed under the wrong shelf.** It was listed for creative direction only, yet its pinned README lists 30 Three.js rendering skills and 14 illustration styles with headless renderers. That makes it the largest source of 3D craft in the catalogue.

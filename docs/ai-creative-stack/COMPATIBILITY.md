# Compatibility

A tool's type decides how it is integrated and what counts as evidence. A skill, an MCP server, a library, a model, a Blender add-on, a ComfyUI node pack and an application are not interchangeable.

| Integration surface | Examples | What counts as evidence | First controlled check |
| --- | --- | --- | --- |
| Agent skill | Taste Skill, Impeccable, Blender Skills, Anatomy, Dream Loop | Upstream documents the host and discovery location | Load one skill and confirm its scope and the files it touches. |
| MCP server | Blender MCP, Figma Context MCP, 21st MCP, Designlang | Host, transport, auth and permission scope are documented | Configure it in a scoped test project and perform one approved read. |
| Library or framework | Three.js, Rough.js, Remotion, HyperFrames | Runtime and peer dependencies match | Build a fixture with the project's package manager and render it. |
| Model and inference code | SAM 3D Objects, Stable Fast 3D, TRELLIS.2, MeshAnything V2, UniRig | GPU, VRAM, CUDA, PyTorch and weights access match | Run one authorized image in an isolated environment and validate the output. |
| Blender add-on | Dream Textures, Blender MCP's add-on | Blender version matches | Open a disposable copy and export one asset. |
| ComfyUI node pack | ComfyUI-3D-Pack | ComfyUI, Python, PyTorch and CUDA builds match; each model's node exists | Run one pinned workflow JSON in a dedicated install. |
| Desktop application | Penpot, Scarlet, Open Design | Supported app build and OS | Open a disposable project and export one asset. |
| CLI | FFmpeg, Spec Kit, Graphify | Version, executable and compute requirements match | Process one fixture and inspect output metadata and appearance. |
| Curated list | Awesome DESIGN.md, Awesome Claude Skills | Not applicable: each linked item needs its own review | Review one item end to end before using it. |

## Integrations by evidence

| Integration | Evidence | Where |
| --- | --- | --- |
| Blender → GLB → Three.js (skin, clip, scale, up axis, seek) | Tested | [fixtures/blender-glb](fixtures/blender-glb/README.md) |
| Three.js scene → DevTools frames → FFmpeg | Tested | [fixtures/seekable-scene](fixtures/seekable-scene/README.md) |
| Open Design → HyperFrames | Documented | [Open Design guide](docs/repositories/open-design.md) |
| Video Use → HyperFrames or Remotion overlays | Documented | [Video Use guide](docs/repositories/video-use.md) |
| Remotion → HyperFrames port | Documented | [HyperFrames guide](docs/repositories/hyperframes.md) |
| Scarlet → transparent ProRes 4444 motion graphics | Documented | [Scarlet guide](docs/repositories/scarlet.md) |
| ComfyUI-3D-Pack → Stable Fast 3D, TRELLIS v1, Hunyuan3D, TripoSG, 3DGS nodes | Documented | [ComfyUI-3D-Pack guide](docs/repositories/comfyui-3d-pack.md) |
| UniRig → Blender (bpy merge, FBX) | Documented | [UniRig guide](docs/repositories/unirig.md) |
| Blender Skills → Blender MCP | Documented | [Blender Skills guide](docs/repositories/blender-skills.md) |
| Video Shotcraft → Remotion project | Documented | [Video Shotcraft guide](docs/repositories/video-shotcraft.md) |
| SAM 3D Objects, SF3D or TRELLIS.2 GLB → Blender | Proposed | [Image to 3D](docs/3d-pipeline/image-to-3d.md) |
| MeshAnything V2 OBJ → Blender UVs | Proposed | [Retopology](docs/3d-pipeline/retopology.md) |
| Gaussian PLY → polygon mesh | Proposed, lossy | [Gaussian Splatting](docs/3d-pipeline/gaussian-splatting.md) |
| SAM 3D Objects, TRELLIS.2, UniRig or MeshAnything V2 inside ComfyUI | Not available natively at the pinned commit | [ComfyUI orchestration](docs/3d-pipeline/comfyui-orchestration.md) |

Protocol compatibility alone leaves host discovery, approval behavior and transport flags to be tested. Figma Context MCP host mappings outside its documented examples, automatic editable-timeline conversion and cross-renderer transparency stay unresolved until checked on a fixture.

## Interchange rules

- **Blender → GLB → Three.js** is standard interchange, and it is tested here. Blender's Z up becomes glTF's Y up on export. Units are meters. glTF splits vertices along UV seams, carries four joint influences per vertex set and keeps clip names. FBX can rename clips.
- **A scene written to the [time contract](docs/contracts/time-contract.md)** avoids timeline interchange: every renderer calls the same `setTime(t)`.
- **FFmpeg** consumes a compatible media file, or numbered images at an explicit frame rate.
- **A Gaussian PLY is not a polygon PLY.** Splat viewers read it; mesh tools do not.
- **SVG tooling** can differ in filter, font and animation support.

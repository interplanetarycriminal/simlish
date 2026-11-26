# Three.js

Use for browser 3D with explicit runtime budgets.

> Core 3D authoring and rendering · Sources A and B · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/mrdoob/three.js)
- Verified 2026-11-26 against default branch `dev` at [`47b80abe3eab`](https://github.com/mrdoob/three.js/commit/47b80abe3eab50614e2b85e4fa61ae903786638f).
- GitHub reports archive state **false** and a repository push at `2026-11-26T03:46:56Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/mrdoob/three.js/blob/47b80abe3eab50614e2b85e4fa61ae903786638f/README.md)
- [LICENSE](https://github.com/mrdoob/three.js/blob/47b80abe3eab50614e2b85e4fa61ae903786638f/LICENSE)
- [package.json](https://github.com/mrdoob/three.js/blob/47b80abe3eab50614e2b85e4fa61ae903786638f/package.json)

## Runtime, hardware and setup

- **Type** 3D rendering library. Primary language JavaScript.
- **Platforms** Browser.
- **Runtime** JavaScript ES modules and compatible browser/GPU
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Set loader base paths, lighting, compression decoders and GPU budget before import.
- **Credentials and services** No separate key.

| Hardware | Documented value |
| --- | --- |
| GPU | unverified |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Not documented |
| CPU fallback | not applicable |
| Training versus inference | Not documented |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
Use the three package named in the README. Resolve a version compatible with the project and verify the loader version matches it.
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | GLTF or GLB assets, textures and scene code |
| Output | Interactive canvas and rendered frames |
| Primary | 3D rendering |
| Supporting | Animation, Frontend implementation |

Skip if a static poster or simple CSS effect meets the brief. Consider the existing project toolchain. Complementary tools include [blender-mcp](blender-mcp.md), [hyperframes](hyperframes.md), [remotion](remotion.md), [mengto-skills](mengto-skills.md), [sam-3d-objects](sam-3d-objects.md), [stable-fast-3d](stable-fast-3d.md), [unirig](unirig.md), [gaussian-splatting](gaussian-splatting.md), [anatomy](anatomy.md), [dream-loop](dream-loop.md), [trellis-2](trellis-2.md), [react-bits](react-bits.md), [huashu-motion](huashu-motion.md), [onetake](onetake.md), [lemo-opuscar](lemo-opuscar.md), [gsap](gsap.md).

Remotion's @remotion/three and HyperFrames' seekable compositions can drive a Three.js scene. The seekable scene fixture verifies the DevTools frame route.

## Craft notes

- Release r187 (three@0.187.0 on npm): WebGL and WebGPU renderers, WebXR, loaders, and SVG and CSS3D add-ons.
- Render loops usually read wall time. Write scenes to the time contract so one scene is both the explorable and the film. Remotion's @remotion/three and HyperFrames' seekable compositions can drive it.

## Examples

1. **Independent** Load a small GLB with GLTFLoader and validate materials under target lighting.
2. **Combined** Load a Blender-authored GLB and test animation clips, scale and compression support.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. fixtures/seekable-scene (seekable, repeatable, pause-to-play, stream) and fixtures/blender-glb (GLB load, skin, clip, seek) with three r187 in headless Chrome 158.

## Security, privacy and licensing

- Serve reviewed assets and loaders. Enforce size budgets on geometry, textures and draw calls.
- No external service in the documented base workflow.

**Software license** MIT.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.

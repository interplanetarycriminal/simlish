# Line Art Animation

Use for animated line figures and scene treatments.

> Illustration and animation · Source B · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/JDhruv14/line-art-animation)
- Verified 2026-11-26 against default branch `main` at [`c43d698913cf`](https://github.com/JDhruv14/line-art-animation/commit/c43d698913cf0ad44f984c7ae14c5348010594d3).
- GitHub reports archive state **false** and a repository push at `2026-11-10T09:25:38Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/JDhruv14/line-art-animation/blob/c43d698913cf0ad44f984c7ae14c5348010594d3/README.md)
- [LICENSE](https://github.com/JDhruv14/line-art-animation/blob/c43d698913cf0ad44f984c7ae14c5348010594d3/LICENSE)
- [package.json](https://github.com/JDhruv14/line-art-animation/blob/c43d698913cf0ad44f984c7ae14c5348010594d3/package.json)

## Runtime, hardware and setup

- **Type** skill and TypeScript library. Primary language TypeScript.
- **Platforms** Browser.
- **Runtime** TypeScript library in a browser project. npm for repository demo.
- **Execution** local.
- **Agent paths** Claude Code. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Approve one SVG figure and move only the required library files into the project.
- **Credentials and services** No separate key established.

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
git clone https://github.com/JDhruv14/line-art-animation .claude/skills/line-art-animation
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Scene and character brief |
| Output | Animated SVG components |
| Primary | Illustration, Animation |
| Supporting | Frontend implementation |

Skip when simple static SVG is sufficient. Consider [rough-js](rough-js.md), [sakuga-vfx](sakuga-vfx.md). Complementary tools include [motion-canvas](motion-canvas.md), [ffmpeg](ffmpeg.md).

The pinned README documents deterministic DevTools frame capture followed by an FFmpeg encode.

## Craft notes

- Dependency-free TypeScript modules for ink strokes, a walk and run gait solver, springs and wind, and a time-of-day palette. The skill shows one figure for approval before building the rest.
- scripts/capture.ts drives headless Chrome over DevTools, advances exactly one frame per screenshot, then FFmpeg encodes. The clock is stepped (phase += dt), so seeking to a moment replays from the start.

## Examples

1. **Independent** Try a single walking figure and approve its silhouette before extending the scene.
2. **Combined** Capture a browser-rendered sequence for compositing with explicit alpha and frame timing.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Audit copied library files and provide static alternatives for motion sensitivity.
- No external service in the documented base workflow.

**Software license** MIT.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.

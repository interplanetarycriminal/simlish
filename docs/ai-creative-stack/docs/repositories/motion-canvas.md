# Motion Canvas

Use when procedural motion and timeline signals are central.

> #19 · Illustration and animation · Source B · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/motion-canvas/motion-canvas)
- Verified 2026-11-26 against default branch `main` at [`7b91435c301d`](https://github.com/motion-canvas/motion-canvas/commit/7b91435c301d530351dcf5ebb91dd139c002e405).
- GitHub reports archive state **false** and a repository push at `2026-07-02T20:01:32Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/motion-canvas/motion-canvas/blob/7b91435c301d530351dcf5ebb91dd139c002e405/README.md)
- [LICENSE](https://github.com/motion-canvas/motion-canvas/blob/7b91435c301d530351dcf5ebb91dd139c002e405/LICENSE)
- [package.json](https://github.com/motion-canvas/motion-canvas/blob/7b91435c301d530351dcf5ebb91dd139c002e405/package.json)

## Runtime, hardware and setup

- **Type** programmatic motion framework. Primary language TypeScript.
- **Platforms** Browser.
- **Runtime** TypeScript, Vite and browser preview
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Set project dimensions, frame rate and the needed exporter.
- **Credentials and services** No separate key established for local workflow.

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
npm install
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | TypeScript generator scenes, images and audio |
| Output | Rendered image sequences or video with exporter |
| Primary | Animation, Video composition |
| Supporting | Illustration |

Skip for native React composition or a simple clip trim. Consider [remotion](remotion.md), [hyperframes](hyperframes.md), [video-shotcraft](video-shotcraft.md), [huashu-motion](huashu-motion.md), [anything2explainer](anything2explainer.md), [onetake](onetake.md), [effectcraft](effectcraft.md), [gsap](gsap.md), [motionmaxxing](motionmaxxing.md). Complementary tools include [ffmpeg](ffmpeg.md), [rough-js](rough-js.md), [line-art-animation](line-art-animation.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- Programs animations with TypeScript generators and previews them in an editor. Built for informative vector animation synchronized with voice-over.
- Its timeline is seekable by design. It has no bundled Three.js bridge.

## Examples

1. **Independent** Animate an explanatory callout entering on a timed cue.
2. **Combined** Pass the exported indexed frame sequence to FFmpeg at the project's declared frame rate.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- The command shown is for the cloned repository. Review npm scripts and exporter packages before use.
- No external service in the documented base workflow.

**Software license** MIT.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.

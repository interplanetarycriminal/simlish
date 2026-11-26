# HyperFrames

Use for HTML-authored motion and video composition.

> Video composition and post-production · Sources A and B · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/heygen-com/hyperframes)
- Verified 2026-11-26 against default branch `main` at [`5b14acd53b5a`](https://github.com/heygen-com/hyperframes/commit/5b14acd53b5a43390f13e6882c31fa2edc969299).
- GitHub reports archive state **false** and a repository push at `2026-11-26T06:59:12Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/heygen-com/hyperframes/blob/5b14acd53b5a43390f13e6882c31fa2edc969299/README.md)
- [LICENSE](https://github.com/heygen-com/hyperframes/blob/5b14acd53b5a43390f13e6882c31fa2edc969299/LICENSE)
- [package.json](https://github.com/heygen-com/hyperframes/blob/5b14acd53b5a43390f13e6882c31fa2edc969299/package.json)

## Runtime, hardware and setup

- **Type** HTML video framework, CLI and editor. Primary language TypeScript.
- **Platforms** Unverified.
- **Runtime** Node 22+ and FFmpeg for local renderer
- **Execution** local or hosted.
- **Agent paths** Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Set composition duration, dimensions, timing and media paths, then preview before rendering.
- **Credentials and services** No separate key established for base local rendering. Cloud and AI features may require credentials.

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
npx hyperframes init my-video
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | HTML compositions, media and timing |
| Output | Preview and MP4 render |
| Primary | Video composition |
| Supporting | Animation, Video editing |

Skip if project already has a satisfactory React or Motion Canvas timeline. Consider [remotion](remotion.md), [motion-canvas](motion-canvas.md), [scarlet](scarlet.md), [video-shotcraft](video-shotcraft.md), [huashu-motion](huashu-motion.md), [anything2explainer](anything2explainer.md), [onetake](onetake.md), [lemo-opuscar](lemo-opuscar.md), [effectcraft](effectcraft.md). Complementary tools include [open-design](open-design.md), [ffmpeg](ffmpeg.md), [three-js](three-js.md), [video-use](video-use.md), [gsap](gsap.md).

Open Design documents a native HyperFrames workspace. FFmpeg is a documented local runtime dependency. The pinned README documents a /remotion-to-hyperframes port skill.

## Craft notes

- Turns HTML, CSS, JavaScript, media and seekable animations into deterministic MP4 through headless Chrome and FFmpeg.
- Ships a /remotion-to-hyperframes port skill and an MCP connector. The showcase includes 3D one-take trailers and 3D type. The Studio app's Pro tier adds hosted models. The open-source renderer runs locally.

## Examples

1. **Independent** Create a 10-second typographic title in Studio or a local composition and render it.
2. **Combined** Render MP4 from its native Open Design feature or pass its master to FFmpeg for delivery.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Keep third-party HTML and media isolated. Review cloud rendering and model settings separately.
- Local rendering keeps media local. Studio Pro and cloud rendering send it to HeyGen services.

**Software license** Apache-2.0.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.

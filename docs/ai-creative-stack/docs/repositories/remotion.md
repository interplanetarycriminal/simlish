# Remotion

Use when React components and deterministic parameterization matter.

> Video composition and post-production · Source B · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/remotion-dev/remotion)
- Verified 2026-11-26 against default branch `main` at [`c1de64d7e260`](https://github.com/remotion-dev/remotion/commit/c1de64d7e260e83cdaf5ff379583d7067c128d20).
- GitHub reports archive state **false** and a repository push at `2026-11-25T16:53:08Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/remotion-dev/remotion/blob/c1de64d7e260e83cdaf5ff379583d7067c128d20/README.md)
- [LICENSE.md](https://github.com/remotion-dev/remotion/blob/c1de64d7e260e83cdaf5ff379583d7067c128d20/LICENSE.md)
- [package.json](https://github.com/remotion-dev/remotion/blob/c1de64d7e260e83cdaf5ff379583d7067c128d20/package.json)

## Runtime, hardware and setup

- **Type** React video framework. Primary language TypeScript.
- **Platforms** Unverified.
- **Runtime** Node.js and browser renderer
- **Execution** local or hosted.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Set composition ID, props, frames, dimensions and frame rate in the project.
- **Credentials and services** No separate key established for local rendering. Cloud execution requires provider access.

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
npx create-video@latest
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | React components and media props |
| Output | Rendered video, image or frames depending on renderer |
| Primary | Video composition |
| Supporting | Animation |

Skip when company license conditions are unresolved or HTML is the better authoring fit. Consider [hyperframes](hyperframes.md), [motion-canvas](motion-canvas.md), [video-shotcraft](video-shotcraft.md). Complementary tools include [ffmpeg](ffmpeg.md), [three-js](three-js.md), [video-use](video-use.md), [anatomy](anatomy.md).

@remotion/three is published on npm (4.0.547 on 2026-11-26) for Three.js scenes in a composition. HyperFrames documents a Remotion port skill.

## Craft notes

- Video as React components, with useCurrentFrame() as the clock. @remotion/three renders Three.js scenes inside a composition.
- More than 1,200 documentation pages, agent skills, Lambda and client-side rendering. Some companies need a paid license.

## Examples

1. **Independent** Parameterize a 10-second title with a locale and preview the first and final frames.
2. **Combined** Give FFmpeg the rendered master for a delivery-specific remux or encode.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Review renderer flags, external asset loading and Lambda permissions if used.
- Local rendering keeps media local. Lambda and cloud rendering send it to the chosen cloud account.

**Software license** Remotion License.

**Commercial use** Review current company-license thresholds and the entity and use definitions before production.

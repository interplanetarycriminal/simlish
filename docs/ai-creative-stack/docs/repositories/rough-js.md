# Rough.js

Use for controlled sketch textures and diagram marks.

> #18 · Frontend components and creative coding · Source B, also listed in Source F (expressive motion) · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/rough-stuff/rough)
- Verified 2026-11-26 against default branch `master` at [`56a2762171b1`](https://github.com/rough-stuff/rough/commit/56a2762171b1294d643501e8d14f120db6b27bd7).
- GitHub reports archive state **false** and a repository push at `2024-07-28T21:12:58Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/rough-stuff/rough/blob/56a2762171b1294d643501e8d14f120db6b27bd7/README.md)
- [LICENSE](https://github.com/rough-stuff/rough/blob/56a2762171b1294d643501e8d14f120db6b27bd7/LICENSE)
- [package.json](https://github.com/rough-stuff/rough/blob/56a2762171b1294d643501e8d14f120db6b27bd7/package.json)

## Runtime, hardware and setup

- **Type** JavaScript library. Primary language HTML.
- **Platforms** Browser.
- **Runtime** Browser Canvas or SVG with JS bundle
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Choose SVG or Canvas renderer. Set a seed where reproducible output matters.
- **Credentials and services** No separate key.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npm install --save roughjs
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Geometry, SVG paths and drawing options |
| Output | Canvas drawing or SVG elements |
| Primary | Illustration |
| Supporting | Frontend implementation |

Skip when precise corporate icon outlines are required. Consider [line-art-animation](line-art-animation.md). Complementary tools include [motion-canvas](motion-canvas.md), [sakuga-vfx](sakuga-vfx.md), [matter-js](matter-js.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- Draws lines, curves, polygons and paths with a hand-sketched look to Canvas or SVG, in under 9 kB.
- Strokes are randomized per draw. Fix the randomness before rendering frames, or the shapes shimmer from frame to frame.

## Examples

1. **Independent** Draw a sketch rectangle and keep its seed stable for visual tests.
2. **Combined** Export a standalone SVG with size and viewBox for a compositor import test.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. roughjs 4.6.6 via bundled/rough.cjs.js in Node 24: same seed gives identical paths, another seed differs. The bin/ ES modules use extensionless imports that Node ESM cannot resolve.

## Security, privacy and licensing

- Escape external SVG content and limit path complexity.
- No external service in the documented base workflow.

**Software license** MIT.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.

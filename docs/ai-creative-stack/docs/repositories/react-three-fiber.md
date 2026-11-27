# React Three Fiber (@react-three/fiber)

Use for building three.js scenes declaratively as React components, with hooks for the render loop, pointer events and on-demand or manually driven rendering.

> #75 · Expressive motion · Source F (expressive motion) · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/pmndrs/react-three-fiber)
- Verified 2026-11-27 against default branch `master` at [`d74622ea8ed7`](https://github.com/pmndrs/react-three-fiber/commit/d74622ea8ed717f7212d7e19d65ff3e325508389).
- GitHub reports archive state **false** and a repository push at `2026-10-21T15:24:39Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the expressive-animation post (source F, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/pmndrs/react-three-fiber/blob/d74622ea8ed717f7212d7e19d65ff3e325508389/README.md)
- [package.json](https://github.com/pmndrs/react-three-fiber/blob/d74622ea8ed717f7212d7e19d65ff3e325508389/packages/fiber/package.json)
- [canvas.mdx](https://github.com/pmndrs/react-three-fiber/blob/d74622ea8ed717f7212d7e19d65ff3e325508389/docs/API/canvas.mdx)
- [hooks.mdx](https://github.com/pmndrs/react-three-fiber/blob/d74622ea8ed717f7212d7e19d65ff3e325508389/docs/API/hooks.mdx)
- [additional-exports.mdx](https://github.com/pmndrs/react-three-fiber/blob/d74622ea8ed717f7212d7e19d65ff3e325508389/docs/API/additional-exports.mdx)
- [scaling-performance.mdx](https://github.com/pmndrs/react-three-fiber/blob/d74622ea8ed717f7212d7e19d65ff3e325508389/docs/advanced/scaling-performance.mdx)
- [loop.ts](https://github.com/pmndrs/react-three-fiber/blob/d74622ea8ed717f7212d7e19d65ff3e325508389/packages/fiber/src/core/loop.ts)

## Runtime, hardware and setup

- **Type** library. Primary language TypeScript.
- **Platforms** Unverified.
- **Runtime** @react-three/fiber 9.8.1: react and react-dom >=19 <19.4, three >=0.156. React Native >=0.78 with expo >=43, expo-gl >=11 are optional peers. v8 pairs with React 18, v9 with React 19.
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Canvas props set frameloop (always, demand, never), dpr, shadows and performance; useFrame subscribes components to the render loop with an optional priority.
- **Credentials and services** None.

| Hardware | Documented value |
| --- | --- |
| GPU | unverified |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Not documented |
| CPU fallback | not documented |
| Training versus inference | Not documented |
| Notes | Renders through three.js WebGL in the browser; no hardware figures are documented. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npm install three @types/three @react-three/fiber
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | React JSX describing three.js objects, three.js loaders' assets (glTF, textures) via useLoader |
| Output | WebGL canvas rendering of the three.js scene, frames driven manually with advance() in frameloop='never' |
| Primary | 3D rendering, Frontend implementation |
| Supporting | Animation, Prototyping |

Skip if your app is on React 18 and cannot upgrade; R3F 9 at this commit requires React >=19 <19.4, so use R3F 8 instead. Consider [babylonjs](babylonjs.md). Complementary tools include [three-js](three-js.md), [theatre](theatre.md), [motion](motion.md), [rapier](rapier.md), [colyseus](colyseus.md), [blockbench](blockbench.md), [howler](howler.md), [reanimate](reanimate.md).

## Craft notes

- frameloop='demand' renders only on prop changes, so code that mutates objects directly (camera controls) must call invalidate().
- frameloop='never' plus advance(timestamp) gives frame-accurate offline rendering; in that mode the pinned loop.ts sets clock.elapsedTime to the timestamp, so pass time in the clock's units (seconds) and useFrame receives the computed delta.
- useFrame(state, delta, xrFrame) runs just before each frame; passing a numeric priority turns off automatic rendering, so you must render yourself.

## Examples

1. **Independent** Render a spinning glTF product model with frameloop='demand' and invalidate on orbit-control changes.
2. **Combined** Proposed handoff: drive a react-three-fiber v8 scene from a Theatre.js sequence and step frames with advance() for video export.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. fixtures/expressive-motion r3f-frameloop: @react-three/fiber 9.8.2 with three 0.187 and React 19.3.1, frameloop 'never'; each advance() renders one frame and a seeked toy_limb.glb renders SHA-256-identical pixels across repeats and fresh browsers.

## Security, privacy and licensing

- Assets load from URLs you pass to loaders; serve them yourself to control the origin.
- No network calls beyond the assets you load.

**Software license** MIT.

**Commercial use** MIT license: commercial use is allowed with the copyright notice kept.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | Not stated in README.md or docs read. |
| installation | 'npm install three @types/three @react-three/fiber' (README.md) |
| runtime_requirements | '"react": ">=19 <19.4"' and '"three": ">=0.156"' (packages/fiber/package.json) |
| version_pairing | '@react-three/fiber@8 pairs with react@18, @react-three/fiber@9 pairs with react@19.' (README.md) |
| license | '"license": "MIT"' (packages/fiber/package.json) |
| model_license | Not a model tool. |
| inputs | 'It merely expresses Threejs in JSX' (README.md) |
| outputs | '/ `advance` / Advances the frameloop (given that it's set to 'never') /' (docs/API/additional-exports.mdx) |
| frameloop | '/ frameloop / Render mode: always, demand, never /' (docs/API/canvas.mdx) |
| never_mode_clock | 'In frameloop='never' mode, clock times are updated using the provided timestamp' (packages/fiber/src/core/loop.ts) |

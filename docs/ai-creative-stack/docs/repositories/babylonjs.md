# Babylon.js

Use for real-time 3D games, product viewers and scenes in the browser with WebGL or WebGPU.

> #46 · Game development · Source E (games) · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/BabylonJS/Babylon.js)
- Verified 2026-11-27 against default branch `master` at [`71c118d5493e`](https://github.com/BabylonJS/Babylon.js/commit/71c118d5493e204b55e0ac700a0320f57bb940a5).
- GitHub reports archive state **false** and a repository push at `2026-11-26T23:39:30Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/BabylonJS/Babylon.js/blob/71c118d5493e204b55e0ac700a0320f57bb940a5/README.md)
- [package.json](https://github.com/BabylonJS/Babylon.js/blob/71c118d5493e204b55e0ac700a0320f57bb940a5/packages/public/@babylonjs/core/package.json)
- [readme.md](https://github.com/BabylonJS/Babylon.js/blob/71c118d5493e204b55e0ac700a0320f57bb940a5/packages/public/@babylonjs/loaders/readme.md)
- [readme.md](https://github.com/BabylonJS/Babylon.js/blob/71c118d5493e204b55e0ac700a0320f57bb940a5/packages/public/@babylonjs/mcp-servers/readme.md)
- [package.json](https://github.com/BabylonJS/Babylon.js/blob/71c118d5493e204b55e0ac700a0320f57bb940a5/packages/public/@babylonjs/mcp-servers/package.json)
- [havokPlugin.ts](https://github.com/BabylonJS/Babylon.js/blob/71c118d5493e204b55e0ac700a0320f57bb940a5/packages/dev/core/src/Physics/v2/Plugins/havokPlugin.ts)

## Runtime, hardware and setup

- **Type** framework. Primary language TypeScript.
- **Platforms** Web.
- **Runtime** Browser runtime; packages on npm (@babylonjs/core 9.38.0). Contributing/building the repo needs Node.js 22.22.2+ (22 line) or 24.16.0+ (24 line) and npm 11.18.0+.
- **Execution** local.
- **Agent paths** Any MCP client (via @babylonjs/mcp-servers), Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Import '@babylonjs/loaders/glTF' to register glTF/GLB loading. Physics V2 uses HavokPlugin, which needs the Havok WASM module awaited (HK()) and passed in.
- **Credentials and services** None.

| Hardware | Documented value |
| --- | --- |
| GPU | unverified |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Not documented |
| CPU fallback | not applicable |
| Training versus inference | Not documented |
| Notes | README gives no GPU requirements; engines for WebGL, WebGPU and Babylon Native exist in core. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npm install babylonjs --save
npm install @babylonjs/core @babylonjs/loaders
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | glTF/GLB, OBJ, STL, SPLAT, BVH, FBX and USD files via @babylonjs/loaders, .babylon scenes, JavaScript/TypeScript code |
| Output | Rendered browser scenes, Exports via @babylonjs/serializers (not read), Node graph JSON from the MCP servers |
| Primary | 3D rendering, Game engine |
| Supporting | Physics, Visual effects, Animation |

Skip when you need a native desktop/console engine with an editor-centered workflow; Godot fits better. Consider [three-js](three-js.md), [react-three-fiber](react-three-fiber.md), [godot](godot.md), [phaser](phaser.md), [bevy](bevy.md). Complementary tools include [blender-mcp](blender-mcp.md), [rapier](rapier.md), [jolt-physics](jolt-physics.md), [howler](howler.md), [colyseus](colyseus.md), [trellis-2](trellis-2.md), [blockbench](blockbench.md).

- README warns the Babylon CDN should not be used in production.

## Craft notes

- glTF loading is in the separate @babylonjs/loaders package (import '@babylonjs/loaders/glTF'); the loaders tree also holds OBJ, STL, SPLAT, BVH, FBX and USD loaders.
- Physics V2 ships only HavokPlugin; the legacy V1 API keeps Ammo.js, Cannon.js and Oimo.js plugins.
- The repo publishes @babylonjs/mcp-servers with seven graph-authoring MCP servers (nme, nge, nrge, npe, gui, flow-graph, smart-filters) that can live-sync with the web editors.

## Examples

1. **Independent** Load a GLB product model with @babylonjs/loaders and add Havok rigid bodies so parts fall and collide.
2. **Combined** Proposed handoff: generate a mesh with trellis-2, export GLB, then view and light it in a Babylon.js scene.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. fixtures/game-dev babylon-glb: Babylon.js 9.38.0 loads the catalogue's toy_limb.glb with 1 skinned mesh, 3 bones, the bend animation group and 0.3 m height; the tip bone moves 5.9 cm at a quarter of the clip, matching Three.js.

## Security, privacy and licensing

- Graph MCP session servers bind to 127.0.0.1 by default and stop after 15 minutes idle.
- Loading from cdn.babylonjs.com sends requests to Babylon's CDN; self-host for production.

**Software license** Apache-2.0.

**Commercial use** Apache-2.0 allows commercial use with notice and patent terms. The Havok physics WASM is a separate package whose license is not in the pinned files: Not established.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| gltf | loaders/readme.md: 'import "@babylonjs/loaders/glTF";' ... 'allow the load of gltf and glb files.' |
| physics | havokPlugin.ts: 'Havok is not ready. Please make sure you await HK() before using the plugin.'; V1 Plugins: ammoJSPlugin.ts, cannonJSPlugin.ts, oimoJSPlugin.ts |
| mcp | mcp-servers/readme.md: 'npx -y @babylonjs/mcp-servers nme' |
| hardware | README.md: no hardware requirements; Node versions are 'development-tool requirements' |
| installation | README.md: 'npm install babylonjs --save'; loaders/readme.md: 'npm install @babylonjs/core @babylonjs/loaders' |
| license | core/package.json: '"license": "Apache-2.0"' |
| model_license | Not applicable; no model weights. |
| inputs | README.md: 'test your .babylon and glTF scenes with a simple drag'n'drop' |
| outputs | README.md usage: 'engine.runRenderLoop(function(){ scene.render(); });' |

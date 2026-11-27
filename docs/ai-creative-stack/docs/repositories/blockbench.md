# Blockbench

Use for building low-poly 3D models with pixel art textures and animations, then exporting them as glTF/GLB, FBX, OBJ, Collada or STL, or as Minecraft Java and Bedrock formats.

> #51 · Game development · Source E (games) · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/JannisX11/blockbench)
- Verified 2026-11-27 against default branch `master` at [`ec0b2827104d`](https://github.com/JannisX11/blockbench/commit/ec0b2827104d0799c153bfb5f867579c0c44652f).
- GitHub reports archive state **false** and a repository push at `2026-11-25T16:03:40Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/JannisX11/blockbench/blob/ec0b2827104d0799c153bfb5f867579c0c44652f/README.md)
- [LICENSE.MD](https://github.com/JannisX11/blockbench/blob/ec0b2827104d0799c153bfb5f867579c0c44652f/LICENSE.MD)
- [package.json](https://github.com/JannisX11/blockbench/blob/ec0b2827104d0799c153bfb5f867579c0c44652f/package.json)
- [gltf.js](https://github.com/JannisX11/blockbench/blob/ec0b2827104d0799c153bfb5f867579c0c44652f/js/formats/standards/gltf.js)
- [obj.js](https://github.com/JannisX11/blockbench/blob/ec0b2827104d0799c153bfb5f867579c0c44652f/js/formats/standards/obj.js)
- [fbx.ts](https://github.com/JannisX11/blockbench/blob/ec0b2827104d0799c153bfb5f867579c0c44652f/js/formats/standards/fbx.ts)

## Runtime, hardware and setup

- **Type** application. Primary language JavaScript.
- **Platforms** Windows, Linux, macOS.
- **Runtime** Desktop app (Electron ^43.4.0) or the web app. Building from source needs Node.js >=20.0.0 and npm. three.js ^0.129.0 is bundled.
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Pick a model format (generic free model, bbmodel, Bedrock, Java block/item, modded entity, OptiFine, skin) when creating a project; each export codec has options such as scale, embedded textures, armature and animations.
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
| Notes | No hardware requirements are stated. The viewport is three.js (WebGL). |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npm install
npm run dev   (Electron, from source)
npm run serve   (web app at http://localhost:3000)
End users download the app from blockbench.net.
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | .bbmodel projects, Minecraft Java and Bedrock model JSON, OptiFine JEM/JPM, OBJ and other standard models via import, PNG textures, images (extruded into models) |
| Output | glTF (ASCII) or GLB (binary) with optional embedded textures, armature and animations, FBX, OBJ + MTL, Collada (.dae), STL, Minecraft Java block/item JSON, Bedrock entity/block geometry and animations, OptiFine JEM/JPM, .bbmodel |
| Primary | 3D authoring, Texturing |
| Supporting | Animation, Pixel art, Rigging |

Skip when you need high-poly sculpting, retopology or photoreal materials; Blockbench targets low-poly models with pixel art textures. Consider [blender-mcp](blender-mcp.md), [blender-skills](blender-skills.md). Complementary tools include [three-js](three-js.md), [react-three-fiber](react-three-fiber.md), [godot](godot.md), [babylonjs](babylonjs.md), [pixelorama](pixelorama.md), [godot-mcp](godot-mcp.md), [bevy](bevy.md).

## Craft notes

- The glTF codec exports ASCII .gltf or binary .glb, with scale, embedded textures, armature and animation export as options.
- Its strongest lane is Minecraft: dedicated Java block/item, Bedrock entity/block, modded entity and OptiFine formats with format-specific features.
- It is a cube- and low-poly-first editor with pixel art texturing; it is not a general sculpting or retopology tool.

## Examples

1. **Independent** Model a low-poly treasure chest with a 32x32 pixel texture and an open-lid animation, and export it as GLB with animations.
2. **Combined** Proposed handoff: export a Blockbench GLB and load it into a react-three-fiber scene for a web game.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- JavaScript plugins run with the app's privileges; install only plugins you trust.
- The pinned README describes no telemetry. The web app runs in the browser.

**Software license** GPL-3.0 (source code); plugins and themes are exempt; created assets belong to the user.

**Commercial use** The README says all assets made with Blockbench (models, textures, animations, screenshots) are your own, so exported models carry no GPL obligation. Changes to Blockbench's source fall under GPL-3.0. Plugins and themes that use the Blockbench API may be open source, proprietary or paid.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | Not stated in README.md or package.json. |
| installation | 'Then install all dependencies via `npm install`' and '`npm run dev`' (README.md) |
| runtime_requirements | '"engines": { "node": ">=20.0.0"' (package.json) |
| license | 'The Blockbench source-code is licensed under the GPL license version 3.' (README.md) |
| exported_assets | 'All assets created with Blockbench (models, textures, animations, screenshots etc.) are your own!' (README.md) |
| model_license | Not a model tool. |
| inputs | js/formats contains bbmodel.js, bedrock/, java/, optifine/ and standards/obj.js codecs (repository tree) |
| outputs | 'encoding: ... ascii: 'ASCII (glTF)', binary: 'Binary (glb)'' (js/formats/standards/gltf.js) |
| platforms | electron-builder config has 'mac', 'win' (nsis) and 'linux' targets (package.json) |

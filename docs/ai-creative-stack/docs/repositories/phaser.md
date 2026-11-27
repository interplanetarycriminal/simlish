# Phaser

Use for building 2D HTML5 games in JavaScript or TypeScript that run in desktop and mobile browsers.

> #44 · Game development · Source E (games) · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/phaserjs/phaser)
- Verified 2026-11-27 against default branch `master` at [`02d8931b626d`](https://github.com/phaserjs/phaser/commit/02d8931b626d9764c133cbb3fbf99966c03c757c).
- GitHub reports archive state **false** and a repository push at `2026-08-21T06:56:13Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/README.md)
- [package.json](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/package.json)
- [SKILL.md](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/skills/physics-matter/SKILL.md)
- [CustomMain.js](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/src/physics/matter-js/CustomMain.js)
- [Matter.js](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/src/physics/matter-js/lib/core/Matter.js)
- [Body.js](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/src/physics/matter-js/lib/body/Body.js)
- [World.js](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/src/physics/matter-js/World.js)

## Runtime, hardware and setup

- **Type** framework. Primary language JavaScript.
- **Platforms** Web.
- **Runtime** Phaser 4.2.1 (package.json). Runs in browsers; npm or CDN. Native/app-store targets need third-party wrappers.
- **Execution** local.
- **Agent paths** Claude Code, Cursor, Codex, Antigravity, GitHub Copilot, Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Game config selects renderer (WebGL or Canvas), physics (Arcade or Matter) and scenes. Matter stepping is configured via the matter 'runner' config (runner.fps for fixed timestep) or set60Hz/set30Hz.
- **Credentials and services** None. A free Phaser account is only needed to save Sandbox entries online.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npm install phaser
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | JavaScript/TypeScript scenes, Images, sprite sheets, atlases, audio, tilemaps (e.g. Tiled JSON) |
| Output | Browser game bundle (WebGL/Canvas) |
| Primary | Game engine |
| Supporting | Physics, Game audio, Animation, Visual effects, Prototyping |

Skip when the game is primarily 3D; Phaser 4 removed the v3 Mesh class and targets 2D. Consider [godot](godot.md), [babylonjs](babylonjs.md), [bevy](bevy.md). Complementary tools include [matter-js](matter-js.md), [howler](howler.md), [jsfxr](jsfxr.md), [ldtk](ldtk.md), [pixelorama](pixelorama.md), [colyseus](colyseus.md), [nakama](nakama.md), [ink](ink.md), [rapier](rapier.md), [pixelfx](pixelfx.md).

- Phaser 3 code needs migration: renderer, tint, FX/Masks, Shader API and lighting changed in v4.

## Craft notes

- Ships two physics systems in-tree: Arcade (src/physics/arcade) and a modified Matter.js 0.20.0 (src/physics/matter-js/lib, with 'Phaser change' and 'custom Phaser property' edits) wrapped by Phaser's own World/Factory.
- Renderers are WebGL (new v4 render-node architecture) and Canvas; audio managers are Web Audio, HTML5 Audio and NoAudio.
- Includes 28 agent SKILL.md files under skills/ (physics-arcade, physics-matter, v3-to-v4-migration, etc.); SpriteGPULayer claims a million or more sprites in one draw call.

## Examples

1. **Independent** Scaffold a Phaser 4 platformer with Arcade physics and a Tiled tilemap using npm create @phaserjs/game@latest.
2. **Combined** Proposed handoff: design a level in LDtk, export JSON, and load it as Phaser tilemap layers.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. fixtures/game-dev phaser-slice: phaser 4.2.1 (WebGL, headless Chrome) stepped at a fixed 1/60 s; the player lands on the platform, a held Right arrow moves it 197.33 px over 75 steps, a coin overlap scores, and a reload reproduces the state trace exactly.

## Security, privacy and licensing

- Standard browser sandbox; loading third-party plugins or assets from CDNs follows normal web supply-chain risks.
- README warns nothing about telemetry; none documented.

**Software license** MIT.

**Commercial use** MIT code allows commercial use. README states the Phaser logo and characters are (c) Phaser Studio Inc, all rights reserved, so do not reuse that branding.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| version | package.json: '"version": "4.2.1"' |
| physics | README.md: 'built-in physics (Arcade and Matter.js)'; lib/core/Matter.js: Matter.version = '0.20.0' |
| matter_custom | lib/body/Body.js: '// Phaser change: no point calling fromPath if they pass in vertices anyway' |
| hardware | README.md: 'phaser.min.js ... comes in at 345 KB with standard gzip' |
| installation | README.md: 'npm install phaser' |
| license | package.json: '"license": "MIT"'; README: 'The Phaser logo and characters are (c) 2011 - 2026 Phaser Studio Inc.' |
| model_license | Not applicable; no model weights. |
| inputs | README.md: 'You can use JavaScript or TypeScript for development.' |
| outputs | README.md: 'offers WebGL and Canvas rendering across desktop and mobile web browsers' |

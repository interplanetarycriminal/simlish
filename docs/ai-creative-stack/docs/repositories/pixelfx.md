# pixelfx

Use for dropping code-driven pixel art effects into a browser game, or exporting them as transparent PNG sprite sheets with Aseprite-style JSON for any engine.

> #70 · Expressive motion · Source F (expressive motion) · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/patch-gg/pixelfx)
- Verified 2026-11-27 against default branch `main` at [`5294518ce7c7`](https://github.com/patch-gg/pixelfx/commit/5294518ce7c72e48b6100a744596e0acf57f2826).
- GitHub reports archive state **false** and a repository push at `2026-11-13T08:43:39Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the expressive-animation post (source F, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/patch-gg/pixelfx/blob/5294518ce7c72e48b6100a744596e0acf57f2826/README.md)
- [package.json](https://github.com/patch-gg/pixelfx/blob/5294518ce7c72e48b6100a744596e0acf57f2826/package.json)
- [NOTICE.md](https://github.com/patch-gg/pixelfx/blob/5294518ce7c72e48b6100a744596e0acf57f2826/NOTICE.md)
- [render.mjs](https://github.com/patch-gg/pixelfx/blob/5294518ce7c72e48b6100a744596e0acf57f2826/tools/render.mjs)
- [SKILL.md](https://github.com/patch-gg/pixelfx/blob/5294518ce7c72e48b6100a744596e0acf57f2826/skills/pixelfx/SKILL.md)

## Runtime, hardware and setup

- **Type** library. Primary language JavaScript.
- **Platforms** Unverified.
- **Runtime** Node 18 or newer for the tools; the library has no runtime dependencies (devDependency esbuild ^0.25.10). ffmpeg is optional, for GIF and MP4 previews.
- **Execution** local.
- **Agent paths** Claude Code. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Each effect takes options such as x, y, flip, angle, seed, palette (a dark-to-bright hex ramp) and light; render tools take --gif, --mp4, --sheet, --all, --scale, --bg, --seed, --fps, --opts and --out.
- **Credentials and services** None. Publishing to Patch (optional) needs a Patch account via pch login.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npm i github:patch-gg/pixelfx
(skill) /plugin marketplace add patch-gg/pixelfx
/plugin install pixelfx@pixelfx
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | effect id, category or pattern (e.g. ice/frost-nova), options JSON (palette, seed, flip, angle), reference images for the skill's refine loop |
| Output | contact sheet PNG (records/<id>/contact.png), transparent PNG sprite sheet plus Aseprite-style JSON with frame rects, durations and meta.pixelfx (fps, loop, columns, pivot, act timing), GIF and MP4 previews (ffmpeg), live frames drawn into a canvas ImageData |
| Primary | Visual effects, Pixel art |
| Supporting | Animation, Prototyping |

Skip when you need hand-painted frame-by-frame sprite work or high-resolution VFX; pixelfx effects are small procedural pixel art drawn in code. Consider the existing project toolchain. Complementary tools include [phaser](phaser.md), [godot](godot.md), [pixelorama](pixelorama.md), [ldtk](ldtk.md), [three-js](three-js.md), [jsfxr](jsfxr.md).

## Craft notes

- 244 effects in 21 categories (12 moves; 61 character effects are acted out with wind-up, hit-stop freeze and recovery), each a single file in src/fx/<category>/<name>.js.
- node tools/render.mjs ice/frost-nova --sheet writes a transparent PNG grid and Aseprite-style JSON that Phaser's atlas loader and Aseprite importers for Godot and Unity read; node tools/sheets.mjs exports the whole library.
- Everything is seeded and pure effects are a function of time, so frame 40 is identical every render and loops tile without seams; the skill's quality loop is draft, render, look at the contact sheet, refine, and tools/check.mjs flags spills, seams and unseeded randomness.

## Examples

1. **Independent** Recolor fire/torch to a blue palette and export it as a sprite sheet with node tools/render.mjs --sheet.
2. **Combined** Proposed handoff: export pixelfx explosion sheets and load the PNG plus JSON atlas into a Phaser scene.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. fixtures/expressive-motion pixelfx-sheet: tools/render.mjs at the pinned commit writes ice-lance as a 528x512 transparent PNG with 24 frame rectangles in Aseprite-style JSON, all inside the sheet.

## Security, privacy and licensing

- The optional Patch CLI install suggests 'curl -fsSL https://patch.gg/install.sh | sh', which runs a remote script; npm i -g @patchgg/cli is the alternative.
- The README says the Patch install gives every agent on the PC Patch's tools; treat that as a global change.
- The library and render tools run locally; only the optional Patch publish step uploads a game.

**Software license** MIT (code and effects); the Patch Pixel font in gallery/fonts is not covered.

**Commercial use** MIT for code and effects: 'Use them in anything, commercial included.' Parts adapt Hugo Duprez's and Hollow Crown's MIT code (see NOTICE.md). The Patch Pixel gallery font is Patch's own and excluded.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'compatibility: Node 18 or newer. ffmpeg is optional (GIF and MP4 previews).' (skills/pixelfx/SKILL.md) |
| installation | 'Install from GitHub with `npm i github:patch-gg/pixelfx`' (README.md) |
| license | 'MIT, code and effects. Use them in anything, commercial included.' (README.md) |
| model_license | Not a model tool. |
| inputs | 'usage: node tools/render.mjs <id/category/pattern>... [--gif] [--mp4] [--sheet] [--all]' (tools/render.mjs) |
| outputs | 'a transparent PNG of every frame in a grid and an Aseprite-style JSON' (README.md) |
| effect_count | '244 pixel art effects and animations, every one a small piece of code.' (README.md) |

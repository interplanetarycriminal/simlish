# Matter.js

Use for 2D rigid-body physics in web pages and Node.js, from playful site interactions to simple physics games.

> #49 · Game development · Source E (games) · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/liabru/matter-js)
- Verified 2026-11-27 against default branch `master` at [`b8ee71cd7f9b`](https://github.com/liabru/matter-js/commit/b8ee71cd7f9b49f53639ddaedd6254f1929bcbe5).
- GitHub reports archive state **false** and a repository push at `2026-09-30T17:14:46Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/liabru/matter-js/blob/b8ee71cd7f9b49f53639ddaedd6254f1929bcbe5/README.md)
- [package.json](https://github.com/liabru/matter-js/blob/b8ee71cd7f9b49f53639ddaedd6254f1929bcbe5/package.json)
- [Runner.js](https://github.com/liabru/matter-js/blob/b8ee71cd7f9b49f53639ddaedd6254f1929bcbe5/src/core/Runner.js)
- [Engine.js](https://github.com/liabru/matter-js/blob/b8ee71cd7f9b49f53639ddaedd6254f1929bcbe5/src/core/Engine.js)
- [CHANGELOG.md](https://github.com/liabru/matter-js/blob/b8ee71cd7f9b49f53639ddaedd6254f1929bcbe5/CHANGELOG.md)

## Runtime, hardware and setup

- **Type** physics engine. Primary language JavaScript.
- **Platforms** Web.
- **Runtime** Browser or Node.js (README: Chrome, Firefox, Safari, IE8+). Version 0.20.0. Building the repo needs Node >=22.13.0 and pnpm >=11.11.0.
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Use Matter.Runner for a browser loop (runner.delta defaults to 1000/60 ms fixed timestep) or call Engine.update(engine, delta) yourself; deltas above 1000/60 ms trigger a warning.
- **Credentials and services** None.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npm install matter-js
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Bodies, composites, constraints via JS API, SVG paths for concave bodies (demo) |
| Output | Body positions/angles per step, Collision events, Canvas debug rendering |
| Primary | Physics |
| Supporting | Prototyping, Animation |

Skip if you need lockstep multiplayer or replays across machines; no determinism guarantee is documented, so prefer Rapier's -deterministic builds. Consider [rapier](rapier.md), [jolt-physics](jolt-physics.md). Complementary tools include [phaser](phaser.md), [rough-js](rough-js.md), [gsap](gsap.md), [howler](howler.md), [react-bits](react-bits.md), [colyseus](colyseus.md).

- Bundler dev modes (Webpack sourcemaps, Vue watchers) can hurt real-time performance per the README.

## Craft notes

- Since 0.20.0 Matter.Runner uses a fixed timestep (delta 1000/60 by default) and runs zero or more Engine.update calls per frame; docs suggest a delta that divides evenly into target display rates (e.g. 1000/240).
- Runner smooths and snaps frame deltas and caps updates per frame (maxUpdates, maxFrameTime); its docs say it favors smoothness over perfect time keeping and is mainly for development.
- For reproducible runs, call Engine.update with a constant delta in your own loop and keep API call order identical; this is a proposed practice, as no determinism claim appears in the pinned files.

## Examples

1. **Independent** Build a ball-pool hero section where Matter bodies fall into a Canvas and react to the mouse.
2. **Combined** Documented integration: Phaser bundles a modified Matter.js 0.20.0 as its 'matter' physics system.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. fixtures/game-dev matter-determinism: matter-js 0.20.0, a 10-box pyramid stepped 300 times at 1000/60 ms; two runs are bitwise equal and the pyramid comes to rest (same machine only).

## Security, privacy and licensing

- Plain JS library; no network access documented.
- None documented.

**Software license** MIT.

**Commercial use** MIT allows commercial use with the notice kept.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| version | package.json: '"version": "0.20.0"'; CHANGELOG.md: '## 0.20.0 (2024-06-23)' |
| fixed_step | CHANGELOG.md: 'added new Matter.Runner with default fixed timestep'; Runner.js: 'The fixed timestep size used for Engine.update calls' |
| runner_caveat | Runner.js: 'This runner favours a smoother user experience over perfect time keeping.' |
| engine_update | Engine.js: 'Moves the simulation forward in time by delta milliseconds.'; Engine._deltaMax = 1000 / 60 |
| hardware | README.md: 'Cross-browser and Node.js support (Chrome, Firefox, Safari, IE8+)' |
| installation | README.md: 'npm install matter-js' |
| license | README.md: 'Matter.js is licensed under The MIT License (MIT)' |
| model_license | Not applicable; no model weights. |
| inputs | README.md Features: 'Rigid bodies', 'Compound bodies', 'Constraints' |
| outputs | README.md Features: 'Canvas renderer (supports vectors and textures)', 'Events' |

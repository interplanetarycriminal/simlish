# howler.js

Use for playing, looping, spriting, fading and spatially panning sound in browser games and web apps with one API over Web Audio and HTML5 Audio.

> #53 · Game development · Source E (games) · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/goldfire/howler.js)
- Verified 2026-11-27 against default branch `master` at [`1d3053576a86`](https://github.com/goldfire/howler.js/commit/1d3053576a860e9854645493ad6c4a72c6cc6e45).
- GitHub reports archive state **false** and a repository push at `2025-11-23T23:49:01Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/goldfire/howler.js/blob/1d3053576a860e9854645493ad6c4a72c6cc6e45/README.md)
- [package.json](https://github.com/goldfire/howler.js/blob/1d3053576a860e9854645493ad6c4a72c6cc6e45/package.json)
- [howler.core.js](https://github.com/goldfire/howler.js/blob/1d3053576a860e9854645493ad6c4a72c6cc6e45/src/howler.core.js)

## Runtime, hardware and setup

- **Type** library. Primary language JavaScript.
- **Platforms** Unverified.
- **Runtime** Browser JavaScript, no outside dependencies (version 2.2.4). Tested in Chrome 7+, IE 9+, Firefox 4+, Safari 5.1.4+, Mobile Safari 6+ (after user input), Opera 12+, Edge.
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Pass sources in order of preference to new Howl({ src: [...] }); set html5: true for large or streamed files, sprite for sound sprites, and global options such as Howler.autoUnlock and html5PoolSize.
- **Credentials and services** None.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npm install howler
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Audio URLs or base64 data URIs: mp3, opus, ogg/oga, wav, aac, caf, m4a, m4b, mp4, weba/webm, dolby (in mp4), flac |
| Output | Audio playback through Web Audio or HTML5 Audio, stereo panning and 3D spatial audio (spatial plugin) |
| Primary | Game audio |
| Supporting | Media processing |

Skip if your engine's built-in audio already covers your needs, or if you need offline audio rendering or mixing to a file; howler only plays sound in the browser. Consider the existing project toolchain. Complementary tools include [phaser](phaser.md), [jsfxr](jsfxr.md), [three-js](three-js.md), [react-three-fiber](react-three-fiber.md), [babylonjs](babylonjs.md), [matter-js](matter-js.md).

## Craft notes

- Autoplay unlock: audio on mobile browsers and desktop Chrome/Safari stays locked until a sound plays inside a user interaction; autoUnlock (default true) tries to unlock on the first touch or click and fires an unlock event.
- If you autoplay on page load, listen for playerror and retry on the unlock event; HTML5 Audio nodes are unlocked one by one from a pool of html5PoolSize (default 10).
- It picks the first compatible source in your list, so the README advises webm first with an mp3 fallback, and webm needs cue elements (ffmpeg -dash 1) to seek in Firefox.

## Examples

1. **Independent** Load one audio sprite with jump, coin and hurt regions and play each on game events with per-sound volume.
2. **Combined** Proposed handoff: generate retro effects with jsfxr, save them as WAV, and play them through a howler sound sprite.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Loads audio from any URL you pass; serve your own assets to avoid mixed-content or CORS problems.
- No network calls beyond loading the audio sources you supply.

**Software license** MIT.

**Commercial use** MIT license: commercial use is allowed with the copyright notice kept.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'As light as 7kb gzipped' (README.md) |
| installation | 'Install with npm: `npm install howler`' (README.md) |
| license | 'Released under the MIT License.' (README.md) |
| model_license | Not a model tool. |
| inputs | '("mp3", "opus", "ogg", "wav", "aac", "m4a", "m4b", "mp4", "webm", ...)' (README.md); codec table also lists caf, weba, dolby, flac (src/howler.core.js) |
| outputs | 'Defaults to Web Audio API and falls back to HTML5 Audio' (README.md) |
| autoplay | 'audio on mobile browsers and Chrome/Safari is locked until a sound is played within a user interaction' (README.md) |
| autoUnlock | 'autoUnlock `Boolean` `true` Automatically attempts to enable audio on mobile ... and desktop Chrome/Safari.' (README.md) |

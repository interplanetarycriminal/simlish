# Theatre.js

Use for authoring detailed keyframed animation of three.js scenes, DOM/SVG or any JS value in a visual studio, then playing or seeking it in code with @theatre/core.

> #74 · Expressive motion · Source F (expressive motion) · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/theatre-js/theatre)
- Verified 2026-11-27 against default branch `main` at [`6ea82b938ea4`](https://github.com/theatre-js/theatre/commit/6ea82b938ea49609489f6377ded693ccc6ee8f5b).
- GitHub reports archive state **false** and a repository push at `2024-08-14T13:20:18Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the expressive-animation post (source F, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/theatre-js/theatre/blob/6ea82b938ea49609489f6377ded693ccc6ee8f5b/README.md)
- [package.json](https://github.com/theatre-js/theatre/blob/6ea82b938ea49609489f6377ded693ccc6ee8f5b/packages/core/package.json)
- [package.json](https://github.com/theatre-js/theatre/blob/6ea82b938ea49609489f6377ded693ccc6ee8f5b/packages/studio/package.json)
- [package.json](https://github.com/theatre-js/theatre/blob/6ea82b938ea49609489f6377ded693ccc6ee8f5b/packages/r3f/package.json)
- [TheatreSequence.ts](https://github.com/theatre-js/theatre/blob/6ea82b938ea49609489f6377ded693ccc6ee8f5b/packages/core/src/sequences/TheatreSequence.ts)

## Runtime, hardware and setup

- **Type** library. Primary language TypeScript.
- **Platforms** Unverified.
- **Runtime** Browser JavaScript. @theatre/core, @theatre/studio and @theatre/r3f are at 0.7.0. @theatre/r3f peers: @react-three/fiber ^8.13.6, react and react-dom >=17.0.2, three >=0.155.0.
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Create a project, sheet and objects with @theatre/core; load @theatre/studio only during design to edit keyframes; ship saved project state with core only.
- **Credentials and services** None.

No install command is documented upstream. Follow the pinned documentation.

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | JS objects and props to animate, three.js / react-three-fiber scenes (via @theatre/r3f), audio for sequence sync (AudioPlaybackController) |
| Output | animated values driven by a sequence, saved project state JSON from the studio |
| Primary | Animation |
| Supporting | 3D rendering, Frontend implementation, Video composition |

Skip if you need an actively maintained public codebase or React 19 / R3F v9 support: the last public push is 2024-08-14, the README says development moved to a private repo, and @theatre/r3f peers on @react-three/fiber ^8. Consider [gsap](gsap.md), [motion](motion.md). Complementary tools include [react-three-fiber](react-three-fiber.md), [three-js](three-js.md).

## Craft notes

- sequence.position is a settable getter, so you can seek to any time and render frames deterministically; play() and pause() control realtime playback, and audio can drive the sequence.
- The @theatre/r3f extension edits react-three-fiber scenes visually but targets R3F v8 (React 18) at this commit.
- Maintenance risk: the README announces Theatre.js 1.0 in a private repo, and the public main branch has not moved since August 2024.

## Examples

1. **Independent** Keyframe a camera move and a light fade in the studio, then seek sequence.position frame by frame to export stills.
2. **Combined** Proposed handoff: animate a react-three-fiber v8 scene with @theatre/r3f and render frames with R3F's frameloop='never' plus advance().

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. fixtures/expressive-motion theatre-seek: @theatre/core 0.7.2 with a hand-written project state; 49 seeks over 2 s match the keyframes exactly and repeat identically.

## Security, privacy and licensing

- Do not ship @theatre/studio in production bundles; it is the editing UI.
- No network calls described for core; the repo also contains a sync-server package not covered by the README.

**Software license** Apache-2.0 for @theatre/core and most packages; AGPL-3.0-only for @theatre/studio.

**Commercial use** The README says final bundles include only @theatre/core, so only Apache-2.0 applies to shipped projects. @theatre/studio is AGPL-3.0-only; shipping or serving the studio to users brings AGPL obligations.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | Not stated in README.md. |
| installation | No install command in README.md; it points to theatrejs.com/docs. |
| license | 'Theatre's core (`@theatre/core`) is released under the Apache License.' (README.md) |
| studio_license | 'The studio (`@theatre/studio`) is released under the AGPL 3.0 License.' (README.md) |
| model_license | Not a model tool. |
| inputs | 'Animate 3D objects made with THREE.js or other 3D libraries' (README.md) |
| outputs | 'get position()' and 'set position(position: number)' (packages/core/src/sequences/TheatreSequence.ts) |
| maintenance | 'We have _temporarily_ moved development to a private repo so we can iterate faster.' (README.md) |
| r3f_peer | '"@react-three/fiber": "^8.13.6"' in peerDependencies (packages/r3f/package.json) |

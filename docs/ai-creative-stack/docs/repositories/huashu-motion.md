# Huashu Motion

Use for having a coding agent write, score and render a short product launch film or data explainer as a single HTML page, then revise it by clicking on frames in a local editor.

> #33 · Motion films, explainers and engines · Source D (cinema) · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/alchaincyf/huashu-motion)
- Verified 2026-11-26 against default branch `main` at [`f4f38bfe295a`](https://github.com/alchaincyf/huashu-motion/commit/f4f38bfe295a3f768753857be9236cc3277c7dad).
- GitHub reports archive state **false** and a repository push at `2026-11-23T06:08:00Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the cinematic post (source D, transcript supplied by the user on 2026-11-26); first added to this catalogue on 2026-11-26.

- [README.md](https://github.com/alchaincyf/huashu-motion/blob/f4f38bfe295a3f768753857be9236cc3277c7dad/README.md)
- [README.en.md](https://github.com/alchaincyf/huashu-motion/blob/f4f38bfe295a3f768753857be9236cc3277c7dad/README.en.md)
- [THIRD_PARTY.md](https://github.com/alchaincyf/huashu-motion/blob/f4f38bfe295a3f768753857be9236cc3277c7dad/THIRD_PARTY.md)
- [package.json](https://github.com/alchaincyf/huashu-motion/blob/f4f38bfe295a3f768753857be9236cc3277c7dad/package.json)
- [LICENSE.md](https://github.com/alchaincyf/huashu-motion/blob/f4f38bfe295a3f768753857be9236cc3277c7dad/music/LICENSE.md)

## Runtime, hardware and setup

- **Type** skill. Primary language JavaScript.
- **Platforms** macOS.
- **Runtime** Node 22+; an installed Chrome, Chromium or Edge (used for preview, stills and render, nothing extra downloaded); FFmpeg. Optional: sampled instruments via 'om samples build' (~55 MB); Kokoro narration needs uv and Python 3.12 (~325 MB model); word timing needs whisper-cli (brew install whisper-cpp).
- **Execution** local.
- **Agent paths** Claude Code, Codex, WorkBuddy, Grok Bot, Muse, Dots, Any Agent Skills-compatible agent. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** The skill drives a bundled 'om' CLI (om new, om studio, om render, om doctor); 'om doctor' reports missing dependencies. Studio UI language follows the browser or --lang / OM_LANG.
- **Credentials and services** None documented; the README says music is generated on the machine with no paid API, and narration uses macOS system voices or local Kokoro.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npx skills add alchaincyf/huashu-motion
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | One-sentence brief or product URL, Real product assets via 'om grab' (web screenshots, logos, brand colors, fonts, local project screenshots and recordings), CSV data (for data explainers), Your own voice recording (e.g. .m4a), Your own music track (e.g. .mp3) via 'om music add', Click-to-comment edits in the browser editor |
| Output | Film source as one index.html (GSAP, Canvas, Three.js, SVG), MP4, MOV with transparency, WebM, GIF, Shareable HTML page with player and source, Share pack: GIF under 10 MB plus share.md post text, Transparent overlay packages for other editors |
| Primary | Video composition, Animation, Creative direction |
| Supporting | Shot planning, Media processing, Design critique |

Skip when the film needs real people or live-action footage generated for you; every frame is drawn in code and real footage must be your own. Consider [hyperframes](hyperframes.md), [remotion](remotion.md), [onetake](onetake.md), [lemo-opuscar](lemo-opuscar.md), [anything2explainer](anything2explainer.md), [motion-canvas](motion-canvas.md), [motionmaxxing](motionmaxxing.md). Complementary tools include [gsap](gsap.md), [three-js](three-js.md), [ffmpeg](ffmpeg.md), [openscreen](openscreen.md).

Its own renderer driving local Chrome; uses GSAP, Canvas, three.js and SVG in one index.html.

- Skip if you cannot run Node 22, a local Chrome and FFmpeg; the README states it is tested on macOS only.

## Craft notes

- Composer mode: the agent writes an ABC-notation score whose markers align with scenes, then plays it with sampled grand piano, strings and drums (synth fallback), plus 23 sound effects tied to animation landing lines.
- Director rules come from 21 measured launch films and 142 dissected motion films, distilled into 20 motion languages and a rhythm sheet (hook within 3 s, a mid-film burst, a held beat before the loudest hit).
- It cannot hear: the agent checks audio by score, energy curve and spectrogram, so a human must do the final listen; 'om qa --sheet' tiles 4 frames per second to spot static or slideshow-like stretches.

## Examples

1. **Independent** Ask the agent for a 30-second launch film from your product URL, pick one of three directions, then press C in om studio to fix one frame.
2. **Combined** Proposed handoff: build a product object in three-js and drop it into a huashu-motion 'object-3d' template, then score and render the film with om render.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Runs a local preview and editor in the browser; the README notes Codex's sandbox blocks the local preview and browser until you approve them.
- First use of 'om voice' downloads Kokoro files from kokoro-onnx releases and whisper.cpp models from Hugging Face; 'om samples build' downloads samples from their original sources.
- The skill records your stated preferences and editor comments as lessons; the README says these stay on your own computer.
- 'om grab' fetches your product's web pages to collect screenshots, logos and colors.

**Software license** MIT (code and docs), with bundled GSAP under the GSAP Standard 'no charge' License, fonts under SIL OFL 1.1, and an AI-generated default music library under a CC0-style dedication.

**Commercial use** MIT allows commercial use of the code and docs. The 'bean Huashu' cartoon character in runtime/clip/lib/toon.js is excluded and only licensed for this project's demos. Default music tracks may be used commercially but carry no warranty against Content ID matches, and the author asks that they not be registered with Content ID. Films of 4 s or more get a small 'Made with huashu-motion' end line by default; you can ask the agent to turn it off.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'A 30-second film renders in about 12-15 s on my 14-core Mac' (README.en.md) |
| supported_platforms | 'Tested on macOS only so far.' (README.en.md) |
| installation | 'npx skills add alchaincyf/huashu-motion' (README.md) |
| license | 'huashu-motion's own code and docs are MIT. These bundled pieces keep their own licenses' (THIRD_PARTY.md) |
| model_license | Not a model; Kokoro and whisper.cpp models 'keep their own licenses and are not redistributed here' (THIRD_PARTY.md) |
| inputs | 'om grab' collects 'web screenshots, logo, images, brand colours and fonts' (README.md table, translated) |
| outputs | 'MP4, MOV (transparent), WebM, GIF; or export a share page with player and source' (README.md, translated) |
| runtime_requirements | 'Node 22+.' and Chrome 'already installed on the machine' (README.en.md, THIRD_PARTY.md) |
| renderer | 'Its own render engine. Several Chrome instances at once' (README.en.md); GSAP 3.14.2 bundled in templates/blank/vendor (THIRD_PARTY.md) |
| music | default library 'instrumental pieces generated by the repository author ... with AI music-generation tools' (music/LICENSE.md) |

# reanimate

Use for cloning an animation from a live site, screen recording, mp4, gif or Lottie file into your own code, then filming the copy and comparing it frame by frame until timing and easing match.

> #72 · Expressive motion · Source F (expressive motion) · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/NiazMorshed2007/reanimate)
- Verified 2026-11-27 against default branch `main` at [`3f7a55a2986a`](https://github.com/NiazMorshed2007/reanimate/commit/3f7a55a2986a84ca2173e86ee9127eefe31d046d).
- GitHub reports archive state **false** and a repository push at `2026-10-31T12:49:35Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the expressive-animation post (source F, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/NiazMorshed2007/reanimate/blob/3f7a55a2986a84ca2173e86ee9127eefe31d046d/README.md)
- [SKILL.md](https://github.com/NiazMorshed2007/reanimate/blob/3f7a55a2986a84ca2173e86ee9127eefe31d046d/skills/reanimate/SKILL.md)
- [package.json](https://github.com/NiazMorshed2007/reanimate/blob/3f7a55a2986a84ca2173e86ee9127eefe31d046d/skills/reanimate/scripts/package.json)

## Runtime, hardware and setup

- **Type** skill. Primary language JavaScript.
- **Platforms** macOS, Linux.
- **Runtime** Bun 1.1 or later. The first run installs a static ffmpeg into the skill folder and Playwright's Chromium (playwright 1.64.1), about 250 MB together. Script dependencies: ffmpeg-static ^5.2.0, pixelmatch ^8.0.0, pngjs ^7.0.0.
- **Execution** local.
- **Agent paths** Claude Code. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Say the target, source and destination file; the match level is chosen by wording (default 'moves the same', or 'match it exactly' for 2% or lower pixel mismatch). Capture flags include --clock virtual, --gl, --assets and --gpu hardware.
- **Credentials and services** None; the README says no API keys.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npx skills add NiazMorshed2007/reanimate -g
bash <skill>/scripts/setup.sh
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | live website URL (with triggers: load, scroll, hover, pointer path, drag, click), screen recordings (mov, mp4, webm), gif, Lottie file, prototype export |
| Output | animation code in your project (CSS, Framer Motion, GSAP, three.js), spec table per element and property, captured video, frames and per-frame element tracks, GPU traces (shaders, uniforms, passes), comparison numbers and side-by-side diff sheets, final report of what still differs |
| Primary | Animation, Frontend implementation |
| Supporting | Visual effects, Design critique, 3D rendering |

Skip if the reference sits behind a login, on YouTube or on Loom; hand it a screen recording instead, or skip when you lack rights to reuse the reference's assets. Consider the existing project toolchain. Complementary tools include [motion](motion.md), [gsap](gsap.md), [three-js](three-js.md), [react-three-fiber](react-three-fiber.md), [ffmpeg](ffmpeg.md).

## Craft notes

- Loop: record the reference, write a spec, build in the project's stack, record the clone the same way, compare, and fix the biggest gap, usually 2 to 5 rounds; leftovers after 5 rounds are reported with reasons.
- --clock virtual steps a seeded virtual clock so captures are identical, and --gl traces WebGL, WebGPU and canvas 2D, hooking three.js, Pixi, PlayCanvas, Babylon and OGL scene graphs.
- Springs are fitted from overshoot and settle time rather than read from source, workers run on real-time clocks, and random particles fall back to a blurred density comparison.

## Examples

1. **Independent** Clone the hero entrance of a public landing page into components/Hero.tsx and match timing within 80 ms.
2. **Combined** Proposed handoff: let reanimate measure a reference's easing curves, then implement the result with Motion's animate() in a React app.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Runs headless Chromium against third-party sites and can save their models, textures and scripts with --assets.
- setup.sh downloads Playwright's Chromium and a static ffmpeg on first run.
- Captures stay local; no API keys or hosted services are used.

**Software license** MIT.

**Commercial use** MIT for the skill. The README warns that fonts, images and code copied from another site still belong to their owners; check you may use what you clone.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'The default, SwiftShader, is slower but gives the same pixels on every machine.' (README.md) |
| runtime_requirements | 'Needs Bun 1.1 or later, on macOS or Linux (Windows is untested).' (README.md) |
| installation | 'npx skills add NiazMorshed2007/reanimate -g' (README.md) |
| license | '## License MIT.' (README.md) |
| model_license | Not a model tool. |
| inputs | 'works from a live site, a screen recording, an mp4, a gif or a Lottie file.' (README.md) |
| outputs | 'It writes the animation with what your project already uses: CSS, Framer Motion, GSAP, three.js.' (README.md) |
| repository | GitHub repository NiazMorshed2007/reanimate resolves at the pinned SHA 3f7a55a with skills/reanimate/ and site/ (git tree) |

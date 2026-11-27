# GSAP

Use for browser animation of CSS, SVG, canvas, WebGL or any JS object with sequenced, seekable timelines that frame-by-frame renderers can drive deterministically.

> #39 · Motion films, explainers and engines · Source D (cinema), also listed in Source F (expressive motion) · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/greensock/GSAP)
- Verified 2026-11-26 against default branch `master` at [`5e6c35ff8eed`](https://github.com/greensock/GSAP/commit/5e6c35ff8eedea12d4f229129def635277d8b0f2).
- GitHub reports archive state **false** and a repository push at `2026-11-04T00:56:41Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the cinematic post (source D, transcript supplied by the user on 2026-11-26); first added to this catalogue on 2026-11-26.

- [README.md](https://github.com/greensock/GSAP/blob/5e6c35ff8eedea12d4f229129def635277d8b0f2/README.md)
- [package.json](https://github.com/greensock/GSAP/blob/5e6c35ff8eedea12d4f229129def635277d8b0f2/package.json)
- [gsap-core.js](https://github.com/greensock/GSAP/blob/5e6c35ff8eedea12d4f229129def635277d8b0f2/src/gsap-core.js)
- [animation.d.ts](https://github.com/greensock/GSAP/blob/5e6c35ff8eedea12d4f229129def635277d8b0f2/types/animation.d.ts)
- [gsap-core.d.ts](https://github.com/greensock/GSAP/blob/5e6c35ff8eedea12d4f229129def635277d8b0f2/types/gsap-core.d.ts)

## Runtime, hardware and setup

- **Type** library. Primary language JavaScript.
- **Platforms** Unverified.
- **Runtime** Any major browser; zero dependencies. Pinned version 3.15.1; ES modules plus UMD files in /dist; @gsap/react provides useGSAP().
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Import the core and register plugins with gsap.registerPlugin(ScrollTrigger, Draggable, Flip, MotionPathPlugin); all tools are also exported from 'gsap/all'.
- **Credentials and services** None.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npm install gsap
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | DOM elements and CSS properties, SVG, Canvas and WebGL objects, Generic JavaScript objects, Colors, strings and motion paths |
| Output | Tweened property values over time, Seekable tweens and timelines |
| Primary | Animation, Frontend implementation |
| Supporting | Video composition |

Skip if your project requires an OSI-approved open-source license for every dependency; GSAP's standard license is a custom no-charge license. Consider [motion-canvas](motion-canvas.md), [react-bits](react-bits.md), [motion](motion.md), [theatre](theatre.md). Complementary tools include [hyperframes](hyperframes.md), [three-js](three-js.md), [huashu-motion](huashu-motion.md), [matter-js](matter-js.md), [motionmaxxing](motionmaxxing.md), [reanimate](reanimate.md).

kit/framecap seeks GSAP pages by pausing gsap.globalTimeline (tested). HyperFrames lists GSAP as an animation runtime; huashu-motion vendors GSAP.

- Skip for frame rendering pipelines that cannot hook the clock unless you unhook the ticker; GSAP otherwise advances on requestAnimationFrame.

## Craft notes

- Every tween and timeline is seekable: seek(time), time(t), totalTime(t) and progress(p) move the playhead, which is what HTML-to-video renderers exploit.
- For deterministic capture, remove the default clock with gsap.ticker.remove(gsap.updateRoot) and step gsap.updateRoot(t) yourself; gsap.globalTimeline is the root, and gsap.exportRoot() moves all running tweens into one controllable timeline.
- Plugins in this repo include ScrollTrigger, ScrollSmoother, Flip, Draggable, Observer, MotionPathPlugin, MorphSVGPlugin, SplitText, DrawSVGPlugin, ScrambleTextPlugin, CustomEase, InertiaPlugin, Physics2D and PixiPlugin.

## Examples

1. **Independent** Build a GSAP timeline of a logo reveal with SplitText and MotionPathPlugin, then scrub it with timeline.progress() in the browser.
2. **Combined** Documented by huashu-motion: its blank template vendors GSAP 3.14.2 and its own renderer drives the page frame by frame in Chrome; proposed: the same pattern with hyperframes.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. gsap 3.13.0 from jsDelivr in kit/framecap's gsapTimeline test: a seeked tween lands within 0.054 px of its expected position in all 24 frames. fixtures/expressive-motion gsap-vs-motion-ownership: GSAP owns x within 0.0003 px beside Motion on opacity; when both animate x the last writer wins silently and GSAP's cache goes stale.

## Security, privacy and licensing

- Loading from a CDN adds a third-party script dependency; self-host or pin the version for reproducible renders.
- Runs entirely in the browser; no network calls beyond loading the script.

**Software license** GreenSock Standard 'no charge' license (https://gsap.com/standard-license); 'Copyright 2008-2026, GreenSock. All rights reserved.' No license file in the repo.

**Commercial use** The README says GSAP is 100% free, including all former Club plugins (SplitText, MorphSVG and others), even for commercial use, thanks to Webflow. It is a proprietary no-charge license, not an OSI open-source license; the full terms live only at gsap.com/standard-license, so any use-specific restrictions are not established from the pinned files.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'At its core, GSAP is a high-speed property manipulator' running in the browser; no hardware requirements stated (README.md) |
| installation | 'npm install gsap' (README.md) |
| license | 'license': "Standard 'no charge' license: https://gsap.com/standard-license." (package.json); 'Subject to the terms at https://gsap.com/standard-license' (src/gsap-core.js) |
| model_license | Not a model tool |
| commercial | 'the entire GSAP toolset is FREE, even for commercial use!' (README.md) |
| inputs | 'Animate CSS, SVG, canvas, React, Vue, WebGL, colors, strings, motion paths, generic objects' (README.md) |
| outputs | 'anim.seek(1); // moves the playhead to the 1 second mark' (types/animation.d.ts) |
| updateRoot | 'Manually update the root (global) timeline. Make sure to unhook GSAP's default ticker.' (types/gsap-core.d.ts) |

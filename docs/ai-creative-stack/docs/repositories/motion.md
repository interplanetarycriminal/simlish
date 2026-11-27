# Motion (formerly Framer Motion)

Use for animating React, vanilla JavaScript and Vue interfaces with springs, gestures, layout transitions, scroll-linked effects and timelines.

> #73 · Expressive motion · Source F (expressive motion) · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/motiondivision/motion)
- Verified 2026-11-27 against default branch `main` at [`6390e6d2ddde`](https://github.com/motiondivision/motion/commit/6390e6d2ddde40128258aaa0499587505f008f1e).
- GitHub reports archive state **false** and a repository push at `2026-11-26T15:35:10Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the expressive-animation post (source F, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/motiondivision/motion/blob/6390e6d2ddde40128258aaa0499587505f008f1e/README.md)
- [package.json](https://github.com/motiondivision/motion/blob/6390e6d2ddde40128258aaa0499587505f008f1e/packages/motion/package.json)
- [package.json](https://github.com/motiondivision/motion/blob/6390e6d2ddde40128258aaa0499587505f008f1e/packages/framer-motion/package.json)
- [GroupAnimation.ts](https://github.com/motiondivision/motion/blob/6390e6d2ddde40128258aaa0499587505f008f1e/packages/motion-dom/src/animation/GroupAnimation.ts)
- [MotionConfigContext.tsx](https://github.com/motiondivision/motion/blob/6390e6d2ddde40128258aaa0499587505f008f1e/packages/framer-motion/src/context/MotionConfigContext.tsx)
- [use-reduced-motion.ts](https://github.com/motiondivision/motion/blob/6390e6d2ddde40128258aaa0499587505f008f1e/packages/framer-motion/src/utils/reduced-motion/use-reduced-motion.ts)

## Runtime, hardware and setup

- **Type** library. Primary language TypeScript.
- **Platforms** Unverified.
- **Runtime** Browser JavaScript. The motion and framer-motion packages (both 14.14.0) have optional peer dependencies react and react-dom ^18.0.0 || ^19.0.0. Vue uses the separate motion-v package.
- **Execution** local.
- **Agent paths** Generic coding agent via project files, Claude Code, Cursor, Amp, OpenCode, Gemini CLI and Copilot via the separate npx motion-ai skill (motiondivision/ai-kit). Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Import from motion/react for React or from motion for vanilla JS; MotionConfig sets tree-wide transition defaults and reducedMotion.
- **Credentials and services** None for the library. Motion+ and Motion Studio are separate paid products.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npm install motion
(Vue) npm install motion-v
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | DOM elements, React components, SVG, motion values and keyframes |
| Output | animated DOM/SVG styles, animation controls objects (play, pause, stop, cancel, complete, time, speed, duration) |
| Primary | Animation, Frontend implementation |
| Supporting | Prototyping |

Skip when you need a visual keyframe timeline editor in the browser; Theatre.js studio fits that, or use Motion Studio, which is a separate product. Consider [gsap](gsap.md), [theatre](theatre.md). Complementary tools include [react-bits](react-bits.md), [magic-ui](magic-ui.md), [react-three-fiber](react-three-fiber.md), [reanimate](reanimate.md), [remotion](remotion.md).

## Craft notes

- Framer Motion is now Motion: import from motion/react instead of framer-motion; both packages ship at the same version (14.14.0).
- animate() returns controls with play(), pause(), stop(), cancel(), complete() and settable time and speed, so a renderer can pause and seek by setting .time for frame-accurate offline capture.
- Reduced motion is opt-in: MotionConfig's reducedMotion defaults to 'never'; set it to respect the device setting, or use the useReducedMotion hook.

## Examples

1. **Independent** Build a staggered list entrance with motion/react and pause and scrub it with the controls' time property.
2. **Combined** Proposed handoff: animate DOM overlays with Motion on top of a react-three-fiber canvas.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. fixtures/expressive-motion motion-seek: motion 14.14.0 animate() paused and seeked matches an independent cubic-bezier within 0.0004 px; repeat, reverse and fresh-browser seeks are identical, and springs seek to the closed-form curve. The DOM write lands one frame after seeking.

## Security, privacy and licensing

- MotionConfig supports a nonce for Content Security Policy when inline styles are restricted.
- The library makes no network calls; the optional MCP server at mcp.motion.dev is a hosted docs service.

**Software license** MIT.

**Commercial use** MIT license: commercial use is allowed. Motion+ (examples, premium APIs, AI kit extras) is a separate paid license.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'Hybrid engine: Power of JavaScript combined with native browser APIs for 120fps, GPU-accelerated animations.' (README.md) |
| installation | 'npm install motion' (README.md) |
| license | 'Motion is MIT licensed.' (README.md) |
| model_license | Not a model tool. |
| inputs | 'animate("#box", { x: 100 })' (README.md) |
| outputs | GroupAnimation has 'get time()', 'set time(time: number)', 'play()', 'pause()' (packages/motion-dom/src/animation/GroupAnimation.ts) |
| reduced_motion | 'reducedMotion: "never",' default in MotionConfigContext (packages/framer-motion/src/context/MotionConfigContext.tsx) |
| rename | 'Framer Motion is now Motion. Import from `motion/react` instead of `framer-motion`.' (README.md) |

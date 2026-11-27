# Sakuga VFX

Use for an isolated anime-style interaction that fits the visual direction.

> #17 · Frontend components and creative coding · Source B, also listed in Source F (expressive motion) · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/finktheartist/sakuga-vfx)
- Verified 2026-11-26 against default branch `main` at [`c3dabb173928`](https://github.com/finktheartist/sakuga-vfx/commit/c3dabb173928a3ad2372183103caf2e6f50953d0).
- GitHub reports archive state **false** and a repository push at `2026-11-15T21:19:34Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/finktheartist/sakuga-vfx/blob/c3dabb173928a3ad2372183103caf2e6f50953d0/README.md)
- [LICENSE](https://github.com/finktheartist/sakuga-vfx/blob/c3dabb173928a3ad2372183103caf2e6f50953d0/LICENSE)

## Runtime, hardware and setup

- **Type** web component reference and skill. Primary language HTML.
- **Platforms** Browser.
- **Runtime** Browser custom elements. Demo uses Python static server.
- **Execution** local.
- **Agent paths** Claude Code and generic skill-capable clients. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Register only the required custom element and verify focus and reduced motion.
- **Credentials and services** No separate key established.

| Hardware | Documented value |
| --- | --- |
| GPU | unverified |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Not documented |
| CPU fallback | not applicable |
| Training versus inference | Not documented |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npx shadcn add finktheartist/sakuga-vfx/button
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | HTML controls and approved visual assets |
| Output | Animated custom elements |
| Primary | Visual effects |
| Supporting | Animation, Frontend implementation |

Skip when decorative feedback distracts from critical tasks. Consider [line-art-animation](line-art-animation.md), [magic-ui](magic-ui.md). Complementary tools include [rough-js](rough-js.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- Twelve ordinary controls (button, toggle, slider, checkbox and more) that squash, overshoot and throw drawn effects with manga lettering. Each is a single file, and all of them share one canvas and loop.
- Reduced motion turns every effect off and keeps the state changes. look.mjs stops the clock and saves frame sheets for review. Tested only in headless Chromium so far.

## Examples

1. **Independent** Add the button to a demo and verify clicks, keyboard activation and reduced motion.
2. **Combined** Pair an isolated accent with a static Rough.js illustration under shared art direction.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Review registry code and generated lettering provenance. Avoid relying on effects as status indicators.
- No external service in the documented base workflow.

**Software license** MIT.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.

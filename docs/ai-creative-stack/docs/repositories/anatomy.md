# Anatomy

Use for explaining a technical idea with an interactive isometric figure of an invented machine whose working embodies the concept, delivered as SVG, SVG plus WebGL, or beta 3D.

> #63 · Supplementary research candidates · Supplementary · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/wheresryan22/anatomy)
- Verified 2026-11-26 against default branch `main` at [`1482e8469b0a`](https://github.com/wheresryan22/anatomy/commit/1482e8469b0a9e0d8cc18ea2740a01423d29ae80).
- GitHub reports archive state **false** and a repository push at `2026-10-18T20:20:24Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Not attributable to any source post. Identified during related research.

- [README.md](https://github.com/wheresryan22/anatomy/blob/1482e8469b0a9e0d8cc18ea2740a01423d29ae80/README.md)

## Runtime, hardware and setup

- **Type** skill. Primary language JavaScript.
- **Platforms** Linux, Windows, macOS.
- **Runtime** Node.js 20.10+ using built-in modules only (examples rebuilt on Node 20.19 and 22.11); Chrome or Chromium for the verification checks (CHROME_PATH override); React 18+ only for React output. The skills CLI 1.7.1 asks for Node 22.20+.
- **Execution** local.
- **Agent paths** Claude Code, Antigravity, OpenCode, Codex, MiniMax Code. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** No settings file; the prompt states the idea with real numbers (or names the object) and where the figure will live: standalone HTML, a lone SVG, or React/Next.js, in light or dark theme.
- **Credentials and services** None (README: no API keys). Publishing to the community gallery uses your GitHub account.

| Hardware | Documented value |
| --- | --- |
| GPU | none (a WebGL-capable browser is needed for shader layers) |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | About 10 MB when the skills CLI copies the whole repository with examples. |
| CPU fallback | not applicable |
| Training versus inference | Not documented |
| Notes | 3D mode (beta): small figures run at 60 fps; the 380-part stress hand measured about 20 fps at 1440 px and 13-15 fps on a throttled phone profile. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npx skills add wheresryan22/anatomy -g
# or: npx skills add wheresryan22/anatomy -g -a claude-code
# or: git clone https://github.com/wheresryan22/anatomy.git ~/.claude/skills/anatomy
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Natural-language idea with real sizes, counts, rates and thresholds, Or a named object (espresso machine, lock, burner) and what should move |
| Output | Standalone HTML page, Standalone .svg with embedded styles, React/Next.js components (server component for static art, client component for motion), Node build script plus geometry modules, PNG screenshots, close-ups and contact sheets, A4 PDFs (poster, technical drawing, explainer) via scripts/print.mjs |
| Primary | Illustration, Animation |
| Supporting | Visual effects, 3D rendering, Frontend implementation |

Skip if you need charts or data plots, people, or exact maps; README says it draws machines, instruments, tools and furniture. Consider the existing project toolchain. Complementary tools include [three-js](three-js.md), [remotion](remotion.md), [react-bits](react-bits.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

- Skip for fast turnaround: a figure takes a long session, the Raptor build takes minutes, and a full 3D orbit audit takes 15-20 minutes for 30 parts.
- The 3D mode is beta, proved only on its example and one test figure.

## Craft notes

- Its strength is metaphor-as-mechanism: a cache key becomes a pin-tumbler lock, one GPU context becomes a gantry plotter, built from dozens of four-tone shaded isometric solids painted back to front, and every readout number comes from the same model that moves the parts.
- kit/audit.mjs proves nothing passes through anything and every end sits on a mount; scripts/lines.mjs fails any line that ends in mid-air; the skill tells the agent to read every PNG it makes.
- WebGL layers (fire, water, caustics) sit between back and front SVG in the same isometric camera, and the SVG still reads without WebGL; under reduced motion figures go still.

## Examples

1. **Independent** /anatomy explain how a token bucket rate limiter works, interactive
2. **Combined** Proposed handoff: have Anatomy emit a React figure, then render its motion to video with remotion for a product explainer.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Checks start headless Chrome with a temporary profile over a local port; in Codex the README suggests per-command approval, and warns that --sandbox danger-full-access lifts every limit.
- scripts/publish.mjs opens a pull request on anatomy-community only after showing what it will send and getting a yes.
- Runs locally with no network calls documented except the optional community-gallery publish, which sends the figure, a title and your GitHub name.

**Software license** MIT.

**Commercial use** MIT allows commercial use of the kit and of figures built with it; keep the MIT notice where kit code is inlined into shipped pages.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | "Node.js 20.10+ / builds, kit, checks / Built-in modules only: nothing to npm install." (README.md Requirements) |
| installation | "npx skills add wheresryan22/anatomy -g" (README.md Quick start) |
| license | "MIT © 2026 Ryan" (README.md License) |
| model_license | Not applicable; "No API keys and nothing to npm install" (README.md) |
| inputs | "Name the idea, not the drawing. Say what it should explain and give the real numbers" (README.md) |
| outputs | "a standalone HTML page, a lone .svg file with its styles embedded, or React/Next.js components" (README.md) |
| what_it_is | "A Claude skill that explains an idea by building it as a real, working object." (README.md) |

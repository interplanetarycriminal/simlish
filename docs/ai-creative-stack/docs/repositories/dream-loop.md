# Dream Loop

Use for driving an agent to build a game, app or 3D scene until a live screenshot matches an AI-generated target image, judged by a separate critic subagent.

> #65 · Supplementary research candidates · Supplementary · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/achimala/dream-loop)
- Verified 2026-11-26 against default branch `main` at [`9bddb901f7d0`](https://github.com/achimala/dream-loop/commit/9bddb901f7d071cfefdd21e264267c757177a9df).
- GitHub reports archive state **false** and a repository push at `2026-09-09T22:43:38Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Not attributable to any source post. Identified during related research.

- [README.md](https://github.com/achimala/dream-loop/blob/9bddb901f7d071cfefdd21e264267c757177a9df/README.md)
- [SKILL.md](https://github.com/achimala/dream-loop/blob/9bddb901f7d071cfefdd21e264267c757177a9df/SKILL.md)
- [fal.md](https://github.com/achimala/dream-loop/blob/9bddb901f7d071cfefdd21e264267c757177a9df/references/fal.md)
- [workflow.md](https://github.com/achimala/dream-loop/blob/9bddb901f7d071cfefdd21e264267c757177a9df/references/plus-mode/workflow.md)
- [assets-3d.md](https://github.com/achimala/dream-loop/blob/9bddb901f7d071cfefdd21e264267c757177a9df/references/plus-mode/assets-3d.md)
- [workflow.md](https://github.com/achimala/dream-loop/blob/9bddb901f7d071cfefdd21e264267c757177a9df/references/pro-mode/workflow.md)
- [assets-3d.md](https://github.com/achimala/dream-loop/blob/9bddb901f7d071cfefdd21e264267c757177a9df/references/pro-mode/assets-3d.md)
- [preview-server.py](https://github.com/achimala/dream-loop/blob/9bddb901f7d071cfefdd21e264267c757177a9df/scripts/preview-server.py)

## Runtime, hardware and setup

- **Type** skill. Primary language JavaScript.
- **Platforms** Unverified.
- **Runtime** An agent with image generation, vision input and (preferably) subagents; Node 18+ for scripts/fal-batch.mjs; Python 3 for scripts/preview-server.py; Blender optional.
- **Execution** local or hosted.
- **Agent paths** Codex, Claude Code, Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Choose Plus (orchestrator spawns worker subagents) or Pro (agent builds, fresh judge subagent scores) by subscription tier; working files go in a gitignored .dream-loop folder. Optional FAL_KEY or FAL_API_KEY enables image-to-3D jobs.
- **Credentials and services** An image-generation tool or API key (e.g. Gemini) is required; FAL_KEY or FAL_API_KEY is needed for image-to-3D asset generation.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npx skills add achimala/dream-loop
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | User description of the game/app/scene, Optional user-supplied target image, Screenshot of an existing product (for refinement), Time budget |
| Output | .dream-loop/target.png target image, Built app or scene code (e.g. Three.js), Judge verdicts scored 0-10, GLB assets from fal.ai image-to-3D, Screenshots in .dream-loop/captures |
| Primary | Creative direction, Design critique, 3D orchestration |
| Supporting | Frontend implementation, Image-to-3D, Texturing |

Skip when budget is tight: with no time budget it loops until exit criteria and the skill warns this may consume a lot of tokens; fal assets cost about $0.30 (Tripo H3.1) or $0.02 (Trellis) each. Consider the existing project toolchain. Complementary tools include [three-js](three-js.md), [blender-mcp](blender-mcp.md), [trellis-2](trellis-2.md), [comfyui-3d-pack](comfyui-3d-pack.md), [impeccable](impeccable.md).

Image-to-3D runs on fal.ai (Tripo or Trellis endpoints), a paid hosted service. Blender use is described but its Plus workflow says not to model in Blender.

- Despite the repo description, the Plus workflow says 'DO NOT use Blender for modeling'; Blender appears only as optional in the README.
- The Plus workflow tells very large models (GPT-6 Astra, Claude Fable) to stop and ask the user to switch to a smaller orchestrator model.
- README says it is only tested with GPT-6 Astra in Codex.

## Craft notes

- Core trick: generate a realistic in-engine screenshot (never 'concept art') as target.png, then iterate to match it down to the pixel.
- Pro judge rubric scores Composition 0-3, Lighting 0-3, Materials 0-3, Details 0-1; exit at score >= 8 with acceptable FPS, with explicit stall rules after 2 rounds without a full-point gain.
- Asset ladder: downloads only if allowed, then fal image-to-3D (Tripo H3.1 for hero assets, Trellis for small props), procedural only as last resort; generated GLBs often land in the wrong orientation or scale.

## Examples

1. **Independent** Build a 60 fps isometric Three.js fantasy scene that matches a generated target screenshot within a one-hour budget.
2. **Combined** Proposed handoff: use dream-loop's judge loop while three-js renders the scene and trellis-2 supplies prop meshes.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- fal-batch.mjs sends selected source images to fal.ai as data URIs and reads the key from the environment; it states it never prints credentials and never auto-resubmits accepted jobs.
- preview-server.py serves the whole working directory on 127.0.0.1:4172 and accepts PNG uploads up to 20 MB to /__capture.
- Screenshots of the product and the target image go to the image-generation provider and judge subagents; asset source images go to fal.ai.

**Software license** MIT License.

**Commercial use** Skill text and scripts are MIT. Generated images and fal.ai 3D assets follow the image provider's and fal model terms; Not established.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | No hardware stated; 'You need an AI agent with: access to image generation ... vision input ... subagents' (README.md) |
| installation | 'npx skills add achimala/dream-loop' (README.md) |
| license | 'license: MIT' (SKILL.md frontmatter); GitHub SPDX MIT |
| model_license | Not applicable; uses external image and fal models |
| inputs | 'If the user supplies this, use that directly. If not, you need to generate it.' (SKILL.md) |
| outputs | 'Store the image in .dream-loop/target.png' (SKILL.md) |
| blender_access | 'Install Blender if you want custom 3D modeling. The Blender MCP or scripting interface is preferred' (README.md) |
| credentials_required | 'requires Node 18+ and FAL_KEY or FAL_API_KEY' (references/fal.md) |

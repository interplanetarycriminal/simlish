# Remotion skills

Use for giving a coding agent Remotion's official best practices for creating, previewing, rendering and upgrading React-based video projects.

> Motion films, explainers and engines · Added by the user · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/remotion-dev/skills)
- Verified 2026-11-26 against default branch `main` at [`a3f4098a2afd`](https://github.com/remotion-dev/skills/commit/a3f4098a2afd0e13f6a6f8c8760e275f75457ea9).
- GitHub reports archive state **false** and a repository push at `2026-11-24T17:19:19Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Added directly by the user on 2026-11-26.

- [README.md](https://github.com/remotion-dev/skills/blob/a3f4098a2afd0e13f6a6f8c8760e275f75457ea9/README.md)
- [package.json](https://github.com/remotion-dev/skills/blob/a3f4098a2afd0e13f6a6f8c8760e275f75457ea9/package.json)
- [SKILL.md](https://github.com/remotion-dev/skills/blob/a3f4098a2afd0e13f6a6f8c8760e275f75457ea9/skills/remotion-best-practices/SKILL.md)
- [SKILL.md](https://github.com/remotion-dev/skills/blob/a3f4098a2afd0e13f6a6f8c8760e275f75457ea9/skills/remotion-license/SKILL.md)

## Runtime, hardware and setup

- **Type** skill collection. Primary language TypeScript.
- **Platforms** Unverified.
- **Runtime** A Remotion 4 project (skills are versioned 4.0.547); Node version not stated in this repo.
- **Execution** local.
- **Agent paths** Claude Code, Codex, Cursor, Kimi Code, OpenCode. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Install into an agent's skills folder; /remotion-best-practices routes to the specific skill, and /remotion-upgrade updates installed skills with Remotion.
- **Credentials and services** None for the skills. Map providers such as Mapbox or MapTiler, and Remotion Lambda, need their own accounts (not documented in this repo).

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npx remotion skills add
npx skills add remotion-dev/skills
gh skill install remotion-dev/skills
npx create-video@latest --skills
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Natural-language video requests, Existing Remotion project code, Element page or library URLs, Map data (GeoJSON, Mapbox, MapLibre, MapTiler, CesiumJS) |
| Output | Remotion compositions and React markup written by the agent, Rendered video or still via /remotion-render, Editable OpenTimelineIO timeline export, Studio preview |
| Primary | Video composition, Animation |
| Supporting | Frontend implementation, Media processing |

Skip if your project is not built on Remotion; the skills only cover Remotion APIs and workflows. Consider the existing project toolchain. Complementary tools include [remotion](remotion.md), [anything2explainer](anything2explainer.md), [ffmpeg](ffmpeg.md).

Agent skills for Remotion, generated from the Remotion monorepo's packages/skills folder.

- Skip redistribution or modification of the skill files until the license is clarified; the pinned repo states none.

## Craft notes

- Fourteen skills: remotion-best-practices (router), -create, -markup, -studio, -render, -maps, -elements, -captions, -saas, -interactivity, -docs, -license, -upgrade and -multimedia (Mediabunny).
- The router tells the agent to preserve edits a user made outside the conversation and to load reference files per task rather than everything at once.
- This repo is generated from the remotion-dev/remotion monorepo (packages/skills); each skill also ships agents/openai.yaml metadata.

## Examples

1. **Independent** Run '/remotion-create Make a promo video for a record store' and then '/remotion-render'.
2. **Combined** Proposed handoff: pair it with anything2explainer so its build agents follow remotion-markup rules while writing per-shot components.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- /remotion-docs fetches pages from remotion.dev as Markdown into the agent's context.
- /remotion-elements installs third-party Element components from library URLs; review what they add.
- No data collection described in the pinned files.

**Software license** No license stated in the pinned repo (no LICENSE file; package.json is private with no license field).

**Commercial use** Not established for the skill files. The /remotion-license skill points to remotion.dev's license, FAQ and pricing pages; Remotion itself has separate terms for companies.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | No hardware stated; skills are Markdown guidance (README.md) |
| installation | 'npx remotion skills add' and 'npx skills add remotion-dev/skills' (README.md) |
| license | Tree at pinned SHA has no LICENSE file; package.json has '"private": true' and no license field |
| model_license | Not a model tool |
| inputs | 'Example prompt: /remotion-maps Animate a route from Los Angeles to New York' (README.md) |
| outputs | 'Render a video or still, or export an editable OpenTimelineIO timeline.' (README.md) |
| agents | 'useful for AI agents like Claude Code, Codex, Cursor, Kimi Code and OpenCode' (README.md) |

# Stitch Skills

Use for prompt-to-prototype in an approved Google Stitch workflow.

> #06 · Design and prototyping · Source A · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/google-labs-code/stitch-skills)
- Verified 2026-11-26 against default branch `main` at [`75f4696f1620`](https://github.com/google-labs-code/stitch-skills/commit/75f4696f162000fb69fca6a31489b5b21d47a506).
- GitHub reports archive state **false** and a repository push at `2026-11-24T21:51:04Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/google-labs-code/stitch-skills/blob/75f4696f162000fb69fca6a31489b5b21d47a506/README.md)
- [LICENSE](https://github.com/google-labs-code/stitch-skills/blob/75f4696f162000fb69fca6a31489b5b21d47a506/LICENSE)

## Runtime, hardware and setup

- **Type** skill collection. Primary language TypeScript.
- **Platforms** Unverified.
- **Runtime** Agent plugin or skill and Stitch MCP for remote actions
- **Execution** hosted.
- **Agent paths** Codex, Claude Code, Cursor, OpenCode. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Enable only the chosen plugin and verify the separately configured Stitch connection.
- **Credentials and services** Google Stitch access and MCP authentication per host.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npx plugins add google-labs-code/stitch-skills --scope project --target claude-code
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Brief and Stitch project or screen identifiers |
| Output | Stitch designs and handoff artifacts, depending on skill |
| Primary | Prototyping |
| Supporting | Creative direction, Frontend implementation |

Skip when policy prohibits remote design submissions. Consider [penpot](penpot.md), [open-design](open-design.md). Complementary tools include [magic-ui](magic-ui.md), [awesome-design-md](awesome-design-md.md), [designlang](designlang.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- Generates screens and variants in Google Stitch, extracts a DESIGN.md from existing code and pushes code back into a Stitch design.
- Needs the Stitch MCP and a Google account. Treat it as a hosted ideation lane, not the source of truth.

## Examples

1. **Independent** Prototype one onboarding screen, then compare it against the flow requirements.
2. **Combined** Implement approved design decisions in the app and keep Stitch output as reference.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Review remote project access and which assets leave the workspace.
- Screens, prompts and code go to Google Stitch.

**Software license** Apache-2.0.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.

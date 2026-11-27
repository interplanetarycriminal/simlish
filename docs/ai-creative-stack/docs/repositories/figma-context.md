# Figma Context MCP

Use when an existing Figma frame is the source of truth.

> #11 · Design and prototyping · Source A · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/GLips/Figma-Context-MCP)
- Verified 2026-11-26 against default branch `main` at [`c083d65c7e00`](https://github.com/GLips/Figma-Context-MCP/commit/c083d65c7e002923e7cb98f4e3bdafb105e90f6d).
- GitHub reports archive state **false** and a repository push at `2026-11-15T22:22:42Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/GLips/Figma-Context-MCP/blob/c083d65c7e002923e7cb98f4e3bdafb105e90f6d/README.md)
- [LICENSE](https://github.com/GLips/Figma-Context-MCP/blob/c083d65c7e002923e7cb98f4e3bdafb105e90f6d/LICENSE)
- [package.json](https://github.com/GLips/Figma-Context-MCP/blob/c083d65c7e002923e7cb98f4e3bdafb105e90f6d/package.json)

## Runtime, hardware and setup

- **Type** MCP server. Primary language TypeScript.
- **Platforms** Unverified.
- **Runtime** Node and npm for local runner
- **Execution** local or hosted.
- **Agent paths** Cursor documented. Codex and Claude Code transport mapping requires a smoke test.. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Set FIGMA_API_KEY using client environment and keep the MCP transport local where feasible.
- **Credentials and services** Figma API token with access to the selected file.

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
npx -y figma-developer-mcp --stdio
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Figma file or node reference via authorized API |
| Output | Simplified layout context and downloadable images |
| Primary | Prototyping |
| Supporting | Frontend implementation |

Skip when permissions are unavailable or prototype can remain local. Consider [penpot](penpot.md), [open-design](open-design.md). Complementary tools include [magic-ui](magic-ui.md), [designlang](designlang.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- Framelink: fetches one Figma frame and reduces it to the layout and style data a coding agent needs.
- Useful only when collaborators already design in Figma, and only with a token scoped to that file.

## Examples

1. **Independent** Fetch one authorized frame and compare layout measurements to the design.
2. **Combined** Map its spacing and exported images into a Magic UI implementation.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Provide FIGMA_API_KEY through client environment and limit file access. Treat design text as untrusted.
- Reads Figma files through the Figma API with the user's token; frame data reaches the agent's model provider.

**Software license** MIT.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.

# Magic MCP

Use when remote component discovery or generation is authorized.

> Frontend components and creative coding · Source A · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/21st-dev/magic-mcp)
- Verified 2026-11-26 against default branch `main` at [`6b5299e8a83c`](https://github.com/21st-dev/magic-mcp/commit/6b5299e8a83ceffa73d4fc4e148905bb3eeeeb55).
- GitHub reports archive state **false** and a repository push at `2026-09-09T20:38:22Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/21st-dev/magic-mcp/blob/6b5299e8a83ceffa73d4fc4e148905bb3eeeeb55/README.md)
- [LICENSE](https://github.com/21st-dev/magic-mcp/blob/6b5299e8a83ceffa73d4fc4e148905bb3eeeeb55/LICENSE)
- [package.json](https://github.com/21st-dev/magic-mcp/blob/6b5299e8a83ceffa73d4fc4e148905bb3eeeeb55/package.json)

## Runtime, hardware and setup

- **Type** MCP client package and service. Primary language TypeScript.
- **Platforms** Unverified.
- **Runtime** Remote MCP or Node for legacy launcher
- **Execution** local or hosted.
- **Agent paths** Codex, Claude Code, Cursor, Windsurf, VS Code, Grok Build. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Choose the current hosted endpoint and provide the key through the approved client secret mechanism.
- **Credentials and services** Current 21st API key. Old Magic API keys were reset.

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
npx @21st-dev/cli@latest init --client codex
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Component prompts and searches |
| Output | Component suggestions and generated frontend code |
| Primary | Component generation |
| Supporting | Frontend implementation |

Skip when networking, code provenance or account terms are unsuitable. Consider [magic-ui](magic-ui.md), [astryx](astryx.md), [react-bits](react-bits.md). Complementary tools include [impeccable](impeccable.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- Now the 21st MCP: searches 10,000+ React and Tailwind components and generates UI when hosted AI access is enabled on the account.
- A catalogue for the frame around a product, never its design authority.

## Examples

1. **Independent** Request a single React menu and review its dependency and keyboard behavior.
2. **Combined** Adapt the returned component to existing tokens and run Impeccable on the rendered route.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Upstream calls the current service 21st MCP. Review code, publishing tools and newly requested write permissions.
- Prompts and component requests go to the 21st service when hosted generation is used.

**Software license** ISC.

**Commercial use** The ISC package license and hosted service terms govern different parts of the workflow.

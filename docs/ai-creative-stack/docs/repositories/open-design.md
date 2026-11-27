# Open Design

Use for local-first design with an approved agent or provider.

> #09 · Design and prototyping · Source A · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/nexu-io/open-design)
- Verified 2026-11-26 against default branch `main` at [`5fdcc3db1e31`](https://github.com/nexu-io/open-design/commit/5fdcc3db1e31bd4fa70f673041b78e87977507c3).
- GitHub reports archive state **false** and a repository push at `2026-11-26T06:58:36Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/nexu-io/open-design/blob/5fdcc3db1e31bd4fa70f673041b78e87977507c3/README.md)
- [LICENSE](https://github.com/nexu-io/open-design/blob/5fdcc3db1e31bd4fa70f673041b78e87977507c3/LICENSE)
- [package.json](https://github.com/nexu-io/open-design/blob/5fdcc3db1e31bd4fa70f673041b78e87977507c3/package.json)

## Runtime, hardware and setup

- **Type** design application and MCP. Primary language TypeScript.
- **Platforms** Desktop releases (check pinned README for platform support), Browser/source workspace.
- **Runtime** Desktop release or source workspace and optional agent CLI
- **Execution** local or hosted.
- **Agent paths** Codex CLI, Claude Code, Cursor, OpenCode. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Choose one local agent or model provider and inspect the MCP configuration scope.
- **Credentials and services** Local agent credentials or provider credentials may apply by mode.

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
od mcp install codex
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Brief, references, design projects |
| Output | Prototypes and artifacts including MP4 for HyperFrames |
| Primary | Prototyping |
| Supporting | Creative direction, Video composition |

Skip when an established prototyping system already covers the job. Consider [penpot](penpot.md), [stitch-skills](stitch-skills.md), [figma-context](figma-context.md). Complementary tools include [hyperframes](hyperframes.md).

The pinned README documents HyperFrames integration.

## Craft notes

- A local-first agent workspace that turns one brief into prototypes, slides, images and HyperFrames video, reads DESIGN.md and supports 26 agent runtimes.
- The catalogue's documented example of a design tool driving a video renderer natively.

## Examples

1. **Independent** Prototype a settings screen and review the export against its reference.
2. **Combined** Use its documented native HyperFrames workspace feature to export a motion prototype.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Inspect agent and cloud settings before routing confidential prompts or assets.
- Prompts and assets go to whichever model provider is configured.

**Software license** Apache-2.0.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.

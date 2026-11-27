# Impeccable

Use for design critique or deterministic checks.

> #02 · Creative direction and design intelligence · Sources A and B · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/pbakaus/impeccable)
- Verified 2026-11-26 against default branch `main` at [`2fc5e1459efb`](https://github.com/pbakaus/impeccable/commit/2fc5e1459efbbf06d92c7306517c286bf12490cf).
- GitHub reports archive state **false** and a repository push at `2026-11-26T02:32:43Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/pbakaus/impeccable/blob/2fc5e1459efbbf06d92c7306517c286bf12490cf/README.md)
- [LICENSE](https://github.com/pbakaus/impeccable/blob/2fc5e1459efbbf06d92c7306517c286bf12490cf/LICENSE)
- [package.json](https://github.com/pbakaus/impeccable/blob/2fc5e1459efbbf06d92c7306517c286bf12490cf/package.json)

## Runtime, hardware and setup

- **Type** skill and CLI. Primary language Rust.
- **Platforms** Unverified.
- **Runtime** Node CLI and optional Chrome or Edge for URL detection
- **Execution** local.
- **Agent paths** Codex, Claude Code. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** For skill use, initialize project context with impeccable init and review generated project guidance.
- **Credentials and services** Detector requires no API key.

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
npx impeccable detect --json .
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Source directory or rendered URL |
| Output | Diagnostics in JSON or SARIF and skill critique |
| Primary | Design critique |
| Supporting | Creative direction, Frontend implementation |

Skip URL scanning without a supported browser or authorized target. Consider [hallmark](hallmark.md). Complementary tools include [taste-skill](taste-skill.md), [mengto-skills](mengto-skills.md), [magic-mcp](magic-mcp.md), [magic-ui](magic-ui.md), [dream-loop](dream-loop.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- 24 named commands (bolder, quieter, distill, typeset, animate, critique, audit, polish, harden and more) let you steer an agent with a verb instead of a paragraph.
- Its detector has 62 deterministic rules, no model and no key. An edit-time hook and SARIF output let findings gate pull requests. Reads PRODUCT.md and DESIGN.md.

## Examples

1. **Independent** Run the JSON detector and confirm each flag in the actual page.
2. **Combined** Audit a Taste-directed site and fix only findings tied to the shared brief.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Rendered URL scanning opens a browser. Treat reports as leads and review false positives.
- No external service in the documented base workflow.

**Software license** Apache-2.0.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.

# Astryx

Use when a coherent React design system with StyleX fits.

> #12 · Design and prototyping · Source A · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/meta/astryx)
- Verified 2026-11-26 against default branch `main` at [`4dd9b9b539f8`](https://github.com/meta/astryx/commit/4dd9b9b539f838a3a178e270be1cd643e1ad551e).
- GitHub reports archive state **false** and a repository push at `2026-11-26T06:50:41Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/meta/astryx/blob/4dd9b9b539f838a3a178e270be1cd643e1ad551e/README.md)
- [LICENSE](https://github.com/meta/astryx/blob/4dd9b9b539f838a3a178e270be1cd643e1ad551e/LICENSE)
- [package.json](https://github.com/meta/astryx/blob/4dd9b9b539f838a3a178e270be1cd643e1ad551e/package.json)

## Runtime, hardware and setup

- **Type** design system and CLI. Primary language TypeScript.
- **Platforms** Browser.
- **Runtime** React 19+ and StyleX. CLI requires Node 22.13+. Repo development uses pnpm 11.
- **Execution** local.
- **Agent paths** Generic coding agents via CLI documentation and skills. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Choose one Astryx theme and configure the StyleX build. Review CLI changes before committing.
- **Credentials and services** No separate key established.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npm install @astryxdesign/core @astryxdesign/theme-neutral @stylexjs/stylex
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Theme, component props and project configuration |
| Output | React UI and themed tokens |
| Primary | Frontend implementation |
| Supporting | Prototyping |

Skip when it would duplicate an existing component and token system. Consider [magic-ui](magic-ui.md), [magic-mcp](magic-mcp.md). Complementary tools include [penpot](penpot.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- Meta's design system: 150+ accessible React components and seven themes that are only CSS custom-property overrides.
- Its CLI writes usage guidance into AGENTS.md and CLAUDE.md, so people and agents work from one reference. Requires React 19+ and StyleX peers.

## Examples

1. **Independent** Implement one theme-backed accessible form and inspect keyboard navigation.
2. **Combined** Apply agreed Penpot values through the Astryx theme and review parity.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Review CLI changes to configuration and agent instruction files.
- No external service in the documented base workflow.

**Software license** MIT.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.

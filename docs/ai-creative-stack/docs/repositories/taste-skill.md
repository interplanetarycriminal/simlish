# Taste Skill

Use for reference-led art direction with browser review.

> Creative direction and design intelligence · Source A · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/Leonxlnx/taste-skill)
- Verified 2026-11-26 against default branch `main` at [`d1a2bb41d927`](https://github.com/Leonxlnx/taste-skill/commit/d1a2bb41d927083ac7118f60cfc9cdf711810ea0).
- GitHub reports archive state **false** and a repository push at `2026-11-26T01:29:24Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/Leonxlnx/taste-skill/blob/d1a2bb41d927083ac7118f60cfc9cdf711810ea0/README.md)
- [LICENSE](https://github.com/Leonxlnx/taste-skill/blob/d1a2bb41d927083ac7118f60cfc9cdf711810ea0/LICENSE)

## Runtime, hardware and setup

- **Type** skill. Primary language JavaScript.
- **Platforms** Unverified.
- **Runtime** Node 22+ for helper scripts
- **Execution** local.
- **Agent paths** Codex, Claude Code. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Load only design-taste-frontend and review browser and reference settings.
- **Credentials and services** No separate key established for the base skill.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Brief and reference images |
| Output | Design direction and frontend revisions |
| Primary | Creative direction |
| Supporting | Design critique, Frontend implementation |

Skip when a mature design direction already exists. Consider [anthropic-frontend](anthropic-frontend.md), [hallmark](hallmark.md), [ui-ux-pro-max](ui-ux-pro-max.md), [mengto-skills](mengto-skills.md). Complementary tools include [impeccable](impeccable.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- Deals palette, type and hero layout from a classification of the business, then checks the page in headless Chrome at 1440, 1024, 768 and 390 px.
- Rations WebGL to software, tech and gaming pages, with at most four contexts. Invert that rule when the 3D scene is the content rather than decoration.

## Examples

1. **Independent** Draft a hero with one composition reference and compare the rendered result to it.
2. **Combined** Hand the approved direction to Impeccable for critique without restyling.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Review browser and reference-image helpers before granting access.
- No external service in the documented base workflow.

**Software license** MIT.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.

# Hallmark

Use its design skill or its Floor checks against a defined brief.

> Creative direction and design intelligence · Sources A and B · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/Nutlope/hallmark)
- Verified 2026-11-26 against default branch `main` at [`04977e15f3df`](https://github.com/Nutlope/hallmark/commit/04977e15f3dfd6ee4b74c887dac3eb52665d6c92).
- GitHub reports archive state **false** and a repository push at `2026-11-11T11:56:16Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/Nutlope/hallmark/blob/04977e15f3dfd6ee4b74c887dac3eb52665d6c92/README.md)
- [LICENSE](https://github.com/Nutlope/hallmark/blob/04977e15f3dfd6ee4b74c887dac3eb52665d6c92/LICENSE)
- [package.json](https://github.com/Nutlope/hallmark/blob/04977e15f3dfd6ee4b74c887dac3eb52665d6c92/package.json)

## Runtime, hardware and setup

- **Type** skill. Primary language CSS.
- **Platforms** Unverified.
- **Runtime** Node installer and browser for page review
- **Execution** local.
- **Agent paths** Claude Code, Codex, Cursor, OpenCode, GitHub Copilot. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Select a single harness and use local scope where appropriate. Edit-time hooks are optional.
- **Credentials and services** No separate key established for the base skill.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npx skills add nutlope/hallmark -g --agent codex
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Design brief and rendered page |
| Output | Design guidance, source edits and critique |
| Primary | Creative direction, Design critique |
| Supporting | Frontend implementation |

Skip global scope in a repo that requires scoped skills. Consider [taste-skill](taste-skill.md), [impeccable](impeccable.md), [anthropic-frontend](anthropic-frontend.md). Complementary tools include [magic-ui](magic-ui.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- Gates in three tiers: Floor never ships, Reflex can be overruled on the record, Finish never blocks.
- Lints at eight widths, then hands the page to a fresh-context reviewer. Its 'nothing invented' pre-flight carries over directly to factual accuracy in explanatory work.

## Examples

1. **Independent** Render a product landing page and inspect repeat patterns and image attribution.
2. **Combined** Review a Magic UI page while preserving its approved tokens.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Inspect optional edit-time hooks and confirm rights and attribution for individual photos.
- No external service in the documented base workflow.

**Software license** MIT.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.

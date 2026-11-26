# UI/UX Pro Max

Use when requirements need structured design-system exploration.

> Creative direction and design intelligence · Source A · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- Verified 2026-11-26 against default branch `main` at [`b73ee96f8d4f`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/commit/b73ee96f8d4ff7bbc279c52dadcd907ffe23629c).
- GitHub reports archive state **false** and a repository push at `2026-11-25T22:08:31Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/b73ee96f8d4ff7bbc279c52dadcd907ffe23629c/README.md)
- [LICENSE](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/b73ee96f8d4ff7bbc279c52dadcd907ffe23629c/LICENSE)

## Runtime, hardware and setup

- **Type** skill and CLI. Primary language Python.
- **Platforms** Unverified.
- **Runtime** Python 3 for design queries and Node for npm installer
- **Execution** local.
- **Agent paths** Claude Code, Codex. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Select a target assistant and review generated local files and design-system recommendations.
- **Credentials and services** No separate key established for local queries.

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
npm install -g ui-ux-pro-max-cli
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Product brief and stack |
| Output | Design system recommendation and implementation guidance |
| Primary | Creative direction |
| Supporting | Prototyping, Frontend implementation |

Skip when project tokens already settle the decision. Consider [taste-skill](taste-skill.md), [anthropic-frontend](anthropic-frontend.md). Complementary tools include [penpot](penpot.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- A searchable database of 80 styles and 194 reasoning rules, plus a generator that turns a product type into pattern, style, palette and section plan.
- Use it to explore, then let one creative authority choose. Its sibling 3dviz-pro-max (not pinned here) carries 3D recipes and a frame-capture helper.

## Examples

1. **Independent** Generate a design-system recommendation for a scheduling product and assess contrast.
2. **Combined** Translate approved tokens into a Penpot prototype and compare component variants.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Review Python scripts and apply accessibility checks to proposals.
- No external service in the documented base workflow.

**Software license** MIT.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.

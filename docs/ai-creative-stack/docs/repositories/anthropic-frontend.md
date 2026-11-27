# Anthropic Frontend Design

Use when you need a focused design brief and expressive typography.

> #04 · Creative direction and design intelligence · Source A · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/anthropics/skills/tree/main/skills/frontend-design)
- Verified 2026-11-26 against default branch `main` at [`e4bb5d960d87`](https://github.com/anthropics/skills/commit/e4bb5d960d87126ff3b3a8af1a104b7db67560ba).
- GitHub reports archive state **false** and a repository push at `2026-11-16T14:22:50Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [SKILL.md](https://github.com/anthropics/skills/blob/e4bb5d960d87126ff3b3a8af1a104b7db67560ba/skills/frontend-design/SKILL.md)
- [LICENSE.txt](https://github.com/anthropics/skills/blob/e4bb5d960d87126ff3b3a8af1a104b7db67560ba/skills/frontend-design/LICENSE.txt)

## Runtime, hardware and setup

- **Type** skill. Primary language Python.
- **Platforms** Unverified.
- **Runtime** Markdown skill and agent execution environment
- **Execution** local.
- **Agent paths** Claude Code. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Read the pinned SKILL.md as scoped guidance in Claude Code, subject to project rules.
- **Credentials and services** No separate key established.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
Load only the pinned frontend-design skill and its license using your agent's local skill discovery.
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Brief and frontend constraints |
| Output | Frontend design and code |
| Primary | Creative direction |
| Supporting | Frontend implementation |

Skip when the project already has an authoritative visual system. Consider [taste-skill](taste-skill.md), [hallmark](hallmark.md), [ui-ux-pro-max](ui-ux-pro-max.md). Complementary tools include [magic-ui](magic-ui.md), [awesome-design-md](awesome-design-md.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- Grounds distinctive choices in the subject's own world and spends boldness in one place.
- Asks for a token plan reviewed against the brief before code, and for critique from screenshots of the rendered page.

## Examples

1. **Independent** Ask for one differentiated editorial layout and implement it using the existing stack.
2. **Combined** Carry its art direction into Magic UI component styling.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Read the skill as project inputs. Review generated dependencies and output.
- No external service in the documented base workflow.

**Software license** Apache-2.0.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.
